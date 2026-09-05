#pragma once
#include "worm/PhysiologyTypes.h"
#include "simulation/SimulationConfig.h"
#include "core/Random.h"
#include <raylib.h>
#include <deque>
namespace ce {
class World;
class Physiology {
public:
    Physiology(PhysiologyParameters parameters,const TimeProfile& time);
    ActionConsequences tryPump(World&,Vector2 mouth,float drive,double dt);
    void updateDigestion(double dt);
    void updateMetabolism(float actionCost,float temperature,double dt,Random& rng);
    void updateDefecation(double dt);
    void applyMechanicalDamage(float amount);
    InternalState summaryForBrain() const;
    ActionConsequences consequencesForLearning() const { return consequences_; }
    void beginTick() { consequences_={}; }
    bool isDead() const { return death_!=DeathCause::None; }
    DeathCause deathCause() const { return death_; }
    float availableEnergy() const { return energy_; }
    float lipidReserve() const { return reserve_; }
    float gutLoad() const;
    float wasteLoad() const { return waste_; }
    float starvationStress() const { return starvation_; }
    float thermalStress() const { return thermal_; }
    float mechanicalDamage() const { return mechanical_; }
    float toxicDamage() const { return toxicity_; }
    double biologicalAge() const { return age_; }
    DmpPhase dmpPhase() const;
#ifdef CE_TESTING
    void setEnergyForTest(float value) { energy_=value; }
    void setReserveForTest(float value) { reserve_=value; }
#endif
private:
    PhysiologyParameters parameters_;
    TimeProfile time_;
    std::deque<DigestivePacket> packets_;
    float energy_=1,reserve_=1,waste_=0,starvation_=0,thermal_=0,mechanical_=0,toxicity_=0,agingDamage_=0;
    double age_=0,dmpTime_=0;
    ActionConsequences consequences_;
    DeathCause death_=DeathCause::None;
};
}
