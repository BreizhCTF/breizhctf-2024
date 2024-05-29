from qiling import Qiling
from qiling.const import QL_INTERCEPT
from qiling.const import QL_VERBOSE
from qiling.utils import *
import sys
from pwn import *
import hashlib
import base64

def generate_random_name(length=12):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    random_name = ''.join(random.choice(characters) for _ in range(length))
    return random_name

output_prog = b""

def calculate_md5(input_bytes):
    md5_hash = hashlib.md5()
    md5_hash.update(input_bytes)
    md5_bytes = md5_hash.digest()
    return md5_bytes

def calculate_sha1(input_bytes):
    sha1_hash = hashlib.sha1()
    sha1_hash.update(input_bytes)
    sha1_bytes = sha1_hash.digest()
    return sha1_bytes

def calculate_sha256(input_bytes):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_bytes)
    sha256_bytes = sha256_hash.digest()
    return sha256_bytes

def custom_mmap(ql):
    #print("Map section")
    buf = ql.mem.map(0x13370000, 0x10000, info = "[memory]")
    return 0

def md5(ql, inp_buf, dest_buf):
    #print("MD5")
    len_inp = ql.arch.regs.rbx
    #print("Param : ",end="")
    #print(hex(inp_buf),hex(dest_buf),hex(len_inp))
    inp_read = ql.mem.read(inp_buf,len_inp)
    #print(inp_read)
    hash = calculate_md5(inp_read)
    #print(b"Hash result : "+hash)
    ql.mem.write(dest_buf,hash)
    #check = ql.mem.read(dest_buf,17)
    #print(check)
    return 0

def sha1(ql, inp_buf, dest_buf):
    #print("SHA1")
    len_inp = ql.arch.regs.rbx
    #print("Param : ",end="")
    #print(hex(inp_buf),hex(dest_buf),hex(len_inp))
    inp_read = ql.mem.read(inp_buf,len_inp)
    #print(inp_read)
    hash = calculate_sha1(inp_read)
    #print(b"Hash result : "+hash)
    ql.mem.write(dest_buf,hash)
    check = ql.mem.read(dest_buf,21)
    #print(check)
    return 0

def sha256(ql, inp_buf, dest_buf):
    #print("sha256")
    len_inp = ql.arch.regs.rbx
    #print("Param : ",end="")
    #print(hex(inp_buf),hex(dest_buf),hex(len_inp))
    inp_read = ql.mem.read(inp_buf,len_inp)
    #print(inp_read)
    hash = calculate_sha256(inp_read)
    #print(b"Hash result : "+hash)
    ql.mem.write(dest_buf,hash)
    check = ql.mem.read(dest_buf,33)
    #print(check)
    return 0

def custom_write(ql, inp_buf, len_inp):
    global output_prog
    #print("custom write")
    id_encodage = ql.arch.regs.rbx
    #print(hex(inp_buf),hex(len_inp),hex(id_encodage))
    inp_read = ql.mem.read(inp_buf,len_inp)

    match id_encodage:
        case 1:
            conv = base64.b64encode(inp_read)
        case 2:
            conv = base64.b32encode(inp_read)
        case 3:
            conv = base64.b16encode(inp_read)
        case 4:
            conv = base64.b85encode(inp_read)

    #print(inp_read)
    #print(conv)
    output_prog = conv

    return 0

def run_emulator(b64_content):
    #ql = Qiling([r'./bin'], r'./rootfs',verbose=QL_VERBOSE.DISASM)
    decode_bin = base64.b64decode(b64_content)
    filename = generate_random_name()
    f = open(f"/tmp/{filename}",'wb')
    f.write(decode_bin)
    f.close()
    
    ql = Qiling([f'/tmp/{filename}'], r'./rootfs',verbose=QL_VERBOSE.DISABLED)

    ql.os.set_syscall(31337, custom_mmap)
    ql.os.set_syscall(31338, md5)
    ql.os.set_syscall(31339, sha1)
    ql.os.set_syscall(31340, sha256)
    ql.os.set_syscall(31341, custom_write)

    ql.run()
    #print(output_prog)

    os.remove(f"/tmp/{filename}")
    return output_prog



