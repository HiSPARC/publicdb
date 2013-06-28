source /srv/publicdb/publicdb_env/bin/activate

cd /srv/publicdb/www/django_publicdb/
cp settings-develop.py settings.py

cp /vagrant/vagrant/puppet/modules/UWSGI.ini/uwsgi.ini /srv/publicdb/www/uwsgi.ini

sudo yum -y install supervisor
sudo /sbin/chkconfig --level 3 supervisord on

cd /srv/publicdb/www/django_publicdb/
sudo ./manage.py syncdb --noinput
sudo ./manage.py migrate
sudo ./manage.py collectstatic --noinput

