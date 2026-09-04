# C.E-PSVAML V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the frozen C.E-PSVAML V1 as a deterministic C++/raylib 2D artificial-life simulation in which *C. elegans*-inspired organisms can sense, move, feed, metabolize, learn, develop, enter/recover from dauer, reproduce, age, die, and evolve through overlapping lineages.

**Architecture:** OOP by composition. `Simulation` owns `World`, `Population`, metrics, RNG and time; `Population` owns `Worm` and `Egg` entities; each `Worm` owns `Genome`, `Body`, `Physiology`, `SensorySystem`, `NervousSystem`, `LearningSystem`, `DevelopmentSystem`, and `ReproductiveSystem`. raylib is read-only presentation over the same deterministic fixed-timestep core used by headless mode.

**Tech Stack:** C++17+, CMake, raylib 2D, Catch2 + CTest, standard library RNG/containers/filesystem.

**Spec:** `C.E-PSVAML/C.E-PSVAML-V1-SPEC.md` frozen by `C.E-PSVAML/V1-FROZEN.md` at spec blob `1b4c22d997a75e0a6d9879ac2232bb0b04f4335a`.

## Global Constraints

- Language: C++17 or newer.
- Render: raylib 2D only; renderer never mutates simulation state.
- Build: CMake.
- Simulation: fixed timestep, default `physicsHz = 50`, `fixedDt = 0.02`.
- Slow biological processes use configurable rate scales; never accelerate by increasing physics `dt`.
- Visual and headless modes use exactly the same `Simulation::tick()` core.
- RNG: one seeded engine owned by `Simulation`; random decisions must flow through it.
- Initial world default: 1000 x 1000 continuous units; default field grid 128 x 128.
- Default body: 12 segments; default physics constraint iterations: 4.
- Default recurrent brain: 12 CTRNN neurons.
- Default initial population: 32.
- Default boundary mode: toroidal.
- No ECS, event bus, plugin framework, generic physics engine, 3D, molecular simulation, artificial `selectBestWorm()`, external reward loop, defensive-dauer button, or Tank/Speedster inheritance rules.
- V1 reproduction: self-fertile hermaphrodites only.
- V1 evolution: overlapping generations and differential reproduction; no mandatory fitness score selector.
- Learned neural state is not written back into inherited `Genome`.
- Every task uses TDD, must leave tests passing, and ends with a commit.

---

# Implementation dependency map

```text
1 Build/Test Skeleton
  -> 2 Core Types + Config + RNG
  -> 3 Scalar Fields + World
  -> 4 Body / Biomechanics
  -> 5 Physiology
  -> 6 Sensory System
  -> 7 CTRNN Nervous System
  -> 8 Learning & Memory
  -> 9 Development / Dauer
  -> 10 Genome + Mutation
  -> 11 Reproduction + Egg
  -> 12 Worm Orchestration
  -> 13 Population + Lineage
  -> 14 Simulation Tick + Determinism
  -> 15 Scenarios + Acceptance Assays
  -> 16 Metrics + Logging
  -> 17 raylib Renderer + CLI
  -> 18 Full-Life Integration + Calibration
```

---

### Task 1: Build, test harness, and executable skeleton

**Files:**
- Create: `C.E-PSVAML/CMakeLists.txt`
- Create: `C.E-PSVAML/src/main.cpp`
- Create: `C.E-PSVAML/tests/CMakeLists.txt`
- Create: `C.E-PSVAML/tests/TestMain.cpp`

**Interfaces:**
- Consumes: none.
- Produces: `ce_psvaml_core` library target, `ce_psvaml` executable, `ce_psvaml_tests` test target.

- [ ] **Step 1: Write the failing smoke test**

```cpp
// tests/TestMain.cpp
#include <catch2/catch_test_macros.hpp>

TEST_CASE("test harness is alive") {
    REQUIRE(1 + 1 == 2);
}
```

- [ ] **Step 2: Add CMake configuration with Catch2 and raylib, then run before source targets exist**

```cmake
cmake_minimum_required(VERSION 3.20)
project(ce_psvaml LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(raylib GIT_REPOSITORY https://github.com/raysan5/raylib.git GIT_TAG 5.5)
FetchContent_Declare(Catch2 GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG v3.8.1)
FetchContent_MakeAvailable(raylib Catch2)

enable_testing()
add_library(ce_psvaml_core STATIC src/placeholder.cpp)
target_include_directories(ce_psvaml_core PUBLIC src)
add_executable(ce_psvaml src/main.cpp)
target_link_libraries(ce_psvaml PRIVATE ce_psvaml_core raylib)
add_subdirectory(tests)
```

```cmake
# tests/CMakeLists.txt
add_executable(ce_psvaml_tests TestMain.cpp)
target_link_libraries(ce_psvaml_tests PRIVATE ce_psvaml_core Catch2::Catch2WithMain)
include(Catch)
catch_discover_tests(ce_psvaml_tests)
```

Run:
```bash
cmake -S C.E-PSVAML -B C.E-PSVAML/build
cmake --build C.E-PSVAML/build
ctest --test-dir C.E-PSVAML/build --output-on-failure
```
Expected: configuration/build fails because `src/placeholder.cpp` does not yet exist.

- [ ] **Step 3: Add minimal source skeleton**

```cpp
// src/placeholder.cpp
namespace ce_psvaml { void core_link_anchor() {} }
```

```cpp
// src/main.cpp
#include <iostream>
int main() {
    std::cout << "C.E-PSVAML V1\n";
    return 0;
}
```

- [ ] **Step 4: Build and verify tests pass**

Run:
```bash
cmake --build C.E-PSVAML/build
ctest --test-dir C.E-PSVAML/build --output-on-failure
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add C.E-PSVAML/CMakeLists.txt C.E-PSVAML/src C.E-PSVAML/tests
git commit -m "build: scaffold C.E-PSVAML C++ project"
```

---

### Task 2: Core math types, configuration, time profile, and deterministic RNG

**Files:**
- Create: `C.E-PSVAML/src/core/Types.h`
- Create: `C.E-PSVAML/src/core/Random.h`
- Create: `C.E-PSVAML/src/core/Random.cpp`
- Create: `C.E-PSVAML/src/simulation/SimulationConfig.h`
- Create: `C.E-PSVAML/tests/CoreTests.cpp`
- Modify: `C.E-PSVAML/CMakeLists.txt`
- Modify: `C.E-PSVAML/tests/CMakeLists.txt`

