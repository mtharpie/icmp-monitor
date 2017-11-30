#!/usr/bin/env bash

cp /mnt/flash/show-icmp-monitor.py /usr/lib/python2.7/site-packages/CliPlugin/show-icmp-monitor.py
sleep 5

killall FastClid-server

rm /mnt/flash/monitor_ip/monitor_state*
