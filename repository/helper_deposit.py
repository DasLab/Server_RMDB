from rdatkit.datahandlers import RDATFile, ISATABFile

from email.mime.text import MIMEText
import os
import re
import smtplib

from rmdb.repository.models import *
from rmdb.repository.settings import *
from rmdb.settings import *
from helper_images import *

from Tkinter import TclError


def get_spreadsheet(url):
	url = os.popen('curl '+url+' -L -I -s -o /dev/null -w %{url_effective}').read().strip().replace('%3D','=').replace('%26','&')
	print url
	idx = url.find('key=')
	print idx
	if idx > 0:
		key = ''
		idx = idx + 4
		while url[idx] != '&' and idx < len(url):
			key += url[idx]
			idx += 1
		authkey = os.popen('curl https://www.google.com/accounts/ClientLogin \
							-d Email=stanfordrmdb@gmail.com -d Passwd=daslab4ever \
							-d accountType=HOSTED_OR_GOOGLE \
							-d source=Google-spreadsheet \
							-d service=wise | grep Auth | cut -d\= -f2').read().strip()
		os.popen('curl -L --silent --header "Authorization: GoogleLogin auth=%s"\
					"http://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&hl&exportFormat=xls" > /tmp/%s.xls' % (authkey, key, key))
		return '/tmp/%s.xls' % key
	else:
		return ''


def write_temp_file(file_name):
	tmp_file = open('/tmp/%s'%file_name.name, 'w')
	tmp_file.write(file_name.read())
	tmp_file.close()
	tmp_file = open('/tmp/%s'%file_name.name, 'r')
	return tmp_file


def validate_file(file_path, link_path, input_type):
	messages = []
	errors = []
	flag = 0

	if input_type == 'rdat':
		input_file = RDATFile()
	else:
		input_file = ISATABFile()

	is_continue = 1
	if link_path:
		if input_type == 'rdat':
			path = RDAT_FILE_DIR + link_path + '/' + link_path + '.rdat'
			is_continue = os.path.exists(path)
		else:
			is_continue = get_spreadsheet(link_path)

		print is_continue
		if not is_continue:
			if input_type == 'rdat':
				errors.append('Input RMDB ID: %s is invalid.' % link_path)
			else:
				errors.append('Input ISATAB file link_path: %s is invalid.' % link_path)
			return (errors, messages, 1)
		else:
			if input_type == 'rdat':
				input_file.load(open(path))
			else:
				input_file.load(is_continue)

	else:
		tmp_file = write_temp_file(file_path)
		try:
			input_file.load(tmp_file)
			messages = input_file.validate()
		except AttributeError, e:
			flag = 1
			errors.append('Invalid input file format: %s' % e)
		tmp_file.close()

	if not flag:
		if not messages:
			flag = 2
		else:
			flag = 3

	return (errors, messages, flag)


def send_email(subject, content, address):
	msg = MIMEText(content)
	msg['Subject']  = subject
	msg['To'] = address
	msg['From'] = SUBMISSION_HOST_EMAIL

	s = smtplib.SMTP(SUBMISSION_HOST_SMTP)
	s.starttls()
	s.login(SUBMISSION_HOST_EMAIL, SUBMISSION_HOST_PWD)
	s.sendmail(msg['From'], msg['To'], msg.as_string())
	s.quit()


def send_notify_emails(entry, request):
	msg_subject = 'RMDB: New entry submitted for review'
	msg_content = ('This is an email triggered by new RMDB entry submission automatically.\n\n' + 'Please review the following submission:\n' + 'RMDB_ID: %s\n' + 'Owner: %s\n' + 'Version: %s\n' + 'Status: %s\n\n' + 'Type: %s\n' + 'Construct(s): %s\n' + 'Data: %s\n' + 'Comments: %s\n' + 'Authors: %s\n' + 'Description: %s\n\n' + 'Please go to the admin page of this entry (http://rmdb.stanford.edu/admin/repository/rmdbentry/%s)\n and check its associated files in RDAT (http://rmdb.stanford.edu/site_media/rdat_files/%s/%s_synced.rdat)\n and ISATAB (http://rmdb.stanford.edu/site_media/isatab_files/%s/%s_%s.xls) formats. \n\n - RMDB server') % (entry.rmdb_id, entry.owner, entry.version, get_choice_type(entry.revision_status, ENTRY_STATUS_CHOICES), get_choice_type(entry.type, ENTRY_TYPE_CHOICES), entry.constructcount, entry.datacount, entry.comments, entry.authors, entry.description, entry.id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.version)
	send_email(msg_subject, msg_content, SUBMISSION_NOTIFY_EMAIL)
	msg_subject = 'Your RMDB Entry %s has been submitted' % entry.rmdb_id
	msg_content = ('This is an automatic email confirmation regarding the following new RMDB entry submission:\n' + 'RMDB_ID: %s\n' + 'Owner: %s\n' + 'Version: %s\n' + 'Status: %s\n\n' + 'Type: %s\n' + 'Construct(s): %s\n' + 'Data: %s\n' + 'Comments: %s\n' + 'Authors: %s\n' + 'Description: %s\n\n' + 'Your submission has been acknowledged by the RMDB team. We will review your entry shortly.\n\n For any questions, please feel free to contact us. Site admin can be reached at: %s \n\n\n Thank you for your submission,\nRMDB server') % (entry.rmdb_id, entry.owner, entry.version, get_choice_type(entry.revision_status, ENTRY_STATUS_CHOICES), get_choice_type(entry.type, ENTRY_TYPE_CHOICES), entry.constructcount, entry.datacount, entry.comments, entry.authors, entry.description, SUBMISSION_NOTIFY_EMAIL)
	send_email(msg_subject, msg_content, request.user.email)


