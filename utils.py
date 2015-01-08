import uuid
import zmq
from zmq import ZMQError
import socket
import datetime,time
from database import Base,init_db,db_session
from models import *
import pdb
import ConfigParser
import sys
import logging
import pprint 

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

class Utils():

		def __init__(self,app,loglevel=logging.INFO):
			logging.info('ass')
			self.context = zmq.Context()
			self.socket = self.context.socket(zmq.PUB)
			self.app=app

		def log_info(self,msg):
			logging.info(msg)
			

		def log_error(self,msg):
			logging.error(msg)
			

		def log_warn(self,msg):
			logging.warnning(msg)
			


		def start_zmq(self,port=43434):
			try:
				self.log_info( "Starting on port %s"%(port))
				self.socket.bind("tcp://*:%s" % port)
			except ZMQError:
				self.log_error( "Port is already used")
				return False
			self.log_info( "Zero MQ server started")
			return True



		def stop_zmq(self):
			self.log_info( "Stopping zmq")
			self.context.destroy();

		def send_zmq_msg(self,topic,msg):
			self.log_info( "->publishing %s to %s"%(msg,topic))
			self.log_info( "Topic:%s msg:%s"%(topic,msg))
			self.socket.send("Topic:%s %s"%(topic,str(msg)))
			#print self.socket.send_multipart([topic,str(msg)])
			self.log_info( "Sending msg to %s"%(topic))

		def getHostId(self,hostip):
			resultSet=hosts.query.filter_by(host_ip=hostip,registered=1).first()
			self.log_info( resultSet);
			if resultSet is not None:
				self.log_info( "returning hostid %s"%(resultSet.host_id))
				return resultSet.host_id	
			print "returning false"
			return False

		
		def getHostNameById(self,hostid):
			resultSet=hosts.query.filter_by(host_id=hostid).one();
			self.log_info( resultSet)
			if resultSet is not None:
				self.log_info( "returning hostname %s for hostid %s"%(resultSet.host_id,resultSet.host_name))
				return resultSet.host_name
			self.log_info( "Could not get hostname for Id [%s]"%(hostid))
			return False

		def registerHost(self,hostname,ip):
			hostsObj=hosts();
			checkQuery=hosts.query.filter_by(host_ip=ip).first();
			if checkQuery==False or checkQuery is None:
				self.log_info( "registering host",hostname,ip)
				hostsObj.host_name=hostname;
				hostsObj.host_ip=ip;
				hostsObj.registered=0
				hostsObj.ts=datetime.datetime.utcnow()
				if ip == 0 or ip == False or ip is None:
					self.log_info( "failed to register, could not obtain IP %s %s"%(hostname,ip))
				else:
					db_session.add(hostsObj);
					db_session.commit();


		def getHostIp(self,hostname):
			try:
				return socket.gethostbyname(hostname)
			except Exception, e:
				self.log_info( "failed to get hostip for %s"%(hostname))
				return False;
			
			
		def getHostName(self,ip):
			try:
				return socket.gethostbyaddr(self,ip)
			except Exception, e:
				return False;


		def updateTransactionLog(self,log):
			tlog=serverTransactionLog(log);
			db_session.add(tlog);
			self.write_to_stdout(log);
			db_session.commit();
		
		def write_to_stdout(self,log):			
				print("%s %s" % (datetime.datetime.utcnow().isoformat(), log));

		def updateStatus(self,eventid,status_id):
			checkEvent.query.filter_by(checkevent_id=eventid).update({"status":status_id})
			db_session.commit();
			

		def getEventStatus(eventId):
			resultSet = checkEvent.query.filter_by(checkevent_id=eventId).first();
			for row in resultSet:
				return row.status
			return False

		def publishToMQ(Topic,publishToMQ):
			return ""

		def recordExecLog(self,eventId,execStatus,stdout,stderr="",comments=""):
			execLog = eventsExeclog();
			execLog.event_id = eventId;
			execLog.event_statusId = execStatus;
			execLog.event_stdout = stdout
			execLog.event_stderr = stderr
			execLog.event_comment =  comments
			db_session.add(execLog)
			db_session.commit()

		def getEventId(self,ename):
			#eventsObj=events()
			resultSet = events.query.filter_by(event_name=ename).first();
			if resultSet == False:
				return False
			if resultSet is not None:
				print "event id ",resultSet.event_id
				return  resultSet.event_id
			return False

		def getEventTimeout(self,eventid):
			#eventsObj=events()
			resultSet = events.query.filter_by(event_id=eventid).first();
			if resultSet == False:
				return False
			if resultSet is not None:
				print "timeout ",resultSet.timeout
				return  resultSet.timeout
			return False

		def getLastEventExecTime(self,eventid,hostid):
			print "%s,%s"%(hostid,eventid)
			resultSet=checkEvent.query.filter_by(dest2_hostid=hostid,event_id=eventid).order_by(checkEvent.ts.desc()).first()
			#print resultSet;
			#print resultSet.ts
			if resultSet is None:
				print "false returned"
				return False
			else:
				print "t returned"
				
				return resultSet.ts

		def getLastEventExecId(self,eventid,hostid):
			print "%s,%s"%(hostid,eventid)
			resultSet=checkEvent.query.filter_by(dest2_hostid=hostid,event_id=eventid).order_by(checkEvent.ts.desc()).first()
			#print resultSet;
			#print resultSet.event_id
			if resultSet is None:
				print "false returned"
				return False
			else:
				print "t returned"
				return resultSet.checkevent_id
								
		def generateUniqId(self):
			return str(uuid.uuid4())
		
		
		def getStatusCodes(self):
			sc=statusCodes.query.all();
			return sc

		def getHosts(self):
			return hosts.query.all();

		def getEvents(self):
			return events.query.all();

		def readConfigTxt(self,filename="config/quix.conf"):
			config = ConfigParser.RawConfigParser()
			try:
				fp=open(filename);
				return fp.read()
				

				
			except:
				print "Unexpected error:", sys.exc_info()
				return False;

		def getChecks(self,status=None):
			if status is None:
				a=db_session.query(checkEvent,statusCodes,events).filter(checkEvent.status==statusCodes.status_id).filter(events.event_id==checkEvent.event_id).all()
			else:
				a=db_session.query(checkEvent,statusCodes,events).filter(statusCodes.status==status).filter(checkEvent.status==statusCodes.status_id).filter(events.event_id==checkEvent.event_id).all()	
			checklist=[]
			for c,s,e in a:
				activechecks={}
				activechecks['event_id']=c.checkevent_id
				activechecks['src']=self.getHostNameById(c.src_hostid)
				activechecks['dest']=self.getHostNameById(c.dest2_hostid)
				activechecks['ts']=c.ts
				activechecks['event_name']=e.event_name

				
				checklist.append(activechecks)
			return checklist
		def timestamp_to_string(self,ts):
			 f = '%Y-%m-%d %H:%M:%S'
			 return ts.strftime(f)

		def getEventLog(self,eventid):
			resultSet=eventsExeclog.query.filter_by(event_id=eventid).all()
			self.log_info(resultSet)
			log=[]
			if resultSet is None:
				self.log_info( "no result found for eventid:%s"%(eventid))
				return log
			else:
				
				for i in resultSet:
					eventlog={}
					eventlog['event_id']=i.event_id
					eventlog['event_statusId']=i.event_statusId
					eventlog['event_stdout']=i.event_stdout
					eventlog['event_stderr']=i.event_stderr
					eventlog['event_comment']=i.event_comment
					eventlog['ts']=self.timestamp_to_string( i.ts)
					log.append(eventlog)
					return log



		def __del__(self):
			self.stop_zmq()

# 
