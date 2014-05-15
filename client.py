#!/usr/bin/python

import urllib2
import urllib

SERVER='http://localhost:5000'
class clientApi:

	def do_get(self,restApi):
		try:
			endpoint=SERVER+restApi
			response = urllib2.urlopen(endpoint).read()
		except Exception as e:
			return ({"STATUS":"Failed","MSG":e})
		return response;

#	def execute_process(self,command):
	
	
#	def get_command_action(self,command):
	
	
	
		
api=clientApi()
restApi="/statuscodes/"
print api.do_get(restApi)

hostname="localhost"
restApi="/PendingActions/%s"%(hostname)
print restApi

restApi="/GetStatus/%s"%(event_id)

restApi="/UpdateLog/%s",%(event_id)


#api.getPendingActions();