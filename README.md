# icmp-monitor

Create a ICMP monitor and take action on your device given the status of the monitor.

#Step 1

Copy files over to /mnt/flash on your Arista EOS device
 - monitor-ip.py
 - icmp-monitor.py

#Step 2

Configure the following event-handlers for each script. The first is to run on boot, the second exposes a new show command to the cli.

event-handler monitor-ip-address
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

event-handler icmp-monitor-show
   trigger on-boot
   action bash cp /mnt/flash/icmp-monitor.py /usr/lib/python2.7/site-packages/CliPlugin/icmp-monitor.py
   delay 300
   
#Kick off Manually

If device is already online follow these steps to kick off manually.

1. copy all files to /mnt/flash/
2. ensure root password is configured
  - aaa root secret <secret>
3. from cli prompt, type in keyword bash
4. su to root user, use root password
5. copy files
  - cp /mnt/flash/icmp-monitor.py /usr/lib/python2.7/site-packages/CliPlugin/icmp-monitor.py
6. kick off monitor script manually and set to run in background
  - /mnt/flash/monitor-ip.py -r 0.0.0.0/0 -n 10.1.1.2 -m 10.1.1.2 -s et1 &
7. logout
8. log back in and verify with show command: show icmp monitor and bash ps -ef | grep monitor-ip


