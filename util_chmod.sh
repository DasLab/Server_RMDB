sudo usermod -a -G www-data ubuntu

sudo chgrp -R www-data *
sudo chown -R ubuntu *.py *.md *.txt repository media misc
sudo chown -R www-data data

sudo chmod 640 *.py* *.md *.txt
sudo chmod 640 repository/*.py* repository/helper/* repository/templatetags/*
sudo chmod 750 repository repository/templatetags
sudo chmod 640 media/css/* media/fonts/* media/html/* media/js/* media/images/*.*g* media/images/*.*p* media/images/docs/* media/rss/*
sudo chmod 750 media/css media/fonts media/html media/js media/images media/images/docs media/rss media
sudo chmod 700 media/images/src
sudo chmod 600 media/images/src/*
sudo chmod 640 media/admin/*.html media/admin/css/* media/admin/img/*.*g* media/admin/img/gis/* media/admin/img/admin/* media/admin/js/*.js media/admin/js/*.txt media/admin/js/*.py* media/admin/js/admin/* 
sudo chmod 750 media/admin media/admin/css media/admin/img media/admin/img/gis media/admin/img/admin media/admin/js media/admin/js/admin 

sudo chmod 640 misc/*.txt misc/V*.* misc/external/* misc/mapseeker/* misc/reeffit/*
sudo chmod 750 misc misc/external misc/mapseeker misc/reeffit
sudo chown www-data misc/mapseeker/mapseeker_user.csv misc/reeffit/reeffit_user.csv 

sudo chmod -R 640 data/
sudo chmod 750 data data/construct_img data/files data/thumbs
sudo chmod 750 data/construct_img/* data/files/*

sudo chgrp -R ubuntu *.sh
sudo chown -R ubuntu *.sh
sudo chmod -R 700 *.sh

