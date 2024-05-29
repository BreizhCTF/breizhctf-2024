data =[66, 91, 148, 210, 352, 375, 774, 406, 784, 711, 590, 1276, 1512, 1664, 1820, 1230, 1040, 2193, 2196, 1330, 2680, 2268, 1562, 3197, 1920, 2700, 3198, 3807, 3556, 3770, 4650]

res = ""

for i in range(len(data)):
    if i ==0:
        newValue = chr( data[i]  - i )
        res+=newValue
    else:
        newValue = chr(( data[i] // i ) - i )
        res += newValue

print(res)