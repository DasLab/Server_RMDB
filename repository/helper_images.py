from django.template.defaultfilters import slugify

from rdatkit.view import VARNA

from rmdb.repository.models import *
from rmdb.repository.settings import *

from pylab import *
import matplotlib
matplotlib.use('Agg')


def get_arrays(datas):
	values, traces, reads, xsels, errors = [], [], [], [], []

	for d in datas:
		values.append(d.values)
		traces.append(d.trace)
		reads.append(d.reads)
		xsels.append(d.xsel)
		errors.append(d.errors)
	return array(values), array(traces), array(reads), array(xsels), array(errors)


def get_correct_mapping_bonuses(data, construct):
	vals = [float(x) for x in data.values.split(',')]
	seqpos = [int(x) - construct.offset - 1 for x in construct.seqpos.strip('[]').split(',')]
	bonuses = [-0.1]*len(construct.sequence)
	valmean = sum(vals)/len(vals)
	for i, s in enumerate(seqpos):
		if vals[i] < -0.01:
			bonuses[s] = valmean
		else:
			bonuses[s] = vals[i]
	return bonuses


def generate_varna_thumbnails(entry):
	try:
		constructs = ConstructSection.objects.filter(entry=entry)
		for c in constructs:
			path = '%s%s' % (CONSTRUCT_THMB_DIR, c.id)
			fname = path
			datas = DataSection.objects.filter(construct_section=c)
			# if not os.path.exists(path):
			# 	os.mkdir(path)
			# 	os.system('chmod 777 %s' % path)

			is_eterna = 'ETERNA' in entry.values('rmdb_id')[0]['rmdb_id']
			is_structure = (c.structure) and ('(' in c.structure)
			is_large = len(datas) > 100
			is_SS = entry.type in ('SS', 'TT')

			if is_structure and is_SS and (not is_large) and (not is_eterna):
				height = 200
				for i, data in enumerate(datas[:min(6, len(datas))]):
					bonuses = get_correct_mapping_bonuses(data, c)
					cms = VARNA.get_colorMapStyle(bonuses)

					VARNA.cmd('\" \"', c.structure, '%s_%s.png' % (fname, i), options={'colorMapStyle':cms, 'colorMap':bonuses, 'bpStyle':'simple', 'baseInner':'#FFFFFF', 'periodNum':400, 'spaceBetweenBases':0.6} )
				os.popen('convert -delay 100 -resize 300x300 -background none -gravity center -extent 300x300 -loop 0 %s_*.png %s.gif' % (path, fname))
			else:
				os.popen('convert %s%s/reactivity.png %s.gif' % (CONSTRUCT_IMG_DIR, c.id, fname))
				if (not entry.datacount): entry.datacount = len(datas[0].values.split(','))
				height = 200 * pow(len(datas), 2) / entry.datacount

				if (len(datas) < 3): height = len(datas)*10
				height = min(height, 1000)
				if not is_eterna: height = min(height, 250)

			width = 200
			os.popen('mogrify -format gif -thumbnail %sx%s! %s.gif' % (width, height, fname))
			if (os.path.isfile('%s_0.png' % fname)): os.popen('rm -rf %s_*.png' % fname)
	except ConstructSection.DoesNotExist:
		print 'FATAL! There are no constructs for entry %s' % entry.rmdb_id


