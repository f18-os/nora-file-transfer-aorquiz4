# nets-tcp-framed-race

To handle the race condition I used 'Lock' from the threading library. This allows to 'acquire()' and 'release()' locks for stopping a thread and executing a thread.

File 'framedThreadServer.py' writes a file recieved from client and where the lock is implemented.

File 'framedThreadClient.py' reads a file that is input by user.

To run (each command in seperate terminal):

	$ ./framedThreadServer.py
	$ ./framedThreadClient.py