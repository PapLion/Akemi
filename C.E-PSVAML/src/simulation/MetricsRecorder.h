#pragma once
#include "simulation/LineageRecord.h"
#include "worm/WormDebugState.h"
#include <filesystem>
#include <map>
#include <string>
namespace ce {
class Simulation;
class MetricsRecorder {
public:
    void sample(const Simulation&);
    void recordBirth(const LineageRecord&);
    void recordDeath(const WormDebugState&,std::uint64_t tick,double dt);
    void flush(const std::filesystem::path&) const;
private:
    struct Individual {
        LineageRecord lineage;
        double food=0,absorbed=0,distance=0,dwelling=0,roaming=0,dauer=0;
        std::uint64_t reversals=0,turns=0,eggsLaid=0;
        bool reversing=false,turning=false;
        float reversalRate=0,turnRate=0;
        std::uint32_t maxDescendantGeneration=0;
    };
    void observe(const WormDebugState&,double dt);
    std::map<EntityId,Individual> individuals_;
    std::vector<std::string> populationRows_,events_;
    std::uint64_t tick_=0,births_=0,deaths_=0;
    double dt_=0.02;
};
}
