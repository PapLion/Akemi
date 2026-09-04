# C.E-PSVAML V1 — Especificación técnica

**Proyecto:** Caenorhabditis elegans — Proyecto Seres Vivos al ML  
**Repositorio:** `PapLion/Akemi`  
**Versión de diseño:** V1  
**Fecha:** 2026-09-03  
**Estado:** Especificación de diseño para revisión antes de implementación  

---

## 0. Propósito y filosofía

C.E-PSVAML es el primer escalón de una línea experimental cuyo objetivo a largo plazo es estudiar, desde sistemas mínimos, cómo se combinan cuerpo, percepción, estado interno, memoria, aprendizaje, desarrollo, reproducción y evolución hasta llegar a agentes artificiales mucho más complejos.

El objetivo de V1 no es crear un gemelo digital molecular de *Caenorhabditis elegans*, ni un videojuego con apariencia de gusano, ni un agente abstracto de RL disfrazado de organismo. El objetivo es construir un **organismo digital funcionalmente completo** inspirado en *C. elegans* que pueda completar de forma autónoma un ciclo de vida coherente dentro de una simulación.

La filosofía acordada es:

> **Arquitectura C, experiencia A, implementación B.**

- **C — Híbrido progresivo:** separar correctamente los sistemas para que cada uno tenga una responsabilidad clara.
- **A — Sensación de fidelidad biológica:** al observar el organismo, debe comportarse y vivir de una forma reconociblemente inspirada en *C. elegans*.
- **B — Implementación abstraída:** los mecanismos microscópicos pueden comprimirse matemáticamente siempre que se conserve la causalidad biológica importante.

La regla de alcance de V1 es:

> **Cobertura funcional antes que profundidad.**

V1 debe contener todas las capacidades necesarias para que el organismo pueda percibir, moverse, alimentarse, mantener su fisiología, aprender de forma básica, desarrollarse, entrar en dauer cuando corresponda, reproducirse, envejecer, morir y dejar descendencia heredable. Ningún subsistema necesita ser hiperrealista en V1.

### 0.1. Qué significa “se siente como A”

Una abstracción es aceptable si mantiene la cadena causal relevante.

Ejemplo correcto:

```text
bacteria/food field
    -> detección química local
    -> decisión neural
    -> locomoción
    -> pharyngeal pumping
    -> alimento ingerido
    -> absorción
    -> energía y reservas
    -> crecimiento / reproducción
```

Ejemplo incorrecto:

```text
worm touches food
    -> +10 reward
    -> +20 energy
```

El segundo puede funcionar como videojuego, pero elimina precisamente los mecanismos que el proyecto pretende estudiar.

### 0.2. Principio de no sobreingeniería

El proyecto se implementará principalmente para ser comprendido, ejecutado y estudiado, no como framework genérico reutilizable.

No se diseñará para soportar arbitrariamente cualquier animal futuro. Si otro organismo se implementa después, se reutilizarán las ideas y, solo cuando resulte natural, parte del código.

V1 evita deliberadamente:

- ECS completo;
- event bus genérico;
- dependency injection;
- factories e interfaces sin necesidad inmediata;
- arquitectura plugin;
- motor físico generalista;
- arquitectura pensada para Akemi/Yoru/Nix;
- mundo 3D;
- simulación molecular o celular completa.

---

# 1. Arquitectura general

## 1.1. Stack

- **Lenguaje:** C++17 o superior.
- **Render:** raylib 2D.
- **Build:** CMake.
- **Simulación:** fixed timestep independiente del render.
- **Modo visual:** raylib.
- **Modo entrenamiento/experimentos:** headless, sin inicializar raylib.
- **Aleatoriedad:** generador seeded único propiedad de `Simulation`.

## 1.2. Modelo orientado a objetos

La arquitectura será OOP por composición.

```text
Application
└── Simulation
    ├── World
    ├── Population
    │   ├── Worm[]
    │   │   ├── Genome
    │   │   ├── Body
    │   │   ├── Physiology
    │   │   ├── SensorySystem
    │   │   ├── NervousSystem
    │   │   ├── LearningSystem
    │   │   ├── DevelopmentSystem
    │   │   └── ReproductiveSystem
    │   └── Egg[]
    ├── MetricsRecorder
    └── Renderer (solo modo visual)
```

`Worm` es la entidad central y contiene sus sistemas internos. `World` contiene el ambiente. `Population` mantiene individuos, huevos y linajes. `Simulation` coordina el tiempo y el orden de actualización.

## 1.3. Responsabilidades

### `Application`

Responsable únicamente de:

- crear configuración;
- seleccionar modo visual/headless;
- inicializar/cerrar raylib cuando proceda;
- crear `Simulation`;
- ejecutar el loop principal.

No contiene biología.

### `Simulation`

Posee:

- `World world`;
- `Population population`;
- `SimulationConfig config`;
- RNG seeded;
- tick global;
- métricas.

Responsabilidades:

1. avanzar el reloj;
2. actualizar el mundo;
3. actualizar organismos;
4. resolver huevos/nacimientos;
5. retirar muertos;
6. actualizar población/linajes;
7. registrar métricas;
8. renderizar solo cuando corresponda.

`Simulation` no decide qué organismo es “mejor”.

### `Worm`

Representa un individuo vivo. Coordina sus propios subsistemas, pero no controla el mundo ni la evolución poblacional.

### `Renderer`

Es read-only respecto a la simulación. Puede observar y dibujar estado, pero nunca modifica posición, energía, comportamiento ni reglas.

## 1.4. Fixed timestep

El tiempo lógico nunca depende del FPS.

Valor inicial recomendado:

```text
simulationHz = 50
fixedDt = 0.02 s biológicos simulados por tick base
renderHz ≈ 60 FPS
```

La escala temporal visual podrá multiplicarse ejecutando múltiples ticks antes de renderizar.

Incorrecto:

```text
dt *= 1000
```

Correcto:

```text
for 1000 iterations:
    simulation.tick(fixedDt)
renderOnce()
```

Esto evita tunneling y diferencias entre simulación visual y headless.

---

# 2. World / Environment

## 2.1. Objetivo

`World` contiene todo lo externo al organismo. El cerebro nunca consulta `World` directamente; solamente `SensorySystem` puede transformar el mundo en señales sensoriales.

## 2.2. Arena

V1 utiliza un espacio 2D continuo.

Configuración base sugerida:

```text
worldWidth  = 1000 simulation units
worldHeight = 1000 simulation units
```

Las posiciones son `Vector2` continuos, no celdas discretas para el cuerpo.

### Boundary modes

El mundo soportará dos modos simples:

- `Toroidal`: salir por un borde introduce al organismo por el borde opuesto. Modo recomendado para ecosistema general porque evita comportamiento artificial de esquina.
- `Closed`: paredes físicas. Útil para tests de nose-touch y navegación.

No se implementa mundo infinito ni generación procedural por chunks en V1.

## 2.3. Representación espacial de campos

Los fenómenos ambientales continuos se representan mediante grids escalares de baja resolución con interpolación bilinear.

Ejemplos:

