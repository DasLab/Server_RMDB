from django.contrib.auth.models import User
from django.db import models
from django import forms
# from django.utils.html import format_html

from src.settings import *

import simplejson

# def get_rdat_file(instance, filename):
#     file_dir = '%s%s/' % (PATH.DATA_DIR['FILE_DIR'], instance.id)
#     if not os.path.exists(file_dir): os.mkdir(file_dir)
#     return '%s%s.rdat' % (file_dir, instance.id)


ENTRY_TYPE_CHOICES = (
    ('SS', 'Standard State'),
    ('MM', 'Mutate And Map'),
    ('MA', 'MOHCA'),
    ('TT', 'Titration'),
)

ENTRY_STATUS_CHOICES = (
    ('REC', 'Received'),
    ('REV', 'Under Review'),
    ('HOL', 'On Hold'),
    ('PUB', 'Published'),
)

DOWNLOAD_SRC_CHOICES = (
    ('reeffit', 'REEFFIT'),
    ('mapseeker', 'MAPseeker'),
    ('hitrace', 'HiTRACE'),
    ('rdatkit', 'RDATKit'),
    ('biers', 'Biers'),
)


class NewsItem(models.Model):
    date = models.DateField(verbose_name='Display Date')
    content = models.TextField(blank=True, verbose_name='Main Text Content', help_text='<span class="glyphicon glyphicon-edit"></span>&nbsp;HTML supported.')

    class Meta():
        verbose_name = 'News Item'
        verbose_name_plural = 'News Items'


class HistoryItem(models.Model):
    date = models.DateField(verbose_name='Display Date')
    content = models.TextField(blank=False, verbose_name='HTML Content', help_text='<span class="glyphicon glyphicon-edit"></span>&nbsp;HTML supported.')

    class Meta():
        verbose_name = 'History Item'
        verbose_name_plural = 'History Items'


class Publication(models.Model):
    title = models.TextField(help_text='<i class="icon-bullhorn"></i> Do <span class="label label-danger">NOT</span> use "CamelCase / InterCaps / CapWords". Only capitalize the first word.')
    authors = models.TextField(help_text='<span class="glyphicon glyphicon-user"></span>&nbsp; Follow the format seen on the website: <span class="label label-inverse">Das, R.,</span>.')
    pubmed_id = models.CharField(max_length=30, verbose_name='PubMed ID')

    def __unicode__(self):
        au = self.authors[:self.authors.find(' ')]
        return u'# %d : %s et al.; PM_ID:%s; %s ...' % (self.id, au, self.pubmed_id, self.title[:30])

    class Meta():
        verbose_name = 'Publication Entry'
        verbose_name_plural = 'Publication Entries'


class Organism(models.Model):
    name = models.CharField(max_length=255, verbose_name='Organism Name', help_text='<i class="icon-bullhorn"></i> Use binomial nomenclature.')
    tax_id = models.IntegerField(verbose_name='Taxonomy ID', help_text='<i class="icon-credit-card"></i> Follow <a href="http://www.ncbi.nlm.nih.gov/taxonomy/" target="_blank">http://www.ncbi.nlm.nih.gov/taxonomy/&nbsp;<i class="icon-new-window"></i></a>.')

    def __unicode__(self):
        return u'%s; TAX_ID:%s' % (self.name, self.tax_id)


