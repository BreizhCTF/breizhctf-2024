#!/usr/bin/env python3

import random
import sys
import ecdsa
from hashlib import sha256
from Crypto.Util.number import bytes_to_long
from base64 import b64decode

NB_DIFFICULTY = 20
NB_TRY_RANDOM = 10 ** 4
NB_GOAL = int(0.74 * NB_TRY_RANDOM)

FLAG = r"BZHCTF{13g3ndreSymb0l1sTheK3y}"

def first_nbits_zero(data, nb):
    data_long = bytes_to_long(data)
    result = True

    for _ in range(nb):
        if data_long % 2 == 1:
            result = False
        data_long = data_long >> 1
    return result


def proof_of_work():
    salt = random.randbytes(8)
    print(f"The salt is {salt.hex()}")

    data = b64decode(input("Give me your input : "))

    if not salt in data[:len(salt)]:
        print(f"Data doesn't have : {salt.hex()}")
        sys.exit()

    hashed = sha256(data).digest()

    if not first_nbits_zero(hashed, NB_DIFFICULTY ):
        print("The hashed need more 0")
        sys.exit()

    print(f"Proof of work validated : {hashed.hex()}")


def create_real_signature():
    msg = random.randbytes(96)
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST384p, hashfunc=sha256)
    sig = sk.sign(msg)
    return sig

def create_false_signature():
    msg = random.randbytes(96)
    return msg

def random_guesser():
    print("Hi wanderer, prove me you can find real signature : ")
    total_good_answers = 0

    for _ in range(NB_TRY_RANDOM):
        is_real = None
        signature = None

        if random.getrandbits(1) == 1:
            is_real = True
            signature = create_real_signature()
        else:
            is_real = False
            signature = create_false_signature()

        print(f"The signature is : {signature.hex()}")

        answer = input("Does my signature is real : ")

        if answer.lower().strip() == "yes":
            if is_real:
                total_good_answers += 1

        if answer.lower().strip() == "no":
            if not is_real:
                total_good_answers += 1

    print(f"You found {total_good_answers} good guesses.")

    if total_good_answers > NB_GOAL:
        print(f"Good job, here is your flag : {FLAG}")

def main():
    proof_of_work()
    random_guesser()

if __name__ == "__main__":
    main()
