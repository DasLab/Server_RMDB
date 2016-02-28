from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from src.models import *

register = template.Library()


def color_rmdb_id(value):
    if ('_' not in value):
        return value

    string = value.split('_')
    s1 = '<span style=\"color: yellow;\">'+string[1]+'</span>'
    s2 = '<span style=\"color: skyblue;\">'+string[2]+'</span>' 
    return string[0] + '<span style=\"color: lightpink;\">_</span>' + s1 + '<span style=\"color: lightpink;\">_</span>' + s2
register.filter('color_rmdb_id', color_rmdb_id)


def color_eterna_id(value):
    if ('_' not in value):
        return value

    string = value.split('_')
    s1 = '<span style=\"color: yellowgreen;\">'+string[1]+'</span>'
    s2 = '<span style=\"color: skyblue;\">'+string[2]+'</span>' 
    return string[0] + '<span style=\"color: lightpink;\">_</span>' + s1 + '<span style=\"color: lightpink;\">_</span>' + s2
register.filter('color_eterna_id', color_eterna_id)


def warning_strip(value):
    return value[8:]
register.filter('warning_strip', warning_strip)


def get_exp_type(string):
    for i in range(len(ENTRY_TYPE_CHOICES)):
        if string in ENTRY_TYPE_CHOICES[i]:
            return ENTRY_TYPE_CHOICES[i][1]
register.filter('get_exp_type', get_exp_type)


def get_rev_stat(string):
    if string == 'REC':
        return '<span class=\"label label-info\">Received</span>'
    if string == "REV":
        return '<span class=\"label label-warning\">In Review</span>'
    if string == "HOL":
        return '<span class=\"label label-danger\">On Hold</span>'
    if string == "PUB":
        return '<span class=\"label label-success\">Published</span>'
register.filter('get_rev_stat', get_rev_stat)

