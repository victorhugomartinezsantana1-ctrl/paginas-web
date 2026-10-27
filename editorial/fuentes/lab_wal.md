# Laboratorio — ART-016 SQLite: WAL, límites y casos de uso

Fecha de ejecución: 2026-10-27. Equipo: Windows 11, SQLite 3.50.4 (módulo sqlite3 de Python 3.14.2), archivos en un directorio temporal del disco local. El script se ejecutó con python -I -X utf8. Las rutas locales se sustituyeron por marcadores (`<PYTHON>`, `<LAB>`) para no publicar rutas del equipo. Los tiempos varían entre ejecuciones y equipos: son medidas de una ejecución, no valores garantizados.

## Fuente: lab_wal.py

```python
import os
import sqlite3
import sys
import tempfile
import threading
import time


def titulo(t):
    print(f"\n=== {t} ===")


def nueva_bd(modo, sync=None):
    d = tempfile.mkdtemp()
    ruta = os.path.join(d, "lab.db")
    con = sqlite3.connect(ruta, isolation_level=None, timeout=0)
    r = con.execute(f"PRAGMA journal_mode={modo}").fetchone()[0]
    if sync:
        con.execute(f"PRAGMA synchronous={sync}")
    con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    return ruta, con, r


def conectar(ruta):
    return sqlite3.connect(ruta, isolation_level=None, timeout=0)


def tam(ruta):
    return os.path.getsize(ruta) if os.path.exists(ruta) else 0


print("SQLite", sqlite3.sqlite_version, "| Python", sys.version.split()[0], "|", sys.platform)

# ------------------------------------------------------------- 1
titulo("1. Valores por defecto y archivos de WAL")
d = tempfile.mkdtemp()
ruta = os.path.join(d, "lab.db")
c = sqlite3.connect(ruta)
print("journal_mode por defecto :", c.execute("PRAGMA journal_mode").fetchone()[0])
print("synchronous por defecto  :", c.execute("PRAGMA synchronous").fetchone()[0], "(2 = FULL)")
print("busy_timeout (módulo sqlite3 de Python, timeout=5 s por defecto):", c.execute("PRAGMA busy_timeout").fetchone()[0], "ms")
print("foreign_keys por defecto :", c.execute("PRAGMA foreign_keys").fetchone()[0])
print("wal_autocheckpoint       :", c.execute("PRAGMA wal_autocheckpoint").fetchone()[0], "páginas")
c.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
c.commit()
print("archivos antes de WAL    :", sorted(os.listdir(d)))
print("PRAGMA journal_mode=WAL  ->", c.execute("PRAGMA journal_mode=WAL").fetchone()[0])
c.execute("INSERT INTO t(v) VALUES ('a')")
c.commit()
print("archivos tras escribir   :", sorted(os.listdir(d)))
c.close()
print("archivos tras cerrar la última conexión:", sorted(os.listdir(d)))
c2 = sqlite3.connect(ruta)
print("al reabrir, journal_mode :", c2.execute("PRAGMA journal_mode").fetchone()[0], "(persistente)")
print("synchronous al reabrir   :", c2.execute("PRAGMA synchronous").fetchone()[0], "(no persistente)")
c2.close()

# ------------------------------------------------------------- 2
titulo("2. Un lector con transacción abierta y un escritor que confirma")
for modo in ("delete", "wal"):
    ruta, w, m = nueva_bd(modo)
    for _ in range(10):
        w.execute("INSERT INTO t(v) VALUES ('x')")
    r = conectar(ruta)
    r.execute("BEGIN")
    n0 = r.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    w.execute("BEGIN IMMEDIATE")
    w.execute("INSERT INTO t(v) VALUES ('nuevo')")
    try:
        w.execute("COMMIT")
        res = "COMMIT correcto"
    except sqlite3.OperationalError as e:
        res = f"COMMIT falla: {e}"
        w.execute("ROLLBACK")
    n1 = r.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    r.execute("COMMIT")
    n2 = r.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    print(f"  modo {m:6s}: {res}")
    print(f"    el lector veía {n0} filas; sigue viendo {n1} dentro de su transacción; al terminarla ve {n2}")
    r.close()
    w.close()

# ------------------------------------------------------------- 3
titulo("3. Dos escritores a la vez")
for modo in ("delete", "wal"):
    ruta, a, m = nueva_bd(modo)
    b = conectar(ruta)
    a.execute("BEGIN IMMEDIATE")
    try:
        b.execute("BEGIN IMMEDIATE")
        res = "el segundo BEGIN IMMEDIATE se concede"
    except sqlite3.OperationalError as e:
        res = f"el segundo BEGIN IMMEDIATE falla: {e}"
    print(f"  modo {m:6s}: {res}")
    a.execute("ROLLBACK")
    a.close()
    b.close()

# ------------------------------------------------------------- 4
titulo("4. Coste de confirmar: 1.000 inserciones, cada una en su transacción")
for modo, sync in (("delete", "FULL"), ("wal", "FULL"), ("wal", "NORMAL")):
    ruta, w, m = nueva_bd(modo, sync)
    t0 = time.perf_counter()
    for i in range(1000):
        w.execute("INSERT INTO t(v) VALUES (?)", ("fila",))
    dt = time.perf_counter() - t0
    print(f"  journal_mode={m:6s} synchronous={sync:6s}: {dt:6.2f} s en total = {dt / 1000 * 1000:6.2f} ms por confirmación")
    w.close()

titulo("4b. Una sola transacción con 100.000 filas")
for modo in ("delete", "wal"):
    ruta, w, m = nueva_bd(modo, "FULL")
    t0 = time.perf_counter()
    w.execute("BEGIN")
    w.executemany("INSERT INTO t(v) VALUES (?)", (("fila",) for _ in range(100_000)))
    w.execute("COMMIT")
    print(f"  journal_mode={m:6s}: {time.perf_counter() - t0:.2f} s")
    w.close()

# ------------------------------------------------------------- 5
titulo("5. Tamaño del archivo WAL y puntos de control")
for etiqueta, auto in (("wal_autocheckpoint=1000 (por defecto)", 1000), ("wal_autocheckpoint=0 (desactivado)", 0)):
    ruta, w, m = nueva_bd("wal", "NORMAL")
    w.execute(f"PRAGMA wal_autocheckpoint={auto}")
    maximo = 0
    for _ in range(200):
        w.execute("BEGIN")
        w.executemany("INSERT INTO t(v) VALUES (?)", (("x" * 100,) for _ in range(100)))
        w.execute("COMMIT")
        maximo = max(maximo, tam(ruta + "-wal"))
    print(f"  {etiqueta}: WAL máximo = {maximo / 1024 / 1024:.2f} MiB, final = {tam(ruta + '-wal') / 1024 / 1024:.2f} MiB, base de datos = {tam(ruta) / 1024 / 1024:.2f} MiB")
    if auto == 0:
        print("    wal_checkpoint(PASSIVE) ->", w.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone(), "(ocupado, páginas en el WAL, páginas pasadas a la base de datos)")
        print("    wal_checkpoint(TRUNCATE) ->", w.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
        print(f"    WAL tras TRUNCATE = {tam(ruta + '-wal')} bytes")
    w.close()

titulo("5b. Un lector con una transacción abierta impide reiniciar el WAL")
ruta, w, m = nueva_bd("wal", "NORMAL")
w.execute("PRAGMA wal_autocheckpoint=0")
w.execute("INSERT INTO t(v) VALUES ('a')")
r = conectar(ruta)
r.execute("BEGIN")
r.execute("SELECT COUNT(*) FROM t").fetchone()
for _ in range(50):
    w.execute("BEGIN")
    w.executemany("INSERT INTO t(v) VALUES (?)", (("x" * 100,) for _ in range(100)))
    w.execute("COMMIT")
print("  con el lector abierto: wal_checkpoint(PASSIVE)  ->", w.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone())
print("  con el lector abierto: wal_checkpoint(TRUNCATE) ->", w.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
print(f"  tamaño del WAL = {tam(ruta + '-wal') / 1024 / 1024:.2f} MiB")
r.execute("COMMIT")
print("  al cerrar la transacción del lector: wal_checkpoint(TRUNCATE) ->", w.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
print(f"  tamaño del WAL = {tam(ruta + '-wal')} bytes")
r.close()
w.close()

# ------------------------------------------------------------- 6
titulo("6. Lectores y escritor a la vez, con 300 confirmaciones del escritor")
for modo in ("delete", "wal"):
    ruta, w, m = nueva_bd(modo, "FULL")
    for _ in range(100):
        w.execute("INSERT INTO t(v) VALUES ('x')")
    estado = {"ok": 0, "bloqueado": 0, "fin": False, "max_ms": 0.0}

    def lector():
        c = conectar(ruta)
        while not estado["fin"]:
            t0 = time.perf_counter()
            try:
                c.execute("SELECT COUNT(*) FROM t").fetchone()
                estado["ok"] += 1
            except sqlite3.OperationalError:
                estado["bloqueado"] += 1
            estado["max_ms"] = max(estado["max_ms"], (time.perf_counter() - t0) * 1000)
        c.close()

    hilo = threading.Thread(target=lector)
    hilo.start()
    fallos_escritor = 0
    for i in range(300):
        try:
            w.execute("INSERT INTO t(v) VALUES ('y')")
        except sqlite3.OperationalError:
            fallos_escritor += 1
    estado["fin"] = True
    hilo.join()
    print(f"  modo {m:6s}: lecturas correctas = {estado['ok']:6d}, lecturas con 'database is locked' = {estado['bloqueado']:5d}, escrituras fallidas = {fallos_escritor}")
    w.close()

# ------------------------------------------------------------- 7
titulo("7. Límites que informa esta compilación")
con = sqlite3.connect(":memory:")
for nombre in (
    "SQLITE_LIMIT_LENGTH", "SQLITE_LIMIT_SQL_LENGTH", "SQLITE_LIMIT_COLUMN", "SQLITE_LIMIT_EXPR_DEPTH",
    "SQLITE_LIMIT_COMPOUND_SELECT", "SQLITE_LIMIT_VARIABLE_NUMBER", "SQLITE_LIMIT_ATTACHED",
    "SQLITE_LIMIT_LIKE_PATTERN_LENGTH", "SQLITE_LIMIT_TRIGGER_DEPTH", "SQLITE_LIMIT_FUNCTION_ARG",
):
    print(f"  {nombre:36s}= {con.getlimit(getattr(sqlite3, nombre)):,}")
print("  PRAGMA page_size                    =", con.execute("PRAGMA page_size").fetchone()[0])
mpc = con.execute("PRAGMA max_page_count").fetchone()[0]
ps = con.execute("PRAGMA page_size").fetchone()[0]
print(f"  PRAGMA max_page_count               = {mpc:,}")
print(f"  tamaño máximo = {mpc:,} x {ps} = {mpc * ps:,} bytes = {mpc * ps / 2**40:.2f} TiB = {mpc * ps / 1e12:.2f} TB")
print(f"  con páginas de 65536 bytes = {mpc * 65536 / 1e12:.1f} TB")
try:
    con.execute("SELECT 1 WHERE 1 IN (" + ",".join("?" * 40000) + ")", tuple(range(40000)))
except sqlite3.Error as e:
    print("  consulta con 40.000 parámetros (IN) ->", type(e).__name__, "-", e)
con.execute("SELECT 1 WHERE 1 IN (" + ",".join("?" * 30000) + ")", tuple(range(30000))).fetchall()
print("  consulta con 30.000 parámetros (IN) -> correcta")
try:
    con.execute("SELECT " + ",".join("?" * 3000), tuple(range(3000)))
except sqlite3.Error as e:
    print("  SELECT con 3.000 columnas de resultado ->", type(e).__name__, "-", e)

# ------------------------------------------------------------- 8
titulo("8. Claves foráneas: desactivadas por defecto")
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE padre (id INTEGER PRIMARY KEY)")
con.execute("CREATE TABLE hijo (id INTEGER PRIMARY KEY, padre_id INTEGER REFERENCES padre(id))")
print("  foreign_keys =", con.execute("PRAGMA foreign_keys").fetchone()[0])
con.execute("INSERT INTO hijo (padre_id) VALUES (999)")
print("  insertar un hijo con padre inexistente -> aceptado (no hay padre 999)")
print("  ¿hay una transacción abierta en el módulo sqlite3? in_transaction =", con.in_transaction)
con.execute("PRAGMA foreign_keys = ON")
print("  PRAGMA foreign_keys = ON dentro de la transacción -> foreign_keys =", con.execute("PRAGMA foreign_keys").fetchone()[0], "(sin efecto)")
con.commit()
con.execute("PRAGMA foreign_keys = ON")
print("  tras con.commit() y repetir el PRAGMA -> foreign_keys =", con.execute("PRAGMA foreign_keys").fetchone()[0])
try:
    con.execute("INSERT INTO hijo (padre_id) VALUES (998)")
except sqlite3.IntegrityError as e:
    print("  con foreign_keys=ON ->", type(e).__name__, "-", e)

print("\nfin")
```

