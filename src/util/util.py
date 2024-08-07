import re
import simplejson
import smtplib
import time

# from django.core.mail import send_mail

from src.console import send_notify_emails as send_email_backup
from src.settings import *
from src.models import *


def try_get_stats(rmdb_id=''):
    file_name = '%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], rmdb_id) if rmdb_id else '%s/cache/stat_stats.json' % MEDIA_ROOT
    try:
        json = simplejson.load(open(file_name, 'r'))
        return (json, 1)
    except Exception:
        return (None, 0)


def do_get_stats(rmdb_id=''):
    (flag, i) = (0, 0)
    while flag == 0 and i < 5:
        (json, flag) = try_get_stats(rmdb_id)
        if json is None:
            i += 1
            time.sleep(1)
    return json


def get_entry_version(rmdb_id):
    entry_list = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version').values('version')
    ver_list = []
    for e in entry_list:
        ver_list.append(int(e['version']))
    return sorted(ver_list, reverse=True)


def temp_file(file_name):
    f = open('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_name.name), 'w')
    f.write(file_name.read())
    f.close()
    return open('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_name.name), 'r')


def check_rmdb_id(id):
    m = re.compile('\w{5,7}_\w{3,4}_\d{4,4}')
    return True if (m.match(id)) else False


def get_choice_type(string, collection):
    for i in xrange(len(collection)):
        if string in collection[i]:
            return collection[i][1]


def send_email(msg_subject, msg_content, msg_receipient):
    smtpserver = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    smtpserver.starttls()
    smtpserver.login(env('RMDB_GMAIL'), env('DJANGO_PASSWORD'))
    msg = 'Subject: %s\n\n%s' % (msg_subject, msg_content)
    smtpserver.sendmail(env('RMDB_GMAIL'), msg_receipient, msg)
    smtpserver.quit()


def send_notify_emails(entry, user_email):
    if entry.status != 'PUB':
        msg_subject = 'RMDB: New entry submitted for review'
        msg_content = ('This is an email triggered by new RMDB entry submission automatically.\n\n' + 'Please review the following submission:\n' + 'RMDB_ID: %s\n' + 'Owner: %s\n' + 'Version: %s\n' + 'Status: %s\n\n' + 'Type: %s\n' + 'Construct(s): %s\n' + 'Data: %s\n' + 'Comments: %s\n' + 'Authors: %s\n' + 'Description: %s\n\n' + 'Please go to the admin page of this entry (http://rmdb.stanford.edu/admin/repository/rmdbentry/%s)\n and check its associated files in RDAT (http://rmdb.stanford.edu/site_data/file/%s/%s.rdat)\n and ISATAB (http://rmdb.stanford.edu/site_data/file/%s/%s_%s.xls) formats. \n\n - RMDB server') % (entry.rmdb_id, entry.owner, entry.version, get_choice_type(entry.status, ENTRY_STATUS_CHOICES), get_choice_type(entry.type, ENTRY_TYPE_CHOICES), entry.construct_count, entry.data_count, entry.comments, entry.authors, entry.description, entry.id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.version)
        try:
            send_email(msg_subject, msg_content, EMAIL_NOTIFY)
        except Exception:
            send_email_backup(msg_subject, '!! FAILURE on stanfordrmdb@stanford.edu Email account !!\n\n' + msg_content)


    msg_subject = 'Your RMDB Entry %s has been submitted' % entry.rmdb_id
    msg_content = ('This is an automatic email confirmation regarding the following new RMDB entry submission:\n' + 'RMDB_ID: %s\n' + 'Owner: %s\n' + 'Version: %s\n' + 'Status: %s\n\n' + 'Type: %s\n' + 'Construct(s): %s\n' + 'Data: %s\n' + 'Comments: %s\n' + 'Authors: %s\n' + 'Description: %s\n\n' + 'Your submission has been acknowledged by the RMDB team. We will review your entry shortly.\n\n For any questions, please feel free to contact us. Site admin can be reached at: %s \n\n\n Thank you for your submission,\nRMDB server') % (entry.rmdb_id, entry.owner, entry.version, get_choice_type(entry.status, ENTRY_STATUS_CHOICES), get_choice_type(entry.type, ENTRY_TYPE_CHOICES), entry.construct_count, entry.data_count, entry.comments, entry.authors, entry.description, EMAIL_NOTIFY)
    try:
        send_email(msg_subject, msg_content, user_email)
    except Exception:
        pass

