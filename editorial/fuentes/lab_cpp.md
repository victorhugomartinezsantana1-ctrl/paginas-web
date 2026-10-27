# Laboratorio — ART-013 C++ moderno: RAII, movimiento y punteros inteligentes

Fecha de ejecución: 2026-10-27. Equipo: Windows 11, g++ (GCC) 16.1.0 (x86_64-w64-mingw32, w64devkit), modo -std=c++20 -Wall -Wextra -O0. El segundo programa (lab_cpp_error.cpp) se compiló sin -Wall con -std=c++20 y falla a propósito. Las rutas locales se sustituyeron por marcadores (`<PYTHON>`, `<LAB>`) para no publicar rutas del equipo. Los tiempos varían entre ejecuciones y equipos: son medidas de una ejecución, no valores garantizados.

## Fuente: lab_cpp.cpp

```cpp
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <new>
#include <set>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// Cuenta las asignaciones de memoria dinámica para poder compararlas.
static int g_asignaciones = 0;
void* operator new(std::size_t n) {
    ++g_asignaciones;
    if (void* p = std::malloc(n)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

// ------------------------------------------------------------------ 1
struct Traza {
    std::string n;
    explicit Traza(std::string nombre) : n(std::move(nombre)) { std::cout << "  adquirir " << n << "\n"; }
    ~Traza() { std::cout << "  liberar  " << n << "\n"; }
    Traza(const Traza&) = delete;
    Traza& operator=(const Traza&) = delete;
};

void s1() {
    std::cout << "\n=== 1. RAII: orden de liberación ===\n";
    Traza a("A");
    Traza b("B");
    Traza c("C");
    std::cout << "  fin del ámbito\n";
}

// ------------------------------------------------------------------ 2
struct Pieza {
    static inline int vivas = 0;
    Pieza() { ++vivas; }
    ~Pieza() { --vivas; }
};
void falla() { throw std::runtime_error("fallo intermedio"); }
void manual() {
    Pieza* p = new Pieza();
    falla();
    delete p;  // nunca se ejecuta
}
void con_raii() {
    auto p = std::make_unique<Pieza>();
    falla();
}
void s2() {
    std::cout << "\n=== 2. Excepciones: new/delete manual frente a unique_ptr ===\n";
    int antes = Pieza::vivas;
    try { manual(); } catch (const std::exception& e) { std::cout << "  manual: capturada '" << e.what() << "'\n"; }
    std::cout << "  piezas que quedaron vivas tras manual(): " << (Pieza::vivas - antes) << "\n";
    antes = Pieza::vivas;
    try { con_raii(); } catch (const std::exception& e) { std::cout << "  con_raii: capturada '" << e.what() << "'\n"; }
    std::cout << "  piezas que quedaron vivas tras con_raii(): " << (Pieza::vivas - antes) << "\n";
}

// ------------------------------------------------------------------ 3
struct Buffer {
    int* d;
    std::size_t n;
    explicit Buffer(std::size_t n_) : d(new int[n_]()), n(n_) { std::cout << "    ctor(" << n << ")\n"; }
    ~Buffer() { delete[] d; }
    Buffer(const Buffer& o) : d(new int[o.n]), n(o.n) {
        std::copy(o.d, o.d + n, d);
        std::cout << "    COPIA: constructor de copia\n";
    }
    Buffer(Buffer&& o) noexcept : d(std::exchange(o.d, nullptr)), n(std::exchange(o.n, 0)) {
        std::cout << "    MOVE: constructor de movimiento\n";
    }
    Buffer& operator=(const Buffer& o) {
        std::cout << "    COPIA: asignación de copia\n";
        if (this != &o) {
            int* nd = new int[o.n];
            std::copy(o.d, o.d + o.n, nd);
            delete[] d;
            d = nd;
            n = o.n;
        }
        return *this;
    }
    Buffer& operator=(Buffer&& o) noexcept {
        std::cout << "    MOVE: asignación de movimiento\n";
        if (this != &o) {
            delete[] d;
            d = std::exchange(o.d, nullptr);
            n = std::exchange(o.n, 0);
        }
        return *this;
    }
};

void s3() {
    std::cout << "\n=== 3. Copia y movimiento (regla de cinco) ===\n";
    Buffer a(4);
    std::cout << "  Buffer b = a;\n";
    Buffer b = a;
    std::cout << "  Buffer c = std::move(a);\n";
    Buffer c = std::move(a);
    std::cout << "  tras mover: a.d es " << (a.d ? "no nulo" : "nulo") << ", a.n = " << a.n << "\n";
    std::cout << "  b = c;\n";
    b = c;
    std::cout << "  b = std::move(c);\n";
    b = std::move(c);
    std::cout << "  const Buffer k(3); Buffer x = std::move(k);\n";
    const Buffer k(3);
    Buffer x = std::move(k);
    (void)x;
}

// ------------------------------------------------------------------ 4
template <bool Noexc>
struct Pesado {
    static inline int copias = 0, movimientos = 0;
    int* d;
    Pesado() : d(new int[4]()) {}
    Pesado(const Pesado& o) : d(new int[4]) { std::copy(o.d, o.d + 4, d); ++copias; }
    Pesado(Pesado&& o) noexcept(Noexc) : d(std::exchange(o.d, nullptr)) { ++movimientos; }
    Pesado& operator=(const Pesado&) = delete;
    ~Pesado() { delete[] d; }
};
template <bool N>
void crece(const char* etiqueta) {
    Pesado<N>::copias = 0;
    Pesado<N>::movimientos = 0;
    std::vector<Pesado<N>> v;
    for (int i = 0; i < 8; ++i) v.emplace_back();
    std::cout << "  " << etiqueta << ": copias=" << Pesado<N>::copias << ", movimientos=" << Pesado<N>::movimientos << "\n";
}
void s4() {
    std::cout << "\n=== 4. Crecimiento de un vector de 8 elementos: movimiento con y sin noexcept ===\n";
    crece<true>("movimiento noexcept   ");
    crece<false>("movimiento sin noexcept");
}

// ------------------------------------------------------------------ 5
void s5() {
    std::cout << "\n=== 5. Estado de un objeto estándar tras moverlo ===\n";
    std::string s(60, 'x');
    std::string t = std::move(s);
    std::cout << "  string: t.size()=" << t.size() << ", s.size() tras mover=" << s.size() << "\n";
    std::vector<int> v1(1000, 7);
    std::vector<int> v2 = std::move(v1);
    std::cout << "  vector: v2.size()=" << v2.size() << ", v1.size() tras mover=" << v1.size() << "\n";
    std::cout << "  ¿Se puede usar de nuevo la movida? s.append(\"ok\") -> ";
    s.append("ok");
    std::cout << "'" << s << "'\n";
}

// ------------------------------------------------------------------ 6
void s6() {
    std::cout << "\n=== 6. Tamaño de los punteros inteligentes (bytes, esta plataforma) ===\n";
    auto lam = [](int* p) { delete p; };
    int cuenta = 0;
    auto lamcap = [&cuenta](int* p) { ++cuenta; delete p; };
    std::cout << "  sizeof(int*)                                  = " << sizeof(int*) << "\n";
    std::cout << "  sizeof(unique_ptr<int>)                       = " << sizeof(std::unique_ptr<int>) << "\n";
    std::cout << "  sizeof(unique_ptr<int, lambda sin capturas>)  = " << sizeof(std::unique_ptr<int, decltype(lam)>) << "\n";
    std::cout << "  sizeof(unique_ptr<int, void(*)(int*)>)        = " << sizeof(std::unique_ptr<int, void (*)(int*)>) << "\n";
    std::cout << "  sizeof(unique_ptr<int, lambda con captura>)   = " << sizeof(std::unique_ptr<int, decltype(lamcap)>) << "\n";
    std::cout << "  sizeof(shared_ptr<int>)                       = " << sizeof(std::shared_ptr<int>) << "\n";
}

// ------------------------------------------------------------------ 7
std::unique_ptr<Buffer> fabrica() { return std::make_unique<Buffer>(2); }
void consume(std::unique_ptr<Buffer> p) { std::cout << "  consume: recibo un Buffer de " << p->n << " elementos\n"; }
void s7() {
    std::cout << "\n=== 7. unique_ptr: transferencia de propiedad ===\n";
    auto p = fabrica();
    std::cout << "  consume(std::move(p));\n";
    consume(std::move(p));
    std::cout << "  tras mover, p es " << (p ? "no nulo" : "nulo") << "\n";
}

// ------------------------------------------------------------------ 8
struct Obj { int x[4]; };
void s8() {
    std::cout << "\n=== 8. Asignaciones dinámicas y contadores de shared_ptr ===\n";
    int a0 = g_asignaciones;
    auto s1p = std::make_shared<Obj>();
    int a1 = g_asignaciones;
    std::shared_ptr<Obj> s2p(new Obj);
    int a2 = g_asignaciones;
    auto u1 = std::make_unique<Obj>();
    int a3 = g_asignaciones;
    std::cout << "  make_shared<Obj>()        : " << (a1 - a0) << " asignación(es)\n";
    std::cout << "  shared_ptr<Obj>(new Obj)  : " << (a2 - a1) << " asignación(es)\n";
    std::cout << "  make_unique<Obj>()        : " << (a3 - a2) << " asignación(es)\n";
    auto copia = s1p;
    std::weak_ptr<Obj> debil = s1p;
    std::cout << "  use_count tras una copia y un weak_ptr: " << s1p.use_count() << "\n";
    copia.reset();
    std::cout << "  use_count tras reset de la copia: " << s1p.use_count() << "\n";
    s1p.reset();
    std::cout << "  weak_ptr.expired() tras soltar el último dueño: " << std::boolalpha << debil.expired() << "\n";
}

// ------------------------------------------------------------------ 9
struct NodoS {
    static inline int destruidos = 0;
    std::shared_ptr<NodoS> otro;
    ~NodoS() { ++destruidos; }
};
struct NodoW {
    static inline int destruidos = 0;
    std::shared_ptr<NodoW> otro;
    std::weak_ptr<NodoW> atras;
    ~NodoW() { ++destruidos; }
};
void s9() {
    std::cout << "\n=== 9. Ciclos de shared_ptr y weak_ptr ===\n";
    {
        auto a = std::make_shared<NodoS>();
        auto b = std::make_shared<NodoS>();
        a->otro = b;
        b->otro = a;
    }
    std::cout << "  ciclo de shared_ptr: destructores ejecutados = " << NodoS::destruidos << " de 2\n";
    {
        auto a = std::make_shared<NodoW>();
        auto b = std::make_shared<NodoW>();
        a->otro = b;
        b->atras = a;
    }
    std::cout << "  con weak_ptr hacia atrás: destructores ejecutados = " << NodoW::destruidos << " de 2\n";
}

// ------------------------------------------------------------------ 10
void s10() {
    std::cout << "\n=== 10. unique_ptr con deleter propio (FILE*) ===\n";
    auto cerrar = [](std::FILE* f) {
        if (f) {
            std::fclose(f);
            std::cout << "  (fclose ejecutado por el deleter)\n";
        }
    };
    {
        std::unique_ptr<std::FILE, decltype(cerrar)> f(std::fopen("lab_cpp_tmp.txt", "w"), cerrar);
        std::fputs("hola desde RAII\n", f.get());
    }
    {
        std::unique_ptr<std::FILE, decltype(cerrar)> f(std::fopen("lab_cpp_tmp.txt", "r"), cerrar);
        char buf[64]{};
        std::fgets(buf, sizeof buf, f.get());
        std::cout << "  leído: " << buf;
    }
    std::remove("lab_cpp_tmp.txt");
}

// ------------------------------------------------------------------ 11
struct Registro {
    std::string nombre;
    std::vector<int> datos;
};
void s11() {
    std::cout << "\n=== 11. Regla de cero ===\n";
    Registro r1{"temperatura", std::vector<int>(1000, 5)};
    Registro r2 = r1;
    Registro r3 = std::move(r1);
    std::cout << "  copia: r2.datos.size()=" << r2.datos.size() << "\n";
    std::cout << "  movimiento: r3.datos.size()=" << r3.datos.size() << ", r1.datos.size() tras mover=" << r1.datos.size() << "\n";
    std::cout << std::boolalpha;
    std::cout << "  is_nothrow_move_constructible<Registro> = " << std::is_nothrow_move_constructible_v<Registro> << "\n";
    std::cout << "  is_copy_constructible<Registro>         = " << std::is_copy_constructible_v<Registro> << "\n";
}

// ------------------------------------------------------------------ 12
// Simulación (sin hardware real) de un recurso exclusivo: un pin que solo puede reservar un dueño.
std::set<int>& pines_ocupados() {
    static std::set<int> s;
    return s;
}
class Pin {
    int n_ = -1;
    void liberar() noexcept {
        if (n_ >= 0) {
            pines_ocupados().erase(n_);
            std::cout << "  liberar pin " << n_ << "\n";
            n_ = -1;
        }
    }
public:
    explicit Pin(int n) {
        if (!pines_ocupados().insert(n).second)
            throw std::runtime_error("el pin " + std::to_string(n) + " ya está reservado");
        n_ = n;
        std::cout << "  reservar pin " << n_ << "\n";
    }
    ~Pin() { liberar(); }
    Pin(const Pin&) = delete;
    Pin& operator=(const Pin&) = delete;
    Pin(Pin&& o) noexcept : n_(std::exchange(o.n_, -1)) {}
    Pin& operator=(Pin&& o) noexcept {
        if (this != &o) {
            liberar();
            n_ = std::exchange(o.n_, -1);
        }
        return *this;
    }
    int numero() const { return n_; }
};
Pin abre_pin(int n) { return Pin(n); }
void s12() {
    std::cout << "\n=== 12. Recurso exclusivo simulado (pin) con movimiento ===\n";
    {
        Pin a = abre_pin(4);
        Pin b = std::move(a);
        std::cout << "  tras mover: a.numero()=" << a.numero() << ", b.numero()=" << b.numero() << "\n";
        try {
            Pin c(4);
        } catch (const std::exception& e) {
            std::cout << "  error esperado: " << e.what() << "\n";
        }
    }
    std::cout << "  fuera del ámbito; se puede reservar de nuevo:\n";
    Pin d(4);
}

int main() {
    std::cout << "g++ " << __VERSION__ << " | __cplusplus=" << __cplusplus << "\n";
    s1();
    s2();
    s3();
    s4();
    s5();
    s6();
    s7();
    s8();
    s9();
    s10();
    s11();
    s12();
    return 0;
}
```

