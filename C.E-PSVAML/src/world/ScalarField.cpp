#include "world/ScalarField.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace ce {
ScalarField::ScalarField(int w,int h,float ww,float wh,float initial)
    : width_(w),height_(h),worldWidth_(ww),worldHeight_(wh) {
    if(w<2||h<2||!(ww>0)||!(wh>0)) throw std::invalid_argument("invalid field dimensions");
    values_.assign(std::size_t(w)*h,initial);
}
std::array<ScalarField::Tap,4> ScalarField::taps(Vector2 p) const {
    float x=std::clamp(p.x/worldWidth_,0.f,1.f)*(width_-1);
    float y=std::clamp(p.y/worldHeight_,0.f,1.f)*(height_-1);
    int ix=std::min(int(x),width_-2),iy=std::min(int(y),height_-2);
    float fx=x-ix,fy=y-iy; std::size_t i=std::size_t(iy)*width_+ix;
    return {{{i,(1-fx)*(1-fy)},{i+1,fx*(1-fy)},
             {i+width_,(1-fx)*fy},{i+width_+1,fx*fy}}};
}
float ScalarField::sample(Vector2 p) const {
    float v=0; for(auto t:taps(p)) v+=values_[t.index]*t.weight; return v;
}
void ScalarField::setCell(int x,int y,float v) { values_.at(std::size_t(y)*width_+x)=v; }
float ScalarField::cell(int x,int y) const { return values_.at(std::size_t(y)*width_+x); }
void ScalarField::addAt(Vector2 p,float amount) { for(auto t:taps(p)) values_[t.index]+=amount*t.weight; }
float ScalarField::consumeAt(Vector2 p,float amount) {
    // Remove the sampled fraction from the four cells; sum of decrements is actual mass.
    const float density=sample(p);
    const float fraction=density>0?std::clamp(amount/density,0.f,1.f):0;
    float removed=0;
    for(auto t:taps(p)) { float m=values_[t.index]*t.weight*fraction; values_[t.index]-=m; removed+=m; }
    return removed;
}
void ScalarField::diffuseAndDecay(float diffusion,float decay,double dt) {
    if(dt<=0) return;
    const int steps=std::max(1,int(std::ceil(std::max(0.f,diffusion)*dt*4)));
    const float a=std::max(0.f,diffusion)*float(dt/steps);
    const float d=std::exp(-std::max(0.f,decay)*float(dt/steps));
    for(int k=0;k<steps;++k) {
        auto next=values_;
        for(int y=0;y<height_;++y) for(int x=0;x<width_;++x) {
            const float v=cell(x,y);
            const float sum=cell(std::max(0,x-1),y)+cell(std::min(width_-1,x+1),y)
                +cell(x,std::max(0,y-1))+cell(x,std::min(height_-1,y+1));
            next[std::size_t(y)*width_+x]=(v+a*(sum-4*v))*d;
        }
        values_.swap(next);
    }
}
void ScalarField::fill(float v) { std::fill(values_.begin(),values_.end(),v); }
Vector2 ScalarField::position(int x,int y) const { return {worldWidth_*x/(width_-1),worldHeight_*y/(height_-1)}; }
void ScalarField::linear(Vector2 dir,float low,float high) {
    const float lo=std::min(0.f,dir.x*worldWidth_)+std::min(0.f,dir.y*worldHeight_);
    const float span=std::abs(dir.x*worldWidth_)+std::abs(dir.y*worldHeight_);
    for(int y=0;y<height_;++y) for(int x=0;x<width_;++x) {
        auto p=position(x,y); float f=span>0?(p.x*dir.x+p.y*dir.y-lo)/span:0;
        setCell(x,y,low+(high-low)*f);
    }
}
void ScalarField::radial(Vector2 center,float radius,float inner,float outer) {
    if(!(radius>0)) throw std::invalid_argument("radius must be positive");
    for(int y=0;y<height_;++y) for(int x=0;x<width_;++x) {
        auto p=position(x,y); float f=std::min(1.f,std::hypot(p.x-center.x,p.y-center.y)/radius);
        setCell(x,y,inner+(outer-inner)*f);
    }
}
}
