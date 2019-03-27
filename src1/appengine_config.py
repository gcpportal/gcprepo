'''
Created on Feb 4, 2019

@author: deepashree.kurnad
'''
from google.appengine.ext import vendor
from google.appengine.api import urlfetch

vendor.add('lib')
urlfetch.set_default_fetch_deadline(60)