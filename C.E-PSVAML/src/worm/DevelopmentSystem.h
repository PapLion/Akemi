#pragma once
#include "simulation/SimulationConfig.h"
namespace ce {
struct DevelopmentParameters {
    float individualRateScale=1,dauerSensitivity=1,stressDevelopmentPenalty=1;
};
struct DevelopmentInputs {
    float foodAvailability=1,dauerPheromone=0,temperature=20,nutritionFactor=1,stressFactor=0;
};
class DevelopmentSystem {
public:
    DevelopmentSystem(DevelopmentParameters parameters,const TimeProfile& time);
    void update(const DevelopmentInputs&,double dt);
    DevelopmentStage stage() const { return stage_; }
    DevelopmentPhase phase() const { return phase_; }
    float stageProgress() const { return progress_; }
    int completedLethargusCount() const { return molts_; }
    float targetBodyScale() const;
    float locomotionMultiplier() const;
    bool pumpingAllowed() const;
    float metabolismMultiplier() const { return stage_==DevelopmentStage::Dauer?0.03f:1.f; }
    float agingMultiplier() const { return stage_==DevelopmentStage::Dauer?0.01f:1.f; }
    float stressResistanceMultiplier() const { return stage_==DevelopmentStage::Dauer?5.f:1.f; }
    bool isReproductivelyAdult() const { return stage_==DevelopmentStage::Adult; }
private:
    DevelopmentParameters parameters_;
    TimeProfile time_;
    DevelopmentStage stage_=DevelopmentStage::L1;
    DevelopmentPhase phase_=DevelopmentPhase::Growing;
    float progress_=0,dauerSignal_=0;
    double moltTime_=0,recoveryTime_=0;
    int molts_=0;
};
}
