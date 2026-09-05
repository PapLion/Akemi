#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include "worm/SensorySystem.h"
#include "worm/Body.h"
#include "worm/Physiology.h"
#include "world/World.h"
TEST_CASE("Sensory attractant delta follows local temporal samples") {
    ce::SimulationConfig c;ce::World w(c);w.setFoodOdorLinear({1,0},0,1);
    ce::Physiology p({},c.time);ce::SensorySystem s;ce::Body a({100,100},12,{},4),b({120,100},12,{},4);
    s.sample(w,a,p,20,0.5f,0,0.02);auto second=s.sample(w,b,p,20,0.5f,0,0.02);
    REQUIRE(second.foodAttractantDelta>0);
    REQUIRE(s.sample(w,b,p,20,0.5f,0,0.02).foodAttractantDelta==0);
}
TEST_CASE("Sensory reports touch vibration proprioception and internal deficit") {
    ce::SimulationConfig c;c.boundaryMode=ce::BoundaryMode::Closed;ce::World w(c);
    ce::Body b({1001,100},12,{},4);b.updatePhysics(w,0.02);
    w.mechanical().addSource({b.headPosition(),20,1,0,1,0.1});w.update(0.02);
    ce::Physiology p({},{});p.setEnergyForTest(0.1f);ce::SensorySystem s;
    auto v=s.sample(w,b,p,20,0.5f,0.7f,0.02);
    REQUIRE(v.noseTouch>0);REQUIRE(v.vibration>0);REQUIRE(v.energyDeficit>0.8f);
    REQUIRE(v.headCurvature==Catch::Approx(b.headCurvature()));REQUIRE(v.recentFoodMemory==Catch::Approx(0.7));
    ce::Body tail({40,200},12,{},4);tail.updatePhysics(w,0.02);
    REQUIRE(s.sample(w,tail,p,20,0.5f,0,0.02).bodyTouch>0);
}
TEST_CASE("Sensory thermal and oxygen errors have correct sign") {
    ce::World w(ce::SimulationConfig{});ce::Body b({100,100},12,{},4);ce::Physiology p({},{});ce::SensorySystem s;
    w.setTemperatureUniform(24);w.setOxygenUniform(0.8f);
    auto a=s.sample(w,b,p,20,0.5f,0,0.02);REQUIRE(a.temperatureErrorToPreference>0);REQUIRE(a.oxygenErrorToPreference>0);
    w.setOxygenUniform(0.2f);REQUIRE(s.sample(w,b,p,20,0.5f,0,0.02).oxygenErrorToPreference<0);
}
