# icmp-monitor

Create a ICMP monitor and take action on your device given the status of the monitor.

#Step 1

Copy files over to /mnt/flash on your Arista EOS device
 - monitor-ip.py
 - show-icmp-monitor.py
 - icmp-monitor-tasks.sh

#Step 2

Configure the following event-handlers for each script. The first is to run on boot, the second exposes a new show command to the cli.

Event-Handler for Monitor Script
![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/event-handler-script-2.png)

Help Menu
![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/help-menu.png)

Event-Handler for cli show commands
![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/event-handler-show-2.png)

Example of show command
![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/show-icmp-monitor.png)
   
#Kick off Manually

If device is already online follow these steps to kick off manually.

1. copy .sh & .py files to /mnt/flash/
2. ensure root password is configured
 - aaa root secret "INSERTYOURPASSWORD"
3. from cli prompt, type in keyword bash
4. su to root user, use root password
5. kick off monitor script manually and set to run in background
 - /mnt/flash/monitor-ip.py -r 0.0.0.0/0 -n 10.1.1.2 -m 10.1.1.2 -s et1 &
6. Wait for 10 seconds and issue the command to ensure script is running
 - ps -ef | grep monitor-ip
7. run the following command to expose the show command via the cli
 - /mnt/flash/icmp-monitor-tasks.sh
8. logout and end ssh session
9. ssh back in and verify with following show commands:
 - show icmp monitor
 - bash ps -ef | grep monitor-ip

