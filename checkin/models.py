from django.db import models

TYPES = (
    ('SYSTEMS', 'Systems'), 
    ('STAFF', 'Staff'),
    ('VENDORS', 'Vendors'),
    ('GUESTS', 'Guests'),
    )

# class Subscription(models.Model):
#     subtype   = models.CharField(max_length=10, choices=TYPES)
#     name      = models.CharField(max_length=255)
#     bandwidth = models.IntegerField()

#     class Meta:
#         verbose_name = 

class Subscriber(models.Model):
#     sub         = models.ForeignKey(Subscription)
    name        = models.CharField(max_length=255)
    email       = models.EmailField()
    mobile      = models.CharField(max_length=12)
    remarks     = models.CharField(max_length=255)
    ipaddress   = models.IPAddressField()
    macaddress  = models.CharField(max_length=18)
    approvedby  = models.CharField(max_length=50) # ForeignKey to users?    
    recommended = models.CharField(max_length=50) # ForeignKey to users?




    
    
