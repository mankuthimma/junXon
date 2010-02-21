#!/usr/bin/env python
#  Copyright (c) 2008 Corey Goldberg (corey@goldb.org)
#
#  Create RRD

import rrd

interval = 10
rrd_file = 'test.rrd'

my_rrd = rrd.RRD(rrd_file)
my_rrd.create_rrd(interval)
