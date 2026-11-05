# GRADIENT_ANALYSIS

Microfit150updates: auxiliar inicial batch=1.3827; evaluación final20programas CE=0.672118, accuracy=70.8333%. Puerta90%/CE<0.5 FALLA. Gradientes auxiliares finitos en23tensores. No se ejecutaron control/tratamiento600updates ni evaluación comparativa.

Normas completas por tensor: results/aux-gradients.json. La loss atraviesa estados reales sin detach; gradientes finitos no certifican actualización selectiva útil. No se completaron tests nuevos de causalidad/reset/resume del entrenador: esa compuerta permanece pendiente.
