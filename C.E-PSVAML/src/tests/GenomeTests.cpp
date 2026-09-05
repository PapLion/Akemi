#include <catch2/catch_test_macros.hpp>
#include "worm/Genome.h"
#include <limits>
TEST_CASE("Genome baseline is valid and mutation replays seed") {
    auto g=ce::Genome::baseline(18,12,5);REQUIRE(g.validate());
    ce::Random a(99),b(99);REQUIRE(ce::mutate(g,a,{})==ce::mutate(g,b,{}));
}
TEST_CASE("Genome disabled mutation preserves inheritance and bounded mutation stays valid") {
    auto g=ce::Genome::baseline(18,12,5);const auto original=g;ce::Random rng(12);
    ce::MutationConfig off;off.parameterProbability=off.neuralProbability=0;
    REQUIRE(ce::mutate(g,rng,off)==g);
    ce::MutationConfig all;all.parameterProbability=all.neuralProbability=1;
    for(int i=0;i<100;++i){g=ce::mutate(g,rng,all);REQUIRE(g.validate());}
    REQUIRE_FALSE(g==original);
    auto bad=original;bad.bodyStiffness=std::numeric_limits<float>::quiet_NaN();REQUIRE_FALSE(bad.validate());
    bad=original;bad.neural.inputWeights.pop_back();REQUIRE_FALSE(bad.validate());
}
