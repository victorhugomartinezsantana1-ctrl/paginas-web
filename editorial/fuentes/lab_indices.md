# Laboratorio — ART-015 índices en bases de datos

Fecha de ejecución: 2026-10-27. Equipo: Windows 11, SQLite 3.50.4 (módulo sqlite3 de Python 3.14.2), base de datos en archivo temporal, 300.000 filas generadas con semilla fija (20261027). No se usó PostgreSQL: no hay servidor en el equipo. El script se ejecutó con python -I -X utf8. Las rutas locales se sustituyeron por marcadores (`<PYTHON>`, `<LAB>`) para no publicar rutas del equipo. Los tiempos varían entre ejecuciones y equipos: son medidas de una ejecución, no valores garantizados.

## Fuente: lab_indices.py

```python
import os
import random
import sqlite3
import statistics
import string
import sys
import tempfile
import time
from datetime import date, timedelta

N = 300_000
CLIENTES = 20_000


def titulo(t):
    print(f"\n=== {t} ===")


def plan(con, sql, params=()):
    filas = con.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return [f[3] for f in filas]


def muestra_plan(con, etiqueta, sql, params=()):
    print(f"  {etiqueta}")
    for linea in plan(con, sql, params):
        print(f"    -> {linea}")


def medir(con, sql, lista_params, repeticiones=3):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        for p in lista_params:
            con.execute(sql, p).fetchall()
        tiempos.append((time.perf_counter() - t0) / len(lista_params) * 1000)
    return min(tiempos)


def tamano_paginas(con):
    return con.execute("PRAGMA page_count").fetchone()[0] * con.execute("PRAGMA page_size").fetchone()[0]


def bytes_objeto(con, nombre):
    try:
        return con.execute("SELECT SUM(pgsize) FROM dbstat WHERE name = ?", (nombre,)).fetchone()[0]
    except sqlite3.OperationalError:
        return None


print("SQLite", sqlite3.sqlite_version, "| Python", sys.version.split()[0], "|", sys.platform)
opciones = [r[0] for r in sqlite3.connect(":memory:").execute("PRAGMA compile_options")]
print("DBSTAT disponible:", any("DBSTAT" in o for o in opciones))

ruta = os.path.join(tempfile.mkdtemp(), "lab_indices.db")
con = sqlite3.connect(ruta)
con.execute("PRAGMA journal_mode = OFF")
con.execute("PRAGMA synchronous = OFF")
con.execute(
    "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER, estado TEXT, importe REAL, creado TEXT, notas TEXT)"
)
rnd = random.Random(20261027)
inicio = date(2024, 1, 1)


def fila(i):
    estado = rnd.choices(("pagado", "pendiente", "cancelado"), weights=(95, 4, 1))[0]
    creado = (inicio + timedelta(days=rnd.randrange(366))).isoformat()
    notas = "".join(rnd.choices(string.ascii_lowercase, k=12))
    return (i, rnd.randrange(1, CLIENTES + 1), estado, round(rnd.uniform(5, 500), 2), creado, notas)


t0 = time.perf_counter()
con.executemany("INSERT INTO pedidos VALUES (?,?,?,?,?,?)", (fila(i) for i in range(1, N + 1)))
con.commit()
print(f"filas insertadas: {N:,} en {time.perf_counter() - t0:.1f} s")
print("reparto por estado:", dict(con.execute("SELECT estado, COUNT(*) FROM pedidos GROUP BY estado")))
print(f"tamaño de la tabla sin índices: {tamano_paginas(con) / 1024 / 1024:.1f} MiB")

clientes = [rnd.randrange(1, CLIENTES + 1) for _ in range(30)]
params_cli = [(c,) for c in clientes]

# ----------------------------------------------------------------- 1
titulo("1. Búsqueda por cliente: sin índice frente a índice")
q = "SELECT * FROM pedidos WHERE cliente_id = ?"
muestra_plan(con, "sin índice:", q, (clientes[0],))
t_sin = medir(con, q, params_cli)
con.execute("CREATE INDEX idx_cliente ON pedidos (cliente_id)")
muestra_plan(con, "con índice idx_cliente(cliente_id):", q, (clientes[0],))
t_con = medir(con, q, params_cli)
print(f"  tiempo medio por consulta: sin índice = {t_sin:.2f} ms | con índice = {t_con:.3f} ms | factor = {t_sin / t_con:.0f}x")
print("  filas devueltas por cliente (media):", round(statistics.mean(len(con.execute(q, p).fetchall()) for p in params_cli), 1))

# ----------------------------------------------------------------- 2
titulo("2. Coste en disco: tamaño de los índices (diferencia de tamaño del archivo)")
con.execute("DROP INDEX idx_cliente")
con.execute("VACUUM")
base = tamano_paginas(con)
print(f"  tabla pedidos sin índices: {base / 1024 / 1024:.2f} MiB")


def tam_indice(ddl, nombre):
    con.execute(ddl)
    con.commit()
    t = tamano_paginas(con)
    con.execute(f"DROP INDEX {nombre}")
    con.execute("VACUUM")
    return t - base


for etiqueta, ddl, nombre in (
    ("(cliente_id)", "CREATE INDEX z ON pedidos (cliente_id)", "z"),
    ("(estado, cliente_id)", "CREATE INDEX z ON pedidos (estado, cliente_id)", "z"),
    ("(cliente_id, estado, importe)", "CREATE INDEX z ON pedidos (cliente_id, estado, importe)", "z"),
    ("(notas), texto de 12 caracteres", "CREATE INDEX z ON pedidos (notas)", "z"),
    ("(cliente_id) WHERE estado = 'pendiente'", "CREATE INDEX z ON pedidos (cliente_id) WHERE estado = 'pendiente'", "z"),
):
    d = tam_indice(ddl, nombre)
    print(f"  índice {etiqueta}: {d / 1024 / 1024:.2f} MiB ({d / base * 100:.0f} % de la tabla)")
con.execute("CREATE INDEX idx_cliente ON pedidos (cliente_id)")
con.commit()

# ----------------------------------------------------------------- 3
titulo("3. Índices compuestos: el orden de las columnas")
con.execute("CREATE INDEX idx_estado_cliente ON pedidos (estado, cliente_id)")
con.execute("CREATE INDEX idx_cliente_estado ON pedidos (cliente_id, estado)")
consultas = [
    ("a) WHERE cliente_id = ? AND estado = 'pendiente'", "SELECT * FROM pedidos INDEXED BY {ix} WHERE cliente_id = ? AND estado = 'pendiente'", (clientes[0],)),
    ("b) WHERE estado = 'pendiente' (sin cliente)", "SELECT COUNT(*) FROM pedidos INDEXED BY {ix} WHERE estado = 'pendiente'", ()),
    ("c) WHERE cliente_id = ? (sin estado)", "SELECT * FROM pedidos INDEXED BY {ix} WHERE cliente_id = ?", (clientes[0],)),
]
for etiqueta, sql, p in consultas:
    print(f"  {etiqueta}")
    for ix in ("idx_estado_cliente", "idx_cliente_estado"):
        try:
            lineas = plan(con, sql.format(ix=ix), p)
            print(f"    {ix:20s}: {lineas[0]}")
        except sqlite3.OperationalError as e:
            print(f"    {ix:20s}: no utilizable ({e})")

# ----------------------------------------------------------------- 4
titulo("4. Una función sobre la columna indexada")
con.execute("CREATE INDEX idx_creado ON pedidos (creado)")
q_directa = "SELECT COUNT(*) FROM pedidos WHERE creado >= '2024-03-01' AND creado < '2024-04-01'"
q_funcion = "SELECT COUNT(*) FROM pedidos WHERE substr(creado, 1, 7) = '2024-03'"
muestra_plan(con, "rango directo sobre la columna:", q_directa)
muestra_plan(con, "substr(creado,1,7) = '2024-03':", q_funcion)
t_dir = medir(con, q_directa, [()], 5)
t_fun = medir(con, q_funcion, [()], 5)
print(f"  tiempos: rango directo = {t_dir:.2f} ms | con función = {t_fun:.2f} ms")
con.execute("CREATE INDEX idx_mes ON pedidos (substr(creado, 1, 7))")
muestra_plan(con, "tras CREATE INDEX idx_mes ON pedidos (substr(creado, 1, 7)):", q_funcion)
t_exp = medir(con, q_funcion, [()], 5)
print(f"  tiempo con índice de expresión = {t_exp:.2f} ms")
print("  resultados idénticos:", con.execute(q_directa).fetchone() == con.execute(q_funcion).fetchone())

# ----------------------------------------------------------------- 5
titulo("5. LIKE: prefijo frente a sufijo")
q_pre = "SELECT COUNT(*) FROM pedidos WHERE notas LIKE 'abc%'"
q_suf = "SELECT COUNT(*) FROM pedidos WHERE notas LIKE '%abc'"
con.execute("CREATE INDEX idx_notas ON pedidos (notas)")
muestra_plan(con, "índice con intercalación BINARY (la predeterminada), LIKE 'abc%':", q_pre)
con.execute("CREATE INDEX idx_notas_nocase ON pedidos (notas COLLATE NOCASE)")
muestra_plan(con, "con índice COLLATE NOCASE, LIKE 'abc%':", q_pre)
muestra_plan(con, "con ambos índices, LIKE '%abc':", q_suf)

# ----------------------------------------------------------------- 6
titulo("6. Índice de cobertura")
q = "SELECT estado, importe FROM pedidos WHERE cliente_id = ?"
muestra_plan(con, "con idx_cliente (solo cliente_id):", q, (clientes[0],))
t_a = medir(con, q.replace("FROM pedidos", "FROM pedidos INDEXED BY idx_cliente"), params_cli)
con.execute("CREATE INDEX idx_cobertura ON pedidos (cliente_id, estado, importe)")
muestra_plan(con, "con idx_cobertura (cliente_id, estado, importe):", q, (clientes[0],))
t_b = medir(con, q.replace("FROM pedidos", "FROM pedidos INDEXED BY idx_cobertura"), params_cli)
print(f"  tiempo medio por consulta: idx_cliente = {t_a:.3f} ms | idx_cobertura = {t_b:.3f} ms | factor = {t_a / t_b:.2f}x")

# ----------------------------------------------------------------- 7
titulo("7. ORDER BY con y sin índice adecuado")
q = "SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY creado DESC LIMIT 5"
muestra_plan(con, "con idx_cliente:", q.replace("FROM pedidos", "FROM pedidos INDEXED BY idx_cliente"), (clientes[0],))
con.execute("CREATE INDEX idx_cliente_creado ON pedidos (cliente_id, creado)")
muestra_plan(con, "con idx_cliente_creado (cliente_id, creado):", q.replace("FROM pedidos", "FROM pedidos INDEXED BY idx_cliente_creado"), (clientes[0],))

# ----------------------------------------------------------------- 8
titulo("8. Selectividad: un índice sobre una columna con pocos valores")
q_comun = "SELECT COUNT(*), AVG(importe) FROM pedidos {hint} WHERE estado = 'pagado'"
q_raro = "SELECT COUNT(*), AVG(importe) FROM pedidos {hint} WHERE estado = 'cancelado'"
t = {}
for nombre, q_ in (("pagado (95 %)", q_comun), ("cancelado (1 %)", q_raro)):
    t[nombre] = (
        medir(con, q_.format(hint="NOT INDEXED"), [()], 3),
        medir(con, q_.format(hint="INDEXED BY idx_estado_cliente"), [()], 3),
    )
    print(f"  estado = {nombre}: sin índice = {t[nombre][0]:.1f} ms | con idx_estado_cliente = {t[nombre][1]:.1f} ms")
q_def = "SELECT COUNT(*), AVG(importe) FROM pedidos WHERE estado = ?"
for valor in ("pagado", "cancelado"):
    muestra_plan(con, f"sin pista, antes de ANALYZE, estado = '{valor}':", q_def, (valor,))
    print(f"    tiempo = {medir(con, q_def, [(valor,)], 3):.1f} ms")
con.execute("ANALYZE")
con.commit()
for valor in ("pagado", "cancelado"):
    muestra_plan(con, f"sin pista, después de ANALYZE, estado = '{valor}':", q_def, (valor,))
    print(f"    tiempo = {medir(con, q_def, [(valor,)], 3):.1f} ms")
print("  filas de sqlite_stat1:")
for fila_stat in con.execute("SELECT tbl, idx, stat FROM sqlite_stat1 ORDER BY idx"):
    print("    ", fila_stat)

# ----------------------------------------------------------------- 9
titulo("9. Índice parcial: solo los pedidos pendientes")
for ix in ("idx_estado_cliente", "idx_cliente_estado", "idx_cobertura", "idx_cliente_creado", "idx_creado", "idx_mes", "idx_notas", "idx_notas_nocase"):
    con.execute(f"DROP INDEX {ix}")
con.execute("CREATE INDEX idx_pend_cliente ON pedidos (cliente_id) WHERE estado = 'pendiente'")
q_pend = "SELECT * FROM pedidos WHERE cliente_id = ? AND estado = 'pendiente'"
muestra_plan(con, "consulta con estado = 'pendiente':", q_pend, (clientes[0],))
q_pag = "SELECT * FROM pedidos WHERE cliente_id = ? AND estado = 'pagado'"
muestra_plan(con, "consulta con estado = 'pagado' (fuera del predicado):", q_pag.replace("FROM pedidos", "FROM pedidos INDEXED BY idx_cliente"), (clientes[0],))
try:
    plan(con, q_pag.replace("FROM pedidos", "FROM pedidos INDEXED BY idx_pend_cliente"), (clientes[0],))
    print("  (el planificador aceptó usar el parcial para 'pagado')")
except sqlite3.OperationalError as e:
    print("  forzar el índice parcial para 'pagado' ->", e)

# ----------------------------------------------------------------- 10
titulo("10. Coste de escritura: insertar 50.000 filas con 0, 1 y 4 índices")
for nombre in ("idx_pend_cliente", "idx_cliente"):
    con.execute(f"DROP INDEX IF EXISTS {nombre}")
variantes = [
    ("0 índices", []),
    ("1 índice (cliente_id)", ["CREATE INDEX w1 ON pedidos (cliente_id)"]),
    ("4 índices", ["CREATE INDEX w1 ON pedidos (cliente_id)", "CREATE INDEX w2 ON pedidos (estado, cliente_id)", "CREATE INDEX w3 ON pedidos (creado)", "CREATE INDEX w4 ON pedidos (notas)"]),
]
siguiente = N + 1
for nombre, ddl in variantes:
    for ix in ("w1", "w2", "w3", "w4"):
        con.execute(f"DROP INDEX IF EXISTS {ix}")
    for sentencia in ddl:
        con.execute(sentencia)
    lote = [fila(i) for i in range(siguiente, siguiente + 50_000)]
    siguiente += 50_000
    t0 = time.perf_counter()
    con.executemany("INSERT INTO pedidos VALUES (?,?,?,?,?,?)", lote)
    con.commit()
    print(f"  {nombre:24s}: {time.perf_counter() - t0:.2f} s")

con.close()
print("\nfin")
```

