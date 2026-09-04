# C.E-PSVAML V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the frozen C.E-PSVAML V1 as a deterministic C++/raylib 2D artificial-life simulation in which *C. elegans*-inspired organisms can sense, move, feed, metabolize, learn, develop, enter/recover from dauer, reproduce, age, die, and evolve through overlapping lineages.

**Architecture:** OOP by composition. `Simulation` owns `World`, `Population`, metrics, RNG and time; `Population` owns `Worm` and `Egg` entities; each `Worm` owns `Genome`, `Body`, `Physiology`, `SensorySystem`, `NervousSystem`, `LearningSystem`, `DevelopmentSystem`, and `ReproductiveSystem`. raylib is a read-only presentation layer over exactly the same deterministic fixed-timestep core used in headless mode.

**Tech Stack:** C++17+, CMake, raylib 2D, Catch2 + CTest, standard library RNG/containers/filesystem.

**Spec:** `C.E-PSVAML/C.E-PSVAML-V1-SPEC.md`, frozen by `C.E-PSVAML/V1-FROZEN.md` at spec blob `1b4c22d997a75e0a6d9879ac2232bb0b04f4335a`.

## Global Constraints

- Language: C++17 or newer.
- Render: raylib 2D only; renderer never mutates simulation state.
- Build: CMake.
- Simulation: fixed timestep, default `physicsHz = 50`, `fixedDt = 0.02`.
- Slow biological processes use configurable rate scales; never accelerate by increasing physics `dt`.
- Visual and headless modes use exactly the same `Simulation::tick()` core.
- RNG: one seeded engine owned by `Simulation`; all stochastic decisions use that engine or an explicitly passed reference to it.
- Initial world default: 1000 x 1000 continuous units; default field grid 128 x 128.
- Default body: 12 segments; default physics constraint iterations: 4.
- Default recurrent brain: 12 CTRNN neurons.
- Default initial population: 32.
- Default boundary mode: toroidal.
- No ECS, generic event bus, plugin framework, dependency-injection framework, generic physics engine, 3D, molecular simulation, `selectBestWorm()`, external RL reward loop, defensive-dauer button, Tank/Speedster inheritance, generation-wide reset, or world-coordinate oracle in the brain.
- V1 reproduction: self-fertile hermaphrodites only.
- V1 evolution: overlapping generations and differential reproduction; no mandatory fitness score selector.
- Learned neural state is not written back into inherited `Genome`.
- Every task uses TDD, leaves the entire test suite passing, receives a review gate, and ends with a commit.

---

# Dependency order

```text
1  Build/Test Skeleton
2  Core Types + Config + RNG
3  World Fields
4  Body / Biomechanics
5  Physiology
6  Sensory System
7  CTRNN Nervous System
8  Learning & Memory
9  Development / Dauer
10 Genome + Mutation
11 Reproduction + Egg
12 Worm Composition
13 Population + Lineage
14 Scenarios
15 Simulation + Determinism
16 Metrics + Logging
17 raylib Renderer + CLI
18 Full-Life Integration + Calibration + DoD
```

---

## Canonical core data types

These names and signatures are fixed for this plan. Later tasks consume them exactly.

```cpp
namespace ce {
using EntityId = std::uint64_t;

enum class BoundaryMode { Toroidal, Closed };
enum class DeathCause { None, Mechanical, Starvation, Thermal, Toxicity, Aging };

enum class DevelopmentStage { L1, L2, L2d, Dauer, DauerRecovery, L3, L4, Adult };
enum class DevelopmentPhase { Growing, Lethargus };

struct MotorCommand {
    float forwardDrive = 0.0f;
    float reverseDrive = 0.0f;
    float turnBias = 0.0f;
    float headSweepDrive = 0.0f;
    float pumpDrive = 0.0f;
};

struct InternalState {
    float energyDeficit = 0.0f;
    float stressLevel = 0.0f;
    float developmentContext = 0.0f;
    float recentFoodMemory = 0.0f;
};

struct ActionConsequences {
    float foodIngested = 0.0f;
    float energyAbsorbed = 0.0f;
    float damageDelta = 0.0f;
    float starvationDelta = 0.0f;
    float thermalStressDelta = 0.0f;
    float distanceMoved = 0.0f;
};
}
```

---

### Task 1: Build, test harness, and executable skeleton

**Files:**
- Create: `C.E-PSVAML/CMakeLists.txt`
- Create: `C.E-PSVAML/src/core/Version.h`
- Create: `C.E-PSVAML/src/core/Version.cpp`
- Create: `C.E-PSVAML/src/main.cpp`
- Create: `C.E-PSVAML/src/tests/CMakeLists.txt`
- Create: `C.E-PSVAML/src/tests/TestMain.cpp`

**Interfaces:**
- Consumes: none.
- Produces: `ce_psvaml_core`, `ce_psvaml`, `ce_psvaml_tests`; `ce::version()`.

- [ ] **Step 1: Write the failing smoke test**

```cpp
// src/tests/TestMain.cpp
#include <catch2/catch_test_macros.hpp>
#include "core/Version.h"

TEST_CASE("V1 core exposes a version") {
    REQUIRE(std::string(ce::version()) == "0.1.0-v1");
}
```

- [ ] **Step 2: Create CMake files before `Version.cpp` exists and verify build fails**

```cmake
# C.E-PSVAML/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(ce_psvaml LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(FetchContent)
FetchContent_Declare(raylib GIT_REPOSITORY https://github.com/raysan5/raylib.git GIT_TAG 5.5)
FetchContent_Declare(Catch2 GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG v3.8.1)
FetchContent_MakeAvailable(raylib Catch2)

enable_testing()
add_library(ce_psvaml_core STATIC src/core/Version.cpp)
target_include_directories(ce_psvaml_core PUBLIC src)
add_executable(ce_psvaml src/main.cpp)
target_link_libraries(ce_psvaml PRIVATE ce_psvaml_core raylib)
add_subdirectory(src/tests)
```

```cmake
# src/tests/CMakeLists.txt
add_executable(ce_psvaml_tests TestMain.cpp)
target_link_libraries(ce_psvaml_tests PRIVATE ce_psvaml_core Catch2::Catch2WithMain)
include(Catch)
catch_discover_tests(ce_psvaml_tests)
```

Run:
```bash
cmake -S C.E-PSVAML -B C.E-PSVAML/build
cmake --build C.E-PSVAML/build
```
Expected: FAIL because `src/core/Version.cpp` does not exist.

- [ ] **Step 3: Add the minimal version implementation and executable**

```cpp
// src/core/Version.h
#pragma once
namespace ce { const char* version(); }
```

```cpp
// src/core/Version.cpp
#include "core/Version.h"
namespace ce { const char* version() { return "0.1.0-v1"; } }
```

```cpp
// src/main.cpp
#include <iostream>
#include "core/Version.h"
int main() {
    std::cout << "C.E-PSVAML " << ce::version() << '\n';
    return 0;
}
```

- [ ] **Step 4: Build and run all tests**

Run:
```bash
cmake -S C.E-PSVAML -B C.E-PSVAML/build
cmake --build C.E-PSVAML/build
ctest --test-dir C.E-PSVAML/build --output-on-failure
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add C.E-PSVAML/CMakeLists.txt C.E-PSVAML/src
git commit -m "build: scaffold C.E-PSVAML C++ project"
```

---

### Task 2: Core types, configuration, time profile, and deterministic RNG

**Files:**
- Create: `C.E-PSVAML/src/core/Types.h`
- Create: `C.E-PSVAML/src/core/Random.h`
- Create: `C.E-PSVAML/src/core/Random.cpp`
- Create: `C.E-PSVAML/src/simulation/SimulationConfig.h`
- Create: `C.E-PSVAML/src/tests/CoreTests.cpp`
- Modify: `C.E-PSVAML/CMakeLists.txt`
- Modify: `C.E-PSVAML/src/tests/CMakeLists.txt`

**Interfaces:**
- Produces `EntityId`, `BoundaryMode`, `DeathCause`, `TimeProfile`, `MutationConfig`, `SimulationConfig`, `Random`.

