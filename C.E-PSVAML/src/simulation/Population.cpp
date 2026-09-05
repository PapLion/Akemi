#include "simulation/Population.h"
#include "world/World.h"
#include <algorithm>
namespace ce {
bool Population::canCreate() { if(worms_.size()+eggs_.size()>=maximum_){guard_=true;return false;}return true; }
void Population::recordBirth(EntityId id,EntityId parent,std::uint32_t generation,std::uint64_t tick) {
    for(auto& record:lineage_)if(record.id==parent){record.childIds.push_back(id);break;}
    lineage_.push_back({id,parent,generation,tick,std::nullopt,DeathCause::None,{}});
}
EntityId Population::spawnWorm(const InitialWormBlueprint& bp,std::uint64_t tick,const SimulationConfig& cfg) {
    if(!canCreate())return 0;
    const auto id=nextId_++;worms_.emplace_back(id,bp.parentId,bp.generation,tick,bp.position,bp.genome,cfg,2,bp.stage);
    recordBirth(id,bp.parentId,bp.generation,tick);return id;
}
EntityId Population::addEgg(const EggBlueprint& bp,std::uint64_t tick) {
    if(!canCreate())return 0;const auto id=nextId_++;eggs_.emplace_back(id,bp,tick);return id;
}
void Population::tickWorms(World& world,double dt,Random& rng) { for(auto& worm:worms_)worm.tick(world,dt,rng); }
void Population::collectLaidEggs(std::uint64_t tick) { for(auto& worm:worms_)for(const auto& bp:worm.takePendingEggs())addEgg(bp,tick); }
void Population::advanceEggs(const World& world,double dt,const TimeProfile& time) {
    for(auto& egg:eggs_)egg.updateEmbryogenesis(world.sampleTemperature(egg.position()),dt,time);
    eggs_.erase(std::remove_if(eggs_.begin(),eggs_.end(),[](const Egg& e){return !e.isViable();}),eggs_.end());
}
void Population::hatchReadyEggs(std::uint64_t tick,const SimulationConfig& cfg) {
    for(auto it=eggs_.begin();it!=eggs_.end();) {
        if(!it->readyToHatch()){++it;continue;}
        // Hatching replaces an existing entity; it does not increase the safety count.
        worms_.emplace_back(it->id(),it->parentId(),it->generation(),tick,it->position(),it->genome(),cfg,it->maternalProvision());
        recordBirth(it->id(),it->parentId(),it->generation(),tick);it=eggs_.erase(it);
    }
}
void Population::removeDeadWorms(std::uint64_t tick) {
    for(const auto& worm:worms_)if(!worm.isAlive())for(auto& record:lineage_)if(record.id==worm.id()) {
        record.deathTick=tick;record.deathCause=worm.deathCause();break;
    }
    worms_.erase(std::remove_if(worms_.begin(),worms_.end(),[](const Worm& w){return !w.isAlive();}),worms_.end());
}
bool Population::hasGenerationAtLeast(std::uint32_t generation) const {
    return std::any_of(lineage_.begin(),lineage_.end(),[generation](const LineageRecord& r){return r.generation>=generation;});
}
}
