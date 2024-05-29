#!/usr/bin/env python3
# pip3 install pwntools

from sys import argv
from pwn import *

if len(argv) < 3:
    print("Usage: solve.py <host> <port> DEBUG")

_, HOST, PORT = argv

NOTHING_MINE = '{"x":5,"y":4}'.encode()

class WichmannHill:

    def __init__(self,s1,s2,s3):
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3

    def generate_number(self):
        self.s1 = (self.s1 * 171 ) % 30269
        self.s2 = (self.s2 * 172 ) % 30307
        self.s3 = (self.s3 * 170 ) % 30323

        return  self.s1 + self.s2 + self.s3


def main():
    lookup_table = []

    s1=4598
    s2=19635
    s3=5236

    prng = WichmannHill(s1,s2,s3)

    for i in range(20_000):
        prng.generate_number()

    for i in range(31_000):
        value = prng.generate_number()
        lookup_table.append(value)

    s = remote(HOST,PORT)

    s.recvline()
    s.recvline()

    # Fail the first round on purpose
    s.sendline(NOTHING_MINE)
    s.sendline(NOTHING_MINE)
    s.sendline(NOTHING_MINE)

    s.recvline()
    s.recvline()
    s.recvline()
    # Grab the last mine to predict more mines
    last_mine = s.recvline().split()
    seed3 = int(last_mine[3])*1000+ int(last_mine[4])
    index = lookup_table.index(seed3)

    for i in range(3):
        for y in range(3):
            val = lookup_table[(index + 1 + i*3 + y) % len(lookup_table)]
            next_mine = '{"x":' +str(val//1000) + ',"y":'+ str(val%1000) +'}'
            s.sendline(next_mine.encode())

        # discard following mines, we don't need those informations
        for _ in range(8):
            s.recvline()

    print(s.recvline().decode())

if __name__ == "__main__":
    main()
