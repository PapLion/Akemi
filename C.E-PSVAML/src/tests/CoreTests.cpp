#include <catch2/catch_test_macros.hpp>
#include "core/Random.h"
#include "simulation/SimulationConfig.h"

TEST_CASE("same seed produces identical random stream") {
    ce::Random a(42), b(42);
    for (int i = 0; i < 100; ++i) REQUIRE(a.uniform01() == b.uniform01());
}

TEST_CASE("V1 defaults match frozen spec") {
    ce::SimulationConfig c{};
    REQUIRE(c.physicsHz == 50);
    REQUIRE(c.fixedDt == 0.02);
    REQUIRE(c.worldWidth == 1000.0f);
    REQUIRE(c.worldHeight == 1000.0f);
    REQUIRE(c.fieldGridWidth == 128);
    REQUIRE(c.fieldGridHeight == 128);
    REQUIRE(c.bodySegments == 12);
    REQUIRE(c.physicsConstraintIterations == 4);
    REQUIRE(c.brainRecurrentNeurons == 12);
    REQUIRE(c.initialPopulation == 32);
    REQUIRE(c.boundaryMode == ce::BoundaryMode::Toroidal);
}

TEST_CASE("Core random distributions replay and probabilities clamp") {
    ce::Random a(9), b(9);
    for (int i = 0; i < 100; ++i) {
        const double u = a.uniform01();
        REQUIRE(u == b.uniform01());
        REQUIRE(u >= 0.0);
        REQUIRE(u < 1.0);
        REQUIRE(a.normal(2.0, 0.3) == b.normal(2.0, 0.3));
        REQUIRE_FALSE(a.chance(-1.0));
        REQUIRE_FALSE(b.chance(-1.0));
        REQUIRE(a.chance(2.0));
        REQUIRE(b.chance(2.0));
    }
}
TEST_CASE("Core slow rate scales do not change physics dt") {
    ce::SimulationConfig c{};
    c.time = {10, 100, 100, 10};
    REQUIRE(c.fixedDt == 0.02);
    REQUIRE(c.physicsHz == 50);
}
