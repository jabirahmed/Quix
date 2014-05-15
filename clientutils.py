#!/usr/bin/python

import os.path;
import sys
import ConfigParser
from subprocess import Popen, PIPE
import subprocess
import datetime
import time
import pdb
import json
import logging
import urllib2



logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

class clientutils(object):
	config = ConfigParser.RawConfigParser()
	FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
	logging.basicConfig(format=FORMAT)

	def __init__(self):
		self.load_config()

	def log_info(self,msg):
		logging.info(msg)
		

	def log_error(self,msg):
		logging.error(msg)
		

	def log_warn(self,msg):
		logging.warnning(msg)
	
	def log_debug(self,msg)	:
		logging.debug(msg)


	def load_config(self):
		path="config/quix.conf"
		exists = os.path.isfile(path)
		if not exists:
			self.log_info( "Failed to load config [%s]"%(path))
			sys.exit(100)
		self.log_info( "Loading Config [%s]"%(path))
		self.config.read(path)
		self.log_info(  "Loaded config")

	def get_checkscript(self,check_name):
		try:
			self.log_info(  "getting config for %s"%(check_name))
			return self.config.get("quix",check_name)
		except:
			print "unexpected error: %s",sys.exc_info()[0]
			self.log_error(  "unable to get_checkscript")
			return False


	def send_response_to_server(self,status,msg,event_id):
		return_msg={};
		return_msg['status_code']=status
		return_msg['msg']=msg
		url="http://localhost:5000/updateCheckStatus/%s"%(event_id);
		request=urllib2.Request(url)
		request.add_data(json.dumps(return_msg))
		self.log_info(["sending data to server ",json.dumps(return_msg)])
		r = urllib2.urlopen(request)


#
#status code reference
#1	CHECK_SCHEDULED
#2	CHECK_RUNNING
#3	CHECK_SUCCESSFULL
#4	CHECK_FAILED
#5	CHECK_RERUN



	def exec_checkscript(self,check_name,timeout=60,event_id=False):
		script=self.get_checkscript(check_name)
		self.log_info(  "Script name %s"%(script))
		self.log_info( "event id %s"%(event_id))
		if  False:
			msg =  "Failed to check %s, could not find the script to run"%(check_name)
			self.send_response_to_server(4,msg,event_id)
			self.log_error(msg)
			return False
		try:
			self.log_info("check:%s script %s "%(check_name,script));
			pipe = subprocess.Popen([script],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			pid = pipe.pid
			stdout, stderr = pipe.communicate()
			rcode= pipe.returncode
			self.log_info([ stdout,rcode])
			msg = "pid:%s stdout:%s stderr:%s"%(pid,stdout,stderr)
			self.log_info(msg)
			self.send_response_to_server(3,msg,event_id)
		except:
			print "unable to exec_checkscript Unexpected error:%s", sys.exc_info()
			self.send_response_to_server(4,'Failed to run check',event_id)
			return False

	def parse_message(self,msg):
            msgobj={};
            self.log_error( [ "parsing ",msg])
            try:
                msgobj=json.loads(msg);
                self.log_info( msgobj);
                return msgobj
            except:
                self.log_error(["Unexpected error:", sys.exc_info()])
                self.log_error( "Unable to parse_message")
                return False



