#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include <cmath>
#include "worm/NervousSystem.h"
TEST_CASE("Nervous CTRNN keeps state after sensory pulse") {
    ce::NervousSystem b(ce::NeuralParameters::baseline(18,12,5));ce::SensoryState s;s.noseTouch=1;
    b.step(s,{},0.02);b.step({}, {},0.02);REQUIRE(b.stateNorm()>0);
}
TEST_CASE("Nervous innate weights drive withdrawal and pumping") {
    for(int cue=0;cue<2;++cue){ce::NervousSystem b(ce::NeuralParameters::baseline(18,12,5));ce::SensoryState s;
        if(cue==0)s.noseTouch=1;else s.repellent=1;ce::MotorCommand m;
        for(int i=0;i<100;++i)m=b.step(s,{},0.02);REQUIRE(m.reverseDrive>m.forwardDrive);
    }
    ce::NervousSystem b(ce::NeuralParameters::baseline(18,12,5));ce::SensoryState s;s.foodAtMouth=1;
    REQUIRE(b.step(s,{},0.02).pumpDrive>0);
}
TEST_CASE("Nervous Euler uses previous recurrent state and tau") {
    auto p=ce::NeuralParameters::baseline(18,12,5);
    std::fill(p.inputWeights.begin(),p.inputWeights.end(),0);std::fill(p.recurrentWeights.begin(),p.recurrentWeights.end(),0);
    std::fill(p.biases.begin(),p.biases.end(),0);std::fill(p.timeConstants.begin(),p.timeConstants.end(),1);
    p.biases[0]=1;p.recurrentWeights[12]=2;
    ce::NervousSystem b(p);b.step({}, {},0.02);
    REQUIRE(b.states()[0]==Catch::Approx(0.02));REQUIRE(b.states()[1]==0);
    b.step({}, {},0.02);REQUIRE(b.states()[0]==Catch::Approx(0.0396));
    REQUIRE(b.states()[1]==Catch::Approx(0.04*std::tanh(0.02)));
}
TEST_CASE("Nervous fixed input packing and bounded 100000 steps") {
    ce::NervousSystem b(ce::NeuralParameters::baseline(18,12,5));ce::SensoryState s;s.noseTouch=1;s.temperatureErrorToPreference=5;
    ce::InternalState in;in.stressLevel=0.7f;in.developmentContext=0.5f;
    b.step(s,in,0.02);REQUIRE(b.lastInputs()[9]==1);REQUIRE(b.lastInputs()[6]==Catch::Approx(0.5));
    REQUIRE(b.lastInputs()[4]==Catch::Approx(0.7));REQUIRE(b.lastInputs()[7]==Catch::Approx(0.5));
    for(int i=0;i<100000;++i){auto m=b.step(s,in,0.02);REQUIRE(std::isfinite(b.stateNorm()));REQUIRE(m.forwardDrive>=0);REQUIRE(m.forwardDrive<=1);}
}
TEST_CASE("Nervous rejects malformed dimensions and unstable tau") {
    auto p=ce::NeuralParameters::baseline(18,12,5);p.inputWeights.pop_back();REQUIRE_THROWS(ce::NervousSystem(p));
    p=ce::NeuralParameters::baseline(18,12,5);p.timeConstants[0]=0;REQUIRE_THROWS(ce::NervousSystem(p));
}
