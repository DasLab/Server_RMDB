import matplotlib
matplotlib.use('Agg')
import pdb
import numpy
import os
from rdatkit import rna, secondary_structure, mapping, view
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repository.settings") 

from src.settings import *
from src.models import *
from src.views import *

def precalculate_structures(entry):
    try:
        constructs = ConstructSection.objects.filter(entry=entry)
        for c in constructs:
            datas = DataSection.objects.filter(construct_section=c)
            for d in datas:
                bonuses = correct_rx_bonus(d, c)
                for i, b in enumerate(bonuses):
                    if b == -1.0:
                        bonuses[i] = -999
                m = mapping.MappingData(data=bonuses)
                structs = secondary_structure.fold(c.sequence, mapping_data=m)
                if len(structs) == 0:
        # No non-trivial structures found, try with data normalization
                    m = mapping.MappingData(data=bonuses, norm=True)
                    structs = secondary_structure.fold(c.sequence, mapping_data=m)
                    if len(structs) == 0:
                        d.structure = 'NA'
                    else:
                        d.structure = structs[0].dbn
                else:
                    d.structure = structs[0].dbn
                d.save()
    except ConstructSection.DoesNotExist:
        print 'FATAL! There are no constructs for entry %s' % entry.rmdb_id


def bpdict_to_str(d):
    res = ''
    for bp in d:
        res += '%s,%s,%s;' % (bp[0], bp[1], d[bp])
    return res.strip(';')


def str_to_bpdict(s):
    res = {}
    for e in s.split(';'):
        fields = e.split(',')
        res[(fields[0], fields[1])] = fields[2]
    return res


def normalize(bonuses):
    l = len(bonuses)
    wtdata = array(bonuses)
    if wtdata.min() < 0:
        wtdata -= wtdata.min()
    interquart = stats.scoreatpercentile(wtdata, 75) - stats.scoreatpercentile(wtdata, 25)
    for i in range(l):
        if wtdata[i] > interquart*1.5:
            wtdata[i] = 999
    tenperc = stats.scoreatpercentile(wtdata, 90)
    maxcount = 0
    maxav = 0.
    for i in range(l):
        if wtdata[i] >= tenperc:
            maxav += wtdata[i]
            maxcount += 1
    maxav /= maxcount
    wtdata = wtdata/maxav
    return wtdata



def render_to_varna(sequences, structures, modifiers, titles, mapping_data, base_annotations, refstruct):
    panels = []
    ncols = min(4, len(sequences))
    nrows = 4
    if ncols < 4:
        nrows = 1
    nelems = nrows * ncols
    for i in range(len(sequences)):
        v = view.VARNA(sequences[i:i+nelems], structures[i:i+nelems], mapping_data=mapping_data[i:i+nelems])
        v.title = titles[i:i+nelems]
        v.colorMapCaption = modifiers[i:i+nelems]
        v.codebase = 'http://rmdb.stanford.edu/site_media/bin'
        v.bpStyle = 'simple'
        v.baseInner = '#FFFFFF'
        v.baseOutline = '#FFFFFF'
        v.width = 400
        v.height = 600
        panels.append(v.render(base_annotations=base_annotations[i:i+nelems], annotation_by_helix=True, annotation_def_val='0.0%', helix_function=(lambda x, y: str(max(float(str(x).strip('%')), float(str(y).strip('%')))) + '%'), reference_structure=refstruct))
    return panels, ncols, nrows


def viewstructures(request):
    if request.method == 'POST':
        sequences = request.POST['sequences'].split('\n')
        titles  = request.POST['titles'].split('\n')
        dbns = request.POST['structures'].split('\n')
        md_seqposes = request.POST['md_seqposes'].split('\n')
        md_datas = request.POST['md_datas'].split('\n')
        bpa = request.POST['base_annotations'].split('\n')
        refstruct = secondary_structure.SecondaryStructure(dbn=request.POST['refstruct'])
        messages = []
        structures = []
        mapping_data = []
        base_annotations = []
        for dbn in dbns:
            structures.append(secondary_structure.SecondaryStructure(dbn=dbn))
        for i in range(len(md_seqposes)):
            seqpos = [int(pos) for pos in md_seqposes[i].split(',')]
            data = [float(d) for d in md_datas[i].split(',')]
            mapping_data.append(mapping.MappingData(data=data, seqpos=seqpos))
        for annotations in bpa:
            if len(annotations) > 0:
                try:
                    base_annotations.append(str_to_bpdict(annotations)) 
                except ValueError:
                    messages.append('An error occurred when annotating helices, please contact tsuname [at] stanford [dot] edu to report this bug')
        if len(request.POST['modifiers']):
            modifiers = request.POST['modifiers'].split(',')
        else:
            modifiers = ['Pseudo energy' for y in sequences]
        panels, ncols, nrows = render_to_varna(sequences, structures, modifiers, titles, mapping_data, base_annotations, refstruct)
        form = VisualizerForm(request.POST)
        return render_to_response('html/predict_result.html', {'panels':panels, 'messages':messages,'ncols':ncols, 'nrows':nrows, 'form':form}, context_instance=RequestContext(request))


if __name__ == '__main__':
    constructs = ConstructSection.objects.all()
    for c in constructs:
        e = RMDBEntry.objects.get(constructsection=c)
        print 'Doing %s' % e.rmdb_id
        precalculate_structures(e)
        #generate_varna_thumbnails(e)
