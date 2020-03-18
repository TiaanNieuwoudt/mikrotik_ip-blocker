# mikrotik_ip-blocker

Uses the routerOS_api pacakge to interface with routerOS devices' API
connects to router and searches log for regex filtered message, upon finding this message, the IP address is filtered via regex expression. 

IP is then compared to existing address list entries, if ip does not exists, its added with timeout.
