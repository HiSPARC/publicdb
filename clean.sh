#!/bin/sh

echo "DROP DATABASE hisparc; CREATE DATABASE hisparc;" | mysql -u hisparc --password='Crapsih'
mysql -u hisparc --password='Crapsih' hisparc < hisparc.sql
