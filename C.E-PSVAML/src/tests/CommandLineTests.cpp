#include <catch2/catch_test_macros.hpp>
#include "simulation/CommandLine.h"
TEST_CASE("CLI parses headless seed scenario ticks and speed") {
    const char* raw[]={"ce_psvaml","--headless","--seed","42","--scenario","chemotaxis_assay","--ticks","1000","--speed","50"};
    auto o=ce::parseCommandLine(10,const_cast<char**>(raw));
    REQUIRE(o.headless);REQUIRE(o.seed==42);REQUIRE(o.scenario=="chemotaxis_assay");REQUIRE(o.ticks==1000);REQUIRE(o.ticksPerFrame==50);
}
TEST_CASE("CLI rejects malformed numeric arguments missing values and unknown flags") {
    for(const char* value:{"-1","abc","12x","18446744073709551616"}) {
        const char* raw[]={"ce_psvaml","--ticks",value};REQUIRE_THROWS(ce::parseCommandLine(3,const_cast<char**>(raw)));
    }
    const char* missing[]={"ce_psvaml","--seed"};REQUIRE_THROWS(ce::parseCommandLine(2,const_cast<char**>(missing)));
    const char* unknown[]={"ce_psvaml","--banana"};REQUIRE_THROWS(ce::parseCommandLine(2,const_cast<char**>(unknown)));
    const char* zero[]={"ce_psvaml","--speed","0"};REQUIRE_THROWS(ce::parseCommandLine(3,const_cast<char**>(zero)));
}