**Interfaces:**
- Consumes: standard library.
- Produces:
  - `using EntityId = std::uint64_t;`
  - `enum class BoundaryMode { Toroidal, Closed };`
  - `struct TimeProfile { double physiologyRateScale, developmentRateScale, reproductionRateScale, agingRateScale; };`
  - `struct SimulationConfig` with frozen defaults.
  - `class Random { double uniform01(); double normal(double mean,double sigma); bool chance(double p); std::uint64_t seed() const; }`.

- [ ] **Step 1: Write deterministic RNG/config tests**

```cpp
#include <catch2/catch_test_macros.hpp>
#include "core/Random.h"
#include "simulation/SimulationConfig.h"

TEST_CASE("same seed produces same random stream") {
    ce::Random a(42), b(42);
    for (int i = 0; i < 100; ++i) REQUIRE(a.uniform01() == b.uniform01());
}

TEST_CASE("frozen V1 defaults are loaded") {
    ce::SimulationConfig c{};
    REQUIRE(c.physicsHz == 50);
    REQUIRE(c.fixedDt == 0.02);
    REQUIRE(c.worldWidth == 1000.0f);
    REQUIRE(c.worldHeight == 1000.0f);
    REQUIRE(c.fieldGridWidth == 128);
    REQUIRE(c.bodySegments == 12);
    REQUIRE(c.initialPopulation == 32);
    REQUIRE(c.boundaryMode == ce::BoundaryMode::Toroidal);
}
```

- [ ] **Step 2: Run focused test and verify failure**

Run:
```bash
ctest --test-dir C.E-PSVAML/build -R "same seed|frozen V1" --output-on-failure
```
Expected: compile failure because types do not exist.

- [ ] **Step 3: Implement types/config/RNG minimally**

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
    bool chance(double p);
    std::uint64_t seed() const { return seed_; }
private:
    std::uint64_t seed_;
    std::mt19937_64 engine_;
};
}
```

```cpp
// simulation/SimulationConfig.h
#pragma once
#include "core/Types.h"
namespace ce {
struct TimeProfile { double physiologyRateScale=1.0, developmentRateScale=1.0, reproductionRateScale=1.0, agingRateScale=1.0; };
struct SimulationConfig {
    int physicsHz = 50;
    double fixedDt = 0.02;
    int renderHz = 60;
    float worldWidth = 1000.0f, worldHeight = 1000.0f;
    int fieldGridWidth = 128, fieldGridHeight = 128;
    int bodySegments = 12;
    int physicsConstraintIterations = 4;
    int brainRecurrentNeurons = 12;
    int initialPopulation = 32;
    BoundaryMode boundaryMode = BoundaryMode::Toroidal;
    std::size_t maxPopulationSafety = 10000;
    TimeProfile time{};
};
}
```

- [ ] **Step 4: Run tests**

Run:
```bash
cmake --build C.E-PSVAML/build && ctest --test-dir C.E-PSVAML/build --output-on-failure
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add C.E-PSVAML/src/core C.E-PSVAML/src/simulation C.E-PSVAML/tests/CoreTests.cpp C.E-PSVAML/CMakeLists.txt C.E-PSVAML/tests/CMakeLists.txt
git commit -m "feat: add deterministic core configuration"
```

---

### Task 3: Scalar fields, food, chemistry, temperature, oxygen, vibration, and World

**Files:**
- Create: `C.E-PSVAML/src/world/ScalarField.h`
- Create: `C.E-PSVAML/src/world/ScalarField.cpp`
- Create: `C.E-PSVAML/src/world/FoodField.h`
- Create: `C.E-PSVAML/src/world/FoodField.cpp`
- Create: `C.E-PSVAML/src/world/MechanicalEnvironment.h`
- Create: `C.E-PSVAML/src/world/MechanicalEnvironment.cpp`
- Create: `C.E-PSVAML/src/world/World.h`
- Create: `C.E-PSVAML/src/world/World.cpp`
- Create: `C.E-PSVAML/tests/WorldTests.cpp`

**Interfaces:**
- Consumes: `SimulationConfig`, `Vector2` from raylib only as math POD.
- Produces:
  - `ScalarField::sample(Vector2)`, `setCell`, `addAt`, `diffuseAndDecay`.
  - `FoodField::sample`, `consume`, `regrow`.
  - `World::sampleFood`, `consumeFood`, `sampleFoodOdor`, `sampleRepellent`, `samplePheromone`, `sampleTemperature`, `sampleOxygen`, `sampleVibration`, `depositPheromone`, `update`.

- [ ] **Step 1: Write field interpolation, food consumption, and world-update tests**

```cpp
TEST_CASE("scalar field bilinear sampling interpolates") {
    ce::ScalarField f(2, 2, 100.0f, 100.0f, 0.0f);
    f.setCell(0,0,0.0f); f.setCell(1,0,1.0f);
    f.setCell(0,1,1.0f); f.setCell(1,1,0.0f);
    REQUIRE(f.sample({50,50}) == Catch::Approx(0.5f).margin(0.01f));
}

