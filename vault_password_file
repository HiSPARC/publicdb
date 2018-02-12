#!/usr/bin/env bash
#
# Vault password is not required for dev VMs, so just echo
#  a dummy value if the vault password is missing.
#
VAULT=~/.hisparc_vault
if [ -f "$VAULT" ]; then
	cat $VAULT
else
	echo "This is not the vault password!"
fi
