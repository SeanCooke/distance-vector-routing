#!/usr/bin/env python
import sys, threading, time, ast, os
from socket import *

# getDistanceVector reads a data file of the format
#
# 3
# b 2.0
# c 5.0
# d 1.0
#
# and returns a dictionary containing the name/value pairs
# of hostnames, next hops, and  weights.  The initial next hops
# are the hostnames.  The initial weights are detailed on lines 2
# through the end of [dataFileLocation].  The key/value pair
# 'host: [gethostname()]' will be in [distanceVector] to identify
# the host from which this routing table came.
#
# input arguments:
# 1. dataFileLocation - the location of a file to read
#
# return values:
# 1. distanceVector - a dictionary containing the name/value
# pairsof hostnames, next hops, and weights detailed on lines 2 through
# the end of [dataFileLocation].  The value of [distanceVector]
# is a dictionary with keys 'nextHop' and 'cost'.  The key 'nextHop' in
# the values of [distanceVector] holds the current next hop to
# get to they key. The key 'cost' in the values of [distanceVector]
# holds the cost to get to the key.  The key/value pair 'host: [gethostname()]'
# will be in [distanceVector] to identify the host from which this 
# routing table came.
#
# i.e. {'host': 'scooke1x9lt.urmc-sh.rochester.edu','c': {'nextHop': 'c', 'cost': 5.0}, 'b': {'nextHop': 'b', 'cost': 2.0}, 'd': {'nextHop': 'd', 'cost': 1.0}}
def getDistanceVector(dataFileLocation):
	distanceVector = {'host': gethostname()}
	with open(dataFileLocation) as dataFile:
		line = dataFile.readline()
		lineIndex = 1
		while line:
			if lineIndex != 1:
				lineSplit = line.split()
				try:
					distanceVector[lineSplit[0]] = {'nextHop':lineSplit[0], 'cost':float(lineSplit[1])}
				except IndexError:
					pass
			line = dataFile.readline()
			lineIndex += 1
	return distanceVector
	
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
	 		# Sending distanceVector to all connected nodes
	 		for key, value in distanceVector.iteritems():
	 			if key != 'host':
	 				udpClient(key, self.port)
			print '\n## '+str(self.sequenceNumber)
			for key, value in distanceVector.iteritems():
				if key != 'host':
					print 'shortest path to node '+key+': the next hop is '+value['nextHop']+' and the cost is '+str(value['cost'])
			time.sleep(self.sleepSeconds)
			self.sequenceNumber += 1
			
def updatedistanceVector(dictionaryRecieved):
	# hostRecieved will hold the host from which this routing table was sent
	hostRecieved = dictionaryRecieved.pop('host', None)
	print '\n***********'
	print 'hostRecieved: '+hostRecieved
	print '***********\n'
	# Only listen to hosts to which route exists in [distanceVector]
	if hostRecieved in distanceVector:
		for keyRecieved, valueRecieved in dictionaryRecieved:
			# If the host [keyRecieved] exists in [distanceVector], see
			# if it's less expensive to go through [hostRecieved]
			if keyRecieved in distanceVector:
				currentCost = distanceVector[keyRecieved]['cost']
				newCost = distanceVector[hostRecieved]['cost'] + valueRecieved['cost']
				if newCost < currentCost:
					distanceVector[keyRecieved] = {'nextHop':hostRecieved, 'cost':newCost}
			# Otherwise, add [keyRecieved] to [distanceVector]
			# by going through [hostRecieved]
			else:
				newCost = distanceVector[hostRecieved]['cost'] + valueRecieved['cost']			
				distanceVector[keyRecieved] = {'nextHop':hostRecieved, 'cost':newCost}
			

class serverThread(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
	def run(self):
		serverSocket = socket(AF_INET, SOCK_DGRAM)
		serverSocket.bind(('', self.port))
		while 1:
			objectRecieved, clientAddress = serverSocket.recvfrom(2048)
			dictionaryRecieved = ast.literal_eval(objectRecieved)
			updatedistanceVector(dictionaryRecieved)

# Global Variables
dataFileLocation = sys.argv[1]
distanceVector = getDistanceVector(dataFileLocation)

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