```text
FoodDensity(x, y)
FoodQuality(x, y)
FoodOdor(x, y)
Repellent(x, y)
DauerPheromone(x, y)
Temperature(x, y)
Oxygen(x, y)
Vibration(x, y)
```

Una resolución inicial razonable es `128 x 128` para un mundo de `1000 x 1000`, configurable.

No se simulan moléculas individuales.

## 2.4. Alimento bacteriano

Las bacterias no serán NPCs móviles.

`FoodField` representa densidad bacteriana y calidad nutricional.

Cada celda mantiene como mínimo:

```text
foodDensity      [0,1]
nutritionalValue > 0
digestibility    [0,1]
toxicity         [0,1]
```

V1 puede comenzar con una sola especie bacteriana estándar y permitir variantes de parámetros en escenarios de prueba.

### Consumo

La comida solo disminuye cuando:

1. la boca está sobre una región con alimento;
2. el pharyngeal pump está activo;
3. existe capacidad para ingerir.

`World::consumeFood(position, amount)` devuelve cuánto alimento fue realmente retirado.

### Regeneración

La densidad bacteriana puede regenerarse lentamente mediante un `foodRegrowthRate` configurable. Esto evita tener que generar NPCs y permite equilibrio ecológico.

## 2.5. Química

V1 usa tres familias funcionales:

1. **Attractant / food odor** — señales asociadas a comida.
2. **Repellent / noxious cue** — señales aversivas.
3. **Dauer pheromone** — señal poblacional usada en desarrollo.

El attractant alimentario puede derivarse de `FoodDensity` mediante difusión discreta simplificada.

La pheromone de dauer es depositada por organismos vivos, difunde localmente y decae con el tiempo. Por tanto su concentración se convierte naturalmente en aproximación de densidad poblacional.

## 2.6. Temperatura

`TemperatureField` devuelve una temperatura continua por posición.

V1 debe soportar al menos:

- temperatura uniforme;
- gradiente lineal;
- gradiente radial.

No se simulan sol, lluvia, noche ni meteorología.

La temperatura afecta:

- sensación neural;
- velocidad de desarrollo;
- metabolismo;
- estrés térmico;
- decisión de dauer.

## 2.7. Oxígeno

`OxygenField` devuelve concentración relativa por posición.

V1 utiliza un rango de preferencia configurable inspirado en aerotaxis de *C. elegans*. El valor ambiental puede ser estático o un gradiente.

No se requiere dinámica de gases real.

Como extensión sencilla, zonas bacterianas densas pueden reducir ligeramente el oxígeno local.

## 2.8. Entorno mecánico

`MechanicalEnvironment` proporciona:

- colisiones con paredes/obstáculos;
- vibraciones ambientales;
- impulsos mecánicos programados;
- contacto dañino opcional en escenarios.

No existe un depredador permanente en V1.

Para experimentos de habituación se usan `MechanicalStimulusSource` simples que pueden generar:

- estímulo repetido inofensivo;
- estímulo ocasional dañino;
- vibración que aumenta/disminuye con distancia.

## 2.9. Qué NO modela World V1

- partículas de tierra;
- suelo volumétrico;
- humedad meteorológica compleja;
- día/noche;
- lluvia;
- bacterias individuales móviles;
- ecosistema de depredadores completo;
- ray tracing químico;
- difusión molecular real.

---

# 3. Body / Biomechanics

## 3.1. Objetivo

El organismo debe ser corporalmente encarnado. El cerebro no altera `x/y` directamente; produce actividad motora que causa deformaciones corporales y éstas producen locomoción al interactuar con el medio.

## 3.2. Rig

El cuerpo se representa como una cadena de nodos 2D.

Valor inicial recomendado:

```text
bodySegmentCount = 12
```

Cada nodo mantiene:

```text
position
previousPosition o velocity
mass
```

El cuerpo mantiene además:

```text
restSegmentLength
bodyRadius
bodyStiffness
currentLength
headIndex = 0
```

El primer nodo es cabeza; el último es cola.

## 3.3. Restricciones físicas

Se utiliza una física simple tipo position-based dynamics / Verlet:

1. integrar movimiento;
2. aplicar resistencia del medio;
3. satisfacer restricciones de longitud entre nodos;
4. aplicar bending constraints;
5. resolver colisiones;
6. repetir pocas iteraciones de constraints.

No se implementa un motor físico general.

## 3.4. Locomoción

La locomoción real de *C. elegans* depende de contracciones alternantes dorsal/ventral y produce ondas sinusoidales.

V1 abstrae esa neuromusculatura mediante un generador de patrón corporal local (`MotorPatternGenerator`) controlado por el cerebro.

Curvatura objetivo de un segmento `i`:

```text
targetCurvature(i,t)
    = amplitude * sin(phase(t) - spatialFrequency * i)
    + turnBias * turnProfile(i)
```

`phase` avanza en dirección opuesta durante reversa.

## 3.5. Resistencia del medio

V1 puede utilizar drag efectivo longitudinal/lateral para conseguir crawling estable:

```text
velocity = tangentComponent + normalComponent

tangentComponent *= longitudinalDrag
normalComponent   *= lateralDrag
```

Esto se documenta explícitamente como **abstracción física del substrato**, no como afirmación de que el gusano utiliza micro-pelos de serpiente.

## 3.6. Motor outputs

El cuerpo recibe un `MotorCommand` continuo:

```text
forwardDrive    [0,1]
reverseDrive    [0,1]
turnBias        [-1,1]
headSweepDrive  [0,1]
pumpDrive       [0,1]
```

El cuerpo nunca recibe Norte/Sur/Este/Oeste.

## 3.7. Patrones observables requeridos

V1 debe poder producir:

- forward locomotion;
- reversal;
- curvatura gradual;
- giro fuerte / omega-like turn;
- reversal + strong turn / pirouette-like reorientation;
- head sweep / foraging con locomoción baja.

No es obligatorio que cada patrón sea un `enum`; pueden emerger de combinaciones de comandos continuos.

## 3.8. Masa

La masa corporal se deriva de:

```text
structuralMass(stage, size)
+ reserveMass(lipidReserve)
+ gutMass(gutContent)
```

No existen arquetipos artificiales `Tank`, `Speedster` o `Standard`.

Cambios extremos en reserva pueden afectar de forma moderada la dinámica corporal, pero no reescriben directamente genes de velocidad de descendientes.

---

# 4. Physiology

## 4.1. Objetivo

`Physiology` modela lo necesario para permanecer vivo: alimentación, digestión, metabolismo, reservas, residuos, estrés, daño y envejecimiento.

No existe una barra RPG de hambre que por sí sola defina toda la vida.

## 4.2. Estado principal

V1 mantiene como mínimo:

```text
availableEnergy
lipidReserve
gutLoad
wasteLoad
starvationStress
thermalStress
mechanicalDamage
agingDamage
biologicalAge
```

Opcionalmente puede exponerse una `healthDisplay` derivada para UI, pero no se utiliza internamente como HP mágico.

## 4.3. Pharyngeal pumping

La faringe funciona como neuromuscular pump.

`pumpDrive` controla la intensidad/frecuencia de pumping dentro de límites fisiológicos.

Un pump exitoso:

1. consulta alimento disponible en la boca;
2. retira una cantidad del `FoodField`;
3. genera un `DigestivePacket`;
4. consume una pequeña cantidad de energía.

## 4.4. DigestivePacket

Para soportar alimento variable sin sobrecomplicar el intestino:

```text
DigestivePacket
- totalMass
- energyPotential
- lipidPotential
- digestibility
- toxicity
- transitRemaining
```

`Physiology` mantiene una cola pequeña de packets.

Por tick:

- parte de su contenido se absorbe;
- parte se convierte en residuos;
- `transitRemaining` disminuye;
- al finalizar tránsito, el residuo pasa a `wasteLoad`.

No existe una mecánica arbitraria de “comió demasiado y explota el intestino”. Si `gutLoad` alcanza capacidad, la ingesta simplemente pierde eficiencia o se detiene.

## 4.5. Energía

Balance por tick:

```text
energyDelta
  = absorbedEnergy
  + mobilizedReserve
  - basalMetabolism
  - movementCost
  - pumpingCost
  - growthCost
  - reproductiveCost
  - stressCost
```

`availableEnergy` es combustible de uso inmediato.

Si cae por debajo del umbral de seguridad, se moviliza `lipidReserve` con una eficiencia menor a 1.

Si energía y reserva permanecen insuficientes, aumenta `starvationStress`.

## 4.6. Reservas

El excedente energético puede convertirse parcialmente en `lipidReserve`.

Las reservas tienen límites fisiológicos configurables. No se usan categorías de obesidad/anorexia como clases hereditarias.

Estado muy bajo de reserva:

- reduce crecimiento;
- reduce reproducción;
- aumenta riesgo por inanición.

Estado excesivamente alto puede aumentar ligeramente coste locomotor/metabólico, pero V1 no necesita patologías complejas de obesidad.

## 4.7. Defecación

La defecación es un proceso fisiológico automático, no un output neuronal de alto nivel.

V1 conserva un `DefecationMotorProgram` simplificado con periodo basal aproximado de 45 segundos biológicos en condiciones de alimentación abundante.

En cada ciclo:

1. posterior body contraction abstracta;
2. anterior contraction abstracta;
3. expulsion;
4. `wasteLoad` disminuye.

El DMP puede modificar visualmente la curvatura corporal durante pocos ticks, pero no requiere simular cada músculo entérico.

## 4.8. Temperatura y metabolismo

La temperatura modifica tasas mediante un factor suave:

```text
metabolicRate = baseMetabolicRate * temperatureFactor(T)
developmentRate = baseDevelopmentRate * developmentTemperatureFactor(T)
```

Fuera de un rango viable aumenta `thermalStress` progresivamente.

## 4.9. Daño

El daño se descompone en causas, no HP único:

```text
mechanicalDamage
starvationStress
thermalStress
agingDamage
optionalToxicDamage
```

La muerte puede ocurrir por:

- daño mecánico catastrófico;
- inanición sostenida;
- estrés térmico extremo sostenido;
- toxicidad;
- riesgo de mortalidad asociado a edad/daño.

## 4.10. Envejecimiento

No existe un `maxLifespan` que mate exactamente al llegar a un tick.

Se utiliza un hazard de mortalidad creciente:

```text
mortalityHazard
  = baselineAgeHazard(age, genome)
  + stressHazard
  + accumulatedDamageHazard
```

Cada tick se evalúa con RNG seeded.

La genética puede cambiar parámetros del hazard, pero dos individuos genéticamente idénticos no tienen obligación de morir al mismo tick.

---

# 5. Sensory System

## 5.1. Regla principal

El organismo jamás conoce información global como:

```text
nearestFoodPosition = (x,y)
```

Solo conoce señales que razonablemente puede percibir localmente.

## 5.2. `SensoryState`

V1 genera un snapshot normalizado aproximadamente en `[-1,1]` o `[0,1]`:

```text
foodAttractant
foodAttractantDelta
repellent
repellentDelta
temperature
temperatureDelta
temperatureErrorToPreference
oxygen
oxygenErrorToPreference
noseTouch
bodyTouch
vibration
foodAtMouth
energyDeficit
headCurvature
meanBodyCurvature
forwardSpeed
recentFoodMemory
```

No todas las variables necesitan entrar crudas a la red; algunas son derivadas sensoriales.

## 5.3. Quimiotaxis

La cabeza muestrea concentración local.

La memoria temporal conserva valores recientes para calcular:

```text
foodAttractantDelta = current - previous
```

Esto evita entregarle mágicamente la dirección exacta del gradiente.

El head sweep crea además muestreo espacial porque la nariz cambia de posición.

## 5.4. Repulsión / nocicepción

Repellents fuertes y nose-touch generan señales rápidas de alta prioridad. El cerebro puede aprender/modular respuesta, pero la red inicial incluye una predisposición innata de retirada.

## 5.5. Termotaxis

La señal térmica incluye:

- temperatura actual;
- cambio temporal;
- diferencia respecto a `preferredTemperature` almacenada por `LearningSystem`.

El animal no memoriza coordenadas de chunks.

## 5.6. Mecanorrecepción

Se distinguen:

- `noseTouch`: contacto anterior;
- `bodyTouch`: contacto corporal;
- `vibration`: movimiento del medio sin contacto directo.

## 5.7. Propiocepción

El sistema recibe información derivada de la geometría corporal:

- curvatura de cabeza;
- curvatura media;
- velocidad longitudinal.

El `MotorPatternGenerator` puede utilizar información segmentaria adicional internamente sin enviar todos los nodos al cerebro global.

## 5.8. Aerotaxis

El organismo recibe oxígeno local y su desviación respecto a un rango preferido. V1 usa preferencia intermedia configurable.

## 5.9. Señales internas

El cerebro recibe señales interoceptivas resumidas como:

- déficit energético;
- estrés fisiológico general;
- estado de alimentación reciente;
- etapa de desarrollo relevante.

No recibe todos los campos de `Physiology` directamente.

---

# 6. Nervous System

## 6.1. Objetivo V1

El sistema nervioso debe:

- mantener estado temporal;
- integrar múltiples sensores;
- producir acciones continuas;
- permitir plasticidad durante la vida;
- ser pequeño y comprensible;
- no intentar reproducir aún las ~302 neuronas reales.

## 6.2. Arquitectura elegida

V1 utiliza una **small continuous-time recurrent neural network (CTRNN)** funcionalmente inspirada en circuito sensor-interneurona-motor.

No se pretende que cada nodo corresponda a una neurona real específica.

### Topología base

Recomendación inicial:

```text
~16 sensory/interoceptive features
        ↓
12 recurrent internal neurons
        ↓
5 motor/behavior outputs
```

El número exacto vive en `BrainConfig`, pero V1 de referencia utilizará 12 neuronas recurrentes.

## 6.3. Dinámica CTRNN

Para neurona recurrente `i`:

```text
tau_i * dv_i/dt
    = -v_i
      + sum_j(w_ij * activation_j)
      + sum_k(inputWeight_ik * input_k)
      + bias_i

activation_i = tanh(v_i)
```

Actualización discreta por fixed tick:

```text
v_i += dt/tau_i * (...)
```

Los estados `v_i` proporcionan memoria temporal sin necesidad de aumentar `dt` ni guardar una secuencia completa.

## 6.4. Outputs

La red produce:

```text
forwardDrive
reverseDrive
turnBias
headSweepDrive
pumpDrive
```

Activaciones se normalizan/clamp antes de llegar al cuerpo/faringe.

## 6.5. Priors innatos

La población inicial no parte necesariamente de una red completamente aleatoria e incapaz de vivir.

`Genome::baseline()` contiene pesos iniciales débiles que codifican reflejos básicos:

- nose touch / fuerte repellent -> tendencia a reversal;
- food at mouth -> tendencia a pumping;
- déficit energético -> aumento de exploración/pumping cuando hay comida;
- food abundance -> menor drive locomotor medio;
- fuerte señal nociva -> mayor reorientación.

Estos comportamientos se codifican como pesos y biases iniciales, no como `if/else` que anulan la red.

Mutación y aprendizaje pueden modificarlos.

## 6.6. Behavioral states

Roaming, dwelling, local search y dispersal no son necesariamente enums rígidos.

Se observan a partir de:

- velocidad;
- reversals;
- turn rate;
- food memory;
- pumping;
- recurrent neural state.

Para telemetría, `BehaviorClassifier` puede etiquetar post-hoc segmentos de comportamiento sin controlar al gusano.

## 6.7. Brain state heredado vs adquirido

`Genome` almacena:

- pesos base;
- biases;
- time constants;
- gains;
- plasticity parameters.

Cada `Worm` crea una copia mutable de pesos efectivos al nacer.

`LearningSystem` modifica la copia durante la vida. Esas modificaciones no se escriben automáticamente de vuelta al `Genome`.

---

# 7. Learning & Memory

## 7.1. Principio

Se separan estrictamente:

```text
aprendizaje individual = cambios durante una vida

evolución = cambios heredables entre generaciones
```

No se utilizará un reward externo `+1/-1` como sustituto de fisiología.

## 7.2. Memoria temporal sensorial

El sistema mantiene traces exponenciales de señales relevantes:

```text
trace = trace * exp(-dt/tau) + current * (1-exp(-dt/tau))
```

Permite:

- derivadas químicas;
- derivadas térmicas;
- food history;
- búsqueda local/distant search;
- habituación.

## 7.3. Habituación

Para mecanosensación repetida:

```text
habituation += learningRate * harmlessStimulus
habituation -= recoveryRate * dt
```

La señal efectiva:

```text
effectiveTouch = rawTouch * (1 - habituation)
```

Si el estímulo produce daño real:

```text
habituation *= dishabituationFactor
```

o se reduce bruscamente.

No existe un número mágico “20 golpes”. La adaptación depende de intensidad, frecuencia, intervalo y consecuencia.

## 7.4. Associative plasticity

Para permitir asociación básica entre cues y consecuencias, una fracción de pesos input→recurrent es plástica.

Eligibility trace:

```text
eligibility_ij
    = lambda * eligibility_ij
    + pre_i * post_j
```

Señal interna de valencia:

```text
internalValence
    = positiveGain * normalizedNutrientAbsorption
    - damageGain * damageDelta
    - starvationGain * starvationStressDelta
    - toxicGain * toxicStressDelta
```

Plasticidad:

```text
weight_ij += learningRate * internalValence * eligibility_ij
```

Los pesos se clamp dentro de límites estables.

Esto permite que una señal inicialmente neutra asociada repetidamente a comida o daño cambie su influencia conductual sin usar un entrenador externo.

## 7.5. Memoria térmica

`preferredTemperature` es estado adquirido.

Cuando el organismo permanece bien alimentado y con bajo estrés:

```text
preferredTemperature
  += thermalLearningRate
     * (currentTemperature - preferredTemperature)
     * feedingContext
```

La actualización es lenta, simulando memoria de temperatura de cultivo de manera funcional.

## 7.6. Food memory

`recentFoodMemory` aumenta al ingerir alimento y decae gradualmente.

Al perder comida recientemente:

- reversals/turning pueden aumentar -> local search.

Tras un periodo prolongado sin comida:

- reversals disminuyen;
- drive longitudinal aumenta -> dispersal/traveling.

La red recibe `recentFoodMemory`; no se hardcodea una ruta espacial.

---

# 8. Development / Life Cycle

## 8.1. Ciclo normal

V1 reproduce:

```text
Egg
 -> hatch
L1
 -> lethargus/molt
L2
 -> lethargus/molt
L3
 -> lethargus/molt
L4
 -> lethargus/molt
Adult
 -> aging
Death
```

L4 **no** es adulto.

## 8.2. Estados

`DevelopmentStage`:

```text
L1
L2
L2d
Dauer
DauerRecovery
L3
L4
Adult
```

`Egg` se representa con clase propia antes de eclosión.

`DevelopmentPhase`:

```text
Growing
Lethargus
```

Dauer y recovery tienen comportamiento especializado.

## 8.3. Stage progress

Cada etapa mantiene:

```text
stageProgress [0,1]
```

La tasa:

```text
developmentRate
  = baseStageRate
    * temperatureFactor
    * nutritionFactor
    * stressFactor
```

No existen etapas inventadas L1.5/L2.5/L3.5.

## 8.4. Lethargus y muda

Al completar una etapa larvaria:

1. entra `Lethargus`;
2. pharyngeal pumping se detiene;
3. locomoción se reduce de forma drástica;
4. desarrollo de nueva cutícula se abstrae como timer/progress;
5. al finalizar, aumenta tamaño corporal y cambia stage.

Lethargus es distinto de dauer.

## 8.5. Dauer

Dauer es una ruta de desarrollo, no habilidad defensiva inmediata.

Factores de entrada:

- alta dauer pheromone / densidad poblacional;
- baja comida;
- temperatura desfavorable, especialmente alta dentro del rango relevante;
- condición fisiológica.

La decisión se integra durante L1/L2.

Si las condiciones favorecen dauer:

```text
L1 -> L2d -> Dauer
```

No se usa `Enter_Dauer` como output neuronal ni `dauerCooldown`.

### Estado Dauer

Durante dauer:

- no feeding/pumping;
- desarrollo arrestado;
- metabolismo muy reducido;
- locomoción reducida pero no necesariamente cero;
- mayor resistencia a estrés;
- reproducción deshabilitada;
- envejecimiento efectivo ralentizado.

### Salida

La recuperación requiere condiciones favorables sostenidas:

- comida disponible;
- menor señal de población;
- temperatura adecuada.

Ruta:

```text
Dauer
 -> DauerRecovery
 -> pumping resumes
 -> molt
 -> L4
 -> Adult
```

## 8.6. Tamaño

Cada stage tiene un `targetBodyScale`. El cuerpo se interpola gradualmente hacia ese tamaño durante desarrollo.

No se cambia instantáneamente el sprite.

---

# 9. Reproduction

## 9.1. Alcance

V1 modela únicamente **hermafroditas autofértiles**.

Males, mating y sexual selection quedan para una versión posterior.

Esta simplificación permite reproducción real sin implementar dos anatomías sexuales completas.