- [ ] **Step 1: Write deterministic RNG and frozen-default tests**

```cpp
#include <catch2/catch_test_macros.hpp>
#include "core/Random.h"
#include "simulation/SimulationConfig.h"

TEST_CASE("same seed produces identical random stream") {
    ce::Random a(42), b(42);
    for (int i = 0; i < 100; ++i) REQUIRE(a.uniform01() == b.uniform01());
}

TEST_CASE("V1 defaults match frozen spec") {
    ce::SimulationConfig c{};
    REQUIRE(c.physicsHz == 50);
    REQUIRE(c.fixedDt == 0.02);
    REQUIRE(c.worldWidth == 1000.0f);
    REQUIRE(c.worldHeight == 1000.0f);
    REQUIRE(c.fieldGridWidth == 128);
    REQUIRE(c.fieldGridHeight == 128);
    REQUIRE(c.bodySegments == 12);
    REQUIRE(c.physicsConstraintIterations == 4);
    REQUIRE(c.brainRecurrentNeurons == 12);
    REQUIRE(c.initialPopulation == 32);
    REQUIRE(c.boundaryMode == ce::BoundaryMode::Toroidal);
}
```

- [ ] **Step 2: Run the tests and verify compile failure**

Run:
```bash
cmake --build C.E-PSVAML/build
```
Expected: FAIL because the types do not exist.

- [ ] **Step 3: Implement the exact configuration surface**

```cpp
// simulation/SimulationConfig.h
#pragma once
#include <cstddef>
#include "core/Types.h"
namespace ce {
struct TimeProfile {
    double physiologyRateScale = 1.0;
    double developmentRateScale = 1.0;
    double reproductionRateScale = 1.0;
    double agingRateScale = 1.0;
};
struct MutationConfig {
    double parameterProbability = 0.02;
    double parameterSigma = 0.03;
    double neuralProbability = 0.02;
    double neuralSigma = 0.05;
};
struct SimulationConfig {
    int physicsHz = 50;
    double fixedDt = 0.02;
    int renderHz = 60;
    float worldWidth = 1000.0f;
    float worldHeight = 1000.0f;
    int fieldGridWidth = 128;
    int fieldGridHeight = 128;
    int bodySegments = 12;
    int physicsConstraintIterations = 4;
    int brainRecurrentNeurons = 12;
    int initialPopulation = 32;
    BoundaryMode boundaryMode = BoundaryMode::Toroidal;
    std::size_t maxPopulationSafety = 10000;
    TimeProfile time{};
    MutationConfig mutation{};
};
}
```

```cpp
// core/Random.h
#pragma once
#include <cstdint>
#include <random>
namespace ce {
class Random {
public:
    explicit Random(std::uint64_t seed);
    double uniform01();
    double normal(double mean, double sigma);
    bool chance(double probability);
    std::uint64_t seed() const { return seed_; }
private:
    std::uint64_t seed_;
    std::mt19937_64 engine_;
};
}
```

`Random::chance` clamps probability to `[0,1]` and uses `uniform01()`.

- [ ] **Step 4: Run full suite**

```bash
cmake --build C.E-PSVAML/build
ctest --test-dir C.E-PSVAML/build --output-on-failure
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add C.E-PSVAML/src/core C.E-PSVAML/src/simulation/SimulationConfig.h C.E-PSVAML/src/tests C.E-PSVAML/CMakeLists.txt
git commit -m "feat: add deterministic core configuration"
```

---

### Task 3: Continuous world fields, food, chemistry, temperature, oxygen, and vibration

**Files:**
- Create: `C.E-PSVAML/src/world/ScalarField.h`
- Create: `C.E-PSVAML/src/world/ScalarField.cpp`
- Create: `C.E-PSVAML/src/world/FoodField.h`
- Create: `C.E-PSVAML/src/world/FoodField.cpp`
- Create: `C.E-PSVAML/src/world/MechanicalEnvironment.h`
- Create: `C.E-PSVAML/src/world/MechanicalEnvironment.cpp`
- Create: `C.E-PSVAML/src/world/World.h`
- Create: `C.E-PSVAML/src/world/World.cpp`
- Create: `C.E-PSVAML/src/tests/WorldTests.cpp`
- Modify: CMake source lists.

**Interfaces:**

```cpp
class ScalarField {
public:
    ScalarField(int width, int height, float worldWidth, float worldHeight, float initialValue = 0.0f);
    float sample(Vector2 position) const;
    void setCell(int x, int y, float value);
    float cell(int x, int y) const;
    void addAt(Vector2 position, float amount);
    void diffuseAndDecay(float diffusionRate, float decayRate, double dt);
};

class FoodField {
public:
    FoodField(int width, int height, float worldWidth, float worldHeight);
    float sampleDensity(Vector2 position) const;
    float sampleNutrition(Vector2 position) const;
    float sampleDigestibility(Vector2 position) const;
    float sampleToxicity(Vector2 position) const;
    void paintPatch(Vector2 center, float radius, float density, float nutrition, float digestibility, float toxicity);
    float consume(Vector2 position, float requestedMass);
    void regrow(double dt, float regrowthRate);
};
```

`World` exposes the frozen sampling/consumption/deposition API and scenario-setup mutators for uniform/linear/radial fields.

- [ ] **Step 1: Write interpolation and food mass-conservation tests**

```cpp
TEST_CASE("scalar field bilinear sample interpolates center") {
    ce::ScalarField f(2, 2, 100.0f, 100.0f, 0.0f);
    f.setCell(0,0,0.0f); f.setCell(1,0,1.0f);
    f.setCell(0,1,1.0f); f.setCell(1,1,0.0f);
    REQUIRE(f.sample({50.0f,50.0f}) == Catch::Approx(0.5f).margin(0.01f));
}

TEST_CASE("food consumption never creates negative density") {
    ce::FoodField food(16, 16, 100.0f, 100.0f);
    food.paintPatch({50,50}, 20.0f, 0.2f, 1.0f, 1.0f, 0.0f);
    const float before = food.sampleDensity({50,50});
    const float eaten = food.consume({50,50}, 1.0f);
    REQUIRE(eaten <= before);
    REQUIRE(food.sampleDensity({50,50}) >= 0.0f);
}
```

- [ ] **Step 2: Verify compile failure**

- [ ] **Step 3: Implement `ScalarField` world-to-grid mapping and bilinear interpolation**

Use clamped coordinates for closed fields. Toroidal wrapping is handled by `World::normalizePosition` before field sampling.

- [ ] **Step 4: Implement `FoodField` as four aligned scalar grids**

Density is consumed; nutrition/digestibility/toxicity are sampled properties and are not decremented independently.

- [ ] **Step 5: Implement `World` members**

```cpp
FoodField food_;
ScalarField foodOdor_;
ScalarField repellent_;
ScalarField dauerPheromone_;
ScalarField temperature_;
ScalarField oxygen_;
MechanicalEnvironment mechanical_;
```

`World::update(dt)` performs food regrowth, food-odor diffusion, pheromone diffusion/decay and vibration decay deterministically.

- [ ] **Step 6: Add tests for pheromone deposit/decay, linear temperature, oxygen sampling, and toroidal position normalization**

- [ ] **Step 7: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R World --output-on-failure
ctest --test-dir C.E-PSVAML/build --output-on-failure
git add C.E-PSVAML/src/world C.E-PSVAML/src/tests/WorldTests.cpp C.E-PSVAML/CMakeLists.txt
git commit -m "feat: implement environmental fields"
```

---

### Task 4: Segmented body, PBD/Verlet constraints, wave locomotion, and boundaries

**Files:**
- Create: `C.E-PSVAML/src/worm/MotorCommand.h`
- Create: `C.E-PSVAML/src/worm/Body.h`
- Create: `C.E-PSVAML/src/worm/Body.cpp`
- Create: `C.E-PSVAML/src/tests/PhysicsTests.cpp`

**Interfaces:**

```cpp
struct BodyParameters {
    float segmentLength = 5.0f;
    float radius = 1.5f;
    float stiffness = 0.7f;
    float structuralMassScale = 1.0f;
    float muscleStrength = 1.0f;
    float baselineWaveFrequency = 2.0f;
    float baselineWaveAmplitude = 0.35f;
    float longitudinalDrag = 0.98f;
    float lateralDrag = 0.85f;
};

