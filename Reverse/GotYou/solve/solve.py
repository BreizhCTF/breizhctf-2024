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

flag = ''
funcs_arr = [
    [3, unk_func1],
    [5, unk_func2],
    [6, unk_func3],
    [7, unk_func4],
]

funcs_idx = [0, 0, 0, 0]
vals_idx = [0, 0, 0, 0]

def increase_idx(idx):
    vals_idx[idx] += 1
    if vals_idx[idx] >= 0x10:
        vals_idx[idx] = 0
        funcs_idx[idx] += 1
        if funcs_idx[idx] >= 4:
            funcs_idx[idx] = 0
            increase_idx(idx+1)

expected_res = [[387488, 1844208, 13, 4661], [10448, 7463745, 1458, 28], [6190, 4218, 701, 4000], [3942, 47313, 63, 2027], [857, 3888, 46, 20741]]
flag_parts = ['']*5
ctr = 0
found_len = 0;
while found_len < 5:
    if (ctr % 0x10000) == 0:
        print(funcs_idx, vals_idx)
    ctr += 1
    vals = [0, 0, 0, 0]
    for i in range(4):
        val = vals_idx[i]
        for func_pair in funcs_arr:
            func_idx, func = func_pair
            if func_idx != funcs_arr[funcs_idx[i]][0]:
                func(val)
    if vals in expected_res:
        found_len += 1
        flag_idx = expected_res.index(vals)
        for i2 in range(4):
            flag_parts[flag_idx] += chr((funcs_arr[funcs_idx[i2]][0] << 4) | vals_idx[i2])
    increase_idx(0)

flag = 'BZHCTF{'+''.join(flag_parts)+'}'
print('Flag:',flag)
