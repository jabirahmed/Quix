#!/usr/bin/python

from flask import Flask,request,jsonify,url_for,redirect,render_template,Response,send_from_directory
from database import Base,init_db,db_session
from models import *
from random import random
from utils import *
import json
import sys
import time
import pdb
import os

init_db()        

app = Flask(__name__,static_url_path='')

utilObj=Utils(app)
utilObj.start_zmq() 

def root_dir(): # pragma: no cover
	rootdir=os.path.abspath(os.path.dirname(__file__));
	utilObj.log_info("root dir %s"%(rootdir))
	return rootdir


def get_file(filename): # pragma: no cover
	try:	
		src = os.path.join(root_dir(), filename)
		utilObj.log_info("Reading file %s"%(src))
		return open(src).read()
	except IOError as exc:
		return str(exc)

@app.route("/test/")
def test():
	utilObj.log_info("Sending test msg")
	utilObj.send_zmq_msg("test","test")
	return "OK"

@app.route("/statuscodes/")
def statuscodes():
	result=list(utilObj.getStatusCodes())
	utilObj.log_info("Getting status codes")
	dict={};
	for a in result:
		dict[a.status_id]=a.status
	utilObj.log_info(json.dumps(dict))	
	return json.dumps(dict);

@app.route("/a/")
def hello():
	#returnObj=array();
	returnObj={}
	returnObj['status']=False
   	return json.dumps(returnObj)

@app.route("/updateCheckStatus/<eventid>",methods=['POST'])
def updateCheckStatus(eventid):
	msg=json.loads(request.stream.read());
	utilObj.log_info("updating check_status for %s"%(eventid))
	utilObj.log_info( utilObj.recordExecLog(eventid,msg['status_code'],msg['msg']))
	utilObj.updateStatus(eventid,msg['status_code'])
	return "OK"


@app.route("/triggerCheck/<hostname>/<check>",methods=['GET'])
def triggerCheck(hostname,check):
	returnObj={}
	utilObj.log_info("Triggering a check for %s on %s"%(check,hostname))
	try:	
		cObj=checkEvent()
		eventid=utilObj.getEventId(check)
		timeout=utilObj.getEventTimeout(eventid)

		if eventid==False or eventid is None:
			returnObj['status']=False
			returnObj['message']="The event %s is not defined"%(check)
			utilObj.log_info(returnObj['message'])
			return json.dumps(returnObj)

		src_ip = request.remote_addr
		target_ip = utilObj.getHostIp(hostname)

		if utilObj.getHostId(src_ip) ==False or utilObj.getHostId(target_ip)==False:

			utilObj.registerHost(hostname,target_ip);
			hostnameStr = utilObj.getHostName(src_ip);
			if hostnameStr == False:
				hostnameStr=src_ip
			utilObj.registerHost(hostnameStr,src_ip);
			utilObj.registerHost(hostname,target_ip);
			
			returnObj['status']=False
			returnObj['message']='''Either src_ip or target_ip is not registered
			please work with the admin to have it approved'''
			utilObj.log_info(returnObj['message'])
			return json.dumps(returnObj)
		
		if target_ip == False:
			returnObj['status']=False
			return json.dumps(returnObj)

		status = 1 # CHECK_SCHEDULED
		
		lastCheck = utilObj.getLastEventExecTime(eventid,utilObj.getHostId(target_ip))
		print datetime.datetime.utcnow() - datetime.timedelta(0,600),' - ',lastCheck

		if lastCheck is None or lastCheck == False or   (datetime.datetime.utcnow() - datetime.timedelta(0,600) > lastCheck) : # never been cheked before or checked in last 10 minutes
			# add to check Queue
			cObj.event_id = eventid;
			cObj.checkevent_id=utilObj.generateUniqId();
			cObj.src_hostid = utilObj.getHostId(src_ip)
			cObj.dest2_hostid = utilObj.getHostId(target_ip)
			cObj.status=status;
			
			db_session.add(cObj)
			db_session.commit()

			returnObj['status']=True
			returnObj['id']=cObj.checkevent_id
			utilObj.log_info("the check has been scheduled with %s"%(returnObj['id']))
			checkObj={};
			checkObj['msg']=check
			checkObj['eventid']=cObj.checkevent_id
			checkObj['timeout']=timeout
			utilObj.log_info("Sending event to client via zmq");
			utilObj.send_zmq_msg(target_ip,json.dumps(checkObj));
			utilObj.log_info("sent event to client via zmq");
			return json.dumps(returnObj)
		else:
			returnObj['status']=False
	 		returnObj['refid']= utilObj.getLastEventExecId(eventid,utilObj.getHostId(target_ip))
			returnObj['message']='same check ran the server less than 10 minutes ago'
			utilObj.log_info(returnObj['message'])
			return json.dumps(returnObj)
	except:
		returnObj['status']=False
		returnObj['message']="Something went terribly wrong. [%s]"%(sys.exc_info())
		print "Unexpected error:", sys.exc_info()
		utilObj.log_error(returnObj['message'])
		return json.dumps(returnObj)
		
@app.route('/shutdown', methods=['GET'])
def shutdown():
    utilObj.stop_zmq()
    func = request.environ.get('werkzeug.server.shutdown')
    utilObj.log_info("Shutting down the server")
    if func is None:
    	tilObj.log_error("Shutting down the server")
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    utilObj.log_info("Shutting down the server")
    return 'Server shutting down...'

# For Static Files
@app.route('/static/<path:path>')
@app.route('/static/')
@app.route('/')
def serve_static(path=None):
	print path
	if path is None:

		path="index.html"
	utilObj.log_info("returning %s"%(path))
	return send_from_directory('static',path)

@app.route('/testq/<path:path>')
def testq(path):
	return path


@app.route('/hl/')
def hl():
	hosts = utilObj.getHosts()
	return render_template("hostslist.html", title = 'List of hosts',hl=hosts)

@app.route('/sc/')
def sc():
	scodes = utilObj.getStatusCodes();
	return render_template("statuscode.html", title = 'Status Codes',sc=scodes)
@app.route('/el/')
def el():
	elist = utilObj.getEvents();
	return render_template("eventlist.html", title = 'Events',el=elist)

@app.route('/cfg/')
def cfg():
	str=utilObj.readConfigTxt()
	if str is False:
		str= "Could not read config"
	
	return render_template("configlist.html", title = 'Configuration',config=str)


@app.route('/listChecks/<status>')
@app.route('/listChecks/')
def ac(status=None):
	title=status
	if title is None: title="ALL_CHECKS"
	utilObj.log_info("getting checks for  %s"%(title))
	ac=utilObj.getChecks(status)
	for a in ac:
		print a['event_id']
	return render_template("activechecks.html", title = title,active_checks=ac)

@app.route('/eventLog/<eventid>')
@app.route('/eventLog/')
def eventLog(eventid=None):
	
	if eventid is None: 
		return "Need an event id"

	utilObj.log_info("getting log for eventid  %s"%(eventid))
	records=utilObj.getEventLog(eventid)
	title="Events Log"
	#for a in ac:
#		print a['event_id']
	return render_template("eventlog.html", title = title,data=records)
	



if __name__ == "__main__":
#	app.debug = True
	app.run(host='0.0.0.0')



