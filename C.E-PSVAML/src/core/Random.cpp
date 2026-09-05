#include "core/Random.h"
#include <algorithm>
namespace ce {
Random::Random(std::uint64_t seed) : seed_(seed), engine_(seed) {}
double Random::uniform01() { return std::generate_canonical<double, 53>(engine_); }
double Random::normal(double mean, double sigma) {
    return std::normal_distribution<double>(mean, sigma)(engine_);
}
bool Random::chance(double probability) {
    return uniform01() < std::clamp(probability, 0.0, 1.0);
}
}
