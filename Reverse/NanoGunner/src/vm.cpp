#include <cstdlib>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <algorithm>
#include <cmath>
#include "vm.h"

using namespace std;

uint8_t VM::signal_n = 0;
uint8_t VM::trigger_instr = 0;
bool VM::trigger = false;
sem_t VM::sem;
uint8_t VM::signals_mapping[16] = {2, 1, 15, 13, 10, 8, 5, 4, 7, 21, 11, 12, 6, 16, 14, 18};
uint8_t VM::triggers_mapping[16] = {0x8b, 0x6c, 0x51, 0x36, 0x39, 0x72, 0xf5, 0xbd, 0x55, 0x69, 0x10, 0x77, 0x01, 0x12, 0xac, 0x48};
uint8_t* VM::bytecode;
uint8_t VM::bytecode_len;

uint8_t VM::pc = 0;
float VM::regs[7];

void VM::mov_const_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = bytecode[pc+2];
    pc += 2;
}

void VM::mov_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7 && bytecode[pc+2] < 7) regs[bytecode[pc+1]] = regs[bytecode[pc+2]];
    pc += 2;
}

void VM::mov_gravity_instr() {
    if(pc + 1 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = 9.81f;
    pc++;
}

void VM::mov_pi_instr() {
    if(pc + 1 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = M_PI;
    pc++;
}

void VM::add_const_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] += (float)bytecode[pc+2];
    pc += 2;
}

void VM::sub_const_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] -= (float)bytecode[pc+2];
    pc += 2;
}

void VM::mul_const_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] *= (float)bytecode[pc+2];
    pc += 2;
}

void VM::div_const_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7 && bytecode[pc+2] != 0) regs[bytecode[pc+1]] /= (float)bytecode[pc+2];
    pc += 2;
}

void VM::add_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7 && bytecode[pc+2] < 7) regs[bytecode[pc+1]] += regs[bytecode[pc+2]];
    pc += 2;
}

void VM::sub_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7 && bytecode[pc+2] < 7) regs[bytecode[pc+1]] -= regs[bytecode[pc+2]];
    pc += 2;
}

void VM::mul_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7 && bytecode[pc+2] < 7) regs[bytecode[pc+1]] *= regs[bytecode[pc+2]];
    pc += 2;
}

void VM::div_instr() {
    if(pc + 2 < bytecode_len && bytecode[pc+1] < 7 && bytecode[pc+2] < 7 && regs[bytecode[pc+2]] != 0) regs[bytecode[pc+1]] /= regs[bytecode[pc+2]];
    pc += 2;
}

void VM::square_instr() {
    if(pc + 1 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = pow(regs[bytecode[pc+1]], 2);
    pc++;
}

void VM::sqrt_instr() {
    if(pc + 1 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = sqrt(regs[bytecode[pc+1]]);
    pc++;
}

void VM::cos_instr() {
    if(pc + 1 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = cos(regs[bytecode[pc+1]]);
    pc++;
}

void VM::sin_instr() {
    if(pc + 1 < bytecode_len && bytecode[pc+1] < 7) regs[bytecode[pc+1]] = sin(regs[bytecode[pc+1]]);
    pc++;
}

std::vector<InstrFunc> VM::instr_funcs = {
    VM::mov_const_instr,
    VM::mov_instr,
    VM::mov_gravity_instr,
    VM::mov_pi_instr,
    VM::add_const_instr,
    VM::sub_const_instr,
    VM::mul_const_instr,
    VM::div_const_instr,
    VM::add_instr,
    VM::sub_instr,
    VM::mul_instr,
    VM::div_instr,
    VM::square_instr,
    VM::sqrt_instr,
    VM::cos_instr,
    VM::sin_instr,
};

void VM::set_bytecode(uint8_t *bytecode, uint8_t bytecode_len) {
    VM::bytecode = bytecode;
    VM::bytecode_len = bytecode_len;
}

void VM::signal_handler(int signal) {
    if(signal == 18) signal = 9;
    if(signal == 21) signal = 3;
    signal--;
    instr_funcs[signal]();
    pc++;
    sem_post(&sem);
}

float VM::run(LAUNCH_PARAMS* params) {
    sem_init(&sem, 0, 0);
    pc = 0;
    trigger = false;
    regs[0] = 0;
    regs[1] = params->init_x;
    regs[2] = params->init_y;
    regs[3] = params->target_x;
    regs[4] = params->target_y;
    regs[5] = params->ke;
    regs[6] = params->angle;
    vector<pid_t> child_pids;
    for(uint8_t i = 0; i < instr_funcs.size(); i++) {
        pid_t child_pid = fork();
        if(!child_pid) {
            ptrace(PTRACE_TRACEME, NULL, NULL, NULL);
            signal_n = signals_mapping[i];
            trigger_instr = triggers_mapping[i];
            run_child();
            exit(0);
        } else child_pids.push_back(child_pid);
    }
    for(uint8_t i = 0; i < instr_funcs.size(); i++) signal(signals_mapping[i], signal_handler);
    int status;
    while(pc < bytecode_len) {
        if(find(begin(VM::triggers_mapping), end(VM::triggers_mapping), bytecode[pc]) != end(VM::triggers_mapping)) {
            for (pid_t child_pid : child_pids) {
                pid_t wait_ret = waitpid(child_pid, &status, WNOHANG);
                if (wait_ret == child_pid) {
                    if(WIFSTOPPED(status) && WSTOPSIG(status) == SIGTRAP) {
                        uint64_t pc_word = ptrace(PTRACE_PEEKDATA, child_pid, &pc, NULL);
                        pc_word = ((pc_word >> 8) << 8) | pc;
                        ptrace(PTRACE_POKEDATA, child_pid, &pc, pc_word);
                        ptrace(PTRACE_CONT, child_pid, NULL, NULL);
                        while (true) {
                            wait_ret = waitpid(child_pid, &status, WNOHANG);
                            if (wait_ret == child_pid) {
                                if(WIFSTOPPED(status) && WSTOPSIG(status) == SIGTRAP) break;
                                ptrace(PTRACE_CONT, child_pid, NULL, NULL);
                            }
                        }
                        trigger = ptrace(PTRACE_PEEKDATA, child_pid, &trigger, NULL) & 0x1;
                        if (trigger) {
                            signal_n = ptrace(PTRACE_PEEKDATA, child_pid, &signal_n, NULL) & 0xff;
                            kill(getpid(), signal_n);
                            sem_wait(&sem);
                            ptrace(PTRACE_CONT, child_pid, NULL, NULL);
                            break;
                        }
                    }
                    ptrace(PTRACE_CONT, child_pid, NULL, NULL);
                }
            }
        } else pc++;
    }
    sem_destroy(&sem);
    for(pid_t child_pid : child_pids) kill(child_pid, SIGKILL);
    return regs[0];
}

void VM::run_child() {
    while(true) {
        __asm__("int3");
        if(bytecode[pc] == trigger_instr) trigger = true;
        __asm__("int3");
        trigger = false;
    }
}