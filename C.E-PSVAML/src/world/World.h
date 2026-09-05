#pragma once
#include "world/FoodField.h"
#include "world/MechanicalEnvironment.h"
#include "simulation/SimulationConfig.h"
namespace ce {
class World {
public:
    explicit World(const SimulationConfig&);
    Vector2 normalizePosition(Vector2 p) const;
    float sampleFood(Vector2 p) const { return food_.sampleDensity(normalizePosition(p)); }
    float consumeFood(Vector2 p,float amount) { return food_.consume(normalizePosition(p),amount); }
    float sampleFoodOdor(Vector2 p) const { return foodOdor_.sample(normalizePosition(p)); }
    float sampleRepellent(Vector2 p) const { return repellent_.sample(normalizePosition(p)); }
    float samplePheromone(Vector2 p) const { return dauerPheromone_.sample(normalizePosition(p)); }
    float sampleTemperature(Vector2 p) const { return temperature_.sample(normalizePosition(p)); }
    float sampleOxygen(Vector2 p) const { return oxygen_.sample(normalizePosition(p)); }
    float sampleVibration(Vector2 p) const { return mechanical_.vibration(normalizePosition(p)); }
    float sampleMechanicalDamage(Vector2 p) const { return mechanical_.damage(normalizePosition(p)); }
    void depositPheromone(Vector2 p,float amount) { dauerPheromone_.addAt(normalizePosition(p),amount); }
    bool resolveCollision(Vector2& p,float radius) const;
    void update(double dt);
    FoodField& food() { return food_; }
    const FoodField& food() const { return food_; }
    MechanicalEnvironment& mechanical() { return mechanical_; }
    void setFoodOdorLinear(Vector2 d,float lo,float hi) { foodOdor_.linear(d,lo,hi); derivedOdor_=false; }
    void setTemperatureUniform(float t) { temperature_.fill(t); }
    void setTemperatureLinear(Vector2 d,float lo,float hi) { temperature_.linear(d,lo,hi); }
    void setTemperatureRadial(Vector2 p,float r,float a,float b) { temperature_.radial(p,r,a,b); }
    void setOxygenUniform(float o) { oxygen_.fill(o); }
    void setOxygenLinear(Vector2 d,float lo,float hi) { oxygen_.linear(d,lo,hi); }
    void setPheromoneUniform(float p) { dauerPheromone_.fill(p); }
    void setRepellentUniform(float p) { repellent_.fill(p); }
    void setFoodRegrowthRate(float r) { foodRegrowthRate_=r; }
private:
    SimulationConfig config_;
    FoodField food_;
    ScalarField foodOdor_,repellent_,dauerPheromone_,temperature_,oxygen_;
    MechanicalEnvironment mechanical_;
    bool derivedOdor_=true;
    float foodRegrowthRate_=0;
};
}
