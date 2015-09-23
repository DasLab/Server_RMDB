from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

from collections import defaultdict
from datetime import date, datetime, timedelta
import operator
# import os
import pickle
import pytz
import simplejson
import subprocess
# import sys
from time import sleep, mktime
import traceback

import boto.ec2.cloudwatch
import dropbox
import gviz_api
from github import Github
import requests
from slacker import Slacker

from src.console import *
from src.settings import *


def cache_aws(request):
    if request['qs'] == 'init':
        dict_aws = {'ec2':[], 'elb':[], 'ebs':[], 'table':[]}
        conn = boto.ec2.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)

        resvs = conn.get_only_instances()
        for i, resv in enumerate(resvs):
            sub_conn = boto.ec2.cloudwatch.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
            data = sub_conn.get_metric_statistics(600, datetime.utcnow() - timedelta(hours=2), datetime.utcnow(), 'CPUCreditBalance', 'AWS/EC2', 'Average', {'InstanceId': resv.id}, 'Count')
            avg = 0
            for d in data:
                avg += d[u'Average']
            if len(data):
                avg = avg / len(data)
            name = ''
            if resv.tags.has_key('Name'): name = resv.tags['Name']
            dict_aws['ec2'].append({'name':name, 'type':resv.instance_type, 'dns':resv.dns_name, 'status':resv.state_code, 'arch':resv.architecture, 'region':resv.placement, 'credit': '%.1f' % avg, 'id':resv.id})

        resvs = conn.get_all_volumes()
        for i, resv in enumerate(resvs):
            name = ''
            if resv.tags.has_key('Name'): name = resv.tags['Name']
            dict_aws['ebs'].append({'name':name, 'size':resv.size, 'type':resv.type, 'region':resv.zone, 'encrypted':resv.encrypted, 'status':resv.status, 'id':resv.id})

        conn = boto.ec2.elb.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
        resvs = conn.get_all_load_balancers()
        for i, resv in enumerate(resvs):
            sub_conn = boto.ec2.cloudwatch.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
            data = sub_conn.get_metric_statistics(300, datetime.utcnow() - timedelta(minutes=30), datetime.utcnow(), 'HealthyHostCount', 'AWS/ELB', 'Maximum', {'LoadBalancerName': resv.name}, 'Count')
            status = True
            for d in data:
                if d[u'Maximum'] < 1: 
                    status = False
                    break
            dict_aws['elb'].append({'name':resv.name, 'dns':resv.dns_name, 'region': ', '.join(resv.availability_zones), 'status':status})

        dict_aws['ec2'] = sorted(dict_aws['ec2'], key=operator.itemgetter(u'name'))
        dict_aws['ebs'] = sorted(dict_aws['ebs'], key=operator.itemgetter(u'name'))
        dict_aws['elb'] = sorted(dict_aws['elb'], key=operator.itemgetter(u'name'))

        for i in range(max(len(dict_aws['ec2']), len(dict_aws['elb']), len(dict_aws['ebs']))):
            temp = {}
            if i < len(dict_aws['ec2']):
                temp.update({'ec2': {'name':dict_aws['ec2'][i]['name'], 'status':dict_aws['ec2'][i]['status'], 'id':dict_aws['ec2'][i]['id']}})
            if i < len(dict_aws['ebs']):
                temp.update({'ebs': {'name':dict_aws['ebs'][i]['name'], 'status':dict_aws['ebs'][i]['status'], 'id':dict_aws['ebs'][i]['id']}})
            if i < len(dict_aws['elb']):
                temp.update({'elb': {'name':dict_aws['elb'][i]['name'], 'status':dict_aws['elb'][i]['status']}})
            dict_aws['table'].append(temp)
        return simplejson.dumps(dict_aws)
    else:
        qs = request['qs']
        id = request['id']
        tp = request['tp']

        conn = boto.ec2.cloudwatch.connect_to_region(AWS['REGION'], aws_access_key_id=AWS['ACCESS_KEY_ID'], aws_secret_access_key=AWS['SECRET_ACCESS_KEY'], is_secure=True)
        if tp in ['ec2', 'elb', 'ebs']:
            args = {'period':3600, 'start_time':datetime.utcnow() - timedelta(days=1), 'end_time':datetime.utcnow()}
        else:
            return HttpResponseBadRequest("Invalid query.")

        if qs == 'lat':
            args.update({'metric':['Latency'], 'namespace':'AWS/ELB', 'cols':['Maximum'], 'dims':{}, 'unit':'Seconds', 'calc_rate':False})
        elif qs == 'req':
            args.update({'metric':['RequestCount'], 'namespace':'AWS/ELB', 'cols':['Sum'], 'dims':{}, 'unit':'Count', 'calc_rate':False})
        elif qs == 'net':
            args.update({'metric':['NetworkIn', 'NetworkOut'], 'namespace':'AWS/EC2', 'cols':['Sum'], 'dims':{}, 'unit':'Bytes', 'calc_rate':True})
        elif qs == 'cpu':
            args.update({'metric':['CPUUtilization'], 'namespace':'AWS/EC2', 'cols':['Average'], 'dims':{}, 'unit':'Percent', 'calc_rate':False})
        elif qs == 'disk':
            args.update({'metric':['VolumeWriteBytes', 'VolumeReadBytes'], 'namespace':'AWS/EBS', 'cols':['Sum'], 'dims':{}, 'unit':'Bytes', 'calc_rate':True})

    if args['namespace'] == 'AWS/ELB':
        args['dims'] = {'LoadBalancerName': id}
    elif args['namespace'] == 'AWS/EC2':
        args['dims'] = {'InstanceId': id}
    elif args['namespace'] == 'AWS/EBS':
        args['dims'] = {'VolumeId': id}
    return aws_call(conn, args, qs)


