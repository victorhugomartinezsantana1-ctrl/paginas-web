# Auditoría — ART-016 SQLite: WAL, límites y casos de uso

Fecha: 2026-10-27 · Palabras editoriales: ver `manifiesto.json` (≈ 5.700) · Fuentes registradas: 6 (5 páginas de SQLite + laboratorio propio)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| WAL: funcionamiento, lectores/escritor, un solo escritor, puntos de control (PASSIVE/FULL/RESTART; 1.000 páginas), índice del WAL, inanición, ventajas y desventajas, activación y persistencia, solo lectura, rendimiento, archivos grandes, versión 3.7.0 | wal.html | Verificado |
| Límites por defecto y máximos; tamaño máximo (~17,5 TB / ~281 TB); filas 2⁶⁴ y 2×10¹³ | limits.html | Verificado |
| Usos adecuados, ≈ 100.000 visitas/día (estimación conservadora, ~10× manejado), cuándo es mejor cliente/servidor, un solo escritor y lectores ilimitados, lista de cuatro preguntas | whentouse.html | Verificado |
| `journal_mode` (modos y valor por defecto), `synchronous` (FULL por defecto; semántica de NORMAL en WAL), `busy_timeout` (máximo 2.147.483.647 ms), `wal_autocheckpoint`, `wal_checkpoint` (modos y fila de tres enteros), `foreign_keys` (desactivado; sin efecto en transacción), `journal_size_limit` | pragma.html (100.000 de 100.251 caracteres) | Verificado |
| DEFERRED/IMMEDIATE/EXCLUSIVE; `SQLITE_BUSY`; instantánea del lector; actualización de lectura a escritura; «IMMEDIATE y EXCLUSIVE son iguales en WAL» | lang_transaction.html | Verificado |
| Medidas: valores por defecto; archivos `-wal`/`-shm`; COMMIT fallido en `delete` y correcto en `wal`; 3,06/0,32/0,03 ms; 0,08 s = 0,08 s; WAL 3,93 MiB y 4,48 MiB; (0,287,3) y (1,287,3); 44/18/28 frente a 10.144/0/0; límites de la compilación; claves foráneas | `lab_wal.md` | Ejecutadas y copiadas de la salida real |
| Aritmética: 1.000 × 4.096 B = 3,91 MiB (+ 24 B por marco = 3,93 MiB); 1.139 marcos ≈ 4,48 MiB; 4.294.967.294 × 4.096 = 17.592.186.036.224 B = 16 TiB = 17,59 TB; × 65.536 = 281,5 TB; 3,06/0,32 ≈ 10×; 3,06/0,03 ≈ 100× | Cálculo propio | Recalculada |

### Correcciones hechas durante la revisión

1. Se retiró la afirmación sin respaldo «la base de datos más desplegada del mundo» de la introducción (no figura en las páginas consultadas) y se sustituyó por una formulación declarada como no verificada.
2. El experimento de límites se corrigió tras un primer fallo del script (30.000 parámetros en la lista de columnas del `SELECT` chocaba con el límite de 2.000 columnas): ahora los parámetros van en un `IN (...)`, y el choque con el límite de columnas se muestra como un resultado aparte.
3. Se descubrió con el laboratorio que `PRAGMA foreign_keys = ON` no tenía efecto porque el módulo de Python había abierto una transacción implícita; se rehízo el experimento mostrando el antes y el después de `commit()` y se citó la regla de la documentación («sin efecto dentro de una transacción»).
4. Se declararon como inferencia o dato general: copiar el archivo de una base de datos en WAL sin sus archivos auxiliares, el tamaño de 24 bytes de la cabecera de cada marco, la comprobación de hilo del módulo de Python y la valoración de qué límite se alcanza antes en la práctica.
5. Se interpretó con cautela el experimento de hilos (no determinista): solo se afirma el contraste cualitativo y se advierte de que el número de lecturas de WAL no es un caudal comparable.

### No ejecutado

No se midió el coste del 1–2 % de lectura que cita la documentación, ni copias de seguridad, ni el comportamiento sobre un sistema de archivos de red, ni el modo `locking_mode=EXCLUSIVE`, ni la combinación con `asyncio`. Las medidas son de una ejecución en Windows 11 con un disco local y varían entre equipos (en particular las de sincronización a disco).

## Auditoría editorial

- 13 secciones, 7 errores frecuentes, 7 preguntas frecuentes, tabla de límites y lista de comprobación.
- Enlaza con índices en bases de datos, PostgreSQL y asyncio.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
