from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from src.models import *

register = template.Library()


def color_rmdb_id(value):
    if ('_' not in value):
        return value

    string = value.split('_')
    s1 = '<span style="color: yellow;">' + string[1] + '</span>'
    s2 = '<span style="color: skyblue;">' + string[2] + '</span>' 
    return string[0] + '<span style="color: lightpink;">_</span>' + s1 + '<span style="color: lightpink;">_</span>' + s2
register.filter('color_rmdb_id', color_rmdb_id)


def color_eterna_id(value):
    if ('_' not in value):
        return value

    string = value.split('_')
    s1 = '<span style="color: yellowgreen;">'+string[1]+'</span>'
    s2 = '<span style="color: skyblue;">'+string[2]+'</span>' 
    return string[0] + '<span style="color: lightpink;">_</span>' + s1 + '<span style="color: lightpink;">_</span>' + s2
register.filter('color_eterna_id', color_eterna_id)


def get_exp_type(string):
    if string == "SS" or string == "DC":
        string = '<span class="label label-primary">Standard State</span>'
    elif string == "TT":
        string = '<span class="label label-warning">Titration</span>'
    elif string == "MM":
        string = '<span class="label label-success">Mutate And Map</span>'
    elif string == "MR":
        string = '<span class="label label-info">Mutation Rescue</span>'
    elif string == "MA":
        string = '<span class="label label-danger">MOHCA</span>'
    else:
        string = '<span class="label label-default">Unknown</span>'
    return string
register.filter('get_exp_type', get_exp_type)


def get_rev_stat(string):
    if string == 'REC':
        string = '<span class="label label-info">Received</span>'
    elif string == "REV":
        string = '<span class="label label-warning">In Review</span>'
    elif string == "HOL":
        string = '<span class="label label-danger">On Hold</span>'
    elif string == "PUB":
        string = '<span class="label label-success">Published</span>'
    else:
        string = '<span class="label label-default">Unknown</span>'
    return string
register.filter('get_rev_stat', get_rev_stat)

