from database import Base,init_db
from sqlalchemy import Column, Integer, String,DateTime,ForeignKey,TEXT

#from utils import *
import datetime


class events(Base):
    __tablename__ = 'event_types'
    event_id = Column(Integer, primary_key=True)
    event_name =  Column(String(120))
    timeout = Column(Integer,default=60)
    
    
class statusCodes(Base):
    __tablename__="status_codes"
    status_id=Column(Integer,primary_key=True)
    status = Column(String(50))
    
class checkEvent(Base):
    __tablename__ = 'check_events'
    checkevent_id = Column(String(50), primary_key=True)
    src_hostid = Column(Integer,ForeignKey('hosts.host_id'))
    dest2_hostid = Column(Integer,ForeignKey('hosts.host_id'))
    event_id= Column(Integer,ForeignKey('event_types.event_id'))
    ts=Column(DateTime,default=datetime.datetime.utcnow)
    status = Column(Integer,ForeignKey('status_codes.status_id'))

'''
    def __init__(self,src_hostid,dest2_hostid,checkevent_id):
        self.checkevent_id=utils.generateUniqId()
        self.src_hostid=src_hostid
        self.dest2_hostid=dest2_hostid
        self.checkevent_id=checkevent_id
'''

class serverTransactionLog(Base):
    __tablename__ = 'server_tlog'
    tlog_id = Column(Integer, primary_key=True)
    ts=Column(DateTime,default=datetime.datetime.utcnow)
    tlog_txt = Column(TEXT)
    def __init__(self,log_msg):
        self.tlog_txt=log_msg


class hosts(Base):
    __tablename__ = 'hosts'
    host_id = Column(Integer, primary_key=True)
    host_name = Column(String(120))
    host_ip = Column(String(120),unique=True)
    registered = Column(Integer)
    Comments = Column(TEXT)
    ts=Column(DateTime,default=datetime.datetime.utcnow)


class eventsExeclog(Base):
    __tablename__ = 'eventsExeclog'
    log_id=Column(Integer, primary_key=True)
    event_id = Column(String(50),ForeignKey('check_events.checkevent_id'))
    event_statusId=Column(Integer,ForeignKey('status_codes.status_id'))
    event_stdout=Column(TEXT)
    event_stderr=Column(TEXT)
    event_comment=Column(TEXT)
    ts=Column(DateTime,default=datetime.datetime.utcnow)