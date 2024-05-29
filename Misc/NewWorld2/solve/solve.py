#!/usr/bin/env python3

from pwn import *
import base64
from emulator import *

if len(sys.argv) < 3:
    print("Usage solve.py <host> <port>")
    exit(1)
_, host, port = sys.argv

io = remote(host, int(port))

for i in range(10):
    io.recvuntil(b"en base64) :\n")
    b64_bin = io.recvline().strip()
    res = run_emulator(b64_bin)
    io.sendlineafter(b"sortie ?\n",res)

io.interactive()