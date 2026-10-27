# Laboratorio — ART-011 asyncio

Fecha de ejecución: 2026-10-27. Equipo: Windows 11 (win32), Python 3.14.2 de 64 bits (compilación estándar, con GIL). Los scripts se ejecutaron con python -I -X utf8. Las rutas locales se sustituyeron por marcadores (`<PYTHON>`, `<LAB>`) para no publicar rutas del equipo. Los tiempos varían entre ejecuciones y equipos: son medidas de una ejecución, no valores garantizados.

## Fuente: lab_asyncio.py

```python
import asyncio
import logging
import sys
import time
import warnings


def titulo(t):
    print(f"\n=== {t} ===")


async def espera(n, d=0.2):
    await asyncio.sleep(d)
    return n


async def exp1():
    titulo("1. Secuencial frente a concurrente (5 esperas de 0,2 s)")
    t0 = time.perf_counter()
    for i in range(5):
        await espera(i)
    print(f"secuencial: {time.perf_counter() - t0:.2f} s")
    t0 = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for i in range(5):
            tg.create_task(espera(i))
    print(f"TaskGroup : {time.perf_counter() - t0:.2f} s")
    t0 = time.perf_counter()
    await asyncio.gather(*(espera(i) for i in range(5)))
    print(f"gather    : {time.perf_counter() - t0:.2f} s")


async def latido(marcas, parar):
    while not parar.is_set():
        marcas.append(time.perf_counter())
        await asyncio.sleep(0.05)


async def exp2():
    titulo("2. Una llamada bloqueante frena a todo el bucle (latido cada 0,05 s)")
    for nombre, trabajo in (
        ("time.sleep(0.5) dentro de la corrutina", lambda: asyncio.sleep(0, result=time.sleep(0.5))),
        ("await asyncio.to_thread(time.sleep, 0.5)", lambda: asyncio.to_thread(time.sleep, 0.5)),
    ):
        marcas, parar = [], asyncio.Event()
        h = asyncio.create_task(latido(marcas, parar))
        await asyncio.sleep(0.2)
        await trabajo()
        await asyncio.sleep(0.2)
        parar.set()
        await h
        huecos = [b - a for a, b in zip(marcas, marcas[1:])]
        print(f"{nombre}: latidos={len(marcas)}, hueco máximo={max(huecos) * 1000:.0f} ms")


async def falla():
    await asyncio.sleep(0.05)
    raise ValueError("fallo en la tarea B")


async def larga(nombre, estado):
    try:
        await asyncio.sleep(1)
        estado[nombre] = "terminó"
    except asyncio.CancelledError:
        estado[nombre] = "cancelada"
        raise


async def exp3():
    titulo("3. Un fallo: TaskGroup frente a gather")
    estado = {}
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(larga("A", estado))
            tg.create_task(falla())
            tg.create_task(larga("C", estado))
    except* ValueError as eg:
        print("TaskGroup: ExceptionGroup con", [repr(e) for e in eg.exceptions])
    print("TaskGroup: estado de las demás ->", estado)

    estado = {}
    t_a = asyncio.create_task(larga("A", estado))
    t_c = asyncio.create_task(larga("C", estado))
    try:
        await asyncio.gather(t_a, falla(), t_c)
    except ValueError as e:
        print("gather: propaga", repr(e), "inmediatamente")
    print("gather: justo después del fallo ->", {"A": t_a.done(), "C": t_c.done()})
    await asyncio.sleep(1.1)
    print("gather: pasado 1,1 s ->", estado)


async def exp4():
    titulo("4. Tiempos límite y cancelación")
    try:
        async with asyncio.timeout(0.1):
            await asyncio.sleep(1)
    except TimeoutError:
        print("asyncio.timeout(0.1): TimeoutError capturada fuera del bloque")
    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=0.1)
    except TimeoutError:
        print("wait_for(timeout=0.1): TimeoutError")
    t = asyncio.create_task(asyncio.sleep(1))
    await asyncio.sleep(0)
    print("cancel() devuelve:", t.cancel())
    try:
        await t
    except asyncio.CancelledError:
        print("await de la tarea cancelada: CancelledError; cancelled() =", t.cancelled())
    print("¿CancelledError es subclase de Exception?", issubclass(asyncio.CancelledError, Exception))
    print("¿CancelledError es subclase de BaseException?", issubclass(asyncio.CancelledError, BaseException))


async def exp5():
    titulo("5. Semáforo: 10 tareas de 0,1 s con Semaphore(3)")
    sem = asyncio.Semaphore(3)
    activas = 0
    maximo = 0

    async def trabajo(i):
        nonlocal activas, maximo
        async with sem:
            activas += 1
            maximo = max(maximo, activas)
            await asyncio.sleep(0.1)
            activas -= 1

    t0 = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for i in range(10):
            tg.create_task(trabajo(i))
    print(f"máximo simultáneo observado={maximo}, tiempo total={time.perf_counter() - t0:.2f} s")


async def exp6():
    titulo("6. Cola con maxsize=2 (contrapresión)")
    cola = asyncio.Queue(maxsize=2)
    registro = []

    async def productor():
        for i in range(6):
            t = time.perf_counter()
            await cola.put(i)
            registro.append((i, time.perf_counter() - t))
        await cola.put(None)

    async def consumidor():
        while (x := await cola.get()) is not None:
            await asyncio.sleep(0.1)
            cola.task_done()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(productor())
        tg.create_task(consumidor())
    for i, espera_put in registro:
        print(f"put({i}) esperó {espera_put * 1000:.0f} ms")


def cpu():
    s = 0
    for i in range(6_000_000):
        s += i * i
    return s


async def exp7():
    titulo("7. Trabajo de CPU: secuencial frente a dos hilos con to_thread")
    print("GIL activado:", sys._is_gil_enabled())
    t0 = time.perf_counter()
    cpu()
    cpu()
    print(f"2 llamadas secuenciales : {time.perf_counter() - t0:.2f} s")
    t0 = time.perf_counter()
    await asyncio.gather(asyncio.to_thread(cpu), asyncio.to_thread(cpu))
    print(f"2 llamadas con to_thread: {time.perf_counter() - t0:.2f} s")


async def sin_esperar():
    return 1


async def exp8():
    titulo("8. Depuración: corrutina sin esperar y callback lento")
    loop = asyncio.get_running_loop()
    print("tipo de bucle:", type(loop).__name__, "| slow_callback_duration =", loop.slow_callback_duration)
    print("depuración activada:", loop.get_debug())


def main():
    print("Python", sys.version.split()[0], "en", sys.platform)
    asyncio.run(exp1())
    asyncio.run(exp2())
    asyncio.run(exp3())
    asyncio.run(exp4())
    asyncio.run(exp5())
    asyncio.run(exp6())
    asyncio.run(exp7())
    asyncio.run(exp8())


if __name__ == "__main__":
    main()
```

