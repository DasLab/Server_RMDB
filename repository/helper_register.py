import string


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
	password_2 = form.cleaned_data['repeatpassword']
	first_name = form.cleaned_data['firstname']
	last_name = form.cleaned_data['lastname']
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
