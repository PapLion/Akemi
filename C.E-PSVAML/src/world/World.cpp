#include "world/World.h"
#include <algorithm>
#include <cmath>
namespace ce {
World::World(const SimulationConfig& c):config_(c),food_(c.fieldGridWidth,c.fieldGridHeight,c.worldWidth,c.worldHeight),
    foodOdor_(c.fieldGridWidth,c.fieldGridHeight,c.worldWidth,c.worldHeight),
    repellent_(foodOdor_),dauerPheromone_(foodOdor_),temperature_(foodOdor_),oxygen_(foodOdor_) {
    temperature_.fill(20); oxygen_.fill(0.5f);
}
Vector2 World::normalizePosition(Vector2 p) const {
    if(config_.boundaryMode==BoundaryMode::Closed) return {std::clamp(p.x,0.f,config_.worldWidth),std::clamp(p.y,0.f,config_.worldHeight)};
    auto wrap=[](float x,float size){ float v=std::fmod(x,size); return v<0?v+size:v; };
    return {wrap(p.x,config_.worldWidth),wrap(p.y,config_.worldHeight)};
}
bool World::resolveCollision(Vector2& p,float radius) const {
    bool hit=false;
    if(config_.boundaryMode==BoundaryMode::Closed) {
        Vector2 q{std::clamp(p.x,radius,config_.worldWidth-radius),std::clamp(p.y,radius,config_.worldHeight-radius)};
        hit=q.x!=p.x||q.y!=p.y; p=q;
    }
    return mechanical_.resolveCollision(p,radius)||hit;
}
void World::update(double dt) {
    food_.regrow(dt,foodRegrowthRate_,foodCapacity_);
    if(derivedOdor_) {
        const float blend=1-std::exp(-float(dt));
        for(int y=0;y<foodOdor_.height();++y) for(int x=0;x<foodOdor_.width();++x) {
            float v=foodOdor_.cell(x,y);
            foodOdor_.setCell(x,y,v+blend*(food_.density().cell(x,y)-v));
        }
        foodOdor_.diffuseAndDecay(0.4f,0,dt);
    }
    if(pheromoneSourceRate_>0)for(int y=0;y<dauerPheromone_.height();++y)for(int x=0;x<dauerPheromone_.width();++x)
        dauerPheromone_.setCell(x,y,dauerPheromone_.cell(x,y)+pheromoneSourceRate_*static_cast<float>(dt));
    dauerPheromone_.diffuseAndDecay(0.2f,0.1f,dt); mechanical_.update(dt);
}
}
