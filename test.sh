cd django_publicdb
yes 'yes' | ./manage.py reset histograms && ./manage.py syncdb
cd ../examples
./django-cron.py
