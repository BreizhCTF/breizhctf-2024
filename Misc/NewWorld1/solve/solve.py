from sys import argv
from pwn import *
from unicorn import *
from unicorn import x86_const, arm_const, arm64_const
import re

EMU_ADDRESS = 0x1000000

# p = process(
#     ["/bin/python3", "server.py"],
#     stdout=PIPE,
# )

if len(argv) < 3:
    print('Usage: solve.py <host> <port> DEBUG')
    exit(1)

_, host, port = argv

p = remote(host, int(port))

p.recvuntil(b'Chaque valeur')
p.recvline()

while True:
    recved = p.recvline().decode()
    # Extract requested registers and ASM code
    try:
        round_num, registers, asm_code = re.findall(
            "\\[(\\d+)/\\d+\\].*des registres ([a-zA-z0-9,\\s]+) .*suivant : (\\S+)",
            recved,
        )[0]
    except:
        break

    # Remove "\x" and convert to raw bytes
    asm_code = bytes.fromhex(asm_code.replace("\\x", ""))

    # Convert registers to uppercase, as Unicorn variables are uppercase
    registers = [reg.upper() for reg in registers.split(", ")]

    # Detect architecture, and grab register names for later
    if registers[0].startswith("E"):
        unicorn_uc = Uc(UC_ARCH_X86, UC_MODE_32)
        registers_uc = [getattr(x86_const, f"UC_X86_REG_{reg}") for reg in registers]
    elif re.match("R[A-Z]+", registers[0]):
        unicorn_uc = Uc(UC_ARCH_X86, UC_MODE_64)
        registers_uc = [getattr(x86_const, f"UC_X86_REG_{reg}") for reg in registers]
    elif re.match("R[0-9]+", registers[0]):
        unicorn_uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        registers_uc = [getattr(arm_const, f"UC_ARM_REG_{reg}") for reg in registers]
    elif registers[0].startswith("X"):
        unicorn_uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        registers_uc = [
            getattr(arm64_const, f"UC_ARM64_REG_{reg}") for reg in registers
        ]
    else:
        print(f"Unknown arch, based on registers : {registers}")
        exit()

    # Initialize emulator in X86-32bit mode
    mu: Uc = unicorn_uc

    # map 2MB memory for this emulation
    mu.mem_map(EMU_ADDRESS, 2 * 1024 * 1024)

    # write machine code to be emulated to memory
    mu.mem_write(EMU_ADDRESS, asm_code)

    # emulate code in infinite time & unlimited instructions
    mu.emu_start(EMU_ADDRESS, EMU_ADDRESS + len(asm_code))

    solve_for_round = []
    for reg_uc in registers_uc:
        reg_value = mu.reg_read(reg_uc)
        solve_for_round.append(f"0X{reg_value:02X}")

    solve_for_round = ",".join(solve_for_round)
    print(f"Sending {solve_for_round} for round {round_num}")
    p.sendline(solve_for_round.encode())

    mu.mem_unmap(EMU_ADDRESS, 2 * 1024 * 1024)

print("Execution done. Got new message :")
print(recved)
p.close()
