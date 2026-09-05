#include <catch2/catch_test_macros.hpp>
#include "worm/LearningSystem.h"
#include "worm/NervousSystem.h"
TEST_CASE("Learning harmless vibration habituates and damage restores sensitivity") {
    ce::LearningSystem l({},20);ce::NervousSystem b(ce::NeuralParameters::baseline(18,12,5));ce::SensoryState raw;raw.vibration=1;
    float first=l.modulate(raw,0.02).vibration;
    for(int i=0;i<200;++i){auto s=l.modulate(raw,0.02);b.step(s,{},0.02);l.updateAfterConsequences(raw,{},b,0.02);}
    float habituated=l.modulate(raw,0.02).vibration;REQUIRE(habituated<first);
    ce::ActionConsequences c;c.damageDelta=1;l.updateAfterConsequences(raw,c,b,0.02);
    REQUIRE(l.modulate(raw,0.02).vibration>habituated);
}
TEST_CASE("Learning observation alone cannot assert harmless consequence") {
    ce::LearningSystem l({},20);ce::SensoryState raw;raw.vibration=1;
    for(int i=0;i<200;++i)l.modulate(raw,0.02);REQUIRE(l.habituationLevel()==0);
}
TEST_CASE("Learning thermal memory needs nutrient absorption") {
    ce::LearningSystem fed({},20),empty({},20);ce::NervousSystem b(ce::NeuralParameters::baseline(18,12,5));
    ce::SensoryState s;s.temperature=24;ce::ActionConsequences c;c.energyAbsorbed=0.1f;
    for(int i=0;i<10000;++i){b.step(s,{},0.02);fed.updateAfterConsequences(s,c,b,0.02);empty.updateAfterConsequences(s,{},b,0.02);}
    REQUIRE(fed.preferredTemperature()>20);REQUIRE(empty.preferredTemperature()==20);
}
TEST_CASE("Learning plasticity changes effective weights not inherited source") {
    const auto p=ce::NeuralParameters::baseline(18,12,5);const auto original=p.inputWeights;
    ce::NervousSystem b(p);ce::LearningSystem l({},20);ce::SensoryState s;s.foodAttractant=0.5f;
    ce::ActionConsequences c;c.energyAbsorbed=0.1f;
    for(int i=0;i<300;++i){b.step(l.modulate(s,0.02),{},0.02);l.updateAfterConsequences(s,c,b,0.02);}
    REQUIRE(b.effectiveInputWeights()!=original);REQUIRE(p.inputWeights==original);REQUIRE(l.lastInternalValence()>0);
}
