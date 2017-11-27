#!/usr/bin/env python

import json
import os
import BasicCli
import CliParser

'''
PLEASE CONFIGURE THE FOLLOWING event-monitor ON THE DEVICE
event-handler icmp-monitor-show
   trigger on-boot
   action bash cp /mnt/flash/show-icmp-monitor.py /usr/lib/python2.7/site-packages/CliPlugin/icmp-monitor.py
   delay 100
'''

token_icmp = CliParser.KeywordRule('icmp', helpdesc='Internet Control Message Protocol')
token_monitor = CliParser.KeywordRule('monitor', helpdesc='Show all monitor statuses')

def icmp_monitor_stat(mode):
    status = ''
    files = os.listdir('/mnt/flash/monitor_ip/')
    for fname in files:
        if 'monitor_state.' in fname:
            f = open('/mnt/flash/monitor_ip/%s' % fname, 'r')
            state = json.load(f)
            f.close()
        else:
            continue

        ''' check if process is actually running '''
        active = os.path.exists('/proc/%s' % state['pid'])

        ''' calculate delay '''
        delay = int(state['pings_per_cycle']) * int(state['ping_wait']) * int(state['fail_threshold'])

        status += '------------    show monitor %s   ------------ \n' % state['pid']
        status += 'Type of operation: icmp echo \n'
        status += 'Monitor IP Address: %s \n' % state['monitor_ip']
        status += 'Source Interface: %s \n' % state['source_int']
        status += 'ICMP Echo Timeout: %ss \n' % state['ping_wait']
        status += '  Delay before action: %s \n' % delay
        status += '\n'
        status += 'Tracking Object: \n'
        status += '  Route Type: %s \n' % state['route_type']
        status += '  Route: %s \n' % state['tracked_route']
        status += '  Route Next Hop: %s \n' % state['next_hop']
        status += '\n'
        status += 'Monitor Current State: \n'
        status += '  Process id: %s \n' % state['pid']
        status += '  Process Active: %s \n' % active
        status += '  Failed: %s \n' % state['failed']
        status += '  Counters: \n'
        status += '    Failure Counter: %s \n' % state['fail_counter']
        status += '    Success Counter: %s \n' % state['success_counter']
        status += '\n'

    return status


def do_show_icmp_monitor(mode):
    print icmp_monitor_stat(mode)

BasicCli.registerShowCommand(token_icmp, token_monitor, do_show_icmp_monitor)
