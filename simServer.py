#!/usr/bin/python

import socket
import sys
import time
from multiprocessing import Process, Lock

HOST = 'localhost'
PORT = 8888

def sim(lock, testname, bitstream, yuv):
    lock.acquire()
    print "Started test [testname bitstream yuv] => [%s %s %s]" % (testname, bitstream, yuv)
    time.sleep(20)
    print "Finished test [testname bitstream yuv] => [%s %s %s]" % (testname, bitstream, yuv)
    lock.release()

if __name__ == '__main__':

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Bind socket to local host and port
    try:

        # prevent socket error when socket left
        # in a TIME_WAIT state from previous execution
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))

    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s.listen(1)

    shutdown = False
    lock = Lock()

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
                    # workaround to check if lock is set
                    if lock.acquire(False):
                        state = "READY"
                        lock.release()
                    else:
                        state = "BUSY [%s %s %s]" % (testname, bitstream, yuv)
                    conn.send(state)

                elif cmd[0].lower() == "exit":
                    shutdown = True
                    break
            elif len(cmd) == 4 :
                if cmd[0].lower() == "test":
                    testname  = cmd[1]
                    bitstream = cmd[2]
                    yuv       = cmd[3]
                    p = Process(target=sim, args=(lock, testname, bitstream, yuv))
                    p.start()


        print "Shutdown requested!"

        # check if we need to terminate a running simulation
        if not(lock.acquire(False)):
            print "terminate running simulation"
            p.terminate()

        s.close()
