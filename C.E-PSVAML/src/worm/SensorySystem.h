#pragma once
#include "worm/SensoryState.h"
namespace ce {
class World; class Body; class Physiology;
class SensorySystem {
public:
    SensoryState sample(const World&,const Body&,const Physiology&,float preferredTemperature,float preferredOxygen,float recentFoodMemory,double dt);
private:
    bool initialized_=false;
    float previousFood_=0,previousRepellent_=0,previousTemperature_=0;
};
}
