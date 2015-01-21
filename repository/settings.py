from rmdb.settings import T47_DEV

if T47_DEV:
	REPO_DIR = '/MATLAB_code/rmdb/'
else:
	REPO_DIT = '/home/daslab/rdat/rmdb/'

CONSTRUCT_IMG_DIR = REPO_DIR + 'design/construct_img/'
CONSTRUCT_THMB_DIR = REPO_DIR + 'design/construct_img/thumbs/'
RDAT_FILE_DIR = REPO_DIR + 'design/rdat_files/'
ISATAB_FILE_DIR = REPO_DIR + 'design/isatab_files/'
TMPDIR = REPO_DIR + 'structureserver/tmp/'

HTML_PATH = {
	'index': 'html/index.html',
	'browse': 'html/browse.html',
	'detail': 'detail.html',
	'about': 'html/about.html',

	'specs': 'html/specs.html',
	'validate': 'html/validate.html',
	'upload': 'html/submit.html',

	'predict': 'html/predict.html',
	'predict_res': 'html/predict_results.html',
	'repos': 'html/tools.html',
	'tt_predict': 'html/tutorial_predict.html',
	'tt_api': 'html/tutorial_api.html',
	'tt_rdatkit': 'html/tutorial_rdatkit.html',
	'tt_hitrace': 'html/tutorial_hitrace.html',

	'search_res': 'html/search_results.html',
	'adv_search': 'html/search_advanced.html',
	'adv_search_res': 'html/search_advanced_results.html',

	'register': 'html/register.html',

}
