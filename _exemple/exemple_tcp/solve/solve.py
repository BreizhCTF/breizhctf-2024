#!/usr/bin/env python3

import sys
from pwn import remote, context

if len(sys.argv) < 3:
    print("Usage solve.py <host> <port>")
    exit(1)

_, host, port = sys.argv

context.log_level = 'DEBUG'
socket = remote(host, port)

socket.recvuntil(b"Your name : ")
socket.sendline(b"plop")
result = socket.recvline()

assert result == b"Salut plop\n", f"Le challenge devrait dire bonjour ({result})"

print("Solved !")
