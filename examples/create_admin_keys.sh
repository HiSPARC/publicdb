#!/bin/sh

cd $1
. easy_rsa/vars-admin
easy_rsa/build-key $2
