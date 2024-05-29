#include <gtkmm-3.0/gtkmm/drawingarea.h>
#include <gtkmm-3.0/gtkmm.h>
#include <cmath>
#include <thread>
#include <iomanip>
#include <iostream>
#include "main.h"
#include "vm.h"

using namespace std;

string double_to_string(double value, int precision) {
    std::ostringstream stream;
    stream << std::fixed << setprecision(precision) << value;
    return stream.str();
}

void Target::check_collision(Projectile projectile) {
    if((projectile.x-projectile.size/2 >= this->x-this->size/2 && projectile.y-projectile.size/2 >= this->y-this->size/2
    && projectile.x-projectile.size/2 <= this->x+this->size/2 && projectile.y-projectile.size/2 <= this->y+this->size/2)) this->hit = true;
    else this->hit = false;
}

class DrawArea : public Gtk::DrawingArea {
private:
    Projectile* projectile = nullptr;
    Target* target = nullptr;
    LAUNCH_PARAMS* params = nullptr;
    bool win = false;
public:
    void initLevel(Projectile* proj, Target* target, LAUNCH_PARAMS* params) {
        this->projectile = proj;
        this->target = target;
        this->params = params;
    }
    void winGame() {
        this->win = true;
    }
protected:
    bool on_draw(const Cairo::RefPtr<Cairo::Context>& cr) override {
        cr->set_source_rgb(0.0, 0.0, 0.0);
        cr->paint();

        if(this->win) {
            cr->set_source_rgb(0.0, 1.0, 0.0);
            cr->set_font_size(30);
            cr->select_font_face("Sans", Cairo::FONT_SLANT_NORMAL, Cairo::FONT_WEIGHT_NORMAL);
            cr->move_to(320, 300);
            cr->show_text("Good job !");
            cr->set_font_size(15);
            cr->move_to(300, 340);
            cr->show_text("The flag is in your shell ;)");
            this->queue_draw();
            return true;
        }

        if(this->projectile) {
            cr->set_source_rgb(1.0, 0.0, 0.0);
            cr->arc(this->projectile->x, 600-this->projectile->y, this->projectile->size, 0.0, 2.0 * M_PI);
            cr->fill();
        }

        if(this->target) {
            if(!target->hit) cr->set_source_rgb(0.0, 1.0, 0.0);
            else cr->set_source_rgb(1.0, 0.0, 0.0);
            cr->rectangle(target->x - target->size/2, 600 - target->y - target->size/2, target->size, target->size);
            cr->fill();
        }

        if(this->params) {
            cr->set_source_rgb(0.0, 1.0, 0.0);
            cr->set_font_size(12);
            cr->select_font_face("Sans", Cairo::FONT_SLANT_NORMAL, Cairo::FONT_WEIGHT_NORMAL);
            cr->move_to(1, 10);
            cr->show_text("Xi: "+double_to_string(params->init_x, 2)+"m, Yi: "+double_to_string(params->init_y, 2)+"m");
            cr->move_to(1, 28);
            cr->show_text("Xt: "+double_to_string(params->target_x, 2)+"m, Yt: "+double_to_string(params->target_y, 2)+"m");
            cr->move_to(1, 46);
            cr->show_text("Kinetic Energy: "+double_to_string(params->ke, 2)+"J");
            cr->move_to(1, 64);
            cr->show_text("Mass: "+double_to_string(params->mass, 2)+"kg");
            cr->move_to(1, 82);
            cr->show_text("Angle: "+double_to_string(params->angle, 2)+"°");
        }
        this->queue_draw();
        return true;
    }
};

struct THREAD_PKG {
    DrawArea* area;
    VM* vm;
};

