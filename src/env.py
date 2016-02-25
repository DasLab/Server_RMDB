from django.template import RequestContext
from django.shortcuts import render_to_response

import environ
import os
import simplejson

from config.t47_dev import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = IS_DEVEL


def reload_conf(DEBUG, MEDIA_ROOT):
    env = environ.Env(DEBUG=DEBUG,) # set default values and casting
    environ.Env.read_env('%s/config/env.conf' % MEDIA_ROOT) # reading .env file

    env_oauth = simplejson.load(open('%s/config/oauth.conf' % MEDIA_ROOT))
    AWS = env_oauth['AWS']
    GA = env_oauth['GA']
    DRIVE = env_oauth['DRIVE']
    GIT = env_oauth['GIT']
    APACHE_ROOT = '/var/www'

    env_cron = simplejson.load(open('%s/config/cron.conf' % MEDIA_ROOT))
    CRONJOBS = env_cron['CRONJOBS']
    CRONTAB_LOCK_JOBS = env_cron['CRONTAB_LOCK_JOBS']
    KEEP_BACKUP = env_cron['KEEP_BACKUP']

    return (env, AWS, GA, DRIVE, GIT, APACHE_ROOT, CRONJOBS, CRONTAB_LOCK_JOBS, KEEP_BACKUP)


class SYS_PATH(object):
    def __init__(self, MEDIA_ROOT):
        self.HTML_PATH = {
            'index': MEDIA_ROOT + '/media/html/public_index.html',
            'browse': MEDIA_ROOT + '/media/html/public_browse.html',
            'detail': MEDIA_ROOT + '/media/html/public_detail.html',

            'about': MEDIA_ROOT + '/media/html/public_about.html',
            'license': MEDIA_ROOT + '/media/html/public_license.html',
            'history': MEDIA_ROOT + '/media/html/public_history.html',

            'specs': MEDIA_ROOT + '/media/html/public_specs.html',
            'validate': MEDIA_ROOT + '/media/html/public_validate.html',
            'upload': MEDIA_ROOT + '/media/html/public_submit.html',

            'predict': MEDIA_ROOT + '/media/html/public_predict.html',
            'predict_res': MEDIA_ROOT + '/media/html/public_predict_results.html',
            'repos': MEDIA_ROOT + '/media/html/tools.html',
            'tools_license': MEDIA_ROOT + '/media/html/tools_license.html',
            'tools_download': MEDIA_ROOT + '/media/html/tools_download.html',
            'tutorial': MEDIA_ROOT + '/media/html/tutorial_xxx.html',

            'search_res': MEDIA_ROOT + '/media/html/search_results.html',
            'adv_search': MEDIA_ROOT + '/media/html/search_advanced.html',
            'adv_search_res': MEDIA_ROOT + '/media/html/search_advanced_results.html',

            'register': MEDIA_ROOT + '/media/html/user_register.html',
            'login': MEDIA_ROOT + '/media/html/user_login.html',

            'admin_apache': MEDIA_ROOT + '/media/html/admin_apache.html',
            'admin_aws': MEDIA_ROOT + '/media/html/admin_aws.html',
            'admin_ga': MEDIA_ROOT + '/media/html/admin_ga.html',
            'admin_git': MEDIA_ROOT + '/media/html/admin_git.html',
            'admin_backup': MEDIA_ROOT + '/media/html/admin_backup.html',
            'admin_dir': MEDIA_ROOT + '/media/html/admin_dir.html',
            'admin_doc': MEDIA_ROOT + '/media/html/admin_doc.html',

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


root = environ.Path(os.path.dirname(os.path.dirname(__file__)))
MEDIA_ROOT = root()
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
PATH = SYS_PATH(MEDIA_ROOT)
# MEDIA_ROOT = os.path.join(os.path.abspath("."))
FILEMANAGER_STATIC_ROOT = root('media/admin') + '/'

(env, AWS, GA, DRIVE, GIT, APACHE_ROOT, CRONJOBS, CRONTAB_LOCK_JOBS, KEEP_BACKUP) = reload_conf(DEBUG, MEDIA_ROOT)



def error400(request, status=True):
    status = (request.GET['status'].lower() != 'false') if request.GET.has_key('status') else status
    status = 400 if status else 200
    return render_to_response(PATH.HTML_PATH['400'], {}, context_instance=RequestContext(request), status=status)
def error401(request, status=True):
    status = (request.GET['status'].lower() != 'false') if request.GET.has_key('status') else status
    status = 401 if status else 200
    return render_to_response(PATH.HTML_PATH['401'], {}, context_instance=RequestContext(request), status=status)
def error403(request, status=True):
    status = (request.GET['status'].lower() != 'false') if request.GET.has_key('status') else status
    status = 403 if status else 200
    return render_to_response(PATH.HTML_PATH['403'], {}, context_instance=RequestContext(request), status=status)
def error404(request, status=True):
    status = (request.GET['status'].lower() != 'false') if request.GET.has_key('status') else status
    status = 404 if status else 200
    return render_to_response(PATH.HTML_PATH['404'], {}, context_instance=RequestContext(request), status=status)
def error500(request, status=True):
    status = (request.GET['status'].lower() != 'false') if request.GET.has_key('status') else status
    status = 500 if status else 200
    return render_to_response(PATH.HTML_PATH['500'], {}, context_instance=RequestContext(request), status=status)
def error503(request, status=True):
    status = (request.GET['status'].lower() != 'false') if request.GET.has_key('status') else status
    status = 503 if status else 200
    return render_to_response(PATH.HTML_PATH['503'], {}, context_instance=RequestContext(request), status=status)

