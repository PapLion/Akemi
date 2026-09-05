#pragma once
#include "simulation/Simulation.h"
namespace ce {
class Renderer {
public:
    explicit Renderer(const SimulationConfig& cfg):config_(cfg) {}
    void draw(const Simulation&);
private:
    SimulationConfig config_;
    int overlay_=0;
    EntityId selected_=0;
};
}