## Salida de lab_cpp.cpp

```text
g++.exe (GCC) 16.1.0
--- comando: g++ -std=c++20 -Wall -Wextra -O0 -o lab_cpp.exe lab_cpp.cpp
exit=0

--- ejecución: ./lab_cpp.exe
g++ 16.1.0 | __cplusplus=202002

=== 1. RAII: orden de liberación ===
  adquirir A
  adquirir B
  adquirir C
  fin del ámbito
  liberar  C
  liberar  B
  liberar  A

=== 2. Excepciones: new/delete manual frente a unique_ptr ===
  manual: capturada 'fallo intermedio'
  piezas que quedaron vivas tras manual(): 1
  con_raii: capturada 'fallo intermedio'
  piezas que quedaron vivas tras con_raii(): 0

=== 3. Copia y movimiento (regla de cinco) ===
    ctor(4)
  Buffer b = a;
    COPIA: constructor de copia
  Buffer c = std::move(a);
    MOVE: constructor de movimiento
  tras mover: a.d es nulo, a.n = 0
  b = c;
    COPIA: asignación de copia
  b = std::move(c);
    MOVE: asignación de movimiento
  const Buffer k(3); Buffer x = std::move(k);
    ctor(3)
    COPIA: constructor de copia

=== 4. Crecimiento de un vector de 8 elementos: movimiento con y sin noexcept ===
  movimiento noexcept   : copias=0, movimientos=7
  movimiento sin noexcept: copias=7, movimientos=0

=== 5. Estado de un objeto estándar tras moverlo ===
  string: t.size()=60, s.size() tras mover=0
  vector: v2.size()=1000, v1.size() tras mover=0
  ¿Se puede usar de nuevo la movida? s.append("ok") -> 'ok'

=== 6. Tamaño de los punteros inteligentes (bytes, esta plataforma) ===
  sizeof(int*)                                  = 8
  sizeof(unique_ptr<int>)                       = 8
  sizeof(unique_ptr<int, lambda sin capturas>)  = 8
  sizeof(unique_ptr<int, void(*)(int*)>)        = 16
  sizeof(unique_ptr<int, lambda con captura>)   = 16
  sizeof(shared_ptr<int>)                       = 16

=== 7. unique_ptr: transferencia de propiedad ===
    ctor(2)
  consume(std::move(p));
  consume: recibo un Buffer de 2 elementos
  tras mover, p es nulo

=== 8. Asignaciones dinámicas y contadores de shared_ptr ===
  make_shared<Obj>()        : 1 asignación(es)
  shared_ptr<Obj>(new Obj)  : 2 asignación(es)
  make_unique<Obj>()        : 1 asignación(es)
  use_count tras una copia y un weak_ptr: 2
  use_count tras reset de la copia: 1
  weak_ptr.expired() tras soltar el último dueño: true

=== 9. Ciclos de shared_ptr y weak_ptr ===
  ciclo de shared_ptr: destructores ejecutados = 0 de 2
  con weak_ptr hacia atrás: destructores ejecutados = 2 de 2

=== 10. unique_ptr con deleter propio (FILE*) ===
  (fclose ejecutado por el deleter)
  leído: hola desde RAII
  (fclose ejecutado por el deleter)

=== 11. Regla de cero ===
  copia: r2.datos.size()=1000
  movimiento: r3.datos.size()=1000, r1.datos.size() tras mover=0
  is_nothrow_move_constructible<Registro> = true
  is_copy_constructible<Registro>         = true

=== 12. Recurso exclusivo simulado (pin) con movimiento ===
  reservar pin 4
  tras mover: a.numero()=-1, b.numero()=4
  error esperado: el pin 4 ya está reservado
  liberar pin 4
  fuera del ámbito; se puede reservar de nuevo:
  reservar pin 4
  liberar pin 4
```

## Fuente: lab_cpp_error.cpp

```cpp
#include <memory>

int main() {
    std::unique_ptr<int> a = std::make_unique<int>(1);
    std::unique_ptr<int> b = a;  // intento de copiar un unique_ptr
    return 0;
}
```

## Salida de lab_cpp_error.cpp

```text
lab_cpp_error.cpp: In function 'int main()':
lab_cpp_error.cpp:5:30: error: use of deleted function 'std::unique_ptr<_Tp, _Dp>::unique_ptr(const std::unique_ptr<_Tp, _Dp>&) [with _Tp = int; _Dp = std::default_delete<int>]'
    5 |     std::unique_ptr<int> b = a;  // intento de copiar un unique_ptr
      |                              ^
In file included from <GCC>/memory:80,
                 from lab_cpp_error.cpp:1:
<GCC>/bits/unique_ptr.h:524:7: note: declared here
  524 |       unique_ptr(const unique_ptr&) = delete;
      |       ^~~~~~~~~~
lab_cpp_error.cpp:5:30: note: use '-fdiagnostics-all-candidates' to display considered candidates
    5 |     std::unique_ptr<int> b = a;  // intento de copiar un unique_ptr
      |                              ^
```
