#include "worm/ReproductiveSystem.h"
#include <algorithm>
namespace ce {
ReproductiveSystem::ReproductiveSystem(ReproductionParameters p,const TimeProfile& t,const Genome& g):parameters_(p),time_(t),genome_(g) {}
void ReproductiveSystem::initializeSpermReserve(int count) {
    if(!spermInitialized_) { sperm_=std::max(0,count);spermInitialized_=true; }
}
void ReproductiveSystem::update(const ReproductionInputs& in,double dt,Random* rng,const MutationConfig& mutation) {
    if(in.stage==DevelopmentStage::L4 && in.stageProgress>=0.75f)
        initializeSpermReserve(static_cast<int>(20*parameters_.spermCapacityScale));
    resources_+=std::max(0.f,in.availableReproductiveResources);
    if(!in.isAdult) return;
    const double elapsed=dt*time_.reproductionRateScale;
    const double condition=std::clamp(in.nutritionState,0.f,1.f)*(1-std::clamp(in.stressState,0.f,1.f));
    for(auto it=uterine_.begin();it!=uterine_.end();) {
        it->holdingTime+=elapsed*(0.1+0.9*condition);
        if(it->holdingTime>=5) { it->blueprint.position=in.position;pending_.push_back(it->blueprint);it=uterine_.erase(it); }
        else ++it;
    }
    if(sperm_<=0) return;
    oocyte_=std::min(1.0,oocyte_+elapsed/20*parameters_.oocyteMaturationRate*condition*std::min(1.0,resources_));
    if(oocyte_>=1 && resources_>=1) {
        const float provision=static_cast<float>(std::clamp(condition*parameters_.eggProvisionBias,0.0,1.0));
        EggBlueprint bp{in.parentId,in.generation+1,rng?mutate(genome_,*rng,mutation):genome_,in.position,provision};
        uterine_.push_back({bp,0});
        resources_-=1;oocyte_=0;--sperm_;
    }
}
std::vector<EggBlueprint> ReproductiveSystem::takeLaidEggs() {
    auto result=std::move(pending_);pending_.clear();return result;
}
}
