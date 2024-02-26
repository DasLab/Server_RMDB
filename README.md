# RMDB RNA Mapping DataBase

<img src="https://rmdb.stanford.edu/site_media/images/logo_rmdb.png" alt="RMDB Logo" width="200" align="right">

This is the _Source Code_ repository for **RMDB** RNA Mapping DataBase **Server**. The production server is freely accessible at https://rmdb.stanford.edu/.

## Installation

**RMDB Server** requires the following *Python* packages as dependencies, most of which can be installed through [`pip`](https://pip.pypa.io/).

```json
boto >= 2.38.0
Django >= 1.9.1
django-adminplus >= 0.5
django-crontab >= 0.7.0
django-environ >= 0.4.0
django-filemanager == 0.0.2
django-suit >= 0.2.15
django-widget-tweaks >= 1.4.1
gviz-api.py == 1.8.2
MySQL-python >= 1.2.5
PyGithub >= 1.26.0
pytz >= 2015.7
requests >= 2.9.1
simplejson >= 3.8.1
Biopython >= 1.70

rdatkit >= 1.0.2
```

The `rdatkit` package is available internally at [`RDATKit`](https://github.com/ribokit/rdatkit/).

The `gviz-api.py` is available at [`google-visualization-python`](https://github.com/google/google-visualization-python/).

The `django-filemanager` is a modified version of [`django-filemanager`](https://github.com/IMGIITRoorkee/django-filemanager/). The source code is available internally at this [fork](https://github.com/t47io/django-filemanager/).

Install with:

```sh
cd ~
git clone https://github.com/ribokit/rdatkit.git
cd rdatkit
sudo python setup.py install

cd ..
git clone https://github.com/google/google-visualization-python.git
cd google-visualization-python
sudo python setup.py install

cd ..
git clone https://github.com/t47io/django-filemanager.git
cd django-filemanager
sudo python setup.py install
```

**RMDB Server** also requires proper setup of `imagemagick`, `optipng`, `VARNA.jar`, `mysql.server`, `apache2`, `mod_wsgi`, `openssl`, `gdrive`, `awscli`, and `cron` jobs.

Lastly, assets preparation is required for the 1st time through running `sudo python manage.py versions`, `sudo python manage.py dist`, `util_prep_dir.sh`, `util_src_dist.sh`, `util_minify.sh`, `util_chmod.sh` and manually replacing `config/*.conf`. For full configuration, please refer to [**Documentation**](https://rmdb.stanford.edu/admin/setup/).


## Usage

To run the test/dev server, use:

```bash
cd path/to/server_RMDB/repo
python manage.py runserver
```

The server should be running at `localhost:8000` with a python session interactive in terminal.

To generate the JSON file for one entry, use:

```bash
cd path/to/server_RMDB/repo
python manage.py make_json RMDB_ID
```

for all entries:

```bash
cd path/to/server_RMDB/repo
python manage.py make_json -A
```

## TODO
* The major incomplete task is a total transfer of licensing of RiboKit packages out of RMDB and into [ribokit-license.stanford.edu](ribokit-license.stanford.edu). That repo is hosted at https://github.com/DasLab/Server_Ribokit_License . Its almost ready except for automatic pulls of RiboKit packages, which is coded up in Server_RMDB `dist.py` but has not yet been transferred over due to problems setting up `oauth`/Github authorization.
* Other RMDB server issues and feature wish list are described in [issues](https://github.com/DasLab/Server_RMDB/issues).


## License

**Copyright &copy; 2014-2017: Siqi Tian _[[t47](https://t47.io/)]_; 2017 Chunwen Xiong; 2017 Das Lab, Stanford University. All Rights Reserved.**

**RMDB Server** _Source Code_ is proprietary and confidential. Unauthorized copying of this repository, via any medium, is strictly prohibited.

## Maintenance for RMDB ops

#### 0. Server login and update:
- contact admin for the amazon.pem
- use `ssh -i amazon.pem ubuntu@ec2-35-91-89-102.us-west-2.compute.amazonaws.com` to login
- use `sync` to merge and update produciton version

#### 1. 500 Errors:
- Investigate **immediately** (you get admin email notice)
- Hot fix or escalate issue, or disable

#### 2. AWS instance monitoring:
- Subscribe to alerts
- Respond when server is down (e.g. check logs, restart)

#### 3. New entry actions:
- Examine and approve for newly submitted entries by non-Admin users (rare)
- Check if heatmap and meta data for new entry is correct (should success)

#### 4. HTTPS certificate renewal:
- Due on _Sep 22 2018_

Things that should _NOT_ need care (done automatically):

- Indexing of all entries [triggered by CRUD]
- Image (thumbnail) and JSON meta for entries [triggered by CRUD]
- Tools repository update download [GitHub Webhook]
- Data/config backup [weekly on Sun morning by cron]

Keep an eye on them when fail (you get admin email notice)


## Reference

>Cordero, P., *et al.* (**2012**)<br/>
>[An RNA Mapping DataBase for Curating RNA Structure Mapping Experiments.](http://bioinformatics.oxfordjournals.org/content/28/22/3006.long)<br/>
>*Bioinformatics* **28 (22)**: 3006-3008.

by [**t47**](http://t47.io/), *March 2016*.

