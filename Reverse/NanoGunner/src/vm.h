#ifndef NANOGUNNER_VM_H
#define NANOGUNNER_VM_H

#include <cstdint>
#include <vector>
#include <semaphore.h>

#define GRAVITY 9.81

using InstrFunc = void (*)();

struct LAUNCH_PARAMS {
    float init_x, init_y;
    float target_x, target_y;
    float ke;
    float mass;
    float angle;
};

class VM {
private:
    static uint8_t signal_n;
    static uint8_t trigger_instr;
    static bool trigger;
    static sem_t sem;
    static uint8_t pc;
    static uint8_t signals_mapping[16];
    static uint8_t triggers_mapping[16];
    static float regs[7];
    static uint8_t* bytecode;
    static uint8_t bytecode_len;
    static std::vector<InstrFunc> instr_funcs;
    static void mov_const_instr();
    static void mov_instr();
    static void mov_gravity_instr();
    static void mov_pi_instr();
    static void add_const_instr();
    static void sub_const_instr();
    static void mul_const_instr();
    static void div_const_instr();
    static void add_instr();
    static void sub_instr();
    static void mul_instr();
    static void div_instr();
    static void square_instr();
    static void sqrt_instr();
    static void cos_instr();
    static void sin_instr();
    static void signal_handler(int signal);
    void run_child();
public:
    void set_bytecode(uint8_t* bytecode, uint8_t bytecode_len);
    float run(LAUNCH_PARAMS* params);
};

#endif //NANOGUNNER_VM_H
