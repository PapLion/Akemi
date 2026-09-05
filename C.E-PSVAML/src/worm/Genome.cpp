#include "worm/Genome.h"
#include "worm/NervousSystem.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace ce {
Genome Genome::baseline(int i,int n,int o) { Genome g;g.neural=NeuralParameters::baseline(i,n,o);g.sensorGains.fill(1);return g; }
bool Genome::validate() const {
    auto valid=[](float v,float lo,float hi){return std::isfinite(v)&&v>=lo&&v<=hi;};
    if(!valid(bodyStiffness,0.1f,1.0f))return false;
    if(!valid(structuralMassScale,0.5f,2.0f))return false;
    if(!valid(muscleStrength,0.2f,2.0f))return false;
    if(!valid(baselineWaveFrequency,0.2f,4.0f))return false;
    if(!valid(baselineWaveAmplitude,0.05f,0.7f))return false;
    if(!valid(baseMetabolicRate,0.001f,0.05f))return false;
    if(!valid(digestiveEfficiency,0.1f,1.0f))return false;
    if(!valid(reserveStorageEfficiency,0.1f,0.95f))return false;
    if(!valid(reserveMobilizationEfficiency,0.1f,0.95f))return false;
    if(!valid(starvationTolerance,0.2f,3.0f))return false;
    if(!valid(thermalTolerance,0.2f,3.0f))return false;
    if(!valid(agingHazardBase,0.00001f,0.01f))return false;
    if(!valid(agingHazardOnset,300.0f,3000.0f))return false;
    if(!valid(agingHazardTimeScale,100.0f,1000.0f))return false;
    if(!valid(plasticityRate,0.0f,0.01f))return false;
    if(!valid(eligibilityDecay,0.5f,0.995f))return false;
    if(!valid(habituationRate,0.0f,0.1f))return false;
    if(!valid(habituationRecovery,0.0f,0.01f))return false;
    if(!valid(thermalLearningRate,0.0f,0.01f))return false;
    if(!valid(developmentRateScaleGene,0.5f,2.0f))return false;
    if(!valid(dauerSensitivity,0.2f,3.0f))return false;
    if(!valid(stressDevelopmentPenalty,0.2f,2.0f))return false;
    if(!valid(reproductiveAllocation,0.01f,0.5f))return false;
    if(!valid(oocyteMaturationRate,0.2f,2.0f))return false;
    if(!valid(spermCapacityScale,0.2f,2.0f))return false;
    if(!valid(eggProvisionBias,0.5f,1.5f))return false;
    for(float gain:sensorGains)if(!valid(gain,0.1f,2.f))return false;
    for(float tau:neural.timeConstants)if(!valid(tau,0.04f,2.f))return false;
    try { NervousSystem check(neural); } catch(const std::invalid_argument&) { return false; }
    return true;
}
BodyParameters Genome::bodyParameters() const {
    BodyParameters p;
    p.stiffness=bodyStiffness;
    p.structuralMassScale=structuralMassScale;
    p.muscleStrength=muscleStrength;
    p.baselineWaveFrequency=baselineWaveFrequency;
    p.baselineWaveAmplitude=baselineWaveAmplitude;
    return p;
}
PhysiologyParameters Genome::physiologyParameters() const {
    PhysiologyParameters p;
    p.baseMetabolicRate=baseMetabolicRate;
    p.digestiveEfficiency=digestiveEfficiency;
    p.reserveStorageEfficiency=reserveStorageEfficiency;
    p.reserveMobilizationEfficiency=reserveMobilizationEfficiency;
    p.starvationTolerance=starvationTolerance;
    p.thermalTolerance=thermalTolerance;
    p.agingHazardBase=agingHazardBase;
    p.agingHazardOnset=agingHazardOnset;
    p.agingHazardTimeScale=agingHazardTimeScale;
    return p;
}
LearningParameters Genome::learningParameters() const {
    LearningParameters p;
    p.plasticityRate=plasticityRate;
    p.eligibilityDecay=eligibilityDecay;
    p.habituationRate=habituationRate;
    p.habituationRecovery=habituationRecovery;
    p.thermalLearningRate=thermalLearningRate;
    return p;
}
DevelopmentParameters Genome::developmentParameters() const {
    DevelopmentParameters p;
    p.individualRateScale=developmentRateScaleGene;
    p.dauerSensitivity=dauerSensitivity;
    p.stressDevelopmentPenalty=stressDevelopmentPenalty;
    return p;
}
ReproductionParameters Genome::reproductionParameters() const {
    ReproductionParameters p;
    p.reproductiveAllocation=reproductiveAllocation;
    p.oocyteMaturationRate=oocyteMaturationRate;
    p.spermCapacityScale=spermCapacityScale;
    p.eggProvisionBias=eggProvisionBias;
    return p;
}
NeuralParameters Genome::neuralParameters() const {
    auto p=neural;
    for(std::size_t i=0;i<p.inputWeights.size();++i)p.inputWeights[i]=std::clamp(p.inputWeights[i]*sensorGains[i%18],-8.f,8.f);
    return p;
}
bool Genome::operator==(const Genome& o) const {
    return bodyStiffness==o.bodyStiffness &&
        structuralMassScale==o.structuralMassScale &&
        muscleStrength==o.muscleStrength &&
        baselineWaveFrequency==o.baselineWaveFrequency &&
        baselineWaveAmplitude==o.baselineWaveAmplitude &&
        baseMetabolicRate==o.baseMetabolicRate &&
        digestiveEfficiency==o.digestiveEfficiency &&
        reserveStorageEfficiency==o.reserveStorageEfficiency &&
        reserveMobilizationEfficiency==o.reserveMobilizationEfficiency &&
        starvationTolerance==o.starvationTolerance &&
        thermalTolerance==o.thermalTolerance &&
        agingHazardBase==o.agingHazardBase &&
        agingHazardOnset==o.agingHazardOnset &&
        agingHazardTimeScale==o.agingHazardTimeScale &&
        plasticityRate==o.plasticityRate &&
        eligibilityDecay==o.eligibilityDecay &&
        habituationRate==o.habituationRate &&
        habituationRecovery==o.habituationRecovery &&
        thermalLearningRate==o.thermalLearningRate &&
        developmentRateScaleGene==o.developmentRateScaleGene &&
        dauerSensitivity==o.dauerSensitivity &&
        stressDevelopmentPenalty==o.stressDevelopmentPenalty &&
        reproductiveAllocation==o.reproductiveAllocation &&
        oocyteMaturationRate==o.oocyteMaturationRate &&
        spermCapacityScale==o.spermCapacityScale &&
        eggProvisionBias==o.eggProvisionBias &&
        sensorGains==o.sensorGains && neural.inputCount==o.neural.inputCount &&
        neural.recurrentCount==o.neural.recurrentCount && neural.outputCount==o.neural.outputCount &&
        neural.inputWeights==o.neural.inputWeights && neural.recurrentWeights==o.neural.recurrentWeights &&
        neural.outputWeights==o.neural.outputWeights && neural.biases==o.neural.biases && neural.timeConstants==o.neural.timeConstants;
}
Genome mutate(const Genome& parent,Random& rng,const MutationConfig& cfg) {
    if(!parent.validate())throw std::invalid_argument("invalid parent genome");
    if(!std::isfinite(cfg.parameterSigma)||cfg.parameterSigma<0||!std::isfinite(cfg.neuralSigma)||cfg.neuralSigma<0)
        throw std::invalid_argument("invalid mutation sigma");
    auto g=parent;
    auto change=[&](float& v,float lo,float hi,double probability,double sigma){
        if(rng.chance(probability)&&sigma>0)v=std::clamp(float(v+rng.normal(0,sigma)),lo,hi);
    };
    change(g.bodyStiffness,0.1f,1.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.structuralMassScale,0.5f,2.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.muscleStrength,0.2f,2.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.baselineWaveFrequency,0.2f,4.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.baselineWaveAmplitude,0.05f,0.7f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.baseMetabolicRate,0.001f,0.05f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.digestiveEfficiency,0.1f,1.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.reserveStorageEfficiency,0.1f,0.95f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.reserveMobilizationEfficiency,0.1f,0.95f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.starvationTolerance,0.2f,3.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.thermalTolerance,0.2f,3.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.agingHazardBase,0.00001f,0.01f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.agingHazardOnset,300.0f,3000.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.agingHazardTimeScale,100.0f,1000.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.plasticityRate,0.0f,0.01f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.eligibilityDecay,0.5f,0.995f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.habituationRate,0.0f,0.1f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.habituationRecovery,0.0f,0.01f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.thermalLearningRate,0.0f,0.01f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.developmentRateScaleGene,0.5f,2.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.dauerSensitivity,0.2f,3.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.stressDevelopmentPenalty,0.2f,2.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.reproductiveAllocation,0.01f,0.5f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.oocyteMaturationRate,0.2f,2.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.spermCapacityScale,0.2f,2.0f,cfg.parameterProbability,cfg.parameterSigma);
    change(g.eggProvisionBias,0.5f,1.5f,cfg.parameterProbability,cfg.parameterSigma);
    for(auto& gain:g.sensorGains)change(gain,0.1f,2.f,cfg.parameterProbability,cfg.parameterSigma);
    for(auto* weights:{&g.neural.inputWeights,&g.neural.recurrentWeights,&g.neural.outputWeights,&g.neural.biases})
        for(auto& w:*weights)change(w,-8.f,8.f,cfg.neuralProbability,cfg.neuralSigma);
    for(auto& tau:g.neural.timeConstants)change(tau,0.04f,2.f,cfg.parameterProbability,cfg.parameterSigma);
    return g;
}
}
