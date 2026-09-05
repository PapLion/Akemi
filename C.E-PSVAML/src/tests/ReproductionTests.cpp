#include <catch2/catch_test_macros.hpp>
#include "worm/ReproductiveSystem.h"
TEST_CASE("Reproduction healthy adult consumes sperm holds and lays egg") {
    ce::ReproductiveSystem r({},{});r.initializeSpermReserve(2);ce::ReproductionInputs in;
    in.isAdult=true;in.availableReproductiveResources=1;in.nutritionState=1;
    bool held=false;
    for(int i=0;i<100000&&!r.hasPendingEggs();++i){r.update(in,0.02);held|=r.uterineEggCount()>0;}
    REQUIRE(held);REQUIRE(r.spermRemaining()<2);REQUIRE(r.takeLaidEggs().size()==1);
    std::size_t count=1;
    for(int i=0;i<10000;++i){r.update(in,0.02);count+=r.takeLaidEggs().size();}
    REQUIRE(count==2);REQUIRE(r.spermRemaining()==0);
}
TEST_CASE("Reproduction provisioning changes resources not genome") {
    auto parent=ce::Genome::baseline(18,12,5);
    auto lay=[&](float nutrition,float stress){ce::ReproductiveSystem r({}, {},parent);r.initializeSpermReserve(1);
        ce::ReproductionInputs in;in.isAdult=true;in.availableReproductiveResources=0.01f;in.nutritionState=nutrition;in.stressState=stress;
        for(int i=0;i<100000&&!r.hasPendingEggs();++i)r.update(in,0.02);
        auto eggs=r.takeLaidEggs();REQUIRE(eggs.size()==1);return eggs.front();};
    auto healthy=lay(1,0),stressed=lay(0.4f,0.3f);
    REQUIRE(healthy.maternalProvision>stressed.maternalProvision);REQUIRE(healthy.genome==parent);REQUIRE(stressed.genome==parent);
}
TEST_CASE("Reproduction only late L4 initializes sperm and viable egg hatches") {
    ce::ReproductiveSystem r({},{});ce::ReproductionInputs in;in.stage=ce::DevelopmentStage::L4;in.stageProgress=0.5f;
    r.update(in,0.02);REQUIRE(r.spermRemaining()==0);in.stageProgress=0.9f;r.update(in,0.02);REQUIRE(r.spermRemaining()>0);REQUIRE_FALSE(r.hasPendingEggs());
    ce::EggBlueprint bp{1,1,ce::Genome::baseline(18,12,5),{50,50},1};ce::Egg e(2,bp,0),bad(3,bp,0);
    ce::TimeProfile t;t.developmentRateScale=100;
    for(int i=0;i<1000;++i){e.updateEmbryogenesis(20,0.02,t);bad.updateEmbryogenesis(60,0.02,t);}
    REQUIRE(e.readyToHatch());REQUIRE_FALSE(bad.readyToHatch());REQUIRE_FALSE(bad.isViable());
}
