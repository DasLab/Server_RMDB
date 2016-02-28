from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.db import IntegrityError

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


def user_login(request):
    if request.user.is_authenticated():
        if request.GET.has_key('next') and 'admin' in request.GET['next']:
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
                        rmdb_user = RMDBUser.objects.get(user=user)
                        (rmdb_user.entry_count, rmdb_user.construct_count, rmdb_user.data_count, rmdb_user.last_entry, rmdb_user.last_date) = get_user_stats(user)
                        rmdb_user.save()

                        return HttpResponseRedirect('/')
                else:
                    messages = 'Inactive/disabled account. Please contact us.'
        return render_to_response(PATH.HTML_PATH['login'], {'form': form, 'messages':messages}, context_instance=RequestContext(request))
    else:
        if request.GET.has_key('next') and 'admin' in request.GET['next']:
            flag = 'Admin'
        else:
            flag = 'Member'
        form = LoginForm(initial={'flag': flag})
        return render_to_response(PATH.HTML_PATH['login'], {'form': form}, context_instance=RequestContext(request))


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
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            error_msg = check_login_register(form)

            if not error_msg:
                try:
                    user =  User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'], last_login=datetime.datetime.now())
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

                    flag = 1
                    form = RegistrationForm()
                except IntegrityError as e:
                    error_msg.append('Username already exists. Try another.')
                except Exception:
                    print traceback.format_exc()
                    error_msg.append('Unknown error. Please contact admin.')
        else:
            if 'username' in form.errors: error_msg.append('Username field is required.')
            if 'password' in form.errors: error_msg.append('Password field is required.')
            if 'first_name' in form.errors: error_msg.append('First name field is required.')
            if 'last_name' in form.errors: error_msg.append('Last name field is required.')
            if 'institution' in form.errors: error_msg.append('Institution field is required.')
            if 'department' in form.errors: error_msg.append('Department field is required.')
            if 'email' in form.errors: error_msg.append('Email field is required.')
            error_msg.append('Form invalid: missing required field(s).')
    else:
        form = RegistrationForm()

    return render_to_response(PATH.HTML_PATH['register'], {'reg_form':form, 'error_msg':error_msg, 'flag':flag}, context_instance=RequestContext(request))



def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")


@user_passes_test(lambda u: u.is_superuser)
def browse(request, path):
    fm = FileManager(MEDIA_ROOT + '/data')
    return fm.render(request, path)
