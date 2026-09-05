// simulation/SimulationConfig.h
#pragma once
#include <cstddef>
#include "core/Types.h"
namespace ce {
struct TimeProfile {
    double physiologyRateScale = 1.0;
    double developmentRateScale = 1.0;
    double reproductionRateScale = 1.0;
    double agingRateScale = 1.0;
    double larvalGrowingSeconds = 120.0;
    double moltSeconds = 12.0;
    double embryoSeconds = 60.0;
    double dauerIntegrationSeconds = 30.0;
    double dauerRecoverySeconds = 30.0;
};
struct MutationConfig {
    double parameterProbability = 0.02;
    double parameterSigma = 0.03;
    double neuralProbability = 0.02;
    double neuralSigma = 0.05;
};
struct SimulationConfig {
    int physicsHz = 50;
    double fixedDt = 0.02;
    int renderHz = 60;
    float worldWidth = 1000.0f;
    float worldHeight = 1000.0f;
    int fieldGridWidth = 128;
    int fieldGridHeight = 128;
    int bodySegments = 12;
    int physicsConstraintIterations = 4;
    int brainRecurrentNeurons = 12;
    int initialPopulation = 32;
    BoundaryMode boundaryMode = BoundaryMode::Toroidal;
    std::size_t maxPopulationSafety = 10000;
    TimeProfile time{};
    MutationConfig mutation{};
};
}
