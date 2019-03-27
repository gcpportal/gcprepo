'''
Created on Feb 14, 2019

@author: deepashree.kurnad
'''
from protorpc import messages

class RequestsPending(messages.Message):
    applicationName = messages.StringField(1)
    projectCode = messages.StringField(2)
    requestOwner = messages.StringField(3)