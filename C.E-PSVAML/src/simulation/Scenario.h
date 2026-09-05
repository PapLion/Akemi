#pragma once
#include "simulation/SimulationConfig.h"
#include "core/Random.h"
#include <string>
#include <string_view>
#include <vector>
namespace ce {
class World;class Population;
class Scenario {
public:
    static std::vector<std::string> requiredV1Names();
    static bool apply(std::string_view,World&,Population&,Random&,const SimulationConfig&);
};
}
