#pragma once
#include "simulation/Population.h"
#include "world/World.h"
#include "simulation/MetricsRecorder.h"
#include <string>
namespace ce {
class Simulation {
public:
    Simulation(SimulationConfig,std::uint64_t seed,std::string scenarioName);
    void tick();
    void runTicks(std::uint64_t count);
    std::uint64_t currentTick() const { return tick_; }
    double simulatedPhysicsTime() const { return tick_*config_.fixedDt; }
    std::uint64_t stateDigest() const;
    const World& world() const { return world_; }
    const Population& population() const { return population_; }
    const SimulationConfig& config() const { return config_; }
    const std::string& scenarioName() const { return scenario_; }
    std::uint64_t seed() const { return rng_.seed(); }
    const MetricsRecorder& metrics() const { return metrics_; }
    World& worldForScenarioSetup();
    Population& populationForScenarioSetup();
private:
    SimulationConfig config_;Random rng_;World world_;Population population_;
    std::string scenario_;std::uint64_t tick_=0;
    MetricsRecorder metrics_;
};
}
