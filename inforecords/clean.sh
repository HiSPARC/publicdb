#!/bin/sh

echo "DROP DATABASE hisparc; CREATE DATABASE hisparc;" | ../django/hisparc/manage.py dbshell
../django/hisparc/manage.py syncdb
mysql -u hisparc_admin --password='Crapsih' hisparc < hisparc_initial_data.sql