TEST_CASE("food cannot be consumed below zero") {
    ce::FoodField food(...);
    food.setDensityAt({10,10}, 0.2f);
    const float eaten = food.consume({10,10}, 1.0f);
    REQUIRE(eaten == Catch::Approx(0.2f));
    REQUIRE(food.sampleDensity({10,10}) == Catch::Approx(0.0f));
}
```

- [ ] **Step 2: Run tests to verify failure**

Run:
```bash
cmake --build C.E-PSVAML/build
```
Expected: compile failure because world classes do not exist.

- [ ] **Step 3: Implement `ScalarField` with normalized world-to-grid coordinates and bilinear interpolation**

Core behavior:
```cpp
float ScalarField::sample(Vector2 p) const {
    const float gx = std::clamp(p.x / worldWidth_ * (width_-1), 0.0f, float(width_-1));
    const float gy = std::clamp(p.y / worldHeight_ * (height_-1), 0.0f, float(height_-1));
    // floor/ceil + lerp four cells
}
```

- [ ] **Step 4: Implement `FoodField`, chemical fields, temperature/oxygen fields and mechanical vibration decay in `World::update(dt)`**

Use explicit members:
```cpp
FoodField food_;
ScalarField foodOdor_, repellent_, dauerPheromone_, temperature_, oxygen_, vibration_;
```

`World::update(dt)` must call food regrowth and diffusion/decay using deterministic loops only.

- [ ] **Step 5: Run world tests and full suite**

Run:
```bash
ctest --test-dir C.E-PSVAML/build -R World --output-on-failure
ctest --test-dir C.E-PSVAML/build --output-on-failure
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add C.E-PSVAML/src/world C.E-PSVAML/tests/WorldTests.cpp
git commit -m "feat: implement environmental scalar fields"
```

---

### Task 4: Segmented Body, Verlet/PBD constraints, locomotor wave, collisions

**Files:**
- Create: `C.E-PSVAML/src/worm/Body.h`
- Create: `C.E-PSVAML/src/worm/Body.cpp`
- Create: `C.E-PSVAML/src/worm/MotorCommand.h`
- Create: `C.E-PSVAML/tests/PhysicsTests.cpp`

**Interfaces:**
- Consumes: `World`, `SimulationConfig`.
- Produces:
  - `struct MotorCommand { float forwardDrive, reverseDrive, turnBias, headSweepDrive, pumpDrive; }`.
  - `Body::applyMotorCommand`, `updatePhysics`, `headPosition`, `midBodyPosition`, `segments`, `headTouch`, `bodyTouch`, `headCurvature`, `meanCurvature`, `forwardSpeed`, `distanceMovedLastTick`.

- [ ] **Step 1: Write tests for segment constraints and forward/reverse displacement**

```cpp
TEST_CASE("body constraints preserve segment length") {
    ce::Body body = ce::Body::makeStraight({100,100}, 12, 5.0f);
    ce::World world = ce::World::uniformForTests();
    ce::MotorCommand cmd{1,0,0,0,0};
    for (int i=0;i<500;++i) { body.applyMotorCommand(cmd); body.updatePhysics(world, 0.02); }
    for (auto d : body.segmentLengths()) REQUIRE(d == Catch::Approx(5.0f).margin(0.5f));
}

TEST_CASE("reverse drive moves opposite body heading") {
    // compare signed displacement after equal forward and reverse trials
}
```

- [ ] **Step 2: Run and verify failure**

Run:
```bash
cmake --build C.E-PSVAML/build
```
Expected: compile failure.

- [ ] **Step 3: Implement body nodes and PBD/Verlet update**

Use:
```cpp
struct BodyNode { Vector2 position; Vector2 previousPosition; float mass = 1.0f; };
```

Update order inside `Body::updatePhysics`:
```text
integrate -> effective drag -> motor curvature targets -> distance constraints -> bending constraints -> world boundary/collision -> repeat constraints N times
```

- [ ] **Step 4: Implement wave generator**

```cpp
float phaseSpeed = baselineFrequency_ * (forwardDrive_ - reverseDrive_);
phase_ += phaseSpeed * dt;
targetCurvature = amplitude_ * std::sin(phase_ - spatialFrequency_ * i) + turnBias_ * turnProfile(i);
```

Head sweep adds a head-local oscillation; it must not directly teleport or rotate the whole body.

- [ ] **Step 5: Run physics tests**

Run:
```bash
ctest --test-dir C.E-PSVAML/build -R Physics --output-on-failure
```
Expected: PASS and no NaNs over 10,000-tick stability test.

- [ ] **Step 6: Commit**

```bash
git add C.E-PSVAML/src/worm/Body.* C.E-PSVAML/src/worm/MotorCommand.h C.E-PSVAML/tests/PhysicsTests.cpp
git commit -m "feat: add segmented worm biomechanics"
```

---

### Task 5: Physiology, pumping, digestion, reserves, DMP, stress, aging hazard

**Files:**
- Create: `C.E-PSVAML/src/worm/Physiology.h`
- Create: `C.E-PSVAML/src/worm/Physiology.cpp`
- Create: `C.E-PSVAML/src/worm/PhysiologyTypes.h`
- Create: `C.E-PSVAML/tests/PhysiologyTests.cpp`

**Interfaces:**
- Consumes: `World`, `Random`, `TimeProfile`, body movement cost.
- Produces:
  - `struct DigestivePacket` exactly as frozen spec.
  - `struct InternalState { float energyDeficit, stressLevel, developmentContext, recentFoodMemory; }`.
  - `struct ActionConsequences { float foodIngested, energyAbsorbed, damageDelta, starvationDelta, thermalStressDelta, distanceMoved; }`.
  - `Physiology::tryPump`, `updateDigestion`, `updateMetabolism`, `updateDefecation`, `applyMechanicalDamage`, `summaryForBrain`, `consequencesForLearning`, `isDead`, `deathCause`.

- [ ] **Step 1: Write feeding/digestion/starvation/DMP tests**

```cpp
TEST_CASE("pumping creates gut content before energy") {
    ce::World world = ce::World::foodPatchForTests({50,50}, 1.0f);
    ce::Physiology p = ce::Physiology::baseline();
    const float e0 = p.availableEnergy();
    p.tryPump(world, {50,50}, 1.0f, 0.02);
    REQUIRE(p.gutLoad() > 0.0f);
    REQUIRE(p.availableEnergy() == Catch::Approx(e0));
    p.updateDigestion(2.0);
    REQUIRE(p.availableEnergy() > e0);
}

TEST_CASE("starvation consumes reserves before lethal stress") {
    ce::Physiology p = ce::Physiology::baseline();
    // run no-food metabolism until available energy falls, then reserve falls, then stress rises
}
```

- [ ] **Step 2: Verify tests fail**

Run:
```bash
cmake --build C.E-PSVAML/build
```
Expected: compile failure.

- [ ] **Step 3: Implement pump and digestive packet queue**

`tryPump` must:
```text
check pumpDrive > threshold -> check gut capacity -> call World::consumeFood -> append DigestivePacket -> subtract pumping energy cost
```

No touch-to-energy shortcut.

- [ ] **Step 4: Implement metabolism and reserve mobilization**

Use frozen balance:
```text
absorbed + mobilized - basal - movement - pumping - growth - reproductive - stress
```

All slow rates multiply `physiologyRateScale`; physics `dt` remains unchanged.

- [ ] **Step 5: Implement DMP timer and mortality hazard**

`updateDefecation` runs automatically. `updateAging(Random&)` evaluates seeded hazard based on biological age + accumulated stress/damage; there is no exact max-lifespan death tick.

- [ ] **Step 6: Run physiology tests**

Run:
```bash
ctest --test-dir C.E-PSVAML/build -R Physiology --output-on-failure
```
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add C.E-PSVAML/src/worm/Physiology* C.E-PSVAML/tests/PhysiologyTests.cpp
git commit -m "feat: implement worm physiology"
```

