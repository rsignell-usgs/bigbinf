#!/bin/bash
USER="grid"

useradd $USER
OUTPUT=`sudo -u myproxy myproxy-admin-adduser -c $USER -l $USER -n | tail -n 1`
grid-mapfile-add-entry -dn "$OUTPUT" -ln $USER
