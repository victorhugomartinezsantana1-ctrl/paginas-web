# Laboratorio — ART-012 memoria en Python

Fecha de ejecución: 2026-10-27. Equipo: Windows 11 (win32), Python 3.14.2 de 64 bits (compilación estándar, con GIL). El script se ejecutó con python -I -X utf8. Las rutas locales se sustituyeron por marcadores (`<PYTHON>`, `<LAB>`) para no publicar rutas del equipo. Los tiempos varían entre ejecuciones y equipos: son medidas de una ejecución, no valores garantizados.

## Fuente: lab_memoria.py

```python
import gc
import sys
import tracemalloc
import weakref


def titulo(t):
    print(f"\n=== {t} ===")


# ---------------------------------------------------------------- 1
titulo("1. Conteo de referencias")
x = []
print("getrefcount([]) recién creada:", sys.getrefcount(x))
y = x
print("tras y = x:", sys.getrefcount(x))
lista_de_listas = [x, x]
print("tras meterla dos veces en otra lista:", sys.getrefcount(x))
del y, lista_de_listas
print("tras borrar y y la otra lista:", sys.getrefcount(x))
print("getrefcount(None):", sys.getrefcount(None))
print("getrefcount(0):", sys.getrefcount(0))
print("getrefcount(10**6 + k):", sys.getrefcount(10**6 + len(x)))
print("¿None es inmortal? sys._is_immortal(None):", sys._is_immortal(None))
print("¿[] es inmortal? sys._is_immortal(x):", sys._is_immortal(x))

# ---------------------------------------------------------------- 2
titulo("2. Liberación inmediata al llegar a cero")


class Ruidoso:
    def __init__(self, nombre):
        self.nombre = nombre

    def __del__(self):
        print(f"  __del__ de {self.nombre}")


print("creo r1 y lo borro con del:")
r1 = Ruidoso("r1")
del r1
print("  (la línea de __del__ debe aparecer antes de esta)")
print("creo r2, lo guardo en una segunda variable y borro una:")
r2 = Ruidoso("r2")
r3 = r2
del r2
print("  r2 borrada, el objeto sigue vivo; ahora borro r3:")
del r3
print("  (aparece __del__ de r2)")

# ---------------------------------------------------------------- 3
titulo("3. Ciclos: el conteo de referencias no basta")


class Nodo:
    def __init__(self):
        self.otro = None


gc.collect()
a, b = Nodo(), Nodo()
a.otro, b.otro = b, a
ref_a = weakref.ref(a)
del a, b
print("tras del a, b (hay ciclo): ¿sigue vivo? ->", ref_a() is not None)
recogidos = gc.collect()
print("gc.collect() devolvió:", recogidos)
print("tras gc.collect(): ¿sigue vivo? ->", ref_a() is not None)

# ---------------------------------------------------------------- 4
titulo("4. Recolector: parámetros y estadísticas")
print("gc.isenabled():", gc.isenabled())
print("gc.get_threshold():", gc.get_threshold())
print("gc.get_count():", gc.get_count())
for i, est in enumerate(gc.get_stats()):
    print(f"generación {i}: collections={est['collections']}, collected={est['collected']}, uncollectable={est['uncollectable']}")

# ---------------------------------------------------------------- 5
titulo("5. sys.getsizeof de objetos básicos (bytes)")
muestras = [
    ("0", 0), ("1", 1), ("2**30", 2**30), ("2**100", 2**100),
    ("1.5", 1.5), ("''", ""), ("'a'", "a"), ("'a'*1000", "a" * 1000),
    ("[]", []), ("[0]*1000", [0] * 1000), ("()", ()), ("(0,)*1000", (0,) * 1000),
    ("{}", {}), ("set()", set()), ("bytes(1000)", bytes(1000)), ("object()", object()),
]
for nombre, valor in muestras:
    print(f"{nombre:>12}: {sys.getsizeof(valor)}")

titulo("5b. getsizeof no cuenta lo referenciado")
lista = [list(range(1000)) for _ in range(10)]
print("getsizeof(lista de 10 listas de 1000 enteros):", sys.getsizeof(lista))
print("suma de getsizeof de sus 10 sublistas        :", sum(sys.getsizeof(s) for s in lista))

# ---------------------------------------------------------------- 6
titulo("6. Sobreasignación al crecer una lista con append")
v = []
tam_ant = sys.getsizeof(v)
print(f"len=0: {tam_ant} bytes")
for i in range(1, 41):
    v.append(i)
    t = sys.getsizeof(v)
    if t != tam_ant:
        print(f"len={i}: {t} bytes (+{t - tam_ant})")
        tam_ant = t

# ---------------------------------------------------------------- 7
titulo("7. Instancias con __dict__ frente a __slots__ (100.000 objetos, con tracemalloc)")


class Normal:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c


class ConSlots:
    __slots__ = ("a", "b", "c")

    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c


N = 100_000
for clase in (Normal, ConSlots):
    gc.collect()
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    objetos = [clase(1, 2, 3) for _ in range(N)]
    actual = tracemalloc.get_traced_memory()[0] - base
    tracemalloc.stop()
    print(f"{clase.__name__:>8}: {actual / 1024:,.0f} KiB para {N:,} objetos = {actual / N:.0f} bytes por objeto (incluye la lista que los contiene)")
    del objetos

titulo("7b. Acceder a __dict__ puede crear el diccionario (100.000 objetos Normal)")
gc.collect()
tracemalloc.start()
base = tracemalloc.get_traced_memory()[0]
objetos = [Normal(1, 2, 3) for _ in range(N)]
antes = tracemalloc.get_traced_memory()[0] - base
for o in objetos:
    o.__dict__
despues = tracemalloc.get_traced_memory()[0] - base
tracemalloc.stop()
print(f"antes de tocar __dict__: {antes / N:.0f} bytes por objeto")
print(f"tras acceder a __dict__ de cada uno: {despues / N:.0f} bytes por objeto")
del objetos

n = Normal(1, 2, 3)
s = ConSlots(1, 2, 3)
print("getsizeof(Normal)  + getsizeof(__dict__):", sys.getsizeof(n), "+", sys.getsizeof(n.__dict__), "=", sys.getsizeof(n) + sys.getsizeof(n.__dict__))
print("getsizeof(ConSlots):", sys.getsizeof(s))
print("¿ConSlots tiene __dict__?", hasattr(s, "__dict__"))
try:
    s.d = 4
except AttributeError as e:
    print("asignar atributo nuevo a ConSlots ->", type(e).__name__, "-", e)
try:
    weakref.ref(s)
except TypeError as e:
    print("weakref.ref(ConSlots) ->", type(e).__name__, "-", e)

# ---------------------------------------------------------------- 8
titulo("8. Lista frente a generador (suma de 1.000.000 de cuadrados)")
tracemalloc.start()
tracemalloc.reset_peak()
r1 = sum([i * i for i in range(1_000_000)])
_, pico_lista = tracemalloc.get_traced_memory()
tracemalloc.reset_peak()
r2 = sum(i * i for i in range(1_000_000))
_, pico_gen = tracemalloc.get_traced_memory()
tracemalloc.stop()
print("mismo resultado:", r1 == r2)
print(f"pico con lista    : {pico_lista / 1024 / 1024:,.1f} MiB")
print(f"pico con generador: {pico_gen / 1024:,.1f} KiB")

# ---------------------------------------------------------------- 9
titulo("9. tracemalloc: encontrar la línea que retiene memoria")
guardado = []


def procesa(n):
    for i in range(n):
        guardado.append("registro-" + str(i) * 5)  # fuga: nunca se libera


tracemalloc.start()
procesa(1000)
foto1 = tracemalloc.take_snapshot()
procesa(50_000)
foto2 = tracemalloc.take_snapshot()
for est in foto2.compare_to(foto1, "lineno")[:3]:
    print(est)
tracemalloc.stop()

# ---------------------------------------------------------------- 10
titulo("10. Internado de cadenas")
s1 = "".join(["hola", " mundo"])
s2 = "".join(["hola", " mundo"])
print("iguales por valor:", s1 == s2, "| misma identidad:", s1 is s2)
i1, i2 = sys.intern(s1), sys.intern(s2)
print("tras sys.intern -> misma identidad:", i1 is i2)

# ---------------------------------------------------------------- 11
titulo("11. Cachés: sin límite, acotada y con referencias débiles")
import functools


def calcula(n):
    return [n] * 100


cache_dict = {}
tracemalloc.start()
base = tracemalloc.get_traced_memory()[0]
for n in range(20_000):
    cache_dict[n] = calcula(n)
dict_kib = (tracemalloc.get_traced_memory()[0] - base) / 1024
tracemalloc.stop()
print(f"dict sin límite: {len(cache_dict):,} entradas, {dict_kib:,.0f} KiB retenidos")
cache_dict.clear()


@functools.lru_cache(maxsize=128)
def calcula_lru(n):
    return [n] * 100


tracemalloc.start()
base = tracemalloc.get_traced_memory()[0]
for n in range(20_000):
    calcula_lru(n)
lru_kib = (tracemalloc.get_traced_memory()[0] - base) / 1024
tracemalloc.stop()
print(f"lru_cache(maxsize=128): {calcula_lru.cache_info()}, {lru_kib:,.0f} KiB retenidos")


class Grande:
    def __init__(self, n):
        self.n = n
        self.datos = [n] * 1000


objs = [Grande(i) for i in range(5)]
debil = weakref.WeakValueDictionary({o.n: o for o in objs})
print("5 objetos vivos; entradas en el diccionario débil:", len(debil))
del objs[2:]
print("tras soltar 3 objetos; entradas:", len(debil), "claves:", sorted(debil.keys()))
```

