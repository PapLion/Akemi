// core/Random.h
#pragma once
#include <cstdint>
#include <random>
namespace ce {
class Random {
public:
    explicit Random(std::uint64_t seed);
    double uniform01();
    double normal(double mean, double sigma);
    bool chance(double probability);
    std::uint64_t seed() const { return seed_; }
private:
    std::uint64_t seed_;
    std::mt19937_64 engine_;
};
}