## Salida de lab_asyncio.py

```text
Python 3.14.2 en win32

=== 1. Secuencial frente a concurrente (5 esperas de 0,2 s) ===
secuencial: 1.03 s
TaskGroup : 0.21 s
gather    : 0.21 s

=== 2. Una llamada bloqueante frena a todo el bucle (latido cada 0,05 s) ===
time.sleep(0.5) dentro de la corrutina: latidos=8, hueco máximo=516 ms
await asyncio.to_thread(time.sleep, 0.5): latidos=15, hueco máximo=64 ms

=== 3. Un fallo: TaskGroup frente a gather ===
TaskGroup: ExceptionGroup con ["ValueError('fallo en la tarea B')"]
TaskGroup: estado de las demás -> {'C': 'cancelada', 'A': 'cancelada'}
gather: propaga ValueError('fallo en la tarea B') inmediatamente
gather: justo después del fallo -> {'A': False, 'C': False}
gather: pasado 1,1 s -> {'A': 'terminó', 'C': 'terminó'}

=== 4. Tiempos límite y cancelación ===
asyncio.timeout(0.1): TimeoutError capturada fuera del bloque
wait_for(timeout=0.1): TimeoutError
cancel() devuelve: True
await de la tarea cancelada: CancelledError; cancelled() = True
¿CancelledError es subclase de Exception? False
¿CancelledError es subclase de BaseException? True

=== 5. Semáforo: 10 tareas de 0,1 s con Semaphore(3) ===
máximo simultáneo observado=3, tiempo total=0.44 s

=== 6. Cola con maxsize=2 (contrapresión) ===
put(0) esperó 0 ms
put(1) esperó 0 ms
put(2) esperó 0 ms
put(3) esperó 110 ms
put(4) esperó 110 ms
put(5) esperó 111 ms

=== 7. Trabajo de CPU: secuencial frente a dos hilos con to_thread ===
GIL activado: True
2 llamadas secuenciales : 0.64 s
2 llamadas con to_thread: 0.67 s

=== 8. Depuración: corrutina sin esperar y callback lento ===
tipo de bucle: ProactorEventLoop | slow_callback_duration = 0.1
depuración activada: False
```