def check_rmdb_id(id):
	m  = re.compile('\w{5,7}_\w{3,3}_\d{4,4}')
	if m.match(id):
		return True
	return False


def get_choice_type(string, collection):
	for i in range(len(collection)):
		if string in collection[i]:
			return collection[i][1]


def write_annotations(dictionary, section, annotation_model):
	count = 0
	for d in dictionary:
		for value in dictionary[d]:
			a = annotation_model()
			a.name = d.strip()
			if d.strip() in ('mutation', 'sequence'):
				count += 1
			a.value = str(value.decode('ascii', 'ignore'))
			a.section = section
			a.save()
	return count


def write_rmdb_file(entry, uploadfile, rdatfile, isatabfile, error_msg):
	if not os.path.exists('%s%s' % (RDAT_FILE_DIR, entry.rmdb_id)):
		os.mkdir('%s%s' % (RDAT_FILE_DIR, entry.rmdb_id))
	if not os.path.exists('%s%s' % (ISATAB_FILE_DIR, entry.rmdb_id)):
		os.mkdir('%s%s' % (ISATAB_FILE_DIR, entry.rmdb_id))

	rdatname = '%s%s/%s_%s.rdat' % (RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id, entry.version)
	os.popen('mv /tmp/%s %s' % (uploadfile.name, rdatname))
	os.popen('cp %s %s%s/%s.rdat' % (rdatname, RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id))
	os.popen('cp %s %s%s/%s_synced.rdat' % (rdatname, RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id))

	# Breaks Excel compatibility if data/columns are > 256
	if len(rdatfile.values.values()[0]) < 256:
		isatabfile.save('%s%s/%s_%s.xls' % (ISATAB_FILE_DIR, entry.rmdb_id, entry.rmdb_id, entry.version))
	write_annotations(rdatfile.annotations, entry, EntryAnnotation)

	data_count = 0
	construct_count = 0

	for k in rdatfile.constructs:
		construct_count += 1
		c = rdatfile.constructs[k]

		construct = ConstructSection()
		construct.entry = entry
		construct.name = c.name
		construct.sequence = c.sequence
		construct.offset = c.offset
		construct.structure = c.structure
		construct.seqpos = ','.join([str(x) for x in c.seqpos])
		construct.xsel = ','.join([str(x) for x in c.xsel])
		construct.save()
		#save_annotations(c.annotations, construct, ConstructAnnotation)

		for d in c.data:
			data = DataSection()
			data.xsel = ','.join([str(x) for x in d.xsel])
			data.values = ','.join([str(x) for x in d.values])
			data.errors = ','.join([str(x) for x in d.errors])
			data_count += len(d.values)
			data.trace = ','.join([str(x) for x in d.trace])
			data.reads = ','.join([str(x) for x in d.reads])
			entry.has_trace = False
			data.seqpos = ','.join([str(x) for x in d.seqpos])
			data.construct_section = construct
			data.save()

			construct_count += write_annotations(d.annotations, data, DataAnnotation)
		entry.datacount = data_count
		entry.constructcount = construct_count

		try:
			entry.has_traces = generate_images(construct, c, entry.type, engine='matplotlib')
		except TclError:
			error_msg.append('Problem generating the images. This is a server-side problem, please try again.')
			# proceed = False
		entry.save()
	
		generate_varna_thumbnails(entry)
		#precalculate_structures(entry)
	return error_msg


def submit_rmdb_entry(form, request, rdatfile, isatabfile):
	error_msg = []

	publication = Publication()
	publication.title = form.cleaned_data['publication']
	publication.authors = form.cleaned_data['authors']
	publication.pubmed_id = form.cleaned_data['pubmed_id']
	publication.save()

	entries = RMDBEntry.objects.filter(rmdb_id=form.cleaned_data['rmdb_id'].upper()).order_by('-version')
	if len(entries) > 0:
		prev_entry = entries[0]
		current_version = prev_entry.version
		owner = prev_entry.owner
	else:
		current_version = 0
		owner = None
	if current_version > 0 and owner != request.user and (not request.user.is_staff):
		error_msg.append('RMDB entry %s exists and you cannot update it since you are not the owner.' % request.POST['rmdb_id'])
		return error_msg

	entry = RMDBEntry()
	entry.comments = rdatfile.comments
	entry.publication = publication
	entry.authors = form.cleaned_data['authors']
	entry.description = form.cleaned_data['description']
	entry.type = form.cleaned_data['type']
	entry.rmdb_id = form.cleaned_data['rmdb_id'].upper()
	entry.datacount = 0	
	entry.constructcount = 0

	if request.user.is_staff:
		entry.revision_status = 'PUB'
	else:
		entry.revision_status = 'REV'
	entry.owner = request.user
	entry.version = current_version + 1
	if current_version == 0:
		entry.latest = True 
	entry.save()

	uploadfile = request.FILES['file']
	error_msg = write_rmdb_file(entry, uploadfile, rdatfile, isatabfile, error_msg)

	send_notify_emails(entry, request)
	return (error_msg, entry)



