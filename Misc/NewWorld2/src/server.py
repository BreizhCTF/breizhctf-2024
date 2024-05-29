#!/usr/bin/env python3

from pwn import *
import random
import base64
import os
from emulator import *

context.arch = "amd64"
MAX_ITERATION = 10
context.log_level = 'error'

def timeout_input(text: str, result: list):
    result.append(input(text))

def generate_random_name(length=12):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    random_name = ''.join(random.choice(characters) for _ in range(length))
    return random_name

def generator_random_data(n):
    ret = """
mov rdx, 0x13370000
"""
    for i in range(n):
        rand_int = random.randint(0,0xffffffffffffffff)
        ret+=f"mov rsi, {hex(rand_int)}\n"
        ret+=f"mov qword ptr [rdx], rsi\n"
        ret+=f"add rdx, 0x8\n"

    return ret

def make_hashes(n):
    ret = """
mov rbx, 0x4
mov rsi, 0x13370000
add rsi, 0x5000
mov rdi, 0x13370000
"""
    hash_syscall_possibilities = [31338,31339,31340]

    for i in range(n):
        rand_int = random.randint(0,0xffffffffffffffff)
        hash_mode = random.choice(hash_syscall_possibilities)
        ret += f"mov rax, {str(hash_mode)}\nsyscall\nadd rsi, 0x4\n"
    
    #print(ret)
    return ret

def generate_bin():
    bin_name = generate_random_name()

    n = random.randint(50,100)
    assembly = asm(f"""
    mov rax, 31337
    syscall

    {generator_random_data(n)}
    {make_hashes(n)}

    mov rdi, 0x13375000
    mov rsi, 0x400
    mov rbx, {hex(random.randint(1,4))}
    mov rax, 31341
    syscall

    mov rax,60
    syscall
    """)
    
    elf = ELF.from_bytes(assembly).save(f"/tmp/{bin_name}")

    content = open(f"/tmp/{bin_name}","rb").read()
    b64_elf = base64.b64encode(content)

    os.remove(f"/tmp/{bin_name}")
    return b64_elf


