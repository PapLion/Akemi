#include <catch2/catch_test_macros.hpp>
#include "worm/Physiology.h"
#include "world/World.h"
TEST_CASE("Physiology pumping creates gut content before absorbed energy") {
    ce::SimulationConfig c;ce::World w(c);w.food().paintPatch({50,50},10,1,1,1,0);
    ce::Physiology p({},c.time);float e=p.availableEnergy();
    REQUIRE(p.tryPump(w,{50,50},0,c.fixedDt).foodIngested==0);
    REQUIRE(p.tryPump(w,{50,50},1,c.fixedDt).foodIngested>0);
    REQUIRE(p.gutLoad()>0);REQUIRE(p.availableEnergy()<=e);
    for(int i=0;i<200;++i)p.updateDigestion(c.fixedDt);
    REQUIRE(p.availableEnergy()>e);
}
TEST_CASE("Physiology starvation mobilizes reserve before severe stress") {
    ce::Physiology p({},{});p.setEnergyForTest(0.05f);p.setReserveForTest(1);
    ce::Random rng(7);const float before=p.lipidReserve();
    for(int i=0;i<500;++i)p.updateMetabolism(0,20,0.02,rng);
    REQUIRE(p.lipidReserve()<before);REQUIRE(p.starvationStress()<0.5f);
    for(int i=0;i<50000&&!p.isDead();++i)p.updateMetabolism(0,20,0.02,rng);
    REQUIRE(p.isDead());REQUIRE(p.deathCause()==ce::DeathCause::Starvation);
}
TEST_CASE("Physiology DMP expels waste through contractions") {
    ce::SimulationConfig c;ce::World w(c);w.food().paintPatch({50,50},10,1,1,0.5f,0);
    ce::Physiology p({},{});p.tryPump(w,{50,50},1,0.02);
    for(int i=0;i<200;++i)p.updateDigestion(0.02);
    const float waste=p.wasteLoad(); REQUIRE(waste>0);
    bool posterior=false,anterior=false;
    for(int i=0;i<160;++i){p.updateDefecation(0.02);posterior|=p.dmpPhase()==ce::DmpPhase::Posterior;anterior|=p.dmpPhase()==ce::DmpPhase::Anterior;}
    REQUIRE(posterior);REQUIRE(anterior);REQUIRE(p.wasteLoad()<waste);
}
TEST_CASE("Physiology mechanical damage has causal death") {
    ce::Physiology p({},{});p.applyMechanicalDamage(2);REQUIRE(p.isDead());REQUIRE(p.deathCause()==ce::DeathCause::Mechanical);
}
TEST_CASE("Physiology aging hazard replays seed without fixed death tick") {
    auto deathTick=[](unsigned seed){
        ce::PhysiologyParameters pars;pars.baseMetabolicRate=0;pars.agingHazardBase=0.5f;pars.agingHazardOnset=0;
        ce::Physiology p(pars,{});ce::Random rng(seed);int tick=0;
        while(!p.isDead()&&tick<10000){p.updateMetabolism(0,20,0.02,rng);++tick;}
        REQUIRE(p.deathCause()==ce::DeathCause::Aging);return tick;
    };
    REQUIRE(deathTick(1)==deathTick(1));REQUIRE(deathTick(1)!=deathTick(2));
}
