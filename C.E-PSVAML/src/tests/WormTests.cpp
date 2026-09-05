#include <catch2/catch_test_macros.hpp>
#include "worm/Worm.h"
#include "world/World.h"
TEST_CASE("Worm learning follows current absorption and preserves inherited genome") {
    ce::SimulationConfig cfg;auto g=ce::Genome::baseline(18,12,5);
    ce::Worm a(1,0,0,0,{500,500},g,cfg),b(2,0,0,0,{500,500},g,cfg);
    ce::World food(cfg),empty(cfg);food.food().paintPatch({500,500},1000,1,1,1,0);
    food.setFoodOdorLinear({1,0},0.5f,0.5f);empty.setFoodOdorLinear({1,0},0.5f,0.5f);
    ce::Random ra(1),rb(1);bool absorbed=false;
    for(int i=0;i<1000&&!absorbed;++i) {
        a.tick(food,cfg.fixedDt,ra);b.tick(empty,cfg.fixedDt,rb);
        auto state=a.getReadOnlyDebugState();
        if(state.lastConsequences.energyAbsorbed>0){REQUIRE(state.lastLearningValence>0);absorbed=true;}
    }
    REQUIRE(absorbed);REQUIRE(a.genome()==g);REQUIRE(b.genome()==g);
    REQUIRE(a.getReadOnlyDebugState().effectiveInputWeights!=b.getReadOnlyDebugState().effectiveInputWeights);
}
TEST_CASE("Worm offspring stores come from provisioning and growth consumes energy") {
    ce::SimulationConfig cfg;auto g=ce::Genome::baseline(18,12,5);
    ce::Worm poor(1,9,1,0,{500,500},g,cfg,0.2f),rich(2,9,1,0,{500,500},g,cfg,1.f);
    REQUIRE(poor.getReadOnlyDebugState().energy+poor.getReadOnlyDebugState().reserve<=0.2f);
    REQUIRE(rich.getReadOnlyDebugState().energy+rich.getReadOnlyDebugState().reserve<=1.f);
    ce::Physiology physiology(g.physiologyParameters(),cfg.time);
    const float before=physiology.availableEnergy();
    REQUIRE(physiology.allocateResources(0.1f)==0.1f);
    REQUIRE(physiology.availableEnergy()<before);
}
