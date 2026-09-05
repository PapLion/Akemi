#include "simulation/Simulation.h"
#include "simulation/Scenario.h"
#include <cmath>
#include <stdexcept>
namespace ce {
Simulation::Simulation(SimulationConfig cfg,std::uint64_t seed,std::string scenario):config_(cfg),rng_(seed),world_(cfg),population_(cfg.maxPopulationSafety),scenario_(std::move(scenario)) {
    if(cfg.physicsHz<=0 || !std::isfinite(cfg.fixedDt) || std::abs(cfg.fixedDt-1.0/cfg.physicsHz)>1e-12 || cfg.fixedDt>0.04)
        throw std::invalid_argument("fixedDt must match physicsHz and remain stable for neural tau");
    if(!Scenario::apply(scenario_,world_,population_,rng_,config_))throw std::invalid_argument("unknown scenario");
    metrics_.sample(*this);
}
World& Simulation::worldForScenarioSetup() { if(tick_)throw std::logic_error("setup has ended");return world_; }
Population& Simulation::populationForScenarioSetup() { if(tick_)throw std::logic_error("setup has ended");return population_; }
void Simulation::tick() {
    if(population_.guardTriggered())throw std::runtime_error("population safety guard triggered");
    ++tick_;world_.update(config_.fixedDt);
    population_.tickWorms(world_,config_.fixedDt,rng_);
    population_.collectLaidEggs(tick_);
    population_.advanceEggs(world_,config_.fixedDt,config_.time);
    population_.hatchReadyEggs(tick_,config_);
    for(const auto& r:population_.lineageRecords())metrics_.recordBirth(r);
    for(const auto& worm:population_.worms())if(!worm.isAlive())metrics_.recordDeath(worm.getReadOnlyDebugState(),tick_,config_.fixedDt);
    population_.removeDeadWorms(tick_);
    metrics_.sample(*this);
}
void Simulation::runTicks(std::uint64_t count) { for(std::uint64_t i=0;i<count;++i)tick(); }
std::uint64_t Simulation::stateDigest() const {
    std::uint64_t hash=1469598103934665603ULL;
    const auto integer=[&](std::uint64_t v){for(int i=0;i<8;++i){hash^=(v>>(8*i))&255;hash*=1099511628211ULL;}};
    const auto number=[&](double v){if(!std::isfinite(v))throw std::runtime_error("nonfinite simulation state");integer(static_cast<std::uint64_t>(std::llround(v*1000000)));};
    integer(tick_);integer(population_.guardTriggered());
    for(float value:world_.food().density().values())number(value);
    for(int y=0;y<config_.fieldGridHeight;++y)for(int x=0;x<config_.fieldGridWidth;++x) {
        Vector2 p{(x+0.5f)*config_.worldWidth/config_.fieldGridWidth,(y+0.5f)*config_.worldHeight/config_.fieldGridHeight};
        number(world_.sampleFoodOdor(p));number(world_.sampleRepellent(p));number(world_.samplePheromone(p));number(world_.sampleTemperature(p));number(world_.sampleOxygen(p));
    }
    integer(population_.worms().size());
    for(const auto& worm:population_.worms()) {
        const auto s=worm.getReadOnlyDebugState();integer(s.id);integer(s.parentId);integer(s.generation);integer(static_cast<int>(s.stage));integer(static_cast<int>(s.phase));
        for(double v:{double(s.stageProgress),double(s.bodyScale),double(s.energy),double(s.reserve),double(s.gutLoad),double(s.waste),double(s.starvationStress),double(s.thermalStress),double(s.mechanicalDamage),double(s.toxicDamage),s.biologicalAge,double(s.habituation),double(s.foodMemory),double(s.preferredTemperature)})number(v);
        integer(s.sperm);integer(s.uterineEggs);
        for(auto p:s.segments){number(p.x);number(p.y);}for(float v:s.neuralStates)number(v);for(float v:s.effectiveInputWeights)number(v);
    }
    integer(population_.eggs().size());
    for(const auto& e:population_.eggs()){integer(e.id());integer(e.parentId());integer(e.generation());number(e.position().x);number(e.position().y);number(e.maternalProvision());number(e.embryoProgress());number(e.viabilityStress());number(e.age());}
    integer(population_.lineageRecords().size());
    for(const auto& r:population_.lineageRecords()){integer(r.id);integer(r.parentId);integer(r.generation);integer(r.birthTick);integer(r.deathTick.value_or(0));integer(static_cast<int>(r.deathCause));for(auto id:r.childIds)integer(id);}
    return hash;
}
}
