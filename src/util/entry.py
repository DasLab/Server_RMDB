import os
import shutil
import subprocess
import sys
import threading
import traceback

if 'pylab' not in sys.modules:
    import matplotlib
    matplotlib.use('Agg')
from pylab import *

from Tkinter import TclError

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.management import call_command

from rdatkit import RDATFile, ISATABFile

from src.models import *
from src.settings import *
from src.user import update_user_stats
from src.util.media import *
from src.util.util import *


def get_spreadsheet(url):
    url = subprocess.Popen("curl %s -L -I -s -o /dev/null -w %{url_effective}" % url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().replace('%3D', '=').replace('%26', '&')
    idx = url.find('key=')
    print url, idx
    if idx > 0:
        key = ''
        idx += 4
        while url[idx] != '&' and idx < len(url):
            key += url[idx]
            idx += 1
        authkey = subprocess.Popen("curl https://www.google.com/accounts/ClientLogin -d Email=%s -d Passwd=%s -d accountType=HOSTED_OR_GOOGLE -d source=Google-spreadsheet -d service=wise | grep Auth | cut -d\= -f2" % (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()
        subprocess.check_call('curl -L --silent --header "Authorization: GoogleLogin auth=%s" "http://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&hl&exportFormat=xls" > %s/%s.xls' % (authkey, key, PATH.DATA_DIR['FILE_DIR'], key), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return '%s/%s.xls' % (PATH.DATA_DIR['TMP_DIR'], key)
    else:
        return ''


def validate_file(file_path, link_path, input_type):
    messages = []
    errors = []
    flag = 0

    input_file = RDATFile() if (input_type == 'rdat') else ISATABFile()
    is_continue = 1
    if link_path:
        if input_type == 'rdat':
            path = '%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], link_path, link_path)
            is_continue = os.path.exists(path)
        else:
            is_continue = get_spreadsheet(link_path)

        if not is_continue:
            if input_type == 'rdat':
                errors.append('Input RMDB_ID: %s is invalid.' % link_path)
            else:
                errors.append('Input ISATAB file link: %s is invalid.' % link_path)
            return (errors, messages, 1)
        else:
            if input_type == 'rdat':
                input_file.load(open(path, 'r'))
            else:
                input_file.load(is_continue)

    else:
        tmp_file = temp_file(file_path)
        try:
            input_file.load(tmp_file)
            messages = input_file.validate()
        except Exception, e:
            flag = 1
            errors.append('Invalid input file format: %s' % e)
        tmp_file.close()
        if os.path.exists('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_path.name)):
            os.remove('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_path.name))

    if not flag:
        if (not messages):
            flag = 2
        else:
            flag = 3
            messages = [m[8:] for m in messages]

    return (errors, messages, flag)


def process_upload(form, formset, upload_file, user):
    (error_msg, flag, entry) = ([], 0, '')
    rmdb_id = form.cleaned_data['rmdb_id'].upper()

    try:
        if not check_rmdb_id(rmdb_id):
            error_msg.append('RMDB ID invalid. Hover mouse over the field to see instructions.')
            flag = 1
        else:
            # check file validation
            (rdatfile, isatabfile) = (RDATFile(), ISATABFile())

            rf = temp_file(upload_file)
            exp_type = [x[1] for i, x in enumerate(ENTRY_TYPE_CHOICES) if x[0] == form.cleaned_data['exp_type']][0].replace(' ', '')
            txt = rf.readlines()
            txt = filter(lambda x: 'experimentType:' in x, txt)
            is_eterna = ("ETERNA" in rmdb_id)
            if txt:
                # find the experimentType(eg. StandardState) in txt
                txt = txt[0]
                txt = txt[txt.find('experimentType:'):]
                txt = txt[txt.find(':')+1 : txt.find('\t')]
                if txt != exp_type:
                    error_msg.append('experimentType mismatch between selected file and web page form; please check and resubmit.')
                    error_msg.append('File indicates experimentType of %s , while form selected %s.' % (txt, exp_type))
                    flag = 1
            elif is_eterna:
                if exp_type != 'StandardState':
                    flag = 1
                    error_msg.append('Use StandardState for Eterna entries.')
            elif exp_type != 'MOHCA':
                flag = 1
                error_msg.append('Missing experimentType.')

            rf.seek(0)
            if form.cleaned_data['file_type'] == 'isatab':
                try:
                    isatabfile.load(rf.name)
                    rdatfile = isatabfile.toRDAT()
                except Exception:
                    print traceback.format_exc()
                    error_msg.append('Invalid ISATAB file; please check and resubmit.')
                    flag = 1
            else:
                try:
                    rdatfile.load(rf)
                    isatabfile = rdatfile.toISATAB()
                except Exception:
                    print traceback.format_exc()
                    error_msg.append('Invaid RDAT file; please check and resubmit.')
                    flag = 1
            rf.close()

        if not flag:
            flag = 2
            (error_msg, flag, entry) = submit_entry(form, formset, user, upload_file, rdatfile, isatabfile, flag)

    except Exception:
        flag = 1
        print traceback.format_exc()
        error_msg.append('500: Internal server error. Please contact admin.')
    return (error_msg, flag, entry)


def submit_entry(form, formset, user, upload_file, rdatfile, isatabfile, flag):
    # print '****************** Submitting Entry ******************'
    error_msg = []
    rmdb_id = form.cleaned_data['rmdb_id'].upper()

    publication = Publication(title=form.cleaned_data['publication'], authors=form.cleaned_data['authors'], pubmed_id=form.cleaned_data['pubmed_id'])
    publication.save()

    entries = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')
    if len(entries) > 0:
        prev_entry = entries[0]
        current_version = prev_entry.version
        owner = prev_entry.owner
        p_inves_list = RMDBUser.objects.get(user=owner).principal_investigator.all()

        if owner != user\
                and (not user.is_staff)\
                and user not in prev_entry.co_owners.all()\
                and user not in p_inves_list:
            error_msg.append('RMDB entry %s exists and you cannot update it since you don\'t have the edit privilege to it.' % rmdb_id)
            flag = 1
            return (error_msg, flag, '')

        current_status = prev_entry.status
        if current_status != form.cleaned_data['entry_status']:
            for previous_entry in entries:
                previous_entry.status=form.cleaned_data['entry_status']
                previous_entry.save()
    else:
        current_version = 0
        owner = None

    entry = RMDBEntry(type=form.cleaned_data['exp_type'],
                      rmdb_id=rmdb_id,
                      authors=form.cleaned_data['authors'],
                      publication=publication,
                      comments=rdatfile.comments,
                      description=form.cleaned_data['description'],
                      data_count=0,
                      construct_count=0,
                      version=current_version + 1,
                      owner=owner if owner else user,
                      status=form.cleaned_data['entry_status'])


    # rmdb_id_series = entry.rmdb_id[:entry.rmdb_id.rfind('_')]
    # current_id = int(entry.rmdb_id[entry.rmdb_id.rfind('_')+1:])
    # entry.latest = -1
    # current_max = False
    # entries = RMDBEntry.objects.filter(rmdb_id__startswith=rmdb_id_series)
    # for e in entries:
    #   max_id = int(e.rmdb_id[e.rmdb_id.rfind('_')+1:])
    #   if max_id <= current_id:
    #       current_max = True
    #   else:
    #       current_max = False
    #       break

    # if current_version == 0 or current_max:
    #   entry.latest = True
    #   for e in entries:
    #       e.latest = False
    #       e.save()
    entry.save()

    entry, co_owner_changes = save_co_owners(entry, formset, user)

    (error_msg, entry) = save_rdat(entry, upload_file, rdatfile, isatabfile, error_msg)
    if not DEBUG: send_notify_emails(entry, user.email)
    return (error_msg, flag, entry)


def save_co_owners(entry, formset, user):
    co_owner_changes = False
    pre_co_owners = set(entry.co_owners.all())
    cur_co_owners = set()
    for co_owner_form in formset:
        if co_owner_form.cleaned_data:
            co_owner = User.objects.get(username=co_owner_form.cleaned_data['co_owner'])
            # don't add Owner to co-owner
            if co_owner != entry.owner:
                cur_co_owners.add(co_owner)
    # always add user to co-owner if he's a previous co-owner
    # users can't remove self from co-owner list
    if user in pre_co_owners:
        cur_co_owners.add(user)

    # update co-owners
    if pre_co_owners != cur_co_owners:
        co_owner_changes = True
        entry.co_owners.clear()
        for co_owner in cur_co_owners:
            entry.co_owners.add(co_owner)
        entry.save()

    return entry,co_owner_changes


def write_annotations(dictionary, section, annotation_model):
    count = 0
    for d in dictionary:
        for value in dictionary[d]:
            a = annotation_model(name=d.strip(), value=str(value.decode('ascii', 'ignore')), section=section)
            a.save()
            if d.strip() in ('mutation', 'sequence'):
                count += 1
    return count


def save_rdat(entry, upload_file, rdatfile, isatabfile, error_msg=[]):
    if not os.path.exists('%s%s' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id)):
        os.mkdir('%s%s' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id))
    if not os.path.exists('%s%s' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id)):
        os.mkdir('%s%s' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id))

    rdat_name = '%s%s/%s_%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version)
    shutil.move('%s%s' % (PATH.DATA_DIR['TMP_DIR'], upload_file.name), rdat_name)
    shutil.copyfile(rdat_name, '%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id, entry.rmdb_id))

    # Breaks Excel compatibility if data/columns are > 256
    if len(rdatfile.values.values()[0]) < 256:
        isatabfile.save('%s%s/%s_%s.xls' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version))
    write_annotations(rdatfile.annotations, entry, EntryAnnotation)

    data_count = 0
    construct_count = 0

    k = rdatfile.constructs.keys()[0]
    construct_count += 1
    c = rdatfile.constructs[k]

    construct = ConstructSection(entry=entry, name=c.name, sequence=c.sequence, offset=c.offset, structure=c.structure, seqpos=','.join([str(x) for x in c.seqpos]), xsel=','.join([str(x) for x in c.xsel]))
    construct.save()

    for d in c.data:
        if rdatfile.version >= 0.4:
            if 'REACTIVITY' in ''.join(d.annotations['datatype']) and 'REACTIVITY_ERROR' not in ''.join(d.annotations['datatype']):
                data = DataSection(xsel=','.join([str(x) for x in d.xsel]), values=','.join([str(x) for x in d.values]), errors='', trace='', reads='', seqpos=','.join([str(x) for x in d.seqpos]), construct_section=construct)
            else:
                continue
        else:
            data = DataSection(xsel=','.join([str(x) for x in d.xsel]), values=','.join([str(x) for x in d.values]), errors=','.join([str(x) for x in d.errors]), trace=','.join([str(x) for x in d.trace]), reads=','.join([str(x) for x in d.reads]), seqpos=','.join([str(x) for x in d.seqpos]), construct_section=construct)
        data.save()
        data_count += len(d.values)
        construct_count += write_annotations(d.annotations, data, DataAnnotation)

    entry.data_count = data_count
    entry.construct_count = construct_count

    try:
        entry.is_trace = save_image(entry.rmdb_id, construct, c, entry.type)
    except TclError:
        error_msg.append('Problem generating the images. This is a server-side problem, please try again.')
    entry.save()
    #precalculate_structures(entry)

    save_thumb(entry)
    save_json(entry.rmdb_id)
    return (error_msg, entry)


def review_entry(new_stat, rmdb_id):
    entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-id')[0]
    construct = ConstructSection.objects.get(entry_id=entry.id)
    entry = RMDBEntry.objects.filter(id=construct.entry.id).order_by('-version')[0]
    entry.status = new_stat
    entry.save()


@receiver(post_save, sender=RMDBEntry)
def on_entry_save(sender, instance, **kwargs):
    job1 = threading.Thread(target=call_command, args=('stats',))
    job2 = threading.Thread(target=update_user_stats, args=(instance.owner,))
    job3 = threading.Thread(target=call_command, args=('make_json', instance.rmdb_id))
    job1.start()
    job2.start()
    job3.start()

    # if os.path.exists('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id)):
    #     json = do_get_stats(instance.rmdb_id)
    #     if json is None: return

    #     json['status'] = instance.status
    #     simplejson.dump(json, open('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id), 'w'), sort_keys=True, indent=' ' * 4)


@receiver(post_delete, sender=RMDBEntry)
def on_entry_del(sender, instance, **kwargs):
    job1 = threading.Thread(target=call_command, args=('stats',))
    job2 = threading.Thread(target=update_user_stats, args=(instance.owner,))
    job1.start()
    job2.start()

    ver = instance.version
    ver_list = get_entry_version(instance.rmdb_id)
    is_last = any([x > ver for x in ver_list])

    if is_last and os.path.exists('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id)):
        json = do_get_stats(instance.rmdb_id)
        if json is None: return
        json['versions'] = ver_list
        simplejson.dump(json, open('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id), 'w'), sort_keys=True, indent=' ' * 4)
        return

    if not ver_list:
        if os.path.exists('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id)):
            os.remove('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id))
        if os.path.exists('%s/%s-hmap.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id)):
            os.remove('%s/%s-hmap.json' % (PATH.DATA_DIR['JSON_DIR'], instance.rmdb_id))
        if os.path.exists('%s/%s-rx.png' % (PATH.DATA_DIR['IMG_DIR'], instance.rmdb_id)):
            os.remove('%s/%s-rx.png' % (PATH.DATA_DIR['IMG_DIR'], instance.rmdb_id))
        if os.path.exists('%s/%s-tr.png' % (PATH.DATA_DIR['IMG_DIR'], instance.rmdb_id)):
            os.remove('%s/%s-tr.png' % (PATH.DATA_DIR['IMG_DIR'], instance.rmdb_id))
        if os.path.exists('%s/%s.gif' % (PATH.DATA_DIR['THUMB_DIR'], instance.rmdb_id)):
            os.remove('%s/%s.gif' % (PATH.DATA_DIR['THUMB_DIR'], instance.rmdb_id))
        return

    ver_list = [x for x in ver_list if x < ver]
    if not ver_list: return
    next_ver = max([x for x in ver_list if x < ver])
    shutil.copyfile('%s%s/%s_%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], instance.rmdb_id, instance.rmdb_id, next_ver), '%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], instance.rmdb_id, instance.rmdb_id))
    os.remove('%s%s/%s_%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], instance.rmdb_id, instance.rmdb_id, ver))
    if os.path.exists('%s%s/%s_%s.xls' % (PATH.DATA_DIR['FILE_DIR'], instance.rmdb_id, instance.rmdb_id, ver)):
        os.remove('%s%s/%s_%s.xls' % (PATH.DATA_DIR['FILE_DIR'], instance.rmdb_id, instance.rmdb_id, ver))

    job3 = threading.Thread(target=call_command, args=('make_img', instance.rmdb_id))
    job4 = threading.Thread(target=call_command, args=('make_json', instance.rmdb_id))
    job3.start()
    job4.start()
