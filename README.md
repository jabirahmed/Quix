Quix
=================

Quix, provides an interface to remotely execute scripts to fix issues on unix servers



Requirement
-------------

  * brew install  mysql
  * easy_install pip
  * pip install flask
  * pip install sqlalchemy
  * pip install pyzmq
  * pip install MySQL-python
  * sudo -E pip install MySQLdb

  Ubuntu Based Packages

  * sudo apt-get install python-mysqldb
  * sudo apt-get install -y libzmq1
  * sudo apt-get install mysql-server mysql-client

	On Mac OSX  10.8 and above
	
  * export CFLAGS=-Qunused-arguments
  * export CPPFLAGS=-Qunused-arguments


Web API's
----------

 * /test/
 * /statuscodes/     : List all status codes
 * /updateCheckStatus/<eventid>",methods=["POST"])     : To update status from client
 * /triggerCheck/<hostname>/<check>",methods=["GET"])   : Initiate a check
 * /shutdown", methods=["GET"])   : Gracefully shutdown server
 * /static/<path:path>
 * /static/   : For static files
 * /      : WebRoot UI
 * /hl/   : Host List
 * /sc/   : Status codes
 * /el/   :
 * /cfg/  : Configuration 
 * /listChecks/<status>  : List all check with specific status
 * /listChecks/     : List all check 
 * /eventLog/<eventid>  : Event log history
 * /eventLog

Starting the server
-------------------
 * ./webservice.py

client
 * ./quixListener.py