class Body {
public:
    Body(Vector2 headPosition, int segmentCount, BodyParameters parameters, int constraintIterations);
    void applyMotorCommand(const MotorCommand& command);
    void updatePhysics(World& world, double dt);
    Vector2 headPosition() const;
    Vector2 midBodyPosition() const;
    const std::vector<Vector2>& bodySegments() const;
    bool headTouch() const;
    bool bodyTouch() const;
    float headCurvature() const;
    float meanBodyCurvature() const;
    float forwardSpeed() const;
    float distanceMovedLastTick() const;
    std::vector<float> segmentLengths() const;
};
```

- [ ] **Step 1: Write segment-length stability test**

```cpp
TEST_CASE("body constraints preserve segment lengths") {
    ce::SimulationConfig cfg{};
    ce::World world(cfg);
    ce::Body body({100,100}, 12, ce::BodyParameters{}, 4);
    ce::MotorCommand cmd{}; cmd.forwardDrive = 1.0f;
    for (int i=0;i<5000;++i) {
        body.applyMotorCommand(cmd);
        body.updatePhysics(world, cfg.fixedDt);
    }
    for (float length : body.segmentLengths()) {
        REQUIRE(length == Catch::Approx(5.0f).margin(0.6f));
    }
}
```

- [ ] **Step 2: Write signed forward/reverse displacement test**

```cpp
TEST_CASE("reverse drive reverses longitudinal displacement") {
    ce::SimulationConfig cfg{};
    ce::World world(cfg);
    ce::Body forward({200,200}, 12, ce::BodyParameters{}, 4);
    ce::Body reverse({200,300}, 12, ce::BodyParameters{}, 4);
    const Vector2 f0 = forward.midBodyPosition();
    const Vector2 r0 = reverse.midBodyPosition();
    ce::MotorCommand f{}; f.forwardDrive = 1.0f;
    ce::MotorCommand r{}; r.reverseDrive = 1.0f;
    for (int i=0;i<2000;++i) {
        forward.applyMotorCommand(f); forward.updatePhysics(world, cfg.fixedDt);
        reverse.applyMotorCommand(r); reverse.updatePhysics(world, cfg.fixedDt);
    }
    REQUIRE(forward.midBodyPosition().x - f0.x > 0.0f);
    REQUIRE(reverse.midBodyPosition().x - r0.x < 0.0f);
}
```

The constructor initially lays the body along +X, making signed displacement deterministic for this test.

- [ ] **Step 3: Verify failure**

- [ ] **Step 4: Implement body nodes and Verlet/PBD update**

```cpp
struct BodyNode { Vector2 position{}; Vector2 previousPosition{}; float mass = 1.0f; };
```

Update order: integrate -> split tangent/normal velocity -> drag -> target curvature -> distance constraints -> bending constraints -> boundary/collision resolution -> repeat constraints four times.

- [ ] **Step 5: Implement target wave**

```cpp
phase_ += parameters_.baselineWaveFrequency * (command_.forwardDrive - command_.reverseDrive) * dt;
const float target = parameters_.baselineWaveAmplitude
                   * std::sin(phase_ - spatialFrequency_ * float(segmentIndex))
                   + command_.turnBias * turnProfile(segmentIndex);
```

`headSweepDrive` adds a head-local oscillatory bias only to anterior segments.

- [ ] **Step 6: Add strong-turn and 10,000-tick finite-state tests**

Assert strong `turnBias` changes heading by a minimum angle without discontinuous head displacement, and every coordinate remains finite.

- [ ] **Step 7: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Physics --output-on-failure
git add C.E-PSVAML/src/worm/Body.* C.E-PSVAML/src/worm/MotorCommand.h C.E-PSVAML/src/tests/PhysicsTests.cpp
git commit -m "feat: add segmented worm biomechanics"
```

---

### Task 5: Physiology, pharyngeal pumping, digestion, reserves, DMP, stress, and mortality hazard

**Files:**
- Create: `C.E-PSVAML/src/worm/PhysiologyTypes.h`
- Create: `C.E-PSVAML/src/worm/Physiology.h`
- Create: `C.E-PSVAML/src/worm/Physiology.cpp`
- Create: `C.E-PSVAML/src/tests/PhysiologyTests.cpp`

**Interfaces:**

```cpp
struct DigestivePacket {
    float totalMass = 0.0f;
    float energyPotential = 0.0f;
    float lipidPotential = 0.0f;
    float digestibility = 1.0f;
    float toxicity = 0.0f;
    double transitRemaining = 0.0;
};

struct PhysiologyParameters {
    float baseMetabolicRate = 0.01f;
    float digestiveEfficiency = 0.8f;
    float reserveStorageEfficiency = 0.8f;
    float reserveMobilizationEfficiency = 0.7f;
    float starvationTolerance = 1.0f;
    float thermalTolerance = 1.0f;
    float gutCapacity = 1.0f;
    float defecationPeriod = 3.0f;
};
```

`Physiology` exposes the frozen methods plus `availableEnergy()`, `lipidReserve()`, `gutLoad()`, `wasteLoad()`, `starvationStress()`, `thermalStress()`, `biologicalAge()`.

- [ ] **Step 1: Write delayed-energy feeding test**

```cpp
TEST_CASE("pumping creates gut content before absorbed energy") {
    ce::SimulationConfig cfg{};
    ce::World world(cfg);
    world.food().paintPatch({50,50}, 10.0f, 1.0f, 1.0f, 1.0f, 0.0f);
    ce::Physiology p(ce::PhysiologyParameters{}, cfg.time);
    const float e0 = p.availableEnergy();
    const auto pump = p.tryPump(world, {50,50}, 1.0f, cfg.fixedDt);
    REQUIRE(pump.foodIngested > 0.0f);
    REQUIRE(p.gutLoad() > 0.0f);
    REQUIRE(p.availableEnergy() <= e0);
    for (int i=0;i<200;++i) p.updateDigestion(cfg.fixedDt);
    REQUIRE(p.availableEnergy() > e0);
}
```

- [ ] **Step 2: Write reserve-before-starvation test**

```cpp
TEST_CASE("starvation mobilizes lipid reserve before severe stress") {
    ce::SimulationConfig cfg{};
    ce::Physiology p(ce::PhysiologyParameters{}, cfg.time);
    p.setEnergyForTest(0.05f);
    p.setReserveForTest(1.0f);
    const float reserve0 = p.lipidReserve();
    for (int i=0;i<500;++i) p.updateMetabolism(0.0f, 20.0f, cfg.fixedDt, ce::Random(7));
    REQUIRE(p.lipidReserve() < reserve0);
    REQUIRE(p.starvationStress() < 0.5f);
}
```

`setEnergyForTest` and `setReserveForTest` are compiled only for the test target behind `CE_TESTING`; production code cannot arbitrarily edit physiology.

- [ ] **Step 3: Implement pumping and `DigestivePacket` queue**

`tryPump`: validate drive/capacity -> consume world food -> build packet from local food properties -> subtract pumping cost -> return `ActionConsequences` with `foodIngested`.

- [ ] **Step 4: Implement digestion/metabolism/reserves**

Use the frozen balance equation. Slow rates multiply `physiologyRateScale`; physics `dt` never changes.

- [ ] **Step 5: Implement DMP and causal damage fields**

DMP is automatic. No neural `defecate` output and no HP scalar used internally.

- [ ] **Step 6: Implement aging hazard**

Per tick hazard is derived from biological age, stress and damage; seeded `Random::chance` decides stochastic death. There is no exact `maxLifespan` kill tick.