## 9.2. Proceso funcional

La abstracción conserva:

```text
larval sperm production
    -> sperm reserve
adult oocyte maturation
    -> ovulation
    -> spermathecal fertilization
    -> embryo/zygote
    -> uterine holding
    -> egg laying
    -> Egg entity in World
```

No se simula cada célula germinal.

## 9.3. Sperm reserve

Durante late L4 se genera `spermReserve` con capacidad genética/configurable.

Al entrar a adulto, la producción principal cambia a oocitos.

Cada fertilización consume una unidad de sperm reserve.

Al agotarse, la autofertilización termina aunque el organismo pueda seguir vivo.

## 9.4. Oocyte maturation

`ReproductiveSystem` mantiene:

```text
reproductiveResources
oocyteProgress
spermReserve
uterineEggs[]
```

Los recursos reproductivos provienen de `Physiology`.

La maduración se ralentiza bajo:

- starvation;
- reservas bajas;
- estrés fuerte.

## 9.5. Maternal provisioning

La calidad fisiológica parental afecta al descendiente mediante **recursos provisionados**, no reescribiendo genes arbitrariamente.

Al fertilizar:

```text
maternalProvision
  = function(reproductiveResources,
             nutritionState,
             stressState,
             oocyteInvestment)
```

El provisioning afecta:

- reservas iniciales del embrión/L1;
- probabilidad de completar embryogenesis bajo estrés;
- condición inicial.

No crea automáticamente un hijo “tank” o “speedster”.

## 9.6. Egg entity

`Egg` contiene:

```text
id
parentId
generation
Genome genome
position
maternalProvision
embryoProgress
age
viabilityStress
```

El genoma del huevo se crea a partir del genoma parental mediante mutación/herencia.

`Population` mantiene huevos separados de worms móviles.

## 9.7. Embryogenesis

El progreso del huevo depende principalmente de:

- temperatura;
- provision maternal;
- condiciones letales extremas.

Al completar `embryoProgress`, el huevo eclosiona y `Population` crea un `Worm` en L1.

## 9.8. Egg laying

La puesta depende de:

- huevos uterinos disponibles;
- timing interno;
- estado fisiológico;
- contexto de alimentación.

V1 puede modelarla dentro de `ReproductiveSystem` con una modulación neural general en lugar de simular circuitos HSN/VC específicos.

---

# 10. Genome / Population / Evolution

## 10.1. Principio evolutivo

No existe una función obligatoria:

```text
Fitness = lifespan * a + eggs * b + children * c
```

El éxito evolutivo primario es literal:

> un linaje que deja más descendencia viable aumenta su representación en la población.

Los scores pueden calcularse como métricas, pero no son el dios de la simulación.

## 10.2. Genome

`Genome` almacena solamente estado heredable.

Familias de parámetros:

### Body genes

```text
bodyStiffness
structuralMassScale
muscleStrength
baselineWaveFrequency
baselineWaveAmplitude
```

### Physiology genes

```text
baseMetabolicRate
digestiveEfficiency
reserveStorageEfficiency
reserveMobilizationEfficiency
starvationTolerance
thermalTolerance
agingHazardParameters
```

### Sensory / neural genes

```text
sensorGains
inputWeights
recurrentWeights
outputWeights
neuralBiases
neuralTimeConstants
```

### Learning genes

```text
plasticityRate
eligibilityDecay
habituationRate
habituationRecovery
thermalLearningRate
```

### Development genes

```text
developmentRateScale
dauerSensitivity
stressDevelopmentPenalty
```

### Reproduction genes

```text
reproductiveAllocation
oocyteMaturationRate
spermCapacityScale
eggProvisionBias
```

Los valores tienen rangos válidos para evitar mutaciones físicamente absurdas.

## 10.3. Mutación

La configuración de mutación pertenece a `SimulationConfig`, no necesita evolucionar en V1.

Al crear un huevo:

```text
childGenome = parentGenome
for each mutable parameter:
    with probability mutationProbability:
        value += Gaussian(0, mutationSigma)
        value = clamp(value, min, max)
```

Los neural weights pueden tener mutation sigma independiente.

## 10.4. Selfing simplificado

V1 no simula cromosomas diploides ni recombinación meiótica completa.

Autofertilización se abstrae como:

```text
parent genome copy + mutation
```

Esto mantiene la dinámica evolutiva necesaria sin implementar genética molecular.

## 10.5. Population

`Population` mantiene:

```text
worms
eggs
nextEntityId
lineage records
population metrics
```

Cada organismo tiene:

```text
id
parentId
generation
birthTick
deathTick
```

Generación:

```text
child.generation = parent.generation + 1
```

Las generaciones son continuas y se solapan. No se espera a que toda una generación muera para crear la siguiente.

## 10.6. Selección

No se elimina activamente a los individuos “malos”.

La selección surge por:

- capacidad para encontrar alimento;
- supervivencia;
- llegar a adulto;
- recursos disponibles;
- reproducción;
- viabilidad de descendencia;
- competencia indirecta por comida.

Puede implementarse más tarde un modo de selección artificial separado, pero no forma parte del ecosistema base.

## 10.7. Population safety guard

Para evitar que un bug de reproducción consuma toda la RAM:

```text
maxPopulationSafety
```

no mata organismos silenciosamente. Si se supera:

- la simulación pausa o finaliza;
- registra error/guard trigger.

Esto es una protección del software, no una regla biológica.

---

# 11. Simulation, raylib, Headless y Observability

## 11.1. Modos

### Visual

- raylib activo;
- simulation core idéntico;
- render cada frame;
- velocidad 0.25x / 1x / 5x / 20x configurable;
- pausa;
- single-step.

### Headless

- raylib no se inicializa;
- ejecutar ticks tan rápido como permita CPU;
- mismo `Simulation::tick()`;
- guardar métricas periódicas.

## 11.2. Determinismo

Una ejecución está definida por:

```text
seed
SimulationConfig
initial genomes
initial world state
```

Misma build + misma plataforma + mismos inputs deben producir el mismo resultado lógico para debugging.

No se exige reproducibilidad bit-perfect entre arquitecturas de CPU distintas.

## 11.3. Renderer

Visuales iniciales deliberadamente simples:

### Worm

- polyline / thick segments;
- cabeza distinguible;
- color/brightness según stage o estado;
- body nodes opcionales en debug.

### Food

- heatmap o puntos según densidad.

### Fields

Overlays togglables:

- food;
- food odor;
- repellent;
- pheromone;
- temperature;
- oxygen;
- vibration.

### Debug organism overlay

Al seleccionar un worm:

```text
id / parent / generation
stage / phase
age
energy
lipid reserve
gut load
starvation stress
thermal stress
sperm reserve
uterine eggs
preferred temperature
recent food memory
brain outputs
```

## 11.4. Métricas

Por individuo:

```text
birthTick
deathTick
deathCause
lifetime
foodConsumed
energyAbsorbed
distanceTraveled
reversalCount
strongTurnCount
timeDwellingEstimate
timeRoamingEstimate
timeInDauer
eggsLaid
eggsHatched
childrenIds
maxGenerationDescendantSeen
```

