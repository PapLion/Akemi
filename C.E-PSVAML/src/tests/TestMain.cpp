#include <catch2/catch_test_macros.hpp>
#include <string>
#include "core/Version.h"

TEST_CASE("V1 core exposes a version") {
    REQUIRE(std::string(ce::version()) == "0.1.0-v1");
}
