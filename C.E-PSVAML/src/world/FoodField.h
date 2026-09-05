#pragma once
#include "world/ScalarField.h"
namespace ce {
class FoodField {
public:
    FoodField(int w,int h,float ww,float wh);
    float sampleDensity(Vector2 p) const { return density_.sample(p); }
    float sampleNutrition(Vector2 p) const { return nutrition_.sample(p); }
    float sampleDigestibility(Vector2 p) const { return digestibility_.sample(p); }
    float sampleToxicity(Vector2 p) const { return toxicity_.sample(p); }
    void paintPatch(Vector2 center,float radius,float density,float nutrition,float digestibility,float toxicity);
    float consume(Vector2 p,float requestedMass);
    void regrow(double dt,float rate,float capacity=1);
    float totalMass() const;
    const ScalarField& density() const { return density_; }
private:
    ScalarField density_,nutrition_,digestibility_,toxicity_;
};
}