Por población:

```text
populationSize
eggCount
birthsPerWindow
deathsPerWindow
stageDistribution
meanEnergy
meanReserve
meanAge
dauerCount
lineageDiversity
traitMeans
traitVariance
```

## 11.5. Logging

V1 usa formatos sencillos:

- CSV para time-series;
- CSV para lifetime summary;
- texto para eventos importantes.

No se requiere base de datos.

## 11.6. Replay/debug

El replay principal es determinista:

```text
seed + config + initial state -> rerun
```

No es necesario guardar cada frame.

## 11.7. Scenarios

Los experimentos viven como configuraciones/factories conocidas, por ejemplo:

```text
baseline_ecosystem
chemotaxis_assay
thermotaxis_assay
aerotaxis_assay
nose_touch_assay
habituation_assay
associative_learning_assay
starvation_assay
dauer_induction_assay
dauer_recovery_assay
reproduction_assay
```

No se necesita un editor visual de escenarios en V1.

---

# 12. Integración final

## 12.1. Orden de un tick

Orden V1 propuesto:

```text
1. Simulation increments global tick
2. World updates dynamic fields
   - food regeneration
   - chemical diffusion/decay
   - pheromone diffusion/decay
   - mechanical stimulus decay

3. For each Worm:
   a. SensorySystem samples World + Body + Physiology
   b. LearningSystem creates temporal/learned sensory modulation
   c. NervousSystem integrates one CTRNN step
   d. NervousSystem emits MotorCommand
   e. Body applies locomotor command
   f. Body integrates biomechanics and collisions
   g. Physiology executes pumping/feeding result
   h. Physiology updates digestion/metabolism/stress/aging
   i. LearningSystem updates plasticity from consequences
   j. DevelopmentSystem updates growth/lethargus/dauer
   k. ReproductiveSystem updates gametes/eggs
   l. Worm reports pending eggs/death if any

4. Population resolves newly laid Eggs
5. Population advances Egg embryogenesis
6. Population hatches ready Eggs -> new Worms
7. Population removes dead Worms after metrics snapshot
8. MetricsRecorder samples state
9. Renderer reads state if visual frame is due
```

## 12.2. Why consequences precede learning

El aprendizaje debe recibir lo que realmente ocurrió:

```text
observation
 -> decision
 -> action
 -> consequence
 -> plasticity
```

No debe actualizar pesos antes de saber si una acción produjo alimento, daño o estrés.

## 12.3. Data transfer structs

Para mantener código entendible, se utilizan pocos structs de transferencia.

### `SensoryState`

Datos normalizados percibidos en el tick.

### `InternalState`

Resumen fisiológico permitido al cerebro:

```text
energyDeficit
stressLevel
developmentContext
recentFoodMemory
```

### `MotorCommand`

```text
forwardDrive
reverseDrive
turnBias
headSweepDrive
pumpDrive
```

### `ActionConsequences`

```text
foodIngested
energyAbsorbed
damageDelta
starvationDelta
thermalStressDelta
distanceMoved
```

Learning utiliza este resumen.

### `EggBlueprint`

Datos necesarios para crear `Egg` sin que `ReproductiveSystem` modifique directamente `Population`.

No se crea un sistema de eventos genérico.

## 12.4. Clase `Worm` — interfaz conceptual

```text
Worm
- identity
- Genome
- Body
- Physiology
- SensorySystem
- NervousSystem
- LearningSystem
- DevelopmentSystem
- ReproductiveSystem

Public responsibilities:
- tick(World&, dt, RNG)
- isAlive()
- takePendingEggs()
- getReadOnlyDebugState()
```

Internamente `tick()` ejecuta sus subsistemas en el orden acordado.

## 12.5. `World` — interfaz conceptual

```text
sampleFood(position)
consumeFood(position, amount)
sampleFoodOdor(position)
sampleRepellent(position)
samplePheromone(position)
sampleTemperature(position)
sampleOxygen(position)
sampleVibration(position)
resolveCollision(body)
depositPheromone(position, amount)
update(dt)
```

## 12.6. `Body` — interfaz conceptual

```text
headPosition()
midBodyPosition()
bodySegments()
applyMotorCommand(command)
updatePhysics(world, dt)
headTouch()
bodyTouch()
curvatureSummary()
forwardSpeed()
```

## 12.7. `Physiology` — interfaz conceptual

```text
tryPump(world, mouthPosition, pumpDrive, dt)
updateMetabolism(actionCost, temperature, dt)
updateDigestion(dt)
updateDefecation(dt)
applyMechanicalDamage(amount)
summaryForBrain()
consequencesForLearning()
isDead()
deathCause()
```

## 12.8. `NervousSystem` — interfaz conceptual

```text
MotorCommand step(SensoryState, InternalState, dt)
applyPlasticWeightDelta(...)
resetFromGenome(genome)
```

## 12.9. `DevelopmentSystem` — interfaz conceptual

```text
update(worldSignals, physiologySignals, dt)
stage()
phase()
locomotionMultiplier()
pumpingAllowed()
metabolismMultiplier()
stressResistanceMultiplier()
isReproductivelyAdult()
```

## 12.10. `ReproductiveSystem` — interfaz conceptual

```text
update(physiology, development, dt)
vector<EggBlueprint> takeLaidEggs()
spermRemaining()
uterineEggCount()
```

---

# 13. Configuración inicial de referencia

Los siguientes valores no pretenden ser medidas biológicas finales; son **defaults de ingeniería** para iniciar implementación y posteriormente calibrar comportamiento sin modificar arquitectura.

```text
simulationHz               = 50
renderHz                   = 60
worldSize                  = 1000 x 1000
fieldGrid                  = 128 x 128
bodySegments               = 12
physicsConstraintIterations = 4
brainRecurrentNeurons      = 12
initialPopulation          = 32
boundaryMode               = Toroidal
```

Todos los rates biológicos importantes deben expresarse respecto a tiempo simulado, no frames.

Para desarrollo, la configuración debe poder comprimirse temporalmente sin alterar el orden relativo del ciclo. Un escenario de debug puede hacer que una vida dure minutos de reloj; un escenario de validación puede mapear tiempos a escalas biológicas más cercanas a laboratorio.

---

# 14. Escenarios y pruebas de aceptación

V1 no está terminada porque “compila”. Está terminada cuando los subsistemas pueden verificarse aisladamente y el ciclo completo funciona.

## 14.1. Physics / locomotion

### Test: forward locomotion

Dado un worm sano en medio uniforme y forward drive estable:

- genera onda corporal;
- centro de masa se desplaza;
- no se separan segmentos;
- movimiento no depende de FPS.

### Test: reversal

Al activar reverse drive:

- la propagación de la onda cambia;
- el worm se desplaza en sentido contrario relativo al eje corporal.

### Test: strong turn

Turn bias alto debe producir curvatura fuerte y reorientación omega-like sin teletransportar la cabeza.

## 14.2. Feeding

Dado un worm con boca sobre food patch:

- pump off -> no ingestión significativa;
- pump on -> food density disminuye;
- se crea contenido digestivo;
- la energía no aparece instantáneamente antes de absorción.

