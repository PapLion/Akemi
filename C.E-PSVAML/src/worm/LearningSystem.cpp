#include "worm/LearningSystem.h"
#include "worm/NervousSystem.h"
#include <algorithm>
#include <cmath>
namespace ce {
LearningSystem::LearningSystem(LearningParameters p,float t):parameters_(p),preferredTemperature_(t){}
SensoryState LearningSystem::modulate(const SensoryState& raw,double) {
    auto s=raw;s.noseTouch*=1-habituation_;s.bodyTouch*=1-habituation_;s.vibration*=1-habituation_;s.recentFoodMemory=foodMemory_;return s;
}
void LearningSystem::updateAfterConsequences(const SensoryState& raw,const ActionConsequences& c,NervousSystem& brain,double dt) {
    const float ticks=float(dt/0.02);
    const float stimulus=std::max({raw.noseTouch,raw.bodyTouch,raw.vibration});
    if(c.damageDelta>0)habituation_*=0.2f;
    else habituation_+=parameters_.habituationRate*stimulus*ticks*(1-habituation_);
    habituation_=std::clamp(habituation_-parameters_.habituationRecovery*float(dt),0.f,0.95f);
    foodMemory_=std::clamp(foodMemory_*std::exp(-float(dt)/20)+c.foodIngested*10,0.f,1.f);
    valence_=std::clamp(c.energyAbsorbed*10-c.damageDelta*4-std::max(0.f,c.starvationDelta)*2-std::max(0.f,c.thermalStressDelta)*2,-1.f,1.f);
    auto& weights=brain.effectiveInputWeights();if(eligibility_.size()!=weights.size())eligibility_.assign(weights.size(),0);
    const auto& pre=brain.lastInputs();const auto& post=brain.activations();
    const float decay=std::pow(parameters_.eligibilityDecay,ticks);
    for(std::size_t j=0;j<post.size();++j)for(std::size_t k=0;k<pre.size();++k){
        // Chemical cue inputs only are plastic in V1; timing comes from actual neural activity.
        if(k>3)continue;auto i=j*pre.size()+k;
        eligibility_[i]=decay*eligibility_[i]+pre[k]*post[j]*ticks;
        weights[i]=std::clamp(weights[i]+parameters_.plasticityRate*valence_*eligibility_[i]*ticks,-8.f,8.f);
    }
    if(c.energyAbsorbed>0&&brain.lastInputs()[4]<0.2f&&c.damageDelta<=0&&c.thermalStressDelta<=0)
        preferredTemperature_+=(raw.temperature-preferredTemperature_)*(1-std::exp(-parameters_.thermalLearningRate*ticks*std::min(1.f,c.energyAbsorbed*10)));
}
}
