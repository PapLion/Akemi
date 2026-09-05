#include <catch2/catch_test_macros.hpp>
#include "simulation/Population.h"
#include "world/World.h"
TEST_CASE("Population hatch preserves identity generation provision and lineage after death") {
    ce::SimulationConfig cfg;ce::Population p(100);ce::World world(cfg);
    auto g=ce::Genome::baseline(18,12,5);auto parent=p.spawnWorm({{100,100},g,0,4},0,cfg);
    auto egg=p.addEgg({parent,5,g,{100,100},0.4f},1);
    ce::TimeProfile time;time.developmentRateScale=100;
    for(int i=0;i<1000&&!p.hasGenerationAtLeast(5);++i){p.advanceEggs(world,0.02,time);p.hatchReadyEggs(i+2,cfg);}
    REQUIRE(p.hasGenerationAtLeast(5));REQUIRE(p.eggs().empty());
    const auto& child=p.worms().back();REQUIRE(child.id()==egg);REQUIRE(child.parentId()==parent);REQUIRE(child.generation()==5);
    REQUIRE(child.getReadOnlyDebugState().energy+child.getReadOnlyDebugState().reserve<=0.4f);
    REQUIRE(p.lineageRecords().front().childIds.size()==1);
    world.setTemperatureUniform(100);ce::Random rng(1);
    for(int i=0;i<10000&&!p.worms().empty();++i){p.tickWorms(world,0.02,rng);p.removeDeadWorms(i+1000);}
    REQUIRE(p.worms().empty());REQUIRE(p.lineageRecords().size()==2);REQUIRE(p.lineageRecords().front().deathTick.has_value());
}
TEST_CASE("Population guard rejects excess without killing existing organism") {
    ce::SimulationConfig cfg;ce::Population p(1);ce::InitialWormBlueprint bp{{100,100},ce::Genome::baseline(18,12,5)};
    REQUIRE(p.spawnWorm(bp,0,cfg)!=0);REQUIRE(p.spawnWorm(bp,0,cfg)==0);
    REQUIRE(p.guardTriggered());REQUIRE(p.worms().size()==1);REQUIRE(p.worms().front().isAlive());
}
