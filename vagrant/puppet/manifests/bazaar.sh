sudo easy_install pip
sudo pip install virtualenvwrapper

cd /srv
sudo mkdir publicdb
sudo chown vagrant.vagrant publicdb
sudo chmod g+rwx publicdb

sudo setfacl -m d:g::rwx publicdb

cd /srv/publicdb
# FIXME: We should use the shared code from the host machine,
#  not the GitHub repo, since it does not have the local changes. 
git clone https://github.com/HiSPARC/publicdb.git www
sudo chmod g+w www
sudo mkdir static
