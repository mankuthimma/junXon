#!/usr/bin/python
##
## junxond.py
## Author : <shashi@inf.in>
## Started on  Mon Feb 15 13:27:24 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA
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


# Pyro Server for libJunxon
import Pyro.core
import Pyro.naming
from Pyro.errors import NamingError
from junxon import Junxon

class Junxond(Pyro.core.ObjBase, Junxon):
        def __init__(self):
                Pyro.core.ObjBase.__init__(self)

Pyro.core.initServer()

ns=Pyro.naming.NameServerLocator().getNS()

daemon=Pyro.core.Daemon()
daemon.useNameServer(ns)

try:
        ns.unregister(':junxon-service.Junxon')
        ns.createGroup(":junxon-service")
except NamingError:
        pass

uri=daemon.connect(Junxond(),":junxon-service.Junxon")

print "junxond... ready",
daemon.requestLoop()

