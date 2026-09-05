#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include "world/World.h"
TEST_CASE("World scalar field bilinear sample interpolates center") {
    ce::ScalarField f(2,2,100,100);
    f.setCell(0,0,0); f.setCell(1,0,1); f.setCell(0,1,1); f.setCell(1,1,0);
    REQUIRE(f.sample({50,50}) == Catch::Approx(0.5).margin(0.01));
}
TEST_CASE("World food consumption conserves mass and never goes negative") {
    ce::FoodField f(16,16,100,100);
    f.paintPatch({50,50},20,0.2f,1,1,0);
    const float before=f.sampleDensity({50,50});
    const float mass=f.totalMass();
    const float eaten=f.consume({50,50},1);
    REQUIRE(eaten <= before);
    REQUIRE(f.sampleDensity({50,50}) >= 0);
    REQUIRE(mass-f.totalMass() == Catch::Approx(eaten).margin(1e-5));
}
TEST_CASE("World pheromone decays and fields normalize positions") {
    ce::SimulationConfig c; ce::World w(c);
    w.depositPheromone({100,100},1);
    const float before=w.samplePheromone({100,100});
    w.update(0.02);
    REQUIRE(w.samplePheromone({100,100}) < before);
    w.setTemperatureLinear({1,0},10,30);
    REQUIRE(w.sampleTemperature({500,500}) == Catch::Approx(20));
    w.setOxygenUniform(0.4f);
    REQUIRE(w.sampleOxygen({-10,100}) == Catch::Approx(0.4));
    REQUIRE(w.normalizePosition({-10,1010}).x == Catch::Approx(990));
    REQUIRE(w.normalizePosition({-10,1010}).y == Catch::Approx(10));
}
TEST_CASE("World mechanical stimulus has local vibration and collision") {
    ce::SimulationConfig c; c.boundaryMode=ce::BoundaryMode::Closed; ce::World w(c);
    w.mechanical().addSource({{100,100},20,1,0.2f,1,0.2f});
    w.update(0.02);
    REQUIRE(w.sampleVibration({100,100}) > w.sampleVibration({500,500}));
    Vector2 p{-2,50}; REQUIRE(w.resolveCollision(p,1)); REQUIRE(p.x >= 1);
}
TEST_CASE("World vibration pulse decays after source stops") {
    ce::MechanicalEnvironment m;
    m.addSource({{0,0},10,1,0,1,0.1});
    m.update(0.02); const float peak=m.vibration({0,0});
    m.update(0.2); const float tail=m.vibration({0,0});
    REQUIRE(tail > 0);
    REQUIRE(tail < peak);
}
