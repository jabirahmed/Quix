from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
import os
import ConfigParser

'''
Adding the Database Config from the config file

'''

config = ConfigParser.ConfigParser()
config.read("config/quix.conf")

user = config.get("mysql", "user")
password = config.get("mysql", "password")
server = config.get("mysql", "server")
port = config.get("mysql", "port")

engine = create_engine('mysql://%s:%s@%s:%s/quix'%(user, password, server, port), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
			
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

    
