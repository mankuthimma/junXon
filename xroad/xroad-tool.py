#!/usr/bin/env python
##
## xroad-tool.py
## XRoad - Network Traffic Monitor
## Author : <shashi@inf.in>
## Started on  Sat Feb 20 11:45:51 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA TECHNOLOGIES (MYSORE) PRIVATE LIMITED
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##


import sys
from xroad import settings

sys.path.append(settings.xroadpath)
sys.path.append(settings.rrdlib)

import rrd

from optparse import OptionParser
from libxroad import XRoad

class XRoadTool:

    def __init__(self):
        self.x = XRoad()

    def addhost(self, macaddress, hostname=None):
        self.x.addhost(macaddress, hostname)
        print "Added host "+macaddress+" to XRoad Monitoring"
        return True

    def remhost(self, macaddress):
        self.x.remhost(macaddress)
        print "Removed host "+macaddress+" from XRoad Monitoring"        

    def initialize(self):
        print "Initializing XRoad ... ",
        self.x.initdb()
        print "done"
    
    def listhosts(self):
        hosts = self.x.listhosts()
        if (len(hosts) > 0):
            print "Hostname\t\tMAC Address" 
            for h in hosts:
                print h[1]+"\t\t"+h[2]
        else:
            print "No hosts being monitored"


def main():
    """ Tool to add and list hosts to XRoad for monitoring purposes """

    usage = "Usage: %prog [options]"

    parser = OptionParser(usage)
    parser.add_option("-a", "--add", help="Add host to XRoad", action="store_true", dest="add", default=False)
    parser.add_option("-d", "--delete", help="Remove host from XRoad", action="store_true", dest="rem", default=False)
    parser.add_option("-l", "--list", help="List hosts being monitored by XRoad", action="store_true", dest="list", default=False)    
    parser.add_option("--mac-address", action="store", dest="macaddress", help="Specify mac address")
    parser.add_option("--hostname", action="store", dest="hostname", help="Specify host name")
    parser.add_option("--init", help="Initialize XRoad. Destroys existing DB if any!", action="store_true", dest="init", default=False)    
    
    (options, args) = parser.parse_args()

    x = XRoadTool()

    if ((options.init is False) and ((options.add is False) and (options.rem is False) and (options.list is False))):
        parser.error("Either add, delete or list must be chosen")

    if ((options.add is True) and (not options.macaddress)):
        parser.error("MAC Address is missing")

    if ((options.rem is True) and (not options.macaddress)):
        parser.error("MAC Address is missing")

    if ((options.add is True) and (options.macaddress is not None)):
        if (options.hostname is not None):
            hostname = options.hostname
        else:
            hostname = "Host"

        x.addhost(options.macaddress, hostname)
    
    if ((options.rem is True) and (options.macaddress is not None)):
        x.remhost(options.macaddress)

    if (options.list is True):
        x.listhosts()

    if (options.init is True):
        x.initialize()


if __name__ == "__main__":
    main()
