# Inline implementation record

Baseline: 039b8170b2dc3a7b85f7763621f43ca7167206f0. Frozen specification blob verified as 1b4c22d997a75e0a6d9879ac2232bb0b04f4335a.
Branch: ce-psvaml-v1-tasks-2-18. No merge to main. Single implementer and self-reviewer.

## Task 1 verification
All six planned files and three CMake targets match the plan. Fresh Windows GCC 16.2 / Ninja Release build passed; CTest 1/1 passed. Portable toolchain and build tree live outside the repository. Upstream raylib 5.5 audio jar_mod warnings observed; no project warnings. No Task 1 changes.

## Task 2
RED: CoreTests compilation failed because core/Random.h did not exist.
GREEN: build passed; CTest 5/5 passed (0 failures).
Self-review: canonical types/defaults match plan, mt19937_64 owns seeded state, probabilities clamp, uniform/normal replay tested. Slow rates do not modify fixedDt. No frozen contract deviation.

## Task 3
RED: WorldTests failed to compile without World.h. Added regression RED for missing vibration decay, then corrected its envelope.
GREEN: World 5/5; full CTest 10/10, 0 failures. Build and diff check pass.
Self-review: bilinear local sampling; actual consumed mass equals sum of cell decrements; quality properties remain separate; seeded-free deterministic fields; bounded explicit diffusion substeps; uniform/linear/radial temperature; oxygen and localized mechanical stimuli. Core includes raylib Vector2 type without linking rendering code. Toroidal coordinates normalize before sampling; field diffusion uses closed/no-flux stencil as allowed by plan. No frozen design change.

## Task 4
RED: PhysicsTests could not compile without Body.h.
GREEN: six physics tests; full CTest 16/16, 0 failures. 10,000-tick finite/continuous strong-turn run passed.
Self-review: angle gradients sum to zero; inverse-mass PBD constraints preserve center of mass; only anisotropic substrate damping produces net locomotion. Zero wave and isotropic-drag controls verify absence of direct commanded translation. Rig wraps together including previous positions; local displacement excludes boundary wrapping.
Ruling (test fixture, not frozen design): plan's reverse test starts x=200 in a 1000-wide torus and wrapped after real negative displacement (reported +740). Signed-coordinate displacement requires no seam crossing. Enlarged only that test arena/start position; a separate original-size toroidal crossing test preserves constraints and checks physical displacement. No physics adjustment made to hide the result.

## Task 5
RED: missing Physiology.h. GREEN: five physiology tests, full CTest 21/21.
Self-review: pump withdraws food and costs energy; packets delay absorption; reserves mobilize before starvation; DMP has posterior/anterior/expulsion phases; cause-specific stress/death and seeded age hazard. Same-seed age death replays, different seed changes death tick. No HP/reward/instant feeding energy.
Ruling: use persistent Random& in reserve test instead of temporary Random(7) each iteration. CE_TESTING variant compiles identical core sources with test-only setters consistently to avoid ODR mismatch; production core excludes them. Growth/reproductive allocation consumers are integrated in their later tasks.

## Task 6
RED: missing SensorySystem.h. GREEN: sensory 3/3, full CTest 24/24.
Self-review: only head-local field samples and body/physiology summaries; deltas initialize to zero and track preceding samples. No global coordinates in SensoryState. Temperature in physical degrees supports thermal learning; neural packing normalizes units in Task 7. No frozen design changes.

## Task 7
RED: missing NervousSystem.h. GREEN: nervous 5/5; full CTest 29/29.
Self-review: synchronous Euler from prior activations, exact two-neuron numerical fixture, tau/dimension/finite-weight validation, 100,000 bounded steps. Priors are solely weights/biases. Fixed 18 features retain local thermal/O2 errors, use redundant raw temperature/O2 slots for stress/development and preserve temporal chemical gain. Source parameter object is copied into mutable individual parameters. No World/position interface.

## Task 8
RED: missing LearningSystem.h. GREEN: learning 4/4; full CTest 33/33.
Self-review: eligibility uses actual packed neural inputs and postsynaptic activation, valence uses physiological consequences (toxic damage currently included in damageDelta); no external reward method. Only individual effective chemical input weights change; source parameters unchanged. Food trace and thermal memory acquired.
Ruling: plan habituation example only called modulate and implicitly assumed harmlessness before consequences. Frozen tick/consequence causality takes priority: revised test runs neural action and explicit zero-damage consequence each iteration; separate test confirms observation alone never habituates. No frozen contract change.

