#include "simulation/MetricsRecorder.h"
#include "simulation/Simulation.h"
#include "simulation/BehaviorClassifier.h"
#include <array>
#include <fstream>
#include <locale>
#include <set>
#include <sstream>
#include <stdexcept>
#include <cmath>
namespace ce {
void MetricsRecorder::recordBirth(const LineageRecord& r) {
    if(individuals_.count(r.id))return;
    Individual i;i.lineage=r;i.maxDescendantGeneration=r.generation;individuals_.emplace(r.id,i);++births_;
    events_.push_back(std::to_string(r.birthTick)+" birth "+std::to_string(r.id)+" parent "+std::to_string(r.parentId));
}
void MetricsRecorder::observe(const WormDebugState& s,double dt) {
    auto& i=individuals_.at(s.id);i.food+=s.lastConsequences.foodIngested;i.absorbed+=s.lastConsequences.energyAbsorbed;i.distance+=s.lastConsequences.distanceMoved;
    const bool reversing=s.motor.reverseDrive>s.motor.forwardDrive,turning=std::abs(s.motor.turnBias)>0.4f;
    const bool reversalEvent=reversing&&!i.reversing,turnEvent=turning&&!i.turning;
    i.reversals+=reversalEvent;i.turns+=turnEvent;i.reversing=reversing;i.turning=turning;
    const float decay=static_cast<float>(std::exp(-dt/5));
    i.reversalRate=decay*i.reversalRate+(1-decay)*reversalEvent/static_cast<float>(dt);
    i.turnRate=decay*i.turnRate+(1-decay)*turnEvent/static_cast<float>(dt);
    auto telemetry=s;telemetry.reversalRateEstimate=i.reversalRate;telemetry.strongTurnRateEstimate=i.turnRate;
    const auto label=BehaviorClassifier::classify(telemetry);
    if(label=="dwelling")i.dwelling+=dt;else if(label!="dauer")i.roaming+=dt;
    if(s.stage==DevelopmentStage::Dauer)i.dauer+=dt;i.eggsLaid=s.eggsLaid;
}
void MetricsRecorder::recordDeath(const WormDebugState& s,std::uint64_t tick,double dt) {
    observe(s,dt);auto& i=individuals_.at(s.id);i.lineage.deathTick=tick;i.lineage.deathCause=s.deathCause;++deaths_;
    events_.push_back(std::to_string(tick)+" death "+std::to_string(s.id)+" cause "+std::to_string(static_cast<int>(s.deathCause)));
}
void MetricsRecorder::sample(const Simulation& sim) {
    tick_=sim.currentTick();dt_=sim.config().fixedDt;
    for(const auto& r:sim.population().lineageRecords()) { recordBirth(r);individuals_.at(r.id).lineage=r; }
    for(const auto& worm:sim.population().worms())if(tick_>0)observe(worm.getReadOnlyDebugState(),dt_);
    for(const auto& [id,child]:individuals_) {
        auto parent=child.lineage.parentId;
        while(parent && individuals_.count(parent)){auto& ancestor=individuals_.at(parent);ancestor.maxDescendantGeneration=std::max(ancestor.maxDescendantGeneration,child.lineage.generation);parent=ancestor.lineage.parentId;}
    }
    if(tick_%100!=0)return;
    std::array<int,8> stages{};double energy=0,reserve=0,age=0;
    std::array<double,6> means{},squares{};std::set<EntityId> roots;
    for(const auto& worm:sim.population().worms()) {
        const auto s=worm.getReadOnlyDebugState();++stages[static_cast<int>(s.stage)];energy+=s.energy;reserve+=s.reserve;age+=s.biologicalAge;
        const auto& g=worm.genome();std::array<double,6> traits{g.bodyStiffness,g.structuralMassScale,g.baseMetabolicRate,g.developmentRateScaleGene,g.plasticityRate,g.reproductiveAllocation};
        for(int j=0;j<6;++j){means[j]+=traits[j];squares[j]+=traits[j]*traits[j];}
        auto root=s.id;while(individuals_.count(root)&&individuals_.at(root).lineage.parentId)root=individuals_.at(root).lineage.parentId;roots.insert(root);
    }
    const auto count=sim.population().worms().size();const double n=count?double(count):1;
    std::ostringstream row;row.imbue(std::locale::classic());row.precision(10);
    row<<tick_<<','<<count<<','<<sim.population().eggs().size()<<','<<births_<<','<<deaths_<<",\"";
    for(int j=0;j<8;++j){if(j)row<<';';row<<stages[j];}
    row<<"\","<<energy/n<<','<<reserve/n<<','<<age/n<<','<<stages[static_cast<int>(DevelopmentStage::Dauer)]<<','<<roots.size()<<",\"";
    for(int j=0;j<6;++j){if(j)row<<';';row<<means[j]/n;}
    row<<"\",\"";for(int j=0;j<6;++j){if(j)row<<';';row<<std::max(0.0,squares[j]/n-means[j]*means[j]/(n*n));}row<<'"';
    populationRows_.push_back(row.str());births_=deaths_=0;
}
void MetricsRecorder::flush(const std::filesystem::path& directory) const {
    std::filesystem::create_directories(directory);
    std::ofstream individual(directory/"individuals.csv"),population(directory/"population.csv"),events(directory/"events.txt");
    for(auto* file:{&individual,&population,&events}){file->imbue(std::locale::classic());file->exceptions(std::ios::badbit|std::ios::failbit);}
    individual<<"id,parentId,generation,birthTick,deathTick,deathCause,lifetime,foodConsumed,energyAbsorbed,distanceTraveled,reversalCount,strongTurnCount,timeDwellingEstimate,timeRoamingEstimate,timeInDauer,eggsLaid,eggsHatched,childrenIds,maxGenerationDescendantSeen\n";
    for(const auto& [id,i]:individuals_) {
        const auto& r=i.lineage;individual<<id<<','<<r.parentId<<','<<r.generation<<','<<r.birthTick<<',';
        if(r.deathTick)individual<<*r.deathTick;
        individual<<','<<static_cast<int>(r.deathCause)<<','<<(r.deathTick.value_or(tick_)-r.birthTick)*dt_<<','<<i.food<<','<<i.absorbed<<','<<i.distance<<','<<i.reversals<<','<<i.turns<<','<<i.dwelling<<','<<i.roaming<<','<<i.dauer<<','<<i.eggsLaid<<','<<r.childIds.size()<<",\"";
        for(std::size_t j=0;j<r.childIds.size();++j){if(j)individual<<';';individual<<r.childIds[j];}individual<<"\","<<i.maxDescendantGeneration<<'\n';
    }
    population<<"tick,populationSize,eggCount,birthsPerWindow,deathsPerWindow,stageDistribution,meanEnergy,meanReserve,meanAge,dauerCount,lineageDiversity,traitMeans,traitVariance\n";
    for(const auto& row:populationRows_)population<<row<<'\n';for(const auto& event:events_)events<<event<<'\n';
}
}
