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

import sys
import Pyro.naming
import Pyro.core
from Pyro.errors import PyroError,NamingError

from junxon import Junxon

group = ':junxon-service'   

Pyro.config.PYRO_PORT=Pyro.config.PYRO_PORT+1

# initialize the server and set the default namespace group
Pyro.core.initServer()
Pyro.config.PYRO_NS_DEFAULTGROUP=group

# locate the NS
print 'Searching Naming Service...'
daemon = Pyro.core.Daemon()
locator = Pyro.naming.NameServerLocator()
ns = locator.getNS()


# make sure our namespace group exists
try:
	ns.createGroup(group)
except NamingError:
	pass

daemon.useNameServer(ns)

# use Delegation approach for object implementation
obj1=Pyro.core.ObjBase()
obj1.delegateTo((Junxon))
daemon.connect(obj1,'Junxon')

# enter the service loop.
print 'Junxon ready!'
daemon.requestLoop()


