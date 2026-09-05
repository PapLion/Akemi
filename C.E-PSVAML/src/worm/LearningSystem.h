#pragma once
#include "worm/SensoryState.h"
#include "core/Types.h"
#include <vector>
namespace ce {
class NervousSystem;
struct LearningParameters {
    float plasticityRate=0.001f,eligibilityDecay=0.98f,habituationRate=0.01f,habituationRecovery=0.001f,thermalLearningRate=0.0001f;
};
class LearningSystem {
public:
    LearningSystem(LearningParameters parameters,float initialPreferredTemperature);
    SensoryState modulate(const SensoryState& raw,double dt);
    void updateAfterConsequences(const SensoryState&,const ActionConsequences&,NervousSystem&,double dt);
    float preferredTemperature() const { return preferredTemperature_; }
    float recentFoodMemory() const { return foodMemory_; }
    float habituationLevel() const { return habituation_; }
    float lastInternalValence() const { return valence_; }
private:
    LearningParameters parameters_;
    float preferredTemperature_,foodMemory_=0,habituation_=0,valence_=0;
    std::vector<float> eligibility_;
};
}