void* logic_thread(void* arg) {
    THREAD_PKG* pkg = (THREAD_PKG*) arg;
    DrawArea* area = pkg->area;
    VM* vm = pkg->vm;

    vector<LAUNCH_PARAMS> lvl_params = {
    {
        10, 10,
        750, 10,
        50000,
        1,
        70
    },
    {
        30, 10,
        650, 10,
        10000,
        1,
        30
    },
    {
        10, 10,
        60, 10,
        100000,
        1,
        80
    },
    {
        100, 80,
        300, 80,
        100000,
        1,
        10
    },
    {
        10, 10,
        750, 10,
        1,
        1,
        87.5
    }
    };

    for(LAUNCH_PARAMS params : lvl_params) {
        cout << "Calculating mass..." << endl;
        params.mass = vm->run(&params);
        cout << "Mass: " << to_string(params.mass) << "kg" << endl;
        //5505023903016900100300bd0072005a10060012067703067705038b0005
        //params.mass = 2*params.ke/((params.target_x-params.init_x)*GRAVITY/sin(2*params.angle*M_PI/180.0));

        Projectile proj(params.init_x, params.init_y, 5);
        Target target(params.target_x, params.target_y, 10);

        area->initLevel(&proj, &target, &params);

        float rad_angle = params.angle * (M_PI / 180.0);
        float speed = sqrt(2 * params.ke / params.mass);

        proj.speed_x = speed * cos(rad_angle);
        proj.speed_y = speed * sin(rad_angle);

        this_thread::sleep_for(chrono::seconds(1));

        chrono::milliseconds start_time = chrono::duration_cast<chrono::milliseconds>(
                chrono::system_clock::now().time_since_epoch());
        while (true) {
            chrono::milliseconds current_time = chrono::duration_cast<chrono::milliseconds>(
                    chrono::system_clock::now().time_since_epoch());
            chrono::milliseconds elapsed_time = current_time - start_time;
            float time_val = elapsed_time.count() / 200.0;
            proj.x = params.init_x + proj.speed_x * time_val;
            proj.y = params.init_y + proj.speed_y * time_val - 0.5 * GRAVITY * pow(time_val, 2);
            target.check_collision(proj);
            if (target.hit) {
                cout << "Nice shot !" << endl;
                this_thread::sleep_for(chrono::seconds(1));
                break;
            } else if (proj.x - proj.size / 2 > 800 || proj.y + proj.size / 2 < 0) {
                cout << "Bad shot..." << endl;
                exit(0);
            }
            this_thread::sleep_for(chrono::milliseconds(1));
        }
    }
    area->winGame();
    printf("Computing flag...\n");
    //art1ll3ry_a1mb0t
    char flag[17] = "\x83\xa5\x4e\x55\x52\x93\xdc\x18\xc5\xcb\x3d\xa8\xa8\x60\xe7\xeb";
    for(uint8_t i = 0; i < 16*10; i++) {
        lvl_params[0].ke = (i+1)*10000;
        lvl_params[0].target_x = 10+i*1.61803398875;
        lvl_params[0].angle = (i % 88) + 1;
        uint8_t res = ((uint64_t)vm->run(&lvl_params[0])) & 0xFF;
        flag[i%16] ^= res;
    }
    printf("Well done ! Here is your flag : BZHCTF{%s}\n", flag);
    exit(0);
}

bool parse_input(uint8_t* input, uint8_t input_sz, uint8_t* parsed_input) {
    if(!input_sz || input_sz % 2) return false;
    bool first = true;
    uint8_t val;
    for(uint8_t i = 0; i < input_sz; i++) {
        uint8_t chr = input[i];
        uint8_t part;
        if(chr >= 0x30 && chr <= 0x39) part = chr-0x30;
        else if(chr >= 0x61 && chr <= 0x66) part = chr-0x61+0xa;
        else return false;
        if(first) val = part;
        else {
            val <<= 4;
            val |= part;
            parsed_input[i / 2] = val;
        }
        first = !first;
    }
    return true;
}

bool first_run = true;

int main(int argc, char *argv[]) {
    if(!first_run) return 0;
    first_run = false;

    VM vm;
    auto app = Gtk::Application::create(argc, argv);

    Gtk::Window window;
    window.set_default_size(800, 600);
    window.set_resizable(false);
    window.set_position(Gtk::WIN_POS_CENTER);

    DrawArea area;
    window.add(area);

    printf(" ------------ NanoGunner v18.3.71 ------------\n"
           "|                                             |\n"
           "|   Chose between a peanut and a cannonball   |\n"
           "|                 by HellCorp                 |\n"
           "|                                             |\n"
           " ---------------------------------------------\n\n");
    printf("Code: ");
    uint8_t input[100];
    if(!fgets((char*)input, sizeof(input), stdin)) {
        printf("Failure...\n");
        return 0;
    }
    uint8_t input_len = strlen((char*)input)-1;
    input[input_len] = 0;
    uint8_t* bytecode = (uint8_t*) malloc(input_len / 2);
    if(!parse_input(input, input_len, bytecode)) {
        printf("Failure...\n");
        return 0;
    }
    vm.set_bytecode(bytecode, input_len/2);

    THREAD_PKG pkg = {
        &area,
        &vm
    };

    pthread_t logic_t;
    pthread_create(&logic_t, NULL, logic_thread, &pkg);

    area.show();

    return app->run(window);
}
