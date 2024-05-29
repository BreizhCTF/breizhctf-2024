#!/usr/bin/env python3
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring

import sys
import json
import math
from pwn import remote

if len(sys.argv) < 3:
    print("Usage: solve.py <host> <port> DEBUG")
    exit(1)

_, HOST, PORT = sys.argv

PROMPT= ">>> ".encode()

s = remote(HOST,PORT)
print(s.recvuntil(PROMPT).decode())

def get_messages():
    for k in range(256):
        messages = []
        for y in range(256):
            tmp = bytearray.fromhex(hex(k).replace("0x",'').zfill(2) * 16)
            tmp[0]=y
            messages.append(tmp.hex())
        yield messages

SHUFFLE_BOX = [0, 0xd, 0xa, 7, 4, 1, 0xe, 0xb, 8, 5, 2, 0xf, 0xc, 9, 6, 3]

LIST_PHI = []
LIST_TETA = []

LIST_PHI.append(0)
for x in range(1,16):
    LIST_PHI.append(2 * math.pi * ((14+x)/40))


LIST_TETA.append(0)
for x in range(1,15):
    LIST_TETA.append(math.pi * ((14+x)/40))
LIST_TETA.append(math.pi)


def int_to_bloch_sphere(val):
    phi = LIST_PHI[val // 16]
    teta = LIST_TETA[val % 16]
    return BlochSphere(phi, teta)


class BlochSphere:
    def __init__(self,phi,teta):
        self.phi = phi
        self.teta = teta

    def get_phi(self):
        return self.phi

    def get_teta(self):
        return self.teta

    def get_int(self):
        return LIST_PHI.index(self.get_phi()) * 16 + LIST_TETA.index(self.get_teta())

    def pauli_x(self, number):
        self.teta = LIST_TETA[(LIST_TETA.index(self.get_teta()) + number) % len(LIST_TETA)]

    def pauli_z(self, number):
        self.phi = LIST_PHI[(LIST_PHI.index(self.get_phi()) + number) % len(LIST_PHI)]

def find_value(index):
    candidates_list = list(range(256))
    for msg_list in get_messages():

        msg_to_send = {"TYPE": "input_multiple_messages"}
        msg_to_send["MESSAGES"] = msg_list
        msg_to_send = json.dumps(msg_to_send)
        s.sendline(str(msg_to_send).encode())
        s.recvline()

        msg_to_send = {"TYPE": "combine_message"}
        msg_to_send = json.dumps(msg_to_send)
        s.sendline(str(msg_to_send).encode())
        s.recvline()

        test_value = candidates_list[0]
        print(f"Round : {str(index)}, testing : {test_value}.")

        shuffle_index = SHUFFLE_BOX[index] # take in account the shuffle operation

        msg_to_send = {
            "TYPE": "measure_message",
            "PHI": test_value // 16,
            "TETA": test_value % 16,
            "INDEX": shuffle_index
        }
        msg_to_send = json.dumps(msg_to_send)

        s.sendline(str(msg_to_send).encode())

        res = s.recvline().decode()
        res = res.split(':')[1].strip().removesuffix(".")
        res = json.loads(res)

        if res[index] != 0:
            candidates_list.remove(test_value)
        else:
            res = candidates_list[0] % 256
            b_sphere = int_to_bloch_sphere(res)
            b_sphere.pauli_x(SHUFFLE_BOX[index])
            b_sphere.pauli_z(SHUFFLE_BOX[index])
            res = b_sphere.get_int()
            print(f"The byte was : {res}.")
            return res
    return None

def main():
    for i in range(16):
        val = find_value(i)
        msg_to_send = {
            "TYPE": "guess_key",
            "USERKEY": hex(val).replace("0x",'').zfill(2)
        }
        msg_to_send = json.dumps(msg_to_send)
        print(msg_to_send)
        s.sendline(str(msg_to_send).encode())
        print(s.recvline().decode())

    print(s.recvline().decode()) # print the flag

if __name__ == "__main__":
    main()