class RMDBEntry(models.Model):
    rmdb_id = models.CharField(max_length=25, null=True, verbose_name='RMDB ID')
    owner = models.ForeignKey(User, null=True)
    # file = models.FileField(upload_to=get_rdat_file, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now=True, null=True)

    version = models.IntegerField(default=1, verbose_name='Revision')
    status = models.CharField(max_length=3, choices=ENTRY_STATUS_CHOICES)
    type = models.CharField(max_length=3, choices=ENTRY_TYPE_CHOICES, verbose_name='Experiment Type')
    supercede_by = models.CharField(max_length=25, null=True, blank=True, verbose_name='Superceded By', help_text='<span class="glyphicon glyphicon-share"></span>&nbsp;<span class="label label-danger">RMDB_ID</span> of entry that supercedes this one. Leave emtpy if does not apply.')

    authors = models.TextField(help_text='<span class="glyphicon glyphicon-user"></span>&nbsp; Follow the format seen on the website: <span class="label label-inverse">Das, R.,</span>.')
    description = models.TextField(blank=True, help_text='<span class="glyphicon glyphicon-edit"></span>&nbsp;Description of this entry submitted by user.')
    comments = models.TextField(blank=True, help_text='<span class="glyphicon glyphicon-edit"></span>&nbsp;Description of this entry from the RDAT file.')
    pdb = models.CharField(max_length=255, null=True, blank=True, verbose_name='PDB Entries')
    organism = models.ForeignKey(Organism, null=True, blank=True)
    publication = models.ForeignKey(Publication)

    data_count = models.IntegerField(verbose_name='Data Count')
    construct_count = models.IntegerField(verbose_name='Construct Count')
    is_trace = models.BooleanField(default=False, verbose_name='Contans TRACE Field?', help_text='<span class="glyphicon glyphicon-check"></span>&nbsp; Check if this entry has data in TRACE field.')
    is_eterna = models.BooleanField(default=False, verbose_name='Is Eterna Dataset?', help_text='<span class="glyphicon glyphicon-check"></span>&nbsp; Check if this entry is from Eterna.')

    def short_desp(self):
        return self.description[:100] + '...'
    short_desp.short_description = 'Short Description'
    short_desp.admin_order_field = 'description'

    @classmethod
    def get_current_version(self, rmdb_id):
        return RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')[0].version

    class Meta():
        verbose_name = 'RMDB Entry'
        verbose_name_plural = 'RMDB Entries'


class ConstructSection(models.Model):
    entry = models.ForeignKey(RMDBEntry)
    name = models.CharField(max_length=255, verbose_name='NAME')
    sequence = models.TextField(verbose_name='SEQUENCE')
    offset = models.IntegerField(verbose_name='OFFSET')
    xsel = models.TextField(blank=True, verbose_name='XSEL')
    seqpos = models.TextField(verbose_name='SEQPOS')
    mutpos = models.TextField(blank=True, verbose_name='MUTPOS')
    structure = models.TextField(verbose_name='STRUCTURE')


class DataSection(models.Model):
    construct_section = models.ForeignKey(ConstructSection)
    trace = models.TextField(verbose_name='TRACE')
    reads = models.TextField(null=True, verbose_name='READS')
    xsel = models.TextField(verbose_name='XSEL')
    values = models.TextField(verbose_name='VALUES')
    errors = models.TextField(verbose_name='ERRORS')
    seqpos = models.TextField(verbose_name='SEQPOS')
    structure = models.TextField(null=True, verbose_name='STRUCTURE')


class EntryAnnotation(models.Model):
    section = models.ForeignKey(RMDBEntry)
    name = models.CharField(max_length=255, verbose_name='NAME')
    value = models.CharField(max_length=255, verbose_name='VALUE')


class DataAnnotation(models.Model):
    section = models.ForeignKey(DataSection)
    name = models.CharField(max_length=255, verbose_name='NAME')
    value = models.TextField(verbose_name='VALUE')


