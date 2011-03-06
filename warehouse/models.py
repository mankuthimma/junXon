from django.db import models
from checkin.models import Subscriber

# class IPAddressPool(models.Model):
#     ipaddress_start = models.IPAddressField()
#     ipaddress_end   = models.IPAddressField()
#     ipaddress_gw    = models.IPAddressField()
#     ipaddress_mask  = models.IPAddressField()
#     ipaddress_brd   = models.IPAddressField(blank=True)

#     def __unicode__(self):
#         pool = self.ipaddress_start + '-' + self.ipaddress_end
#         return pool
