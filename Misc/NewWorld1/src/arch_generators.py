from pwn import context, asm
from unicorn import (
    Uc,
    UC_ARCH_X86,
    UC_ARCH_ARM,
    UC_ARCH_ARM64,
    UC_MODE_32,
    UC_MODE_64,
    UC_MODE_ARM,
)
from unicorn import x86_const, arm_const, arm64_const
import secrets
import random


class x86:
    unicorn_uc = Uc(UC_ARCH_X86, UC_MODE_32)

    registers = [
        ("eax", x86_const.UC_X86_REG_EAX),
        ("ebx", x86_const.UC_X86_REG_EBX),
        ("ecx", x86_const.UC_X86_REG_ECX),
        ("edx", x86_const.UC_X86_REG_EDX),
    ]

    assembly_instructions = [
        ("add", 2),
        ("and", 2),
        ("or", 2),
        ("xor", 2),
        ("mov", 2),
        ("inc", 1),
    ]

    @classmethod
    def random_assembly(cls):
        code = []
        context.update({"os": "linux", "arch": "i386", "bits": 32})

        for reg in cls.registers:
            code.append(f"MOV {reg[0]}, {random.randint(2**10, 2**16)}")

        num_instructions = random.randint(12, 15)  # Random number of instructions
        for _ in range(num_instructions):
            instruction, parameters = secrets.choice(cls.assembly_instructions)
            registers = [secrets.choice(cls.registers)[0] for _ in range(parameters)]
            assembled_instruction = f"{instruction} {', '.join(registers)}"
            code.append(assembled_instruction)

        code = "\n".join(code)
        return asm(code)


class x64:
    unicorn_uc = Uc(UC_ARCH_X86, UC_MODE_64)
    registers = [
        ("rax", x86_const.UC_X86_REG_RAX),
        ("rbx", x86_const.UC_X86_REG_RBX),
        ("rcx", x86_const.UC_X86_REG_RCX),
        ("rdx", x86_const.UC_X86_REG_RDX),
    ]

    assembly_instructions = [
        ("add", 2),
        ("and", 2),
        ("or", 2),
        ("xor", 2),
        ("mov", 2),
        ("inc", 1),
    ]

    @classmethod
    def random_assembly(cls):
        code = []
        context.update({"os": "linux", "arch": "amd64", "bits": 64})

        for reg in cls.registers:
            code.append(f"MOV {reg[0]}, {random.randint(2**10, 2**16)}")

        num_instructions = random.randint(12, 15)
        for _ in range(num_instructions):
            instruction, parameters = secrets.choice(cls.assembly_instructions)
            registers = [secrets.choice(cls.registers)[0] for _ in range(parameters)]
            assembled_instruction = f"{instruction} {', '.join(registers)}"
            code.append(assembled_instruction)

        code = "\n".join(code)
        return asm(code)


class ARM32:
    unicorn_uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)

    registers = [
        ("r0", arm_const.UC_ARM_REG_R0),
        ("r1", arm_const.UC_ARM_REG_R1),
        ("r2", arm_const.UC_ARM_REG_R2),
        ("r3", arm_const.UC_ARM_REG_R3),
        ("r4", arm_const.UC_ARM_REG_R4),
        ("r5", arm_const.UC_ARM_REG_R5),
        ("r6", arm_const.UC_ARM_REG_R6),
    ]

    assembly_instructions = [
        ("add", 2),
        ("and", 2),
        ("orr", 2),
        ("eor", 2),
        ("mov", 2),
    ]

    @classmethod
    def random_assembly(cls):
        code = []
        context.update({"os": "linux", "arch": "arm", "bits": 32})

        for reg in cls.registers:
            code.append(f"mov {reg[0]}, #0x{random.randint(2**10, 2**16):X}")

        num_instructions = random.randint(12, 15)
        for _ in range(num_instructions):
            instruction, parameters = secrets.choice(cls.assembly_instructions)
            operands = [secrets.choice(cls.registers)[0] for _ in range(parameters)]
            assembled_instruction = f"{instruction} {', '.join(operands)}"
            code.append(assembled_instruction)

        code = "\n".join(code)
        return asm(code)


class AArch64:
    unicorn_uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

    registers = [
        ("x9", arm64_const.UC_ARM64_REG_X9),
        ("x10", arm64_const.UC_ARM64_REG_X10),
        ("x11", arm64_const.UC_ARM64_REG_X11),
        ("x12", arm64_const.UC_ARM64_REG_X12),
        ("x13", arm64_const.UC_ARM64_REG_X13),
        ("x14", arm64_const.UC_ARM64_REG_X14),
        ("x15", arm64_const.UC_ARM64_REG_X15),
    ]

    assembly_instructions = [
        ("add", 3),
        ("and", 3),
        ("orr", 3),
        ("eor", 3),
        ("mov", 2),
    ]

    @classmethod
    def random_assembly(cls):
        code = []
        context.update({"os": "linux", "arch": "aarch64", "bits": 64})

        for reg in cls.registers:
            code.append(f"mov {reg[0]}, #0x{random.randint(2**10, 2**16):X}")

        num_instructions = random.randint(12, 15)
        for _ in range(num_instructions):
            instruction, parameters = secrets.choice(cls.assembly_instructions)
            operands = [secrets.choice(cls.registers)[0] for _ in range(parameters)]
            assembled_instruction = f"{instruction} {', '.join(operands)}"
            code.append(assembled_instruction)

        code = "\n".join(code)
        return asm(code)
