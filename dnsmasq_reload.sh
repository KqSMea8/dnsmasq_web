#!/bin/bash
find /data/webserver/dnsmasq_web/ -name 'hosts' -mmin -1 -exec /usr/bin/systemctl restart dnsmasq.service {} \;
