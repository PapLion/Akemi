#include <iostream>
#include "simulation/CommandLine.h"
#include "simulation/Simulation.h"
#include "render/Renderer.h"
int main(int argc,char** argv) {
    bool window=false;
    try {
        const auto options=ce::parseCommandLine(argc,argv);ce::SimulationConfig cfg;
        ce::Simulation simulation(cfg,options.seed,options.scenario);
        if(options.headless)simulation.runTicks(options.ticks?options.ticks:250000);
        else {
            InitWindow(1200,900,"C.E-PSVAML V1");window=true;
            if(!IsWindowReady())throw std::runtime_error("raylib window initialization failed");
            SetTargetFPS(cfg.renderHz);ce::Renderer renderer(cfg);bool paused=false;
            while(!WindowShouldClose() && (!options.ticks || simulation.currentTick()<options.ticks)) {
                if(IsKeyPressed(KEY_SPACE))paused=!paused;
                const int steps=paused?(IsKeyPressed(KEY_N)?1:0):options.ticksPerFrame;
                for(int i=0;i<steps && (!options.ticks || simulation.currentTick()<options.ticks);++i)simulation.tick();
                renderer.draw(simulation);
            }
            CloseWindow();window=false;
        }
        simulation.metrics().flush(std::filesystem::path("output")/(options.scenario+"-"+std::to_string(options.seed)));
        std::cout<<"ticks="<<simulation.currentTick()<<" digest="<<simulation.stateDigest()<<" worms="<<simulation.population().worms().size()<<" eggs="<<simulation.population().eggs().size()<<" guard="<<simulation.population().guardTriggered()<<'\n';
        return simulation.population().guardTriggered()?2:0;
    } catch(const std::exception& error) {if(window)CloseWindow();std::cerr<<error.what()<<'\n';return 1;}
}