- [ ] **Step 7: Add DMP and mortality-cause tests; run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Physiology --output-on-failure
git add C.E-PSVAML/src/worm/Physiology* C.E-PSVAML/src/tests/PhysiologyTests.cpp
git commit -m "feat: implement worm physiology"
```

---

### Task 6: Local sensory system

**Files:**
- Create: `C.E-PSVAML/src/worm/SensoryState.h`
- Create: `C.E-PSVAML/src/worm/SensorySystem.h`
- Create: `C.E-PSVAML/src/worm/SensorySystem.cpp`
- Create: `C.E-PSVAML/src/tests/SensoryTests.cpp`

**Interfaces:**

```cpp
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

class SensorySystem {
public:
    SensoryState sample(const World&, const Body&, const Physiology&, float preferredTemperature,
                        float preferredOxygen, float recentFoodMemory, double dt);
};
```

- [ ] **Step 1: Write local temporal-gradient test using two body poses**

```cpp
TEST_CASE("sensory attractant delta follows local temporal samples") {
    ce::SimulationConfig cfg{};
    ce::World world(cfg);
    world.setFoodOdorLinear({1.0f,0.0f}, 0.0f, 1.0f);
    ce::Physiology physiology(ce::PhysiologyParameters{}, cfg.time);
    ce::SensorySystem sensors;
    ce::Body b1({100,100}, 12, ce::BodyParameters{}, 4);
    ce::Body b2({120,100}, 12, ce::BodyParameters{}, 4);
    sensors.sample(world, b1, physiology, 20.0f, 0.5f, 0.0f, cfg.fixedDt);
    auto second = sensors.sample(world, b2, physiology, 20.0f, 0.5f, 0.0f, cfg.fixedDt);
    REQUIRE(second.foodAttractantDelta > 0.0f);
}
```

- [ ] **Step 2: Verify failure**

- [ ] **Step 3: Implement head/mouth/body-local sampling and normalization**

No API returns nearest-food coordinates. `temperatureErrorToPreference = temperature - preferredTemperature`; oxygen error is signed relative to configured preferred range center for V1.

- [ ] **Step 4: Add nose-touch/body-touch, vibration, curvature and interoception tests**

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Sensory --output-on-failure
git add C.E-PSVAML/src/worm/Sensory* C.E-PSVAML/src/tests/SensoryTests.cpp
git commit -m "feat: add local sensory system"
```

---

### Task 7: CTRNN nervous system and weak innate priors

**Files:**
- Create: `C.E-PSVAML/src/worm/NeuralParameters.h`
- Create: `C.E-PSVAML/src/worm/NervousSystem.h`
- Create: `C.E-PSVAML/src/worm/NervousSystem.cpp`
- Create: `C.E-PSVAML/src/tests/NervousSystemTests.cpp`

**Interfaces:**

```cpp
struct NeuralParameters {
    int inputCount = 18;
    int recurrentCount = 12;
    int outputCount = 5;
    std::vector<float> inputWeights;
    std::vector<float> recurrentWeights;
    std::vector<float> outputWeights;
    std::vector<float> biases;
    std::vector<float> timeConstants;
    static NeuralParameters baseline(int inputCount, int recurrentCount, int outputCount);
};

class NervousSystem {
public:
    explicit NervousSystem(const NeuralParameters& parameters);
    MotorCommand step(const SensoryState&, const InternalState&, double dt);
    std::vector<float>& effectiveInputWeights();
    const std::vector<float>& effectiveInputWeights() const;
    float stateNorm() const;
};
```

Input packing order is defined once in `NervousSystem.cpp` and unit-tested; it must not change silently after genome dimensions are created.

- [ ] **Step 1: Write temporal-state test**

```cpp
TEST_CASE("CTRNN keeps state after a sensory pulse") {
    ce::NervousSystem brain(ce::NeuralParameters::baseline(18,12,5));
    ce::SensoryState pulse{}; pulse.noseTouch = 1.0f;
    brain.step(pulse, ce::InternalState{}, 0.02);
    brain.step(ce::SensoryState{}, ce::InternalState{}, 0.02);
    REQUIRE(brain.stateNorm() > 0.0f);
}
```

- [ ] **Step 2: Write baseline reflex tests**

Nose touch and strong repellent must make reversal output larger than forward output; food at mouth must make pump output positive.

- [ ] **Step 3: Implement CTRNN Euler integration**

```cpp
v_[i] += dt / tau_[i] * (-v_[i] + recurrentSum + inputSum + bias_[i]);
a_[i] = std::tanh(v_[i]);
```

Map output activations to clamped `MotorCommand` fields.

- [ ] **Step 4: Implement baseline prior weights, not behavior `if/else` overrides**

- [ ] **Step 5: Add stable-range test for 100,000 recurrent steps; run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Nervous --output-on-failure
git add C.E-PSVAML/src/worm/NervousSystem* C.E-PSVAML/src/worm/NeuralParameters.h C.E-PSVAML/src/tests/NervousSystemTests.cpp
git commit -m "feat: add recurrent worm nervous system"
```

---

### Task 8: Learning and memory

**Files:**
- Create: `C.E-PSVAML/src/worm/LearningSystem.h`
- Create: `C.E-PSVAML/src/worm/LearningSystem.cpp`
- Create: `C.E-PSVAML/src/tests/LearningTests.cpp`

**Interfaces:**

```cpp
struct LearningParameters {
    float plasticityRate = 0.001f;
    float eligibilityDecay = 0.98f;
    float habituationRate = 0.01f;
    float habituationRecovery = 0.001f;
    float thermalLearningRate = 0.0001f;
};

class LearningSystem {
public:
    LearningSystem(LearningParameters parameters, float initialPreferredTemperature);
    SensoryState modulate(const SensoryState& raw, double dt);
    void updateAfterConsequences(const SensoryState&, const ActionConsequences&, NervousSystem&, double dt);
    float preferredTemperature() const;
    float recentFoodMemory() const;
    float habituationLevel() const;
    float lastInternalValence() const;
};
```

- [ ] **Step 1: Write habituation and dishabituation tests**

```cpp
TEST_CASE("repeated harmless vibration habituates and damage restores sensitivity") {
    ce::LearningSystem l(ce::LearningParameters{}, 20.0f);
    ce::SensoryState raw{}; raw.vibration = 1.0f;
    const float first = l.modulate(raw, 0.02).vibration;
    for (int i=0;i<200;++i) l.modulate(raw, 0.02);
    const float habituated = l.modulate(raw, 0.02).vibration;
    REQUIRE(habituated < first);
    ce::ActionConsequences damage{}; damage.damageDelta = 1.0f;
    ce::NervousSystem brain(ce::NeuralParameters::baseline(18,12,5));
    l.updateAfterConsequences(raw, damage, brain, 0.02);
    REQUIRE(l.modulate(raw, 0.02).vibration > habituated);
}
```

- [ ] **Step 2: Write thermal-memory test**

Repeated favorable nutrient absorption at 24°C moves preference upward from 20°C; zero nutrient absorption does not.

- [ ] **Step 3: Write associative-plasticity isolation test**

Copy baseline input weights before repeated neutral-cue + nutrient consequence pairings. Assert effective `NervousSystem` weights change while the separate `NeuralParameters` source object remains byte-for-byte/value-for-value unchanged.

- [ ] **Step 4: Implement exponential traces, habituation, eligibility traces, internal valence, food memory, and thermal memory using frozen equations**

There is no `reward(float)` method.

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Learning --output-on-failure
git add C.E-PSVAML/src/worm/LearningSystem* C.E-PSVAML/src/tests/LearningTests.cpp
git commit -m "feat: implement lifetime learning and memory"
```

---

### Task 9: Development, lethargus, L2d/dauer, and recovery

**Files:**
- Create: `C.E-PSVAML/src/worm/DevelopmentSystem.h`
- Create: `C.E-PSVAML/src/worm/DevelopmentSystem.cpp`
- Create: `C.E-PSVAML/src/tests/DevelopmentTests.cpp`

**Interfaces:**

