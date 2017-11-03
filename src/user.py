from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.forms import formset_factory

import datetime
import string
import traceback

from filemanager import FileManager

from src.models import *


def get_user_stats(user):
    entries = RMDBEntry.objects.filter(owner=user)
    N_entries = len(entries)
    N_constructs = 0
    N_datapoints = 0
    for e in entries:
        N_constructs += e.construct_count
        N_datapoints += e.data_count

    entries = RMDBEntry.objects.filter(owner=user).order_by('-creation_date')
    if entries:
        return (N_entries, N_constructs, N_datapoints, entries[0].rmdb_id, entries[0].creation_date)
    else:
        return (N_entries, N_constructs, N_datapoints, None, None)


def update_user_stats(user):
    rmdb_user = RMDBUser.objects.get(user=user)
    (rmdb_user.entry_count, rmdb_user.construct_count, rmdb_user.data_count, rmdb_user.last_entry, rmdb_user.last_date) = get_user_stats(user)
    rmdb_user.save()


def user_login(request):
    if request.user.is_authenticated():
        if 'next' in request.GET and 'admin' in request.GET.get('next'):
            return error403(request)
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        messages = 'Invalid username and/or password. Please try again.'
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            flag = form.cleaned_data['flag']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    if flag == "Admin":
                        return HttpResponseRedirect('/admin/')
                    else:
                        update_user_stats(user)
                        return HttpResponseRedirect('/')
                else:
                    messages = 'Inactive/disabled account. Please contact us.'
        return render(request, PATH.HTML_PATH['login'], {'form': form, 'messages': messages})
    else:
        if 'next' in request.GET and 'admin' in request.GET.get('next'):
            flag = 'Admin'
        else:
            flag = 'Member'
        form = LoginForm(initial={'flag': flag})
        return render(request, PATH.HTML_PATH['login'], {'form': form})


def is_valid_name(input, char_allow, length):
    if len(input) <= length: return 0
    src = ''.join([string.digits, string.ascii_letters, char_allow])
    for char in input:
        if char not in src: return 0
    return 1


def is_valid_email(input):
    input_split = input.split("@")
    if len(input_split) != 2: return 0
    if not is_valid_name(input_split[0], ".-_", 2): return 0
    input_split = input_split[1].split(".")
    if len(input_split) == 1: return 0
    for char in input_split:
        if not is_valid_name(char, "", 1): return 0
    return 1


def check_login_register(form):
    error_msg = []

    user_name = form.cleaned_data['username']
    password_1 = form.cleaned_data['password']
    password_2 = form.cleaned_data['repeat_password']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    institution = form.cleaned_data['institution']
    department = form.cleaned_data['department']
    email = form.cleaned_data['email']

    if password_1 != password_2:
        error_msg.append('Password fields do not match. Try again.')
    if not is_valid_name(user_name, '', 2):
        error_msg.append('Username must be at least 3 characters.')
    if len(password_1) < 6 or len(password_2) < 6:
        error_msg.append('Password must be at least 6 characters.')
    if not is_valid_name(first_name, '- ', 2):
        error_msg.append('First name must be at least 3 characters.')
    if not is_valid_name(last_name, '- ', 1):
        error_msg.append('Last name must be at least 2 characters.')
    if not is_valid_name(institution, '()-, ', 3):
        error_msg.append('Institution must be at least 4 characters.')
    if not is_valid_name(department, '()-, ', 3):
        error_msg.append('Department must be at least 4 characters.')
    if not is_valid_email(email):
        error_msg.append('Email address invalid.')
    return error_msg