---

### Task 6: Local sensory system and sensory snapshots

**Files:**
- Create: `C.E-PSVAML/src/worm/SensorySystem.h`
- Create: `C.E-PSVAML/src/worm/SensorySystem.cpp`
- Create: `C.E-PSVAML/src/worm/SensoryState.h`
- Create: `C.E-PSVAML/tests/SensoryTests.cpp`

**Interfaces:**
- Consumes: `World`, `Body`, `Physiology`, learned preferred temperature/recent traces.
- Produces: `SensoryState` fields frozen in spec: attractant/current delta, repellent/delta, temperature/delta/error, oxygen/error, nose/body touch, vibration, foodAtMouth, energyDeficit, head/mean curvature, forwardSpeed, recentFoodMemory.

- [ ] **Step 1: Write tests proving no global-coordinate oracle is needed**

```cpp
TEST_CASE("sensory system reports local gradient delta") {
    ce::World world = ce::World::linearFoodOdorForTests();
    ce::Body body = ce::Body::makeStraight({20,50}, 12, 5);
    ce::SensorySystem s;
    auto first = s.sample(world, body, ce::Physiology::baseline(), 20.0f, 0.0f, 0.02);
    body.translateForTest({2,0});
    auto second = s.sample(world, body, ce::Physiology::baseline(), 20.0f, 0.0f, 0.02);
    REQUIRE(second.foodAttractantDelta > 0.0f);
}
```

- [ ] **Step 2: Run and verify failure**

- [ ] **Step 3: Implement local sampling at head/mouth/body positions and normalization**

Do not expose `nearestFoodPosition`, world grid coordinates, or hidden global state in `SensoryState`.

- [ ] **Step 4: Implement temporal previous-sample storage only for raw deltas; learned traces stay in `LearningSystem`**

- [ ] **Step 5: Run sensory tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Sensory --output-on-failure
git add C.E-PSVAML/src/worm/Sensory* C.E-PSVAML/tests/SensoryTests.cpp
git commit -m "feat: add local worm sensory system"
```

---

### Task 7: CTRNN nervous system and baseline innate priors

**Files:**
- Create: `C.E-PSVAML/src/worm/NervousSystem.h`
- Create: `C.E-PSVAML/src/worm/NervousSystem.cpp`
- Create: `C.E-PSVAML/src/worm/NeuralParameters.h`
- Create: `C.E-PSVAML/tests/NervousSystemTests.cpp`

**Interfaces:**
- Consumes: `SensoryState`, `InternalState`, neural parameters copied from genome.
- Produces: `MotorCommand NervousSystem::step(const SensoryState&, const InternalState&, double dt)` and mutable effective weights for learning.

- [ ] **Step 1: Write CTRNN integration and prior tests**

```cpp
TEST_CASE("CTRNN preserves temporal state") {
    auto brain = ce::NervousSystem::baseline(12);
    ce::SensoryState pulse{}; pulse.noseTouch = 1.0f;
    auto a = brain.step(pulse, {}, 0.02);
    auto b = brain.step({}, {}, 0.02);
    REQUIRE(brain.stateNorm() > 0.0f);
}

TEST_CASE("baseline nose touch favors reversal") {
    auto brain = ce::NervousSystem::baseline(12);
    ce::SensoryState s{}; s.noseTouch = 1.0f;
    auto out = brain.step(s, {}, 0.02);
    REQUIRE(out.reverseDrive > out.forwardDrive);
}
```

- [ ] **Step 2: Verify failure**

- [ ] **Step 3: Implement CTRNN Euler step exactly from spec**

```cpp
v_[i] += dt / tau_[i] * (-v_[i] + recurrentSum + inputSum + bias_[i]);
a_[i] = std::tanh(v_[i]);
```

- [ ] **Step 4: Implement deterministic baseline weights for weak innate priors**

Encode tendencies via weights/biases only: nose-touch/repellent->reversal, food-at-mouth->pump, food abundance->lower locomotor drive, strong noxious cue->turn/reversal.

- [ ] **Step 5: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Nervous --output-on-failure
git add C.E-PSVAML/src/worm/NervousSystem* C.E-PSVAML/src/worm/NeuralParameters.h C.E-PSVAML/tests/NervousSystemTests.cpp
git commit -m "feat: add recurrent worm nervous system"
```

---

### Task 8: Learning, memory traces, habituation, associative plasticity, thermal memory

**Files:**
- Create: `C.E-PSVAML/src/worm/LearningSystem.h`
- Create: `C.E-PSVAML/src/worm/LearningSystem.cpp`
- Create: `C.E-PSVAML/tests/LearningTests.cpp`

**Interfaces:**
- Consumes: raw sensory state, `ActionConsequences`, effective neural weights.
- Produces: modulated sensory state/traces, `preferredTemperature`, `recentFoodMemory`, plastic weight deltas.

- [ ] **Step 1: Write habituation, dishabituation, and genome-isolation tests**

```cpp
TEST_CASE("harmless repeated touch habituates") {
    ce::LearningSystem l = ce::LearningSystem::baseline(20.0f);
    float first = 0, last = 0;
    for (int i=0;i<100;++i) {
        auto m = l.modulateTouch(1.0f, false, 0.02);
        if (i==0) first=m;
        last=m;
    }
    REQUIRE(last < first);
}

TEST_CASE("damage dishabituates") {
    ce::LearningSystem l = ce::LearningSystem::baseline(20.0f);
    for (int i=0;i<100;++i) l.modulateTouch(1.0f, false, 0.02);
    const float before = l.modulateTouch(1.0f, false, 0.02);
    const float after = l.modulateTouch(1.0f, true, 0.02);
    REQUIRE(after > before);
}
```

- [ ] **Step 2: Verify failure**

- [ ] **Step 3: Implement exponential traces and food/temperature memory**

Use frozen equations:
```cpp
trace = trace * std::exp(-dt/tau) + current * (1.0-std::exp(-dt/tau));
```

- [ ] **Step 4: Implement habituation and associative eligibility traces**

Internal valence comes only from nutrient absorption, damage, starvation change, toxic stress change; no external reward API.

- [ ] **Step 5: Implement thermal preference update in favorable feeding context**

