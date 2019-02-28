cd /tmp
mount -o loop /home/hisparc/VBoxGuestAdditions.iso /mnt
sh /mnt/VBoxLinuxAdditions.run
umount /mnt
rm -rf /home/hisparc/VBoxGuestAdditions.iso
