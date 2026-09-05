#include <catch2/catch_test_macros.hpp>
#include "simulation/Simulation.h"
#include "simulation/MetricsRecorder.h"
#include <fstream>
TEST_CASE("Metrics CSV headers cover frozen lifetime and population fields without mutating core") {
    ce::SimulationConfig cfg;ce::Simulation s(cfg,1,"starvation_assay");s.runTicks(100);
    const auto before=s.stateDigest();auto path=std::filesystem::temp_directory_path()/"ce_psvaml_metrics_test";
    s.metrics().flush(path);REQUIRE(s.stateDigest()==before);
    std::string line;std::ifstream individuals(path/"individuals.csv");std::getline(individuals,line);
    REQUIRE(line=="id,parentId,generation,birthTick,deathTick,deathCause,lifetime,foodConsumed,energyAbsorbed,distanceTraveled,reversalCount,strongTurnCount,timeDwellingEstimate,timeRoamingEstimate,timeInDauer,eggsLaid,eggsHatched,childrenIds,maxGenerationDescendantSeen");
    std::ifstream population(path/"population.csv");std::getline(population,line);
    REQUIRE(line=="tick,populationSize,eggCount,birthsPerWindow,deathsPerWindow,stageDistribution,meanEnergy,meanReserve,meanAge,dauerCount,lineageDiversity,traitMeans,traitVariance");
    REQUIRE(std::getline(population,line));REQUIRE_FALSE(line.empty());
    REQUIRE(std::filesystem::exists(path/"events.txt"));individuals.close();population.close();std::filesystem::remove_all(path);
}