## Salida de lab_wal.py

```text
SQLite 3.50.4 | Python 3.14.2 | win32

=== 1. Valores por defecto y archivos de WAL ===
journal_mode por defecto : delete
synchronous por defecto  : 2 (2 = FULL)
busy_timeout (módulo sqlite3 de Python, timeout=5 s por defecto): 5000 ms
foreign_keys por defecto : 0
wal_autocheckpoint       : 1000 páginas
archivos antes de WAL    : ['lab.db']
PRAGMA journal_mode=WAL  -> wal
archivos tras escribir   : ['lab.db', 'lab.db-shm', 'lab.db-wal']
archivos tras cerrar la última conexión: ['lab.db']
al reabrir, journal_mode : wal (persistente)
synchronous al reabrir   : 2 (no persistente)

=== 2. Un lector con transacción abierta y un escritor que confirma ===
  modo delete: COMMIT falla: database is locked
    el lector veía 10 filas; sigue viendo 10 dentro de su transacción; al terminarla ve 10
  modo wal   : COMMIT correcto
    el lector veía 10 filas; sigue viendo 10 dentro de su transacción; al terminarla ve 11

=== 3. Dos escritores a la vez ===
  modo delete: el segundo BEGIN IMMEDIATE falla: database is locked
  modo wal   : el segundo BEGIN IMMEDIATE falla: database is locked

=== 4. Coste de confirmar: 1.000 inserciones, cada una en su transacción ===
  journal_mode=delete synchronous=FULL  :   3.06 s en total =   3.06 ms por confirmación
  journal_mode=wal    synchronous=FULL  :   0.32 s en total =   0.32 ms por confirmación
  journal_mode=wal    synchronous=NORMAL:   0.03 s en total =   0.03 ms por confirmación

=== 4b. Una sola transacción con 100.000 filas ===
  journal_mode=delete: 0.08 s
  journal_mode=wal   : 0.08 s

=== 5. Tamaño del archivo WAL y puntos de control ===
  wal_autocheckpoint=1000 (por defecto): WAL máximo = 3.93 MiB, final = 3.93 MiB, base de datos = 1.87 MiB
  wal_autocheckpoint=0 (desactivado): WAL máximo = 4.48 MiB, final = 4.48 MiB, base de datos = 0.00 MiB
    wal_checkpoint(PASSIVE) -> (0, 1139, 1139) (ocupado, páginas en el WAL, páginas pasadas a la base de datos)
    wal_checkpoint(TRUNCATE) -> (0, 0, 0)
    WAL tras TRUNCATE = 0 bytes

=== 5b. Un lector con una transacción abierta impide reiniciar el WAL ===
  con el lector abierto: wal_checkpoint(PASSIVE)  -> (0, 287, 3)
  con el lector abierto: wal_checkpoint(TRUNCATE) -> (1, 287, 3)
  tamaño del WAL = 1.13 MiB
  al cerrar la transacción del lector: wal_checkpoint(TRUNCATE) -> (0, 0, 0)
  tamaño del WAL = 0 bytes

=== 6. Lectores y escritor a la vez, con 300 confirmaciones del escritor ===
  modo delete: lecturas correctas =     44, lecturas con 'database is locked' =    18, escrituras fallidas = 28
  modo wal   : lecturas correctas =  10144, lecturas con 'database is locked' =     0, escrituras fallidas = 0

=== 7. Límites que informa esta compilación ===
  SQLITE_LIMIT_LENGTH                 = 1,000,000,000
  SQLITE_LIMIT_SQL_LENGTH             = 1,000,000,000
  SQLITE_LIMIT_COLUMN                 = 2,000
  SQLITE_LIMIT_EXPR_DEPTH             = 1,000
  SQLITE_LIMIT_COMPOUND_SELECT        = 500
  SQLITE_LIMIT_VARIABLE_NUMBER        = 32,766
  SQLITE_LIMIT_ATTACHED               = 10
  SQLITE_LIMIT_LIKE_PATTERN_LENGTH    = 50,000
  SQLITE_LIMIT_TRIGGER_DEPTH          = 1,000
  SQLITE_LIMIT_FUNCTION_ARG           = 1,000
  PRAGMA page_size                    = 4096
  PRAGMA max_page_count               = 4,294,967,294
  tamaño máximo = 4,294,967,294 x 4096 = 17,592,186,036,224 bytes = 16.00 TiB = 17.59 TB
  con páginas de 65536 bytes = 281.5 TB
  consulta con 40.000 parámetros (IN) -> OperationalError - too many SQL variables
  consulta con 30.000 parámetros (IN) -> correcta
  SELECT con 3.000 columnas de resultado -> OperationalError - too many columns in result set

=== 8. Claves foráneas: desactivadas por defecto ===
  foreign_keys = 0
  insertar un hijo con padre inexistente -> aceptado (no hay padre 999)
  ¿hay una transacción abierta en el módulo sqlite3? in_transaction = True
  PRAGMA foreign_keys = ON dentro de la transacción -> foreign_keys = 0 (sin efecto)
  tras con.commit() y repetir el PRAGMA -> foreign_keys = 1
  con foreign_keys=ON -> IntegrityError - FOREIGN KEY constraint failed

fin
```
