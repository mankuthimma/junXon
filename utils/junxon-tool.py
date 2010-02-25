#!/usr/bin/env python
##
## junxon-tool.py
## Author : <shashi@inf.in>
## Started on  Mon Feb 22 19:07:16 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA TECHNOLOGIES (MYSORE) PRIVATE LIMITED
##

junxonpath = ("/opt/","/opt/junxon","/opt/junxon/lib","/opt/junxon/xroad")          # HACK-ALERT!!! Move this to config - shashi
import sys
sys.path.extend(junxonpath)

from optparse import OptionParser
from libjunxon import Junxon
from libxroad import XRoad

from junxon.checkin.models import Subscriber

class JunxonUtil:

    def __init__(self, ipaddress, macaddress):
        self.j = Junxon()
        self.x = XRoad()
        self.ipaddress = ipaddress
        self.macaddress = macaddress

    def disconnect(self):
        self.j.disable_subscription(self.ipaddress, self.macaddress)
        self.j.remove_dhcp_record_by_mac(self.macaddress)
        
        sub = Subscriber.objects.filter(macaddress=self.macaddress, ipaddress=self.ipaddress, active=True)
        for s in sub:
            self.x.remhost(self.ipaddress, s.id) # Stop host from being monitored
            s.active=False
            s.save()
        return True
    

def main():
    """ Tool to disconnect active hosts """

    usage = "Usage: %prog [options]"

    parser = OptionParser(usage)
    parser.add_option("--mac-address", action="store", dest="macaddress", help="Specify mac address")
    parser.add_option("--ipaddress", action="store", dest="ipaddress", help="Specify ip address")

    (options, args) = parser.parse_args()

    if ((options.ipaddress is None) or (options.macaddress is None)):
        parser.error("Specify both mac address and ipaddress")
    else:
        j = JunxonUtil(options.ipaddress, options.macaddress)
        j.disconnect()

if __name__ == "__main__":
    main()


