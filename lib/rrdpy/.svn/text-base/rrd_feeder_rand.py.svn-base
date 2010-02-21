#!/usr/bin/env python
#  Copyright (c) 2008 Corey Goldberg (corey@goldb.org)
#
#  RRDTool Random Number Data Feeder/Grapher


import rrd
import random
import time


interval = 10
rrd_file = 'test.rrd'
           
my_rrd = rrd.RRD(rrd_file)

while True:
    rand = random.randint(1, 100)
    my_rrd.update(rand)
    my_rrd.graph(60)
    time.sleep(interval)
    

