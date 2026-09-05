#pragma once
#include "worm/Body.h"
#include "worm/PhysiologyTypes.h"
#include "worm/NeuralParameters.h"
#include "worm/LearningSystem.h"
#include "worm/DevelopmentSystem.h"
#include "core/Random.h"
#include <array>
namespace ce {
struct ReproductionParameters { float reproductiveAllocation=0.2f,oocyteMaturationRate=1,spermCapacityScale=1,eggProvisionBias=1; };
class Genome {
public:
    static Genome baseline(int sensoryInputs,int recurrentNeurons,int outputs);
    bool validate() const;
    BodyParameters bodyParameters() const;
    PhysiologyParameters physiologyParameters() const;
    LearningParameters learningParameters() const;
    DevelopmentParameters developmentParameters() const;
    ReproductionParameters reproductionParameters() const;
    NeuralParameters neuralParameters() const;
    bool operator==(const Genome&) const;
    // Inherited traits only: no physiological stores, age, or learned state.
    float bodyStiffness=0.7f;
    float structuralMassScale=1.0f;
    float muscleStrength=1.0f;
    float baselineWaveFrequency=2.0f;
    float baselineWaveAmplitude=0.35f;
    float baseMetabolicRate=0.01f;
    float digestiveEfficiency=0.8f;
    float reserveStorageEfficiency=0.8f;
    float reserveMobilizationEfficiency=0.7f;
    float starvationTolerance=1.0f;
    float thermalTolerance=1.0f;
    float agingHazardBase=0.0005f;
    float agingHazardOnset=1500.0f;
    float agingHazardTimeScale=300.0f;
    float plasticityRate=0.001f;
    float eligibilityDecay=0.98f;
    float habituationRate=0.01f;
    float habituationRecovery=0.001f;
    float thermalLearningRate=0.0001f;
    float developmentRateScaleGene=1.0f;
    float dauerSensitivity=1.0f;
    float stressDevelopmentPenalty=1.0f;
    float reproductiveAllocation=0.2f;
    float oocyteMaturationRate=1.0f;
    float spermCapacityScale=1.0f;
    float eggProvisionBias=1.0f;
    std::array<float,18> sensorGains{};
    NeuralParameters neural;
};
Genome mutate(const Genome&,Random&,const MutationConfig&);
}
