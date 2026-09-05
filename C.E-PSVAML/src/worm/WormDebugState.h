#pragma once
#include "worm/PhysiologyTypes.h"
#include "worm/SensoryState.h"
#include "worm/MotorCommand.h"
#include <raylib.h>
#include <vector>
namespace ce {
struct WormDebugState {
    EntityId id=0,parentId=0;std::uint32_t generation=0;std::uint64_t birthTick=0;
    DevelopmentStage stage=DevelopmentStage::L1;DevelopmentPhase phase=DevelopmentPhase::Growing;
    float stageProgress=0,bodyScale=0.4f,energy=0,reserve=0,gutLoad=0,waste=0;
    float starvationStress=0,thermalStress=0,mechanicalDamage=0,toxicDamage=0;
    double biologicalAge=0;
    int sperm=0,molts=0;std::size_t uterineEggs=0;
    float preferredTemperature=20,habituation=0,foodMemory=0,lastLearningValence=0,neuralNorm=0,speed=0;
    DmpPhase dmpPhase=DmpPhase::Rest;
    DeathCause deathCause=DeathCause::None;
    ActionConsequences lastConsequences;
    SensoryState sensory;
    MotorCommand motor;
    std::vector<Vector2> segments;
    std::vector<float> effectiveInputWeights,neuralStates;
};
}
