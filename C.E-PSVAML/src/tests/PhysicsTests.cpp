#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include <cmath>
#include "worm/Body.h"
#include "world/World.h"
TEST_CASE("Physics body constraints preserve segment lengths") {
    ce::SimulationConfig c; ce::World w(c); ce::Body b({100,100},12,{},4);
    ce::MotorCommand m; m.forwardDrive=1;
    for(int i=0;i<5000;++i){b.applyMotorCommand(m);b.updatePhysics(w,c.fixedDt);}
    for(float len:b.segmentLengths()) REQUIRE(len == Catch::Approx(5).margin(0.6));
}
TEST_CASE("Physics reverse drive reverses longitudinal displacement") {
    ce::SimulationConfig c; c.worldWidth=10000; c.worldHeight=10000; ce::World w(c); ce::Body f({5000,5000},12,{},4),r({5000,6000},12,{},4);
    const auto f0=f.midBodyPosition(),r0=r.midBodyPosition();
    ce::MotorCommand fm,rm; fm.forwardDrive=1; rm.reverseDrive=1;
    for(int i=0;i<2000;++i){ f.applyMotorCommand(fm);f.updatePhysics(w,c.fixedDt);r.applyMotorCommand(rm);r.updatePhysics(w,c.fixedDt); }
    REQUIRE(f.midBodyPosition().x-f0.x > 0); REQUIRE(r.midBodyPosition().x-r0.x < 0);
}
TEST_CASE("Physics strong turn reorients continuously and remains finite") {
    ce::SimulationConfig c; ce::World w(c); ce::Body b({400,400},12,{},4);
    ce::MotorCommand m; m.forwardDrive=0.5; m.turnBias=1;
    bool turned=false;
    for(int i=0;i<10000;++i){
        auto before=b.headPosition(); b.applyMotorCommand(m);b.updatePhysics(w,c.fixedDt);
        REQUIRE(std::hypot(b.headPosition().x-before.x,b.headPosition().y-before.y)<5);
        for(auto p:b.bodySegments()){ REQUIRE(std::isfinite(p.x));REQUIRE(std::isfinite(p.y)); }
        auto a=b.bodySegments().front(),z=b.bodySegments().back();
        if(std::abs(std::atan2(a.y-z.y,a.x-z.x))>0.5) turned=true;
    }
    REQUIRE(turned);
}
TEST_CASE("Physics no curvature means no artificial propulsion") {
    ce::SimulationConfig c; ce::World w(c); ce::BodyParameters p; p.baselineWaveAmplitude=0;
    ce::Body b({200,200},12,p,4); auto before=b.midBodyPosition(); ce::MotorCommand m;m.forwardDrive=1;
    for(int i=0;i<1000;++i){b.applyMotorCommand(m);b.updatePhysics(w,c.fixedDt);}
    REQUIRE(b.midBodyPosition().x == Catch::Approx(before.x).margin(0.001));
    REQUIRE(b.midBodyPosition().y == Catch::Approx(before.y).margin(0.001));
}
TEST_CASE("Physics toroidal crossing preserves rig and physical displacement") {
    ce::SimulationConfig c; ce::World w(c); ce::Body b({40,200},12,{},4);
    ce::MotorCommand m; m.reverseDrive=1; bool crossed=false;
    for(int i=0;i<2000;++i){
        const auto before=b.midBodyPosition(); b.applyMotorCommand(m);b.updatePhysics(w,c.fixedDt);
        if(b.midBodyPosition().x-before.x>500) crossed=true;
        REQUIRE(b.distanceMovedLastTick()<5);
        for(float len:b.segmentLengths()) REQUIRE(len==Catch::Approx(5).margin(0.6));
    }
    REQUIRE(crossed);
}
TEST_CASE("Physics internal constraints cannot propel without substrate anisotropy") {
    ce::SimulationConfig c;ce::World w(c);ce::BodyParameters p;p.longitudinalDrag=p.lateralDrag=0.85f;
    ce::Body b({400,400},12,p,4);auto start=b.midBodyPosition();ce::MotorCommand m;m.forwardDrive=1;
    for(int i=0;i<2000;++i){b.applyMotorCommand(m);b.updatePhysics(w,c.fixedDt);}
    REQUIRE(std::hypot(b.midBodyPosition().x-start.x,b.midBodyPosition().y-start.y)<0.5f);
}
