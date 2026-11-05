# Gradientes y su alcance

{
  "A": {
    "lm_norm": 1.0932166576385498,
    "initial_norm": 0.3550585210323334,
    "post_norm": 0.19422170519828796,
    "cosine_initial_post": 0.7114561796188354,
    "cosine_initial_lm": -0.09493999183177948,
    "scope": "fixed 16-program batch, model trainable params only; raw terms before .1 weighting/clipping"
  },
  "B": {
    "lm_norm": 1.2555962800979614,
    "initial_norm": 0.15209263563156128,
    "post_norm": 0.1870194375514984,
    "cosine_initial_post": 0.4322594404220581,
    "cosine_initial_lm": -0.026387128978967667,
    "scope": "fixed 16-program batch, model trainable params only; raw terms before .1 weighting/clipping"
  }
}

Coseno inicial/posterior positivo en ambos checkpoints sobre16programas fijos. No demuestra ausencia de interferencia en todos los batches ni durante toda la trayectoria; tampoco permite atribuir el fallo a gradientes opuestos. Norma de respuesta mayor que las auxiliares en ese batch, especialmente después de ponderar. Esto no prueba que respuesta sea la causa del fallo. No se varió lambda ni clipping. Normas durante los150updates guardadas por tensor; Trapos/escritura no se congelaron para mejorar resultados.
