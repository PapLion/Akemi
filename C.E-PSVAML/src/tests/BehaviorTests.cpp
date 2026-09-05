#include <catch2/catch_test_macros.hpp>
#include "simulation/Simulation.h"
#include <algorithm>
#include <cmath>
#include <numeric>
TEST_CASE("Behavior chemotaxis improves gradient progress over mirrored controls") {
    ce::SimulationConfig cfg;cfg.fieldGridWidth=cfg.fieldGridHeight=16;
    std::vector<double> directed,controls;
    for(auto seed:{11,22,33})for(float sign:{-1.f,1.f}) {
        ce::Simulation sim(cfg,seed,"chemotaxis_assay"),flat(cfg,seed,"chemotaxis_assay");
        sim.worldForScenarioSetup().setFoodOdorLinear({sign,0},0,1);flat.worldForScenarioSetup().setFoodOdorLinear({1,0},0.5f,0.5f);
        sim.worldForScenarioSetup().food().paintPatch({500,500},2000,0,1,1,0);sim.worldForScenarioSetup().setFoodRegrowthRate(0);
        flat.worldForScenarioSetup().food().paintPatch({500,500},2000,0,1,1,0);flat.worldForScenarioSetup().setFoodRegrowthRate(0);
        sim.runTicks(2000);flat.runTicks(2000);
        REQUIRE_FALSE(sim.population().worms().empty());REQUIRE_FALSE(flat.population().worms().empty());
        directed.push_back(sign*(sim.population().worms().front().getReadOnlyDebugState().segments.front().x-500));
        controls.push_back(sign*(flat.population().worms().front().getReadOnlyDebugState().segments.front().x-500));
    }
    std::sort(controls.begin(),controls.end());const auto median=(controls[2]+controls[3])/2;
    const auto mean=std::accumulate(directed.begin(),directed.end(),0.0)/directed.size();
    INFO("directed="<<mean<<" control median="<<median);REQUIRE(mean>median+0.0001);
}
TEST_CASE("Behavior nose withdrawal habituates and actual damage restores response") {
    ce::SimulationConfig cfg;cfg.fieldGridWidth=cfg.fieldGridHeight=16;
    ce::World world(cfg);world.setFoodOdorLinear({1,0},0,0);
    world.mechanical().addSource({{500,500},2000,1,0,1,0.1});
    ce::Worm worm(1,0,0,0,{500,500},ce::Genome::baseline(18,12,5),cfg);ce::Random rng(1);
    double early=0,late=0,restored=0;
    for(int i=0;i<1000;++i){world.update(0.02);worm.tick(world,0.02,rng);if(i>=50&&i<150)early+=worm.getReadOnlyDebugState().motor.reverseDrive;if(i>=900)late+=worm.getReadOnlyDebugState().motor.reverseDrive;}
    world.mechanical().addSource({{500,500},2000,0,0.01f,1,1});
    for(int i=0;i<100;++i){world.update(0.02);worm.tick(world,0.02,rng);restored+=worm.getReadOnlyDebugState().motor.reverseDrive;}
    INFO(early<<" "<<late<<" "<<restored);REQUIRE(early>late);REQUIRE(restored>late);
    ce::Simulation touch(cfg,4,"nose_touch_assay"),control(cfg,4,"thermotaxis_assay");
    double touchResponse=0,controlResponse=0;
    for(int i=0;i<20;++i){touch.tick();control.tick();touchResponse+=touch.population().worms().front().getReadOnlyDebugState().motor.reverseDrive;controlResponse+=control.population().worms().front().getReadOnlyDebugState().motor.reverseDrive;}
    INFO("touch window="<<touchResponse<<" control="<<controlResponse);REQUIRE(touchResponse>controlResponse);
}
TEST_CASE("Behavior actual paired absorption changes learned weights and cue response only") {
    ce::SimulationConfig cfg;auto g=ce::Genome::baseline(18,12,5);ce::World fed(cfg),empty(cfg);
    fed.food().paintPatch({500,500},2000,1,1,1,0);fed.setFoodOdorLinear({1,0},0.5f,0.5f);empty.setFoodOdorLinear({1,0},0,0);
    ce::Worm paired(1,0,0,0,{500,500},g,cfg),unpaired(2,0,0,0,{500,500},g,cfg);ce::Random ra(1),rb(1);
    // Both receive actual food; only paired receives the chemical cue during absorption.
    ce::World controlFed=fed;controlFed.setFoodOdorLinear({1,0},0,0);
    for(int i=0;i<1500;++i){paired.tick(fed,0.02,ra);unpaired.tick(controlFed,0.02,rb);}
    empty.setFoodOdorLinear({1,0},0.5f,0.5f);
    for(int i=0;i<300;++i){paired.tick(empty,0.02,ra);unpaired.tick(empty,0.02,rb);}
    const auto p=paired.getReadOnlyDebugState(),u=unpaired.getReadOnlyDebugState();
    double pd=0,ud=0;const auto base=g.neuralParameters().inputWeights;
    for(std::size_t i=0;i<base.size();++i){pd+=std::abs(p.effectiveInputWeights[i]-base[i]);ud+=std::abs(u.effectiveInputWeights[i]-base[i]);}
    INFO(pd<<" "<<ud);REQUIRE(pd>ud);REQUIRE(std::abs(p.motor.forwardDrive-u.motor.forwardDrive)+std::abs(p.motor.turnBias-u.motor.turnBias)>0.000001);
    REQUIRE(paired.genome()==g);REQUIRE(unpaired.genome()==g);
}
TEST_CASE("Behavior favorable thermal feeding changes preference and oxygen changes motor output") {
    ce::SimulationConfig cfg;cfg.fieldGridWidth=cfg.fieldGridHeight=16;
    ce::Simulation fed(cfg,1,"thermotaxis_assay");fed.worldForScenarioSetup().setTemperatureUniform(24);fed.runTicks(3000);
    REQUIRE(fed.population().worms().front().getReadOnlyDebugState().preferredTemperature>20);
    ce::Simulation low(cfg,2,"aerotaxis_assay"),high(cfg,2,"aerotaxis_assay");
    low.worldForScenarioSetup().setOxygenUniform(0.2f);high.worldForScenarioSetup().setOxygenUniform(0.8f);low.runTicks(100);high.runTicks(100);
    const auto l=low.population().worms().front().getReadOnlyDebugState(),h=high.population().worms().front().getReadOnlyDebugState();
    REQUIRE(l.sensory.oxygenErrorToPreference*h.sensory.oxygenErrorToPreference<0);REQUIRE(l.motor.turnBias!=h.motor.turnBias);
}
