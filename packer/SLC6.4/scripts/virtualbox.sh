# Installing the virtualbox guest additions
VBOX_VERSION=$(cat /home/hisparc/.vbox_version)
cd /tmp
mount -o loop /home/hisparc/VBoxGuestAdditions_$VBOX_VERSION.iso /mnt
sh /mnt/VBoxLinuxAdditions.run
umount /mnt
rm -rf /home/hisparc/VBoxGuestAdditions_*.iso

