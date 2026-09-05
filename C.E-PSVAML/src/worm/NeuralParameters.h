#pragma once
#include <vector>
namespace ce {
struct NeuralParameters {
    int inputCount=18,recurrentCount=12,outputCount=5;
    std::vector<float> inputWeights,recurrentWeights,outputWeights,biases,timeConstants;
    static NeuralParameters baseline(int inputs,int recurrent,int outputs);
};
}
