import os

MEDIA_ROOT = os.path.dirname(os.path.dirname(__file__))

class SYS_PATH:
    def __init__(self):
        self.HTML_PATH = {
            'index': MEDIA_ROOT + '/media/html/index.html',
            'browse': MEDIA_ROOT + '/media/html/browse.html',
            'detail': MEDIA_ROOT + '/media/html/detail.html',

            'about': MEDIA_ROOT + '/media/html/about.html',
            'license': MEDIA_ROOT + '/media/html/license.html',
            'history': MEDIA_ROOT + '/media/html/history.html',

            'specs': MEDIA_ROOT + '/media/html/specs.html',
            'validate': MEDIA_ROOT + '/media/html/validate.html',
            'upload': MEDIA_ROOT + '/media/html/submit.html',

            'predict': MEDIA_ROOT + '/media/html/predict.html',
            'predict_res': MEDIA_ROOT + '/media/html/predict_results.html',
            'repos': MEDIA_ROOT + '/media/html/tools.html',
            'tools_license': MEDIA_ROOT + '/media/html/tools_license.html',
            'tools_download': MEDIA_ROOT + '/media/html/tools_download.html',
            'tutorial': MEDIA_ROOT + '/media/html/tutorial_xxx.html',

            'search_res': MEDIA_ROOT + '/media/html/search_results.html',
            'adv_search': MEDIA_ROOT + '/media/html/search_advanced.html',
            'adv_search_res': MEDIA_ROOT + '/media/html/search_advanced_results.html',

            'register': MEDIA_ROOT + '/media/html/register.html',
            'login': MEDIA_ROOT + '/media/html/_login.html',

            'admin_apache': MEDIA_ROOT + '/media/admin/_apache.html',
            'admin_aws': MEDIA_ROOT + '/media/admin/_aws.html',
            'admin_ga': MEDIA_ROOT + '/media/admin/_ga.html',
            'admin_git': MEDIA_ROOT + '/media/admin/_git.html',
            'admin_backup': MEDIA_ROOT + '/media/admin/_backup.html',
            'admin_dir': MEDIA_ROOT + '/media/admin/_dir.html',
            'admin_doc': MEDIA_ROOT + '/media/admin/_doc.html',

            '400': MEDIA_ROOT + '/media/html/error_400.html',
            '401': MEDIA_ROOT + '/media/html/error_401.html',
            '403': MEDIA_ROOT + '/media/html/error_403.html',
            '404': MEDIA_ROOT + '/media/html/error_404.html',
            '500': MEDIA_ROOT + '/media/html/error_500.html',
       }

        self.DATA_DIR = {
            'CONSTRUCT_IMG_DIR': MEDIA_ROOT + '/data/construct_img/',
            'CONSTRUCT_THMB_DIR': MEDIA_ROOT + '/data/thumbs/',
            'RDAT_FILE_DIR': MEDIA_ROOT + '/data/files/',
            'ISATAB_FILE_DIR': MEDIA_ROOT + '/data/files/',

            'TMPDIR': MEDIA_ROOT + '/temp/',
        }


