#pragma once
namespace ce {
struct SensoryState {
    float foodAttractant = 0;
    float foodAttractantDelta = 0;
    float repellent = 0;
    float repellentDelta = 0;
    float temperature = 0;
    float temperatureDelta = 0;
    float temperatureErrorToPreference = 0;
    float oxygen = 0;
    float oxygenErrorToPreference = 0;
    float noseTouch = 0;
    float bodyTouch = 0;
    float vibration = 0;
    float foodAtMouth = 0;
    float energyDeficit = 0;
    float headCurvature = 0;
    float meanBodyCurvature = 0;
    float forwardSpeed = 0;
    float recentFoodMemory = 0;
};

}
