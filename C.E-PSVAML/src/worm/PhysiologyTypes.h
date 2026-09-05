#pragma once
#include "core/Types.h"
namespace ce {
struct DigestivePacket {
    float totalMass=0,energyPotential=0,lipidPotential=0,digestibility=1,toxicity=0;
    double transitRemaining=0;
};
struct PhysiologyParameters {
    float baseMetabolicRate=0.01f,digestiveEfficiency=0.8f,reserveStorageEfficiency=0.8f,reserveMobilizationEfficiency=0.7f;
    float starvationTolerance=1,thermalTolerance=1,gutCapacity=1,defecationPeriod=3;
    float agingHazardBase=0.0005f,agingHazardOnset=1500,agingHazardTimeScale=300;
    float transitDuration=2,pumpRate=0.2f,energyPerMass=6,reserveCapacity=2;
};
enum class DmpPhase { Rest, Posterior, Anterior, Expulsion };
}
