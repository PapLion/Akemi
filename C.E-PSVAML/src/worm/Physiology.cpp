#include "worm/Physiology.h"
#include "world/World.h"
#include <algorithm>
#include <cmath>
namespace ce {
Physiology::Physiology(PhysiologyParameters p,const TimeProfile& t):parameters_(p),time_(t){}
void Physiology::initializeProvision(float provision) { energy_=std::max(0.f,provision)*0.5f;reserve_=std::max(0.f,provision)*0.5f; }
float Physiology::allocateResources(float requested) {
    const float paid=std::min(std::max(0.f,requested),std::max(0.f,energy_-0.2f));energy_-=paid;return paid;
}
void Physiology::setDevelopmentEffects(float metabolism,float aging,float resistance) {
    metabolismMultiplier_=metabolism;agingMultiplier_=aging;resistanceMultiplier_=resistance;
}
float Physiology::gutLoad() const {float m=0;for(const auto& p:packets_)m+=p.totalMass;return m;}
ActionConsequences Physiology::tryPump(World& world,Vector2 mouth,float drive,double dt) {
    ActionConsequences result;
    if(isDead()||drive<=0||dt<=0)return result;
    auto p=world.normalizePosition(mouth);const auto& food=world.food();
    const float nutrition=food.sampleNutrition(p),dig=food.sampleDigestibility(p),tox=food.sampleToxicity(p);
    const float request=std::min(std::max(0.f,parameters_.gutCapacity-gutLoad()),parameters_.pumpRate*std::clamp(drive,0.f,1.f)*float(dt*time_.physiologyRateScale));
    const float mass=world.consumeFood(p,request);
    if(mass>0) {
        packets_.push_back({mass,mass*nutrition*parameters_.energyPerMass,mass*0.1f,dig,tox,parameters_.transitDuration});
        energy_=std::max(0.f,energy_-mass*0.02f);
        result.foodIngested=mass;consequences_.foodIngested+=mass;
    }
    return result;
}
void Physiology::updateDigestion(double dt) {
    if(isDead())return;
    const double elapsed=std::max(0.,dt*time_.physiologyRateScale);
    for(auto& p:packets_) {
        // Newly ingested food traverses an initial processing interval before absorption.
        const double before=p.transitRemaining;p.transitRemaining=std::max(0.,before-elapsed);
        const double absorbWindow=parameters_.transitDuration*0.95;
        const double activeBefore=std::min(before,absorbWindow),activeAfter=std::min(p.transitRemaining,absorbWindow);
        const float fraction=activeBefore>0?float((activeBefore-activeAfter)/activeBefore):0;
        const float mass=p.totalMass*fraction,absorbed=p.energyPotential*fraction*p.digestibility*parameters_.digestiveEfficiency;
        energy_+=absorbed;reserve_=std::min(parameters_.reserveCapacity,reserve_+p.lipidPotential*fraction*p.digestibility);
        const float toxin=mass*p.toxicity;toxicity_+=toxin;consequences_.damageDelta+=toxin;
        consequences_.energyAbsorbed+=absorbed;waste_+=mass*(1-p.digestibility*parameters_.digestiveEfficiency);
        p.totalMass-=mass;p.energyPotential*=1-fraction;p.lipidPotential*=1-fraction;
    }
    while(!packets_.empty()&&packets_.front().transitRemaining<=0){waste_+=packets_.front().totalMass;packets_.pop_front();}
    if(toxicity_>=1)death_=DeathCause::Toxicity;
}
void Physiology::updateMetabolism(float actionCost,float temperature,double dt,Random& rng) {
    if(isDead())return;
    const float elapsed=float(std::max(0.,dt*time_.physiologyRateScale));
    const float oldStarvation=starvation_,oldThermal=thermal_;
    const float factor=std::exp(std::clamp((temperature-20)*0.04f,-1.f,1.f));
    energy_-=elapsed*(parameters_.baseMetabolicRate*factor*metabolismMultiplier_+std::max(0.f,actionCost)+0.01f*(thermal_+starvation_)*metabolismMultiplier_);
    if(energy_<0.2f) {
        float mobilized=std::min(reserve_,std::max(0.f,(0.2f-energy_)/parameters_.reserveMobilizationEfficiency));
        reserve_-=mobilized;energy_+=mobilized*parameters_.reserveMobilizationEfficiency;
    }
    if(energy_>1) {
        float stored=std::min(energy_-1,(parameters_.reserveCapacity-reserve_)/parameters_.reserveStorageEfficiency);
        energy_-=stored;reserve_+=stored*parameters_.reserveStorageEfficiency;
    }
    if(energy_<=0&&reserve_<=0)starvation_+=elapsed*0.03f/(parameters_.starvationTolerance*resistanceMultiplier_);
    else starvation_=std::max(0.f,starvation_-elapsed*0.01f);
    energy_=std::max(0.f,energy_);
    const float thermalExcess=std::max(0.f,std::abs(temperature-20)-10);
    thermal_=std::max(0.f,thermal_+elapsed*(thermalExcess>0?thermalExcess*0.01f/(parameters_.thermalTolerance*resistanceMultiplier_):-0.01f));
    age_+=dt*time_.agingRateScale*agingMultiplier_;agingDamage_=float(age_/parameters_.agingHazardTimeScale)*0.001f;
    consequences_.starvationDelta+=starvation_-oldStarvation;consequences_.thermalStressDelta+=thermal_-oldThermal;
    if(starvation_>=1)death_=DeathCause::Starvation;
    else if(thermal_>=1)death_=DeathCause::Thermal;
    else {
        const double hazard=parameters_.agingHazardBase*std::exp(std::clamp((age_-parameters_.agingHazardOnset)/parameters_.agingHazardTimeScale,-30.,20.))*(1+thermal_+starvation_+mechanical_+agingDamage_);
        if(rng.chance(-std::expm1(-hazard*dt*time_.agingRateScale*agingMultiplier_)))death_=DeathCause::Aging;
    }
}
void Physiology::applyMechanicalDamage(float amount) {
    if(isDead())return;const float damage=std::max(0.f,amount)/resistanceMultiplier_;mechanical_+=damage;consequences_.damageDelta+=damage;
    if(mechanical_>=1)death_=DeathCause::Mechanical;
}
void Physiology::updateDefecation(double dt) {
    if(isDead()||parameters_.defecationPeriod<=0)return;
    const double previous=dmpTime_;dmpTime_+=dt*time_.physiologyRateScale;
    if(std::floor(previous/parameters_.defecationPeriod)!=std::floor(dmpTime_/parameters_.defecationPeriod))waste_*=0.1f;
}
DmpPhase Physiology::dmpPhase() const {
    float phase=float(std::fmod(dmpTime_,parameters_.defecationPeriod)/parameters_.defecationPeriod);
    if(phase>=0.94f)return DmpPhase::Anterior;
    if(phase>=0.88f)return DmpPhase::Posterior;
    if(phase<0.02f&&dmpTime_>0)return DmpPhase::Expulsion;
    return DmpPhase::Rest;
}
InternalState Physiology::summaryForBrain() const { return {std::clamp(1-energy_,0.f,1.f),std::clamp(starvation_+thermal_+mechanical_+toxicity_,0.f,1.f),0,0}; }
}