## Fuente: lab_asyncio_debug.py

```python
import asyncio
import gc
import sys
import time


async def sin_esperar():
    return 1


async def bloquea():
    time.sleep(0.25)


async def explota():
    raise RuntimeError("nadie recoge esta excepcion")


async def main():
    loop = asyncio.get_running_loop()
    print("depuracion activada:", loop.get_debug())
    sin_esperar()  # corrutina que nunca se espera
    gc.collect()
    await bloquea()  # callback lento: supera slow_callback_duration (0,1 s)
    t = asyncio.create_task(explota())
    await asyncio.sleep(0.05)
    del t
    gc.collect()
    await asyncio.sleep(0.05)
    print("fin de main")


if __name__ == "__main__":
    print("Python", sys.version.split()[0])
    asyncio.run(main(), debug=True)
```

## Salida de lab_asyncio_debug.py

```text
<LAB>\lab_asyncio_debug.py:22: RuntimeWarning: coroutine 'sin_esperar' was never awaited
Coroutine created at (most recent call last)
  File "<LAB>\lab_asyncio_debug.py", line 35, in <module>
    asyncio.run(main(), debug=True)
  File "<PYTHON>\Lib\asyncio\runners.py", line 204, in run
    return runner.run(main)
  File "<PYTHON>\Lib\asyncio\runners.py", line 127, in run
    return self._loop.run_until_complete(task)
  File "<PYTHON>\Lib\asyncio\base_events.py", line 706, in run_until_complete
    self.run_forever()
  File "<PYTHON>\Lib\asyncio\base_events.py", line 677, in run_forever
    self._run_once()
  File "<PYTHON>\Lib\asyncio\base_events.py", line 2038, in _run_once
    handle._run()
  File "<PYTHON>\Lib\asyncio\events.py", line 94, in _run
    self._context.run(self._callback, *self._args)
  File "<LAB>\lab_asyncio_debug.py", line 22, in main
    sin_esperar()  # corrutina que nunca se espera
  sin_esperar()  # corrutina que nunca se espera
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Executing <Task pending name='Task-1' coro=<main() running at <LAB>\lab_asyncio_debug.py:26> wait_for=<Future pending cb=[Task.task_wakeup()] created at <PYTHON>\Lib\asyncio\base_events.py:459> cb=[_run_until_complete_cb() at <PYTHON>\Lib\asyncio\base_events.py:181] created at <PYTHON>\Lib\asyncio\runners.py:109> took 0.277 seconds
Task exception was never retrieved
future: <Task finished name='Task-2' coro=<explota() done, defined at <LAB>\lab_asyncio_debug.py:15> exception=RuntimeError('nadie recoge esta excepcion') created at <PYTHON>\Lib\asyncio\tasks.py:395>
source_traceback: Object created at (most recent call last):
  File "<LAB>\lab_asyncio_debug.py", line 35, in <module>
    asyncio.run(main(), debug=True)
  File "<PYTHON>\Lib\asyncio\runners.py", line 204, in run
    return runner.run(main)
  File "<PYTHON>\Lib\asyncio\runners.py", line 127, in run
    return self._loop.run_until_complete(task)
  File "<PYTHON>\Lib\asyncio\base_events.py", line 706, in run_until_complete
    self.run_forever()
  File "<PYTHON>\Lib\asyncio\base_events.py", line 677, in run_forever
    self._run_once()
  File "<PYTHON>\Lib\asyncio\base_events.py", line 2038, in _run_once
    handle._run()
  File "<PYTHON>\Lib\asyncio\events.py", line 94, in _run
    self._context.run(self._callback, *self._args)
  File "<LAB>\lab_asyncio_debug.py", line 25, in main
    t = asyncio.create_task(explota())
  File "<PYTHON>\Lib\asyncio\tasks.py", line 395, in create_task
    return loop.create_task(coro, **kwargs)
Traceback (most recent call last):
  File "<LAB>\lab_asyncio_debug.py", line 16, in explota
    raise RuntimeError("nadie recoge esta excepcion")
RuntimeError: nadie recoge esta excepcion
Python 3.14.2
depuracion activada: True
fin de main
```

