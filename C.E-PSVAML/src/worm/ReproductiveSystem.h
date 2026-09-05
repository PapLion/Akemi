#pragma once
#include "worm/Egg.h"
#include <vector>
namespace ce {
struct ReproductionInputs {
    bool isAdult=false;
    DevelopmentStage stage=DevelopmentStage::L1;
    float stageProgress=0;
    // An amount already transferred from Physiology during this tick, not a rate.
    float availableReproductiveResources=0,nutritionState=0,stressState=0;
    EntityId parentId=0;
    std::uint32_t generation=0;
    Vector2 position{};
};
class ReproductiveSystem {
public:
    ReproductiveSystem(ReproductionParameters parameters,const TimeProfile& time,
                       const Genome& genome=Genome::baseline(18,12,5));
    void initializeSpermReserve(int count);
    void update(const ReproductionInputs&,double dt,Random* rng=nullptr,const MutationConfig& mutation={});
    bool hasPendingEggs() const { return !pending_.empty(); }
    std::vector<EggBlueprint> takeLaidEggs();
    int spermRemaining() const { return sperm_; }
    std::size_t uterineEggCount() const { return uterine_.size(); }
    double reproductiveResources() const { return resources_; }
    double oocyteProgress() const { return oocyte_; }
private:
    struct HeldEgg { EggBlueprint blueprint; double holdingTime=0; };
    ReproductionParameters parameters_;
    TimeProfile time_;
    Genome genome_;
    int sperm_=0;
    bool spermInitialized_=false;
    double resources_=0,oocyte_=0;
    std::vector<HeldEgg> uterine_;
    std::vector<EggBlueprint> pending_;
};
}
