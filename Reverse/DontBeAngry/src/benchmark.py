import subprocess
import sys

for i in range(0x1000):
    command = ["./dont_be_angry"]

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    input_data = "G00d_j0b"
    process.stdin.write(input_data)

    output, error = process.communicate()

    if "Success !" not in output:
        print("Error...")
        print(output)
        sys.exit(1)
print("Success !")
