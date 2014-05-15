#!/usr/bin/python

import time
import zmq
from clientutils import clientutils;
import thread
import pdb;

c=clientutils();
context = zmq.Context()
socket = context.socket(zmq.SUB)

port=43434
server="localhost"
topicfilter = "Topic:127.0.0.1"

c.log_info( "Collecting checks to run server:%s port:%s topic:%s"%(server,port,topicfilter))
socket.connect("tcp://%s:%s" % (server,port))
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
c.log_info("Connected")


def run_check(event):
	#thread.start_new_thread(c.exec_checkscript,(event['msg'],event['timeout'],event['eventid']))
	c.log_info("Executing check script for msg:%s timeout:%s eventid:%s"%(event['msg'],event['timeout'],event['eventid']))
	c.exec_checkscript(event['msg'],event['timeout'],event['eventid'])




while True:
	messagedata = socket.recv()
	c.log_debug(messagedata)
	onlymsg=messagedata.replace("%s "%(topicfilter),"")
	c.log_debug("recvd--> %s"%(messagedata))
	c.log_info("Cleaned--> %s"%(onlymsg))
	obj=c.parse_message(onlymsg);
	if obj is not False:
		run_check(obj)
	else:
		c.log_error( "Unable to find exec script for %s "%(onlymsg))


#subscriber.close()
#context.term()


