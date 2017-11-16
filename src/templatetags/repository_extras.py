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


'''
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
'''


def get_rev_stat(string):
    if string == "PUB":
        string = '<span class="label label-success">Published</span>'
    elif string == "UNP":
        string = '<span class="label label-success">Unpublished</span>'
    else:
        string = '<span class="label label-default">Unknown</span>'
    return string
register.filter('get_rev_stat', get_rev_stat)


def get_status(string):
    if string == "PUB":
        string = 'Published'
    elif string == "UNP":
        string = 'Unpublished'
    else:
        string = 'Unknown'
    return string
register.filter('get_status', get_status)


def get_entry_field(string):
    if string == "entry_status":
        string = 'Status'
    elif string == "description":
        string = 'Description'
    elif string == "authors":
        string = 'Authors'
    elif string == "pubmed_id":
        string = 'Pubmed ID'
    elif string == "publication_title":
        string = 'Publication Title'
    return string
register.filter('get_entry_field', get_entry_field)


def get_user_field(string):
    if string == "first_name":
        string = 'First Name'
    elif string == "last_name":
        string = 'Last Name'
    elif string == "institution":
        string = 'Institution'
    elif string == "department":
        string = 'Department'
    elif string == "email":
        string = 'Email'
    return string
register.filter('get_user_field', get_user_field)
