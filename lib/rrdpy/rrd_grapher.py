#!/usr/bin/env python
#  Copyright (c) 2008 Corey Goldberg (corey@goldb.org)
#
#  Generate Graph From RRD

import rrd

interval = 10
rrd_file = 'test.rrd'

rrd = rrd.RRD(rrd_file)
rrd.graph(60)
