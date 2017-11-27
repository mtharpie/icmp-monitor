# icmp-monitor

Create a ICMP monitor and take action on your device given the status of the monitor.

# Step 1

Copy the following files to `/mnt/flash` on your Arista EOS device:
 - monitor-ip.py
 - show-icmp-monitor.py

# Step 2

Configure the following event-handlers for each script. The first is to run on boot, the second exposes a new `show` command to the CLI.

### Event-Handler for Monitor Script

![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/event-handler-script.png)

### Help Menu

![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/help-menu.png)

### Event-Handler for cli `show` commands
![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/event-handler-show.png)

### Example of show command

![alt text](https://github.com/mtharpie/icmp-monitor/blob/master/pics/show-icmp-monitor.png)

# Kick off Manually

If device is already online follow these steps to kick off manually.

1. copy `.py` files to `/mnt/flash/`
2. ensure root password is configured
  - `aaa root secret "INSERTYOURPASSWORD"`
3. from a CLI prompt, type in `bash`
4. Use `su` to become the root user, use root password
5. copy files
  - `cp /mnt/flash/icmp-monitor.py /usr/lib/python2.7/site-packages/CliPlugin/icmp-monitor.py`
6. kick off monitor script manually and set to run in background
  - `/mnt/flash/monitor-ip.py -r 0.0.0.0/0 -n 10.1.1.2 -m 10.1.1.2 -s et1 &`
7. `logout`
8. log back in and verify with show command: `show icmp monitor` and `bash ps -ef | grep monitor-ip`
