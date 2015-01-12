

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
	if len(user_name) < 3:
	 	error_msg.append('Username must be at least 3 characters.')
	if len(password_1) < 6 or len(password_2) < 6:
	 	error_msg.append('Password must be at least 6 characters.')
	if len(first_name) < 3:
	 	error_msg.append('First name must be at least 3 characters.')
	if len(last_name) < 2:
	 	error_msg.append('Last name must be at least 2 characters.')
	if len(institution) < 4:
	 	error_msg.append('Institution must be at least 4 characters.')
	if len(department) < 4:
	 	error_msg.append('Department must be at least 4 characters.')
	if len(email) < 6:
	 	error_msg.append('Email too short.')

	return error_msg
