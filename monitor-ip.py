#!/usr/bin/env python

'''
The following event handler needs to be configured. 

event-handler monitor-ip-address-10-1-1-2
   trigger on-boot
   action bash /mnt/flash/monitor-ip.py -r 0.0.0.0/0 -n 10.1.1.2 -m 10.1.1.2 -s et1
   delay 300

Help Menu is below:
Monitor IP Command Line Parser

optional arguments:
  -h, --help  show this help message and exit
  -r R        specify route in CIDR format: 192.168.0.0/24
  -n N        specify next-hop for route, IPv4 accepted
  -m M        specify ip to monitor, IPv4 accepted
  -s S        specify source-int for icmp echo, must be linux name; ie et1,
              vlan10, lo0
'''

import subprocess
import sys
import json
import argparse
import syslog
import traceback
import datetime
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description='Monitor IP Command Line Parser')
    parser.add_argument('-r', required=True,
                        help='specify route in CIDR format: 192.168.0.0/24')
    parser.add_argument('-n', required=True,
                        help='specify next-hop for route, IPv4 accepted')
    parser.add_argument('-m', required=True,
                        help='specify ip to monitor, IPv4 accepted')
    parser.add_argument('-s', required=True,
                        help='specify source-int for icmp echo, must be linux name; ie et1, vlan10, lo0')

    values = parser.parse_args()
    return (values.r, values.n, values.m, values.s)


def sendCmds(commands):
    ''' function to take a list of of commands and issue to command line '''
    cli_cmd = subprocess.Popen( commands, stdout= subprocess.PIPE, stderr= subprocess.PIPE )
    stdout, stderr = cli_cmd.communicate()
    return (stdout, stderr)


def is_interface_connected():
    ''' function to take action '''
    global source_int, pid

    show_cmds = ['FastCli', '-p15', '-c', 'show interface %s status' % source_int]

    stdout, stderr = sendCmds(failover_cmds)
    if 'Invalid input' in stdout:
        syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s Error grabbing interface status: interface %s ' % (pid, source_int) )
        sys.exit(1)
    else:
        status = json.loads(stdout)
        int_name = status['interfaceStatuses'].keys()[0]
        if status['interfaceStatuses'][int_name]['linkStatus'] == 'connected':
            return True
        else:
            return False


def action(failed=True):
    ''' function to take action '''
    global tracked_route, next_hop, route_type, pid

    failover_cmds = ['FastCli', '-p15', '-c', 'configure \n no ip route %s %s' % (tracked_route, next_hop)]
    failback_cmds = ['FastCli', '-p15', '-c', 'configure \n ip route %s %s' % (tracked_route, next_hop)]

    if failed:
        stdout, stderr = sendCmds(failover_cmds)
        if 'Invalid input' in stdout:
            syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s Error pulling route-type: %s route: %s next-hop: %s' % (pid, route_type, tracked_route, next_hop) )
            sys.exit(1)
        else:
            syslog.syslog('%%MONITOR_IP-5-INFO: pid: %s monitor has route change for %s, route removed' % (pid, tracked_route) )
    elif not failed:
        stdout, stderr = sendCmds(failback_cmds)
        if 'Invalid input' in stdout:
            syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s Error configuring route-type: %s route: %s next-hop: %s' % (pid, route_type, tracked_route, next_hop) )
            sys.exit(1)
        else:
            syslog.syslog('%%MONITOR_IP-5-INFO: pid %s monitor has completed route change for %s, route added' % (pid, tracked_route) )

    return