- [ ] **Step 6: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Learning --output-on-failure
git add C.E-PSVAML/src/worm/LearningSystem* C.E-PSVAML/tests/LearningTests.cpp
git commit -m "feat: implement lifetime learning and memory"
```

---

### Task 9: Development stages, lethargus, L2d/dauer, recovery, body scaling

**Files:**
- Create: `C.E-PSVAML/src/worm/DevelopmentSystem.h`
- Create: `C.E-PSVAML/src/worm/DevelopmentSystem.cpp`
- Create: `C.E-PSVAML/tests/DevelopmentTests.cpp`

**Interfaces:**
- Consumes: environmental developmental signals, physiology summary, `TimeProfile`, RNG for probabilistic dauer decision if used.
- Produces:
  - `enum class DevelopmentStage { L1, L2, L2d, Dauer, DauerRecovery, L3, L4, Adult };`
  - `enum class DevelopmentPhase { Growing, Lethargus };`
  - multipliers/flags in frozen spec.

- [ ] **Step 1: Write normal-cycle and lethargus tests**

```cpp
TEST_CASE("normal development passes all real larval stages") {
    auto d = ce::DevelopmentSystem::baselineL1();
    for (int i=0;i<200000 && d.stage()!=ce::DevelopmentStage::Adult;++i)
        d.update(ce::WorldSignals::favorable(), ce::PhysiologySignals::healthy(), 0.02);
    REQUIRE(d.stage() == ce::DevelopmentStage::Adult);
    REQUIRE(d.completedLethargusCount() == 4);
}
```

- [ ] **Step 2: Write dauer induction/recovery tests**

```cpp
TEST_CASE("dauer is developmental not defensive") {
    auto d = ce::DevelopmentSystem::baselineL1();
    d.update(ce::WorldSignals::dauerInducing(), ce::PhysiologySignals::stressed(), 0.02);
    // eventually L2d/Dauer is reachable during larval decision window
    // direct Adult -> Dauer transition must be impossible
}
```

- [ ] **Step 3: Implement stage progress and lethargus timers**

Development rate = base stage rate * temperature factor * nutrition factor * stress factor * global development rate scale.

- [ ] **Step 4: Implement dauer pathway and recovery**

Only allow `L1/L2 decision -> L2d -> Dauer`; recovery requires sustained favorable conditions and routes `Dauer -> DauerRecovery -> L4 -> Adult`.

- [ ] **Step 5: Expose pumping/locomotion/metabolism/reproduction multipliers**

- [ ] **Step 6: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Development --output-on-failure
git add C.E-PSVAML/src/worm/DevelopmentSystem* C.E-PSVAML/tests/DevelopmentTests.cpp
git commit -m "feat: implement worm development and dauer"
```

---

### Task 10: Genome schema, valid trait ranges, baseline genome, mutation

**Files:**
- Create: `C.E-PSVAML/src/worm/Genome.h`
- Create: `C.E-PSVAML/src/worm/Genome.cpp`
- Create: `C.E-PSVAML/tests/GenomeTests.cpp`

**Interfaces:**
- Consumes: `Random`, neural parameter layout.
- Produces: body, physiology, neural, learning, development and reproduction genes from frozen spec plus `Genome::baseline()` and `Genome mutate(const Genome&, Random&, const MutationConfig&)`.

- [ ] **Step 1: Write baseline-range and deterministic-mutation tests**

```cpp
TEST_CASE("baseline genome is valid") {
    auto g = ce::Genome::baseline(16, 12, 5);
    REQUIRE(g.validate());
}

TEST_CASE("mutation is deterministic for same seed") {
    auto g = ce::Genome::baseline(16,12,5);
    ce::Random a(99), b(99);
    REQUIRE(ce::mutate(g,a,{}) == ce::mutate(g,b,{}));
}
```

- [ ] **Step 2: Verify failure**

- [ ] **Step 3: Implement explicit named genes and neural vectors/matrices**

Do not store current energy, age, learned weights, current preferred temperature, or learned habituation in `Genome`.

- [ ] **Step 4: Implement bounded Gaussian mutation**

```cpp
if (rng.chance(cfg.parameterProbability)) value = clamp(value + rng.normal(0,cfg.parameterSigma), min,max);
```

Neural weights use their own sigma.

- [ ] **Step 5: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Genome --output-on-failure
git add C.E-PSVAML/src/worm/Genome* C.E-PSVAML/tests/GenomeTests.cpp
git commit -m "feat: add inheritable genome and mutation"
```

---

### Task 11: Reproductive system, sperm reserve, oocytes, uterine eggs, Egg blueprint/entity

**Files:**
- Create: `C.E-PSVAML/src/worm/Egg.h`
- Create: `C.E-PSVAML/src/worm/ReproductiveSystem.h`
- Create: `C.E-PSVAML/src/worm/ReproductiveSystem.cpp`
- Create: `C.E-PSVAML/tests/ReproductionTests.cpp`

**Interfaces:**
- Consumes: `Genome`, physiology resources, development state, `Random`, mutation config.
- Produces:
  - `struct EggBlueprint { EntityId parentId; std::uint32_t generation; Genome genome; Vector2 position; float maternalProvision; };`
  - `class Egg` with frozen fields and embryogenesis update.
  - `ReproductiveSystem::update`, `takeLaidEggs`, `spermRemaining`, `uterineEggCount`.

- [ ] **Step 1: Write sperm/oocyte/egg-laying tests**

```cpp
TEST_CASE("adult hermaphrodite consumes sperm to create egg") {
    auto r = ce::ReproductiveSystem::baseline();
    r.seedLateL4SpermForTest(10);
    const auto before = r.spermRemaining();
    for (int i=0;i<10000 && r.takeLaidEggs().empty();++i)
        r.update(ce::ReproductionInputs::healthyAdult(), 0.02);
    REQUIRE(r.spermRemaining() < before);
}
```

- [ ] **Step 2: Write maternal provisioning test**

Healthy-resource input must produce higher provision than severe-starvation input while child genes are still parent-copy-plus-mutation rather than Tank/Speedster rewriting.

- [ ] **Step 3: Implement late-L4 sperm reserve and adult oocyte maturation**

- [ ] **Step 4: Implement fertilization -> uterine holding -> egg laying -> `EggBlueprint`**

- [ ] **Step 5: Implement `Egg::updateEmbryogenesis(temperature, dt, TimeProfile)` and hatch readiness**

- [ ] **Step 6: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Reproduction --output-on-failure
git add C.E-PSVAML/src/worm/Egg.h C.E-PSVAML/src/worm/ReproductiveSystem* C.E-PSVAML/tests/ReproductionTests.cpp
git commit -m "feat: implement hermaphrodite reproduction"
```

