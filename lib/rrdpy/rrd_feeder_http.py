#!/usr/bin/env python
#  Copyright (c) 2008 Corey Goldberg (corey@goldb.org)
#
#  RRDTool HTTP Performance Meter (Data Feeder/Grapher)


import rrd
import time
import sys
import httplib


host = 'www.python.org'
path = '/'
use_ssl = False

interval = 10
rrd_file = 'test.rrd'
            
            
def main():            
    my_rrd = rrd.RRD(rrd_file, 'Response Time')
    while True:   
        start_time = time.clock()
        try: 
            send(host)
        except:
            print 'failed request'
        end_time = time.clock()
        raw_latency = (end_time - start_time)
        expire_time = (interval - raw_latency)
        latency = ('%.3f' % raw_latency)
        my_rrd.update(latency)
        my_rrd.graph(60)
        print latency
        if expire_time > 0:
            time.sleep(expire_time)
                

def send(host):
    if use_ssl:
        conn = httplib.HTTPSConnection(host)
    else:
        conn = httplib.HTTPConnection(host)
    try:
        conn.request('GET', path)
        conn.getresponse().read()
    except:
        raise
    finally:
        conn.close()
        
        
        
if __name__ == '__main__':
    main()
                