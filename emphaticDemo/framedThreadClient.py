#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

path = os.getcwd()+"/serverFiles"
try:  
    os.mkdir(path)
except OSError: 
    print ("Creation of the directory %s failed" % path)
else:  
    print ("Created the directory %s " % path)

# Get file info
fileName = ''
print("Enter File for transfer (only puts file, does not get): ")
fileName = input()

newPath = path+"/"+fileName

if os.path.exists(newPath):
  print("File already exists on server.")
  sys.exit()

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
      s = None
      for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
          af, socktype, proto, canonname, sa = res
          try:
              print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
              s = socket.socket(af, socktype, proto)
          except socket.error as msg:
              print(" error: %s" % msg)
              s = None
              continue
          try:
              print(" attempting to connect to %s" % repr(sa))
              s.connect(sa)
          except socket.error as msg:
              print(" error: %s" % msg)
              s.close()
              s = None
              continue
          break

      if s is None:
          print('could not open socket')
          sys.exit(1)

      fs = FramedStreamSock(s, debug=debug)


      # Read file
      if '.txt' in fileName: # handles text files, read as string and decoded into bytes
          header = str.encode(fileName)
          try:
              file = open(fileName, 'r') # reading text file
          except FileNotFoundError: # if the file doesn't exist don't run
              print(fileName+" does not exist.")
              print("Exiting program...")
              sys.exit(0)
          
          print("Transferring %s to default location on server." % (fileName))
          
          statinfo = os.stat(fileName) # checking the size of file

          if statinfo.st_size:
              print("Size of file (in bytes): %s" % (statinfo.st_size)) 
          else:
              print("File is of size zero (empty file).") # if size is zero then dont continue because file is empty.
              print("Exiting program...")
              sys.exit(0)

          readFile = file.read()
          readFile = readFile.replace('\n', '\0')
          readFile = readFile.encode()
          fs.sendmsg(header) # send file name
          fs.sendmsg(readFile) # send the data 
      else:                                       # handles other file types, read as bytes
          header = str.encode(fileName)

          try:
              file = open(fileName, 'rb') # read that jpg's and exe's are read in bytes
          except FileNotFoundError:
              print(fileName+" does not exist.")
              print("Exiting program...")
              sys.exit(0)

          print("Transferring %s to default location on server." % (fileName))
          
          statinfo = os.stat(fileName) # checking the size of file

          if statinfo:
              print("Size of file (in bytes): %s" % (statinfo.st_size)) 
          else:
              print("File is of size zero (empty file).") # if size is zero then dont continue because file is empty.
              print("Exiting program...")
              sys.exit(0)

          readFile = file.read()
          fs.sendmsg(header) # send file name
          fs.sendmsg(readFile) # send the data

for i in range(100):
    ClientThread(serverHost, serverPort, debug) # create 100 threads of the same file and just overwritres a hundred times

