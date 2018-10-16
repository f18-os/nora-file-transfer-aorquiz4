#! /usr/bin/env python3
import sys, os, socket, params, time, threading
from threading import Thread
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

lock = threading.Lock() # method of syncronization

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        lock.acquire()  # lock execution until release
        while True:
            header = self.fsock.receivemsg()
            if not header:
                lock.release()
                if self.debug: print(self.fsock, "server thread done")
                return
            fileName = header.decode() # convert to string by decoding bytes
            payload = self.fsock.receivemsg()
            wrtieFile = open(os.getcwd()+"/serverFiles/"+fileName, 'wb')
            wrtieFile.write(payload)
            wrtieFile.close()  # write the new file and close it
            requestNum = ServerThread.requestCount
            ServerThread.requestCount = requestNum + 1
            print("complete %s" % (requestNum+1)) # prints number of file transfers 
        lock.release() # unlocked and returns 


while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug) 