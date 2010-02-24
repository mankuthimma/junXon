##
## xroad.py
## XRoad - Network Traffic Monitor
## Author : <shashi@inf.in>
## Started on  Thu Feb 18 17:15:14 2010 Shashishekhar S
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

from xroad import settings
import sys, os.path
import sqlite

sys.path.append(settings.xroadpath)
sys.path.append(settings.rrdlib)

import rrd

from netfilter.rule import Match, Target, Rule
from netfilter.table import Table, IptablesError
from netfilter.stats import Readings

class XRoad:
    """ Base Class """

    def __init__(self):
        self.cx = self.dbasecx()
        pass

    def dbasecx(self):
        """ Return a SQLite DB Handle """
    
        dbpath = settings.db
        c = sqlite.connect(dbpath)
        return c

    def initdb(self):
        """ Drop table and recreate if needed """

        _sql_ = "DROP TABLE hosts;"
        c = self.cx.cursor()        
        try:
            c.execute(_sql_)
        except sqlite.Error, e:
            pass

        _sql_ = "CREATE TABLE hosts (id INTEGER PRIMARY KEY, hostname TEXT, macaddress TEXT)"
        c.execute(_sql_)

        self.cx.commit()
        return True
        
    
    def addhost(self, macaddress=None, hostname=None, ipaddress=None):
        """ Add a host to be monitored """

        macaddress = macaddress.upper()
        hostname   = hostname.upper()
        _sql_ = "INSERT INTO hosts (hostname, macaddress) VALUES ('"+hostname+"','"+macaddress+"')"
        c = self.cx.cursor()
        c.execute(_sql_)
        self.cx.commit()
        self.createrrd(macaddress)
        return True

    def createrrd(self, macaddress):
        mac_norm = macaddress.replace(":","")
        rrd_file = settings.rrdroot + mac_norm + ".rrd"
        if (not os.path.exists(rrd_file)):
            r = rrd.RRD(rrd_file, vertical_label='value')
            r.create_rrd(settings.rrdinterval)
        return True

    def remhost(self, macaddress=None):
        """ Remove host that is being monitored currently """

        macaddress = macaddress.upper()
        _sql_ = "DELETE FROM hosts WHERE macaddress='"+macaddress+"'"
        c = self.cx.cursor()
        c.execute(_sql_)
        self.cx.commit()
        return True

    def markhost(self, id, macaddress):
        # rule = Rule(jump=Target('LOG', '--log-prefix "ICMP accepted : " --log-level 4'))
        target = Target('CONNMARK', '--set-mark '+repr(id))
        rule = Rule(
            in_interface=settings.interface,
            matches = [Match('mac', '--mac-source '+macaddress)],
            jump = target)
            
        table = Table('mangle')
        table.append_rule('FORWARD', rule)
        return True

    def unmarkhost(self, id, macaddress):
        target = Target('CONNMARK', '--set-mark '+repr(id))
        rule = Rule(
            in_interface=settings.interface,
            matches = [Match('mac', '--mac-source '+macaddress)],
            jump = target)
            
        table = Table('mangle')
        try:
            table.delete_rule('FORWARD', rule)
        except IptablesError, e:
            sys.stdout.write('Rule unavailable' % e)            
        return True        

    def updreading(self):
        r = Readings()
        vals = r.getstats()
        for m in vals.keys():
            mac = m.upper().replace(":","")
            rrd_file = settings.rrdroot + mac + ".rrd"
            r = rrd.RRD(rrd_file)
            r.update(vals[m])
            self.gengraph(mac, mac)
        return True

    def gengraph(self, macaddress, legend="Host Traffic"):
        fname = macaddress.upper().replace(":","")
        rrd_file = settings.rrdroot + fname + ".rrd"
        png_file = settings.rrdpng + fname + ".png"
        r = rrd.RRD(rrd_file, vertical_label="Traffic")
        r.graph(10, png_file, legend)
        return True

    def listhosts(self):
        _sql_ = "SELECT id, hostname, macaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        hosts = []
        for h in c:
            hosts.append(h)
        self.cx.commit()
        return hosts

    def flushall(self):
        _sql_ = "SELECT id, hostname, macaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        hosts = []
        for h in c:
            # rule = Rule(jump=Target('LOG', '--log-prefix "ICMP accepted : " --log-level 4'))
            id = h[0]
            macaddress = h[2]
            self.unmarkhost(id, macaddress)

            
    def markall(self):
        _sql_ = "SELECT id, hostname, macaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        hosts = []
        for h in c:
            id = h[0]
            macaddress = h[2]
            self.markhost(id, macaddress)

if __name__ == "__main__":
    x = XRoad()
    #     x.initdb()
    #     x.addhost("woodlice","aa:bb:cc:dd:ee:ff")
    #     x.markhost(3, "aa:bb:cc:dd:ee:ff")
    #x.updreading()
    #     x.gengraph("aa:bb:cc:dd:ee:ff")
#     systems = {}
#     systems['caterpillar']  = '00:15:f2:bc:97:49'
#     systems['roadhog']      = '00:17:31:32:de:3f'
#     systems['cockatoo']     = '00:17:31:31:3f:94'
#     systems['balderdash']   = '00:17:31:31:3f:95'
#     systems['rhizopod']     = '00:17:31:31:3f:93'
#     systems['spitfire']     = '00:17:31:31:3f:83'
#     systems['eel']          = '00:16:6f:8a:96:b0'
#     j=1
#     for i in systems.keys():
#         #         x.markhost(j, systems[i])
#         x.gengraph(systems[i])
#         j+=1



