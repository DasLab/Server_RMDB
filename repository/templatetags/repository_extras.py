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


def get_construct_dataset_type(value, args):

	for i in value.entries:
		if args in i.get_type_display():
			return 1
	return 0
register.filter('get_construct_dataset_type', get_construct_dataset_type)


def color_rmdb_id(value):

	string = value.split('_')
	s1 = '<span style=\"color: yellow;\">'+string[1]+'</span>'
	s2 = '<span style=\"color: skyblue;\">'+string[2]+'</span>'	
	return string[0] + '<span style=\"color: lightpink;\">_</span>' + s1 + '<span style=\"color: lightpink;\">_</span>' + s2
register.filter('color_rmdb_id', color_rmdb_id)



