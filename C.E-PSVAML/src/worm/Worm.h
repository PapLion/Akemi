#pragma once
#include "worm/ReproductiveSystem.h"
#include "worm/Physiology.h"
#include "worm/SensorySystem.h"
#include "worm/NervousSystem.h"
#include "worm/WormDebugState.h"
namespace ce {
class Worm {
public:
    Worm(EntityId id,EntityId parentId,std::uint32_t generation,std::uint64_t birthTick,
         Vector2 position,const Genome&,const SimulationConfig&,float maternalProvision=2,DevelopmentStage initialStage=DevelopmentStage::L1);
    void tick(World&,double dt,Random&);
    bool isAlive() const { return !physiology_.isDead(); }
    DeathCause deathCause() const { return physiology_.deathCause(); }
    std::vector<EggBlueprint> takePendingEggs() { return reproduction_.takeLaidEggs(); }
    WormDebugState getReadOnlyDebugState() const;
    EntityId id() const { return id_; }
    EntityId parentId() const { return parentId_; }
    std::uint32_t generation() const { return generation_; }
    const Genome& genome() const { return genome_; }
private:
    EntityId id_,parentId_;std::uint32_t generation_;std::uint64_t birthTick_;
    Genome genome_;SimulationConfig config_;
    Body body_;Physiology physiology_;SensorySystem sensory_;NervousSystem brain_;
    LearningSystem learning_;DevelopmentSystem development_;ReproductiveSystem reproduction_;
    SensoryState lastSensory_;MotorCommand lastMotor_;ActionConsequences lastConsequences_;
    float bodyScale_=0.4f;
};
}