```cpp
struct DevelopmentParameters {
    float individualRateScale = 1.0f;
    float dauerSensitivity = 1.0f;
    float stressDevelopmentPenalty = 1.0f;
};
struct DevelopmentInputs {
    float foodAvailability = 1.0f;
    float dauerPheromone = 0.0f;
    float temperature = 20.0f;
    float nutritionFactor = 1.0f;
    float stressFactor = 0.0f;
};
class DevelopmentSystem {
public:
    DevelopmentSystem(DevelopmentParameters, const TimeProfile&);
    void update(const DevelopmentInputs&, double dt);
    DevelopmentStage stage() const;
    DevelopmentPhase phase() const;
    float stageProgress() const;
    int completedLethargusCount() const;
    float targetBodyScale() const;
    float locomotionMultiplier() const;
    bool pumpingAllowed() const;
    float metabolismMultiplier() const;
    float stressResistanceMultiplier() const;
    bool isReproductivelyAdult() const;
};
```

- [ ] **Step 1: Write normal cycle test**

```cpp
TEST_CASE("normal development reaches adult through four lethargus periods") {
    ce::TimeProfile time{}; time.developmentRateScale = 100.0;
    ce::DevelopmentSystem d(ce::DevelopmentParameters{}, time);
    ce::DevelopmentInputs favorable{};
    for (int i=0;i<200000 && d.stage()!=ce::DevelopmentStage::Adult;++i) d.update(favorable, 0.02);
    REQUIRE(d.stage() == ce::DevelopmentStage::Adult);
    REQUIRE(d.completedLethargusCount() == 4);
}
```

- [ ] **Step 2: Write dauer induction and adult-non-entry tests**

Drive a larva with low food + high pheromone + unfavorable temperature until it reaches `Dauer`; separately advance a normal animal to `Adult`, then expose the same cues and assert stage remains `Adult`.

- [ ] **Step 3: Implement stage progress, lethargus, pumping/locomotion suppression, and body-scale targets**

- [ ] **Step 4: Implement `L1/L2 -> L2d -> Dauer` and sustained favorable recovery `Dauer -> DauerRecovery -> L4 -> Adult`**

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Development --output-on-failure
git add C.E-PSVAML/src/worm/DevelopmentSystem* C.E-PSVAML/src/tests/DevelopmentTests.cpp
git commit -m "feat: implement development and dauer"
```

---

### Task 10: Genome and bounded mutation

**Files:**
- Create: `C.E-PSVAML/src/worm/Genome.h`
- Create: `C.E-PSVAML/src/worm/Genome.cpp`
- Create: `C.E-PSVAML/src/tests/GenomeTests.cpp`

**Interfaces:**

`Genome` stores every inherited field in frozen spec section 10.2 and provides:

```cpp
class Genome {
public:
    static Genome baseline(int sensoryInputs, int recurrentNeurons, int outputs);
    bool validate() const;
    BodyParameters bodyParameters() const;
    PhysiologyParameters physiologyParameters() const;
    NeuralParameters neuralParameters() const;
    LearningParameters learningParameters() const;
    DevelopmentParameters developmentParameters() const;
    ReproductionParameters reproductionParameters() const;
    bool operator==(const Genome&) const = default;
};
Genome mutate(const Genome& parent, Random& rng, const MutationConfig& config);
```

`ReproductionParameters` is declared in `Genome.h` at this task and consumed by Task 11:

```cpp
struct ReproductionParameters {
    float reproductiveAllocation = 0.2f;
    float oocyteMaturationRate = 1.0f;
    float spermCapacityScale = 1.0f;
    float eggProvisionBias = 1.0f;
};
```

- [ ] **Step 1: Write genome validity and deterministic mutation tests**

```cpp
TEST_CASE("baseline genome is valid") {
    REQUIRE(ce::Genome::baseline(18,12,5).validate());
}

TEST_CASE("mutation is deterministic for same seed") {
    auto g = ce::Genome::baseline(18,12,5);
    ce::Random a(99), b(99);
    ce::MutationConfig m{};
    REQUIRE(ce::mutate(g,a,m) == ce::mutate(g,b,m));
}
```

- [ ] **Step 2: Write non-heritable-state compile/design test**

A source-level test/static assertion file includes `Genome.h` and confirms Genome exposes no `availableEnergy`, `biologicalAge`, `preferredTemperature`, `habituationLevel`, or mutable effective weight accessor. This can be enforced by keeping those symbols absent and reviewing header surface in the task gate.

- [ ] **Step 3: Implement named gene fields and conversion methods**

Use validated finite ranges for every scalar; neural arrays must have exact dimensions matching input/recurrent/output counts.

- [ ] **Step 4: Implement Gaussian mutation with separate neural sigma and clamping**

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Genome --output-on-failure
git add C.E-PSVAML/src/worm/Genome* C.E-PSVAML/src/tests/GenomeTests.cpp
git commit -m "feat: add inheritable genome and mutation"
```

---

### Task 11: Reproductive system and Egg entity

**Files:**
- Create: `C.E-PSVAML/src/worm/Egg.h`
- Create: `C.E-PSVAML/src/worm/Egg.cpp`
- Create: `C.E-PSVAML/src/worm/ReproductiveSystem.h`
- Create: `C.E-PSVAML/src/worm/ReproductiveSystem.cpp`
- Create: `C.E-PSVAML/src/tests/ReproductionTests.cpp`

**Interfaces:**

```cpp
struct EggBlueprint {
    EntityId parentId = 0;
    std::uint32_t generation = 0;
    Genome genome;
    Vector2 position{};
    float maternalProvision = 0.0f;
};

class Egg {
public:
    Egg(EntityId id, const EggBlueprint&, std::uint64_t laidTick);
    void updateEmbryogenesis(float temperature, double dt, const TimeProfile&);
    bool readyToHatch() const;
    EntityId id() const;
    EntityId parentId() const;
    std::uint32_t generation() const;
    const Genome& genome() const;
    Vector2 position() const;
    float maternalProvision() const;
};
```

`ReproductiveSystem` exposes `update`, `hasPendingEggs`, `takeLaidEggs`, `spermRemaining`, `uterineEggCount`.

- [ ] **Step 1: Write sperm-reserve and egg-production test**

```cpp
TEST_CASE("healthy adult uses sperm and eventually lays an egg") {
    ce::ReproductiveSystem r(ce::ReproductionParameters{}, ce::TimeProfile{});
    r.initializeSpermReserve(20);
    const int before = r.spermRemaining();
    ce::ReproductionInputs in{};
    in.isAdult = true; in.availableReproductiveResources = 1.0f; in.nutritionState = 1.0f;
    for (int i=0;i<100000 && !r.hasPendingEggs();++i) r.update(in, 0.02);
    REQUIRE(r.hasPendingEggs());
    REQUIRE(r.spermRemaining() < before);
    REQUIRE(r.takeLaidEggs().size() == 1);
}
```

- [ ] **Step 2: Write maternal-provisioning comparison**

Using identical parent genome and deterministic mutation-disabled configuration, healthy inputs must create higher `maternalProvision` than starved/stressed inputs while child genome remains identical.

- [ ] **Step 3: Implement late-L4 sperm initialization, adult oocyte maturation, fertilization, uterine holding, and laying**

- [ ] **Step 4: Implement Egg embryogenesis and viability stress**

