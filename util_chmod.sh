sudo usermod -a -G www-data ubuntu

sudo chgrp -R www-data *
sudo chown -R ubuntu *.py *.md *.txt src media config dist .gitignore
sudo chown -R www-data backup data cache

find src -type f | sudo xargs chmod 640
find src -type d | sudo xargs chmod 750
find media -type f | sudo xargs chmod 640
find media -type d | sudo xargs chmod 750

find cache -type f | sudo xargs chmod 660
find cache -type d | sudo xargs chmod 770
find backup -type f | sudo xargs chmod 660
find backup -type d | sudo xargs chmod 770
find data -type f | sudo xargs chmod 660
find data -type d | sudo xargs chmod 770

find dist -type f | sudo xargs chmod 640
find dist -type d | sudo xargs chmod 750
find config -type f | sudo xargs chmod 640
find config -type d | sudo xargs chmod 750
sudo chown www-data config/cron.conf

sudo chown -R ubuntu:ubuntu *.sh .git
sudo chmod -R 700 *.sh
sudo chmod 640 robots.txt *.py*
sudo chown ubuntu:ubuntu *.md requirements.txt
sudo chmod 600 *.md requirements.txt .gitignore

find .git -type f | sudo xargs chmod 640
find .git -type d | sudo xargs chmod 750

sudo chown ubuntu:www-data ../yuicompressor.jar
sudo chmod 640 ../yuicompressor.jar