## 14.3. Metabolism

En ausencia de alimento:

- energía inmediata disminuye;
- después se movilizan reservas;
- después aumenta starvation stress;
- starvation sostenida puede causar muerte.

## 14.4. Defecation

En organismo alimentado:

- waste se acumula;
- DMP ocurre aproximadamente con el periodo configurado;
- waste disminuye tras expulsión.

## 14.5. Chemotaxis

En gradiente atractivo:

- un controlador baseline/evolucionado muestra mayor probabilidad de permanecer en dirección de concentración creciente;
- reducción brusca de attractant favorece reversal/turning.

El test no le entrega coordenadas del attractant.

## 14.6. Mechanosensation

Nose-touch fuerte:

- genera señal sensorial;
- baseline network favorece reversal.

## 14.7. Habituation

Estímulos repetidos inofensivos:

- respuesta promedio disminuye progresivamente.

Tras daño:

- la sensibilidad aumenta nuevamente.

## 14.8. Associative learning

Cue químico inicialmente neutro repetidamente seguido de alimento:

- cambia la influencia del cue sobre la red;
- el cambio ocurre en pesos efectivos del individuo;
- el genome original permanece intacto.

## 14.9. Thermotaxis memory

Tras exposición prolongada a una nueva temperatura en contexto favorable:

- `preferredTemperature` se desplaza lentamente hacia ella;
- el error térmico cambia en consecuencia.

## 14.10. Aerotaxis

En gradiente de O2:

- la señal de error cambia de signo alrededor del rango preferido;
- la red puede utilizarla para modificar locomoción.

## 14.11. Development

Un huevo viable:

```text
Egg -> L1 -> L2 -> L3 -> L4 -> Adult
```

Cada transición larvaria contiene lethargus y pumping suspendido.

## 14.12. Dauer induction

Con:

- food bajo;
- pheromone alta;
- temperatura que favorece dauer;

la probabilidad de:

```text
L1 -> L2d -> Dauer
```

aumenta fuertemente.

Un adult nunca entra repentinamente en dauer por ver un peligro.

## 14.13. Dauer recovery

Al mejorar condiciones durante periodo suficiente:

```text
Dauer -> Recovery -> L4 -> Adult
```

## 14.14. Reproduction

Un hermafrodita adulto sano con sperm reserve:

- madura oocitos;
- fertiliza;
- genera uterine egg;
- pone Egg en mundo;
- consume recursos reproductivos;
- sperm reserve disminuye.

## 14.15. Hatch / lineage

Egg puesto:

- completa embryogenesis;
- crea nuevo L1;
- child.parentId coincide;
- child.generation = parent.generation + 1;
- child genome contiene herencia + posibles mutaciones.

## 14.16. Evolution

En ejecución larga:

- no existe `selectBestWorm()` necesario para continuidad;
- linajes pueden extinguirse;
- linajes pueden expandirse;
- distribución de genes puede cambiar como consecuencia de reproducción diferencial.

## 14.17. Determinism

Misma seed/config/build:

- mismo estado a tick N;
- modo visual y headless generan el mismo core state a tick N.

---

# 15. Definition of Done — V1

C.E-PSVAML V1 se considera funcionalmente terminada cuando:

1. existe un mundo 2D continuo con alimento, química, temperatura, oxígeno y estímulos mecánicos;
2. existen varios worms simultáneamente;
3. cada worm posee un cuerpo segmentado con locomoción ondulatoria;
4. el cerebro solo conoce el mundo mediante sensores locales;
5. existe quimiotaxis funcional posible mediante señales temporales/locales;
6. existe termotaxis con memoria térmica básica;
7. existe mecanosensación y respuesta de retirada;
8. existe aerotaxis funcional;
9. existe pharyngeal pumping activo;
10. existe digestión con tránsito temporal;
11. existe metabolismo, energía y reservas;
12. existe defecation motor program simplificado;
13. existe habituación;
14. existe aprendizaje asociativo básico durante una vida;
15. existe memoria de comida / local vs distant search;
16. existe ciclo Egg -> L1 -> L2 -> L3 -> L4 -> Adult;
17. cada molt contiene lethargus;
18. existe ruta L2d -> Dauer bajo condiciones apropiadas;
19. existe recovery de Dauer;
20. adulto hermafrodita puede autofertilizarse;
21. existen oocitos/fertilización/uterine holding/egg laying de forma abstraída;
22. los huevos existen físicamente en el mundo;
23. huevos viables eclosionan;
24. existe herencia genética con mutación;
25. el estado aprendido no se hereda automáticamente;
26. existen linajes y generaciones solapadas;
27. la evolución ocurre por reproducción diferencial, no por score obligatorio;
28. existen envejecimiento y causas de muerte;
29. existe modo raylib 2D;
30. existe modo headless acelerado;
31. ambos modos usan exactamente el mismo simulation core;
32. una seed permite reproducir ejecuciones para debugging;
33. los escenarios aislados anteriores pasan de forma consistente;
34. el código puede entenderse siguiendo las clases y el orden de tick sin arquitectura genérica adicional.

---

# 16. Decisiones antiguas descartadas o corregidas

Esta sección preserva la intención histórica y evita reintroducir errores durante implementación.

| Diseño antiguo | Decisión V1 |
|---|---|
| `Worm` controla evolución/nueva generación | Eliminado. Evolución emerge en `Population`; Worm solo vive/reproduce/muere. |
| Norte/Sur/Este/Oeste como outputs | Eliminado. Outputs son actividad motora relativa al cuerpo. |
| `Muscle_Left/Muscle_Right` tipo tanque | Sustituido por drive corporal dorsal/ventral abstraído mediante CPG + curvature bias. |
| Fricción anisotrópica explicada por “micro-pelos” | Se permite drag anisotrópico efectivo, pero documentado como abstracción del medio. |
| Tierra granular / cabeza se pega y arrastra cuerpo | Eliminado. Cuerpo segmentado + onda neuromuscular + resistencia. |
| Bacterias como NPC random walk | Sustituido por food density field. |
| Mundo infinito procedural por chunks | Eliminado en V1. Arena finita continua. |
| Sol, lluvia, noche | Eliminados. Solo variables ambientales relevantes. |
| Depredador permanente persiguiendo al worm | Eliminado. Mechanical stimuli/hazards de escenario. |
| 20 golpes exactos = habituación | Eliminado. Adaptación continua dependiente de repetición/consecuencia. |
| Reward externo por comida | Eliminado como necesidad fisiológica. Comer tiene consecuencias energéticas reales. |
| `Fitness = tiempo + huevos + hijos` como selector | Eliminado del core. Puede registrarse como métrica analítica. |
| Al morir, elegir mejor hijo y continuar solo con él | Eliminado. Población continua y múltiples linajes. |
| Dauer como botón defensivo ante depredadores | Eliminado. Es ruta de desarrollo inducida por ambiente. |
| `dauerCooldown` | Eliminado; resolvía un exploit de una mecánica que ya no existe. |
| L1.5/L2.5/L3.5 | Eliminados. `stageProgress` continuo dentro de stages reales. |
| L4 = adulto | Corregido. Adult ocurre después de molt L4. |
| `maxLifespan` mata al llegar a tick exacto | Sustituido por age/stress mortality hazard. |
| HP único | Sustituido por daño/estrés causal; health visual puede ser derivado. |
| Obeso -> hijo Tank / flaco -> Speedster | Eliminado. Genotipo, maternal provisioning y fenotipo están separados. |
| Embrión fertilizado drena directamente porcentaje de cada comida | Sustituido por reproductive allocation y maternal provisioning durante oocyte/egg production. |
| `eggProductionProgress` único | Sustituido por oocyte maturation + sperm reserve + uterine eggs. |
| Aprendizaje asociativo = RL externo | Sustituido por plasticidad interna basada en consecuencias fisiológicas. |
| Feed-forward network sin memoria | Sustituida por CTRNN recurrente pequeña. |
| Simular futuro de hijos es “computacionalmente imposible” | Corregido. Headless fixed-tick permite múltiples vidas; no es necesario para selection base. |
| Acelerar simulación aumentando `dt` | Eliminado. Se ejecutan más fixed ticks por frame. |