def write_state():
    ''' function to write script state to file in order to view in cli '''
    global route_type, failed, success_counter, fail_counter, fail_threshold
    global tracked_route, next_hop, monitor_ip, source_int, pid

    d = { 'route_type': route_type, 'failed': failed, 'success_counter': success_counter,
          'fail_counter': fail_counter, 'fail_threshold': fail_threshold, 'pid': pid,
          'tracked_route': tracked_route, 'next_hop': next_hop, 'monitor_ip': monitor_ip,
          'source_int': source_int, 'pings_per_cycle': pings_per_cycle, 'ping_wait': ping_wait }

    if not os.path.exists('/mnt/flash/monitor_ip/'):
        os.mkdir('/mnt/flash/monitor_ip/')

    f1_name = '/mnt/flash/monitor_ip/monitor_state.%s' % pid

    f1 = open(f1_name, 'w')
    json.dump(d, f1)
    f1.close()

    return


def monitor():
    ''' monitor ip and fail when condition hits '''
    global pings_per_cycle, ping_wait, source_int, monitor_ip, loss_threshold
    global fail_counter, success_counter, failed, fail_threshold

    #print 'Interface connected = %s' % str(is_interface_connected())

    #if not is_interface_connected():
    #    if failed:
    #        return
    #    else:
    #        failed = True
    #        syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s interface %s connected check failed, starting failover task' % (pid, source_int) )
    #        action(failed)
    #        return

    ping_cmds = ['ping', '-c', str(pings_per_cycle), '-i', str(ping_wait), '-I', source_int, monitor_ip]

    stdout, stderr = sendCmds(ping_cmds)
    if stderr:
        syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s stderr %s: during ping' % (pid, stderr) )
        sys.exit(1)
    else:
        results = stdout.splitlines()[-2]
        if 'errors' in results:
            loss_percentage = results.split(',')[3].replace('% packet loss','').strip()
        else:
            loss_percentage = results.split(',')[2].replace('% packet loss','').strip()
            
        loss = float(loss_percentage)
        if loss >= loss_threshold:
            fail_counter += 1
            success_counter = 0

            if failed:
                pass
            elif fail_counter >= fail_threshold:
                failed = True
                syslog.syslog('%%MONITOR_IP-4-WARN: pid: %s threshold reached starting failover task' % pid )
                action(failed)
        else:
            success_counter += 1
            if failed and (success_counter >= fail_threshold):
                failed = False
                fail_counter = 0
                syslog.syslog('%%MONITOR_IP-5-INFO: pid: %s reachability stable starting failback task' % pid)
                action(failed)

        write_state()

        if success_counter > 1000000:
            old_counter = success_counter
            success_counter = 0
            syslog.syslog('%%MONITOR_IP-5-INFO: pid: %s resetting counter was %s now %s' % (pid, old_counter, success_counter) )

    return

if __name__ == '__main__':
    ''' GLOBAL VARS '''
    route_type = 'static'
    failed = False
    success_counter = 0
    fail_counter = 0
    fail_threshold = 3
    loss_threshold = 50.00
    pings_per_cycle = 5
    ping_wait = 2

    try:
        ''' Open syslog for script '''
        syslog.openlog('MONITOR_IP', 0, syslog.LOG_LOCAL4)

        ''' grab process id for storage '''
        pid = os.getpid()

        (tracked_route, next_hop, monitor_ip, source_int) = parse_arguments()
        while True:
            monitor()

    except:
        t, v, tb = sys.exc_info()
        date_str = str(datetime.datetime.now())
        f = open('/mnt/flash/monitor_ip/monitor_ip.traceback', 'ab')
        f.write('************** %s Process ID: %s **************\n' % (date_str, pid) )
        f.write('Type = %s \n' % t)
        f.write('Value = %s \n' % v)
        extract_tb = traceback.extract_tb(tb)
        l = traceback.format_list(extract_tb)
        for item in l:
           f.write(item)
        f.close()

        ''' remove monitor state file from /mnt/flash/montior_ip/ '''
        try:
            os.remove('/mnt/flash/monitor_ip/monitor_state.%s' % pid)
        except:
            pass
        syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s exception caught see /mnt/flash/monitor_ip/monitor_ip.traceback' % pid )
        syslog.syslog('%%MONITOR_IP-3-ERROR: pid: %s exiting program monitor_ip' % pid )


