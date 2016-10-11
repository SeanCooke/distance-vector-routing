#!/usr/bin/env python
import sys, threading
from socket import *

# getConnectedNodeWeights reads a data file of the format
#
# 3
# b 2.0
# c 5.0
# d 1.0
#
# and returns a dictionary containing the name/value pairs
# of hostnames and weights detailed on lines 2 through the end
# of [dataFileLocation] i.e. {'c': 5.0, 'b': 2.0, 'd': 1.0}
#
# input arguments:
# 1. dataFileLocation - the location of a file to read
#
# return values:
# 1. connectedNodeWeights - a dictionary containing the name/value
# pairsof hostnames and weights detailed on lines 2 through the
# end of [dataFileLocation] i.e. {'c': 5.0, 'b': 2.0, 'd': 1.0}
def getConnectedNodeWeights(dataFileLocation):
	connectedNodeWeights = {}
	with open(dataFileLocation) as dataFile:
		line = dataFile.readline()
		lineIndex = 1
		while line:
			if lineIndex != 1:
				lineSplit = line.split()
				try:
					connectedNodeWeights[lineSplit[0]] = float(lineSplit[1])
				except IndexError:
					pass
			line = dataFile.readline()
			lineIndex += 1
	return connectedNodeWeights

class serverThread(threading.Thread):
	def __init__(self, port):
		threadingThread.__init(self)
			self.port = port
	def run(self):
		serverSocket = socket(AF_INET, SOCK_DGRAM)
		serverSocket.bind(('', port))
		print 'The server is ready to receive'
		while 1:
			message, clientAddress = serverSocket.recvfrom(2048)
			modifiedMessage = message.upper()
			serverSocket.sendto(modifiedMessage, clientAddress)
	
def main():
	if len(sys.argv) == 3:
		dataFileLocation = sys.argv[1]
		port = int(sys.argv[2])
		connectedNodeWeights = getConnectedNodeWeights(dataFileLocation)
		serverThread(port).start()
	else:
		print 'ERROR: Invalid number of arguments'
		
main()