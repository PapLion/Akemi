#include "simulation/Scenario.h"
#include "simulation/Population.h"
#include "world/World.h"
#include <algorithm>
namespace ce {
std::vector<std::string> Scenario::requiredV1Names() {
    return {"baseline_ecosystem","chemotaxis_assay","thermotaxis_assay","aerotaxis_assay","nose_touch_assay","habituation_assay","associative_learning_assay","starvation_assay","dauer_induction_assay","dauer_recovery_assay","reproduction_assay"};
}
bool Scenario::apply(std::string_view name,World& world,Population& population,Random& rng,const SimulationConfig& cfg) {
    const auto names=requiredV1Names();if(std::find(names.begin(),names.end(),name)==names.end())return false;
    const Vector2 center{cfg.worldWidth*0.5f,cfg.worldHeight*0.5f};
    const float extent=std::max(cfg.worldWidth,cfg.worldHeight);
    auto genome=Genome::baseline(18,cfg.brainRecurrentNeurons,5);
    if(name=="baseline_ecosystem") {
        for(Vector2 pos:std::vector<Vector2>{{cfg.worldWidth*0.25f,cfg.worldHeight*0.25f},{cfg.worldWidth*0.75f,cfg.worldHeight*0.75f}})
            world.food().paintPatch(pos,extent*0.22f,1,1,1,0);
        world.setFoodRegrowthRate(0.02f);
        for(int i=0;i<cfg.initialPopulation;++i)population.spawnWorm({{float(rng.uniform01()*cfg.worldWidth),float(rng.uniform01()*cfg.worldHeight)},genome},0,cfg);
        return true;
    }
    DevelopmentStage stage=DevelopmentStage::L1;
    if(name=="reproduction_assay")stage=DevelopmentStage::Adult;
    if(name=="dauer_recovery_assay")stage=DevelopmentStage::Dauer;
    if(name!="starvation_assay" && name!="dauer_induction_assay" && name!="habituation_assay") {
        world.food().paintPatch(center,extent,1,1,1,0);world.setFoodRegrowthRate(0.05f);
    }
    if(name=="chemotaxis_assay" || name=="associative_learning_assay")world.setFoodOdorLinear({1,0},0,1);
    if(name=="thermotaxis_assay")world.setTemperatureLinear({1,0},15,25);
    if(name=="aerotaxis_assay")world.setOxygenLinear({1,0},0.1f,0.9f);
    if(name=="nose_touch_assay")world.mechanical().addObstacle({{center.x+1,center.y},2});
    if(name=="habituation_assay")world.mechanical().addSource({center,extent,1,0,1,0.1});
    if(name=="dauer_induction_assay") {
        world.food().paintPatch(center,extent,0.05f,1,1,0);world.setFoodRegrowthRate(0.01f,0.05f);
        world.setPheromoneUniform(1);world.setPheromoneSourceRate(0.1f);world.setTemperatureUniform(25);
    }
    population.spawnWorm({center,genome,0,0,stage},0,cfg);return true;
}
}
