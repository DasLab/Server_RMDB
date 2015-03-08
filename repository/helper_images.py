from django.template.defaultfilters import slugify

from rdatkit.view import VARNA

from rmdb.repository.models import *
from rmdb.repository.settings import *

from pylab import *
import matplotlib
matplotlib.use('Agg')


def get_arrays(datas):
	values = []
	traces = []
	reads = []
	xsels = []
	errors = []

	for d in datas:
		values.append(d.values)
		traces.append(d.trace)
		reads.append(d.reads)
		xsels.append(d.xsel)
		errors.append(d.errors)
	return array(values), array(traces), array(reads), array(xsels), array(errors)


def generate_varna_thumbnails(entry):
	try:
		constructs = ConstructSection.objects.filter(entry=entry)
		for c in constructs:
			path = '%s%s' % (CONSTRUCT_THMB_DIR, c.id)
			fname = '%s/%s' % (path, slugify(c.name))
			datas = DataSection.objects.filter(construct_section=c)
			if not os.path.exists(path):
				os.mkdir(path)
				os.system('chmod 777 %s' % path)
			if not c.structure or '(' not in c.structure or entry.type == 'MM' or len(datas) > 100:
				peakfname = '%s%s/values.png' % (CONSTRUCT_IMG_DIR, c.id) 
				os.popen('cp %s %s.png' % (peakfname, fname))
				os.popen('convert %s.png %s.gif' % (fname, fname))
				height = min(len(datas), 1000)
			else:
				height = 200
				os.popen('rm %s/*.png' % path)
				for i, data in enumerate(datas[:5]):
					bonuses = get_correct_mapping_bonuses(data, c)
					cms = VARNA.get_colorMapStyle(bonuses)
					VARNA.cmd(' '*len(c.sequence), c.structure, '%s_%s.png' % (fname, i), options={'colorMapStyle':cms, 'colorMap':bonuses, 'bpStyle':'simple', 'baseInner':'#FFFFFF', 'periodNum':400} )
				print path
				os.popen('convert -delay 100 -resize 300x300 infile.jpg -background none -gravity center -extent 300x300 -loop 0 %s/*.png %s.gif' % (path, fname))

			width = 200
			os.popen('mogrify -format gif -thumbnail %sx%s! %s.gif' % (width, height, fname))
	except ConstructSection.DoesNotExist:
		print 'FATAL! There are no constructs for entry %s' % entry.rmdb_id


def generate_images(construct_model, construct_section, entry_type, engine='matplotlib'):
	data = DataSection.objects.filter(construct_section=construct_model)
	values = []
	traces = []
	reads = []
	xsels = []
	errors = []
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
	
	dir = CONSTRUCT_IMG_DIR+'%s/'%construct_model.id
	if not os.path.exists(dir):
		os.mkdir(dir)
		os.system('chmod 777 %s' % dir)
	values_array, trace_array, reads_array, xsel_array, errors_array = get_arrays(construct_section.data)
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
					order.append(int(data.annotations['mutation'][0].replace('Lib1-','').replace('Lib2-', '')[1:-1]))
			else:
				order.append(i)
		order = [i[0] for i in sorted(enumerate(order), key=lambda x:x[1])][::-1]
	else:
		order = range(values_dims[0])
	
	if engine == 'matplotlib':
		has_traces = False
		if size(trace_array) > 0:
			figure(2)
			aspect_ratio = "auto"
			if (entry_type == 'MM'):  aspect_ratio = shape( trace_array[order, :] )[1] / float( shape( trace_array)[0]  )
			#imshow(trace_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean(), aspect=aspect_ratio, interpolation='nearest')
			imshow(trace_array[order, :], cmap=get_cmap('Greys'))
			#apply_xlabels( construct_section )
			xticks( [],[] )
			#apply_ylabels( construct_section )
			savefig(dir+'/trace.png')
			has_traces = True
		if size(reads_array) > 0:
			figure(2)
			aspect_ratio = "auto"
			if (entry_type == 'MM'):  aspect_ratio = shape( reads_array[order, :] )[1] / float( shape(reads_array)[0]  )
			#imshow(trace_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean(), aspect=aspect_ratio, interpolation='nearest')
			imshow(reads_array[order, :], cmap=get_cmap('Greys'))
			#apply_xlabels( construct_section )
			xticks( [],[] )
			#apply_ylabels( construct_section )
			savefig(dir+'/trace.png')
			has_traces = True


		figure(2)
		clf()

		aspect_ratio = "auto"
		if (entry_type == 'MM'):  aspect_ratio = "equal" #aspect_ratio = shape(values_array)[0]/ float( shape( values_array )[1] )

		imshow(values_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=values_array.mean(), aspect=aspect_ratio, interpolation='nearest')


		frame = gca()
		frame.axes.get_xaxis().set_visible(False)
		frame.axes.get_yaxis().set_visible(False)
		#apply_xlabels( construct_section )
		#apply_ylabels( construct_section )
		ylim( [-0.5, shape( values_array )[0]-0.5  ] )
		savefig(dir+'/values.png')

		#figure(1)
		#clf()
		#matshow(corrcoef(values_array.T)**10)
		#savefig(dir+'/corrcoef.png')
		if entry_type == 'SS' and values_dims[0] < 100:
			for j in range(values_dims[0]):
				figure(1)
				clf()
				bar(range(values_dims[1]), values_array[j,:], yerr=errors_array[j,:])
				bartitle = '  '.join( [','.join(x) if type(x) == list else str(x) for x in construct_section.data[j].annotations.values()] )
				suptitle( bartitle )
				#apply_xlabels( construct_section )
				xlim( [0, shape( values_array )[1] ] )
				savefig(dir+'/barplot%s.png'%j)

	return has_traces



