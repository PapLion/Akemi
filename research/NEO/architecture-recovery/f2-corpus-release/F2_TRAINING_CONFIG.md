# Configuración preparada, deshabilitada

F2_TRAINING_CONFIG.json mantiene F2=2.082.176 y baseline=2.032.768, contexto128, batch2, CPU FP32, semilla17, AdamW LR0,003 betas0,9/0,95 decay0,01 clip1. Hielo/TraposOFF. training_authorized=false, ready=false. No se genera un comando que entrene 5M repitiendo los 25.355 aprobados.

Evaluación: reutilizar protocolo anterior NLL/PPL por idioma y dominio, curvas por targets vistos, prompts fijos y repetición, comparación baseline. El dev candidato ES107.333/EN104.772 targets sirve para planificar, pero no puede usarse como aprobado hasta resolver derechos. El dev aprobado contiene dos archivos de código EN, insuficiente para conclusiones bilingües o prosa general. Frecuencia y coste total de evaluación aún pendientes de release aprobado. No seleccionar checkpoints por ejemplos anecdóticos.
