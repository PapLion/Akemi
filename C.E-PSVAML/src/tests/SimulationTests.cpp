#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include "simulation/Simulation.h"
TEST_CASE("Simulation fixed ticks and same seed replay across frame grouping") {
    ce::SimulationConfig cfg;ce::Simulation a(cfg,777,"baseline_ecosystem"),b(cfg,777,"baseline_ecosystem"),c(cfg,778,"baseline_ecosystem");
    a.runTicks(10000);
    for(int frame=0;frame<100;++frame){b.runTicks(100);const auto digest=b.stateDigest();REQUIRE(digest==b.stateDigest());}
    c.runTicks(10000);
    REQUIRE(a.currentTick()==10000);REQUIRE(a.simulatedPhysicsTime()==Catch::Approx(200));
    REQUIRE(a.stateDigest()==b.stateDigest());REQUIRE(a.stateDigest()!=c.stateDigest());
}
TEST_CASE("Simulation invalid timestep and late mutable setup are rejected") {
    ce::SimulationConfig cfg;cfg.fixedDt=0.1;REQUIRE_THROWS(ce::Simulation(cfg,1,"baseline_ecosystem"));
    cfg.fixedDt=0.02;ce::Simulation s(cfg,1,"starvation_assay");s.tick();REQUIRE_THROWS(s.worldForScenarioSetup());
}
