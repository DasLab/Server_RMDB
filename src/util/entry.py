import os
from pylab import *
import shutil
import subprocess
import traceback

from Tkinter import TclError

from rdatkit.datahandlers import RDATFile, RDATSection, ISATABFile

from src.models import *
from src.settings import *
from src.util.media import *
from src.util.util import *
from src.helper.helper_images import *


def get_spreadsheet(url):
    url = subprocess.Popen("curl %s -L -I -s -o /dev/null -w %{url_effective}" % url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().replace('%3D','=').replace('%26','&')
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
        except AttributeError, e:
            flag = 1
            errors.append('Invalid input file format: %s' % e)
        tmp_file.close()
        os.remove('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_path.name))

    if not flag:
        if (not messages):
            flag = 2
        else:
            flag = 3
            messages = [m[8:] for m in messages]

    return (errors, messages, flag)


def process_upload(form, upload_file, user):
    (error_msg, flag, entry) = ([], 0, '')

    try:
        if not check_rmdb_id(form.cleaned_data['rmdb_id']):
            error_msg.append('RMDB ID invalid. Hover mouse over the field to see instructions.')
            flag = 1
        else:
            (rdatfile, isatabfile) = (RDATFile(), ISATABFile())
            isatabfile.loaded = False
            rdatfile.loaded = False

            rf = temp_file(upload_file)
            txt = rf.readlines()
            txt = filter(lambda x:'experimentType:' in x, txt)
            if txt:
                txt = txt[0]
                txt = txt[txt.find('experimentType:'):]
                txt = txt[txt.find(':')+1 : txt.find('\t')]
                exp_type = [x[1] for i, x in enumerate(ENTRY_TYPE_CHOICES) if x[0] == form.cleaned_data['exp_type']][0].replace(' ', '')
                if txt != exp_type:
                    error_msg.append('experimentType mismatch between selected file and web page form; please check and resubmit.')
                    error_msg.append('File indicates experimentType of %s , while form selected %s.' % (txt, exp_type))
                    flag = 1
            else:
                flag = 1
                error_msg.append('Missing experimentType.')


            rf.seek(0)
            if form.cleaned_data['file_type'] == 'isatab':
                try:
                    isatabfile.load(rf.name)
                    isatabfile.loaded = True
                    rdatfile = isatabfile.toRDAT()
                except Exception:
                    error_msg.append('Invalid ISATAB file; please check and resubmit.')
                    flag = 1
            else:
                try:
                    rdatfile.load(rf)
                    rdatfile.loaded = True
                    isatabfile = rdatfile.toISATAB()
                except Exception:
                    error_msg.append('Unknown error. Please contact admin.')
                    flag = 1

        if not flag:
            (error_msg, entry) = submit_entry(form, user, upload_file, rdatfile, isatabfile)
            flag = 2

    except Exception:
        flag = 1
        print traceback.format_exc()
        error_msg.append('Internal Server Error; please check and resubmit.')
    return (error_msg, flag, entry)


def submit_entry(form, user, upload_file, rdatfile, isatabfile):
    error_msg = []
    rmdb_id = form.cleaned_data['rmdb_id'].upper()

    publication = Publication(title=form.cleaned_data['publication'], authors=form.cleaned_data['authors'], pubmed_id=form.cleaned_data['pubmed_id'])
    publication.save()

    entries = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')
    if len(entries) > 0:
        prev_entry = entries[0]
        current_version = prev_entry.version
        owner = prev_entry.owner

        if owner != user and (not user.is_staff):
            error_msg.append('RMDB entry %s exists and you cannot update it since you are not the owner.' % rmdb_id)
            return (error_msg, '')
    else:
        current_version = 0
        owner = None

    entry = RMDBEntry(type=form.cleaned_data['exp_type'], rmdb_id=rmdb_id, authors=form.cleaned_data['authors'], publication=publication, comments=rdatfile.comments, description=form.cleaned_data['description'], data_count=0, construct_count=0, version=current_version + 1, owner=user)
    entry.status = 'PUB' if user.is_staff else 'REV'
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

    (error_msg, entry) = save_rdat(entry, upload_file, rdatfile, isatabfile, error_msg)
    if not DEBUG: send_notify_emails(entry, request)
    return (error_msg, entry)


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
    shutil.copyfile(rdat_name, '%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id, entry.rmdb_id))

    # Breaks Excel compatibility if data/columns are > 256
    if len(rdatfile.values.values()[0]) < 256:
        isatabfile.save('%s%s/%s_%s.xls' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version))
    write_annotations(rdatfile.annotations, entry, EntryAnnotation)

    data_count = 0
    construct_count = 0

    for k in rdatfile.constructs:
        construct_count += 1
        c = rdatfile.constructs[k]

        construct = ConstructSection(entry=entry, name=c.name, sequence=c.sequence, offset=c.offset, structure=c.structure, seqpos=','.join([str(x) for x in c.seqpos]), xsel=','.join([str(x) for x in c.xsel]))
        construct.save()

        for d in c.data:
            data = DataSection(xsel=','.join([str(x) for x in d.xsel]), values=','.join([str(x) for x in d.values]), errors=','.join([str(x) for x in d.errors]), trace=','.join([str(x) for x in d.trace]), reads=','.join([str(x) for x in d.reads]), seqpos=','.join([str(x) for x in d.seqpos]), construct_section=construct)
            data.save()
            data_count += len(d.values)

            construct_count += write_annotations(d.annotations, data, DataAnnotation)
        entry.data_count = data_count
        entry.construct_count = construct_count

        try:
            entry.is_trace = generate_images(construct, c, entry.type, engine='matplotlib')
        except TclError:
            error_msg.append('Problem generating the images. This is a server-side problem, please try again.')
            # proceed = False
        entry.save()
    
        generate_varna_thumbnails(entry)
        #precalculate_structures(entry)

    save_json(entry.rmdb_id)
    return (error_msg, entry)


def review_entry(new_stat, rmdb_id, cid):
    construct = ConstructSection.objects.get(id=cid)
    entry = RMDBEntry.objects.filter(id=construct.entry.id).order_by('-version')[0]
    if new_stat == "PUB":
        rdatfile = RDATFile()
        file_name = '%s%s/%s_%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], rmdb_id, rmdb_id, entry.version)
        if not os.path.isfile(file_name):
            file_name = '%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], rmdb_id, rmdb_id)
        rdatfile.load(open(file_name, 'r'))
        # for k in rdatfile.constructs:
        #     c = rdatfile.constructs[k]
        #     entry.is_trace = generate_images(construct, c, entry.type, engine='matplotlib')

        # generate_varna_thumbnails(entry)
        save_json(entry.rmdb_id)

    entry.status = new_stat
    entry.save()
