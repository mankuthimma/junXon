#!/usr/bin/env python
##
## xroad-daemon.py
## XRoad - Network Traffic Monitor
## Author : <shashi@inf.in>
## Started on  Sat Feb 20 15:34:29 2010 Shashishekhar S
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

import settings
import sys, time
import daemon

sys.path.append(settings.xroadpath)
sys.path.append(settings.rrdlib)

from xroad import XRoad

class XRoadD:
    
    def __init__(self):
        self.x = XRoad()

    def flush_current(self):
        self.x.flushall()

    def mark_hosts(self):
        self.x.markall()
        
    def updator(self):
        self.x.updreading()

xrd = daemon.Daemon(
                stdin="/dev/null",
                stdout=settings.logfile,
                stderr=settings.logfile,
                pidfile="/var/run/xroad.pid",
                user="root"
                )

if __name__ == "__main__":
    
    if xrd.service():
        x = XRoadD()
        x.flush_current()
        x.mark_hosts()
        while True:
            x.updator()
            time.sleep(10)
