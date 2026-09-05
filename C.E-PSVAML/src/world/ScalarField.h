#pragma once
#include <raylib.h>
#include <array>
#include <vector>
namespace ce {
class ScalarField {
public:
    ScalarField(int width, int height, float worldWidth, float worldHeight, float initialValue=0);
    float sample(Vector2 position) const;
    void setCell(int x,int y,float value);
    float cell(int x,int y) const;
    void addAt(Vector2 position,float amount);
    float consumeAt(Vector2 position,float amount);
    void diffuseAndDecay(float diffusionRate,float decayRate,double dt);
    void fill(float value);
    void linear(Vector2 direction,float low,float high);
    void radial(Vector2 center,float radius,float inner,float outer);
    Vector2 position(int x,int y) const;
    int width() const { return width_; }
    int height() const { return height_; }
    const std::vector<float>& values() const { return values_; }
private:
    struct Tap { std::size_t index; float weight; };
    std::array<Tap,4> taps(Vector2 p) const;
    int width_,height_;
    float worldWidth_,worldHeight_;
    std::vector<float> values_;
};
}
