from rmdb.repository.settings import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *


entryfeed = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>RMDB entries</title>
<link>http://rmdb.stanford.edu/repository</link>
<description>The RNA Mapping Database is a repository of 
experimental results on RNA structural probing using mapping (a.k.a.
footprinting) techniques. This feed lists the current entries on the database.</description>
"""

rdatfeed = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>RMDB entries (RDAT files)</title>
<link>http://rmdb.stanford.edu/repository</link>
<description>The RNA Mapping Database is a repository of 
experimental results on RNA structural probing using mapping (a.k.a.
footprinting) techniques. This feed links to each entry's RDAT file.</description>
"""


isatabfeed = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>RMDB entries (ISATAB files)</title>
<link>http://rmdb.stanford.edu/repository</link>
<description>The RNA Mapping Database is a repository of 
experimental results on RNA structural probing using mapping (a.k.a.
footprinting) techniques. This feed links to each entry's ISATAB file.</description>
"""

newsfeed = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>RMDB news</title>
<link>http://rmdb.stanford.edu/repository</link>
<description>The RNA Mapping Database is a repository of 
experimental results on RNA structural probing using mapping (a.k.a.
footprinting) techniques. This feed gives news updates relevant to the databse.</description>
"""
news = NewsItem.objects.all()
entries = RMDBEntry.objects.all()

for entry in entries:
    itemstr = """
    <item>
        <title>RMDB %(rmdbid)s</title>
        <link>http://rmdb.stanford.edu/repository/detail/%(rmdbid)s</link>
        <guid>%(rmdbid)s</guid>
        <pubDate>%(date)s</pubDate>
        <description>%(description)s</description>
    </item>
    """ % { 'rmdbid':entry.rmdb_id, 'date':entry.creation_date.strftime('%a, %d %b %Y %H:%M:%S GMT'), 'description':entry.comments}
    entryfeed += itemstr
    itemstr = """
    <item>
        <title>RMDB %(rmdbid)s</title>
        <link>http://rmdb.stanford.edu/site_media/isatab_files/%(rmdbid)s/%(rmdbid)s_%(version)s.xls</link>
        <guid>%(rmdbid)s</guid>
        <pubDate>%(date)s</pubDate>
        <description>%(description)s</description>
    </item>
    """ % { 'rmdbid':entry.rmdb_id, 'date':entry.creation_date.strftime('%a, %d %b %Y %H:%M:%S GMT'), 'version':RMDBEntry.get_current_version(entry.rmdb_id) ,'description':entry.comments}
    isatabfeed += itemstr
    itemstr = """
    <item>
        <title>RMDB %(rmdbid)s</title>
        <link>http://rmdb.stanford.edu/site_media/rdat_files/%(rmdbid)s/%(rmdbid)s_%(version)s.rdat</link>
        <guid>%(rmdbid)s</guid>
        <pubDate>%(date)s</pubDate>
        <description>%(description)s</description>
    </item>
    """ % { 'rmdbid':entry.rmdb_id, 'date':entry.creation_date.strftime('%a, %d %b %Y %H:%M:%S GMT'), 'version':RMDBEntry.get_current_version(entry.rmdb_id) ,'description':entry.comments}
    rdatfeed += itemstr

entryfeed += """
</channel>
</rss>"""

for n in news:
    itemstr = """
    <item>
        <title>%(title)s</title>
        <link>%(reference)s</link>
        <guid>%(id)s</guid>
        <pubDate>%(date)s</pubDate>
        <description>%(description)s</description>
    </item>
    """ % { 'id':n.id, 'date':n.date.strftime('%a, %d %b %Y %H:%M:%S GMT'), 'description':n.title, 'title':n.title, 'reference':n.reference}
    newsfeed += itemstr
newsfeed += """
</channel>
</rss>"""

isatabfeed += """
</channel>
</rss>"""

rdatfeed += """
</channel>
</rss>"""

FEED_DIR = '/home/daslab/rdat/rmdb/design/rss/'
newsfeedfile = open(FEED_DIR + 'news.xml', 'w')
entriesfeedfile = open(FEED_DIR + 'entries.xml', 'w')
isatabfeedfile = open(FEED_DIR + 'isatab.xml', 'w')
rdatfeedfile = open(FEED_DIR + 'rdat.xml', 'w')
newsfeedfile.write(newsfeed)
entriesfeedfile.write(entryfeed)
isatabfeedfile.write(isatabfeed)
rdatfeedfile.write(rdatfeed)

