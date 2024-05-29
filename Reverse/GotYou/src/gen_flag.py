vals = [0, 0, 0, 0]

def unk_func1(val):
    vals[0] *= (val+1)*7
    vals[1] //= (val+1)
    vals[2] += val+3
    vals[3] += val+4
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

def unk_func2(val):
    vals[0] += val+8
    vals[1] += val+5
    vals[2] *= (val+1)*3
    vals[3] //= (val+1)
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

def unk_func3(val):
    vals[0] //= (val+1)
    vals[1] += val+1
    vals[2] += val+7
    vals[3] *= (val+1)*5
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

def unk_func4(val):
    vals[0] += val+2
    vals[1] *= (val+1)*9
    vals[2] //= (val+1)
    vals[3] += val+6
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

flag = '_ld_le4ds_ctr1_f10w_'
funcs_arr = [
    [3, unk_func1],
    [5, unk_func2],
    [6, unk_func3],
    [7, unk_func4],
]

for i in range(0, len(flag), 4):
    vals = [0, 0, 0, 0]
    for c in flag[i:i+4]:
        for func_pair in funcs_arr:
            func_idx, func = func_pair
            if func_idx != ord(c)>>4:
                func(ord(c)&0xF)
    print(vals)