## Task 9 - VALIDATED
Clean Windows GCC 16.2 / Ninja Release build completed successfully in an external build tree. Full CTest passed: 35/35 test cases, 0 failures. Direct executable summary: 575127 assertions in 35 test cases. Task-specific filter `*Development*` passed: 2/2 test cases, 127 assertions.
Task 9 acceptance criteria passed: normal progression L1 -> L2 -> L3 -> L4 -> Adult with four lethargus periods; Dauer induction through L2d; pumping/metabolism suppression in Dauer; sustained favorable recovery through DauerRecovery and L4 to Adult; adults do not re-enter Dauer under adverse cues. Tasks 1-8 remain green in the same full suite.
Static review of commit 1fcfc39 found only the planned Task 9 sources/tests plus CMake and this record; no frozen specification files were changed and `git diff --check` passed. Warnings are limited to upstream raylib/CMake compatibility diagnostics; no project compilation errors. Tasks 10-18 remain unstarted.

## Incomplete final acceptance
No full-life scenario, visual/headless integration, whole-system determinism, final clean Task-18 build or calibration has been performed. The Definition of Done is NOT fulfilled. Subsystem evidence exists for body, local sensors, pumping/digestion/metabolism/DMP, and isolated learning; none establishes the complete organism.
Recommended independent review once execution resumes: Body PBD/drag and toroidal boundaries; physiology resource accounting and forthcoming growth/reproduction costs; CTRNN input packing/priors/stability; consequence eligibility and inherited-state isolation; unexecuted development/Dauer transitions. Later Tasks 11/12/15/18 require full integration review.

## Task 10 - VALIDATED
Preflight: clean ce-psvaml-v1-tasks-2-18, remote already contained 703a78a. Single baseline CTest run: 35/35 PASS. No reopening Tasks 1-9.
RED: GenomeTests failed for missing Genome.h. GREEN: Genome 2/2; full CTest 37/37.
Review: named hereditary fields cover frozen 10.2; sensor gains applied to copied neural parameters; bounded Gaussian mutation uses passed RNG, independent neural sigma, no learned/physiological state. No changes to prior subsystem implementations.
Ruling: explicit C++17 equality instead of C++20 defaulted equality from plan example. Neural tau mutation lower bound 0.04 preserves stability at fixedDt 0.02. No frozen deviation.

## Task 11 - VALIDATED
RED: missing ReproductiveSystem.h. GREEN: Reproduction 3/3; full CTest 40/40. Diff whitespace check PASS.
Review: one-time late-L4 sperm initialization, adult-only maturation/fertilization, one sperm and one paid resource unit consumed per fertilization, uterine delay before laying, finite sperm exhaustion. Provisioning is capped by investment and depends on nutrition/stress; copied or mutated hereditary genome never includes provisioning. Egg viability and development respond to temperature and provision.
Ruling: availableReproductiveResources is an amount transferred from Physiology each tick, not an inexhaustible balance or rate. Optional passed Random enables mutation at fertilization; omitting it is a mutation-disabled fixture, not a separate RNG. Resource transfer integration belongs to Task 12. No frozen deviation.

## Task 12 - VALIDATED
RED: missing Worm.h. GREEN: Worm 2/2; full CTest 42/42.
Review: explicit frozen order, current absorption feeds current learning, inherited genome remains isolated, offspring energy plus reserve equals provision. Paid growth adjusts constraint rest lengths/mass, never translates body coordinates. Prior development state gates current pumping/movement; newly updated development effects apply on the following physics/physiology tick. Death prevents further reproduction.
Rulings: Task 5 deferred growth/reproductive consumers; integration requires minimal resource-transfer, birth-provision and developmental multiplier methods in Physiology, and rest-length/mass configuration in Body. Defaults preserve isolated Tasks 1-9 behavior; all remain green. Oxygen preference uses world normalized 0.5. Learning fixture supplies the same explicit chemical cue to both worms because no World update had generated food odor; only one receives actual absorption. No frozen change.

## Task 13 - VALIDATED
RED: missing Population.h. GREEN: Population 2/2; full CTest 44/44.
Review: stable vectors and monotonic IDs, egg ID survives hatching, actual provision passed to L1, lineage retained after thermal death. Safety counts worms plus eggs; rejects new entities without culling; hatching replaces an entity and does not trigger the guard. Birth means hatching, not fertilization. No frozen deviation.

## Task 14 - VALIDATED
RED: missing Scenario.h. GREEN: Scenario 2/2; full CTest 46/46.
Review: all eleven frozen names, explicit local fields/stimuli/population; unknown names return before mutation or RNG use. Baseline positions use passed seeded RNG. Reproduction starts adult with sperm; recovery starts Dauer.
Ruling: initial-stage scenario blueprints replay DevelopmentSystem transitions during construction and late-L4 sperm initialization, without adding a runtime stage setter or a defensive Dauer action. This setup history does not claim a measured full-life assay; Task 18 must exercise actual integrated transitions. No frozen deviation.

