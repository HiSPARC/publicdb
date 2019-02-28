# Installing vagrant keys for hisparc user
mkdir /home/hisparc/.ssh
chmod 700 /home/hisparc/.ssh
cd /home/hisparc/.ssh
wget --no-check-certificate 'https://github.com/hashicorp/vagrant/raw/master/keys/vagrant.pub' -O authorized_keys
chown -R hisparc /home/hisparc/.ssh
