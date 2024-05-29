from rich import print
from Maze import move_right, move_down, move_up, move_left, check_solved
from Madness import get_flag
from Module import check

move_right()
move_down()
move_down()
move_down()
move_right()
move_right()
move_up()
move_up()
move_right()
move_right()
move_down()
move_down()
move_right()
move_right()
move_up()
move_up()
[move_right() for _ in range(6)]
move_down()
move_down()
move_down()
move_down()
move_down()
move_down()
move_left()
move_left()
move_left()
move_left()
move_down()
move_down()
move_down()
move_down()
move_left()
move_left()
move_down()
move_down()
move_right()
move_right()
move_right()
move_right()
move_right()
move_right()
move_right()

print(check("BZHCTF{S33!"))
print(data := check_solved())

key = data.split()[-1]

print(res := get_flag(bytes.fromhex(key)))

print("Flag: ", "BZHCTF{S33!" + res.split("! ")[-1])