---

# 17. Qué se difiere después de V1

Estas funciones no son necesarias para validar el objetivo actual y su omisión es intencional:

- conectoma completo de ~302 neuronas;
- neuronas nombradas una a una y sinapsis reales completas;
- gap junctions detalladas;
- canales iónicos específicos;
- señalización molecular de dauer (DAF/TGF-beta/insulin/steroid pathways) detallada;
- anatomía celular de la gónada;
- meiosis/recombinación diploide real;
- machos y mating;
- sexual selection;
- full cell lineage;
- immune system;
- microbioma complejo;
- excretory/osmoregulatory system detallado;
- CO2 sensing detallado;
- phototaxis/UV avoidance detallada;
- simulación de cutícula molecular;
- física granular de suelo;
- 3D;
- OpenGL custom renderer;
- clima;
- depredadores ecológicamente realistas;
- enfermedades y patógenos;
- simulación de bacterias individuales;
- interacción con hardware/robotics.

Estos elementos solo se añadirán si una pregunta experimental futura justifica el coste.

---

# 18. Estructura de archivos propuesta

```text
C.E-PSVAML/
├── C.E-PSVAML-V1-SPEC.md
└── src/                       # creado durante implementación
    ├── main.cpp
    ├── simulation/
    │   ├── Simulation.h
    │   ├── Simulation.cpp
    │   ├── SimulationConfig.h
    │   ├── Population.h
    │   ├── Population.cpp
    │   ├── MetricsRecorder.h
    │   └── MetricsRecorder.cpp
    ├── world/
    │   ├── World.h
    │   ├── World.cpp
    │   ├── FoodField.h
    │   ├── FoodField.cpp
    │   ├── ChemicalFields.h
    │   ├── ChemicalFields.cpp
    │   ├── TemperatureField.h
    │   ├── OxygenField.h
    │   └── MechanicalEnvironment.h
    ├── worm/
    │   ├── Worm.h
    │   ├── Worm.cpp
    │   ├── Genome.h
    │   ├── Body.h
    │   ├── Body.cpp
    │   ├── Physiology.h
    │   ├── Physiology.cpp
    │   ├── SensorySystem.h
    │   ├── SensorySystem.cpp
    │   ├── NervousSystem.h
    │   ├── NervousSystem.cpp
    │   ├── LearningSystem.h
    │   ├── LearningSystem.cpp
    │   ├── DevelopmentSystem.h
    │   ├── DevelopmentSystem.cpp
    │   ├── ReproductiveSystem.h
    │   ├── ReproductiveSystem.cpp
    │   └── Egg.h
    ├── render/
    │   ├── Renderer.h
    │   └── Renderer.cpp
    └── tests/
        ├── TestMain.cpp
        ├── PhysicsTests.cpp
        ├── PhysiologyTests.cpp
        ├── BehaviorTests.cpp
        ├── DevelopmentTests.cpp
        └── ReproductionTests.cpp
```

La estructura puede reducirse durante implementación si algunos archivos resultan triviales. No se crearán archivos vacíos solamente para respetar el árbol.

---

# 19. Referencias biológicas utilizadas para corregir el diseño original

Estas fuentes se utilizan como referencia de comportamiento y ciclo de vida; V1 sigue siendo una abstracción computacional y no una reproducción literal de todos sus mecanismos.

1. **WormAtlas — Introduction to C. elegans Anatomy**  
   https://wormatlas.org/hermaphrodite/introduction/mainframe.htm

2. **WormAtlas — Hermaphrodite Handbook / Reproductive System**  
   https://wormatlas.org/hermaphrodite/hermaphroditehomepage.htm

3. **NCBI Bookshelf / WormBook — Chemosensation in C. elegans**  
   https://www.ncbi.nlm.nih.gov/books/NBK19746/

4. **NCBI Bookshelf — The Behavioral Mechanism of Chemotaxis and Thermotaxis**  
   https://www.ncbi.nlm.nih.gov/books/NBK20016/

5. **NCBI Bookshelf / WormBook — Thermotaxis navigation behavior**  
   https://www.ncbi.nlm.nih.gov/books/NBK426003/

6. **NCBI Bookshelf / WormBook — C. elegans feeding**  
   https://www.ncbi.nlm.nih.gov/books/NBK116080/

7. **NCBI Bookshelf — Defecation Motor Program**  
   https://www.ncbi.nlm.nih.gov/books/NBK20047/

8. **NCBI Bookshelf — Mechanotransduction in C. elegans**  
   https://www.ncbi.nlm.nih.gov/books/NBK7498/

9. **NCBI Bookshelf / WormBook — Working with dauer larvae**  
   https://www.ncbi.nlm.nih.gov/books/NBK535516/

10. **NCBI Bookshelf — Genetic and Environmental Regulation of Dauer Larva Development**  
    https://www.ncbi.nlm.nih.gov/books/NBK20057/

---

# 20. Resumen ejecutivo

C.E-PSVAML V1 será una simulación 2D en C++/raylib de una población de organismos inspirados funcionalmente en *C. elegans*.

Cada organismo tendrá:

```text
un cuerpo físico segmentado
+ fisiología
+ alimentación/digestión
+ sensores locales
+ sistema nervioso recurrente
+ memoria y plasticidad
+ desarrollo completo
+ lethargus/molting
+ dauer
+ reproducción autofértil
+ herencia y mutación
+ envejecimiento y muerte
```

El mundo tendrá:

```text
alimento
+ química
+ temperatura
+ oxígeno
+ señales de población
+ estímulos mecánicos
```

La población vivirá de forma continua:

```text
nacer
-> percibir
-> actuar
-> alimentarse
-> aprender
-> crecer
-> reproducirse
-> dejar descendencia
-> envejecer
-> morir
```

No existe un “best worm” central ni una función de reward obligatoria. El entorno y la reproducción generan las presiones selectivas.

El mismo core se ejecutará visualmente con raylib o acelerado sin render en modo headless.

La prioridad de V1 es que **todo el organismo exista de extremo a extremo**. La fidelidad microscópica y el pulido se añaden después únicamente cuando aporten valor experimental.