class RMDBUser(models.Model):
    user = models.OneToOneField(User)
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    data_count = models.IntegerField(verbose_name='Total Data Count')
    construct_count = models.IntegerField(verbose_name='Total Construct Count')
    entry_count = models.IntegerField(verbose_name='Total Entries')
    last_entry = models.CharField(max_length=25, null=True, verbose_name='Last Submitted RMDB ID')
    last_date = models.DateField(null=True, verbose_name='Last Submission Date')

    def __unicode__(self):
        if not self.user:
            return '__(None)__'
        return self.user.username

    class Meta():
        verbose_name = 'RMDB User'
        verbose_name_plural = 'RMDB Users'

    def full_name(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'user.first_name'

    def affiliation(self):
        return '%s - %s' % (self.institution, self.department)
    affiliation.admin_order_field = 'institution'


class SourceDownloader(models.Model):
    date = models.DateField(verbose_name='Request Date')
    package = models.CharField(max_length=3, choices=DOWNLOAD_SRC_CHOICES)
    rmdb_user = models.ForeignKey(RMDBUser, verbose_name='RMDB User')

    class Meta():
        verbose_name = 'Source Downloader'
        verbose_name_plural = 'Source Downloaders'


############################################################################################################################################

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


SEC_STRUCT_ELEMS_CHOICES = (
    ('dangles', 'Dangles'),
    ('bulges', 'Bulges'),
    ('hairpins', 'Hairpins'),
    ('interiorloops', 'Interior Loops'),
    ('helices', 'Helices'),
    ('3wayjunctions', '3-way Junctions'),
    ('4wayjunctions', '4-way Junctions'),
)

PRED_TYPE_CHOICES = (
    ('1D', '  1-Dimensional (Traditional Chemical Mapping)  '),
    ('2D', '  2-Dimensional (Mutate-and-Map)  '),
    ('NN', '  None (No data)  '),
)

MOD_TYPE_CHOICES = (
    ('SHAPE', 'SHAPE'),
    ('DMS', 'DMS'),
    ('CMCT', 'CMCT'),
)

EXEC_TYPE_CHOICES = (
    ('Fold', 'Fold'),
    ('Spkt', 'ShapeKnots')
)


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    flag = forms.CharField(required=True)


class RegisterForm(forms.Form):
    username = forms.CharField(required=True, max_length=31)
    password = forms.CharField(widget=forms.PasswordInput, max_length=63)
    repeat_password = forms.CharField(widget=forms.PasswordInput, max_length=63)
    first_name = forms.CharField(required=True, max_length=255)
    last_name = forms.CharField(required=True, max_length=255)
    institution = forms.CharField(required=True, max_length=255)
    department = forms.CharField(required=True, max_length=255)
    email = forms.EmailField(required=True, max_length=255)


class SearchForm(forms.Form):
    sstring = forms.CharField(required=True, max_length=63)


class UploadForm(forms.Form):
    exp_type = forms.ChoiceField(required=True, choices=ENTRY_TYPE_CHOICES)
    file_type = forms.ChoiceField(required=True, choices=FORMAT_TYPE_CHOICES)
    file = forms.FileField(required=True)

    rmdb_id = forms.CharField(required=True, max_length=25)
    publication = forms.CharField(required=False, max_length=255)
    pubmed_id = forms.CharField(required=False, max_length=31)
    authors = forms.CharField(required=True, max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)


class ReviewForm(forms.Form):
    new_stat = forms.ChoiceField(required=True, choices=ENTRY_STATUS_CHOICES)
    rmdb_id = forms.CharField(required=True)


class ValidateForm(forms.Form):
    file_type = forms.ChoiceField(required=True, choices=FORMAT_TYPE_CHOICES)
    file = forms.FileField(required=False)
    link = forms.CharField(required=False)


# class AdvancedSearchForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super(AdvancedSearchForm, self).__init__(*args, **kwargs)
#         self.fields['modifiers'].initial = [m[0] for m in MODIFIERS]
#         self.fields['entry_type'].initial = [et[0] for et in ENTRY_TYPE_CHOICES]
#         self.fields['numresults'].initial = '200'

#     sequence = forms.CharField()
#     structure = forms.CharField()
#     secstructelems = forms.MultipleChoiceField(choices=SEC_STRUCT_ELEMS_CHOICES, widget=forms.CheckboxSelectMultiple)
#     include_eterna = forms.BooleanField(initial=True)
#     entry_type = forms.MultipleChoiceField(choices=ENTRY_TYPE_CHOICES, widget=forms.CheckboxSelectMultiple)
#     modifiers = forms.MultipleChoiceField(choices=MODIFIERS, widget=forms.CheckboxSelectMultiple)
#     background_processed = forms.BooleanField(initial=True)
#     numresults = forms.IntegerField(widget=forms.TextInput(attrs={'size':'10'}))


# class VisualizerForm(forms.Form):
#     sequences = forms.CharField(widget=forms.Textarea)
#     structures = forms.CharField(widget=forms.Textarea)
#     md_datas = forms.CharField(widget=forms.Textarea)
#     md_seqposes = forms.CharField(widget=forms.Textarea)
#     modifiers = forms.CharField(widget=forms.Textarea)
#     titles = forms.CharField(widget=forms.Textarea)
#     base_annotations = forms.CharField(widget=forms.Textarea)
#     refstruct = forms.CharField()


class PredictionForm(forms.Form):
    sequences = forms.CharField(widget=forms.Textarea)
    structures = forms.CharField(widget=forms.Textarea)
    annotations = forms.CharField(widget=forms.Textarea)
    clipsequence = forms.BooleanField(initial=False)
    bonusfile = forms.FileField()
    rdatfile = forms.FileField()
    rmdbid = forms.CharField(required=False)

    modtype = forms.ChoiceField(choices=MOD_TYPE_CHOICES)
    bonuses_1d = forms.CharField(widget=forms.Textarea)
    slope_1d = forms.CharField(initial='2.6')
    intercept_1d = forms.CharField(initial='-0.8')
    raw_bonuses = forms.BooleanField(initial=False)

    bonuses_2d = forms.CharField(widget=forms.Textarea)
    slope_2d = forms.CharField(initial='1.0')
    intercept_2d = forms.CharField(initial='0.0')
    applyzscores = forms.BooleanField(initial=True)

    predtype = forms.ChoiceField(choices=PRED_TYPE_CHOICES)
    normalize = forms.BooleanField(initial=True)
    temperature = forms.CharField(initial='37')
    executable = forms.ChoiceField(choices=EXEC_TYPE_CHOICES)
    refstruct = forms.CharField(widget=forms.Textarea)
    nbootstraps = forms.CharField(initial='100')


############################################################################################################################################


WEEKDAY_CHOICES = (
    ('0', 'Sunday'),
    ('1', 'Monday'),
    ('2', 'Tuesday'),
    ('3', 'Wednesday'),
    ('4', 'Thursday'),
    ('5', 'Friday'),
    ('6', 'Saturday'),
)

class BackupForm(forms.Form):
    time_backup = forms.TimeField(required=True)
    time_upload = forms.TimeField(required=True)
    day_backup = forms.ChoiceField(choices=WEEKDAY_CHOICES)
    day_upload = forms.ChoiceField(choices=WEEKDAY_CHOICES)
    keep_backup = forms.IntegerField(required=True)
    keep_job = forms.IntegerField(required=True)


def rmdb_user(request):
    if request.user.is_authenticated():
        user = RMDBUser.objects.get(user=request.user)
    else:
        user = None
    return {'rmdb_user': user}

def search_form(request):
    return {'search_form': SearchForm()}

def banner_stat(request):
    json = simplejson.load(open('%s/cache/stat_stats.json' % MEDIA_ROOT, 'r'))
    return {'N_constructs': '{:,}'.format(json['N_constructs'])}

def debug_flag(request):
    if DEBUG:
        return {'DEBUG_STR': '', 'DEBUG_DIR': ''}
    else:
        return {'DEBUG_STR': '.min', 'DEBUG_DIR': 'min/'}

def ga_tracker(request):
    return {'TRACKING_ID': GA['TRACKING_ID']}