## Task 15 - VALIDATED
RED: missing Simulation.h. GREEN: Simulation 2/2; full CTest 48/48 (39.48 seconds).
Review: single persistent RNG, stable entity order, frozen global tick, constant dt with physicsHz validation, no visual dependency. 10,000 direct ticks match 100x100 grouped ticks with read-only digest calls; seed 778 diverges from 777. Digest includes world grid samples, food, body/physiology/neural states, eggs and lineage. Mutable setup access is rejected after tick zero. No frozen deviation. Digest is a debugging fingerprint, not serialization or a cross-platform floating-point guarantee.

## Task 16 - VALIDATED
RED: missing MetricsRecorder.h. GREEN: Metrics 1/1; full CTest 49/49 (27.57 seconds).
Review: frozen CSV columns, per-tick individual accumulation, 100-tick population windows, final death observation before removal, retained lineage/descendant counts, text birth/death events. Behavior classification uses speed, rolling reversal/turn estimates, pumping and food memory only in telemetry. File flush leaves core digest unchanged. Fixed Windows fixture cleanup by closing read streams first.
Ruling: traitMeans/traitVariance order is body stiffness, structural mass, basal metabolism, development rate, plasticity rate, reproductive allocation; stageDistribution follows DevelopmentStage enum order. No database/event bus and no frozen deviation.

## Task 17 - VALIDATED
RED: missing CommandLine.h. GREEN: CLI 2/2; full CTest including headless_smoke 52/52 (32.90 seconds).
Review: headless never initializes raylib window, fixed ticks per frame, pause/single-step, const-only renderer, seven field overlays, organism debug panel, explicit CLI numeric/flag failures. Real raylib 5.5 GLFW/OpenGL 3.3 Intel UHD initialization and 100-tick exit PASS. reproduction_assay seed 99 at tick 100: visual and headless both digest 17128848772829224968, one worm, zero eggs, no guard.
Ruling: headless with no --ticks defaults to the planned 250,000-tick run. Output goes to output/<scenario>-<seed>. No frozen deviation.

## Task 18 - acceptance verification in progress
Added BehaviorTests and FullLifeTests before integration fixes. All task assays and regressions now pass: final clean-directory Release build, CTest 63/63 (47.27 seconds), Catch2 62 cases / 575485 assertions. Calibration: Egg-to-Adult 29409 ticks, fed adult median 87772 (seeds 11/22/33/44/55), fed DMP 150. No rate-default adjustment or fixedDt change needed.
Real final-build Renderer execution preserved the digest on every draw and matched headless at tick 100, seed 99, reproduction_assay: 10408388582522398976. Screenshot inspected: segmented worm, distinct head, field and selected-organism data render correctly.
Necessary integration findings corrected:
- Default-rate Dauer induction originally failed because the scenario's pheromone decayed and food regrew toward one. Maintain low carrying density 0.05 and a source balancing pheromone decay. Default-rate integrated L2d/Dauer/recovery now passes; DevelopmentSystem was not rewritten.
- Worm mass omitted gut content from frozen section 3.8. Added actual gut contribution to structural/reserve mass and a test checking total Body node mass.
Assay rulings: nose contact is transient, so compare the complete response window rather than only its last tick; repeated-pulse habituation isolates mechanical consequences without simultaneous food/cue reinforcement, which otherwise recruits the separate associative mechanism. The paired-learning assay explicitly retains that reinforcement and its unpaired control. No valid frozen expectation was weakened.
Reviewed accumulated implementation diff from Task 1, including original subsystem tests and new integration. Frozen marker, exact spec and implementation plan remain unchanged. No selector, simulation threading, event bus, ECS, world/coordinate input to Brain/Learning, or renderer mutation found.
Remaining final gate: 250000-tick baseline seed 12345 using final build. An earlier run from the superseded build was stopped and is not acceptance evidence. All 35 DoD entries are mapped in README; final status awaits that runtime. Upstream warnings: raylib CMake compatibility and four jar_mod.h stringop-overflow diagnostics; no project compiler warnings/errors were found.

### Task 18 initialization boundary correction
The mass invariant also needs to hold before the first tick. Added an initial-state assertion, which reproduced 12 versus expected 1.1 total mass in an adult founder. Constructor now distributes structural plus reserve mass across nodes using the same convention as subsequent updates. Task-related regression 10/10; full CTest again 63/63 (47.71 seconds), now 575486 Catch2 assertions. Calibration remains within range and real visual/headless digest still matches 10408388582522398976.
The long run was restarted on the corrected binary; superseded runs are not final acceptance evidence. Headless now reports tick/worm/egg counts every 10000 ticks to stderr so the required long validation is observable; grouping only changes diagnostics, not fixedDt or core decisions.
