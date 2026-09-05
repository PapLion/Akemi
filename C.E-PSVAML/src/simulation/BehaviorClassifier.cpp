#include "simulation/BehaviorClassifier.h"
#include <cmath>
namespace ce {
std::string_view BehaviorClassifier::classify(const WormDebugState& s) {
    if(s.stage==DevelopmentStage::Dauer)return "dauer";
    if(s.motor.reverseDrive>s.motor.forwardDrive)return "reversal";
    if(std::abs(s.motor.turnBias)>0.4f)return "strong_turn";
    if((std::abs(s.speed)<0.05f || s.reversalRateEstimate+s.strongTurnRateEstimate>0.2f) && (s.motor.pumpDrive>0.2f || s.foodMemory>0.2f))return "dwelling";
    return "roaming";
}
}