## Salida de lab_indices.py

```text
SQLite 3.50.4 | Python 3.14.2 | win32
DBSTAT disponible: False
filas insertadas: 300,000 en 2.4 s
reparto por estado: {'cancelado': 2990, 'pagado': 284981, 'pendiente': 12029}
tamaño de la tabla sin índices: 14.8 MiB

=== 1. Búsqueda por cliente: sin índice frente a índice ===
  sin índice:
    -> SCAN pedidos
  con índice idx_cliente(cliente_id):
    -> SEARCH pedidos USING INDEX idx_cliente (cliente_id=?)
  tiempo medio por consulta: sin índice = 29.28 ms | con índice = 0.111 ms | factor = 264x
  filas devueltas por cliente (media): 15.0

=== 2. Coste en disco: tamaño de los índices (diferencia de tamaño del archivo) ===
  tabla pedidos sin índices: 14.76 MiB
  índice (cliente_id): 3.13 MiB (21 % de la tabla)
  índice (estado, cliente_id): 5.20 MiB (35 % de la tabla)
  índice (cliente_id, estado, importe): 7.77 MiB (53 % de la tabla)
  índice (notas), texto de 12 caracteres: 6.02 MiB (41 % de la tabla)
  índice (cliente_id) WHERE estado = 'pendiente': 0.13 MiB (1 % de la tabla)

=== 3. Índices compuestos: el orden de las columnas ===
  a) WHERE cliente_id = ? AND estado = 'pendiente'
    idx_estado_cliente  : SEARCH pedidos USING INDEX idx_estado_cliente (estado=? AND cliente_id=?)
    idx_cliente_estado  : SEARCH pedidos USING INDEX idx_cliente_estado (cliente_id=? AND estado=?)
  b) WHERE estado = 'pendiente' (sin cliente)
    idx_estado_cliente  : SEARCH pedidos USING COVERING INDEX idx_estado_cliente (estado=?)
    idx_cliente_estado  : SCAN pedidos USING COVERING INDEX idx_cliente_estado
  c) WHERE cliente_id = ? (sin estado)
    idx_estado_cliente  : SCAN pedidos USING INDEX idx_estado_cliente
    idx_cliente_estado  : SEARCH pedidos USING INDEX idx_cliente_estado (cliente_id=?)

=== 4. Una función sobre la columna indexada ===
  rango directo sobre la columna:
    -> SEARCH pedidos USING COVERING INDEX idx_creado (creado>? AND creado<?)
  substr(creado,1,7) = '2024-03':
    -> SCAN pedidos USING COVERING INDEX idx_creado
  tiempos: rango directo = 1.43 ms | con función = 35.79 ms
  tras CREATE INDEX idx_mes ON pedidos (substr(creado, 1, 7)):
    -> SEARCH pedidos USING COVERING INDEX idx_mes (<expr>=?)
  tiempo con índice de expresión = 1.65 ms
  resultados idénticos: True

=== 5. LIKE: prefijo frente a sufijo ===
  índice con intercalación BINARY (la predeterminada), LIKE 'abc%':
    -> SCAN pedidos USING COVERING INDEX idx_notas
  con índice COLLATE NOCASE, LIKE 'abc%':
    -> SEARCH pedidos USING COVERING INDEX idx_notas_nocase (notas>? AND notas<?)
  con ambos índices, LIKE '%abc':
    -> SCAN pedidos USING COVERING INDEX idx_notas_nocase

=== 6. Índice de cobertura ===
  con idx_cliente (solo cliente_id):
    -> SEARCH pedidos USING INDEX idx_cliente (cliente_id=?)
  con idx_cobertura (cliente_id, estado, importe):
    -> SEARCH pedidos USING COVERING INDEX idx_cobertura (cliente_id=?)
  tiempo medio por consulta: idx_cliente = 0.110 ms | idx_cobertura = 0.082 ms | factor = 1.34x

=== 7. ORDER BY con y sin índice adecuado ===
  con idx_cliente:
    -> SEARCH pedidos USING INDEX idx_cliente (cliente_id=?)
    -> USE TEMP B-TREE FOR ORDER BY
  con idx_cliente_creado (cliente_id, creado):
    -> SEARCH pedidos USING INDEX idx_cliente_creado (cliente_id=?)

=== 8. Selectividad: un índice sobre una columna con pocos valores ===
  estado = pagado (95 %): sin índice = 43.8 ms | con idx_estado_cliente = 1895.7 ms
  estado = cancelado (1 %): sin índice = 37.2 ms | con idx_estado_cliente = 26.8 ms
  sin pista, antes de ANALYZE, estado = 'pagado':
    -> SEARCH pedidos USING INDEX idx_estado_cliente (estado=?)
    tiempo = 1835.3 ms
  sin pista, antes de ANALYZE, estado = 'cancelado':
    -> SEARCH pedidos USING INDEX idx_estado_cliente (estado=?)
    tiempo = 17.1 ms
  sin pista, después de ANALYZE, estado = 'pagado':
    -> SEARCH pedidos USING INDEX idx_estado_cliente (estado=?)
    tiempo = 1805.1 ms
  sin pista, después de ANALYZE, estado = 'cancelado':
    -> SEARCH pedidos USING INDEX idx_estado_cliente (estado=?)
    tiempo = 17.4 ms
  filas de sqlite_stat1:
     ('pedidos', 'idx_cliente', '300000 15')
     ('pedidos', 'idx_cliente_creado', '300000 15 1')
     ('pedidos', 'idx_cliente_estado', '300000 15 10')
     ('pedidos', 'idx_cobertura', '300000 15 10 1')
     ('pedidos', 'idx_creado', '300000 820')
     ('pedidos', 'idx_estado_cliente', '300000 100000 10')
     ('pedidos', 'idx_mes', '300000 25000')
     ('pedidos', 'idx_notas', '300000 1')
     ('pedidos', 'idx_notas_nocase', '300000 1')

=== 9. Índice parcial: solo los pedidos pendientes ===
  consulta con estado = 'pendiente':
    -> SEARCH pedidos USING INDEX idx_pend_cliente (cliente_id=?)
  consulta con estado = 'pagado' (fuera del predicado):
    -> SEARCH pedidos USING INDEX idx_cliente (cliente_id=?)
  forzar el índice parcial para 'pagado' -> no query solution

=== 10. Coste de escritura: insertar 50.000 filas con 0, 1 y 4 índices ===
  0 índices               : 0.07 s
  1 índice (cliente_id)   : 0.49 s
  4 índices               : 3.41 s

fin
```
