f1 = open('rick_angr.bmp', 'rb')
data1 = f1.read()
f1.close()

f2 = open('flag.bmp', 'rb')
data2 = f2.read()
f2.close()

f_enc = open('flag.enc', 'wb')

pass_1 = 'C0ngRatz'
pass_2 = 'G00d_j0b'

input_i = 0

for i in range(len(data1)):
    f_enc.write(int.to_bytes(data1[i] ^ ord(pass_1[input_i]) ^ ord(pass_1[(input_i+1)%8]), 1, 'little'))
    f_enc.write(int.to_bytes(data2[i] ^ ord(pass_2[input_i]) ^ ord(pass_2[(input_i+1)%8]), 1, 'little'))
    input_i+=1
    if input_i == 8:
        input_i = 0
        
f_enc.close()