def dash_aws(request):
    if request.GET.has_key('qs') and request.GET.has_key('id') and request.GET.has_key('tp') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        id = request.GET.get('id')
        tp = request.GET.get('tp')
        req_id = request.GET.get('tqx').replace('reqId:', '')

        if qs == 'init':
            f = open('%s/cache/aws/init.pickle' % MEDIA_ROOT, 'rb')
            result = pickle.load(f)
            f.close()
            return result
        elif qs in ['cpu', 'net', 'lat', 'req', 'disk']:
            f = open('%s/cache/aws/%s_%s_%s.pickle' % (MEDIA_ROOT, tp, id, qs), 'rb')
            (data_table, stats) = pickle.load(f)
            f.close()
            results = data_table.ToJSonResponse(columns_order=stats, order_by='Timestamp', req_id=req_id)
            return results
        else:
            return HttpResponseBadRequest("Invalid query.")
    else:
        return HttpResponseBadRequest("Invalid query.")


def cache_ga(request):
    if request['qs'] == 'init':
        access_token = requests.post('https://www.googleapis.com/oauth2/v3/token?refresh_token=%s&client_id=%s&client_secret=%s&grant_type=refresh_token' % (GA['REFRESH_TOKEN'], GA['CLIENT_ID'], GA['CLIENT_SECRET'])).json()['access_token']
        list_proj = requests.get('https://www.googleapis.com/analytics/v3/management/accountSummaries?access_token=%s' % access_token).json()['items'][0]['webProperties'][::-1]
        url_colon = urllib.quote(':')
        url_comma = urllib.quote(',')
        dict_ga = {'access_token':access_token, 'client_id':GA['CLIENT_ID'], 'projs':[]}

        for proj in list_proj:
            dict_ga['projs'].append({'id':proj['profiles'][0]['id'], 'track_id':proj['id'], 'name':proj['name'], 'url':proj['websiteUrl']})

        for j, proj in enumerate(dict_ga['projs']):
            temp = requests.get('https://www.googleapis.com/analytics/v3/data/ga?ids=ga%s%s&start-date=30daysAgo&end-date=yesterday&metrics=ga%ssessionDuration%sga%sbounceRate%sga%spageviewsPerSession%sga%spageviews%sga%ssessions%sga%susers&access_token=%s' % (url_colon, proj['id'], url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, url_comma, url_colon, access_token)).json()['totalsForAllResults']
            for i, key in enumerate(temp):
                ga_key = key[3:]
                if ga_key in ['bounceRate', 'pageviewsPerSession']:
                    curr = '%.2f' % float(temp[key])
                elif ga_key == 'sessionDuration':
                    curr = str(timedelta(seconds=int(float(temp[key]) / 1000)))
                else:
                    curr = '%d' % int(temp[key])
                dict_ga['projs'][j][ga_key] = curr
        return simplejson.dumps(dict_ga)
    else:
        url_colon = urllib.quote(':')
        temp = requests.get('https://www.googleapis.com/analytics/v3/data/ga?ids=ga%s%s&start-date=30daysAgo&end-date=yesterday&metrics=ga%s%s&dimensions=ga%sdate&access_token=%s' % (url_colon, request['id'], url_colon, request['qs'], url_colon, request['access_token'])).json()['rows']

        data = []
        stats = ['Timestamp']
        if request['qs'] == 'sessions':
            desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', 'Count')}
            fields = ['Sessions']
        else:
            desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', 'Percent')}
            fields = ['percentNewSessions']

        for row in temp:
            data.append({u'Timestamp': datetime.strptime(row[0], '%Y%m%d'), fields[0]: float(row[1])})

        for field in fields:
            stats.append(field)
            desp[field] = ('number', field)
        
        data = sorted(data, key=operator.itemgetter(stats[0]))
        data_table = gviz_api.DataTable(desp)
        data_table.LoadData(data)
        return (data_table, stats)


