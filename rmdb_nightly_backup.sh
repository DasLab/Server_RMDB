fname=rmdb_`date +%m-%d-%Y`
localname=/home/daslab/rmdb_backup/
remotename=/home/tsuname/rmdb_backup/
mysqldump -u root -pbeckman rmdb | gzip > $localname$fname.sql.gz
echo "scp -r $localname$fname.sql.gz tsuname@ade.stanford.edu:$remotename$fname"
scp $localname$fname.sql.gz tsuname@ade.stanford.edu:$remotename
sudo tar zcf $localname${fname}_site.gz /home/daslab/rdat/rmdb
scp $localname${fname}_site.gz tsuname@ade.stanford.edu:$remotename
