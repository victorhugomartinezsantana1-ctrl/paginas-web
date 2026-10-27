# Auditoría — ART-012 Memoria en Python

Fecha: 2026-10-27 · Palabras editoriales: ver `manifiesto.json` (≈ 5.700) · Fuentes registradas: 8 (7 páginas oficiales + laboratorio propio)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Montón privado, `pymalloc` (≤ 512 bytes, arenas de 1 MiB en 64 bits), mimalloc en compilaciones sin GIL | Memory Management (C API) | Verificado |
| Conteo de referencias de CPython y detección diferida de ciclos; `__del__` (no garantizado al salir, excepciones ignoradas, `del x` solo decrementa); `weakref.finalize`; no depender de la finalización inmediata | Data model | Verificado |
| `getrefcount` (+1 temporal), objetos inmortales (3.12), `_is_immortal()` (3.14), `getsizeof` (solo el objeto + sobrecarga del recolector), `intern` | sys | Verificado (primeros 100.000 de 107.586 caracteres) |
| `gc`: tres generaciones, umbrales, `collect()` y su valor de retorno, `threshold2` ignorado en 3.14 y restaurado en 3.14.5, `freeze`, `DEBUG_SAVEALL`, `garbage`, `callbacks`, PEP 442 | gc | Verificado |
| `tracemalloc`: `start(nframe)`, snapshots sin bloques previos, `statistics`, `compare_to`, `get_traced_memory`, `reset_peak` (3.9), dominio 0, coste de rastrear | tracemalloc | Verificado |
| `__slots__`: sin `__dict__`/`__weakref__`, ahorro de espacio y velocidad de búsqueda (sin medir la velocidad), restricciones de herencia y de valores por defecto | Data model (3.3.2.4) | Verificado |
| `weakref`, `WeakValueDictionary`, objetos admitidos, `finalize`; `lru_cache` (128), `cache`, `cache_info`, referencias retenidas, `self` en la clave de métodos | weakref, functools | Verificado |
| Medidas: refcount 2/3/5/2, inmortales 3.221.225.472, ciclo + `gc.collect()` = 2, umbrales `(2000, 10, 0)`, tamaños de la tabla, 184 B frente a 80.560 B, crecimiento 88/120/184/248/312/376, 104 → 64 bytes/objeto (y 168 tras tocar `__dict__`), 38,6 MiB frente a 3,7 KiB, línea 182 con +50.000 bloques, dict 17.909 KiB frente a `lru_cache` 120 KiB, 5 → 2 entradas débiles | `lab_memoria.md` | Ejecutadas y copiadas de la salida real |
| Aritmética derivada: 3 × 2³⁰ = 3.221.225.472; 104/64 = −38 %; 17.909/120 ≈ 149 veces; 917 B/entrada | Cálculo propio | Recalculada |

### Correcciones hechas durante la revisión

1. La explicación de los 184 bytes de la lista exterior decía «10 punteros más cierto margen»; se corrigió a «16 huecos» (capacidad real tras crecer por `append`, coherente con la tabla de crecimiento).
2. La frase sobre `weakref.finalize` como forma «fiable» de limpieza se rebajó a la alternativa que propone la documentación.
3. Se añadió una sección de cachés y referencias débiles porque el primer borrador quedaba en 4.902 palabras (< 5.000); la sección se apoya en documentación (weakref, functools) y en un experimento nuevo.
4. La explicación de por qué `getsizeof(obj) + getsizeof(obj.__dict__)` (144) supera la medida real (104) se marcó como inferencia propia, apoyada en el experimento de 104 → 168 bytes tras acceder a `__dict__`.
5. La memoria devuelta (o no) al sistema operativo se declaró como no medida.

### No ejecutado

No se midió ninguna compilación sin GIL, ni la velocidad de acceso con `__slots__`, ni el efecto de `lru_cache` sobre métodos, ni el comportamiento de numpy con `tracemalloc`. Las medidas son de una ejecución en este equipo.

## Auditoría editorial

- 14 secciones, método de investigación en 6 pasos, 7 errores frecuentes, 7 preguntas frecuentes.
- Enlaza con asyncio, métodos numéricos y observabilidad.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
