sudo rm -rf config/sys
sudo mkdir config/sys
sudo cp ../drive config/sys/
sudo cp -r ../.gdrive config/sys/gdrive
sudo cp ../.bash_profile config/sys/bash_profile
sudo cp -r ../.nano config/sys/nano
sudo cp ../.nanorc config/sys/nanorc
sudo cp ../.dircolors config/sys/dircolors
sudo cp -r ../.ssl_cert config/sys/ssl_cert
sudo cp ../.aws-credential config/sys/aws-credential

sudo cp -r ../django-filemanager config/sys/
sudo cp ../yuicompressor.jar config/sys/
sudo cp ../VARNA* config/sys/

sudo chown -R ubuntu:www-data config/sys
sudo chmod 750 $(find config/sys -type d)
sudo chmod 640 $(find config/sys -type f)

