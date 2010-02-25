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

        _sql_ = "CREATE TABLE hosts (id INTEGER PRIMARY KEY, hostname TEXT, macaddress TEXT, ipaddress TEXT)"
        c.execute(_sql_)

        self.cx.commit()
        return True
        
    
    def addhost(self, macaddress=None, hostname=None, ipaddress=None, idnum=None):
        """ Add a host to be monitored """

        macaddress = macaddress.upper()
        hostname   = hostname.upper()
        # Remove if record pertaining to macaddress already exists
        self.remhost(macaddress)

        _sql_ = "INSERT INTO hosts (id, hostname, macaddress, ipaddress) VALUES (%d, '%s', '%s', '%s')" % (int(idnum), hostname, macaddress, ipaddress)
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

    def markhost(self, oid, ipaddress):
        target_out = Target('CONNMARK', '--set-mark '+str(oid))
        rule_out = Rule(
            source = ipaddress + "/32",
            jump = target_out)

        target_in = Target('CONNMARK', '--set-mark '+str(oid))
        rule_in = Rule(
            destination = ipaddress + "/32",
            jump = target_out)
            
        table = Table('mangle')
        try:
            table.append_rule('out_traffic', rule_out)
            table.append_rule('in_traffic', rule_in)
        except IptablesError, e:
            sys.stdout.write("Unknown error: %s" % e)
        return True

    def unmarkhost(self, oid, ipaddress):
        target_out = Target('CONNMARK', '--set-mark '+str(oid))
        rule_out = Rule(
            source = ipaddress + "/32",
            jump = target_out)

        target_in = Target('CONNMARK', '--set-mark '+str(oid))
        rule_in = Rule(
            destination = ipaddress + "/32",
            jump = target_out)

        table = Table('mangle')
        try:
            table.delete_rule('out_traffic', rule_out)
            table.delete_rule('in_traffic', rule_in)        
        except IptablesError, e:
            sys.stdout.write('Rule not found: %s' % e)            
        return True        

    def updreading(self):
        r = Readings()
        vals_in = r.getstats("in")
        vals_out = r.getstats("out")

        _sql_ = "SELECT id, hostname, macaddress, ipaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)

        for h in c:
            mac = h[2].upper().replace(":","")
            idnum = h[0]
            rrd_file = settings.rrdroot + mac + ".rrd"
            r = rrd.RRD(rrd_file)
            r.update(vals_in[idnum], vals_out[idnum])
        return True

    def gengraphs(self):
        
        _sql_ = "SELECT id, hostname, macaddress, ipaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        rrdpng = settings.rrdpng

        opts = {}
        for h in c:
            mac = h[2].upper().replace(":","")
            idnum = h[0]
            rrd_file = settings.rrdroot + mac + ".rrd"

            hostname = h[1]
            ipaddress = h[3]
            title = " report for "+hostname+"/"+ipaddress
            
            # Common for all below
            opts['rrdfile'] = rrd_file
            r = rrd.RRD(rrd_file)
            
            pngdir = rrdpng + str(idnum) + "/"
            if (not os.path.exists(pngdir)):
                os.mkdir(pngdir)
            
            # Daily
            opts['graphtype'] = "day"
            opts['title'] = "Usage " + title
            opts['filename'] = pngdir + "daily.png"
            r.graph(opts)

            # Weekly
#             opts['graphtype'] = "week"
#             opts['title'] = "Weekly" + title            
#             opts['filename'] = pngdir + "weekly.png"
#             r.graph(opts)
            
#             # Monthly
#             opts['graphtype'] = "month"
#             opts['title'] = "Monthly" + title            
#             opts['filename'] = pngdir + "monthly.png"
#             r.graph(opts)

#             # Yearly
#             opts['graphtype'] = "year"
#             opts['title'] = "Yearly" + title            
#             opts['filename'] = pngdir + "yearly.png"
#             r.graph(opts)
            
        return True

    def listhosts(self):
        _sql_ = "SELECT id, hostname, macaddress, ipaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        hosts = []
        for h in c:
            hosts.append(h)
        self.cx.commit()
        return hosts

    def flushall(self):
        _sql_ = "SELECT id, ipaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        hosts = []
        for h in c:
            xid = h[0]
            ipaddress = h[1]
            self.unmarkhost(xid, ipaddress)

            
    def markall(self):
        _sql_ = "SELECT id, ipaddress  FROM hosts ORDER BY id"
        c = self.cx.cursor()
        c.execute(_sql_)
        hosts = []
        for h in c:
            xid = h[0]
            ipaddress = h[1]
            self.markhost(xid, ipaddress)

if __name__ == "__main__":
    x = XRoad()
    x.gengraphs()
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



