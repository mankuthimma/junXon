#!/usr/bin/env python
#
#  rrd.py
#  Simple RRDTool wrapper
#  Copyright (c) 2008 Corey Goldberg (corey@goldb.org)
#
#  Download the Windows version of RRDTool from:
#    http://www.gknw.net/mirror/rrdtool/
# 
#  You may need these fonts if RRDTool throws an error when you graph:
#    http://dejavu.sourceforge.net/wiki/index.php/Main_Page


import os
import time
import sys


class RRD(object):
    def __init__(self, rrd_name, vertical_label='test'):     
        self.rrd_name = rrd_name
        self.vertical_label = vertical_label


    def create_rrd(self, interval):  
        interval                = 60  # 1 minute step (base interval with which data will be fed into the RRD)
        heartbeat               = 300  # 5 minute heartbeat for each data source
        ds1                     = ' DS:in:DERIVE:%s:0:12500000' % heartbeat # 2 data sources (in, and out)
        ds2                     = ' DS:out:DERIVE:%s:0:12500000' % heartbeat
        rra1                    = ' RRA:AVERAGE:0.5:1:576' # 2 days of 5 minute averages
        rra2                    = ' RRA:AVERAGE:0.5:6:672' # 2 weeks of 1/2 hour averages
        rra3                    = ' RRA:AVERAGE:0.5:24:732' # 2 months of 2 hour averages
        rra4                    = ' RRA:AVERAGE:0.5:144:1460' # 2 years of 12 hour averages

        cmd_create = ''.join((
            'rrdtool create ', self.rrd_name, ' --step ', str(interval),
            ds1, ds2,
            rra1, rra2, rra3, rra4,
            ))
        cmd = os.popen4(cmd_create)
        cmd_output = cmd[1].read()
        for fd in cmd: fd.close()
        if len(cmd_output) > 0:
            raise RRDException, 'Unable to create RRD: ' + cmd_output
  
  
    def update(self, *values):   
        values_args = ''.join([str(value) + ':' for value in values])[:-1]
        cmd_update = 'rrdtool update %s -t in:out N:%s' % (self.rrd_name, values_args)
        f = open("/tmp/upd.log","a+")
        f.write(cmd_update)
        f.close()
        cmd = os.popen4(cmd_update)
        cmd_output = cmd[1].read()
        for fd in cmd: fd.close()
        if len(cmd_output) > 0:
            raise RRDException, 'Unable to update RRD: ' + cmd_output
            
    def graph(self, vals):
        """
                Inputs:
        
                graphtype       = vals['graphtype'] (day, week, month, year)
                filename        = vals['filename'] (filename.png)
                title           = vals['title'] (Host: 122_user_name/192.168.1.17)
                dsfile          = vals['rrdfile'] (/path/to/rrdfile)
                
        """
        
        cur_date = time.strftime('%m/%d/%Y %H\:%M\:%S', time.localtime())

        graphtype       = vals['graphtype']
        filename        = vals['filename']
        title           = vals['title']
        dsfile          = vals['rrdfile']

        cmd_graph = ('rrdtool graph ' + filename,
                    ' --start=-1' + graphtype,
                    ' --title="' + title + '"',
                    ' --lazy',
                    ' --height=80',
                    ' --width=600',
                    ' --lower-limit=0',
                    ' --imgformat="PNG"',
                    ' --vertical-label=bytes/sec',
                    ' DEF:in="' + dsfile + ':in:AVERAGE"',
                    ' DEF:out="' + dsfile + ':out:AVERAGE"',
                    ' CDEF:out_neg=out,-1,*,',
                    ' AREA:in#32CD32:Incoming',
                    ' LINE1:in#336600',
                    ' GPRINT:in:MAX:"Max\\: %8.2lf %s"',
                    ' GPRINT:in:AVERAGE:"Avg\\: %8.2lf %S"',
                    ' GPRINT:in:LAST:"Current\\: %8.2lf %Sbytes/sec\\n"',
                    ' AREA:out_neg#4169E1:Outgoing',
                    ' LINE1:out_neg#0033CC',
                    ' GPRINT:out:MAX:"Max\\: %8.2lf %S"',
                    ' GPRINT:out:AVERAGE:"Avg\\: %8.2lf %S"',
                    ' GPRINT:out:LAST:"Current\\: %8.2lf %Sbytes/sec\\n"',
                    ' HRULE:0#000000',
                     )
        cmdline = ' '.join(cmd_graph)

        cmd = os.popen4(cmdline)
        for fd in cmd: fd.close()

            
class RRDException(Exception): pass
