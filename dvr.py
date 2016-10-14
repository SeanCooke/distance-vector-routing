#!/usr/bin/env python
import sys, threading, time
from socket import *

# getConnectedNodeWeights reads a data file of the format
#
# 3
# b 2.0
# c 5.0
# d 1.0
#
# and returns a dictionary containing the name/value pairs
# of hostnames, next hops, and  weights.  The initial next hops
# are the hostnames.  The initial weights are detailed on lines 2
# through the end of [dataFileLocation].
#
# input arguments:
# 1. dataFileLocation - the location of a file to read
#
# return values:
# 1. connectedNodeWeights - a dictionary containing the name/value
# pairsof hostnames, next hops, and weights detailed on lines 2 through
# the end of [dataFileLocation].  The value of [connectedNodeWeights]
# is a dictionary with keys 'nextHop' and 'cost'.  The key 'nextHop' in
# the values of [connectedNodeWeights] holds the current next hop to
# get to they key. The key 'cost' in the values of [connectedNodeWeights]
# holds the cost to get to the key.
#
# i.e. {'c': {'nextHop': 'c', 'cost': 5.0}, 'b': {'nextHop': 'b', 'cost': 2.0}, 'd': {'nextHop': 'd', 'cost': 1.0}}
def getConnectedNodeWeights(dataFileLocation):
	connectedNodeWeights = {}
	with open(dataFileLocation) as dataFile:
		line = dataFile.readline()
		lineIndex = 1
		while line:
			if lineIndex != 1:
				lineSplit = line.split()
				try:
					connectedNodeWeights[lineSplit[0]] = {'nextHop':lineSplit[0], 'cost':float(lineSplit[1])}
				except IndexError:
					pass
			line = dataFile.readline()
			lineIndex += 1
	return connectedNodeWeights
	
def openUDPConnection(serverName, serverPort):
	print 'Opening A UDP Connection with '+serverName+':'+str(+serverPort)
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	message = raw_input('Enter input: ')
	clientSocket.sendto(message,(serverName, serverPort))
	modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
	print modifiedMessage
	clientSocket.close()

class printConnectedNodeWeights(threading.Thread):
	def __init__(self, sequenceNumber, sleepSeconds):
		threading.Thread.__init__(self)
		self.sequenceNumber = sequenceNumber
		self.sleepSeconds = sleepSeconds
	def run(self):
		while 1:
			print '## '+str(self.sequenceNumber)
			for key, value in connectedNodeWeights.iteritems():
				print 'shortest path to node '+key+' the next hop is '+value['nextHop']+' and the cost is '+str(value['cost'])
			time.sleep(self.sleepSeconds)
			self.sequenceNumber += 1

class serverThread(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
	def run(self):
		serverSocket = socket(AF_INET, SOCK_DGRAM)
		serverSocket.bind(('', self.port))
		while 1:
			messageRecieved, clientAddress = serverSocket.recvfrom(2048)
			myString = messageRecieved
			serverSocket.sendto(myString, clientAddress)

# Global Variables
dataFileLocation = sys.argv[1]
connectedNodeWeights = getConnectedNodeWeights(dataFileLocation)

def main():
	if len(sys.argv) == 3:
		port = int(sys.argv[2])
		# Listening on user specified port for incomming UDP connections
		print gethostname()+' listening on port '+str(port)
 		serverThread(port).start()
 		# Printing the current routing table at 10 second intervals
 		printConnectedNodeWeights(1, 10).start()
 		# Sending connectedNodeWeights to all connected nodes
 		for key, value in connectedNodeWeights.iteritems():
 			openUDPConnection(key, port)
	else:
		print 'ERROR: Invalid number of arguments'

main()