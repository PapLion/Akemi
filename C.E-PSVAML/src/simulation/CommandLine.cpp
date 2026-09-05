#include "simulation/CommandLine.h"
#include <charconv>
#include <limits>
#include <stdexcept>
#include <string_view>
namespace ce {
CommandLineOptions parseCommandLine(int argc,char** argv) {
    CommandLineOptions options;
    for(int i=1;i<argc;++i) {
        const std::string flag=argv[i];if(flag=="--headless"){options.headless=true;continue;}
        if(flag!="--seed" && flag!="--ticks" && flag!="--speed" && flag!="--scenario")throw std::invalid_argument("unknown flag: "+flag);
        if(++i>=argc)throw std::invalid_argument("missing value for "+flag);
        const std::string_view value=argv[i];if(flag=="--scenario"){options.scenario=value;continue;}
        std::uint64_t number=0;auto result=std::from_chars(value.data(),value.data()+value.size(),number);
        if(result.ec!=std::errc{} || result.ptr!=value.data()+value.size())throw std::invalid_argument("invalid unsigned number for "+flag);
        if(flag=="--seed")options.seed=number;else if(flag=="--ticks")options.ticks=number;
        else {if(number==0 || number>std::numeric_limits<int>::max())throw std::invalid_argument("speed must be a positive int");options.ticksPerFrame=static_cast<int>(number);}
    }
    return options;
}
}
