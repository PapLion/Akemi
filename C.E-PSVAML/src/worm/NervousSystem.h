#pragma once
#include "worm/NeuralParameters.h"
#include "worm/SensoryState.h"
#include "worm/MotorCommand.h"
#include "core/Types.h"
#include <array>
namespace ce {
class NervousSystem {
public:
    explicit NervousSystem(const NeuralParameters&);
    MotorCommand step(const SensoryState&,const InternalState&,double dt);
    std::vector<float>& effectiveInputWeights() { return parameters_.inputWeights; }
    const std::vector<float>& effectiveInputWeights() const { return parameters_.inputWeights; }
    const std::vector<float>& states() const { return v_; }
    const std::vector<float>& activations() const { return a_; }
    const std::array<float,18>& lastInputs() const { return inputs_; }
    float stateNorm() const;
private:
    NeuralParameters parameters_;
    std::vector<float> v_,a_;
    std::array<float,18> inputs_{};
};
}
