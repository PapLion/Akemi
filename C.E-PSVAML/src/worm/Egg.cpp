#include "worm/Egg.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace ce {
Egg::Egg(EntityId id,const EggBlueprint& bp,std::uint64_t tick):id_(id),blueprint_(bp),laidTick_(tick) {
    if(!bp.genome.validate() || !std::isfinite(bp.maternalProvision) || bp.maternalProvision<0)
        throw std::invalid_argument("invalid egg blueprint");
}
void Egg::updateEmbryogenesis(float temperature,double dt,const TimeProfile& time) {
    if(!isViable() || readyToHatch()) return;
    const double elapsed=dt*time.developmentRateScale;
    age_+=elapsed;
    const double provision=blueprint_.maternalProvision;
    const double thermalStress=std::max(0.0,std::abs(temperature-20.0)-10.0);
    viabilityStress_+=elapsed*(thermalStress*0.01+ (provision<=0?0.05:0))/(0.25+provision);
    if(isViable()) progress_+=elapsed/time.embryoSeconds * std::clamp(std::exp((temperature-20.0)*0.04),0.25,2.0)*std::clamp(provision,0.0,1.0);
}
}
