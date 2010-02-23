#!/usr/bin/env python
##
## junxond.py
## Author : <shashi@inf.in>
## Started on  Mon Feb 15 13:27:24 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA TECHNOLOGIES (MYSORE) PRIVATE LIMITED

import daemon, sys

# Pyro Server for libJunxon
from Pyro.errors import NamingError
import Pyro.core, Pyro.naming, Pyro.util

from libjunxon import Junxon

JUNXON_GROUP = ":Junxon"
JUNXON_NAME = JUNXON_GROUP+".Server"


class Junxond(Pyro.core.ObjBase, Junxon):
        def __init__(self):
                Pyro.core.ObjBase.__init__(self)
                Junxon.__init__(self)
                
# TODO: Load netfilter NAT rules for currently active subscriptions

def main():


        jx = Junxon()
        jx.init_active()

        # Daemonize PyroJunxon
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon()
	ns = Pyro.naming.NameServerLocator().getNS()
	daemon.useNameServer(ns)

	try:
		ns.createGroup(JUNXON_GROUP)
	except NamingError:
		pass
	try:
		ns.unregister(JUNXON_NAME)
	except NamingError:
		pass

	uri=daemon.connect(Junxond(),JUNXON_NAME)

	sys.stdout.write('Junxon Ready...')
	daemon.requestLoop()


# TODO: Move log file location to configuration
jxd = daemon.Daemon(
                stdin="/dev/null",
                stdout="/tmp/junxon.log",
                stderr="/tmp/junxon.log",
                pidfile="/var/run/junxon.pid",
                user="root"
                )


if __name__=='__main__':

        if jxd.service():
                main()
