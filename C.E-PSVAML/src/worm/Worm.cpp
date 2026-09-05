#include "worm/Worm.h"
#include "world/World.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace ce {
namespace { BodyParameters newbornBody(const Genome& g) { auto p=g.bodyParameters();p.segmentLength*=0.4f;p.radius*=0.4f;p.structuralMassScale*=0.4f;return p; } }
Worm::Worm(EntityId id,EntityId parent,std::uint32_t generation,std::uint64_t tick,Vector2 pos,const Genome& g,const SimulationConfig& c,float provision,DevelopmentStage initialStage):
    id_(id),parentId_(parent),generation_(generation),birthTick_(tick),genome_(g),config_(c),
    body_(pos,c.bodySegments,newbornBody(g),c.physicsConstraintIterations),physiology_(g.physiologyParameters(),c.time),
    brain_(g.neuralParameters()),learning_(g.learningParameters(),20),development_(g.developmentParameters(),c.time),
    reproduction_(g.reproductionParameters(),c.time,g) {
    physiology_.initializeProvision(provision);
    // Scenario-only initial history uses the real developmental transition rules.
    DevelopmentInputs history;
    if(initialStage==DevelopmentStage::Dauer){history.foodAvailability=0;history.dauerPheromone=1;history.temperature=25;}
    for(int i=0;development_.stage()!=initialStage && i<1000000;++i) {
        development_.update(history,c.fixedDt);
        ReproductionInputs in;in.stage=development_.stage();in.stageProgress=development_.stageProgress();
        reproduction_.update(in,0);
    }
    if(development_.stage()!=initialStage)throw std::invalid_argument("unreachable initial development stage");
    bodyScale_=development_.targetBodyScale();auto bp=g.bodyParameters();bp.segmentLength*=bodyScale_;bp.radius*=bodyScale_;bp.structuralMassScale*=bodyScale_;
    body_=Body(pos,c.bodySegments,bp,c.physicsConstraintIterations);
    physiology_.setDevelopmentEffects(development_.metabolismMultiplier(),development_.agingMultiplier(),development_.stressResistanceMultiplier());
}
void Worm::tick(World& world,double dt,Random& rng) {
    if(!isAlive())return;
    // Frozen causal order: observation -> temporal processing -> brain -> action -> physics.
    lastSensory_=sensory_.sample(world,body_,physiology_,learning_.preferredTemperature(),0.5f,learning_.recentFoodMemory(),dt);
    const auto perceived=learning_.modulate(lastSensory_,dt);
    auto internal=physiology_.summaryForBrain();internal.developmentContext=static_cast<float>(development_.stage())/8;
    internal.recentFoodMemory=learning_.recentFoodMemory();lastMotor_=brain_.step(perceived,internal,dt);
    const float movement=development_.locomotionMultiplier();
    lastMotor_.forwardDrive*=movement;lastMotor_.reverseDrive*=movement;lastMotor_.turnBias*=movement;lastMotor_.headSweepDrive*=movement;
    if(!development_.pumpingAllowed())lastMotor_.pumpDrive=0;
    body_.applyMotorCommand(lastMotor_);body_.updatePhysics(world,dt);
    // Actual physiology precedes consequences and plasticity.
    physiology_.beginTick();physiology_.tryPump(world,body_.headPosition(),lastMotor_.pumpDrive,dt);
    physiology_.updateDigestion(dt);
    physiology_.applyMechanicalDamage(world.sampleMechanicalDamage(body_.headPosition())*static_cast<float>(dt));
    physiology_.updateMetabolism(0.003f*(lastMotor_.forwardDrive+lastMotor_.reverseDrive+std::abs(lastMotor_.turnBias)),world.sampleTemperature(body_.headPosition()),dt,rng);
    physiology_.updateDefecation(dt);
    lastConsequences_=physiology_.consequencesForLearning();lastConsequences_.distanceMoved=body_.distanceMovedLastTick();
    learning_.updateAfterConsequences(lastSensory_,lastConsequences_,brain_,dt);
    if(!isAlive())return;
    const float nutrition=std::clamp(physiology_.availableEnergy()+physiology_.lipidReserve(),0.f,1.f);
    const float stress=physiology_.summaryForBrain().stressLevel;
    development_.update({world.sampleFood(body_.headPosition()),world.samplePheromone(body_.headPosition()),world.sampleTemperature(body_.headPosition()),nutrition,stress},dt);
    physiology_.setDevelopmentEffects(development_.metabolismMultiplier(),development_.agingMultiplier(),development_.stressResistanceMultiplier());
    const float target=development_.targetBodyScale();
    if(target>bodyScale_)bodyScale_+=physiology_.allocateResources((target-bodyScale_)*genome_.structuralMassScale)/genome_.structuralMassScale;
    const auto bp=genome_.bodyParameters();body_.setSizeAndMass(bp.segmentLength*bodyScale_,bp.radius*bodyScale_,bp.structuralMassScale*bodyScale_+physiology_.lipidReserve()*0.1f);
    ReproductionInputs in;in.isAdult=development_.isReproductivelyAdult();in.stage=development_.stage();in.stageProgress=development_.stageProgress();
    in.nutritionState=nutrition;in.stressState=stress;in.parentId=id_;in.generation=generation_;in.position=body_.headPosition();
    if(in.isAdult && reproduction_.spermRemaining()>0 && reproduction_.reproductiveResources()<2)
        in.availableReproductiveResources=physiology_.allocateResources(static_cast<float>(dt*config_.time.reproductionRateScale)*genome_.reproductiveAllocation);
    reproduction_.update(in,dt,&rng,config_.mutation);
    world.depositPheromone(body_.midBodyPosition(),static_cast<float>(dt)*0.001f);
}
WormDebugState Worm::getReadOnlyDebugState() const {
    WormDebugState s;s.id=id_;s.parentId=parentId_;s.generation=generation_;s.birthTick=birthTick_;
    s.stage=development_.stage();s.phase=development_.phase();s.stageProgress=development_.stageProgress();s.molts=development_.completedLethargusCount();s.bodyScale=bodyScale_;
    s.energy=physiology_.availableEnergy();s.reserve=physiology_.lipidReserve();s.gutLoad=physiology_.gutLoad();s.waste=physiology_.wasteLoad();
    s.starvationStress=physiology_.starvationStress();s.thermalStress=physiology_.thermalStress();s.mechanicalDamage=physiology_.mechanicalDamage();s.toxicDamage=physiology_.toxicDamage();s.biologicalAge=physiology_.biologicalAge();s.dmpPhase=physiology_.dmpPhase();
    s.sperm=reproduction_.spermRemaining();s.uterineEggs=reproduction_.uterineEggCount();s.preferredTemperature=learning_.preferredTemperature();s.habituation=learning_.habituationLevel();s.foodMemory=learning_.recentFoodMemory();s.lastLearningValence=learning_.lastInternalValence();
    s.neuralNorm=brain_.stateNorm();s.neuralStates=brain_.states();s.effectiveInputWeights=brain_.effectiveInputWeights();s.segments=body_.bodySegments();s.speed=body_.forwardSpeed();
    s.deathCause=deathCause();s.lastConsequences=lastConsequences_;s.sensory=lastSensory_;s.motor=lastMotor_;return s;
}
}