def main():
    print("""
⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠤⠤⠀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀ ⠀⣀⣀⡠⠤⠔⠒⠂⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠁⠀⠒⠒⠠⠤⠤⣀⣀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⠤⠒⠒⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠒⠒⠤⠄⠲⠵⢦⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣄⢒⣉⢀⣀⡀⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠾⠁⠙⠒⢤⣄⡀⠠⣀⠀⠀⠒⠂⠤⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠒⠒⠠⠤⢀⣀⡀⠀⠈⠉⠉⠐⠒⠤⢄⣀⠀⠀⠀⠈⠣⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠫⡢⣀⠉⠒⢄⡀⠀⠀⠀⠉⠑⠂⠤⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠒⠢⠤⣀⡀⠀⠀⠀⠉⠒⠢⢄⡀⠈⢦⡀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡴⢵⠶⢊⡍⢉⠉⠉⠉⠉⠉⠈⠪⡑⠦⡀⠈⠑⠄⠀⠀⠀⠀⠀⠀⠈⠉⠒⠠⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠒⠤⢀⡀⠀⡠⠌⠉⠒⠬⣦⣀⠀
⠀⠀⠀⠀⠀⠈⢁⠴⢟⠿⣲⢿⣅⢒⠠⢄⡀⠀⠀⠈⠢⡈⠑⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠠⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⠏⠛⠧⣄⠀⠀⠀⠀⠉
⠀⠀⠀⠀⠀⣠⠋⢀⠈⠀⠉⠀⠹⡎⠳⡀⠘⠠⠀⠀⠀⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠦⣀⡀⠀⠀⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⡼⢛⠞⠫⣀⢀⡀⠀⠀⣿⠀⠘⣦⠀⠀⡀⠀⠀⡇⠀⠀⡴⠀⡠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠣⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠰⠿⢃⣀⣤⡞⢁⣼⠷⠀⠀⡇⠀⠀⡇⠀⢰⠃⠀⢠⠁⠀⡰⠁⡰⠁⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⠤⠔⠒⠒⠂⠀⠀⠀⠀⠉⠉⠉⠲⢦⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠳⣾⡿⣫⠞⡝⠀⢠⠄⢸⠃⠀⠀⡻⠀⠊⠀⢀⠎⠀⡰⠁⢰⠃⠀⠀⠀⠀⢀⡠⠔⠊⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⠦⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠑⠴⠁⡸⠁⠀⡜⢀⡟⠀⠀⠀⡇⠀⠀⡠⡋⠀⠰⢁⡠⡮⠀⠀⠀⣠⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⠃⠀⢰⠁⣼⠁⠀⠀⢰⠁⢀⡮⣊⠤⠒⠛⠓⠲⠀⠀⠀⠛⠻⢧⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⠎⠀⠀⡇⠀⡧⠀⠀⠀⡧⣶⠕⠫⠴⠒⠦⠀⠀⠒⠀⠀⠀⡠⠄⠀⠠⢭⡲⢤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢝⠢⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣸⠀⠀⠀⠀⠀⠱⣦⣤⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠁⠀⠀⠀⠀⠱⡀⠙⠚⢧⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⡈⠣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢱⠀⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠑⢧⣀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⣆⠀⠀⠈⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⢣⠀⠀⠀⠀⠀⢀⠣⣀⠀⠀⠀⠀⠙⢧⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢦⡀⠀⠀⠉⠢⢄⠀⠀⠀⠀⢸⠀⠀⠀⢠⠖⠉⡌⠁⠘⡏⡽⠚⠥⣲⡸⠀⠀⠉⠢⠀⠀⠀⠀⠈⠫⢄⣀⡀⠀⠀⡰⠁⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⡀⠀⠀⠀⠉⢇⠀⠀⢰⠁⣀⠴⡏⠀⠀⠈⠢⡀⠘⢧⡀⠀⠈⠈⢳⡦⣀⠀⠀⠀⢄⡀⠀⠀⠀⠉⠁⠘⠊⠁⠀⣠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠢⠤⢠⡬⠖⠁⣸⡋⢣⡄⠈⠓⠤⣀⣤⠒⡄⠀⠉⠒⠤⣀⣀⠑⢄⠉⠲⢄⡀⠈⠓⠤⠀⠀⠀⠀⠀⠄⣴⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠔⠋⠀⢤⡦⠚⢡⠎⠀⢀⡠⠔⠁⢀⡠⠃⠀⠀⠀⢀⠆⠀⢠⠃⠀⠀⠀⠈⠓⠦⠤⢀⣀⣀⡀⠤⠚⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⣤⡶⣶⠋⠁⡠⣶⢶⣝⠏⢀⠔⣡⢶⢲⠟⢖⣠⠒⠁⠀⠀⢀⣀⣤⣊⠀⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠉⠛⠹⠊⠉⠉⠘⠉⠻⠒⠒⠁⠀⠓⠓⠛⠃⠀⠁⠀⠀⠀⠀⠛⠗⠓⠿⠖⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
""")
    print("Pour chaque binaire donné, vous devez afficher sa sortie")
    
    for i in range(1, 1 + MAX_ITERATION):
        bin_b64 = generate_bin()
        challenge = f"[{i}/{MAX_ITERATION}] Voici l'ELF que vous devez émuler (à décoder au préalable en base64) :\n".encode()
        challenge += bin_b64
        challenge += b"\n----\n"
        challenge += b"Quelle est sa sortie ?\n"
        
        valid_string_for_round = run_emulator(bin_b64).decode()
        #print(valid_string_for_round)

        result = []
        worker_thread = threading.Thread(target=timeout_input, args=(challenge.decode(), result))
        worker_thread.start()
        worker_thread.join(timeout=6)

        if worker_thread.is_alive():
            exit("Temps écoulé !")

        if result[0].strip() in valid_string_for_round:
            continue
        else:
            print(f"Incorrect ! La réponse était : {valid_string_for_round}")
            break
    
    else:
        print("BZHCTF{r34dy_70_pwn_53cur3_w0rld!!}")

if __name__ == "__main__":
    main()