def dash_ga(request):
    if request.GET.has_key('qs') and request.GET.has_key('id') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        id = request.GET.get('id')
        req_id = request.GET.get('tqx').replace('reqId:', '')

        if qs == 'init':
            f = open('%s/cache/ga/init.pickle' % MEDIA_ROOT, 'rb')
            results = pickle.load(f)
            f.close()
            return results
        elif qs in ['sessions', 'percentNewSessions']:
            f = open('%s/cache/ga/%s_%s.pickle' % (MEDIA_ROOT, id, qs), 'rb')
            (data_table, stats) = pickle.load(f)
            f.close()
            results = data_table.ToJSonResponse(columns_order=stats, order_by='Timestamp', req_id=req_id)
            return results
        else:
            return HttpResponseBadRequest("Invalid query.")
    else:
        return HttpResponseBadRequest("Invalid query.")



def cache_git(request):
    # if request.GET.has_key('qs') and request.GET.has_key('repo') and request.GET.has_key('tqx'):
    gh = Github(login_or_token=GIT["ACCESS_TOKEN"])
    qs = request['qs']

    if qs == 'init':
        repos = []
        for repo in gh.get_organization('DasLab').get_repos():
            i = 0
            contribs = repo.get_stats_contributors()
            while (contribs is None and i <= 5):
                sleep(1)
                contribs = repo.get_stats_contributors()
            if contribs is None: raise Exception("PyGithub failed")
            data = []
            for contrib in contribs:
                a, d = (0, 0)
                for w in contrib.weeks:
                    a += w.a
                    d += w.d
                data.append({u'Contributors': contrib.author.login, u'Commits': contrib.total, u'Additions': a, u'Deletions': d})

            data = sorted(data, key=operator.itemgetter(u'Commits'), reverse=True)[0:4]
            repos.append({'url':repo.html_url, 'private':repo.private, 'data':data, 'name':repo.name, 'id':repo.full_name})
        return simplejson.dumps({'git':repos})
    else:
        if qs == 'num':
            name = 'DasLab/' + request['repo']
            repo = gh.get_repo(name)
            created_at = repo.created_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
            pushed_at = repo.pushed_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
            
            num_issues = len(requests.get('https://api.github.com/repos/' + name + '/issues?access_token=%s' % GIT['ACCESS_TOKEN']).json())
            num_pulls = len(requests.get('https://api.github.com/repos/' + name + '/pulls?access_token=%s' % GIT['ACCESS_TOKEN']).json())
            num_watchers = len(requests.get('https://api.github.com/repos/' + name + '/watchers?access_token=%s' % GIT['ACCESS_TOKEN']).json())
            num_branches = len(requests.get('https://api.github.com/repos/' + name + '/branches?access_token=%s' % GIT['ACCESS_TOKEN']).json())
            num_forks = len(requests.get('https://api.github.com/repos/' + name + '/forks?access_token=%s' % GIT['ACCESS_TOKEN']).json())
            num_downloads = len(requests.get('https://api.github.com/repos/' + name + '/downloads?access_token=%s' % GIT['ACCESS_TOKEN']).json())
            return simplejson.dumps({'name':request['repo'], 'created_at':created_at, 'pushed_at':pushed_at, 'num_watchers':num_watchers, 'num_pulls':num_pulls, 'num_issues':num_issues, 'num_branches':num_branches, 'num_forks':num_forks, 'num_downloads':num_downloads})

        elif qs in ['c', 'ad']:
            repo = gh.get_repo('DasLab/' + request['repo'])
            data = []
            desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', 'Count')}
            stats = ['Timestamp']

            if qs == 'c':
                i = 0
                contribs = repo.get_stats_commit_activity()
                while (contribs is None and i <= 5):
                    sleep(1)
                    contribs = repo.get_stats_commit_activity()
                if contribs is None: raise Exception("PyGithub failed")
                fields = ['Commits']
                for contrib in contribs: 
                    data.append({u'Timestamp': contrib.week, u'Commits': sum(contrib.days)})
            elif qs == 'ad':
                i = 0
                contribs = repo.get_stats_code_frequency()
                while (contribs is None and i <= 5):
                    sleep(1)
                    contribs = repo.get_stats_code_frequency()
                if contribs is None: raise Exception("PyGithub failed")
                fields = ['Additions', 'Deletions']
                for contrib in contribs:
                    data.append({u'Timestamp': contrib.week, u'Additions': contrib.additions, u'Deletions': contrib.deletions})

            for field in fields:
                stats.append(field)
                desp[field] = ('number', field)
            
            data = sorted(data, key=operator.itemgetter(stats[0]))
            data_table = gviz_api.DataTable(desp)
            data_table.LoadData(data)
            return (data_table, stats)