# def generate_images(construct_model, construct_section, entry_type, engine='matplotlib'):
# 	dir = CONSTRUCT_IMG_DIR+'%s/'%construct_model.id
# 	if not os.path.exists(dir):
# 		os.mkdir(dir)
# 	values_array, trace_array, xsel_array, errors_array = get_arrays(construct_section.data)
# 	values_dims = shape(values_array)
# 	trace_dims = shape(trace_array)
# 	values_mean = values_array.mean(axis=0)
# 	values_std = values_array.std(axis=0)
# 	if engine == 'matplotlib':
# 		if size(trace_array) > 0:
# 			figure(2)
# 			aspect_ratio = "auto"
# 			if (entry_type == 'MM'):  aspect_ratio = shape( trace_array )[1] / float( shape( trace_array)[0]  )
# 			imshow(trace_array, cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean(), aspect=aspect_ratio, interpolation='nearest')
# 			#apply_xlabels( construct_section )
# 			xticks( [],[] )
# 			apply_ylabels( construct_section )
# 			savefig(dir+'/trace.png')
# 			has_traces = True
# 		else:
# 			has_traces = False

# 		figure(2)
# 		clf()

# 		aspect_ratio = "auto"
# 		if (entry_type == 'MM'):  aspect_ratio = "equal" #aspect_ratio = shape(values_array)[0]/ float( shape( values_array )[1] )

# 		#imshow(values_array, cmap=get_cmap('Greys'), vmin=0, vmax=values_array.mean(), aspect=aspect_ratio, interpolation='nearest')
# 		imshow(values_array, cmap=get_cmap('Greys'), vmin=0, vmax=values_array.max(), aspect=aspect_ratio, interpolation='nearest')

# 		apply_xlabels( construct_section )
# 		apply_ylabels( construct_section )
# 		ylim( [-0.5, shape( values_array )[0]-0.5  ] )
# 		savefig(dir+'/values.png')

# 		figure(1)
# 		clf()
# 		#matshow(corrcoef(values_array.T)**10)
# 		#savefig(dir+'/corrcoef.png')
# 		if entry_type == 'SS':
# 			for j in range(values_dims[0]):
# 				figure(1)
# 				clf()
# 				yerr=errors_array[j,:]
# 				if len( yerr ) == 0:
# 				yerr = values_array[j,:]*0.01 #placeholder
# 				yval = values_array[j,:]
# 				for m in range( len( yval) ):
# 				if yval[m] < 0.0: yval[m] = 0.0
# 				bar(range(values_dims[1]), yval, yerr)
# 				bartitle = ''
# 				for vals in  construct_section.data[j].annotations.values(): bartitle += ' '.join( vals )
# 				suptitle( bartitle )
# 				apply_xlabels( construct_section )
# 				xlim( [0, shape( values_array )[1] ] )
# 				savefig(dir+'/barplot%s.png'%j)


# 	elif engine == 'matlab':
# 		h = mlab.figure(1)
# 		mlab.clf()
# 		mlab.colormap( 1 - mlab.gray(100));
# 		mlab.image( 100 * trace_array/trace_array.mean().mean()  )
# 		mlab.saveas(h, dir+'/trace.png')
# 		h = mlab.figure(2)
# 		mlab.clf()
# 		mlab.colormap( 1 - mlab.gray(100));
# 		mlab.image( 100 * values_array/values_array.mean().mean()  )
# 		mlab.saveas(h, dir+'/values.png')
# 		figure(3)
# 		clf()
# 		hist(values_array.reshape(size(values_array)), 50)
# 		savefig(dir+'/values_hist.png')
# 		figure(3)
# 		clf()
# 		hist(trace_array.reshape(size(trace_array)), 50)
# 		savefig(dir+'/trace_hist.png')
# 		figure(1)
# 		clf()
# 		matshow(corrcoef(values_array.T)**10)
# 		savefig(dir+'/corrcoef.png')
# 		figure(1)
# 		clf()
# 		bar(range(values_dims[1]), values_mean, yerr=values_std)
# 		seq = ''
# 		for i in construct_section.seqpos:
# 		seq += construct_section.sequence[i - construct_section.offset]
# 		labels = ['%s%s' % (s,construct_section.seqpos[i]) for i, s in enumerate(seq)]
# 		xticks(range(len(labels)), labels, rotation=90)
# 		savefig(dir+'/barplot.png')
# 	else:
# 		raise Exception('Uknown plotting engine '+engine)
# 	return has_traces
