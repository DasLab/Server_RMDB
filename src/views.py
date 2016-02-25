from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.template import RequestContext#, Template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, render_to_response, redirect

from rdatkit.datahandlers import RDATFile, RDATSection, ISATABFile
from rdatkit.secondary_structure import SecondaryStructure

from src.env import error400, error401, error403, error404, error500, error503
from src.models import *
from src.settings import *

from src.helper.helpers import *
from src.helper.helper_api import *
from src.helper.helper_deposit import *
from src.helper.helper_display import *
from src.helper.helper_predict import *

import datetime
import simplejson
import sys
import time
import traceback
# from sys import stderr


def index(request):
    return render_to_response(PATH.HTML_PATH['index'], {}, context_instance=RequestContext(request))

def browse(request):
    return render_to_response(PATH.HTML_PATH['browse'], {}, context_instance=RequestContext(request))

def specs(request, section):
    if len(section) > 0:
        return HttpResponseRedirect('/specs/' + section)
    return render_to_response(PATH.HTML_PATH['specs'], {}, context_instance=RequestContext(request))

def tools(request):
    return render_to_response(PATH.HTML_PATH['repos'], {}, context_instance=RequestContext(request))

def tools_license(request, keyword):
    if keyword in ('mapseeker', 'reeffit'):
        return render_to_response(PATH.HTML_PATH['tools_license'], {'keyword':keyword}, context_instance=RequestContext(request))
    else:
        return error404(request)

@login_required
def tools_download(request, keyword):
    if keyword in ('mapseeker', 'reeffit'):
        new = SourceDownloader(date=datetime.datetime.now(), package=keyword, rmdb_user=RMDBUser.objects.get(user=request.user))
        new.save()

        if keyword == 'mapseeker':
            title = "MAPseeker"
        elif keyword == 'reeffit':
            title = "REEFFIT"
        return render_to_response(PATH.HTML_PATH['tools_download'], {'keyword':keyword, 'title':title}, context_instance=RequestContext(request))
    else:
        return error404(request)

def tutorial(request, keyword):
    if keyword in ('predict', 'api', 'rdatkit', 'hitrace', 'mapseeker', 'reeffit'):
        return render_to_response(PATH.HTML_PATH['tutorial'].replace('xxx', keyword), {}, context_instance=RequestContext(request))
    else:
        return error404(request)

def about(request):
    return render_to_response(PATH.HTML_PATH['about'], {}, context_instance=RequestContext(request))

def license(request):
    return render_to_response(PATH.HTML_PATH['license'], {}, context_instance=RequestContext(request))

def history(request):
    hist_list = []
    hist = HistoryItem.objects.all()
    for h in hist:
        lines = h.content
        lines = [line for line in lines.split('\r\n') if line.strip()]
        ls_1_flag = 0
        ls_2_flag = 0
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip()
            if lines[i][0] == "#":
                lines[i] = "<span class=\"lead\"><b>" + lines[i][1:] + "</b></span><br/>"
            elif lines[i][0] != '-':
                if lines[i][0] == "!":
                    lines[i] = "by <kbd><i>" + lines[i][1:] + "</i></kbd><br/><br/>"
                else:
                    lines[i] = "<p>" + lines[i] + "</p><p><ul>"
                
            else:
                if lines[i][:2] != '-\\':
                    lines[i] = "<li><u>" + lines[i][1:] + "</u></li>"
                    if ls_1_flag:
                        lines[i] = "</ul></p>" + lines[i]
                    ls_1_flag = i

                else:
                    lines[i] = "<li>" + lines[i][2:] + "</li>"
                    if ls_2_flag < ls_1_flag:
                        lines[i] = "<ul><p>" + lines[i]
                    ls_2_flag = i        
        lines.append("</ul></ul><br/><hr/>")
        date_string = h.date.strftime("%b %d, %Y (%a)")
        lines.insert(0, "<i>%s</i><br/>" % date_string)
        hist_list.insert(0, ''.join(lines))
        
    return render_to_response(PATH.HTML_PATH['history'], {'hist': hist_list}, context_instance=RequestContext(request))


def validate(request):
    flag = -1
    if request.method == 'POST':
        form = ValidateForm(request.POST, request.FILES)
        link = request.POST['link']
        uploadfile = ''
        if not link:
            try:
                uploadfile = request.FILES['file']
                (errors, messages, flag) = validate_file(uploadfile, link, request.POST['type'])
            except:
                pass
        else:
            (errors, messages, flag) = validate_file(uploadfile, link, request.POST['type'])

    if flag == -1:
        messages = []
        errors = []
        form = ValidateForm()
        flag = 0

    return render_to_response(PATH.HTML_PATH['validate'], {'form':form, 'valerrors':errors, 'valmsgs':messages, 'flag':flag}, context_instance=RequestContext(request))


