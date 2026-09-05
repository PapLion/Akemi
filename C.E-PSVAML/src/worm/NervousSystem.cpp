#include "worm/NervousSystem.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace ce {
NeuralParameters NeuralParameters::baseline(int inputs,int recurrent,int outputs) {
    if(inputs!=18||recurrent<6||outputs!=5)throw std::invalid_argument("V1 network requires 18 inputs, at least 6 recurrent neurons, 5 outputs");
    NeuralParameters p;p.inputCount=inputs;p.recurrentCount=recurrent;p.outputCount=outputs;
    p.inputWeights.assign(inputs*recurrent,0);p.recurrentWeights.assign(recurrent*recurrent,0);p.outputWeights.assign(outputs*recurrent,0);
    p.biases.assign(recurrent,0);p.timeConstants.assign(recurrent,0.2f);
    auto in=[&](int n,int k,float w){p.inputWeights[n*inputs+k]=w;};
    auto out=[&](int n,int k,float w){p.outputWeights[n*recurrent+k]=w;};
    p.biases[0]=0.6f;in(0,12,-0.55f);in(0,13,0.2f);in(0,1,0.8f);
    in(1,9,6);in(1,10,3);in(1,11,2);in(1,2,4);in(1,1,-3);
    in(2,12,3);in(2,13,0.3f);p.biases[2]=0.1f;
    p.biases[3]=0.015f;in(3,2,1);in(3,9,1);in(3,6,0.3f);in(3,8,0.6f);
    in(4,17,0.4f);in(4,12,-0.4f);in(4,1,-0.5f);
    for(int i=0;i<recurrent;++i)p.recurrentWeights[i*recurrent+i]=0.15f;
    out(0,0,1);out(0,1,-2);out(1,1,2);out(1,4,0.2f);
    out(2,3,0.7f);out(2,1,0.5f);out(2,4,0.3f);
    out(3,2,0.5f);out(3,4,0.3f);out(4,2,1);
    return p;
}
NervousSystem::NervousSystem(const NeuralParameters& p):parameters_(p) {
    auto valid=[](const std::vector<float>& values){return std::all_of(values.begin(),values.end(),[](float v){return std::isfinite(v)&&std::abs(v)<=8;});};
    const auto n=std::size_t(p.recurrentCount);
    if(p.inputCount!=18||p.recurrentCount<1||p.outputCount!=5||p.inputWeights.size()!=18*n||p.recurrentWeights.size()!=n*n||p.outputWeights.size()!=5*n||p.biases.size()!=n||p.timeConstants.size()!=n
        ||!valid(p.inputWeights)||!valid(p.recurrentWeights)||!valid(p.outputWeights)||!valid(p.biases)
        ||!std::all_of(p.timeConstants.begin(),p.timeConstants.end(),[](float t){return std::isfinite(t)&&t>=0.02f;}))throw std::invalid_argument("invalid CTRNN dimensions, weights or tau");
    v_.assign(n,0);a_.assign(n,0);
}
MotorCommand NervousSystem::step(const SensoryState& s,const InternalState& in,double dt) {
    if(!(dt>0)||!std::isfinite(dt))throw std::invalid_argument("invalid neural timestep");
    // Fixed 18-feature order. Redundant raw temperature/O2 slots carry stress/development;
    // temperature and O2 remain represented by signed preference errors and thermal delta.
    inputs_={s.foodAttractant,s.foodAttractantDelta*100,s.repellent,s.repellentDelta*100,
        in.stressLevel,s.temperatureDelta,s.temperatureErrorToPreference/10,in.developmentContext,
        s.oxygenErrorToPreference,s.noseTouch,s.bodyTouch,s.vibration,s.foodAtMouth,
        std::max(s.energyDeficit,in.energyDeficit),s.headCurvature,s.meanBodyCurvature,s.forwardSpeed/10,
        std::max(s.recentFoodMemory,in.recentFoodMemory)};
    for(auto& x:inputs_)x=std::clamp(x,-1.f,1.f);
    const int n=parameters_.recurrentCount;
    // All recurrent sums read the previous tick's activation vector (synchronous Euler).
    for(int i=0;i<n;++i) {
        if(dt>parameters_.timeConstants[i])throw std::invalid_argument("fixed dt exceeds CTRNN tau");
        double sum=parameters_.biases[i];
        for(int j=0;j<n;++j)sum+=parameters_.recurrentWeights[i*n+j]*a_[j];
        for(int k=0;k<18;++k)sum+=parameters_.inputWeights[i*18+k]*inputs_[k];
        v_[i]+=float(dt/parameters_.timeConstants[i]*(-v_[i]+sum));
    }
    for(int i=0;i<n;++i)a_[i]=std::tanh(v_[i]);
    std::array<float,5> output{};
    for(int o=0;o<5;++o){float sum=0;for(int j=0;j<n;++j)sum+=parameters_.outputWeights[o*n+j]*a_[j];output[o]=std::tanh(sum);}
    return {std::max(0.f,output[0]),std::max(0.f,output[1]),output[2],std::max(0.f,output[3]),std::max(0.f,output[4])};
}
float NervousSystem::stateNorm() const {double n=0;for(float v:v_)n+=v*v;return float(std::sqrt(n));}
}
