# C.E-PSVAML V1

C++17 + CMake + raylib 2D, with one simulation core for visual and headless execution. Simulation owns World and Population; Population owns Worms and Eggs; each Worm composes its body, physiology, sensors, recurrent brain, individual learning, development and reproduction. No score-based selection, ECS, event bus or simulation multithreading.

```sh
cmake -S C.E-PSVAML -B C.E-PSVAML/build -DCMAKE_BUILD_TYPE=Release
cmake --build C.E-PSVAML/build -j 4
ctest --test-dir C.E-PSVAML/build --output-on-failure
C.E-PSVAML/build/ce_psvaml --scenario baseline_ecosystem --seed 1
C.E-PSVAML/build/ce_psvaml --headless --scenario baseline_ecosystem --seed 12345 --ticks 250000
```

Use `.exe` on Windows. A C++ compiler, CMake, Git and platform graphics dependencies are required. CMake fetches raylib 5.5 and Catch2 3.8.1. Headless never initializes a window. `--speed N` executes N fixed ticks per visual frame; `--ticks N` stops either mode at exactly N ticks. Headless without `--ticks` runs 250,000 ticks. Space pauses, N single-steps, Tab cycles field overlays, and clicking a head selects a worm. Output: `output/<scenario>-<seed>/individuals.csv`, `population.csv`, `events.txt`.

The per-organism invariant is sensing -> temporal modulation -> CTRNN -> motor command -> body physics -> feeding/physiology -> actual consequences -> learning -> development/effects -> reproduction. New developmental effects govern the following physics tick. Growth and reproduction consume physiological resources. Maternal provision is distinct from the inherited genome.

Scenarios: `baseline_ecosystem`, `chemotaxis_assay`, `thermotaxis_assay`, `aerotaxis_assay`, `nose_touch_assay`, `habituation_assay`, `associative_learning_assay`, `starvation_assay`, `dauer_induction_assay`, `dauer_recovery_assay`, `reproduction_assay`.

## Frozen Definition of Done evidence

Final acceptance (2026-09-05, source bd4740a): **35/35 DoD items fulfilled**. Clean Release build passed; CTest 63/63, Catch2 62 cases / 575486 assertions. The default-world baseline seed 12345 completed 250000 ticks with exit 0, digest 8205094381958857740, 3493 worms, 833 eggs and no safety guard. CSV balances reconcile, generation 6 was reached, and no NaN/Inf entries were found. Detailed evidence and limitations are recorded in [IMPLEMENTATION-RECORD.md](IMPLEMENTATION-RECORD.md).

Names below identify actual Catch2 cases (leading group plus distinguishing text), source contracts or runtime checks. Assays are controlled engineering checks of the V1 abstractions, not validation of biological fidelity.

| DoD | Requirement | Evidence |
|---:|---|---|
| 1 | Continuous 2D world and local fields/stimuli | World scalar interpolation, mechanical stimulus, Scenario all frozen V1 names |
| 2 | Multiple simultaneous worms | Simulation same-seed baseline, Population hatch, FullLife overlapping generations |
| 3 | Segmented undulatory body | Physics constraints, reverse displacement, strong turn, no artificial propulsion, isotropic-drag control |
| 4 | Brain perceives through local sensors | Sensory local deltas/proprioception; NervousSystem accepts SensoryState/InternalState only |
| 5 | Local temporal chemotaxis | Behavior chemotaxis improves gradient progress over mirrored controls, seeds 11/22/33 |
| 6 | Thermal memory/thermotaxis | Behavior favorable thermal feeding; Sensory signed thermal error; Learning thermal memory |
| 7 | Mechanosensation and withdrawal | Behavior nose withdrawal and actual damage restoration; Sensory touch/vibration |
| 8 | Aerotaxis | Behavior oxygen changes motor output; Sensory oxygen preference sign |
| 9 | Active pumping | Physiology pumping before absorbed energy; Worm current absorption |
| 10 | Delayed digestive transit | Physiology pumping creates gut content before energy |
| 11 | Energy, metabolism, reserves | FullLife starvation chain; Physiology reserve mobilization; FullLife body mass |
| 12 | Defecation program | Physiology DMP contractions; FullLife fed DMP 150 ticks |
| 13 | Habituation | Behavior repeated pulses, lower response, restoration after actual damage |
| 14 | Individual associative learning | Behavior actual paired absorption changes weights and cue response versus unpaired control |
| 15 | Food memory and search modulation | Learning food trace; NervousSystem baseline food-memory inputs alter reverse/turn/sweep; paired-association organism assay |
| 16 | Egg -> L1 -> L2 -> L3 -> L4 -> Adult | FullLife viable egg all normal stages, 29,409 ticks |
| 17 | Lethargus in each molt | Development normal cycle asserts pumping/movement suppression; FullLife four molts |
| 18 | L2d -> Dauer | FullLife integrated Dauer pathway at default rates; sustained induction environment |
| 19 | Dauer recovery | FullLife DauerRecovery -> L4 -> Adult; Development adult cannot re-enter Dauer |
| 20 | Adult self-fertilization | Reproduction healthy adult consumes sperm; FullLife viable lineage |
| 21 | Oocytes, fertilization, uterine hold, laying | Reproduction healthy adult uses finite sperm and holds before laying |
| 22 | Physical eggs in world | Population Egg collection and position; raylib egg drawing |
| 23 | Viable hatching | Reproduction embryo viability; Population hatch; FullLife lineage |
| 24 | Genetic inheritance/mutation | Genome bounded seeded mutation; FullLife mutated child |
| 25 | Learned state not inherited | Worm construction isolation; Behavior source genomes unchanged; Egg copies/mutates original genome |
| 26 | Lineage and overlapping generations | Population lineage survives death; FullLife living parent and child |
| 27 | Differential reproduction | FullLife resource-rich founder has more children than resource-poor founder; no selection API |
| 28 | Aging and causes of death | FullLife adult lifetime and starvation; Physiology seeded aging, mechanical death; Population thermal deaths |
| 29 | raylib viewer | Real GLFW/OpenGL runtime and inspected screenshot |
| 30 | Accelerated headless | CTest headless_smoke; required 250,000-tick runtime |
| 31 | Identical visual/headless core | Simulation grouped schedule; actual Renderer checks preserve digest and match headless |
| 32 | Seeded reproducibility | Simulation 10,000-tick same-seed equality and different-seed divergence |
| 33 | Isolated assays pass | Scenario required names plus Behavior/FullLife/Development/Reproduction cases |
| 34 | Slow rates without changing fixedDt | Core slow-rate test; FullLife accelerated lineage and default-rate calibration |
| 35 | Understandable composition and tick | Worm::tick and Simulation::tick, explicit owning classes, no generic orchestration framework |

Calibration and metric column conventions are in [config/v1-defaults.md](config/v1-defaults.md). Commit-by-commit TDD evidence, integration rulings and final acceptance results are in [IMPLEMENTATION-RECORD.md](IMPLEMENTATION-RECORD.md).

Second review should focus on body constraints/drag and mass semantics, resource accounting across digestion/growth/provisioning, CTRNN priors and eligibility-based plasticity, and the strength of behavioral assay controls. These are intentionally simplified V1 mechanisms. Exact replay across different compilers/standard libraries is not claimed.
