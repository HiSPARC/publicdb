source /srv/publicdb/publicdb_env/bin/activate

sudo yum -y install mysql-devel

sudo pip install uwsgi uwsgitop
sudo pip install mysql-python

sudo yum -y install sqlite-devel

sudo pip install pysqlite
