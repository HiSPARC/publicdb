#!/bin/sh

../django/hisparc/manage.py sqlreset inforecords | ../django/hisparc/manage.py dbshell
mysql -u hisparc_admin --password='Crapsih' hisparc < hisparc_initial_data.sql
