'''
Created on Jan 22, 2019

@author: deepashree.kurnad
'''

import ndb

class GCPRequest(ndb.Model):
    applicationName = ndb.StringProperty()
    projectCode = ndb.StringProperty()
    environment = ndb.StringProperty()
    requestOwner = ndb.StringProperty()
    risk = ndb.StringProperty()
    partner = ndb.StringProperty()
    services = ndb.StringProperty(repeated=True)
    status=ndb.StringProperty()
    approver=ndb.StringProperty()
    approverName=ndb.StringProperty()
    requester=ndb.StringProperty()
    requesterName=ndb.StringProperty()
    client = ndb.StringProperty()
    
class Creds(ndb.Model):
    access_token = ndb.StringProperty()
    userId = ndb.StringProperty()
    userName=ndb.StringProperty()
    
class BillingAccounts(ndb.Model):
    accountName = ndb.StringProperty()
    accountID = ndb.StringProperty()
