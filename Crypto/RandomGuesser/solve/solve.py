#!/usr/bin/env python3

import sys
from base64 import b64encode
from hashlib import sha256
from random import randbytes
from Crypto.Util.number import bytes_to_long
import ecdsa
from pwn import *

if len(sys.argv) < 3:
    print("Usage: solve.py <host> <port> DEBUG")
    exit(1)

_, HOST, PORT = sys.argv

CURVE = ecdsa.NIST384p
CURVE_P = CURVE.curve.p()
CURVE_A = CURVE.curve.a()
CURVE_B = CURVE.curve.b()

NB_TRY_RANDOM = 10 ** 4
NB_DIFFICULTY = 20

def legendre(data):
    r = bytes_to_long(data[:len(data)//2])
    base = pow(r,3) + r * CURVE_A + CURVE_B
    power = (CURVE_P-1) // 2
    modulo = CURVE_P
    return pow(base,power,modulo)

def first_nbits_zero(data, nb):
    data_long = bytes_to_long(data)
    result = True

    for _ in range(nb):
        if data_long % 2 == 1:
            result = False
        data_long = data_long >> 1
    return result

def proof_of_work(s):
    tmp = s.recvlineS()
    salt = bytearray.fromhex(tmp.split()[-1])
    print(f"Salt : {tmp}")

    goal = False
    compt = 0
    while not goal:
        compt += 1
        if compt % 10_000 == 0:
            print('.', end='', flush=True)
        data = salt + randbytes(4)
        hashed_data = sha256(data).digest()
        goal = first_nbits_zero(hashed_data, NB_DIFFICULTY )

    s.sendline(b64encode(data))

    print("proof_of_work finished.")
    s.recvlineS()
    s.recvlineS()

def main():
    s = remote(HOST,PORT)
    proof_of_work(s)

    for i in range(NB_TRY_RANDOM):
        if i%100 == 0:
            print(f"{int(100 * (i/NB_TRY_RANDOM))}% done")
        data = s.recvlineS()

        signature = data.split()[-1]
        signature_byte = bytearray.fromhex(signature)

        result = legendre(signature_byte)

        if result==1:
            s.sendline(b"yes")
        elif result == CURVE_P-1:
            s.sendline(b"no")
        else:
            print("Should not happend")
            sys.exit()

    print(s.recvlineS())
    print(s.recvlineS())

if __name__ == "__main__":
    main()
