#include <catch2/catch_test_macros.hpp>
#include "simulation/Scenario.h"
#include "simulation/Population.h"
#include "world/World.h"
TEST_CASE("Scenario all frozen V1 names initialize their required context") {
    ce::SimulationConfig cfg;
    REQUIRE(ce::Scenario::requiredV1Names().size()==11);
    for(const auto& name:ce::Scenario::requiredV1Names()) {
        INFO(name);ce::World world(cfg);ce::Population p(1000);ce::Random rng(123);
        REQUIRE(ce::Scenario::apply(name,world,p,rng,cfg));REQUIRE_FALSE(p.worms().empty());
        if(name=="reproduction_assay"){REQUIRE(p.worms().front().getReadOnlyDebugState().stage==ce::DevelopmentStage::Adult);REQUIRE(p.worms().front().getReadOnlyDebugState().sperm>0);}
        if(name=="dauer_recovery_assay")REQUIRE(p.worms().front().getReadOnlyDebugState().stage==ce::DevelopmentStage::Dauer);
    }
}
TEST_CASE("Scenario unknown name leaves world population and RNG unchanged") {
    ce::SimulationConfig cfg;ce::World world(cfg);ce::Population p(10);ce::Random rng(1),control(1);
    const auto mass=world.food().totalMass();
    REQUIRE_FALSE(ce::Scenario::apply("does_not_exist",world,p,rng,cfg));
    REQUIRE(world.food().totalMass()==mass);REQUIRE(p.worms().empty());REQUIRE(rng.uniform01()==control.uniform01());
}