---

### Task 12: Worm object composition and exact per-worm tick order

**Files:**
- Create: `C.E-PSVAML/src/worm/Worm.h`
- Create: `C.E-PSVAML/src/worm/Worm.cpp`
- Create: `C.E-PSVAML/src/worm/WormDebugState.h`
- Create: `C.E-PSVAML/tests/WormTests.cpp`

**Interfaces:**
- Consumes: all Tasks 4–11.
- Produces:
  - `Worm::tick(World&, double dt, Random&)`
  - `bool isAlive() const`
  - `std::vector<EggBlueprint> takePendingEggs()`
  - `WormDebugState getReadOnlyDebugState() const`
  - identity fields `id`, `parentId`, `generation`, `birthTick`.

- [ ] **Step 1: Write orchestration test proving consequences precede plasticity**

Create a test learning spy or exposed counter so one tick with food at mouth shows: sensory sample -> brain output -> pump/feeding -> physiology absorption/consequences -> learning update. Assert learning sees current-tick consequence only after action.

- [ ] **Step 2: Verify failure**

- [ ] **Step 3: Implement constructor from identity + genome + starting position/stage**

The constructor must copy genome neural parameters into mutable `NervousSystem` state and initialize learned state separately.

- [ ] **Step 4: Implement frozen tick order inside `Worm::tick`**

```text
sample sensors
-> learning sensory modulation
-> CTRNN step
-> body motor application + physics
-> pumping/feeding
-> digestion/metabolism/stress/aging
-> learning/plasticity from consequences
-> development
-> reproduction
-> queue eggs/death state
```

- [ ] **Step 5: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Worm --output-on-failure
git add C.E-PSVAML/src/worm/Worm* C.E-PSVAML/tests/WormTests.cpp
git commit -m "feat: compose complete worm lifecycle tick"
```

---

### Task 13: Population, eggs, births, deaths, lineage, overlapping generations, safety guard

**Files:**
- Create: `C.E-PSVAML/src/simulation/Population.h`
- Create: `C.E-PSVAML/src/simulation/Population.cpp`
- Create: `C.E-PSVAML/src/simulation/LineageRecord.h`
- Create: `C.E-PSVAML/tests/PopulationTests.cpp`

**Interfaces:**
- Consumes: `Worm`, `Egg`, `EggBlueprint`, `Genome`, `Random`.
- Produces: entity creation/removal, `advanceEggs`, `hatchReadyEggs`, `resolveDeaths`, lineage lookup, safety guard state.

- [ ] **Step 1: Write lineage/hatch test**

```cpp
TEST_CASE("hatched child preserves parent and generation") {
    ce::Population p;
    auto parentId = p.addBaselineAdultForTest(...);
    p.addEggBlueprint(ce::EggBlueprint{parentId, 4, ce::Genome::baseline(...), {1,1}, 1.0f});
    p.forceEggsReadyForTest();
    p.hatchReadyEggs(...);
    auto child = p.lastBorn();
    REQUIRE(child.parentId() == parentId);
    REQUIRE(child.generation() == 5);
}
```

- [ ] **Step 2: Write safety guard test**

When count exceeds `maxPopulationSafety`, `Population` reports guard trigger; it must not silently kill arbitrary entities.

- [ ] **Step 3: Implement overlapping generations**

No generation-wide reset or `selectBestWorm()` method exists.

- [ ] **Step 4: Implement death removal after snapshot and lineage record preservation**

- [ ] **Step 5: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Population --output-on-failure
git add C.E-PSVAML/src/simulation/Population* C.E-PSVAML/src/simulation/LineageRecord.h C.E-PSVAML/tests/PopulationTests.cpp
git commit -m "feat: add population and lineage lifecycle"
```

---

### Task 14: Simulation core, exact global tick order, visual/headless state equality, fixed timestep

**Files:**
- Create: `C.E-PSVAML/src/simulation/Simulation.h`
- Create: `C.E-PSVAML/src/simulation/Simulation.cpp`
- Create: `C.E-PSVAML/tests/SimulationTests.cpp`

**Interfaces:**
- Consumes: `World`, `Population`, `SimulationConfig`, `Random`.
- Produces: `Simulation::tick()`, `runTicks(std::uint64_t)`, `currentTick`, read-only world/population access, deterministic state digest.

- [ ] **Step 1: Write fixed-tick test**

```cpp
TEST_CASE("runTicks executes exact number of fixed updates") {
    ce::Simulation s(ce::SimulationConfig{}, 123);
    s.runTicks(1000);
    REQUIRE(s.currentTick() == 1000);
    REQUIRE(s.simulatedPhysicsTime() == Catch::Approx(20.0));
}
```

- [ ] **Step 2: Write deterministic-state test**

Two simulations with same config + seed + initial state must produce identical `stateDigest()` at tick 10,000.

- [ ] **Step 3: Implement exact global tick order from spec section 12.1**

```text
increment tick -> world dynamic fields -> worm ticks -> collect laid eggs -> egg embryogenesis -> hatch -> death snapshot/removal -> metrics hook
```

- [ ] **Step 4: Add deterministic state digest for tests/debug**

Digest IDs, stages, selected scalar states, body coordinates quantized to stable precision, egg states and world field checksums. This is debugging output only.

