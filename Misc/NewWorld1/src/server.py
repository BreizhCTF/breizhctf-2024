#!/usr/bin/env python3

from pwn import *
from unicorn import *
import arch_generators
import secrets
import threading

MAX_ITERATION = 15
EMU_ADDRESS = 0x1000000

ARCHS = [
    arch_generators.x86,
    arch_generators.x64,
    arch_generators.ARM32,
    arch_generators.AArch64,
]

BANNER = '''
\\.
 \\\\      .
  \\\\ _,.+;)_
  .\\\\;~%:88%%.
 (( a   `)9,8;%.
 /`   _) ' `9%%%?
(' .-' j    '8%%'
 `"+   |    .88%)+._____..,,_   ,+%$%.
       :.   d%9`             `-%*'"'~%$.
    ___(   (%C                 `.   68%%9
  ."        \\7                  ;  C8%%)`
  : ."-.__,'.____________..,`   L.  \\86' ,
  : L    : :            `  .'\\.   '.  %$9%)
  ;  -.  : |             \\  \\  "-._ `. `~"
   `. !  : |              )  >     ". ?
     `'  : |            .' .'       : |
         ; !          .' .'         : |
        ,' ;         ' .'           ; (
       .  (         j  (            `  \\
       """'          ""'             `"" mh
'''


def timeout_input(text: str, result: list):
    result.append(input(text))


def main():
    print(BANNER)
    print(
        "Chaque valeur de réponse doit être en hexadécimal (paddé sur deux caractères), et séparée par une virgule. Exemple : 0x00,0xAA,0x085F"
    )

    for i in range(1, 1 + MAX_ITERATION):
        arch = secrets.choice(ARCHS)
        random_assembly = arch.random_assembly()
        registers_to_check = random.sample(arch.registers, 3)
        try:
            # Initialize emulator in X86-32bit mode
            mu: Uc = arch.unicorn_uc

            # map 2MB memory for this emulation
            mu.mem_map(EMU_ADDRESS, 2 * 1024 * 1024)

            # write machine code to be emulated to memory
            mu.mem_write(EMU_ADDRESS, random_assembly)

            # emulate code in infinite time & unlimited instructions
            mu.emu_start(EMU_ADDRESS, EMU_ADDRESS + len(random_assembly))
            registers_values = []
            for plain_name, uc_name in registers_to_check:
                reg_value = mu.reg_read(uc_name)
                registers_values.append((plain_name, reg_value))
        except UcError as e:
            print("ERROR: %s" % e)
            exit()

        mu.mem_unmap(EMU_ADDRESS, 2 * 1024 * 1024)

        challenge = f"[{i}/{MAX_ITERATION}] Quelles sont les valeurs des registres {', '.join([reg[0] for reg in registers_to_check])} après exécution du code assembleur {arch.__name__} suivant : "
        challenge += "".join(f"\\x{byte:02x}" for byte in random_assembly)
        challenge += "\n"

        valid_string_for_round = ",".join(
            [f"0x{reg_value:02x}" for reg_name, reg_value in registers_values]
        )

        result = []
        worker_thread = threading.Thread(target=timeout_input, args=(challenge, result))
        worker_thread.start()
        worker_thread.join(timeout=4)

        if worker_thread.is_alive():
            exit("Temps écoulé !")

        if result[0].strip().lower() == valid_string_for_round:
            continue
        else:
            print(f"Incorrect ! La réponse était : {valid_string_for_round}")
            break

    else:
        print("BZHCTF{w3lc0me_to_the_new_w0rld_x-x-x-x}")


if __name__ == "__main__":
    main()
