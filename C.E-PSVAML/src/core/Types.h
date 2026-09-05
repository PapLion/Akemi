#pragma once
#include <cstdint>
namespace ce {
using EntityId = std::uint64_t;
enum class BoundaryMode { Toroidal, Closed };
enum class DeathCause { None, Mechanical, Starvation, Thermal, Toxicity, Aging };
enum class DevelopmentStage { L1, L2, L2d, Dauer, DauerRecovery, L3, L4, Adult };
enum class DevelopmentPhase { Growing, Lethargus };
struct InternalState {
    float energyDeficit = 0, stressLevel = 0, developmentContext = 0, recentFoodMemory = 0;
};
struct ActionConsequences {
    float foodIngested = 0, energyAbsorbed = 0, damageDelta = 0;
    float starvationDelta = 0, thermalStressDelta = 0, distanceMoved = 0;
};
}