Temperature/provision affect progression; no full cell lineage.

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Reproduction --output-on-failure
git add C.E-PSVAML/src/worm/Egg.* C.E-PSVAML/src/worm/ReproductiveSystem* C.E-PSVAML/src/tests/ReproductionTests.cpp
git commit -m "feat: implement hermaphrodite reproduction"
```

---

### Task 12: Compose a complete Worm object and per-worm tick

**Files:**
- Create: `C.E-PSVAML/src/worm/WormDebugState.h`
- Create: `C.E-PSVAML/src/worm/Worm.h`
- Create: `C.E-PSVAML/src/worm/Worm.cpp`
- Create: `C.E-PSVAML/src/tests/WormTests.cpp`

**Interfaces:**

```cpp
class Worm {
public:
    Worm(EntityId id, EntityId parentId, std::uint32_t generation, std::uint64_t birthTick,
         Vector2 position, const Genome& genome, const SimulationConfig& config);
    void tick(World&, double dt, Random&);
    bool isAlive() const;
    DeathCause deathCause() const;
    std::vector<EggBlueprint> takePendingEggs();
    WormDebugState getReadOnlyDebugState() const;
    EntityId id() const;
    EntityId parentId() const;
    std::uint32_t generation() const;
    const Genome& genome() const;
};
```

- [ ] **Step 1: Write construction-isolation test**

Construct two worms from the same `Genome`; induce learning only in one; assert both immutable `Genome` values remain equal while effective neural weights diverge.

- [ ] **Step 2: Write one-tick causal-order test using debug state**

`WormDebugState` contains read-only `lastConsequences` and `lastLearningValence`. Place baseline worm with food at mouth and enough time for a pump/absorption cycle. After the tick in which absorption occurs, assert `lastConsequences.energyAbsorbed > 0` and `lastLearningValence > 0`. This catches learning-before-consequence ordering because prior ticks have zero absorption.

- [ ] **Step 3: Implement constructor from Genome-derived subsystem parameters**

Mutable neural effective weights are copied from genome at birth; learned state starts fresh.

- [ ] **Step 4: Implement exact frozen per-worm tick**

```text
SensorySystem sample
-> LearningSystem modulate
-> NervousSystem step
-> Body apply/update
-> Physiology pumping/digestion/metabolism/stress/aging
-> LearningSystem consequence update
-> DevelopmentSystem update
-> apply development multipliers/state effects
-> ReproductiveSystem update
-> queue EggBlueprints / death state
```

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Worm --output-on-failure
git add C.E-PSVAML/src/worm/Worm* C.E-PSVAML/src/tests/WormTests.cpp
git commit -m "feat: compose complete worm tick"
```

---

### Task 13: Population, eggs, births, deaths, lineage, and population guard

**Files:**
- Create: `C.E-PSVAML/src/simulation/LineageRecord.h`
- Create: `C.E-PSVAML/src/simulation/Population.h`
- Create: `C.E-PSVAML/src/simulation/Population.cpp`
- Create: `C.E-PSVAML/src/tests/PopulationTests.cpp`

**Interfaces:**

```cpp
struct InitialWormBlueprint {
    Vector2 position{};
    Genome genome;
    EntityId parentId = 0;
    std::uint32_t generation = 0;
};

class Population {
public:
    explicit Population(std::size_t maxPopulationSafety);
    EntityId spawnWorm(const InitialWormBlueprint&, std::uint64_t birthTick, const SimulationConfig&);
    EntityId addEgg(const EggBlueprint&, std::uint64_t laidTick);
    void advanceEggs(const World&, double dt, const TimeProfile&);
    void hatchReadyEggs(std::uint64_t tick, const SimulationConfig&);
    void removeDeadWorms(std::uint64_t tick);
    bool guardTriggered() const;
    const std::vector<Worm>& worms() const;
    const std::vector<Egg>& eggs() const;
    const std::vector<LineageRecord>& lineageRecords() const;
    bool hasGenerationAtLeast(std::uint32_t generation) const;
};
```

- [ ] **Step 1: Write hatch/lineage test without test-only population mutation API**

```cpp
TEST_CASE("hatched child keeps parent identity and increments generation") {
    ce::SimulationConfig cfg{};
    ce::Population p(100);
    ce::InitialWormBlueprint parentBp{{100,100}, ce::Genome::baseline(18,12,5), 0, 4};
    const ce::EntityId parent = p.spawnWorm(parentBp, 0, cfg);
    ce::EggBlueprint egg{parent, 5, parentBp.genome, {100,100}, 1.0f};
    p.addEgg(egg, 1);
    for (int i=0;i<200000 && !p.hasGenerationAtLeast(5);++i) {
        p.advanceEggs(ce::World(cfg), 0.02, ce::TimeProfile{1,100,1,1});
        p.hatchReadyEggs(i+2, cfg);
    }
    REQUIRE(p.hasGenerationAtLeast(5));
    const auto& child = p.worms().back();
    REQUIRE(child.parentId() == parent);
    REQUIRE(child.generation() == 5);
}
```

Create a persistent `World world(cfg);` outside the loop in actual test to avoid reconstructing it; the loop passes that same instance.

- [ ] **Step 2: Write population safety guard test**

With max 1, spawn first worm successfully; spawning a second must set `guardTriggered()` and reject creation without killing the first.

- [ ] **Step 3: Implement overlapping worm/egg collections and monotonic entity IDs**

- [ ] **Step 4: Implement lineage records preserved after death**

`LineageRecord` stores ID, parent, generation, birth tick, optional death tick/cause and child IDs.

- [ ] **Step 5: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Population --output-on-failure
git add C.E-PSVAML/src/simulation/Population* C.E-PSVAML/src/simulation/LineageRecord.h C.E-PSVAML/src/tests/PopulationTests.cpp
git commit -m "feat: add population and lineage lifecycle"
```

---

### Task 14: Scenario factory for every frozen V1 assay

**Files:**
- Create: `C.E-PSVAML/src/simulation/Scenario.h`
- Create: `C.E-PSVAML/src/simulation/Scenario.cpp`
- Create: `C.E-PSVAML/src/tests/ScenarioTests.cpp`

**Interfaces:**

```cpp
class Scenario {
public:
    static std::vector<std::string> requiredV1Names();
    static bool apply(std::string_view name, World&, Population&, Random&, const SimulationConfig&);
};
```

Required names: `baseline_ecosystem`, `chemotaxis_assay`, `thermotaxis_assay`, `aerotaxis_assay`, `nose_touch_assay`, `habituation_assay`, `associative_learning_assay`, `starvation_assay`, `dauer_induction_assay`, `dauer_recovery_assay`, `reproduction_assay`.

- [ ] **Step 1: Write required-name creation test**

```cpp
TEST_CASE("all frozen V1 scenarios initialize") {
    ce::SimulationConfig cfg{};
    for (const auto& name : ce::Scenario::requiredV1Names()) {
        ce::World world(cfg);
        ce::Population population(1000);
        ce::Random rng(123);
        REQUIRE(ce::Scenario::apply(name, world, population, rng, cfg));
    }
}
```

- [ ] **Step 2: Implement every scenario with explicit field/population setup**

Examples: chemotaxis = attractive gradient + one baseline worm; thermotaxis = temperature gradient + controlled food context; habituation = repeated harmless mechanical source; dauer induction = low food + high pheromone + unfavorable temperature; reproduction = healthy adult with sperm reserve and food.

- [ ] **Step 3: Unknown scenario returns false and mutates nothing**

Add a test for `"does_not_exist"`.

- [ ] **Step 4: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Scenario --output-on-failure
git add C.E-PSVAML/src/simulation/Scenario* C.E-PSVAML/src/tests/ScenarioTests.cpp
git commit -m "feat: add deterministic V1 scenarios"
```

---

### Task 15: Simulation core and determinism

**Files:**
- Create: `C.E-PSVAML/src/simulation/Simulation.h`
- Create: `C.E-PSVAML/src/simulation/Simulation.cpp`
- Create: `C.E-PSVAML/src/tests/SimulationTests.cpp`

**Interfaces:**

```cpp
class Simulation {
public:
    Simulation(SimulationConfig config, std::uint64_t seed, std::string scenarioName);
    void tick();
    void runTicks(std::uint64_t count);
    std::uint64_t currentTick() const;
    double simulatedPhysicsTime() const;
    std::uint64_t stateDigest() const;
    const World& world() const;
    const Population& population() const;
    World& worldForScenarioSetup();
    Population& populationForScenarioSetup();
};
```

The two mutable setup accessors are only used during construction/scenario initialization and are not exposed to Renderer.

- [ ] **Step 1: Write exact fixed-tick test**

```cpp
TEST_CASE("runTicks advances exact fixed time") {
    ce::Simulation s(ce::SimulationConfig{}, 123, "baseline_ecosystem");
    s.runTicks(1000);
    REQUIRE(s.currentTick() == 1000);
    REQUIRE(s.simulatedPhysicsTime() == Catch::Approx(20.0));
}
```

