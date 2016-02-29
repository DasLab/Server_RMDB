import re

from django.core.mail import send_mail

from src.models import *


def temp_file(file_name):
    open('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_name.name), 'w').write(file_name.read())
    return open('%s/%s' % (PATH.DATA_DIR['TMP_DIR'], file_name.name), 'r')


def check_rmdb_id(id):
    m = re.compile('\w{5,7}_\w{3,4}_\d{4,4}')
    return True if (m.match(id)) else False


def get_choice_type(string, collection):
    for i in range(len(collection)):
        if string in collection[i]:
            return collection[i][1]


def send_notify_emails(entry, request):
    msg_subject = 'RMDB: New entry submitted for review'
    msg_content = ('This is an email triggered by new RMDB entry submission automatically.\n\n' + 'Please review the following submission:\n' + 'RMDB_ID: %s\n' + 'Owner: %s\n' + 'Version: %s\n' + 'Status: %s\n\n' + 'Type: %s\n' + 'Construct(s): %s\n' + 'Data: %s\n' + 'Comments: %s\n' + 'Authors: %s\n' + 'Description: %s\n\n' + 'Please go to the admin page of this entry (http://rmdb.stanford.edu/admin/repository/rmdbentry/%s)\n and check its associated files in RDAT (http://rmdb.stanford.edu/site_data/files/%s/%s.rdat)\n and ISATAB (http://rmdb.stanford.edu/site_data/files/%s/%s_%s.xls) formats. \n\n - RMDB server') % (entry.rmdb_id, entry.owner, entry.version, get_choice_type(entry.status, ENTRY_STATUS_CHOICES), get_choice_type(entry.type, ENTRY_TYPE_CHOICES), entry.construct_count, entry.data_count, entry.comments, entry.authors, entry.description, entry.id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.version)
    send_mail(msg_subject, msg_content, EMAIL_HOST_USER, [EMAIL_NOTIFY])
    msg_subject = 'Your RMDB Entry %s has been submitted' % entry.rmdb_id
    msg_content = ('This is an automatic email confirmation regarding the following new RMDB entry submission:\n' + 'RMDB_ID: %s\n' + 'Owner: %s\n' + 'Version: %s\n' + 'Status: %s\n\n' + 'Type: %s\n' + 'Construct(s): %s\n' + 'Data: %s\n' + 'Comments: %s\n' + 'Authors: %s\n' + 'Description: %s\n\n' + 'Your submission has been acknowledged by the RMDB team. We will review your entry shortly.\n\n For any questions, please feel free to contact us. Site admin can be reached at: %s \n\n\n Thank you for your submission,\nRMDB server') % (entry.rmdb_id, entry.owner, entry.version, get_choice_type(entry.status, ENTRY_STATUS_CHOICES), get_choice_type(entry.type, ENTRY_TYPE_CHOICES), entry.construct_count, entry.data_count, entry.comments, entry.authors, entry.description, EMAIL_NOTIFY)
    send_mail(msg_subject, msg_content, EMAIL_HOST_USER, [request.user.email])

