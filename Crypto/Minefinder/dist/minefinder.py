#!/usr/bin/env python3

import random
import json

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


FLAG = "REDACTED"


def create_map(prng):
    carte = []

    rng1 = prng.generate_number()
    rng2 = prng.generate_number()
    rng3 = prng.generate_number()

    mine1 = (rng1 // 1000,rng1 % 1000)
    mine2 = (rng2 // 1000,rng2 % 1000)
    mine3 = (rng3 // 1000,rng3 % 1000)

    carte.append(mine1)
    carte.append(mine2)
    carte.append(mine3)

    return carte


def play_round(prng):
    carte = create_map(prng)
    result = False
    nb_mine_found = 0

    copy_carte = []
    for mine in carte:
        copy_carte.append((mine[0], mine[1]))

    for _ in range(3):
        user_input = json.loads(input())

        for mine in list(copy_carte):
            if user_input["x"] == mine[0] and user_input["y"] == mine[1]:
                print("You found a mine !")
                nb_mine_found += 1
                copy_carte.remove(mine)


    print("The map was : ")
    print(f"Mine 1 : {carte[0][0]} {carte[0][1]}")
    print(f"Mine 2 : {carte[1][0]} {carte[1][1]}")
    print(f"Mine 3 : {carte[2][0]} {carte[2][1]}")

    if nb_mine_found == 3:
        result = True

    return result

def main():
    s1=4598
    s2=19635
    s3=5236

    prng = WichmannHill(s1,s2,s3)

    for _ in range(random.randrange(20_000, 30_000)):
        prng.generate_number()

    print("Hello, can you find all mines ? ")

    nb_victory = 0

    for i in range(5):
        print(f"Round number : {i+1}")

        try:
            result = play_round(prng)
        except Exception:
            print("Input error !")
            i -= 1
            result = False

        if result:
            nb_victory += 1

        if nb_victory == 3:
            print(f"Good job, here is your flag : {FLAG}")


if __name__ == "__main__":
    main()