def dash_git(request):
    if request.GET.has_key('qs') and request.GET.has_key('repo') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        repo = request.GET.get('repo')
        req_id = request.GET.get('tqx').replace('reqId:', '')

        if qs == 'init':
            f = open('%s/cache/git/init.pickle' % MEDIA_ROOT, 'rb')
            result = pickle.load(f)
            f.close()
            return result
        elif qs in ['c', 'ad', 'num']:
            f = open('%s/cache/git/%s_%s.pickle' % (MEDIA_ROOT, repo, qs), 'rb')
            if qs == 'num':
                results = pickle.load(f)
            else:
                (data_table, stats) = pickle.load(f)
                results = data_table.ToJSonResponse(columns_order=stats,    order_by='Timestamp', req_id=req_id)
            f.close()
            return results
        else:
            return HttpResponseBadRequest("Invalid query.")
    else:
        return HttpResponseBadRequest("Invalid query.")


def cache_slack(request):
    qs = request['qs']
    sh = Slacker(SLACK["ACCESS_TOKEN"])

    if qs in ['users', 'home']:
        response = sh.users.list().body['members']
        owners, admins, users, gones = [], [], [], []
        for resp in response:
            if resp.has_key('is_bot') and resp['is_bot']: continue
            presence = sh.users.get_presence(resp['id']).body['presence']
            presence = (presence == 'active')
            temp = {'name':resp['profile']['real_name'], 'id':resp['name'], 'email':resp['profile']['email'], 'image':resp['profile']['image_24'], 'presence':presence}
            if qs == 'home':
                if not resp['deleted']: users.append(temp)
            else:
                if resp['deleted']:
                    gones.append(temp)
                elif resp['is_owner']:
                    owners.append(temp)
                elif resp['is_admin']:
                    admins.append(temp)
                else:
                    users.append(temp)
        json = {'users':users, 'admins':admins, 'owners':owners, 'gones':gones}
    elif qs == 'channels':
        response = sh.channels.list().body['channels']
        channels, archives = [], []
        for resp in response:
            temp = {'name':resp['name'], 'num_members':resp['num_members']}
            history = sh.channels.history(channel=resp['id'], count=1000, inclusive=1).body
            temp.update({'num_msgs':len(history['messages']), 'has_more':history['has_more']})
            num_files = 0
            latest = 0
            for msg in history['messages']:
                if msg.has_key('file'): num_files += 1
                latest = max(latest, float(msg['ts']))
            latest = datetime.fromtimestamp(latest).strftime('%Y-%m-%d %H:%M:%S')
            temp.update({'latest':latest, 'num_files':num_files})
            if resp['is_archived']:
                archives.append(temp)
            else:
                channels.append(temp)
        json = {'channels':channels, 'archives':archives}
    elif qs == 'files':
        types = ['all', 'pdfs', 'images', 'gdocs', 'zips', 'posts', 'snippets']
        nums, sizes = [], []
        for t in types:
            response = sh.files.list(count=100, types=t).body
            size = 0
            for i in range(response['paging']['pages']):
                page = sh.files.list(count=100, types=t, page=i).body['files']
                for p in page:
                    size += p['size']
            nums.append(response['paging']['total'])
            sizes.append(size)
        json = {'files':{'types':types, 'nums':nums, 'sizes':sizes}}

    elif qs in ["plot_files", "plot_msgs"]:
        desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', 'Count')}
        stats = ['Timestamp']
        data = []

        if qs == 'plot_files':
            fields = ['Files']
            for i in range(7):
                start_time = datetime.today() - timedelta(days=i+1)
                end_time = start_time + timedelta(days=1)
                num = sh.files.list(types="all", ts_from=mktime(start_time.timetuple()), ts_to=mktime(end_time.timetuple())).body['paging']['total']
                data.append({u'Timestamp': end_time.replace(hour=0, minute=0, second=0, microsecond=0), u'Files': num})
        elif qs == 'plot_msgs':
            fields = ['Messages']
            response = sh.channels.list().body['channels']
            for resp in response:
                if resp['is_archived']: continue
                for i in range(7):
                    start_time = datetime.today() - timedelta(days=i+1)
                    end_time = start_time + timedelta(days=1)
                    num = len(sh.channels.history(channel=resp['id'], latest=mktime(end_time.timetuple()), oldest=mktime(start_time.timetuple()), count=1000).body['messages'])
                    if len(data) > i:
                        data[i]['Messages'] += num
                    else:
                        data.append({u'Timestamp': end_time.replace(hour=0, minute=0, second=0, microsecond=0), u'Messages': num})

        for field in fields:
            stats.append(field)
            desp[field] = ('number', field)
        
        data = sorted(data, key=operator.itemgetter(stats[0]))
        data_table = gviz_api.DataTable(desp)
        data_table.LoadData(data)
        return (data_table, stats)

    return simplejson.dumps(json)


