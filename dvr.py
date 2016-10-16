#!/usr/bin/env python
import sys, threading, time, ast, os
from socket import *

# computeDistanceVector reads a data file of the format
#
# 3
# b 2.0
# c 5.0
# d 1.0
#
# and returns a dictionary containing the name/value pairs
# of hostnames and and  weights.  The key/value pair
# 'host: [gethostname()]' will be in [distanceVector] to identify
# the host from which this distance vector came.
#
# input arguments:
# 1. dataFileLocation - the location of a file to read
#
# return values:
# 1. distanceVector - a dictionary containing the name/value
# pairs of hostnames and weights detailed on lines 2 through
# the end of [dataFileLocation].  The values of [distanceVector]
# are the costs to the directly connected hosts.  The key/value pair
# 'host: [gethostname()]' will be in [distanceVector] to identify
# the host from which this distance vector came.
#
# i.e. {'host': 'smddevmysql01.urmc-sh.rochester.edu', 'smddevapche01.urmc-sh.rochester.edu': 2.0, 'smdsndphp01.urmc-sh.rochester.edu': 0.5}
def computeDistanceVector(dataFileLocation):
	distanceVector = {'host': gethostname()}
	with open(dataFileLocation) as dataFile:
		line = dataFile.readline()
		lineIndex = 1
		while line:
			if lineIndex != 1:
				lineSplit = line.split()
				try:
					distanceVector[lineSplit[0]] = float(lineSplit[1])
				except IndexError:
					pass
			line = dataFile.readline()
			lineIndex += 1
	return distanceVector
	
def initializeRoutingTable(distanceVector):
	routingTable = {}
	routingTable['host'] = distanceVector.pop('host', None)
	for distanceVectorHost, distanceVectorCost in distanceVector.iteritems():
		routingTable[distanceVectorHost] = {'nextHop':distanceVectorHost, 'cost':distanceVectorCost}
	return routingTable

def udpClient(serverName, serverPort):
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	clientSocket.sendto(str(distanceVector),(serverName, serverPort))
	clientSocket.close()

class clientThread(threading.Thread):
	def __init__(self, port, sequenceNumber, sleepSeconds):
		threading.Thread.__init__(self)
		self.port = port
		self.sequenceNumber = sequenceNumber
		self.sleepSeconds = sleepSeconds
	def run(self):
		while 1:
	 		# Recomputing [distanceVector] and sending it to all connected nodes
			computeDistanceVector(dataFileLocation)
	 		for key, value in distanceVector.iteritems():
	 			if key != 'host':
	 				udpClient(key, self.port)
	 		# Printing routing table 
			print '\n## '+str(self.sequenceNumber)
			for key, value in routingTable.iteritems():
				if key != 'host':
					print 'shortest path to node '+key+': the next hop is '+value['nextHop']+' and the cost is '+str(value['cost'])
			time.sleep(self.sleepSeconds)
			self.sequenceNumber += 1
			
def updateRoutingTable(distanceVectorDictionaryReceived):
	# hostRecieved will hold the host from which this distance vector was sent
	hostRecieved = distanceVectorDictionaryReceived.pop('host', None)
	# Only listen to hosts to which route exists in [routingTable]
	if hostRecieved in routingTable:
		for distanceVectorHostRecieved, distanceVectorCostRecieved in distanceVectorDictionaryReceived.iteritems():
			# If the host [distanceVectorHostRecieved] exists in [routingTable], see
			# if it's less expensive to go through [distanceVectorHostRecieved]
			if distanceVectorHostRecieved in routingTable:
				currentCost = routingTable[distanceVectorHostRecieved]['cost']
				newCost = routingTable[hostRecieved]['cost'] + distanceVectorCostRecieved
				if newCost < currentCost:
					newNextHop = routingTable[hostRecieved]['nextHop']
					routingTable[distanceVectorHostRecieved] = {'nextHop':newNextHop, 'cost':newCost}
			# Otherwise, add [keyRecieved] to [distanceVector]
			# by going through [hostRecieved]
			else:
				newCost = routingTable[hostRecieved]['cost'] + distanceVectorCostRecieved
				newNextHop = routingTable[hostRecieved]['nextHop']
				routingTable[distanceVectorHostRecieved] = {'nextHop':newNextHop, 'cost':newCost}
			

class serverThread(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
	def run(self):
		serverSocket = socket(AF_INET, SOCK_DGRAM)
		serverSocket.bind(('', self.port))
		while 1:
			distanceVectorStringReceived, clientAddress = serverSocket.recvfrom(2048)
			print '\n*****'
			print 'DISTANCE VECTOR RECEIVED'
			print '*****\n'
			distanceVectorDictionaryReceived = ast.literal_eval(distanceVectorStringReceived)
			updateRoutingTable(distanceVectorDictionaryReceived)

# Global Variables
dataFileLocation = sys.argv[1]
distanceVector = computeDistanceVector(dataFileLocation)
# routingTable is initialized with information from distanceVector
routingTable = initializeRoutingTable(distanceVector)

def main():
	if len(sys.argv) == 3:
		port = int(sys.argv[2])
		# Listening on user specified port for incomming UDP connections
		print gethostname()+' listening on port '+str(port)
 		serverThread(port).start()
 		# Printing the current routing table at 10 second intervals
 		clientThread(port, 1, 10).start()
	else:
		print 'ERROR: Invalid number of arguments'

main()