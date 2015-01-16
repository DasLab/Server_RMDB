from django.contrib.auth.models import User
from django.db import models
from django import forms

from rmdb.repository.settings import *

import os
from simplejson import JSONEncoder


def get_rdat_filename(instance, filename):
    dir = RDAT_FILE_DIR+'%s/'%instance.id
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir+'%s.rdat'%instance.id

ENTRY_TYPE_CHOICES = (
    ('SS', 'StandardState'),
    ('MM', 'MutateAndMap'),
    ('MA', 'MOHCA'),
    ('TT', 'Titration'),
)

MODIFIERS = (
    ('SHP', 'SHAPE'),
    ('DMS', 'DMS'),
    ('CMC', 'CMCT'),
    ('NMD', 'No modification'),
)

FORMAT_TYPE_CHOICES = (
    ('rdat', 'RDAT'),
    ('isatab', 'ISATAB'),
)

ENTRY_STATUS_CHOICES = (
    ('REC', 'Received'),
    ('REV', 'In review'),
    ('HOL', 'On hold'),
    ('PUB', 'Published'),
)

SEC_STRUCT_ELEMS_CHOICES = (
    ('dangles', 'Dangles'),
    ('bulges', 'Bulges'),
    ('hairpins', 'Hairpins'),
    ('interiorloops', 'Interior Loops'),
    ('helices', 'Helices'),
    ('3wayjunctions', '3-way Junctions'),
    ('4wayjunctions', '4-way Junctions'),
#    ('5wayjunctions', '5-way Junctions'),
)

class RMDBJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Publication):
            jdict = {}
            for att in obj.__dict__:
                if att[0] != '_':
                    jdict[att] = obj.__dict__[att]
            return jdict
        if isinstance(obj, Organism):
            jdict = {}
            for att in obj.__dict__:
                if att[0] != '_' and att[0] != 'id':
                    jdict[att.replace('taxonomy_id', 'id')] = obj.__dict__[att]
            return jdict

        if isinstance(obj, RMDBEntry):
            entrydict = {}
            entrydict['rmdb_id'] = obj.rmdb_id
            entrydict['comments'] = obj.comments
            if obj.publication:
                entrydict['publication'] = self.default(obj.publication)
            else:
                entrydict['publication'] = {}
            entrydict['authors'] = obj.authors.split(',')
            entrydict['description'] = obj.description
            entrydict['type'] = obj.type
            entrydict['revision_status'] = obj.revision_status
            entrydict['creation_date'] = str(obj.creation_date)
            entrydict['from_eterna'] = obj.from_eterna
            if obj.pdb_entries:
                entrydict['pdb_entries'] = obj.pdb_entries.split(',')
            else:
                entrydict['pdb_entries'] = []
            if 'constructs' in obj.__dict__:
                entrydict['constructs'] = [self.default(c) for c in obj.constructs]
            if 'annotations' in obj.__dict__:
                entrydict['annotations'] = dict([self.default(a) for a in obj.annotations])
            return entrydict

        if isinstance(obj, DataAnnotation) or isinstance(obj, EntryAnnotation):
            return (obj.name, obj.value)

        if isinstance(obj, ConstructSection):
            constructdict = {}
            for att in obj.__dict__:
                if att == 'entry' or att[0] == '_':
                    continue
                elif att == 'annotations':
                    datadict['annotations'] = dict([self.default(a) for a in obj.annotations])
                elif att == 'datas':
                    constructdict['data_sections'] = [self.default(d) for d in obj.datas]
                elif att in ['mutpos', 'seqpos', 'xsel']:
                    if len(obj.__dict__[att]) > 0:
                        constructdict[att] = [i for i in obj.__dict__[att].strip('[]').split(',')]
                elif att == 'offset':
                    constructdict[att] = int(obj.offset)
                else:
                    constructdict[att] = obj.__dict__[att]
            return constructdict

        if isinstance(obj, DataSection):
            datadict = {}
            for att in obj.__dict__:
                if att == 'construct_section' or att[0] == '_':
                    continue
                elif att == 'annotations':
                    datadict['annotations'] = dict([self.default(a) for a in obj.annotations])
                elif att in ['seqpos', 'xsel', 'values', 'errors', 'error', 'trace', 'reads']:
                    if obj.__dict__[att] is not None and len(obj.__dict__[att]) > 0:
                        datadict[att] = [float(i) for i in obj.__dict__[att].strip('[]').split(',')]
                else:
                    datadict[att] = obj.__dict__[att]

            return datadict
        return JSONEncoder().encode(obj)



class NewsItem(models.Model):
    title = models.TextField()
    reference = models.CharField(max_length=400, blank=True)
    date = models.DateField()


