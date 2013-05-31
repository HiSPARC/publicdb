#!/usr/bin/python
""" Reload nagios if necessary

    This script checks for the existence of the nagios restart flag,
    placed by the XML-RPC server when it is informed by the inforecords
    app running on data.hisparc.nl.  If that flag exists, it will load the
    nagios configuration from a url and checks it against a hash.  If the
    nagios configuration is indeed updated, it will write the new config,
    update the hash and restart nagios.

    This script tries to really make sure that nagios will always reload
    on an update.  If something goes wrong before succesful reloading, the
    hash and the flag are not updated and cleared, so that on next
    execution, this script will try to reload nagios again.

    This script is intended to be run as a cron job on the nagios server.

"""
import os
import urllib2
import hashlib
import subprocess

FLAG = '/tmp/flag_nagios_reload'
HASH = '/tmp/hash_nagios'
NAGIOS_CFG = '/usr/local/nagios/etc/objects/hisparc.cfg'
CFG_URL = 'http://data.hisparc.nl/config/nagios'


def reload_nagios():
    """Load nagios config and reload nagios, if necessary"""

    nagios_cfg = urllib2.urlopen(CFG_URL).read()
    new_hash = hashlib.sha1(nagios_cfg).hexdigest()

    try:
        with open(HASH, 'r') as file:
            old_hash = file.readline()
    except IOError:
        old_hash = None

    if new_hash == old_hash:
        return
    else:
        with open(NAGIOS_CFG, 'w') as file:
            file.write(nagios_cfg)

        subprocess.check_call(['/sbin/service', 'nagios', 'reload'])

        with open(HASH, 'w') as file:
            file.write(new_hash)


if __name__ == '__main__':
    if os.path.exists(FLAG):
        reload_nagios()
        os.remove(FLAG)
