#include "worm/SensorySystem.h"
#include "worm/Body.h"
#include "worm/Physiology.h"
#include "world/World.h"
#include <algorithm>
namespace ce {
SensoryState SensorySystem::sample(const World& w,const Body& b,const Physiology& p,float preferredTemperature,float preferredOxygen,float memory,double) {
    SensoryState s;auto head=b.headPosition();
    s.foodAttractant=w.sampleFoodOdor(head);s.repellent=w.sampleRepellent(head);s.temperature=w.sampleTemperature(head);
    if(initialized_){s.foodAttractantDelta=s.foodAttractant-previousFood_;s.repellentDelta=s.repellent-previousRepellent_;s.temperatureDelta=s.temperature-previousTemperature_;}
    initialized_=true;previousFood_=s.foodAttractant;previousRepellent_=s.repellent;previousTemperature_=s.temperature;
    // Physical temperature remains in degrees for acquired thermal memory; neural packing normalizes it.
    s.temperatureErrorToPreference=s.temperature-preferredTemperature;s.oxygen=w.sampleOxygen(head);s.oxygenErrorToPreference=s.oxygen-preferredOxygen;
    s.noseTouch=b.headTouch()?1:0;s.bodyTouch=b.bodyTouch()?1:0;s.vibration=w.sampleVibration(head);
    s.foodAtMouth=w.sampleFood(head);s.energyDeficit=p.summaryForBrain().energyDeficit;
    s.headCurvature=b.headCurvature();s.meanBodyCurvature=b.meanBodyCurvature();s.forwardSpeed=b.forwardSpeed();s.recentFoodMemory=memory;
    return s;
}
}
