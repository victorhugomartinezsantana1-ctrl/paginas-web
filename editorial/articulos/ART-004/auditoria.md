# Auditoría — ART-004 FreeRTOS en el ESP32

Fecha: 2026-10-27 · Palabras editoriales: 6.529 · Fuentes registradas: 8

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| IDF FreeRTOS basado en v10.5.1 con SMP; `CONFIG_FREERTOS_UNICORE`; pila en bytes; creación sin afinidad | freertos_idf | Verificado (primeros 100.000 caracteres) |
| Planificador por núcleo; ejemplo A/B/C; "Best Effort Round Robin" | freertos_idf | Verificado |
| Núcleo 0 hace todas las tareas del tick; desfase de ticks | freertos_idf | Verificado |
| `taskDISABLE_INTERRUPTS` solo afecta al núcleo actual; `vTaskSuspendAll` no es exclusión mutua; spinlocks `portMUX_TYPE` | freertos_idf | Verificado |
| `float` ancla la tarea al núcleo; `double` por software | freertos_idf | Verificado |
| Interrupción asignada en el núcleo que la solicita; `ESP_INTR_FLAG_IRAM/SHARED`; niveles 4–7 en ensamblador | intr_alloc | Verificado |
| TWDT e IWDT: qué vigilan, opciones Kconfig, comportamiento al vencer | wdts | Verificado (sin valores numéricos por defecto) |
| Estados de tarea; fixed priority preemptive + time slicing; idle prioridad 0; delay relativo vs absoluto | FreeRTOS Kernel Book cap. 4 | Verificado |
| Colas por copia, bloqueo, orden de desbloqueo, conjuntos, punteros | cap. 5 | Verificado |
| `FromISR`, `xHigherPriorityTaskWoken`, procesamiento diferido | cap. 7 | Verificado |
| Mutex, herencia de prioridad (no "arregla"), deadlock, recursivos, gatekeeper | cap. 8 | Verificado |
| Notificaciones: ventajas y límites | cap. 10 | Verificado (sin cifra de rendimiento) |

### Correcciones hechas durante la revisión

1. "El soporte de Arduino se apoya en ESP-IDF" y "`loop()` es una tarea": no contrastado → marcado como dato general (dos lugares).
2. No se afirma la frecuencia de tick por defecto (no figura en la fuente leída).
3. No se afirma que los manejadores en C estén limitados a niveles 1–3 (la fuente no lo dice de forma expresa).
4. No se cita ninguna cifra de mejora de velocidad de las notificaciones (el libro no la da).
5. Entidades dobles en bloques de código (`&lt;`, `&amp;`) detectadas al revisar el generador → constructor corregido y verificado.

### Conocimiento general (señalado)

Regla "menor periodo, mayor prioridad", `uxTaskGetStackHighWaterMark`, reparto típico de núcleos con WiFi.

### No ejecutado ni compilado

Todo el código en C es ilustrativo: no hay toolchain de ESP-IDF en el equipo de redacción. El artículo lo declara al inicio y en cada ejemplo.

## Auditoría editorial

- 17 secciones, 9 preguntas frecuentes, diagnóstico paso a paso, errores comunes.
- Enlaza con los artículos de ESP32 y de Rust frente a C++.

## Auditoría técnica (verificar.py local)

OK — sin errores; recuento publicado = aprobado; 8 referencias.
