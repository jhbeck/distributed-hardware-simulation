#!/usr/bin/python

import socket
import sys
import time
from thread import *

HOST = 'localhost'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind socket to local host and port
try:
    # prevent socket error when socket left in a TIME_WAIT state from previous execution
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

s.listen(1)

shutdown = False
state    = "READY"

def simthread(testname, bitstream, yuv):
    print "Started test [testname bitstream yuv] => [%s %s %s]" % (testname, bitstream, yuv)
    global state
    state = "BUSY %s %s %s" % (testname, bitstream, yuv)
    time.sleep(10)
    print "Finished test [testname bitstream yuv] => [%s %s %s]" % (testname, bitstream, yuv)
    state = "READY"

while not shutdown:

    print "Waiting for a new request"
    conn, addr = s.accept()
    print 'New connection from ' + addr[0] + ':' + str(addr[1])

    # handle incoming data
    while True:

        data = conn.recv(1024)
        print data.split()

        if not data:
            break

        cmd = data.split()

        if len(cmd) == 1:

            if cmd[0].lower() == "state":
                conn.send(state)
            elif cmd[0].lower() == "shutdown":
                shutdown = True
                break

        elif len(cmd) == 4 :

            if cmd[0].lower() == "test":
                start_new_thread(simthread, (cmd[1], cmd[2], cmd[3]))

print "Shutdown requested!"
s.close()