- [ ] **Step 2: Write same-seed digest test**

```cpp
TEST_CASE("same seed and scenario produce same state digest") {
    ce::Simulation a(ce::SimulationConfig{}, 777, "baseline_ecosystem");
    ce::Simulation b(ce::SimulationConfig{}, 777, "baseline_ecosystem");
    a.runTicks(10000); b.runTicks(10000);
    REQUIRE(a.stateDigest() == b.stateDigest());
}
```

- [ ] **Step 3: Implement exact global tick order**

```text
++tick
World::update
for each Worm: Worm::tick
collect pending EggBlueprints into Population
Population::advanceEggs
Population::hatchReadyEggs
capture death state then Population::removeDeadWorms
metrics hook added in Task 16
```

Iterate worms in stable vector order and never use unordered-container iteration to drive simulation decisions.

- [ ] **Step 4: Implement debugging `stateDigest()`**

Hash tick, world field samples/checksums, entity IDs, development stages, quantized physiology values, quantized body node coordinates, egg states and lineage counts in deterministic order.

- [ ] **Step 5: Add different-seed-diverges test; run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Simulation --output-on-failure
git add C.E-PSVAML/src/simulation/Simulation* C.E-PSVAML/src/tests/SimulationTests.cpp
git commit -m "feat: implement deterministic simulation core"
```

---

### Task 16: Metrics, CSV logging, events, and post-hoc behavior classification

**Files:**
- Create: `C.E-PSVAML/src/simulation/BehaviorClassifier.h`
- Create: `C.E-PSVAML/src/simulation/BehaviorClassifier.cpp`
- Create: `C.E-PSVAML/src/simulation/MetricsRecorder.h`
- Create: `C.E-PSVAML/src/simulation/MetricsRecorder.cpp`
- Create: `C.E-PSVAML/src/tests/MetricsTests.cpp`
- Modify: `Simulation.h/.cpp` to own/call recorder.

**Interfaces:**
- `MetricsRecorder::sample(const Simulation&)`
- `MetricsRecorder::recordBirth(...)`
- `MetricsRecorder::recordDeath(...)`
- `MetricsRecorder::flush(const std::filesystem::path&)`
- `BehaviorClassifier::classify(const WormDebugState&)` returning telemetry label only.

- [ ] **Step 1: Write exact CSV-header test in a temporary directory**

Individual summary must include the frozen fields: birth/death ticks/cause, lifetime, food, absorbed energy, distance, reversals, strong turns, dwelling/roaming estimates, dauer time, eggs laid/hatched, child IDs, maximum descendant generation. Population series must include population/egg counts, births/deaths, stage distribution, mean energy/reserve/age, dauer count, lineage diversity, trait means/variance.

- [ ] **Step 2: Implement in-memory snapshots before file writing**

- [ ] **Step 3: Implement CSV and text event output using `std::ofstream`**

No database dependency.

- [ ] **Step 4: Implement BehaviorClassifier from speed, reversal rate, turn rate, pumping and food memory**

It never modifies `Worm`, `Brain`, or simulation decisions.

- [ ] **Step 5: Wire metrics at the frozen tick location after births/deaths are resolved**

- [ ] **Step 6: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Metrics --output-on-failure
git add C.E-PSVAML/src/simulation C.E-PSVAML/src/tests/MetricsTests.cpp
git commit -m "feat: add metrics and deterministic logging"
```

---

### Task 17: raylib renderer, debug overlays, CLI, and headless execution

**Files:**
- Create: `C.E-PSVAML/src/render/Renderer.h`
- Create: `C.E-PSVAML/src/render/Renderer.cpp`
- Create: `C.E-PSVAML/src/simulation/CommandLine.h`
- Create: `C.E-PSVAML/src/simulation/CommandLine.cpp`
- Replace: `C.E-PSVAML/src/main.cpp`
- Create: `C.E-PSVAML/src/tests/CommandLineTests.cpp`

**Interfaces:**

```cpp
struct CommandLineOptions {
    bool headless = false;
    std::uint64_t seed = 1;
    std::string scenario = "baseline_ecosystem";
    std::uint64_t ticks = 0;
    int ticksPerFrame = 1;
};
CommandLineOptions parseCommandLine(int argc, char** argv);

class Renderer {
public:
    explicit Renderer(const SimulationConfig&);
    void draw(const Simulation& simulation);
};
```

- [ ] **Step 1: Write complete CLI parse test**

```cpp
TEST_CASE("CLI parses headless seed scenario ticks and speed") {
    const char* raw[] = {"ce_psvaml","--headless","--seed","42","--scenario","chemotaxis_assay","--ticks","1000","--speed","50"};
    auto argv = const_cast<char**>(raw);
    auto o = ce::parseCommandLine(10, argv);
    REQUIRE(o.headless);
    REQUIRE(o.seed == 42);
    REQUIRE(o.scenario == "chemotaxis_assay");
    REQUIRE(o.ticks == 1000);
    REQUIRE(o.ticksPerFrame == 50);
}
```

- [ ] **Step 2: Implement parser with explicit error messages for malformed numeric arguments and unknown flags**

- [ ] **Step 3: Implement read-only Renderer**

Draw polyline/thick body segments, distinct head, food density, optional overlays for food odor/repellent/pheromone/temperature/oxygen/vibration, and selected-worm debug fields from frozen spec. Renderer receives `const Simulation&` only.

- [ ] **Step 4: Implement `main` paths**

Headless never calls `InitWindow`; it constructs `Simulation`, runs requested ticks or until safety guard, flushes metrics, exits.

Visual initializes raylib, executes `ticksPerFrame` fixed ticks each frame, then draws. Pausing/single-step can be mapped to keyboard controls without changing `fixedDt`.

- [ ] **Step 5: Add headless process smoke test through CTest**

CMake test command:
```cmake
add_test(NAME headless_smoke COMMAND ce_psvaml --headless --seed 1 --scenario baseline_ecosystem --ticks 10000)
```
Expected: exit 0 on a machine without a display server.

- [ ] **Step 6: Run and commit**

```bash
ctest --test-dir C.E-PSVAML/build --output-on-failure
git add C.E-PSVAML/src/render C.E-PSVAML/src/simulation/CommandLine* C.E-PSVAML/src/main.cpp C.E-PSVAML/src/tests/CommandLineTests.cpp C.E-PSVAML/CMakeLists.txt
git commit -m "feat: add raylib viewer and headless runner"
```

---

### Task 18: Full-life integration, all biological assays, calibration, and V1 Definition of Done

**Files:**
- Create: `C.E-PSVAML/src/tests/BehaviorTests.cpp`
- Create: `C.E-PSVAML/src/tests/FullLifeTests.cpp`
- Create: `C.E-PSVAML/config/v1-defaults.md`
- Create: `C.E-PSVAML/README.md`
- Modify only calibrated configuration/baseline constants where measurement requires it.

**Interfaces:**
- Consumes: complete V1.
- Produces: acceptance evidence for frozen spec sections 14–15 and calibrated compressed time profile.

- [ ] **Step 1: Implement chemotaxis acceptance test**

Run a fixed set of seeds in `chemotaxis_assay`. Measure net occupancy/time or displacement toward increasing attractant versus mirrored controls. Require the baseline/prior controller to perform above mirrored-control median while receiving only local concentration/delta signals.

- [ ] **Step 2: Implement nose-touch and habituation acceptance tests**

Nose touch must raise reversal tendency. Repeated harmless mechanical stimuli must reduce mean response over windows; an actual damage consequence must increase response again.

- [ ] **Step 3: Implement associative-learning acceptance test**

Pair a neutral cue with nutrient absorption in one group and present cue unpaired in a control group. Assert larger effective input-weight change and cue-driven behavior change in paired group; assert both original `Genome` values unchanged.

- [ ] **Step 4: Implement thermotaxis and aerotaxis acceptance tests**

Thermal preference shifts under prolonged favorable feeding temperature; oxygen error changes sign around preferred range and can alter motor output without exposing position.