## Salida de lab_memoria.py

```text

=== 1. Conteo de referencias ===
getrefcount([]) recién creada: 2
tras y = x: 3
tras meterla dos veces en otra lista: 5
tras borrar y y la otra lista: 2
getrefcount(None): 3221225472
getrefcount(0): 3221225472
getrefcount(10**6 + k): 1
¿None es inmortal? sys._is_immortal(None): True
¿[] es inmortal? sys._is_immortal(x): False

=== 2. Liberación inmediata al llegar a cero ===
creo r1 y lo borro con del:
  __del__ de r1
  (la línea de __del__ debe aparecer antes de esta)
creo r2, lo guardo en una segunda variable y borro una:
  r2 borrada, el objeto sigue vivo; ahora borro r3:
  __del__ de r2
  (aparece __del__ de r2)

=== 3. Ciclos: el conteo de referencias no basta ===
tras del a, b (hay ciclo): ¿sigue vivo? -> True
gc.collect() devolvió: 2
tras gc.collect(): ¿sigue vivo? -> False

=== 4. Recolector: parámetros y estadísticas ===
gc.isenabled(): True
gc.get_threshold(): (2000, 10, 0)
gc.get_count(): (2, 0, 0)
generación 0: collections=0, collected=0, uncollectable=0
generación 1: collections=0, collected=0, uncollectable=0
generación 2: collections=2, collected=147, uncollectable=0

=== 5. sys.getsizeof de objetos básicos (bytes) ===
           0: 28
           1: 28
       2**30: 32
      2**100: 40
         1.5: 24
          '': 41
         'a': 42
    'a'*1000: 1041
          []: 56
    [0]*1000: 8056
          (): 48
   (0,)*1000: 8048
          {}: 64
       set(): 216
 bytes(1000): 1033
    object(): 16

=== 5b. getsizeof no cuenta lo referenciado ===
getsizeof(lista de 10 listas de 1000 enteros): 184
suma de getsizeof de sus 10 sublistas        : 80560

=== 6. Sobreasignación al crecer una lista con append ===
len=0: 56 bytes
len=1: 88 bytes (+32)
len=5: 120 bytes (+32)
len=9: 184 bytes (+64)
len=17: 248 bytes (+64)
len=25: 312 bytes (+64)
len=33: 376 bytes (+64)

=== 7. Instancias con __dict__ frente a __slots__ (100.000 objetos, con tracemalloc) ===
  Normal: 10,161 KiB para 100,000 objetos = 104 bytes por objeto (incluye la lista que los contiene)
ConSlots: 6,251 KiB para 100,000 objetos = 64 bytes por objeto (incluye la lista que los contiene)

=== 7b. Acceder a __dict__ puede crear el diccionario (100.000 objetos Normal) ===
antes de tocar __dict__: 104 bytes por objeto
tras acceder a __dict__ de cada uno: 168 bytes por objeto
getsizeof(Normal)  + getsizeof(__dict__): 48 + 96 = 144
getsizeof(ConSlots): 56
¿ConSlots tiene __dict__? False
asignar atributo nuevo a ConSlots -> AttributeError - 'ConSlots' object has no attribute 'd' and no __dict__ for setting new attributes
weakref.ref(ConSlots) -> TypeError - cannot create weak reference to 'ConSlots' object

=== 8. Lista frente a generador (suma de 1.000.000 de cuadrados) ===
mismo resultado: True
pico con lista    : 38.6 MiB
pico con generador: 3.7 KiB

=== 9. tracemalloc: encontrar la línea que retiene memoria ===
<LAB>\lab_memoria.py:182: size=4105 KiB (+4033 KiB), count=51001 (+50000), average=82 B
<PYTHON>\Lib\tracemalloc.py:560: size=392 B (+392 B), count=2 (+2), average=196 B
<PYTHON>\Lib\tracemalloc.py:423: size=328 B (+328 B), count=1 (+1), average=328 B

=== 10. Internado de cadenas ===
iguales por valor: True | misma identidad: False
tras sys.intern -> misma identidad: True

=== 11. Cachés: sin límite, acotada y con referencias débiles ===
dict sin límite: 20,000 entradas, 17,909 KiB retenidos
lru_cache(maxsize=128): CacheInfo(hits=0, misses=20000, maxsize=128, currsize=128), 120 KiB retenidos
5 objetos vivos; entradas en el diccionario débil: 5
tras soltar 3 objetos; entradas: 2 claves: [0, 1]
```
