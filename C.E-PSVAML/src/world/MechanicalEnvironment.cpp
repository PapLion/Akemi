#include "world/MechanicalEnvironment.h"
#include <algorithm>
#include <cmath>
namespace ce {
float MechanicalEnvironment::vibration(Vector2 p) const {
    float result=0;
    for(const auto& s:sources_) if(s.radius>0) {
        const double phase=s.period>0?std::fmod(time_,s.period):0;
        const float envelope=std::exp(-float(std::max(0.,phase-s.duration))*12.f);
        result+=s.amplitude*envelope*std::max(0.f,1-std::hypot(p.x-s.position.x,p.y-s.position.y)/s.radius);
    }
    return std::clamp(result,0.f,1.f);
}
float MechanicalEnvironment::damage(Vector2 p) const {
    float result=0;
    for(const auto& s:sources_) if(s.radius>0 && (s.period<=0||std::fmod(time_,s.period)<s.duration))
        result+=s.damage*std::max(0.f,1-std::hypot(p.x-s.position.x,p.y-s.position.y)/s.radius);
    return std::max(0.f,result);
}
bool MechanicalEnvironment::resolveCollision(Vector2& p,float radius) const {
    bool hit=false;
    for(const auto& o:obstacles_) {
        float dx=p.x-o.center.x,dy=p.y-o.center.y,d=std::hypot(dx,dy),r=radius+o.radius;
        if(d>=r) continue;
        hit=true; if(d<1e-6f){ dx=1; dy=0; d=1; }
        p={o.center.x+dx*r/d,o.center.y+dy*r/d};
    }
    return hit;
}
}
