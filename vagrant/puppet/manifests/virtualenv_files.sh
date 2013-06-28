cd /srv/publicdb
sudo virtualenv --distribute publicdb_env
source /srv/publicdb/publicdb_env/bin/activate

cd /srv/publicdb/publicdb_env/bin/hisparc
wget http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
wget http://rpms.famillecollet.com/enterprise/remi-release-5.rpm
sudo rpm -Uvh remi-release-5*.rpm epel-release-5*.rpm

sudo yum -y install atlas-devel

sudo yum -y install gcc-gfortran

