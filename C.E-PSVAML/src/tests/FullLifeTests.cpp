#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include "simulation/Simulation.h"
#include <algorithm>
#include <set>
#include <iostream>
TEST_CASE("FullLife body mass includes structural reserves and actual gut content") {
    ce::SimulationConfig cfg;ce::Simulation sim(cfg,1,"reproduction_assay");sim.runTicks(50);
    const auto s=sim.population().worms().front().getReadOnlyDebugState();REQUIRE(s.gutLoad>0);
    REQUIRE(s.bodyMass>s.bodyScale*sim.population().worms().front().genome().structuralMassScale+s.reserve*0.1f);
    REQUIRE(s.bodyMass==Catch::Approx(s.bodyScale*sim.population().worms().front().genome().structuralMassScale+s.reserve*0.1f+s.gutLoad));
}
TEST_CASE("FullLife viable egg reaches all normal stages and four molts within calibrated time") {
    ce::SimulationConfig cfg;cfg.initialPopulation=0;cfg.fieldGridWidth=cfg.fieldGridHeight=16;
    ce::Simulation sim(cfg,424242,"baseline_ecosystem");sim.worldForScenarioSetup().food().paintPatch({500,500},2000,1,1,1,0);sim.worldForScenarioSetup().setFoodRegrowthRate(0.1f);
    sim.populationForScenarioSetup().addEgg({0,0,ce::Genome::baseline(18,12,5),{500,500},1},0);
    std::set<ce::DevelopmentStage> stages;std::uint64_t adultTick=0;int molts=0;
    for(int i=0;i<36001;++i){sim.tick();if(!sim.population().worms().empty()){auto s=sim.population().worms().front().getReadOnlyDebugState();stages.insert(s.stage);if(s.stage==ce::DevelopmentStage::Adult){adultTick=sim.currentTick();molts=s.molts;break;}}}
    std::cout<<"CALIBRATION egg_to_adult_ticks="<<adultTick<<'\n';INFO("adultTick="<<adultTick);REQUIRE(adultTick>=24000);REQUIRE(adultTick<=36000);REQUIRE(molts==4);
    for(auto stage:{ce::DevelopmentStage::L1,ce::DevelopmentStage::L2,ce::DevelopmentStage::L3,ce::DevelopmentStage::L4,ce::DevelopmentStage::Adult})REQUIRE(stages.count(stage)==1);
}
TEST_CASE("FullLife Dauer induction and recovery follow actual integrated developmental pathway") {
    ce::SimulationConfig cfg;cfg.fieldGridWidth=cfg.fieldGridHeight=16;
    ce::Simulation induction(cfg,3,"dauer_induction_assay");std::set<ce::DevelopmentStage> path;
    for(int i=0;i<36000&&!path.count(ce::DevelopmentStage::Dauer);++i){induction.tick();if(!induction.population().worms().empty())path.insert(induction.population().worms().front().getReadOnlyDebugState().stage);}
    REQUIRE(path.count(ce::DevelopmentStage::L2d)==1);REQUIRE(path.count(ce::DevelopmentStage::Dauer)==1);
    ce::Simulation recovery(cfg,3,"dauer_recovery_assay");path.clear();
    for(int i=0;i<36000&&!path.count(ce::DevelopmentStage::Adult);++i){recovery.tick();if(!recovery.population().worms().empty())path.insert(recovery.population().worms().front().getReadOnlyDebugState().stage);}
    REQUIRE(path.count(ce::DevelopmentStage::DauerRecovery)==1);REQUIRE(path.count(ce::DevelopmentStage::L4)==1);REQUIRE(path.count(ce::DevelopmentStage::Adult)==1);
}
TEST_CASE("FullLife viable lineage hatches a mutated child with overlapping generations") {
    ce::SimulationConfig cfg;cfg.fieldGridWidth=cfg.fieldGridHeight=16;cfg.time.developmentRateScale=100;cfg.time.reproductionRateScale=100;
    ce::Simulation sim(cfg,424242,"reproduction_assay");
    for(int i=0;i<250000&&!sim.population().hasGenerationAtLeast(1);++i)sim.tick();
    REQUIRE(sim.population().hasGenerationAtLeast(1));REQUIRE(sim.population().lineageRecords().size()>=2);REQUIRE(sim.population().worms().size()>=2);
    REQUIRE(sim.population().worms().back().genome().validate());REQUIRE_FALSE(sim.population().worms().back().genome()==sim.population().worms().front().genome());
}
TEST_CASE("FullLife differential reproduction arises from resources without score selection") {
    ce::SimulationConfig cfg;cfg.initialPopulation=0;cfg.fieldGridWidth=cfg.fieldGridHeight=32;cfg.time.developmentRateScale=100;cfg.time.reproductionRateScale=100;
    ce::Simulation sim(cfg,22,"baseline_ecosystem");auto& world=sim.worldForScenarioSetup();world.food().paintPatch({500,500},2000,0,1,1,0);world.setFoodRegrowthRate(0);
    world.food().paintPatch({200,200},150,1,1,1,0);auto g=ce::Genome::baseline(18,12,5);
    auto& population=sim.populationForScenarioSetup();auto a=population.spawnWorm({{200,200},g,0,0,ce::DevelopmentStage::Adult},0,cfg);auto b=population.spawnWorm({{800,800},g,0,0,ce::DevelopmentStage::Adult},0,cfg);
    sim.runTicks(3000);std::size_t ca=0,cb=0;for(const auto& r:sim.population().lineageRecords()){if(r.id==a)ca=r.childIds.size();if(r.id==b)cb=r.childIds.size();}
    INFO(ca<<" "<<cb);REQUIRE(ca>cb);
}
TEST_CASE("FullLife starvation chain and fed DMP remain causal") {
    ce::SimulationConfig cfg;ce::World empty(cfg),fed(cfg);fed.food().paintPatch({500,500},2000,1,1,0.5f,0);
    auto g=ce::Genome::baseline(18,12,5);ce::Worm starving(1,0,0,0,{500,500},g,cfg),eating(2,0,0,0,{500,500},g,cfg);ce::Random r(1),f(1);
    bool reserveUsed=false,stressed=false,wasteDropped=false;float previousWaste=0;int previousExpulsion=0,period=0;
    for(int i=1;i<20000;++i){starving.tick(empty,0.02,r);eating.tick(fed,0.02,f);auto s=starving.getReadOnlyDebugState(),e=eating.getReadOnlyDebugState();reserveUsed|=s.reserve<0.5f;stressed|=s.starvationStress>0;
        if(e.waste<previousWaste){wasteDropped=true;if(previousExpulsion)period=i-previousExpulsion;previousExpulsion=i;}previousWaste=e.waste;
        if(!starving.isAlive()&&wasteDropped)break;
    }
    std::cout<<"CALIBRATION fed_dmp_ticks="<<period<<'\n';REQUIRE(reserveUsed);REQUIRE(stressed);REQUIRE(starving.deathCause()==ce::DeathCause::Starvation);REQUIRE(wasteDropped);REQUIRE(period>=100);REQUIRE(period<=200);
}
TEST_CASE("FullLife calibrated fed adult median lifetime stays in engineering range") {
    ce::SimulationConfig cfg;cfg.fieldGridWidth=cfg.fieldGridHeight=16;std::vector<int> lives;
    for(auto seed:{11,22,33,44,55}) {
        ce::World world(cfg);world.food().paintPatch({500,500},2000,1,1,1,0);
        ce::Worm worm(1,0,0,0,{500,500},ce::Genome::baseline(18,12,5),cfg,2,ce::DevelopmentStage::Adult);ce::Random rng(seed);
        int ticks=0;for(;ticks<150000&&worm.isAlive();++ticks){if(ticks%100==0)world.food().paintPatch({500,500},2000,1,1,1,0);worm.tick(world,0.02,rng);worm.takePendingEggs();}
        REQUIRE(worm.deathCause()==ce::DeathCause::Aging);lives.push_back(ticks);
    }
    std::sort(lives.begin(),lives.end());std::cout<<"CALIBRATION adult_median_ticks="<<lives[2]<<'\n';INFO("adult median="<<lives[2]);REQUIRE(lives[2]>=60000);REQUIRE(lives[2]<=90000);
}
