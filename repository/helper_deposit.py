from rdatkit.datahandlers import RDATFile, ISATABFile

import os

from settings import *



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
		tmp_file = open('/tmp/%s'%file_path.name, 'w')
		tmp_file.write(file_path.read())
		tmp_file.close()
		tmp_file = open('/tmp/%s'%file_path.name)
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

