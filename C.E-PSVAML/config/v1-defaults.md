# V1 defaults and calibration

Physics/control use 50 Hz, fixedDt 0.02 seconds, 12 body nodes and four constraint iterations. Rendering defaults to 60 FPS. Speed means more identical ticks per frame, never a larger dt. World: 1000 x 1000, 128 x 128 fields, toroidal boundary, 32 founders, safety maximum 10,000 worms plus eggs. The CTRNN has 18 inputs, 12 recurrent units and five motor outputs.

TimeProfile physiology/development/reproduction/aging multipliers remain 1. Larval growing stages take 120 biological seconds, each lethargus 12, embryogenesis 60, Dauer cue integration and recovery 30. Individual inherited parameters and physiological conditions modulate these times.

Measured with GCC 16.2, C++17, Release, fixedDt 0.02:

| Measurement | Result (ticks) | Required range |
|---|---:|---:|
| Favorable viable Egg to Adult, seed 424242 | 29,409 | 24,000–36,000 |
| Fed adult median lifetime, seeds 11/22/33/44/55 | 87,772 | 60,000–90,000 |
| Fed defecation period | 150 | 100–200 |

No slow-rate adjustment was needed. Calibration assays use smaller field grids (16 x 16) with controlled uniform food, keeping all organism parameters and fixedDt unchanged. The final baseline runtime uses the complete default 128 x 128 world. Adult lifetime calibration replenishes food to isolate aging; it is not a claim that an unfed animal survives that long.

Default reproductive investment is one paid physiological resource unit per fertilization, 20 sperm initialized once during late L4, a 20-second condition-modulated oocyte maturation interval and a five-second condition-modulated uterine holding interval. Provision is capped by investment. Offspring energy plus reserve equals provision; learned state is initialized fresh. Scenario founders receive two initial resource units.

The Dauer induction assay maintains a low food carrying density of 0.05 and a pheromone source balancing decay. Recovery starts with an initialized Dauer history and sustained favorable food/temperature. Habituation excludes food reinforcement to isolate harmless mechanical pulses. Scenario initial Adult/Dauer histories replay developmental transitions; full-life acceptance separately starts from an actual Egg.

Population CSV sampling is every 100 ticks. Individual totals accumulate each tick. Stage columns follow L1, L2, L2d, Dauer, DauerRecovery, L3, L4, Adult. Trait means/variances report, in order: body stiffness, structural mass scale, basal metabolic rate, development rate gene, plasticity rate, reproductive allocation. Death causes: 0 none, 1 mechanical, 2 starvation, 3 thermal, 4 toxicity, 5 aging. Times in lifetime summaries use simulated physics seconds.

Determinism is verified for identical seed/configuration on the same build/platform. The digest quantizes numeric observations to 1e-6 and is a debugging fingerprint, not a save-state format or a promise of identical standard-library random distributions across platforms.
