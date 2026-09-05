#include "worm/DevelopmentSystem.h"
#include <algorithm>
#include <cmath>
namespace ce {
DevelopmentSystem::DevelopmentSystem(DevelopmentParameters p,const TimeProfile& t):parameters_(p),time_(t){}
void DevelopmentSystem::update(const DevelopmentInputs& in,double dt) {
    if(stage_==DevelopmentStage::Adult)return;
    const double elapsed=dt*time_.developmentRateScale*parameters_.individualRateScale;
    const bool favorable=in.foodAvailability>0.3f&&in.dauerPheromone<0.3f&&in.temperature>=15&&in.temperature<=25;
    if(stage_==DevelopmentStage::Dauer) {
        recoveryTime_=favorable?recoveryTime_+elapsed:0;
        if(recoveryTime_>=time_.dauerRecoverySeconds){stage_=DevelopmentStage::DauerRecovery;progress_=0;recoveryTime_=0;}
        return;
    }
    if(stage_==DevelopmentStage::L1||stage_==DevelopmentStage::L2) {
        const float cue=std::clamp((1-in.foodAvailability)*in.dauerPheromone*(1+std::max(0.f,in.temperature-20)*0.1f)*parameters_.dauerSensitivity,0.f,1.f);
        dauerSignal_+=(cue-dauerSignal_)*(1-std::exp(-float(elapsed/time_.dauerIntegrationSeconds)));
    }
    if(phase_==DevelopmentPhase::Lethargus) {
        moltTime_+=elapsed;if(moltTime_<time_.moltSeconds)return;
        ++molts_;moltTime_=0;phase_=DevelopmentPhase::Growing;progress_=0;
        switch(stage_) {
        case DevelopmentStage::L1:stage_=dauerSignal_>0.5f?DevelopmentStage::L2d:DevelopmentStage::L2;break;
        case DevelopmentStage::L2:stage_=dauerSignal_>0.5f?DevelopmentStage::L2d:DevelopmentStage::L3;break;
        case DevelopmentStage::L2d:stage_=DevelopmentStage::Dauer;break;
        case DevelopmentStage::L3:stage_=DevelopmentStage::L4;break;
        case DevelopmentStage::L4:stage_=DevelopmentStage::Adult;break;
        case DevelopmentStage::DauerRecovery:stage_=DevelopmentStage::L4;break;
        default:break;
        }
        return;
    }
    const float temperatureFactor=std::exp(std::clamp((in.temperature-20)*0.025f,-1.f,0.4f));
    const float nutrition=std::clamp(in.nutritionFactor,0.f,1.f);
    const float stress=std::clamp(1-in.stressFactor*parameters_.stressDevelopmentPenalty,0.f,1.f);
    progress_=std::min(1.f,progress_+float(elapsed/time_.larvalGrowingSeconds)*temperatureFactor*nutrition*stress);
    if(progress_>=1){phase_=DevelopmentPhase::Lethargus;moltTime_=0;}
}
bool DevelopmentSystem::pumpingAllowed() const {return stage_!=DevelopmentStage::Dauer&&phase_!=DevelopmentPhase::Lethargus;}
float DevelopmentSystem::locomotionMultiplier() const {return phase_==DevelopmentPhase::Lethargus?0.03f:(stage_==DevelopmentStage::Dauer?0.15f:1.f);}
float DevelopmentSystem::targetBodyScale() const {
    switch(stage_) {
    case DevelopmentStage::L1:return 0.4f+0.15f*progress_;
    case DevelopmentStage::L2:return 0.55f+0.15f*progress_;
    case DevelopmentStage::L3:return 0.7f+0.15f*progress_;
    case DevelopmentStage::L4:return 0.85f+0.15f*progress_;
    case DevelopmentStage::L2d:return 0.55f;
    case DevelopmentStage::Dauer:return 0.55f;
    case DevelopmentStage::DauerRecovery:return 0.55f+0.3f*progress_;
    case DevelopmentStage::Adult:return 1;
    }
    return 1;
}
}
