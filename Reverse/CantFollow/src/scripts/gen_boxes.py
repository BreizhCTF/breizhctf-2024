import random

flag = b'BZHCTF{4_g00d_01d_w4y_t0_h1d3_c0ntr01_f10w}'

if __name__ == '__main__':
    box1 = []
    box2 = []
    box3 = []
    random.seed(621934)
    for c in flag:
        ran_i = random.randint(1, 256)
        box1.append(ran_i)
        box2.append(c * (ran_i ^ c))
        box3.append(c & ran_i)
    print(box1)
    print(box2)
    print(box3)
