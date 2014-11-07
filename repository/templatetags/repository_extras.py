from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
register = template.Library()


def wordbreak(value, arg, autoescape=None):
    i = 0
    res = ''
    count = int(arg)
    if ',' in value:
	sv = value.split(',')
	for j in range(count, len(sv), count):
	    res += ','.join(sv[i:j]) + ',<wbr>'
	    i = j
	res += ','.join(sv[i:])
    else:
	for j in range(count, len(value), count):
	    res += value[i:j] + '&shy;'
	    i = j
	res += value[i:]
    return mark_safe(res)

wordbreak.needs_autoescape = True
register.filter('wordbreak', wordbreak)
