#!/bin/bash
cp -f /data/webserver/dnsmasq_web/dnsmasq.conf /etc/dnsmasq.conf
change=$(find /data/webserver/dnsmasq_web/ -name 'hosts.conf' -mmin -1)
if [ "x"$change == "x/data/webserver/dnsmasq_web/hosts.conf" ];then
    cp -f /data/webserver/dnsmasq_web/hosts.conf /etc/dnsmasq.d/hosts.conf
    cp -f /data/webserver/dnsmasq_web/dnsmasq.conf /etc/dnsmasq.conf
    /usr/bin/systemctl restart dnsmasq.service
fi

