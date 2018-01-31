#!/bin/bash
LAST_KERNEL=$(rpm -q --last kernel | perl -pe 's/^kernel-(\S+).*/$1/' | head -1)
CURRENT_KERNEL=$(uname -r)

test $LAST_KERNEL = $CURRENT_KERNEL && exit `false` || exit `true`
