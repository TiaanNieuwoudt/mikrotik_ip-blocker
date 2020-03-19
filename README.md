# mikrotik_ip-blocker

Usage: Run program with api.py, use scheduler function to change the amount of times between every IP_blocker run counter

Uses the routerOS_api pacakge to interface with routerOS devices' API
connects to router and searches log for regex filtered message, upon finding this message, the IP address is filtered via regex expression. 

IP is then compared to existing address list entries, if ip does not exists, its added with timeout.


Ip addresses gets added to sqlite database and simple IP address: date time mail of IP's blocked is sent via email once per day


Anyone is welcome to provide me with some kind of task that needs to be done on mikrotik, I'll be happy to give it a try.

NOTE: The MIkrotik firewall is supposed to block IP's added to the address list, and not the Python program itself