- [ ] **Step 5: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Simulation --output-on-failure
git add C.E-PSVAML/src/simulation/Simulation* C.E-PSVAML/tests/SimulationTests.cpp
git commit -m "feat: implement deterministic simulation core"
```

---

### Task 15: Scenario factory and isolated biological/behavioral assays

**Files:**
- Create: `C.E-PSVAML/src/simulation/Scenario.h`
- Create: `C.E-PSVAML/src/simulation/Scenario.cpp`
- Create: `C.E-PSVAML/tests/BehaviorTests.cpp`
- Extend: `C.E-PSVAML/tests/DevelopmentTests.cpp`
- Extend: `C.E-PSVAML/tests/ReproductionTests.cpp`

**Interfaces:**
- Consumes: `SimulationConfig`, `World`, baseline genomes/population.
- Produces named scenario constructors:
  - `baseline_ecosystem`
  - `chemotaxis_assay`
  - `thermotaxis_assay`
  - `aerotaxis_assay`
  - `nose_touch_assay`
  - `habituation_assay`
  - `associative_learning_assay`
  - `starvation_assay`
  - `dauer_induction_assay`
  - `dauer_recovery_assay`
  - `reproduction_assay`.

- [ ] **Step 1: Write scenario-name lookup test**

```cpp
TEST_CASE("all frozen V1 scenarios can be created") {
    for (auto name : ce::Scenario::requiredV1Names()) {
        auto s = ce::Scenario::create(name, ce::SimulationConfig{});
        REQUIRE(s.has_value());
    }
}
```

- [ ] **Step 2: Implement deterministic scenario factories with explicit world field setup**

No visual editor.

- [ ] **Step 3: Implement chemotaxis/nose-touch/habituation acceptance tests**

Use repeated trials with fixed seed sets where probabilistic behavior is involved; assert aggregate directional/reversal response rather than one exact motor output if the CTRNN is stochastic only through mutation/initialization.

- [ ] **Step 4: Implement thermotaxis/aerotaxis/associative-learning acceptance tests**

Verify signal/memory/plastic change, not global-location cheating.

- [ ] **Step 5: Implement starvation/dauer/reproduction/hatch acceptance tests**

Match frozen Definition of Done sections 14.3, 14.11–14.15.

- [ ] **Step 6: Run behavior/acceptance suite and commit**

```bash
ctest --test-dir C.E-PSVAML/build --output-on-failure
git add C.E-PSVAML/src/simulation/Scenario* C.E-PSVAML/tests
git commit -m "test: add biological scenario acceptance assays"
```

---

### Task 16: Metrics recorder, lineage/population statistics, CSV/event logging, behavior classifier

**Files:**
- Create: `C.E-PSVAML/src/simulation/MetricsRecorder.h`
- Create: `C.E-PSVAML/src/simulation/MetricsRecorder.cpp`
- Create: `C.E-PSVAML/src/simulation/BehaviorClassifier.h`
- Create: `C.E-PSVAML/src/simulation/BehaviorClassifier.cpp`
- Create: `C.E-PSVAML/tests/MetricsTests.cpp`

**Interfaces:**
- Consumes: read-only `Simulation`, `Population`, `WormDebugState`.
- Produces individual lifetime summary CSV, population time-series CSV, event log, post-hoc roaming/dwelling labels.

- [ ] **Step 1: Write CSV header/content test using temporary directory**

Assert exact required columns from spec 11.4 are present, including birth/death cause, food, energy, distance, reversals, turns, dauer time, eggs laid/hatched, descendants; population CSV includes population/egg counts, births/deaths, stages, energy/reserve/age, dauer, lineage diversity, trait means/variance.

- [ ] **Step 2: Implement in-memory metric snapshots before file output**

- [ ] **Step 3: Implement CSV writers and event log**

No database.

- [ ] **Step 4: Implement post-hoc `BehaviorClassifier` from speed, reversal rate, turn rate, food memory and pumping**

Classifier never feeds back into `Worm` control.

- [ ] **Step 5: Run tests and commit**

```bash
ctest --test-dir C.E-PSVAML/build -R Metrics --output-on-failure
git add C.E-PSVAML/src/simulation/MetricsRecorder* C.E-PSVAML/src/simulation/BehaviorClassifier* C.E-PSVAML/tests/MetricsTests.cpp
git commit -m "feat: add simulation metrics and logging"
```

---

### Task 17: raylib renderer, debug overlays, CLI, visual/headless runners

**Files:**
- Create: `C.E-PSVAML/src/render/Renderer.h`
- Create: `C.E-PSVAML/src/render/Renderer.cpp`
- Create: `C.E-PSVAML/src/simulation/CommandLine.h`
- Create: `C.E-PSVAML/src/simulation/CommandLine.cpp`
- Replace: `C.E-PSVAML/src/main.cpp`
- Create: `C.E-PSVAML/tests/CommandLineTests.cpp`

**Interfaces:**
- Consumes: read-only `Simulation`.
- Produces CLI modes:
  - `--headless`
  - `--scenario <name>`
  - `--seed <uint64>`
  - `--ticks <uint64>`
  - `--speed <ticks-per-frame>`
  - `--pause-at <tick>` optional debug.

Renderer toggles fields: food, odor, repellent, pheromone, temperature, oxygen, vibration; selected-worm overlay displays frozen debug fields.

- [ ] **Step 1: Write CLI parse tests**

```cpp
TEST_CASE("headless CLI parses seed scenario and ticks") {
    const char* argv[] = {"ce_psvaml","--headless","--seed","42","--scenario","chemotaxis_assay","--ticks","1000"};
    auto o = ce::parseCommandLine(8, const_cast<char**>(argv));
    REQUIRE(o.headless);
    REQUIRE(o.seed == 42);
    REQUIRE(o.scenario == "chemotaxis_assay");
    REQUIRE(o.ticks == 1000);
}
```

- [ ] **Step 2: Implement CLI parser**

- [ ] **Step 3: Implement renderer as const/read-only consumer**

Draw worm polyline/segments, distinct head, food field, optional field heatmaps and selected-organism debug text. Renderer methods accept `const Simulation&` only.

- [ ] **Step 4: Implement `main` headless path without calling `InitWindow`**

Headless:
```text
create scenario -> create Simulation -> run requested ticks/until guard/end -> flush metrics -> exit
```

Visual:
```text
InitWindow -> accumulator/frame loop -> run N fixed ticks -> draw const state -> CloseWindow
```

- [ ] **Step 5: Add automated headless smoke test**

Run:
```bash
C.E-PSVAML/build/ce_psvaml --headless --seed 1 --scenario baseline_ecosystem --ticks 10000
```
Expected: exit 0, no raylib window requirement, metrics files produced.

- [ ] **Step 6: Commit**

```bash
git add C.E-PSVAML/src/render C.E-PSVAML/src/simulation/CommandLine* C.E-PSVAML/src/main.cpp C.E-PSVAML/tests/CommandLineTests.cpp
git commit -m "feat: add raylib viewer and headless runner"
```

---

### Task 18: Full-life integration, temporal calibration, evolution smoke test, Definition-of-Done closure

**Files:**
- Create: `C.E-PSVAML/tests/FullLifeTests.cpp`
- Create: `C.E-PSVAML/config/v1-defaults.md`
- Create: `C.E-PSVAML/README.md`
- Modify calibrated defaults only in: `C.E-PSVAML/src/simulation/SimulationConfig.h` and subsystem baseline constants/config tables.

**Interfaces:**
- Consumes: entire V1.
- Produces: verified end-to-end V1, calibrated compressed time profile, user-facing run instructions.

- [ ] **Step 1: Write full lifecycle integration test**

```cpp
TEST_CASE("viable lineage can complete one full generation") {
    auto config = ce::SimulationConfig::v1Compressed();
    auto scenario = ce::Scenario::create("reproduction_assay", config).value();
    ce::Simulation sim(config, 424242, scenario);
    sim.runUntil([&]{ return sim.population().hasGenerationAtLeast(1); }, 250000);
    REQUIRE(sim.population().hasGenerationAtLeast(1));
    REQUIRE(sim.population().lineageRecords().size() >= 2);
}
```

- [ ] **Step 2: Write evolution smoke test with no artificial selector**

Run a longer seeded baseline with mutation enabled. Assert:
```text
births > 0
multiple lineage records exist
at least one lineage extinct or expanded
trait variance changes from initial value
no code path invokes mandatory score selection
```

- [ ] **Step 3: Write visual/headless state-equality test**

Do not initialize raylib in test. Compare the same core execution schedule used by visual runner (`N ticks then render no-op`) against pure headless `N ticks`; require identical `stateDigest()`.

- [ ] **Step 4: Calibrate compressed time profile to frozen engineering targets**

Using automated measurements, tune config so baseline favorable conditions approximately satisfy:
```text
Egg -> Adult          24,000–36,000 ticks
Adult median life     60,000–90,000 ticks
Fed DMP               100–200 ticks
```

Do not change `fixedDt` to hit targets. Change only slow-rate configuration/baseline physiology parameters.

- [ ] **Step 5: Run the entire Definition-of-Done suite**

Run:
```bash
cmake --build C.E-PSVAML/build -j
ctest --test-dir C.E-PSVAML/build --output-on-failure
C.E-PSVAML/build/ce_psvaml --headless --seed 12345 --scenario baseline_ecosystem --ticks 250000
```

Expected:
- all tests PASS;
- no NaN/Inf states;
- no population safety trigger in baseline unless deliberately stress-tested;
- headless run exits 0;
- metrics and lineage output generated.

- [ ] **Step 6: Verify every frozen DoD item 1–35 has a passing test or explicit runtime check**

Record the mapping in `README.md` under `V1 verification matrix`, e.g.:
```text
DoD 1  -> WorldTests / baseline_ecosystem
DoD 3  -> PhysicsTests
DoD 13 -> LearningTests habituation
DoD 18 -> DevelopmentTests dauer induction
DoD 31 -> FullLifeTests visual/headless equality
...
```

No DoD item may be marked complete without evidence.

- [ ] **Step 7: Document run commands and architecture in README**

Include:
```bash
cmake -S C.E-PSVAML -B C.E-PSVAML/build
cmake --build C.E-PSVAML/build -j
ctest --test-dir C.E-PSVAML/build --output-on-failure
C.E-PSVAML/build/ce_psvaml --scenario baseline_ecosystem --seed 1
C.E-PSVAML/build/ce_psvaml --headless --scenario baseline_ecosystem --seed 1 --ticks 250000
```

- [ ] **Step 8: Final verification commit**

```bash
git add C.E-PSVAML
git commit -m "feat: complete C.E-PSVAML V1 simulation"
```

---

# Review gates between tasks

After each task:

1. run the task-specific tests;
2. run the full suite;
3. inspect the diff for scope creep;
4. verify no frozen design decision was silently changed;
5. commit before beginning the next task.

If a task reveals that a frozen requirement is impossible or internally contradictory, stop implementation and record:

```text
Frozen requirement:
Observed contradiction:
Minimal proposed deviation:
Affected tests/files:
```

Do not silently alter `C.E-PSVAML-V1-SPEC.md`.

---

# Spec coverage self-review

- Architecture/fixed timestep/time profile -> Tasks 1, 2, 14, 17, 18.
- World/food/chemistry/temperature/O2/mechanical stimuli -> Task 3.
- Segmented body/forward/reversal/omega-like/head sweep -> Task 4.
- Pumping/digestion/energy/reserves/DMP/stress/aging/death -> Task 5.
- Local sensory system/quimio/thermo/mechano/proprio/aerotaxis/interoception -> Task 6.
- Recurrent temporal nervous system and innate priors -> Task 7.
- Habituation/associative plasticity/thermal memory/food memory -> Task 8.
- Egg-L1-L2-L3-L4-Adult/lethargus/L2d/dauer/recovery -> Task 9 + Task 11 for Egg.
- Complete hereditary genome/mutation -> Task 10.
- Hermaphrodite reproduction/oocytes/sperm/uterine eggs/provisioning/laying/embryogenesis -> Task 11.
- Whole-organism integration -> Task 12.
- Overlapping generations/lineage/natural differential reproduction/safety guard -> Task 13.
- Exact tick ordering/determinism -> Task 14.
- Frozen assay list and behavioral acceptance -> Task 15.
- Metrics/CSV/logging/post-hoc behavior labels -> Task 16.
- raylib visual mode/headless same core/debug overlays -> Task 17.
- Full generation, temporal calibration, evolution smoke, DoD 1–35 -> Task 18.

No frozen V1 subsystem is intentionally omitted.

---

# Type consistency reference

The following names are canonical across the implementation plan:

```text
Simulation
SimulationConfig
TimeProfile
Random
World
ScalarField
FoodField
MechanicalEnvironment
Population
LineageRecord
Worm
Genome
Body
BodyNode
Physiology
DigestivePacket
SensorySystem
SensoryState
InternalState
NervousSystem
LearningSystem
DevelopmentSystem
DevelopmentStage
DevelopmentPhase
ReproductiveSystem
EggBlueprint
Egg
MotorCommand
ActionConsequences
MetricsRecorder
BehaviorClassifier
Scenario
Renderer
```

Canonical per-tick data flow:

```text
World + Body + Physiology
    -> SensorySystem -> SensoryState
    -> LearningSystem modulation
    -> NervousSystem + InternalState -> MotorCommand
    -> Body + Physiology actions
    -> ActionConsequences
    -> LearningSystem plasticity
    -> DevelopmentSystem
    -> ReproductiveSystem -> EggBlueprint[]
    -> Population -> Egg -> Worm
```

---

# Execution handoff

Recommended implementation mode: **Subagent-Driven Development**, one fresh worker per task with review between tasks. This plan is intentionally ordered so every task depends only on earlier committed interfaces and leaves independently testable software.