- [ ] **Step 5: Implement starvation and DMP acceptance tests**

No food: available energy decreases -> reserves mobilize -> starvation stress rises -> sustained starvation can kill. Fed animal: waste accumulates and automatic DMP reduces waste at configured period.

- [ ] **Step 6: Implement full development/dauer tests**

Normal viable egg reaches `L1 -> L2 -> L3 -> L4 -> Adult` with four lethargus periods. Dauer-inducing scenario reaches `L2d -> Dauer`; adult never jumps into Dauer. Recovery reaches `DauerRecovery -> L4 -> Adult` under sustained favorable conditions.

- [ ] **Step 7: Implement full reproduction/hatch/lineage test**

```cpp
TEST_CASE("a viable lineage completes one full generation") {
    ce::SimulationConfig cfg{};
    cfg.time.developmentRateScale = 100.0;
    cfg.time.reproductionRateScale = 100.0;
    ce::Simulation sim(cfg, 424242, "reproduction_assay");
    bool reached = false;
    for (std::uint64_t i=0; i<250000; ++i) {
        sim.tick();
        if (sim.population().hasGenerationAtLeast(1)) { reached = true; break; }
    }
    REQUIRE(reached);
    REQUIRE(sim.population().lineageRecords().size() >= 2);
}
```

- [ ] **Step 8: Implement differential-reproduction evolution smoke test without score selection**

Create a deterministic test fixture with two founders. Founder A starts adjacent to a sustainable food patch; Founder B starts in a food-poor region. Mutation is enabled. Run long enough for A to produce descendants while B may fail or produce fewer. Assert:

```text
children(A) > children(B)
no selectBestWorm API exists
at least one child genome differs from parent within legal bounds when mutation fires
population contains overlapping generations during the run
```

This verifies the mechanism of differential reproduction without demanding a particular long-run evolutionary optimum.

- [ ] **Step 9: Implement visual-schedule/headless-schedule equality test**

Run simulation A as 10,000 consecutive ticks. Run simulation B as 100 groups of 100 ticks with a no-op read-only state inspection between groups, mimicking render scheduling. Require identical `stateDigest()`.

- [ ] **Step 10: Calibrate the compressed V1 TimeProfile**

Measure baseline favorable runs and adjust slow-rate defaults only until approximate engineering targets are met:

```text
Egg -> Adult          24,000–36,000 ticks
Adult median life     60,000–90,000 ticks
Fed DMP               100–200 ticks
```

Do not change `fixedDt` to hit these targets.

- [ ] **Step 11: Run full verification**

```bash
cmake -S C.E-PSVAML -B C.E-PSVAML/build
cmake --build C.E-PSVAML/build -j
ctest --test-dir C.E-PSVAML/build --output-on-failure
C.E-PSVAML/build/ce_psvaml --headless --seed 12345 --scenario baseline_ecosystem --ticks 250000
```

Expected: all tests PASS, no NaN/Inf states, baseline does not hit population safety guard, headless exits 0, CSV/event outputs are created.

- [ ] **Step 12: Create `README.md` verification matrix for frozen DoD 1–35**

Every DoD line maps to at least one named test or runtime check. Use exact entries rather than generic claims, for example:

```text
DoD 1  -> WorldTests: continuous fields + ScenarioTests: baseline_ecosystem
DoD 3  -> PhysicsTests: body constraints / forward / reverse / strong turn
DoD 13 -> LearningTests: repeated harmless vibration habituates
DoD 18 -> DevelopmentTests: dauer induction
DoD 24 -> GenomeTests + PopulationTests: inheritance with bounded mutation
DoD 31 -> FullLifeTests: grouped-read schedule equals headless digest
DoD 34 -> SimulationConfig tests + temporal calibration measurements
```

- [ ] **Step 13: Document build/run commands and calibrated defaults**

```bash
cmake -S C.E-PSVAML -B C.E-PSVAML/build
cmake --build C.E-PSVAML/build -j
ctest --test-dir C.E-PSVAML/build --output-on-failure
C.E-PSVAML/build/ce_psvaml --scenario baseline_ecosystem --seed 1
C.E-PSVAML/build/ce_psvaml --headless --scenario baseline_ecosystem --seed 1 --ticks 250000
```

- [ ] **Step 14: Final commit**

```bash
git add C.E-PSVAML
git commit -m "feat: complete C.E-PSVAML V1 simulation"
```

---

# Review gate after every task

Before starting the next task:

1. run the task-specific tests;
2. run the entire suite;
3. inspect the diff for unrelated work;
4. verify no frozen design requirement changed silently;
5. check new public interfaces against the canonical names in this plan;
6. commit the accepted task.

If implementation discovers a contradiction in the frozen spec, stop and record exactly:

```text
Frozen requirement: <quote or section>
Observed contradiction: <reproducible technical reason>
Minimal proposed deviation: <single concrete change>
Affected files/tests: <exact paths and test names>
```

Then obtain approval before changing the frozen design baseline.

---

# Spec coverage self-review

| Frozen area | Implementation evidence |
|---|---|
| OOP composition, build, fixed timing | Tasks 1–2, 12, 15 |
| World, food, chemistry, temperature, oxygen, mechanics | Task 3 |
| Segmented body, forward/reversal/turn/head sweep | Task 4 |
| Pumping, digestion, energy, reserves, DMP, stress, aging/death | Task 5 |
| Local quimio/thermo/mechano/proprio/aerotaxis/interoception | Task 6 |
| CTRNN, recurrent state, weak innate priors | Task 7 |
| Habituation, association, thermal and food memory | Task 8 |
| Egg-L1-L2-L3-L4-Adult, lethargus, L2d, dauer/recovery | Tasks 9, 11 |
| Inherited traits and bounded mutation | Task 10 |
| Hermaphrodite sperm/oocytes/fertilization/provisioning/laying/embryogenesis | Task 11 |
| Whole-organism causal tick | Task 12 |
| Eggs, hatch, overlapping generations, lineage, population guard | Task 13 |
| All named V1 scenarios | Task 14 |
| Global tick order, fixed timestep, deterministic replay | Task 15 |
| Metrics, CSV, events, post-hoc behavior labels | Task 16 |
| raylib visual mode, field overlays, selected-worm debug, headless | Task 17 |
| Every behavioral assay, temporal calibration, natural differential reproduction, DoD 1–35 | Task 18 |

No frozen V1 subsystem is intentionally omitted.

---

# Placeholder and type-consistency self-review

- No implementation step uses `TBD`, `TODO`, “implement later”, or an unspecified error-handling instruction.
- Tests with setup helpers either use production scenario/setup APIs or explicitly define `CE_TESTING`-only physiology setters.
- `DevelopmentInputs`, `ReproductionParameters`, `EggBlueprint`, `InitialWormBlueprint`, `MotorCommand`, `SensoryState`, `InternalState`, and `ActionConsequences` are defined before their downstream use.
- `Simulation` constructor is canonical everywhere: `Simulation(SimulationConfig, std::uint64_t seed, std::string scenarioName)`.
- Tests use `src/tests/`, matching the frozen proposed project tree.
- `Scenario::apply` initializes `World` and `Population` before `Simulation` begins ticking.
- `Renderer` has no mutable simulation interface.
- Task 18 checks behavior statistically/deterministically without introducing an external reward or mandatory fitness selector.

---

# Canonical per-tick data flow

```text
World + Body + Physiology
    -> SensorySystem -> raw SensoryState
    -> LearningSystem::modulate
    -> NervousSystem + InternalState -> MotorCommand
    -> Body biomechanics + Physiology feeding/action cost
    -> Physiology digestion/metabolism/stress/aging -> ActionConsequences
    -> LearningSystem::updateAfterConsequences
    -> DevelopmentSystem
    -> ReproductiveSystem -> EggBlueprint[]
    -> Population -> Egg -> Worm
```

---

# Execution handoff

Recommended implementation mode: **Subagent-Driven Development**. Use one fresh worker per task, run a specification-compliance review and a code-quality review before accepting each task, and keep the commits isolated so failures are easy to bisect.
