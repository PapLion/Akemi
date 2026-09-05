#pragma once
#include <raylib.h>
#include <vector>
#include "worm/MotorCommand.h"
namespace ce {
class World;
struct BodyParameters {
    float segmentLength=5,radius=1.5f,stiffness=0.7f,structuralMassScale=1;
    float muscleStrength=1,baselineWaveFrequency=2,baselineWaveAmplitude=0.35f;
    float longitudinalDrag=0.98f,lateralDrag=0.85f;
};
struct BodyNode { Vector2 position{},previousPosition{}; float mass=1; };
class Body {
public:
    Body(Vector2 headPosition,int segmentCount,BodyParameters parameters,int constraintIterations);
    void applyMotorCommand(const MotorCommand&);
    void updatePhysics(World&,double dt);
    Vector2 headPosition() const { return nodes_.front().position; }
    Vector2 midBodyPosition() const;
    const std::vector<Vector2>& bodySegments() const { return segments_; }
    bool headTouch() const { return headTouch_; }
    bool bodyTouch() const { return bodyTouch_; }
    float headCurvature() const;
    float meanBodyCurvature() const;
    float forwardSpeed() const { return speed_; }
    float distanceMovedLastTick() const { return distance_; }
    std::vector<float> segmentLengths() const;
private:
    void constrainLength();
    void constrainBending();
    float curvature(std::size_t i) const;
    BodyParameters parameters_;
    int iterations_;
    std::vector<BodyNode> nodes_;
    std::vector<Vector2> segments_;
    MotorCommand command_;
    double phase_=0,sweepPhase_=0;
    float speed_=0,distance_=0;
    bool headTouch_=false,bodyTouch_=false;
};
}