def dash_slack(request):
    if request.GET.has_key('qs') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        req_id = request.GET.get('tqx').replace('reqId:', '')

        if qs in ['users', 'home', 'channels', 'files']:
            f = open('%s/cache/slack/%s.pickle' % (MEDIA_ROOT, qs), 'rb')
            result = pickle.load(f)
            f.close()
            return result

        elif qs in ["plot_files", "plot_msgs"]:
            f = open('%s/cache/slack/%s.pickle' % (MEDIA_ROOT, qs), 'rb')
            (data_table, stats) = pickle.load(f)
            results = data_table.ToJSonResponse(columns_order=stats,    order_by='Timestamp', req_id=req_id)
            f.close()
            return results
        else:
            return HttpResponseBadRequest("Invalid query.")
    else:
        return HttpResponseBadRequest("Invalid query.")


def cache_dropbox(request):
    qs = request['qs']
    dh = dropbox.client.DropboxClient(DROPBOX["ACCESS_TOKEN"])

    if qs == 'sizes':
        account = dh.account_info()
        json = {'quota_used':account['quota_info']['shared'], 'quota_all':account['quota_info']['quota']}
        json.update({'quota_avail':(json['quota_all'] - json['quota_used'])})
        return simplejson.dumps(json)

    elif qs == "folders":
        json = []
        sizes = {}
        cursor = None
        while cursor is None or result['has_more']:
            result = dh.delta(cursor)
            for path, metadata in result['entries']:
                sizes[path] = metadata['bytes'] if metadata else 0
            cursor = result['cursor']

        folder_sizes = defaultdict(lambda: 0)
        folder_nums = defaultdict(lambda: 0)
        for path, size in sizes.items():
            segments = path.split('/')
            for i in range(1, len(segments)):
                folder = '/'.join(segments[:i])
                if folder == '': folder = '/'
                folder_sizes[folder] += size
                folder_nums[folder] += 1

        shares = requests.get("https://api.dropboxapi.com/1/shared_folders/?include_membership=True&access_token=%s" % DROPBOX["ACCESS_TOKEN"]).json()
        folder_shares = defaultdict(lambda: 0)
        for f in shares:
            folder_shares[f['shared_folder_name'].lower()] = len(f['membership'])

        for folder in sorted(folder_sizes.keys()):
            if folder == '/' or '/' in folder[1:]: continue
            result = dh.metadata(folder, list=False)
            latest = datetime.strptime(result['modified'][:-6], "%a, %d %b %Y %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
            json.append({'name':result['path'][1:], 'nums':folder_nums[folder], 'sizes':folder_sizes[folder], 'shares':folder_shares[folder[1:]], 'latest':latest})
        return simplejson.dumps({'folders':json})

    elif qs == "history":
        desp = {'Timestamp':('datetime', 'Timestamp'), 'Samples':('number', 'Samples'), 'Unit':('string', 'Count')}
        stats = ['Timestamp']
        data = []
        fields = ['Files']

        sizes = {}
        cursor = None
        while cursor is None or result['has_more']:
            result = dh.delta(cursor)
            for path, metadata in result['entries']:
                sizes[path] = metadata['modified'] if metadata else 0
            cursor = result['cursor']

        temp = {}
        for i in range(8):
            ts = (datetime.utcnow() - timedelta(days=i)).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).replace(hour=0, minute=0, second=0, microsecond=0)
            temp.update({ts:0})
        for path, ts in sizes.items():
                ts = datetime.strptime(ts[:-6], "%a, %d %b %Y %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE))
                for i in range(7):
                    ts_u = (datetime.utcnow() - timedelta(days=i)).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).replace(hour=0, minute=0, second=0, microsecond=0)
                    ts_l = (datetime.utcnow() - timedelta(days=i+1)).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIME_ZONE)).replace(hour=0, minute=0, second=0, microsecond=0)
                    if ts <= ts_u and ts > ts_l:
                        temp[ts_u] += 1
                        break
        data = []
        for ts in temp.keys():
            data.append({u'Timestamp':ts, u'Files':temp[ts]})

        for field in fields:
            stats.append(field)
            desp[field] = ('number', field)
        
        data = sorted(data, key=operator.itemgetter(stats[0]))
        data_table = gviz_api.DataTable(desp)
        data_table.LoadData(data)
        return (data_table, stats)


