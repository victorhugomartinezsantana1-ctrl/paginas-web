# Auditoría — ART-011 Python asyncio

Fecha: 2026-10-27 · Palabras editoriales: 6.049 · Fuentes registradas: 8 (7 páginas oficiales + laboratorio propio)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Definiciones (corrutina, objeto corrutina, awaitable), `asyncio.run()`, llamar a una corrutina no la planifica | asyncio-task | Verificado |
| Advertencia de referencias débiles de `create_task()` | asyncio-task | Verificado (parafraseado) |
| `TaskGroup` (3.11): espera, cancela al primer fallo, `ExceptionGroup`; `gather()` y `return_exceptions`; `timeout()` (3.11), `wait_for()` (desde 3.12 sobre `timeout()`); `to_thread()` (3.9) y nota del GIL; cancelación y `BaseException`; `sleep(0)`; `as_completed`, `shield` | asyncio-task | Verificado |
| Modo de depuración (4 formas), umbral de 100 ms, `call_soon_threadsafe`, `run_coroutine_threadsafe`, avisos de corrutina no esperada y excepción no recuperada, objetos no seguros entre hilos | asyncio-dev | Verificado |
| `run_in_executor`, `slow_callback_duration` = 0,1 s, `asyncio.EventLoop` (Proactor en Windows, 3.13), políticas obsoletas (3.16) | asyncio-eventloop | Verificado |
| Primitivas no seguras entre hilos, `Semaphore` por defecto 1, sin `timeout`; `Queue` (`maxsize`, `put`/`get`, `shutdown` 3.13) | asyncio-sync, asyncio-queue | Verificado |
| GIL, `multiprocessing`/`ProcessPoolExecutor`, hilos para E/S, compilaciones sin GIL (3.13) | threading | Verificado |
| Todas las medidas (1,03/0,21/0,21 s; 516/64 ms; 3 simultáneas y 0,44 s; esperas de `put` 0/0/0/110/110/111 ms; 0,64/0,67 s; `took 0.277 seconds`; caso de 20 descargas: 18/1/1, máx. 5, 0,83 s) | `lab_asyncio.md` | Ejecutadas y copiadas de la salida real |
| «Tiempo secuencial estimado 3,30 s» | Suma de esperas programadas (2,75 + 0,5 + 0,05) | Es un cálculo, declarado como no medido |

### Correcciones hechas durante la revisión

1. La cita literal larga de la advertencia de `create_task()` se sustituyó por una paráfrasis (límite de citas textuales).
2. La explicación de por qué la medida de depuración (0,277 s) supera el bloqueo (0,25 s) se hizo exacta: el paso de la tarea incluía la recolección forzada y el primer aviso antes del primer `await` que cede.
3. Se marcó como dato general la sintaxis `except*` y la restricción de `asyncio.run()` dentro de un bucle en marcha.
4. La recomendación de no tocar políticas se declaró como opinión propia.
5. Se evitó afirmar el `max_workers` por defecto del ejecutor y el comportamiento de `-X dev` (las páginas no lo dicen).

### No ejecutado

No se reprodujo el fallo de la tarea recogida por el recolector de basura (no es provocable de forma fiable); se cita la documentación. No se midió ninguna conexión de red real ni el comportamiento sin GIL. Las medidas son de una ejecución y de este equipo.

## Auditoría editorial

- 17 secciones, 7 errores frecuentes, 7 preguntas frecuentes, caso completo ejecutado.
- Enlaza con pathlib, observabilidad y TCP.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
