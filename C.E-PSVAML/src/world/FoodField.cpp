#include "world/FoodField.h"
#include <algorithm>
#include <cmath>
#include <numeric>
namespace ce {
FoodField::FoodField(int w,int h,float ww,float wh):density_(w,h,ww,wh),nutrition_(w,h,ww,wh,1),digestibility_(w,h,ww,wh,1),toxicity_(w,h,ww,wh){}
void FoodField::paintPatch(Vector2 c,float r,float d,float n,float dig,float tox) {
    for(int y=0;y<density_.height();++y) for(int x=0;x<density_.width();++x) {
        auto p=density_.position(x,y); if(std::hypot(p.x-c.x,p.y-c.y)>r) continue;
        density_.setCell(x,y,std::clamp(d,0.f,1.f)); nutrition_.setCell(x,y,std::max(n,0.001f));
        digestibility_.setCell(x,y,std::clamp(dig,0.f,1.f)); toxicity_.setCell(x,y,std::clamp(tox,0.f,1.f));
    }
}
float FoodField::consume(Vector2 p,float amount) { return density_.consumeAt(p,std::max(0.f,amount)); }
float FoodField::totalMass() const { return std::accumulate(density_.values().begin(),density_.values().end(),0.f); }
void FoodField::regrow(double dt,float rate,float capacity) {
    const float a=1-std::exp(-std::max(0.f,rate)*float(std::max(0.,dt)));
    for(int y=0;y<density_.height();++y) for(int x=0;x<density_.width();++x) {
        float d=density_.cell(x,y); density_.setCell(x,y,d+(std::clamp(capacity,0.f,1.f)-d)*a);
    }
}
}
