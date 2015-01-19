from django.db import models
from django import forms


PRED_TYPE_CHOICES = (
    ('1D', '1D'),
    ('2D', '2D'),
    ('NN', 'None'),
)

MOD_TYPE_CHOICES = (
    ('SHAPE', 'SHAPE'),
    ('DMS', 'DMS'),
    ('CMCT', 'CMCT'),
)
class VisualizerForm(forms.Form):
    sequences = forms.CharField(widget=forms.Textarea)
    structures = forms.CharField(widget=forms.Textarea)
    md_datas = forms.CharField(widget=forms.Textarea)
    md_seqposes = forms.CharField(widget=forms.Textarea)
    modifiers = forms.CharField(widget=forms.Textarea)
    titles = forms.CharField(widget=forms.Textarea)
    base_annotations = forms.CharField(widget=forms.Textarea)
    refstruct = forms.CharField()

class PredictionForm(forms.Form):
    sequences = forms.CharField(widget=forms.Textarea)
    structures = forms.CharField(widget=forms.Textarea)
    bonuses_1d = forms.CharField(widget=forms.Textarea)
    bonuses_2d = forms.CharField(widget=forms.Textarea)
    annotations = forms.CharField(widget=forms.Textarea)
    bonusfile = forms.FileField()
    predtype = forms.ChoiceField(choices=PRED_TYPE_CHOICES)
    modtype = forms.ChoiceField(choices=MOD_TYPE_CHOICES)
    rdatfile = forms.FileField()
    temperature = forms.CharField(initial='37')
    refstruct = forms.CharField()
    slope_1d = forms.CharField(initial='2.6')
    intercept_1d = forms.CharField(initial='-0.8')
    slope_2d = forms.CharField(initial='1.0')
    applyzscores = forms.BooleanField(initial=True)
    clipsequence = forms.BooleanField(initial=False)
    intercept_2d = forms.CharField(initial='0.0')
    normalize = forms.BooleanField(initial=True)
    rmdbid = forms.CharField(required=False)
    nbootstraps_1d = forms.CharField()
    nbootstraps_2d = forms.CharField()
    raw_bonuses = forms.BooleanField(initial=False)
    
