from rmdb.settings import MEDIA_ROOT

CONSTRUCT_IMG_DIR = MEDIA_ROOT + '/data/construct_img/'
CONSTRUCT_THMB_DIR = MEDIA_ROOT + '/data/thumbs/'
RDAT_FILE_DIR = MEDIA_ROOT + '/data/files/'
ISATAB_FILE_DIR = MEDIA_ROOT + '/data/files/'
TMPDIR = MEDIA_ROOT + '/structureserver/tmp/'

HTML_PATH = {
	'index': 'design/html/index.html',
	'browse': 'design/html/browse.html',
	'detail': 'design/html/detail.html',

	'about': 'design/html/about.html',
	'license': 'design/html/license.html',
	'history': 'design/html/history.html',

	'specs': 'design/html/specs.html',
	'validate': 'design/html/validate.html',
	'upload': 'design/html/submit.html',

	'predict': 'design/html/predict.html',
	'predict_res': 'design/html/predict_results.html',
	'repos': 'design/html/tools.html',
	'license_mapseeker': 'design/html/tools_mapseeker_license.html',
	'link_mapseeker': 'design/html/tools_mapseeker_download.html',
	'tt_predict': 'design/html/tutorial_predict.html',
	'tt_api': 'design/html/tutorial_api.html',
	'tt_rdatkit': 'design/html/tutorial_rdatkit.html',
	'tt_hitrace': 'design/html/tutorial_hitrace.html',
	'tt_mapseeker': 'design/html/tutorial_mapseeker.html',

	'search_res': 'design/html/search_results.html',
	'adv_search': 'design/html/search_advanced.html',
	'adv_search_res': 'design/html/search_advanced_results.html',

	'register': 'design/html/register.html',

}
