#pragma once
#include "worm/Worm.h"
#include "simulation/LineageRecord.h"
namespace ce {
struct InitialWormBlueprint { Vector2 position{};Genome genome;EntityId parentId=0;std::uint32_t generation=0;DevelopmentStage stage=DevelopmentStage::L1; };
class Population {
public:
    explicit Population(std::size_t maximum):maximum_(maximum) {}
    EntityId spawnWorm(const InitialWormBlueprint&,std::uint64_t birthTick,const SimulationConfig&);
    EntityId addEgg(const EggBlueprint&,std::uint64_t laidTick);
    void tickWorms(World&,double dt,Random&);
    void collectLaidEggs(std::uint64_t tick);
    void advanceEggs(const World&,double dt,const TimeProfile&);
    void hatchReadyEggs(std::uint64_t tick,const SimulationConfig&);
    void removeDeadWorms(std::uint64_t tick);
    bool guardTriggered() const { return guard_; }
    const std::vector<Worm>& worms() const { return worms_; }
    const std::vector<Egg>& eggs() const { return eggs_; }
    const std::vector<LineageRecord>& lineageRecords() const { return lineage_; }
    bool hasGenerationAtLeast(std::uint32_t) const;
private:
    bool canCreate();
    void recordBirth(EntityId,EntityId,std::uint32_t,std::uint64_t);
    std::size_t maximum_;
    EntityId nextId_=1;
    bool guard_=false;
    std::vector<Worm> worms_;
    std::vector<Egg> eggs_;
    std::vector<LineageRecord> lineage_;
};
}
