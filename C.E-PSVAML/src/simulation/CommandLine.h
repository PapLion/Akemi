#pragma once
#include <cstdint>
#include <string>
namespace ce {
struct CommandLineOptions { bool headless=false;std::uint64_t seed=1;std::string scenario="baseline_ecosystem";std::uint64_t ticks=0;int ticksPerFrame=1; };
CommandLineOptions parseCommandLine(int argc,char** argv);
}
