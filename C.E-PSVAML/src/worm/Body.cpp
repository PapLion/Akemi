#include "worm/Body.h"
#include "world/World.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace ce {
namespace {
Vector2 add(Vector2 a,Vector2 b){return {a.x+b.x,a.y+b.y};}
Vector2 sub(Vector2 a,Vector2 b){return {a.x-b.x,a.y-b.y};}
Vector2 mul(Vector2 a,float b){return {a.x*b,a.y*b};}
float dot(Vector2 a,Vector2 b){return a.x*b.x+a.y*b.y;}
float length(Vector2 a){return std::hypot(a.x,a.y);}
Vector2 unit(Vector2 a){float l=length(a);return l>1e-6f?mul(a,1/l):Vector2{1,0};}
Vector2 perp(Vector2 a){return {-a.y,a.x};}
float angle(Vector2 a,Vector2 b){return std::atan2(a.x*b.y-a.y*b.x,dot(a,b));}
}
Body::Body(Vector2 head,int count,BodyParameters p,int iterations):parameters_(p),iterations_(iterations) {
    if(count<3||iterations<1||p.segmentLength<=0||p.structuralMassScale<=0) throw std::invalid_argument("invalid body parameters");
    for(int i=0;i<count;++i){Vector2 q{head.x-i*p.segmentLength,head.y};nodes_.push_back({q,q,p.structuralMassScale});segments_.push_back(q);}
}
void Body::applyMotorCommand(const MotorCommand& c) {
    command_={std::clamp(c.forwardDrive,0.f,1.f),std::clamp(c.reverseDrive,0.f,1.f),std::clamp(c.turnBias,-1.f,1.f),std::clamp(c.headSweepDrive,0.f,1.f),std::clamp(c.pumpDrive,0.f,1.f)};
}
Vector2 Body::midBodyPosition() const {
    Vector2 p{};for(const auto& n:nodes_) p=add(p,n.position);return mul(p,1.f/nodes_.size());
}
float Body::curvature(std::size_t i) const {
    return angle(sub(nodes_[i].position,nodes_[i-1].position),sub(nodes_[i+1].position,nodes_[i].position));
}
float Body::headCurvature() const {return curvature(1);}
float Body::meanBodyCurvature() const {float v=0;for(std::size_t i=1;i+1<nodes_.size();++i)v+=curvature(i);return v/(nodes_.size()-2);}
std::vector<float> Body::segmentLengths() const {
    std::vector<float> result;for(std::size_t i=1;i<nodes_.size();++i)result.push_back(length(sub(nodes_[i].position,nodes_[i-1].position)));return result;
}
void Body::constrainLength() {
    for(std::size_t i=1;i<nodes_.size();++i) {
        auto& a=nodes_[i-1];auto& b=nodes_[i];const auto delta=sub(b.position,a.position);float d=length(delta);
        if(d<1e-6f) continue;
        float wa=1/a.mass,wb=1/b.mass;auto correction=mul(delta,(d-parameters_.segmentLength)/(d*(wa+wb)));
        a.position=add(a.position,mul(correction,wa));b.position=sub(b.position,mul(correction,wb));
    }
}
void Body::constrainBending() {
    for(std::size_t i=1;i+1<nodes_.size();++i) {
        auto a=sub(nodes_[i].position,nodes_[i-1].position),b=sub(nodes_[i+1].position,nodes_[i].position);
        if(dot(a,a)<1e-6f||dot(b,b)<1e-6f) continue;
        float drive=std::max(command_.forwardDrive,command_.reverseDrive);
        float target=parameters_.baselineWaveAmplitude*drive*std::sin(phase_-0.65*i)
            +command_.turnBias*0.4f;
        if(i<4) target+=command_.headSweepDrive*0.2f*std::sin(sweepPhase_)*(4-i)/3;
        auto g0=mul(perp(a),1/dot(a,a)),g2=mul(perp(b),1/dot(b,b)),g1=mul(add(g0,g2),-1);
        float w0=1/nodes_[i-1].mass,w1=1/nodes_[i].mass,w2=1/nodes_[i+1].mass;
        float denominator=w0*dot(g0,g0)+w1*dot(g1,g1)+w2*dot(g2,g2);
        float error=std::remainder(curvature(i)-target,6.2831853f);
        float lambda=-std::clamp(parameters_.stiffness*parameters_.muscleStrength,0.f,1.f)*error/denominator;
        nodes_[i-1].position=add(nodes_[i-1].position,mul(g0,lambda*w0));
        nodes_[i].position=add(nodes_[i].position,mul(g1,lambda*w1));
        nodes_[i+1].position=add(nodes_[i+1].position,mul(g2,lambda*w2));
    }
}
void Body::updatePhysics(World& world,double dt) {
    if(dt<=0) return;
    const auto before=midBodyPosition();const auto heading=unit(sub(nodes_.front().position,nodes_.back().position));
    phase_+=parameters_.baselineWaveFrequency*(command_.forwardDrive-command_.reverseDrive)*dt;
    sweepPhase_+=3*dt;headTouch_=bodyTouch_=false;
    // Effective anisotropic substrate drag: locomotion comes from bending plus this interaction.
    // Internal length/angle corrections preserve center of mass; no commanded translation exists.
    auto old=nodes_;
    for(std::size_t i=0;i<nodes_.size();++i) {
        auto tangent=unit(sub(old[i?i-1:i].position,old[std::min(i+1,old.size()-1)].position));
        auto v=sub(old[i].position,old[i].previousPosition),longitudinal=mul(tangent,dot(v,tangent));
        auto damped=add(mul(longitudinal,parameters_.longitudinalDrag),mul(sub(v,longitudinal),parameters_.lateralDrag));
        nodes_[i].previousPosition=old[i].position;nodes_[i].position=add(old[i].position,damped);
    }
    for(int k=0;k<iterations_;++k) {
        constrainLength();constrainBending();
        for(std::size_t i=0;i<nodes_.size();++i) if(world.resolveCollision(nodes_[i].position,parameters_.radius)) {
            if(i==0)headTouch_=true;else bodyTouch_=true;
        }
    }
    auto displacement=sub(midBodyPosition(),before);distance_=length(displacement);speed_=dot(displacement,heading)/float(dt);
    // Wrap the entire rig together, preserving local geometry and Verlet velocity at the seam.
    auto center=midBodyPosition();auto shift=sub(world.normalizePosition(center),center);
    // Closed walls have already resolved nodes, so their center does not require translation.
    for(std::size_t i=0;i<nodes_.size();++i) {
        nodes_[i].position=add(nodes_[i].position,shift);nodes_[i].previousPosition=add(nodes_[i].previousPosition,shift);
        segments_[i]=nodes_[i].position;
    }
}
}
