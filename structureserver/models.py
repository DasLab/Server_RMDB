from django.db import models
from django import forms


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
    refstruct = forms.CharField(widget=forms.Textarea)

    nbootstraps_1d = forms.CharField(initial='100')
    nbootstraps_2d = forms.CharField(initial='100')
    
