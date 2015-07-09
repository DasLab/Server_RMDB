sudo gunzip < backup/backup_mysql.gz | mysql -u root -pbeckman rmdb
sudo tar zvxf backup/backup_data.tgz

sudo rm -rf data/files
sudo rm -rf data/thumbs
sudo rm -rf data/construct_img

mv backup/data_backup/files/ data/files
mv backup/data_backup/thumbs/ data/thumbs
mv backup/data_backup/construct_img/ data/construct_img

sudo rm -rf backup/data_backup
sudo ./util_chmod.sh

sudo apache2ctl restart
