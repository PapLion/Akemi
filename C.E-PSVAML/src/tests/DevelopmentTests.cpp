#include <catch2/catch_test_macros.hpp>
#include "worm/DevelopmentSystem.h"
#include <vector>
TEST_CASE("Development normal cycle has L1 L2 L3 L4 Adult and four lethargus") {
    ce::TimeProfile t;t.developmentRateScale=100;ce::DevelopmentSystem d({},t);
    std::vector<ce::DevelopmentStage> stages{d.stage()};
    for(int i=0;i<200000&&d.stage()!=ce::DevelopmentStage::Adult;++i){d.update({},0.02);
        if(d.phase()==ce::DevelopmentPhase::Lethargus){REQUIRE_FALSE(d.pumpingAllowed());REQUIRE(d.locomotionMultiplier()<0.1f);}
        if(stages.back()!=d.stage())stages.push_back(d.stage());
        if(d.stage()==ce::DevelopmentStage::L4)REQUIRE_FALSE(d.isReproductivelyAdult());
    }
    REQUIRE(stages==std::vector<ce::DevelopmentStage>{ce::DevelopmentStage::L1,ce::DevelopmentStage::L2,ce::DevelopmentStage::L3,ce::DevelopmentStage::L4,ce::DevelopmentStage::Adult});
    REQUIRE(d.completedLethargusCount()==4);
}
TEST_CASE("Development Dauer is sustained larval pathway with recovery via L4") {
    ce::TimeProfile t;t.developmentRateScale=100;ce::DevelopmentSystem d({},t);ce::DevelopmentInputs bad;bad.foodAvailability=0;bad.dauerPheromone=1;bad.temperature=27;
    d.update(bad,0.02);REQUIRE(d.stage()==ce::DevelopmentStage::L1);bool l2d=false;
    for(int i=0;i<10000&&d.stage()!=ce::DevelopmentStage::Dauer;++i){d.update(bad,0.02);l2d|=d.stage()==ce::DevelopmentStage::L2d;}
    REQUIRE(l2d);REQUIRE(d.stage()==ce::DevelopmentStage::Dauer);REQUIRE_FALSE(d.pumpingAllowed());REQUIRE(d.metabolismMultiplier()<0.1f);
    d.update({},0.02);REQUIRE(d.stage()==ce::DevelopmentStage::Dauer);
    bool recovery=false,l4=false;
    for(int i=0;i<10000&&d.stage()!=ce::DevelopmentStage::Adult;++i){d.update({},0.02);recovery|=d.stage()==ce::DevelopmentStage::DauerRecovery;l4|=d.stage()==ce::DevelopmentStage::L4;}
    REQUIRE(recovery);REQUIRE(l4);REQUIRE(d.isReproductivelyAdult());
    for(int i=0;i<10000;++i)d.update(bad,0.02);REQUIRE(d.isReproductivelyAdult());
}
