##
## reports.py
## Author : <shashi@inf.in>
## Started on  Wed Mar 24 14:08:07 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA
##

import reporting
from models import Subscriber

class SubscriberReport(reporting.Report):
    model = Subscriber
    verbose_name = 'Subscriber Report'
    detail_list_display = [      
        'name', 
    ]

#     date_hierarchy = 'requested' 


reporting.register('subscriber', SubscriberReport) 
