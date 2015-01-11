
from django.contrib.auth.forms import AuthenticationForm


def include_login_form(request):
    login_form = AuthenticationForm()
    return {'login_form': login_form}