def generate_images(construct_model, construct_section, entry_type, engine='matplotlib'):
	data = DataSection.objects.filter(construct_section=construct_model)
	values, traces, reads, xsels, errors = [], [], [], [], []
	for d in data:
		values.append([float(x) for x in d.values.strip().split(',')])
		if d.trace:
			traces.append([float(x) for x in d.trace.strip().split(',')])
		if d.reads:
			reads.append([float(x) for x in d.reads.strip().split(',')])
		if d.errors:
			errors.append([float(x) for x in d.errors.strip().split(',')])
		if d.xsel:
			xsels.append([float(x) for x in d.xsel.strip().split(',')])
	values_array, trace_array, reads_array, xsel_array, errors_array = array(values), array(traces), array(reads), array(xsels), array(errors)
	values_array, trace_array, reads_array, xsel_array, errors_array = get_arrays(construct_section.data)
	
	dir = CONSTRUCT_IMG_DIR + '%s/' % construct_model.id
	if not os.path.exists(dir):
		os.mkdir(dir)
		os.system('chmod 777 %s' % dir)

	values_dims = shape(values_array)
	trace_dims = shape(trace_array)
	values_mean = values_array.mean(axis=-1)
	values_std = values_array.std(axis=0)

	if entry_type == 'MM':
		order = []
		order_offset = 0
		for i, data in enumerate(construct_section.data):
			if 'mutation' in data.annotations:
				if data.annotations['mutation'][0].upper() == 'WT':
					order.append(order_offset)
					order_offset += 1
				else:
					i_order = data.annotations['mutation'][0].replace('Lib1-', '').replace('Lib2-', '').replace('Bad Quality', '').replace('badQuality', '').replace('warning:', '').replace(',', '').strip()
					order.append(int(i_order[1:-1]))
			else:
				order.append(i)
		order = [i[0] for i in sorted(enumerate(order), key=lambda x:x[1])][::-1]
	else:
		order = range(values_dims[0])
		# if entry_type == 'MA':
		# 	order = order[::-1]
	

	if engine == 'matplotlib':
		has_traces = False
		aspect_ratio = "auto"

		figure(2)
		frame = gca()
		frame.axes.get_xaxis().set_visible(False)
		frame.axes.get_yaxis().set_visible(False)

		if size(trace_array) > 0:
			if (entry_type == 'MM'):  aspect_ratio = shape( trace_array[order, :] )[1] / float( shape( trace_array)[0]  )
			imshow(trace_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean()+0.4*trace_array.std(), aspect=aspect_ratio, interpolation='nearest')
			savefig(dir+'/trace.png', bbox_inches='tight')
			has_traces = True

		if size(reads_array) > 0:
			if (entry_type == 'MM'):  aspect_ratio = shape( reads_array[order, :] )[1] / float( shape( reads_array)[0]  )
			imshow(reads_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=reads_array.mean()+0.4*reads_array.std(), aspect=aspect_ratio, interpolation='nearest')
			savefig(dir+'/trace.png', bbox_inches='tight')
			has_traces = True

		figure(2)
		clf()
		is_eterna = 'ETERNA' in RMDBEntry.objects.filter(id=construct_model.values('entry'))[0].rmdb_id
		if is_eterna or shape(values_array)[0] < 3:
			aspect_ratio = 'auto'
		else:
			aspect_ratio = 'equal'
		if entry_type == "MA":
			sub_id = tril_indices(min(shape(values_array)))
			if (values_array[sub_id].mean() > 10):
				outliers = where(values_array > values_array[sub_id].mean()*3)
				values_array[outliers] = values_array[sub_id].mean()*3
			vmax_adjust = values_array[sub_id].mean()*2 #+ values_array[sub_id].std()*0.35

			# print values_array[sub_id].mean(), values_array.mean(),values_array[sub_id].std(), values_array.std()
		else:
			vmax_adjust = values_array.mean()*1.5 #+ values_array.std()*0.35
			# print values_array.mean(),values_array.std();
		if vmax_adjust < 0: vmax_adjust = values_array.mean() + values_array.std()*0.5

		imshow(values_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=vmax_adjust, aspect=aspect_ratio, interpolation='kaiser')
		frame = gca()
		frame.axes.get_xaxis().set_visible(False)
		frame.axes.get_yaxis().set_visible(False)
		savefig(dir+'/reactivity.png', bbox_inches='tight')

		#figure(1)
		#clf()
		#matshow(corrcoef(values_array.T)**10)
		#savefig(dir+'/corrcoef.png')
		# if entry_type == 'SS' and values_dims[0] < 100:
		# 	for j in range(values_dims[0]):
		# 		figure(1)
		# 		clf()
		# 		bar(range(values_dims[1]), values_array[j,:], yerr=errors_array[j,:])
		# 		bartitle = '  '.join( [','.join(x) if type(x) == list else str(x) for x in construct_section.data[j].annotations.values()] )
		# 		suptitle( bartitle )
		# 		#apply_xlabels( construct_section )
		# 		xlim( [0, shape( values_array )[1] ] )
		# 		savefig(dir+'/barplot%s.png'%j)

	return has_traces

