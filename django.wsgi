import os, sys
sys.stdout = sys.stderr
os.environ['HOME'] = '/var/www/tmp'
sys.path.append('/home/daslab/rdat/')
sys.path.append('/home/daslab/rdat/rmdb')
sys.path.append('/home/daslab/rdat/RNA_Mapping_Database/TapestryAnalysis/src')
sys.path.append('/home/daslab/rdatkit')
sys.path.append('/home/daslab/')
sys.path.append('/home/daslab/rdat/external/ViennaRNA-1.8.4/PythonRNA')
os.environ['DATAPATH'] = '/home/daslab/rdat/external/RNAstructure/data_tables/'
os.environ['DJANGO_SETTINGS_MODULE'] = 'rmdb.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

