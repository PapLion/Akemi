#include "render/Renderer.h"
#include <algorithm>
#include <cmath>
#include <sstream>
namespace ce {
void Renderer::draw(const Simulation& simulation) {
    if(IsKeyPressed(KEY_TAB))overlay_=(overlay_+1)%7;
    const float scale=std::min((GetScreenWidth()-310.f)/config_.worldWidth,(GetScreenHeight()-50.f)/config_.worldHeight);
    const auto screen=[&](Vector2 p){return Vector2{20+p.x*scale,30+p.y*scale};};
    BeginDrawing();ClearBackground({17,22,28,255});
    for(int y=0;y<config_.fieldGridHeight;++y)for(int x=0;x<config_.fieldGridWidth;++x) {
        Vector2 p{config_.worldWidth*x/config_.fieldGridWidth,config_.worldHeight*y/config_.fieldGridHeight};float value=0;
        const auto& w=simulation.world();
        switch(overlay_) {case 0:value=w.sampleFood(p);break;case 1:value=w.sampleFoodOdor(p);break;case 2:value=w.sampleRepellent(p);break;case 3:value=w.samplePheromone(p);break;case 4:value=(w.sampleTemperature(p)-10)/25;break;case 5:value=w.sampleOxygen(p);break;case 6:value=w.sampleVibration(p);break;}
        auto q=screen(p);DrawRectangle(int(q.x),int(q.y),int(std::ceil(config_.worldWidth/config_.fieldGridWidth*scale)),int(std::ceil(config_.worldHeight/config_.fieldGridHeight*scale)),Color{35,static_cast<unsigned char>(35+150*std::clamp(value,0.f,1.f)),static_cast<unsigned char>(40+50*std::clamp(value,0.f,1.f)),255});
    }
    for(const auto& egg:simulation.population().eggs())DrawCircleV(screen(egg.position()),3,GOLD);
    if(!selected_ && !simulation.population().worms().empty())selected_=simulation.population().worms().front().id();
    for(const auto& worm:simulation.population().worms()) {
        const auto s=worm.getReadOnlyDebugState();const Color color=s.stage==DevelopmentStage::Dauer?SKYBLUE:RAYWHITE;
        for(std::size_t i=1;i<s.segments.size();++i) {
            auto a=screen(s.segments[i-1]),b=screen(s.segments[i]);DrawLineEx(a,b,std::max(2.f,4*s.bodyScale*scale),color);
        }
        const auto head=screen(s.segments.front());DrawCircleV(head,3,worm.id()==selected_?ORANGE:RED);
        if(IsMouseButtonPressed(MOUSE_BUTTON_LEFT) && CheckCollisionPointCircle(GetMousePosition(),head,15))selected_=worm.id();
        if(worm.id()==selected_) {
            std::ostringstream info;info<<"Worm "<<s.id<<" parent "<<s.parentId<<" gen "<<s.generation<<"\nStage "<<int(s.stage)<<" phase "<<int(s.phase)<<"\nAge "<<s.biologicalAge<<"\nEnergy "<<s.energy<<"\nReserve "<<s.reserve<<"\nGut "<<s.gutLoad<<"\nStarvation "<<s.starvationStress<<"\nThermal stress "<<s.thermalStress<<"\nSperm "<<s.sperm<<"\nUterine eggs "<<s.uterineEggs<<"\nPreferred T "<<s.preferredTemperature<<"\nFood memory "<<s.foodMemory<<"\nForward "<<s.motor.forwardDrive<<"\nReverse "<<s.motor.reverseDrive<<"\nTurn "<<s.motor.turnBias<<"\nSweep "<<s.motor.headSweepDrive<<"\nPump "<<s.motor.pumpDrive;
            DrawText(info.str().c_str(),GetScreenWidth()-280,90,17,RAYWHITE);
        }
    }
    const char* names[]={"food","food odor","repellent","pheromone","temperature","oxygen","vibration"};
    DrawText(TextFormat("Tick %llu  Worms %i  Eggs %i",static_cast<unsigned long long>(simulation.currentTick()),int(simulation.population().worms().size()),int(simulation.population().eggs().size())),20,8,18,RAYWHITE);
    DrawText(TextFormat("Overlay: %s",names[overlay_]),GetScreenWidth()-280,30,18,SKYBLUE);
    DrawText("Tab overlay | Space pause | N step",20,GetScreenHeight()-22,16,RAYWHITE);EndDrawing();
}
}
