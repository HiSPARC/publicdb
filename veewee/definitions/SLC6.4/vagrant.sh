# Vagrant specific
date > /etc/vagrant_box_build_time

# Add vagrant user
/usr/sbin/groupadd vagrant
/usr/sbin/useradd vagrant -g vagrant -G wheel
echo "vagrant"|passwd --stdin vagrant
echo "vagrant        ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers.d/vagrant
chmod 0440 /etc/sudoers.d/vagrant

# Installing vagrant keys
mkdir -pm 700 /home/vagrant/.ssh
wget --no-check-certificate 'https://raw.github.com/mitchellh/vagrant/master/keys/vagrant.pub' -O /home/vagrant/.ssh/authorized_keys
chmod 0600 /home/vagrant/.ssh/authorized_keys
chown -R vagrant /home/vagrant/.ssh

# Customize the message of the day
echo 'Welcome to your Vagrant-built virtual machine.' > /etc/motd


#
# The real server will have a hisparc user
#

# Add user hisparc with sudo access
/usr/sbin/adduser hisparc
echo "hisparc"|passwd --stdin hisparc
echo "hisparc        ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers

# Installing vagrant keys for hisparc user
mkdir /home/hisparc/.ssh
chmod 700 /home/hisparc/.ssh
cd /home/hisparc/.ssh
wget --no-check-certificate 'https://raw.github.com/mitchellh/vagrant/master/keys/vagrant.pub' -O authorized_keys
chown -R hisparc /home/hisparc/.ssh