def dash_dropbox(request):
    if request.GET.has_key('qs') and request.GET.has_key('tqx'):
        qs = request.GET.get('qs')
        req_id = request.GET.get('tqx').replace('reqId:', '')

        if qs in ['sizes', 'folders']:
            f = open('%s/cache/dropbox/%s.pickle' % (MEDIA_ROOT, qs), 'rb')
            result = pickle.load(f)
            f.close()
            return result

        elif qs == 'history':
            f = open('%s/cache/dropbox/%s.pickle' % (MEDIA_ROOT, qs), 'rb')
            (data_table, stats) = pickle.load(f)
            results = data_table.ToJSonResponse(columns_order=stats,    order_by='Timestamp', req_id=req_id)
            f.close()
            return results
        else:
            return HttpResponseBadRequest("Invalid query.")
    else:
        return HttpResponseBadRequest("Invalid query.")


def dash_ssl(request):
    subprocess.check_call('echo | openssl s_client -connect daslab.stanford.edu:443 | openssl x509 -noout -enddate > %s' % os.path.join(MEDIA_ROOT, 'data/temp.txt'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    exp_date = subprocess.Popen('sed %s %s' % ("'s/^notAfter\=//g'", os.path.join(MEDIA_ROOT, 'data/temp.txt')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()
    subprocess.check_call('rm %s' % os.path.join(MEDIA_ROOT, 'data/temp.txt'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    exp_date = datetime.strptime(exp_date.replace('notAfter=', ''), "%b %d %H:%M:%S %Y %Z").strftime('%Y-%m-%d %H:%M:%S')
    return simplejson.dumps({'exp_date':exp_date})


def cache_schedule():
    # if not DEBUG: 
    #     gdrive_dir = 'sudo cd %s' % APACHE_ROOT
    #     gdrive_mv = 'mv Das\ Group\ Meeting\ Schedule.csv %s/data/schedule.csv' % MEDIA_ROOT
    # else:
    gdrive_dir = 'cd %s/cache' % MEDIA_ROOT
    gdrive_mv = 'mv Das\ Group\ Meeting\ Schedule.csv schedule.csv'
    try:
        subprocess.check_call("%s && drive download --format csv --force -i %s && %s" % (gdrive_dir, DRIVE["SPREADSHEET_ID"], gdrive_mv), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print traceback.format_exc()
        raise Exception('Error with downloading schedule spreadsheet.')

    try:
        f = open('%s/cache/schedule.csv' % MEDIA_ROOT, 'r')
        lines = f.readlines()
        f.close()
        tp = lines[0].split(',')[5]
        for row in lines:
            row = row.split(',')
            if 'this' in locals(): 
                next = (datetime.strptime(row[1], '%m/%d/%Y').strftime('%b %d'), row[2], row[3], row[5])
                break
            if len(row) >= 9 and row[8] == '[NEXT]':
                this = (datetime.strptime(row[1], '%m/%d/%Y').strftime('%b %d'), row[2], row[3], row[5])
                
        if not 'this' in locals(): raise Exception('Error with parsing spreadsheet csv: no [NEXT] found.')
        for row in reversed(lines):
            row = row.split(',')
            if len(row) == 10 and any(row):
                last = (datetime.strptime(row[1], '%m/%d/%Y').strftime('%b %d'), row[2], row[3], row[5])
                break

        subprocess.check_call("rm %s/cache/schedule.csv" % MEDIA_ROOT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return {'last':last, 'this':this, 'next':next, 'tp':tp}
    except:
        print traceback.format_exc()
        raise Exception('Error with parsing spreadsheet csv.')


def dash_schedule(request):
    f = open('%s/cache/schedule.pickle' % MEDIA_ROOT, 'rb')
    result = pickle.load(f)
    f.close()
    return result


def cache_cal():
    ics = subprocess.Popen('curl --silent --request GET "%s"' % GCAL['ICS'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip()
    cal = Calendar.from_ical(ics)
    data = []

    format_UTC = "%Y-%m-%d %H:%M:%S"
    for event in cal.walk('vevent'):
        title = event.get('SUMMARY')
        start = event.get('DTSTART').dt
        end = event.get('DTEND').dt

        all_day = (not isinstance(start, datetime))
        if all_day:
            color = "#29be92"
        else:
            color = "#5496d7"
        if ("group meeting" in title.lower()) or ("das lab group" in title.lower()):
            color = "#ff5c2b"
        if "BD" in title or 'b-day' in title or 'birthday' in title.lower():
            color = "#c28fdd"
        data.append({'title':title, 'start':datetime.strftime(start, format_UTC), 'end':datetime.strftime(end, format_UTC), 'allDay':all_day, 'color':color})

        if event.has_key('RRULE') and event.get('RRULE').has_key('FREQ'):
            rrule = event.get('RRULE')
            while True:
                if 'YEARLY' in rrule['FREQ']:
                    start += relativedelta(years=1)
                    end += relativedelta(years=1)
                elif 'MONTHLY' in rrule['FREQ']:
                    start += relativedelta(months=1)
                    end += relativedelta(months=1)
                elif 'WEEKLY' in rrule['FREQ']:
                    start += timedelta(days=7)
                    end += timedelta(days=7)
                elif 'DAILY' in rrule['FREQ']:
                    start += timedelta(days=1)
                    end += timedelta(days=1)
                else:
                    break

                until = (datetime.today() + relativedelta(years=2)).date()
                if rrule.has_key('UNTIL'): 
                    until = rrule['UNTIL'][0]
                    if isinstance(until, datetime): until = until.date()

                if all_day:
                    if start > until: break
                else:
                    if start.date() > until: break

                data.append({'title':title, 'start':datetime.strftime(start, format_UTC), 'end':datetime.strftime(end, format_UTC), 'allDay':all_day, 'color':color})

    return simplejson.dumps(data)    


def dash_cal():
    f = open('%s/cache/calendar.pickle' % MEDIA_ROOT, 'rb')
    result = pickle.load(f)
    f.close()
    return result


