# Auditoría — ART-018 Control PID

Fecha: 2026-10-27 · Palabras editoriales: ver `manifiesto.json` (≈ 5.150) · Fuentes: 3 páginas enciclopédicas (secundarias) + simulación propia

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Formas paralela y estándar, efecto de cada término, tabla de efectos, filtrado de la derivada, remedios ante cambios bruscos de consigna, limitaciones | Wikipedia, PID (100.000 de 163.840 caracteres) | Verificado; fuente secundaria declarada |
| Procedimiento y tabla de Ziegler–Nichols, ganancias derivadas, «quarter wave decay», agresividad | Wikipedia, Ziegler–Nichols | Verificado; la página no da un porcentaje de sobreimpulso y el texto no lo atribuye |
| Windup: definición, causa y lista de remedios | Wikipedia, Integral windup | Verificado; la página no usa «clamping» ni «anti-windup» y el texto tampoco los atribuye |
| Todas las cifras (error estacionario, P/PI/PID, Ku y Tu, ZN, efecto de ganancias, windup, ruido/derivada, robustez, retardo, ajuste manual) | `lab_pid.md` (Python 3.14.2) | Ejecutadas; el caso del paso 5 se contrastó con un port a C++ (g++ 16.1.0) con resultado idéntico |
| Aritmética: Kp/(1+Kp); Ku=8 y Tu=2π/√3 de la planta 1/(s+1)³; 7,079/0,020 ≈ 354; 7,079/0,215 ≈ 33; Kd/dt = 500 | Cálculo propio | Recalculada |

### Correcciones hechas durante la revisión

1. El primer script ocultaba el «golpe» de la derivada (inicializaba el estado con el primer error); se corrigió y se midió el pico real (495,5 / 21,0 / 2,7). Durante la corrección se introdujo y se retiró un fallo propio (estado de la derivada), y se repitió toda la simulación.
2. Se contrastó la tabla de efectos de las ganancias con la simulación y se declararon explícitamente tres casillas que no se cumplen en este caso.
3. Un intento de usar la página de tutoriales de la Universidad de Michigan dio HTTP 403; se usaron fuentes secundarias y se declaró en el texto.
4. El borrador quedó en 3.745 palabras; se amplió con experimentos reales (ajuste manual, robustez, retardo, comprobación en C++) y no con relleno.
5. Se corrigió un error de redacción («u mal») y una frase sobre «dos filas» de solo P (hay una).

### No ejecutado

No hay hardware: nada se probó en un motor, horno ni microcontrolador. Planta ficticia, Euler de 2 ms. No se trataron aritmética de coma fija, otros métodos de ajuste ni controladores en cascada.

## Auditoría editorial

- 15 secciones, 6 errores frecuentes, 6 preguntas frecuentes, tabla comparativa de sintonías, lista de comprobación.
- Enlaza con control de motores ESP32, FreeRTOS y Rust frente a C++.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
