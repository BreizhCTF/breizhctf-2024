import angr
import claripy
import logging

logging.getLogger('angr').setLevel('ERROR')
bin_name = '../dist/DontBeAngry'

input_len = 8
base_addr = 0x0
win_addr = 0x16ca + base_addr
fail_addr = [0x16e0 + base_addr]
p = angr.Project(bin_name, main_opts={'base_addr': base_addr}, auto_load_libs=True)
flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(input_len)]
flag = claripy.Concat(*flag_chars)
entry_state = p.factory.entry_state(args=[bin_name], stdin=flag)
simgr = p.factory.simulation_manager(entry_state)
simgr.explore(find = win_addr, avoid = fail_addr)
if not len(simgr.found):
    print('Failure')
for win_state in simgr.found:
    flag_resolved = win_state.posix.dumps(0).decode()
    print(f'Password: {flag_resolved}')
    exit()
