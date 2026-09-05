#pragma once
#include "worm/Genome.h"
namespace ce {
struct EggBlueprint {
    EntityId parentId=0;
    std::uint32_t generation=0;
    Genome genome;
    Vector2 position{};
    float maternalProvision=0;
};
class Egg {
public:
    Egg(EntityId id,const EggBlueprint& blueprint,std::uint64_t laidTick);
    void updateEmbryogenesis(float temperature,double dt,const TimeProfile&);
    bool readyToHatch() const { return isViable() && progress_>=1; }
    bool isViable() const { return viabilityStress_<1; }
    EntityId id() const { return id_; }
    EntityId parentId() const { return blueprint_.parentId; }
    std::uint32_t generation() const { return blueprint_.generation; }
    const Genome& genome() const { return blueprint_.genome; }
    Vector2 position() const { return blueprint_.position; }
    float maternalProvision() const { return blueprint_.maternalProvision; }
    double embryoProgress() const { return progress_; }
    double age() const { return age_; }
    double viabilityStress() const { return viabilityStress_; }
    std::uint64_t laidTick() const { return laidTick_; }
private:
    EntityId id_;
    EggBlueprint blueprint_;
    std::uint64_t laidTick_;
    double progress_=0,age_=0,viabilityStress_=0;
};
}
