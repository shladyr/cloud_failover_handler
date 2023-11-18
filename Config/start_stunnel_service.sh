#!/bin/bash

source /opt/application/tmp/ext_cloud.env
echo "EXT_CLOUD env variable:" $EXT_CLOUD

if grep -q EXT_CLOUD /opt/application/tmp/ext_cloud.env; then
    sed -i "/^connect/c\connect = $EXT_CLOUD:443" /opt/stunnel/etc/stunnel.conf
    sed -i "/^checkHost/c\checkHost = $EXT_CLOUD" /opt/stunnel/etc/stunnel.conf
    exec stunnel /opt/stunnel/etc/stunnel.conf
else
  exit 5;
fi
