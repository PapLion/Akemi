#pragma once
#include <raylib.h>
#include <vector>
namespace ce {
struct MechanicalStimulusSource {
    Vector2 position{};
    float radius=20,amplitude=1,damage=0;
    double period=1,duration=0.1;
};
struct Obstacle { Vector2 center{}; float radius=1; };
class MechanicalEnvironment {
public:
    void addSource(MechanicalStimulusSource source) { sources_.push_back(source); }
    void addObstacle(Obstacle obstacle) { obstacles_.push_back(obstacle); }
    void update(double dt) { time_+=dt; }
    float vibration(Vector2 p) const;
    float damage(Vector2 p) const;
    bool resolveCollision(Vector2& p,float radius) const;
private:
    double time_=0;
    std::vector<MechanicalStimulusSource> sources_;
    std::vector<Obstacle> obstacles_;
};
}