def detail(request, rmdb_id):
    try:
        entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')[0]
        entry.cid = ConstructSection.objects.filter(entry=entry).values( 'id' )[ 0 ][ 'id' ]
        is_isatab = True if os.path.exists('%s/files/%s/%s_%s.xls' % (PATH.DATA_DIR['ISATAB_FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version)) else False
    except (RMDBEntry.DoesNotExist, IndexError):
        return error404(request)

    # {'codebase':get_codebase(request)}
    return render_to_response(PATH.HTML_PATH['detail'], {'rmdb_id':entry.rmdb_id, 'cid':entry.cid, 'version':entry.version, 'revision_status':entry.revision_status, 'is_isatab':is_isatab}, context_instance=RequestContext(request))


def predict(request):
    if request.method != 'POST':
        return render_to_response(PATH.HTML_PATH['predict'], {'secstr_form':PredictionForm(), 'rdatloaded':False, 'messages':[], 'other_errors':[]}, context_instance=RequestContext(request))
    else:
        try:
            sequences, titles, structures, modifiers, mapping_data, base_annotations, messages, valerrors = ([],[],[],[],[],[],[],[])

            is_get_rmdb = (len(request.POST['rmdbid']) > 0)
            is_get_file = (len(request.POST['rdatfile']) > 0)
            if is_get_rmdb or is_get_file:
                (messages, valerrors, bonuses_1d, bonuses_2d, titles, modifiers, offset_seqpos, temperature, sequences, refstruct) = parse_rdat_data(request, is_get_file)
                form = fill_predict_form(request, sequences, structures, temperature, refstruct, bonuses_1d, bonuses_2d, modifiers, titles, offset_seqpos)
                return render_to_response(PATH.HTML_PATH['predict'], {'secstr_form':form, 'rdatloaded':True, 'msg_y':messages, 'msg_r':valerrors}, context_instance=RequestContext(request))
            elif not request.POST['sequences']:
                return render_to_response(PATH.HTML_PATH['predict'], {'secstr_form':PredictionForm(), 'rdatloaded':False, 'msg_y':[], 'msg_r':[]}, context_instance=RequestContext(request))

            other_options = ' -t %s ' % (float(request.POST['temperature']) + 273.15)
            refstruct = SecondaryStructure(dbn=request.POST['refstruct'])

            lines = request.POST['sequences'].split('\n')
            for l in lines:
                if l:
                    if l[0] == '>':
                        titles.append(l.replace('>',''))
                    else:
                        if l.strip():
                            sequences.append(rna.RNA(l.strip())) 
            if not sequences:
                messages.append('ERROR: No SEQUENCE found. Due to either no input field, or no modification lanes in RDAT.')
                return render_to_response(PATH.HTML_PATH['predict_res'], {'panels':[], 'messages':messages,'bppmimg':'', 'ncols':0, 'nrows':0}, context_instance=RequestContext(request))

            if 'structures' in request.POST:
                lines = request.POST['structures'].split('\n')
                for l in lines:
                    if l.strip():
                        structures.append(l)

            if request.POST['predtype'] in ('NN', '1D'):
                (base_annotations, structures, mapping_data, messages) = predict_run_1D_NN(request, sequences, mapping_data, structures, other_options, messages)

            if request.POST['predtype'] == '2D':
                (sequences, structures, messages, base_annotations) = predict_run_2D(request, sequences, titles, structures, other_options, messages)
                modifiers = ['']


            panels, ncols, nrows = render_to_varna([s.sequence for s in sequences], structures, modifiers, titles, mapping_data, base_annotations, refstruct)
            visform_params = {}
            visform_params['sequences'] = '\n'.join([s.sequence for s in sequences])
            visform_params['structures'] = '\n'.join([s.dbn for s in structures])
            if 'raw_bonuses' in request.POST:
                print [str(slope*log(1 + d) + intercept) for d in mapping_data[0].data()]
                visform_params['md_datas'] = '\n'.join([','.join([str(slope*log(1 + d) + intercept) for d in m.data()]) for m in mapping_data])
            else:
                visform_params['md_datas'] = '\n'.join([','.join([str(d) for d in m.data()]) for m in mapping_data])
            visform_params['md_seqposes'] = '\n'.join([','.join([str(pos) for pos in m.seqpos]) for m in mapping_data])
            visform_params['modifiers'] = modifiers
            visform_params['base_annotations'] = '\n'.join([bpdict_to_str(ann) for ann in base_annotations])
            visform_params['refstruct'] = refstruct.dbn
            visform = VisualizerForm(visform_params)
            return render_to_response(PATH.HTML_PATH['predict_res'], {'panels':[], 'messages':messages,'ncols':[], 'nrows':[], 'form':visform}, context_instance=RequestContext(request))

        except IndexError, err:
            print err
            return render_to_response(PATH.HTML_PATH['predict'], {'secstr_form':PredictionForm(), 'rdatloaded':False, 'msg_y':messages, 'msg_r':['Invalid input. Please check your inputs and try again.']}, context_instance=RequestContext(request))


def str_view(request):
    return render_to_response(PATH.HTML_PATH['index'], context_instance=RequestContext(request))


def search(request):
    return render_to_response(PATH.HTML_PATH['search_res'], {}, context_instance=RequestContext(request))


def advanced_search(request):
    other_errors = []
    check_structure_balance = False
    valid = True
    if request.method == 'POST':
        try:
            form = AdvancedSearchForm(request.POST)
            constructs_byquery = {}
            rdat_paths = {}
            rdats = {}
            query_data = {}
            construct_secstructelemdicts = {}
            searchid = randint(1, 10000)
            if 'structure' in request.POST and 'sequence' in request.POST:
                if len(request.POST['structure']) != len(request.POST['sequence']) and len(request.POST['structure']) > 0 and len(request.POST['sequence']) > 0:
                    other_errors.append('Structure and sequence motifs searched must have equal length')
                    valid =  False
            try:
                numresults = int(request.POST['numresults'])
            except:
                valid =  False

            if valid:
                for field in ('structure', 'sequence'):
                    if field in request.POST and request.POST[field]:
                        if field == 'structure':
                            if ' ' in request.POST[field]:
                                check_structure_balance = True
                            query_field = request.POST[field]
                            for ec in '.(){}':
                                query_field = query_field.replace(ec,'\\'+ec).replace('\\\\'+ec,ec)
                            if check_structure_balance:
                                query_field = query_field.replace(' ', '.*')
                            constructs_byquery[field] = ConstructSection.objects.filter(structure__regex=query_field)
                        if field =='sequence':
                            query_field = ''.join([toIUPACregex(s.upper()) for s in request.POST[field]])
                            constructs_byquery[field] = ConstructSection.objects.filter(sequence__regex=query_field)
                        query_data[field] = query_field
                if 'secstructelems' in request.POST:
                    query_data['secstructelems'] = request.POST.getlist('secstructelems')
                    all_constructs = ConstructSection.objects.all()
                    constructs_byquery['secstructelems'] = []
                    cids = []
                    for construct in all_constructs:
                        if structure_is_valid(construct.structure):
                            sstruct = SecondaryStructure(dbn=construct.structure)
                            ssdict = sstruct.explode()
                            for elem in query_data['secstructelems']:
                                if elem in ssdict and ssdict[elem]:
                                    cids.append(construct.id)
                                    construct_secstructelemdicts[construct.id] = ssdict
                                    break
                            constructs_byquery['secstructelems'] = ConstructSection.objects.filter(id__in=cids)
                if len(query_data) == 0: # No search criteria was chosen, get all constructs
                    constructs_byquery['all'] = ConstructSection.objects.all()
                    query_data['all'] = True

                if 'background_processed' in request.POST:
                    bp_entry_ids = [d.section.rmdb_id for d in EntryAnnotation.objects.filter(name='processing', value='backgroundSubtraction')]
                for field in constructs_byquery:
                    entry_types = request.POST.getlist('entry_type')
                    modifiers = request.POST.getlist('modifiers')
                    constructs_byquery[field].exclude(entry__latest=False)
                    for t, name in ENTRY_TYPE_CHOICES:
                        if t not in entry_types:
                            constructs_byquery[field] = constructs_byquery[field].exclude(entry__type=t)
                    for t, name in MODIFIERS:
                        if t not in modifiers:
                            constructs_byquery[field] = constructs_byquery[field].exclude(entry__rmdb_id__contains='_%s_' % t)
                    if 'include_eterna' not in request.POST:
                        constructs_byquery[field] = constructs_byquery[field].exclude(entry__from_eterna=True)
                    if 'background_processed' in request.POST:
                        constructs_byquery[field] = constructs_byquery[field].filter(entry__rmdb_id__in=bp_entry_ids)

                constructs = constructs_byquery.values()[0]
                for k, v in constructs_byquery.iteritems():
                    constructs = [c for c in constructs if c in v]

                entries_visited = []
                unique_constructs = []
                for c in constructs:
                    if c.entry.rmdb_id not in entries_visited:
                        unique_constructs.append(c)
                        entries_visited.append(c.entry.rmdb_id)
                rdat, all_values, cell_labels, values_min, values_max, values_min_heatmap, values_max_heatmap, unpaired_bins, paired_bins, unpaired_bin_anchors, paired_bin_anchors, rmdb_ids, messages, numallresults, render = get_restricted_RDATFile_and_plot_data(unique_constructs, numresults, query_data, searchid, construct_secstructelemdicts, check_structure_balance)
                
                rdat_path = 'search/%s.rdat' % searchid
                rdat.save(MEDIA_ROOT + '/data/' + rdat_path, version=0.24)

                return render_to_response(PATH.HTML_PATH['adv_search_res'], \
                        {'rdat_path':rdat_path, 'all_values':simplejson.dumps(all_values), 'values_min':values_min, 'values_max':values_max, \
                        'values_min_heatmap':values_min_heatmap, 'values_max_heatmap':values_max_heatmap, \
                        'rmdb_ids':simplejson.dumps(rmdb_ids), 'messages':messages, \
                        'unpaired_bins':simplejson.dumps(unpaired_bins), 'paired_bins':simplejson.dumps(paired_bins), \
                        'unpaired_bin_anchors':simplejson.dumps(unpaired_bin_anchors), 'paired_bin_anchors':simplejson.dumps(paired_bin_anchors), \
                        'render':render, 'render_paired_histogram':len(paired_bins) > 0, 'render_unpaired_histogram':len(unpaired_bins) > 0,\
                        'form':form, 'numresults':numallresults, 'cell_labels':simplejson.dumps(cell_labels), 'all_results_rendered':numallresults <= numresults},\
                        context_instance=RequestContext(request) )

        except ValueError as e:
            return render_to_response(PATH.HTML_PATH['adv_search_res'], {'render':False}, context_instance=RequestContext(request))

    else:
        form = AdvancedSearchForm()
    return render_to_response(PATH.HTML_PATH['adv_search'], {'form':form, 'other_errors':other_errors}, context_instance=RequestContext(request))


@login_required
def upload(request):
    error_msg = []
    flag = 0
    entry = []

    if request.method == 'POST':
        try:
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                proceed = True
                if not check_rmdb_id(form.cleaned_data['rmdb_id']):
                    error_msg.append('RMDB ID invalid. Hover mouse over the field to see instructions.')
                    flag = 1
                    proceed = False
                else:
                    isatabfile = ISATABFile()
                    isatabfile.loaded = False
                    rdatfile = RDATFile()
                    rdatfile.loaded = False

                    uploadfile = request.FILES['file']
                    rf = write_temp_file(uploadfile)
                    txt = rf.readlines()
                    txt = filter(lambda x:'experimentType:' in x, txt)
                    if txt:
                        txt = txt[0]
                        idx = txt.find('experimentType:')
                        txt = txt[idx:]
                        txt = txt[txt.find(':')+1 : txt.find('\t')]
                        expType = [x[1] for i, x in enumerate(ENTRY_TYPE_CHOICES) if x[0] == form.cleaned_data['type']][0]
                        if txt != expType:
                            error_msg.append('experimentType mismatch between selected file and web page form; please check and resubmit.')
                            error_msg.append('File indicates experimentType of ' + txt + ', while form selected ' + expType + '.')
                            flag = 1
                            proceed = False
                    else:
                        error_msg.append('experimentType missing.')


                    rf.seek(0)
                    if form.cleaned_data['filetype'] == 'isatab':
                        try:
                            isatabfile.load(rf.name)
                            isatabfile.loaded = True
                            rdatfile = isatabfile.toRDAT()
                        except Exception:
                            error_msg.append('ISATAB file invalid; please check and resubmit.')
                            flag = 1
                            proceed = False
                    else:
                        try:
                            rdatfile.load(rf)
                            rdatfile.loaded = True
                            isatabfile = rdatfile.toISATAB()
                        except Exception:
                            error_msg.append('RDAT file invalid; please check and resubmit.')
                            flag = 1
                            proceed = False

                if proceed:
                    (error_msg, entry) = submit_rmdb_entry(form, request, rdatfile, isatabfile)
                    flag = 2
            else:
                flag = 1
                if 'rmdb_id' in form.errors: error_msg.append('RMDB_ID field is required.')
                if 'file' in form.errors: error_msg.append('Input file field is required.')
                if 'authors' in form.errors: error_msg.append('Authors field is required.')

        except IndexError, e:
            flag = 1
            print traceback.format_exc()
            error_msg.append('Input file invalid; please check and resubmit.')
    else:
        form = UploadForm()
    return render_to_response(PATH.HTML_PATH['upload'], {'form':form, 'error_msg':error_msg, 'flag':flag, 'entry':entry}, context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_rev_stat(request):
    new_stat = request.POST['rev_stat']
    rmdb_id = request.POST['rmdb_id']
    cid = request.POST['cid']
    construct = ConstructSection.objects.filter(id=cid)[0]
    entry = RMDBEntry.objects.filter(id=construct.entry.id).order_by('-version')[0]
    if new_stat == "PUB":
        rdatfile = RDATFile()
        file_name = '%s%s/%s_%s.rdat' %(PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id, rmdb_id, entry.version)
        if not os.path.isfile(file_name):
            file_name = '%s%s/%s.rdat' %(PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id, rmdb_id)
        rf = open(file_name, 'r')
        rdatfile.load(rf)
        rf.close()
        for k in rdatfile.constructs:
            c = rdatfile.constructs[k]
            entry.has_traces = generate_images(construct, c, entry.type, engine='matplotlib')

        generate_varna_thumbnails(entry)
        make_json_for_rdat(entry.rmdb_id)

    entry.revision_status = new_stat
    entry.save()
    is_isatab = True if os.path.exists('%s/files/%s/%s_%s.xls' % (PATH.DATA_DIR['ISATAB_FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version)) else False

    return render_to_response(PATH.HTML_PATH['detail'], {'rmdb_id':entry.rmdb_id, 'cid':cid, 'version':entry.version, 'codebase':get_codebase(request), 'revision_status':entry.revision_status, 'is_isatab':is_isatab}, context_instance=RequestContext(request))


def url_redirect(request, path):
    if 'detail/' in path:
        path = path.rstrip('/')
    if request.GET.get('searchtext'):
        path = path + '?searchtext=' + request.GET.get('searchtext')
    return HttpResponsePermanentRedirect("/%s" % path)



def get_admin(request):
    return HttpResponse(simplejson.dumps({'email':EMAIL_NOTIFY}, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_user(request):
    if request.user.username: 
        user = request.user.username
    else:
        user = 'unknown'
    return HttpResponse(simplejson.dumps({'user': user}, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_js(request):
    stats = simplejson.load(open('%s/cache/stat_sys.json' % MEDIA_ROOT, 'r'))
    json = {'jquery':stats['jquery'], 'bootstrap':stats['bootstrap'], 'd3':stats['d3'], 'zclip':stats['zclip']}
    return HttpResponse(simplejson.dumps(json, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_stats(request):
    json = simplejson.load(open('%s/cache/stat_stats.json' % MEDIA_ROOT, 'r'))
    for key in json.keys():
        json[key] = '{:,}'.format(json[key])
    return HttpResponse(simplejson.dumps(json, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_news(request):
    n_news = 20
    news = NewsItem.objects.all().order_by('-date')[:n_news]
    json = {}
    for i, n in enumerate(news):
        json[i] = {'content': n.content, 'date': n.date.strftime('%b %d, %Y')}
    return HttpResponse(simplejson.dumps(json, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_recent(request):
    entries = RMDBEntry.objects.all().filter(status='PUB').order_by('-creation_date')
    entries_list = []
    for e in entries:
        if e.rmdb_id not in entries_list:
            entries_list.append(e.rmdb_id)
        if len(entries_list) == 10:
            break
    entries = []
    for e in entries_list:
        entries.append(RMDBEntry.objects.filter(rmdb_id=e).order_by('-creation_date')[0])

    entries_list = []
    for e in entries:
        cid = ConstructSection.objects.filter(entry=e).values('id')[0]['id']
        rmdb_id = e.rmdb_id
        for c in ConstructSection.objects.filter(entry=e).values('name').distinct():
            name = c['name']
        e_temp = {'cid':cid, 'name':name, 'rmdb_id':rmdb_id}
        entries_list.append(e_temp)
    return HttpResponse(simplejson.dumps(entries_list, sort_keys=True, indent=' ' * 4), content_type='application/json')    


def ping_test(request):
    return HttpResponse(content="", status=200)


def test(request):
    print request.META
    return error400(request)
    raise ValueError
    # send_notify_emails('test', 'test')
    # send_mail('text', 'test', EMAIL_HOST_USER, [EMAIL_NOTIFY])
    return HttpResponse(content="", status=200)


