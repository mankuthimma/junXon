##
## settings.py
## XRoad - Network Traffic Monitor
## Author : <shashi@inf.in>
## Started on  Thu Feb 18 16:32:59 2010 Shashishekhar S
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

_version_ = 0.01

xroadpath       = "/opt/junxon/xroad"
junxonpath      = "/opt/junxon"
db              = junxonpath + "/cache/hosts.db"
interface       = "eth0"
rrdlib          = junxonpath + "/lib/rrdpy/"
rrdroot         = junxonpath + "/cache/flowdata/"
rrdpng          = junxonpath + "/cache/png/"
rrdinterval     = 60
logfile         = junxonpath "/log/xroad.log"

