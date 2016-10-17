#!/usr/bin/env python
import sys, threading, time, ast, os
from socket import *

# Global Variables
hostname = gethostname()

# computeDistanceVector reads a data file of the format
#
# 3
# b 2.0
# c 5.0
# d 1.0
#
# and returns a dictionary containing the name/value pairs
# of hostnames and and  weights.  The key/value pair
# 'host: [hostname]' will be in [distanceVector] to identify
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
# 'host: [hostname]' will be in [distanceVector] to identify
# the host from which this distance vector came.
#
# i.e. {'host': 'smddevmysql01.urmc-sh.rochester.edu', 'smddevapche01.urmc-sh.rochester.edu': 2.0, 'smdsndphp01.urmc-sh.rochester.edu': 0.5}
def computeDistanceVector(dataFileLocation):
	distanceVector = {}
	distanceVector['host'] = hostname
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

# initializeRoutingTable takes a distance vector and returns
# routing table based on the information in the distance vector.
#
# input arguments:
# 1. distanceVector - A dictionary containing name/value pairs
# where each key is the string name of a directly connected host
# and each value is the float cost of the link between this host
# and the key.  The key/value pair "host' = [gethostname()]" must
# be included in  [distanceVector].
#
# return values:
# 1. routingTable - A dictionary containing name value pairs where
# each key is the string name of the key in [distanceVector] and
# each value is a dictionary containing two keys 'nextHop' and 'cost'.
# The value to nextHop is initialized to be the string name of the key
# in [distanceVector].  The value to cost is initialized to be the
# values in [distanceVector].
def initializeRoutingTable(distanceVector):
	routingTable = {}
	routingTable['host'] = distanceVector['host']
	for distanceVectorHost, distanceVectorCost in distanceVector.iteritems():
		if distanceVectorHost != 'host':
			routingTable[distanceVectorHost] = {'nextHop':distanceVectorHost, 'cost':distanceVectorCost}
	return routingTable

# udpClient opens a udpConnection with [serverName]:[serverPort].
#
# input arguments:
# 1. serverName - the string name of the server to which you would like
# to open a UDP connection.
# 2. serverPort - the integer port number of the server to which you would
# like to open a UDP connection.
def udpClient(serverName, serverPort):
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	clientSocket.sendto(str(distanceVector),(serverName, serverPort))
	clientSocket.close()

# a clientThread is a three tuple consisting of a port number,
# a sequence number that you would like the print statements to start at
# and the number of seconds you would like to wait between print
# statements.  Every [sleepSeconds] seconds, [distanceVector] is sent
# to all hosts in [distanceVector] via UDP and [routingTable] is updated
# accordingly.
#
# input arguments:
# 1. port - the integer port number that you would like to open a
# udp connection on.
# 2. sequenceNumber - the integer that you would like the sequence
# in the print statements to start on (1 is highly suggested).
# 3. sleepSeconds - the integer number of seconds you would like
# between udp messages to all hosts in [distanceVector].
class clientThread(threading.Thread):
	def __init__(self, port, sequenceNumber, sleepSeconds):
		threading.Thread.__init__(self)
		self.port = port
		self.sequenceNumber = sequenceNumber
		self.sleepSeconds = sleepSeconds
	def run(self):
		while 1:
	 		# Recomputing [distanceVector] and sending it to all connected nodes
			distanceVector = computeDistanceVector(dataFileLocation)
	 		for serverName in distanceVector:
	 			if serverName != 'host':
	 				udpClient(serverName, self.port)
	 		# Printing routing table 
			print '\n## '+str(self.sequenceNumber)
			for key, value in routingTable.iteritems():
				if key != 'host':
					print 'shortest path to node '+key+': the next hop is '+value['nextHop']+' and the cost is '+str(value['cost'])
			time.sleep(self.sleepSeconds)
			self.sequenceNumber += 1

# updateRoutingTable updates [routingTable] based on information
# recieved from UDP connections.  [routingTable] is updated if
# a better route is found to any hosts in [routingTable].
#
# input arguments:
# 1. distanceVectorDictionaryReceived - a dictionary representing
# a distance vector recieved from a directly connected client.
# [routingTable] is updated if a directly connected client knows
# of a more efficient route to any host in [routingTable].
def updateRoutingTable(distanceVectorDictionaryReceived):
	# hostRecieved will hold the host from which this distance vector was sent
	hostRecieved = distanceVectorDictionaryReceived['host']
	# Only listen to hosts to which route exists in [routingTable]
	if hostRecieved in routingTable:
		for distanceVectorHostRecieved, distanceVectorCostRecieved in distanceVectorDictionaryReceived.iteritems():
			if distanceVectorHostRecieved != 'host' and distanceVectorHostRecieved != hostname:
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

# a serverThread is a one-tuple consisting of an integer port number.
# serverThread will listen on this port number for incomming UDP connections.
# serverThread will update [routingTable] if a more efficient route is found
# in any client's [distanceVector].
#
# input arguments:
# 1. port - an integer representing the port number to listen for incomming UDP
# connections.
class serverThread(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
	def run(self):
		serverSocket = socket(AF_INET, SOCK_DGRAM)
		serverSocket.bind(('', self.port))
		while 1:
			distanceVectorStringReceived, clientAddress = serverSocket.recvfrom(2048)
			distanceVectorDictionaryReceived = ast.literal_eval(distanceVectorStringReceived)
			updateRoutingTable(distanceVectorDictionaryReceived)

# Global Variables
dataFileLocation = sys.argv[1]
distanceVector = computeDistanceVector(dataFileLocation)
# routingTable is initialized with information from distanceVector
routingTable = initializeRoutingTable(distanceVector)

# main method spawns off client thread and server thread.
def main():
	if len(sys.argv) == 3:
		port = int(sys.argv[2])
		# Listening on user specified port for incomming UDP connections
		print hostname+' listening on port '+str(port)
 		serverThread(port).start()
 		# Printing the current routing table at 10 second intervals
 		clientThread(port, 1, 10).start()
	else:
		print 'ERROR: Invalid number of arguments'

main()