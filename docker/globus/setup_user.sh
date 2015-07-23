#!/bin/bash
USER="grid"

useradd -d / $USER
echo "Added $USER user. Setting up myproxy."
sudo -u myproxy myproxy-admin-adduser -c $USER -l $USER
grid-mapfile-add-entry -dn $MYPROXY_SERVER_DN -ln $USER

