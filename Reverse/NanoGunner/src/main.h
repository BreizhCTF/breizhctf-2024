#ifndef NANOGUNNER_MAIN_H
#define NANOGUNNER_MAIN_H

class Projectile {
public:
    float x, y;
    float speed_x, speed_y;
    float size;
    Projectile(float x, float y, float size) : x(x), y(y), size(size) {};
};

class Target {
public:
    float x, y;
    float size;
    bool hit = false;
    Target(float x, float y, float size) : x(x), y(y), size(size) {};
    void check_collision(Projectile projectile);
};

#endif //NANOGUNNER_MAIN_H
