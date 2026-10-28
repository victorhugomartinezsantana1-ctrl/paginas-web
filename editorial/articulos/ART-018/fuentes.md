# Fuentes — ART-018 Control PID

Consulta: 2026-10-27.

| # | Fuente | Organismo | URL | Respalda | Limitaciones |
|---|---|---|---|---|---|
| 1 | Proportional–integral–derivative controller | Wikipedia (enciclopedia colaborativa) | https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller | Forma paralela y estándar (Ti, Td); efecto de cada término; tabla de efectos de aumentar Kp, Ki, Kd; filtrado de la derivada; remedios ante un cambio brusco de consigna (rampa, derivada sobre la medida, ponderación de consigna); limitaciones (no linealidad, ruido, ganancias fijas) | Fuente secundaria; se leyeron 100.000 de 163.840 caracteres (falta la sección de implementación discreta). La página no usa «setpoint kick» |
| 2 | Ziegler–Nichols method | Wikipedia | https://en.wikipedia.org/wiki/Ziegler%E2%80%93Nichols_method | Procedimiento de lazo cerrado (Ku, Tu) y tabla de reglas (P, PI, PD, PID clásico); ganancias derivadas; «quarter wave decay», orientado al rechazo de perturbaciones, ganancia agresiva con sobreimpulso | No da un porcentaje de sobreimpulso ni trata procesos inestables |
| 3 | Integral windup | Wikipedia | https://en.wikipedia.org/wiki/Integral_windup | Definición, causa (saturación), remedios (inicializar, rampa, integración condicional, limitar el integral, cálculo inverso, integrador de Clegg, limitar la salida) | No usa los términos «clamping» ni «anti-windup» |
| 4 | Laboratorio propio (simulación) | Equipo editorial | `editorial/fuentes/lab_pid.md` | Todas las cifras: error estacionario, P/PI/PID, Ku y Tu medidos, reglas de Ziegler–Nichols aplicadas, efecto de cada ganancia, windup, ruido y derivada | Planta ficticia 1/(s+1)³ y paso de Euler de 2 ms: **no hay hardware**; no se muestra ningún dato de un motor real |

## Observaciones

- La fuente primaria sobre control (libros y notas de aplicación) no está disponible en abierto desde este equipo; se usaron páginas enciclopédicas y se declara que son fuentes secundarias. Un intento con la página de tutoriales de la Universidad de Michigan dio HTTP 403.
- Conocimiento general (señalado): implementación discreta, filtro de primer orden de la derivada, integración condicional como forma concreta de limitar el integral.
