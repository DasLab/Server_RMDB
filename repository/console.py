from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import operator
import os
import pytz
import simplejson
import subprocess
import sys
import textwrap
from time import sleep, mktime
import traceback
import urllib
import urllib2

from icalendar import Calendar
import boto.ec2.cloudwatch, boto.ec2.elb
import gviz_api
from github import Github
import requests

from django.core.management import call_command
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

from src.settings import *
from src.models import BackupForm, Publication


def get_backup_stat():
    ver = str(int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/news_img/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1) + '\t'
    ver += subprocess.Popen('du -h %s' % os.path.join(MEDIA_ROOT, 'data/news_img/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'
    ver += str(int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/ppl_img/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1) + '\t'
    ver += subprocess.Popen('du -h %s' % os.path.join(MEDIA_ROOT, 'data/ppl_img/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'

    ver += str(int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/pub_pdf/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1 + int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/pub_img/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1 + int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/pub_data/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1) + '\t'
    ver += subprocess.Popen('du -h --total %s %s %s | tail -1' % (os.path.join(MEDIA_ROOT, 'data/pub_pdf/'), os.path.join(MEDIA_ROOT, 'data/pub_img/'), os.path.join(MEDIA_ROOT, 'data/pub_data/')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'
    
    ver += str(int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/rot_ppt/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1 + int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/rot_data/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1) + '\t'
    ver += subprocess.Popen('du -h --total %s %s' % (os.path.join(MEDIA_ROOT, 'data/rot_ppt/'), os.path.join(MEDIA_ROOT, 'data/rot_data/')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'
    
    ver += str(int(subprocess.Popen('ls -l %s | wc -l' % os.path.join(MEDIA_ROOT, 'data/spe_ppt/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()) - 1) + '\t'
    ver += subprocess.Popen('du -h %s' % os.path.join(MEDIA_ROOT, 'data/spe_ppt/'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'

    ver += subprocess.Popen('du -h %s' % os.path.join(MEDIA_ROOT, 'backup/backup_mysql.gz'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'
    ver += subprocess.Popen('du -h %s' % os.path.join(MEDIA_ROOT, 'backup/backup_static.tgz'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'
    ver += subprocess.Popen('du -h %s' % os.path.join(MEDIA_ROOT, 'backup/backup_apache.tgz'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[0] + '\t'
    ver += '%s\t%s\t%s\t' % (os.path.join(os.path.dirname(MEDIA_ROOT), 'backup/backup_mysql.gz'), os.path.join(os.path.dirname(MEDIA_ROOT), 'backup/backup_static.tgz'), os.path.join(os.path.dirname(MEDIA_ROOT), 'backup/backup_apache.tgz'))

    gdrive_dir = 'echo'
    if not DEBUG: gdrive_dir = 'cd %s' % APACHE_ROOT
    ver += '~|~'.join(subprocess.Popen("%s && drive list -q \"title contains 'DasLab_' and (title contains '.gz' or title contains '.tgz')\"" % gdrive_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[4:])

    f = open(os.path.join(MEDIA_ROOT, 'cache/stat_backup.txt'), 'w')
    f.write(ver)
    f.close()
    subprocess.Popen('rm %s' % os.path.join(MEDIA_ROOT, 'data/temp.txt'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def get_backup_form():
    cron = subprocess.Popen('crontab -l | cut -d" " -f1-5', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()
    try:
        day_backup = cron[4]
        day_upload = cron[9]
        time_backup = '%02d:%02d' % (int(cron[1]), int(cron[0]))
        time_upload = '%02d:%02d' % (int(cron[6]), int(cron[5]))
    except:
        time_backup = time_upload = day_backup = day_upload = ''

    json = {'day_backup':day_backup, 'day_upload':day_upload, 'time_backup':time_backup, 'time_upload':time_upload}
    return simplejson.dumps(json)


def set_backup_form(request):
    time_backup = request.POST['time_backup'].split(':')
    time_upload = request.POST['time_upload'].split(':')
    day_backup = request.POST['day_backup']
    day_upload = request.POST['day_upload']

    cron_backup = '%s %s * * %s' % (time_backup[1], time_backup[0], day_backup)
    cron_upload = '%s %s * * %s' % (time_upload[1], time_upload[0], day_upload)

    f = open('%s/config/cron.conf' % MEDIA_ROOT, 'r')
    lines = f.readlines()
    f.close()

    index =  [i for i, line in enumerate(lines) if 'src.cron.backup_weekly' in line or 'src.cron.gdrive_weekly' in line or 'KEEP_BACKUP' in line]
    lines[index[0]] = '\t\t["%s", "src.cron.backup_weekly", ">> %s/cache/log_cron.log # backup_weekly"],\n' % (cron_backup, MEDIA_ROOT)
    lines[index[1]] = '\t\t["%s", "src.cron.gdrive_weekly", ">> %s/cache/log_cron.log # gdrive_weekly"],\n' % (cron_upload, MEDIA_ROOT)
    lines[index[2]] = '\t"KEEP_BACKUP": %s\n' % request.POST['keep']

    f = open('%s/config/cron.conf' % MEDIA_ROOT, 'w')
    f.writelines(lines)
    f.close()
    try:
        cron = subprocess.Popen('crontab -l | cut -d" " -f1-5', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()
        if len(cron) > 9:
            subprocess.check_call('crontab -r', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.check_call('cd %s && python manage.py crontab add' % MEDIA_ROOT, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print "    \033[41mERROR\033[0m: Failed to reset \033[94mcrontab\033[0m schedules."
        print traceback.format_exc()
        raise Exception('Error with setting crontab scheduled jobs.')
        # call_command('crontab', 'add')
    # except:
        # pass


def restyle_apache():
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    apache_url = "http://daslab.stanford.edu/server-status/"
    password_mgr.add_password(None, apache_url, env('APACHE_USER'), env('APACHE_PASSWORD'))
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)

    request = urllib2.urlopen(apache_url)
    response = request.read().split('\n')

    title = 'Apache Server Status for <code>daslab.stanford.edu</code> (via <kbd>%s</kbd> )' % response[4].replace(')</h1>', '')[-13:].replace('via ', '')
    ver = response[6].replace('<dl><dt>Server Version: Apache/', '').replace('(Ubuntu) OpenSSL/', '').replace('mod_wsgi/', '').replace('Python/', '').replace('</dt>', '').split()
    mpm = response[7].replace('<dt>Server MPM: ', '').replace('</dt>', '')
    tz = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Los_Angeles")).tzname()
    time_build = datetime.strftime(datetime.strptime(response[8].replace('<dt>Server Built: ', ''), '%b %d %Y %H:%M:%S'), '%Y-%m-%d (%A) %I:%M:%S %p') + ' (%s)' % tz
    time_current = datetime.strftime(datetime.strptime(response[10].replace('<dt>Current Time: ', '').replace('</dt>', ''), '%A, %d-%b-%Y %H:%M:%S %Z'), '%Y-%m-%d (%A) %I:%M:%S %p') + ' (%s)' % tz
    time_restart = datetime.strftime(datetime.strptime(response[11].replace('<dt>Restart Time: ', '').replace('</dt>', ''), '%A, %d-%b-%Y %H:%M:%S %Z'), '%Y-%m-%d (%A) %I:%M:%S %p') + ' (%s)' % tz
    time_up = response[14].replace('<dt>Server uptime:  ', '').replace('</dt>', '').replace('hours', '<i>h</i>').replace('hour', '<i>h</i>').replace('minutes', '<i>min</i>').replace('minute', '<i>min</i>').replace('seconds', '<i>s</i>').replace('second', '<i>s</i>')

    server_load = response[15].replace('<dt>Server load: ', '').replace('</dt>', '').replace(' ', ' / ')
    total = response[16].replace('<dt>Total accesses: ', '').replace(' - Total Traffic:', '').replace('</dt>', '').split()
    cpu = response[17].replace('<dt>CPU Usage: ', '').replace('CPU load</dt>', '').replace(' -', '').replace('%', '').replace('</dt>', '').split()
    cpu_usage = '%.2f / %.2f / %.2f / %.2f' % (float(cpu[0][1:]), float(cpu[1][1:]), float(cpu[2][2:]), float(cpu[3][2:]))
    cpu_load = '%1.4f' % float(cpu[4])
    traffic = response[18].replace('<dt>', '').replace('B/request</dt>', '').replace('requests/sec -', '').replace('B/second -', '').split()
    if traffic[-1] in ('k', 'M', 'G'): 
        traffic = '%1.2f / %.1f / %s' % (float(traffic[0]), float(traffic[-2]), traffic[-1])
    else:
        traffic = '%1.2f / %.1f' % (float(traffic[0]), float(traffic[-1]))
    workers = response[19].replace('<dt>', '').replace('requests currently being processed, ', '').replace('idle workers</dt>', '').split()
    worker = '<p style="margin-bottom:0px;">' + '</p><p style="margin-bottom:0px;">'.join(textwrap.wrap(''.join(response[20:22]).replace('</dl><pre>', '').replace('</pre>', ''), 30)).replace('.', '<span class="label label-primary">.</span>').replace('_', '<span class="label label-inverse">_</span>').replace('S', '<span class="label label-default">S</span>').replace('R', '<span class="label label-violet">R</span>').replace('W', '<span class="label label-info">W</span>').replace('K', '<span class="label label-success">K</span>').replace('D', '<span class="label label-warning">D</span>').replace('C', '<span class="label label-danger">C</span>').replace('L', '<span class="label label-orange">L</span>').replace('G', '<span class="label label-green">G</span>').replace('I', '<span class="label label-brown">I</span>') + '</p>'

    table = ''.join(response[40:len(response)-23]).replace('<td>.</td>', '<td><span class="label label-primary">.</span></td>').replace('<td>_</td>', '<td><span class="label label-inverse">_</span></td>').replace('<td><b>S</b></td>', '<td><span class="label label-default">S</span></td>').replace('<td><b>R</b></td>', '<td><span class="label label-violet">R</span></td>').replace('<td><b>W</b></td>', '<td><span class="label label-info">W</span></td>').replace('<td><b>K</b></td>', '<td><span class="label label-success">K</span></td>').replace('<td><b>D</b></td>', '<td><span class="label label-warning">D</span></td>').replace('<td><b>C</b></td>', '<td><span class="label label-danger">C</span></td>').replace('<td><b>L</b></td>', '<td><span class="label label-orange">L</span></td>').replace('<td><b>G</b></td>', '<td><span class="label label-green">G</span></td>').replace('<td><b>I</b></td>', '<td><span class="label label-brown">I</span></td>')
    ssl = response[len(response)-6].replace('<b>', '').replace('</b>', '').replace('cache type: ', '').replace(', shared memory: ', '<br>').replace(' bytes, current entries: ', '<br>').replace('subcaches: ', '').replace(', indexes per subcache: ', '<br>').replace('index usage: ', '').replace(', cache usage: ', '<br>').split('<br>')
    ssl_subcache = '%s of %s' % (ssl[6], ssl[3])
    ssl_index = '%s of %s' % (ssl[5], ssl[4])
    port = response[len(response)-3].replace('</address>', '')[-3:]

    json = {'title':title, 'ver_apache':ver[0], 'ver_wsgi':ver[2], 'ver_ssl':ver[1], 'mpm':mpm, 'time_build':time_build, 'time_current':time_current, 'time_restart':time_restart, 'time_up':time_up, 'server_load':server_load, 'total_access':total[0], 'total_traffic':'%s %s' % (total[1], total[2]), 'cpu_load':cpu_load, 'cpu_usage':cpu_usage, 'traffic':traffic, 'idle':workers[1], 'processing':workers[0], 'worker':worker, 'table':table, 'port':port, 'ssl_subcache':ssl_subcache, 'ssl_index':ssl_index, 'ssl_cache':ssl[0], 'ssl_mem': ssl[1], 'ssl_entry':ssl[2]}
    return simplejson.dumps(json)
    

def aws_result(results, args, req_id=None):
    data = []
    data.extend(results[0])
    for i, d in enumerate(data):
        ts = d[u'Timestamp'].replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE))
        d.update({u'Timestamp': ts})
        if args['calc_rate'] and 'Sum' in args['cols']: 
            d.update({args['metric'][0] + u'Rate': d[u'Sum'] / args['period']})
        for j, r in enumerate(results):
            if j == 0 and len(results) > 1 and args['calc_rate']: 
                continue
            keys = r[i].keys()
            keys.remove(u'Timestamp')
            keys.remove(u'Unit')
            for k in keys:
                val = r[i][k]
                name = args['metric'][j] + k
                if args['calc_rate'] and k == u'Sum': 
                    val = val / args['period']
                    name = args['metric'][j] + u'Rate'
                d[name] = val
                if d.has_key(k): del d[k]

    desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', args['unit'])}
    stats = ['Timestamp']
    for i, me in enumerate(args['metric']):
        if len(args['cols']) == len(args['metric']) and len(args['cols']) > 1:
            col = args['cols'][i]
            if col == 'Sum' and args['calc_rate']: col = 'Rate'
            desp[me + col] = ('number', me + col)
            stats.append(me + col)
        else:
            for col in args['cols']:
                if col == 'Sum' and args['calc_rate']: col = 'Rate'
                desp[me + col] = ('number', me + col)
                stats.append(me + col)
    
    data = sorted(data, key=operator.itemgetter(u'Timestamp'))
    data_table = gviz_api.DataTable(desp)
    data_table.LoadData(data)
    if req_id:
        results = data_table.ToJSonResponse(columns_order=stats,    order_by='Timestamp', req_id=req_id)
        return results
    else:
        return (data_table, stats)


def aws_call(conn, args, qs, req_id=None):
    results = []
    for i, me in enumerate(args['metric']):
        col = args['cols']
        if len(args['cols']) == len(args['metric']) and len(args['cols']) > 1: col = args['cols'][i]
        data = conn.get_metric_statistics(args['period'], args['start_time'], args['end_time'], me, args['namespace'], col, args['dims'], args['unit'])

        temp = []
        for d in data:
            temp.append(d[u'Timestamp'])
        period = range(0, int((args['end_time'] - args['start_time']).total_seconds()), args['period'])
        for t in (args['start_time'] + timedelta(seconds=n) for n in period):
            t = t.replace(second=0, microsecond=0)
            if (not t in temp):
                data.append({u'Timestamp':t, u'Unit':args['unit'], unicode(args['cols'][0]):0})

        if qs in ['lat', 'latency']:
            for d in data:
                d[u'Maximum'] = d[u'Maximum'] * 1000
        if qs in ['disk', 'net', 'volbytes', 'network']:
            for d in data:
                d[u'Sum'] = d[u'Sum'] / 1024
        results.append(data)
    return aws_result(results, args, req_id)


def aws_stats(request):
    if request.GET.has_key('qs') and request.GET.has_key('sp') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        sp = request.GET.get('sp')
        req_id = request.GET.get('tqx').replace('reqId:', '')

        if qs == 'init':
            conn = boto.ec2.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
            resv = conn.get_only_instances(instance_ids=AWS['EC2_INSTANCE_ID'])
            stat = resv[0].__dict__
            stat1 = {k: stat[k] for k in ('id', 'instance_type', 'private_dns_name', 'public_dns_name', 'vpc_id', 'subnet_id', 'image_id', 'architecture')} 
            resv = conn.get_all_volumes(volume_ids=AWS['EBS_VOLUME_ID'])
            stat = resv[0].__dict__
            stat2 = {k: stat[k] for k in ('id', 'type', 'size', 'zone', 'snapshot_id', 'encrypted')} 

            conn = boto.ec2.elb.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
            resv = conn.get_all_load_balancers(load_balancer_names=AWS['ELB_NAME'])
            stat = resv[0].__dict__
            stat3 = {k: stat[k] for k in ('dns_name', 'vpc_id', 'subnets', 'health_check')} 
            stat3['health_check'] = str(stat3['health_check']).replace('HealthCheck:', '')

            return simplejson.dumps({'ec2':stat1, 'ebs':stat2, 'elb':stat3})

        else:
            conn = boto.ec2.cloudwatch.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
            if sp == '7d':
                args = {'period':7200, 'start_time':datetime.utcnow() - timedelta(days=7), 'end_time':datetime.utcnow()}
            elif sp == '48h':
                args = {'period':720, 'start_time':datetime.utcnow() - timedelta(hours=48), 'end_time':datetime.utcnow()}
            else:
                return HttpResponseBadRequest("Invalid query.")

            if qs == 'latency':
                args.update({'metric':['Latency'], 'namespace':'AWS/ELB', 'cols':['Maximum'], 'dims':{}, 'unit':'Seconds', 'calc_rate':False})
            elif qs == 'request':
                args.update({'metric':['RequestCount'], 'namespace':'AWS/ELB', 'cols':['Sum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == '23xx':
                args.update({'metric':['HTTPCode_Backend_2XX', 'HTTPCode_Backend_3XX'], 'namespace':'AWS/ELB', 'cols':['Sum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == '45xx':
                args.update({'metric':['HTTPCode_Backend_4XX', 'HTTPCode_Backend_5XX'], 'namespace':'AWS/ELB', 'cols':['Sum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == 'host':
                args.update({'metric':['HealthyHostCount', 'UnHealthyHostCount'], 'namespace':'AWS/ELB', 'cols':['Minimum', 'Maximum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == 'status':
                args.update({'metric':['BackendConnectionErrors', 'StatusCheckFailed_Instance', 'StatusCheckFailed_System'], 'namespace':'AWS/EC2', 'cols':['Sum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == 'network':
                args.update({'metric':['NetworkIn', 'NetworkOut'], 'namespace':'AWS/EC2', 'cols':['Sum'], 'dims':{}, 'unit':'Bytes', 'calc_rate':True})
            elif qs == 'cpu':
                args.update({'metric':['CPUUtilization'], 'namespace':'AWS/EC2', 'cols':['Average'], 'dims':{}, 'unit':'Percent', 'calc_rate':False})
            elif qs == 'credit':
                args.update({'metric':['CPUCreditUsage', 'CPUCreditBalance'], 'namespace':'AWS/EC2', 'cols':['Average'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == 'volops':
                args.update({'metric':['VolumeWriteOps', 'VolumeReadOps'], 'namespace':'AWS/EBS', 'cols':['Sum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
            elif qs == 'volbytes':
                args.update({'metric':['VolumeWriteBytes', 'VolumeReadBytes'], 'namespace':'AWS/EBS', 'cols':['Sum'], 'dims':{}, 'unit':'Bytes', 'calc_rate':True})
            else:
                return HttpResponseBadRequest("Invalid query.")
    else:
        return HttpResponseBadRequest("Invalid query.")

    if args['namespace'] == 'AWS/ELB':
        args['dims'] = {'LoadBalancerName': AWS['ELB_NAME']}
    elif args['namespace'] == 'AWS/EC2':
        args['dims'] = {'InstanceId': AWS['EC2_INSTANCE_ID']}
    elif args['namespace'] == 'AWS/EBS':
        args['dims'] = {'VolumeId': AWS['EBS_VOLUME_ID']}

    return aws_call(conn, args, qs, req_id)


def ga_stats():
    access_token = requests.post('https://www.googleapis.com/oauth2/v3/token?refresh_token=%s&client_id=%s&client_secret=%s&grant_type=refresh_token' % (GA['REFRESH_TOKEN'], GA['CLIENT_ID'], GA['CLIENT_SECRET'])).json()['access_token']
    stats = {'access_token':access_token, 'client_id':GA['CLIENT_ID'], 'id':GA['ID']}
    url_colon = urllib.quote(':')
    url_comma = urllib.quote(',')

    temp = requests.get('https://www.googleapis.com/analytics/v3/data/ga?ids=ga%s%s&start-date=30daysAgo&end-date=yesterday&metrics=ga%ssessionDuration%sga%sbounceRate%sga%spageviewsPerSession%sga%spageviews%sga%ssessions%sga%susers&access_token=%s' % (url_colon, GA['ID'], url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, access_token)).json()['totalsForAllResults']
    temp_prev = requests.get('https://www.googleapis.com/analytics/v3/data/ga?ids=ga%s%s&start-date=60daysAgo&end-date=30daysAgo&metrics=ga%ssessionDuration%sga%sbounceRate%sga%spageviewsPerSession%sga%spageviews%sga%ssessions%sga%susers&access_token=%s' % (url_colon, GA['ID'], url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, access_token)).json()['totalsForAllResults']

    for i, key in enumerate(temp):
        ga_key = key[3:]
        if ga_key in ['bounceRate', 'pageviewsPerSession']:
            prev = '%.2f' % (float(temp[key]) - float(temp_prev[key]))
            curr = '%.2f' % float(temp[key])
        elif ga_key == 'sessionDuration':
            diff = int(float(temp[key]) / 1000) - int(float(temp_prev[key]) / 1000)
            prev = str(timedelta(seconds=abs(diff)))
            if diff < 0: prev = '-%s' % prev
            curr = str(timedelta(seconds=int(float(temp[key]) / 1000)))
        else:
            prev = '%d' % (int(temp[key]) - int(temp_prev[key]))
            curr = '%d' % int(temp[key])
        stats.update({ga_key:curr, (ga_key + '_prev'):prev})
    return simplejson.dumps(stats)


def git_stats(request):
    # gdrive_dir = 'echo'
    # if not DEBUG: gdrive_dir = 'cd %s' % APACHE_ROOT
    # try:
    #     subprocess.check_call('%s && gitinspector -wHlmrT %s -F html > %s/data/stat_git.html' % (gdrive_dir, MEDIA_ROOT, MEDIA_ROOT), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # except subprocess.CalledProcessError:
    #     print "    \033[41mERROR\033[0m: Failed to generate \033[94mgitinspector\033[0m stats."
    #     print traceback.format_exc()
    #     raise Exception('Error with generating gitinsepctor stats.')

    if request.GET.has_key('qs') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        req_id = request.GET.get('tqx').replace('reqId:', '')
        gh = Github(login_or_token=GIT["ACCESS_TOKEN"])
        repo_name = 'DasLab/Server_DasLab'
        repo = gh.get_repo(repo_name)

        if qs in ['init', 'num']:
            if qs == 'init':
                contribs = repo.get_stats_contributors()
                data = []
                i = 0
                while (contribs is None and i <= 5):
                    sleep(1)
                    contribs = repo.get_stats_contributors()
                if contribs is None: return HttpResponseServerError("PyGithub failed")

                for contrib in contribs:
                    a, d = (0, 0)
                    for w in contrib.weeks:
                        a += w.a
                        d += w.d
                    name = '<i>%s</i> <span style="color:#888">(%s)</span>' % (contrib.author.login, contrib.author.name)
                    data.append({u'Contributors': name, u'Commits': contrib.total, u'Additions': a, u'Deletions': d})
                data = sorted(data, key=operator.itemgetter(u'Commits'))            
                return simplejson.dumps({'contrib':data})
            else:
                created_at = repo.created_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
                pushed_at = repo.pushed_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
                
                num_issues = len(requests.get('https://api.github.com/repos/' + repo_name + '/issues?access_token=%s' % GIT['ACCESS_TOKEN']).json())
                num_pulls = len(requests.get('https://api.github.com/repos/' + repo_name + '/pulls?access_token=%s' % GIT['ACCESS_TOKEN']).json())
                num_watchers = len(requests.get('https://api.github.com/repos/' + repo_name + '/watchers?access_token=%s' % GIT['ACCESS_TOKEN']).json())
                num_branches = len(requests.get('https://api.github.com/repos/' + repo_name + '/branches?access_token=%s' % GIT['ACCESS_TOKEN']).json())
                num_forks = len(requests.get('https://api.github.com/repos/' + repo_name + '/forks?access_token=%s' % GIT['ACCESS_TOKEN']).json())
                num_downloads = len(requests.get('https://api.github.com/repos/' + repo_name + '/downloads?access_token=%s' % GIT['ACCESS_TOKEN']).json())
                return simplejson.dumps({'created_at':created_at, 'pushed_at':pushed_at, 'num_watchers':num_watchers, 'num_pulls':num_pulls, 'num_issues':num_issues, 'num_branches':num_branches, 'num_forks':num_forks, 'num_downloads':num_downloads})

        else:
            data = []
            desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', 'Count')}
            stats = ['Timestamp']

            if qs == 'c':
                contribs = repo.get_stats_commit_activity()
                if contribs is None: return HttpResponseServerError("PyGithub failed")
                fields = ['Commits']
                for contrib in contribs:
                    for i, day in enumerate(contrib.days):
                        data.append({u'Timestamp': contrib.week + timedelta(days=i), u'Commits': day})
            elif qs == 'ad':
                contribs = repo.get_stats_code_frequency()
                if contribs is None: return HttpResponseServerError("PyGithub failed")
                fields = ['Additions', 'Deletions']
                for contrib in contribs:
                    data.append({u'Timestamp': contrib.week, u'Additions': contrib.additions, u'Deletions': contrib.deletions})
            elif qs == 'au':
                contribs = repo.get_stats_contributors()
                if contribs is None: return HttpResponseServerError("PyGithub failed")
                fields = ['Commits', 'Additions', 'Deletions']
                for contrib in contribs:
                    a, d = (0, 0)
                    for w in contrib.weeks:
                        a += w.a
                        d += w.d
                    data.append({u'Contributors': contrib.author.login, u'Commits': contrib.total, u'Additions': a, u'Deletions': d})
                stats = ['Contributors']
                desp['Contributors'] = ('string', 'Name')
                del desp['Timestamp']
            else:
                return HttpResponseBadRequest("Invalid query.")

            for field in fields:
                stats.append(field)
                desp[field] = ('number', field)
            
            data = sorted(data, key=operator.itemgetter(stats[0]))
            data_table = gviz_api.DataTable(desp)
            data_table.LoadData(data)
            results = data_table.ToJSonResponse(columns_order=stats, order_by='Timestamp', req_id=req_id)
            return results
    else:
        return HttpResponseBadRequest("Invalid query.")


def export_citation(request):
    is_order_number = 'order_number' in request.POST
    is_quote_title = 'quote_title' in request.POST
    is_double_space = 'double_space' in request.POST
    is_include_preprint = 'include_preprint' in request.POST

    text_type = request.POST['text_type']
    year_start = int(request.POST['year_start'])
    number_order = (request.POST['number_order'] == '1')
    sort_order = 'display_date'
    if request.POST['sort_order'] == '1': sort_order = '-' + sort_order

    publications = Publication.objects.filter(year__gte=year_start).order_by(sort_order)
    if not is_include_preprint: publications = publications.filter(preprint=False)

    if text_type == '0':
        txt = ''
        for i, pub in enumerate(publications):
            order = ''
            if is_order_number: 
                if number_order:
                    order = '%d. ' % (len(publications) - i)
                else:
                    order = '%d. ' % (i + 1)
            
            title = pub.title
            if is_quote_title: title = '"%s"' % title
            number = pub.volume
            if pub.issue: number += '(%s)' % pub.issue
            page = ''
            if pub.begin_page: page += ': %s' % pub.begin_page
            if pub.end_page: page += '-%s' % pub.end_page 
            double_space = ''
            if is_double_space: double_space = '\n'
            txt += '%s%s (%s) %s %s %s%s\n%s' % (order, pub.authors, pub.year, title, pub.journal, number, page, double_space)

        response = HttpResponse(txt, content_type='text/plain')
    else:
        is_bold_author = 'bold_author' in request.POST
        is_bold_year = 'bold_year' in request.POST
        is_underline_title = 'underline_title' in request.POST
        is_italic_journal = 'italic_journal' in request.POST
        is_bold_volume = 'bold_volume' in request.POST

        html = '<html><body>'
        for i, pub in enumerate(publications):
            order = ''
            if is_order_number: 
                if number_order:
                    order = '%d. ' % (len(publications) - i)
                else:
                    order = '%d. ' % (i + 1)

            authors = pub.authors
            if is_bold_author: authors = authors.replace('Das, R.', '<b>Das, R.</b>').replace('Das R.', '<b>Das, R.</b>')
            year = pub.year
            if is_bold_year: year = '<b>%s</b>' % year
            title = pub.title
            if is_underline_title: title = '<u>%s</u>' % title
            if is_quote_title: title = '&quot;%s&quot;' % title
            journal = pub.journal
            if is_italic_journal: journal = '<i>%s</i>' % journal
            number = pub.volume
            if is_bold_volume: number = '<b>%s</b>' % number
            if pub.issue: number += '(%s)' % pub.issue
            page = ''
            if pub.begin_page: page += ': %s' % pub.begin_page
            if pub.end_page: page += '-%s' % pub.end_page 
            double_space = ''
            if is_double_space: double_space = '<br/>'
            html += '<p>%s%s (%s) %s %s %s%s</p>%s' % (order, authors, year, title, journal, number, page, double_space)

        html += '</body></html>'
        response = HttpResponse(html, content_type='text/html')
        

    if request.POST['action'] == 'save':
        if text_type == '0':
            response["Content-Disposition"] = "attachment; filename=export_citation.txt"
        else:
            f = open(os.path.join(MEDIA_ROOT, 'data/export_citation.html'), 'w')
            f.write(html.encode('UTF-8'))
            f.close()

            try:
                subprocess.check_call('cd %s/data && pandoc -f html -t docx -o export_citation.docx export_citation.html' % MEDIA_ROOT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                print "    \033[41mERROR\033[0m: Failed to export \033[94mcitation\033[0m as DOCX file."
                print traceback.format_exc()
                raise Exception('Error with pandoc converting html source file to docx output.')

            f = open(os.path.join(MEDIA_ROOT, 'data/export_citation.docx'), 'r')
            lines = f.readlines()
            f.close()

            response = HttpResponse(lines, content_type='application/msword')
            response["Content-Disposition"] = "attachment; filename=export_citation.docx"
    return response




