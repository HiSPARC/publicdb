cd /etc/httpd/conf.d/
sudo cp /vagrant/vagrant/puppet/modules/apache/manifests/hisparc.conf /etc/httpd/conf.d/hisparc.conf
sudo chown vagrant hisparc.conf
sudo chmod g+w hisparc.conf
