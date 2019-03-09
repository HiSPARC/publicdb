#!/bin/bash
# TK mar2019
# The current CentOS kernel fails to boot on our hardware. CT patched grub to
#  boot an old one (3.10.0-514.el7.x86_64). As a result this scripts always
#  flags a reboot, because a newer kernel is availabe. This is a hack to
#  prevent rebooting our servers at every provisioning run.
#  This extracts the menuentry lines from the GRUB config.
#LAST_KERNEL=$(rpm -q --last kernel | perl -pe 's/^kernel-(\S+).*/$1/' | head -1)
LAST_KERNEL=$(grep ^menuentry /etc/grub2.cfg |  head -1 | awk -F"[()]" '{print $2}')
CURRENT_KERNEL=$(uname -r)

test $LAST_KERNEL = $CURRENT_KERNEL && exit `false` || exit `true`