## Fuente: lab_asyncio_caso.py

```python
import asyncio
import time

# Simulación de 20 "descargas" sin red: cada una espera un tiempo fijo.
# La nº 7 tarda demasiado (supera el plazo) y la nº 11 falla.
CONCURRENCIA = 5
PLAZO = 0.5

activas = 0
maximo = 0


async def descargar(i):
    global activas, maximo
    activas += 1
    maximo = max(maximo, activas)
    try:
        if i == 7:
            await asyncio.sleep(2.0)
        elif i == 11:
            await asyncio.sleep(0.05)
            raise ConnectionError("conexión rechazada")
        else:
            await asyncio.sleep(0.05 + (i % 5) * 0.05)
        return f"contenido {i}"
    finally:
        activas -= 1


async def tarea(i, sem, resultados):
    async with sem:
        try:
            async with asyncio.timeout(PLAZO):
                resultados[i] = ("ok", await descargar(i))
        except TimeoutError:
            resultados[i] = ("plazo", None)
        except ConnectionError as e:
            resultados[i] = ("error", str(e))


async def main():
    sem = asyncio.Semaphore(CONCURRENCIA)
    resultados = {}
    t0 = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for i in range(20):
            tg.create_task(tarea(i, sem, resultados))
    total = time.perf_counter() - t0
    cuenta = {}
    for estado, _ in resultados.values():
        cuenta[estado] = cuenta.get(estado, 0) + 1
    print("resultados por estado:", dict(sorted(cuenta.items())))
    print("fallidas:", {i: r for i, r in sorted(resultados.items()) if r[0] != "ok"})
    print(f"máximo de descargas simultáneas: {maximo} (límite {CONCURRENCIA})")
    print(f"tiempo total: {total:.2f} s")
    suma_secuencial = sum(0.05 + (i % 5) * 0.05 for i in range(20) if i not in (7, 11)) + PLAZO + 0.05
    print(f"tiempo secuencial estimado (suma de esperas, con plazo de {PLAZO} s para la nº 7): {suma_secuencial:.2f} s")


asyncio.run(main())
```

## Salida de lab_asyncio_caso.py

```text
resultados por estado: {'error': 1, 'ok': 18, 'plazo': 1}
fallidas: {7: ('plazo', None), 11: ('error', 'conexión rechazada')}
máximo de descargas simultáneas: 5 (límite 5)
tiempo total: 0.83 s
tiempo secuencial estimado (suma de esperas, con plazo de 0.5 s para la nº 7): 3.30 s
```
