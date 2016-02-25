from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from src.models import *

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


def get_stt_type(string):
    if string == 'REC':
        return '<span class=\"label label-info\">Received</span>'
    elif string == "REV":
        return '<span class=\"label label-warning\">In Review</span>'
    elif string == "HOL":
        return '<span class=\"label label-danger\">On Hold</span>'
    elif string == "PUB":
        return '<span class=\"label label-success\">Published</span>'
register.filter('get_stt_type', get_stt_type)



def get_annotation_item(a_all, key):
    val = a_all[key]
    string = ''
    for i,v in enumerate(val):
        if i != len(val)-1:
            string += '<p style=\"padding-bottom:5px;\"><span class=\"label label-warning\">' + v + '</span></p>'
        else:
            string += '<span class=\"label label-warning\">' + v + '</span>'

    return string
register.filter('get_annotation_item', get_annotation_item)


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


def get_plot_idx(hist_data, idx):
    print idx
    return ''
register.filter('get_plot_idx', get_plot_idx)