def register(request):
    error_msg = []
    flag = 0
    form = RegisterForm()

    PInvesFormSet = formset_factory(PInvesForm, formset=BasePInvesFormSet)
    formset = PInvesFormSet()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        formset = PInvesFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            error_msg = check_login_register(form)

            if not error_msg:
                try:
                    user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'], last_login=datetime.datetime.now())
                    user.first_name = form.cleaned_data['first_name']
                    user.last_name = form.cleaned_data['last_name']
                    user.set_password(form.cleaned_data['password'])
                    user.is_active = True
                    user.save()

                    rmdb_user = RMDBUser()
                    rmdb_user.user = user
                    rmdb_user.institution = form.cleaned_data['institution']
                    rmdb_user.department = form.cleaned_data['department']
                    rmdb_user.save()

                    rmdb_user, p_inves_changes = save_p_inves(rmdb_user, formset, user)

                    flag = 1

                    # update form and formset
                    formset = PInvesFormSet()
                    form = RegisterForm()

                except IntegrityError:
                    error_msg.append('Username already exists. Try another.')
                except Exception:
                    print traceback.format_exc()
                    error_msg.append('Unknown error. Please contact admin.')
        """
        else:
            if 'username' in form.errors: error_msg.append('Username field is required.')
            if 'password' in form.errors: error_msg.append('Password field is required.')
            if 'first_name' in form.errors: error_msg.append('First name field is required.')
            if 'last_name' in form.errors: error_msg.append('Last name field is required.')
            if 'institution' in form.errors: error_msg.append('Institution field is required.')
            if 'department' in form.errors: error_msg.append('Department field is required.')
            if 'email' in form.errors: error_msg.append('Email field is required.')
            error_msg.append('Form invalid: missing required field(s).')
        """

    return render(request, PATH.HTML_PATH['register'], {'reg_form': form,
                                                        'formset': formset,
                                                        'error_msg': error_msg,
                                                        'flag': flag})



def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")


@user_passes_test(lambda u: u.is_superuser)
def browse(request, path):
    fm = FileManager(MEDIA_ROOT + '/data')
    return fm.render(request, path)


#
# Down below create by Chunwen Xiong
#

def save_p_inves(rmdb_usr, formset, user):
    p_inves_changes = False
    pre_p_investigator = set(rmdb_usr.principal_investigator.all())
    cur_p_investigator = set()
    for p_inves_form in formset:
        if p_inves_form.cleaned_data:
            p_inves = User.objects.get(username=p_inves_form.cleaned_data['p_inves'])
            # don't add user to principal investigator
            if p_inves != user:
                cur_p_investigator.add(p_inves)

    if pre_p_investigator != cur_p_investigator:
        p_inves_changes = True
        rmdb_usr.principal_investigator.clear()
        for p_inves in cur_p_investigator:
            rmdb_usr.principal_investigator.add(p_inves)
        rmdb_usr.save()

    return rmdb_usr,p_inves_changes


def edit_profile(request):
    error_msg = []
    flag = 0
    p_inves_changes = False

    usr = request.user
    rmdb_usr = RMDBUser.objects.get(user=usr)
    initial_value = {"first_name": usr.first_name,
                     "last_name": usr.last_name,
                     "institution":rmdb_usr.institution,
                     "department":rmdb_usr.department,
                     "email": usr.email,
                     }
    form = ProfileForm(initial=initial_value)

    initial_value_formset = [{'p_inves': p_inves} for p_inves in rmdb_usr.principal_investigator.all() if p_inves != usr]

    PInvesFormSet = formset_factory(PInvesForm, formset=BasePInvesFormSet, extra=0 if initial_value_formset else 1)
    formset = PInvesFormSet(initial=initial_value_formset)

    if request.method == 'POST':
        form = ProfileForm(request.POST, initial=initial_value)
        formset = PInvesFormSet(request.POST, initial=initial_value_formset)
        if form.is_valid() and formset.is_valid():
            try:
                usr.email = form.cleaned_data['email']
                usr.first_name = form.cleaned_data['first_name']
                usr.last_name = form.cleaned_data['last_name']
                usr.save()

                rmdb_usr.institution = form.cleaned_data['institution']
                rmdb_usr.department = form.cleaned_data['department']
                rmdb_usr.save()

                rmdb_usr, p_inves_changes = save_p_inves(rmdb_usr, formset, usr)

                # update formset
                updated_value_formset = [{'p_inves': p_inves} for p_inves in rmdb_usr.principal_investigator.all()
                                         if p_inves != usr]
                PInvesFormSet = formset_factory(PInvesForm, formset=BasePInvesFormSet,
                                                extra=0 if updated_value_formset else 1)
                formset = PInvesFormSet(initial=updated_value_formset)

                flag = 1
            except Exception:
                print traceback.format_exc()
                error_msg.append('Unknown error. Please contact admin.')

    return render(request, PATH.HTML_PATH['edit_profile'],
                  {'prof_form': form,
                   'formset': formset,
                   'error_msg': error_msg,
                   'flag': flag,
                   'p_inves_changes': p_inves_changes,
                   'usr': usr})


def change_password(request):
    message = ''

    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            # messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse('change_password_done'))
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, PATH.HTML_PATH['change_password'], {'form': form})


def change_password_done(request):
    return render(request, PATH.HTML_PATH['change_password_done'])
