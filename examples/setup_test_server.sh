mkdir /tmp/datastore
ssh -N -f -L 2201:frome:22 davidf@login.nikhef.nl
sshfs -p 2201 davidf@localhost:/databases/frome /tmp/datastore

mkdir /tmp/mediaroot
ln -s $(pwd)/../django_publicdb/static /tmp/mediaroot/static