class Publication(models.Model):
    title = models.TextField()
    authors = models.TextField()
    pubmed_id = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s;PMID:%s' % (self.authors, self.pubmed_id)


class Organism(models.Model):
    name = models.TextField()
    taxonomy_id = models.TextField()

    def __unicode__(self):
        return u'%s;TAXID:%s' % (self.name, self.taxonomy_id)


class RMDBEntry(models.Model):
    version = models.CharField(max_length=10)
    comments = models.TextField()
    publication = models.ForeignKey(Publication)
    authors = models.TextField()
    description = models.TextField(blank=True)
    latest = models.BooleanField(default=False)
    type = models.CharField(max_length=3, choices=ENTRY_TYPE_CHOICES)
    datacount = models.IntegerField()
    constructcount = models.IntegerField()
    revision_status = models.CharField(max_length=3, choices=ENTRY_STATUS_CHOICES)
    file = models.FileField(upload_to=get_rdat_filename, blank=True, null=True)
    rmdb_id = models.CharField(max_length=25, null=True)
    owner = models.ForeignKey(User, null=True)
    version = models.IntegerField()
    has_traces = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now=True, null=True)
    from_eterna = models.BooleanField(default=False)
    pdb_entries = models.CharField(max_length=255, null=True, blank=True)
    organism = models.ForeignKey(Organism, null=True, blank=True)

    def short_description(self):
        return self.description[:200]+'...'

    @classmethod
    def get_current_version(self, rmdb_id):
        return RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')[0].version


class ConstructSection(models.Model):
    entry = models.ForeignKey(RMDBEntry)
    name = models.CharField(max_length=255)
    sequence = models.TextField()
    offset = models.IntegerField()
    xsel = models.TextField(blank=True)
    seqpos = models.TextField()
    mutpos = models.TextField(blank=True)
    structure = models.TextField()


class DataSection(models.Model):
    construct_section = models.ForeignKey(ConstructSection)
    trace = models.TextField()
    reads = models.TextField(null=True)
    xsel = models.TextField()
    values = models.TextField()
    errors = models.TextField()
    seqpos = models.TextField()
    structure = models.TextField(null=True)


class EntryAnnotation(models.Model):
    section = models.ForeignKey(RMDBEntry)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)


class DataAnnotation(models.Model):
    section = models.ForeignKey(DataSection)
    name = models.CharField(max_length=255)
    value = models.TextField()


class RMDBUser(models.Model):
    user = models.OneToOneField(User)
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255)


class UploadForm(forms.Form):
    file = forms.FileField()
    publication = forms.CharField(required=False)
    pubmed_id = forms.CharField(required=False)
    authors = forms.CharField(required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    rmdb_id = forms.CharField(required=True)
    type = forms.ChoiceField(choices=ENTRY_TYPE_CHOICES)
    filetype = forms.ChoiceField(choices=FORMAT_TYPE_CHOICES)


class RegistrationForm(forms.Form):
    username = forms.CharField(required=True, max_length=31)
    password = forms.CharField(widget=forms.PasswordInput, max_length=63)
    repeatpassword = forms.CharField(widget=forms.PasswordInput, max_length=63)
    firstname = forms.CharField(required=True, max_length=255)
    lastname = forms.CharField(required=True, max_length=255)
    institution = forms.CharField(required=True, max_length=255)
    department = forms.CharField(required=True, max_length=255)
    email = forms.EmailField(required=True, max_length=255)


class ValidateForm(forms.Form):
    file = forms.FileField(required=False)
    link = forms.CharField()
    type = forms.ChoiceField(choices=FORMAT_TYPE_CHOICES)


class AdvancedSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        self.fields['modifiers'].initial = [m[0] for m in MODIFIERS]
        self.fields['entry_type'].initial = [et[0] for et in ENTRY_TYPE_CHOICES]
        self.fields['numresults'].initial = '200'

    sequence = forms.CharField()
    structure = forms.CharField()
    secstructelems = forms.MultipleChoiceField(choices=SEC_STRUCT_ELEMS_CHOICES, widget=forms.CheckboxSelectMultiple)
    include_eterna = forms.BooleanField(initial=True)
    entry_type = forms.MultipleChoiceField(choices=ENTRY_TYPE_CHOICES, widget=forms.CheckboxSelectMultiple)
    modifiers = forms.MultipleChoiceField(choices=MODIFIERS, widget=forms.CheckboxSelectMultiple)
    background_processed = forms.BooleanField(initial=True)
    numresults = forms.IntegerField(widget=forms.TextInput(attrs={'size':'10'}))



