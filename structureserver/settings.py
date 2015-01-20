from rmdb.settings import T47_DEV

if T47_DEV:
	TMPDIR = '~/Desktop/tmp/'
else:
	TMPDIR = '/home/daslab/rdat/rmdb/structureserver/tmp/'
