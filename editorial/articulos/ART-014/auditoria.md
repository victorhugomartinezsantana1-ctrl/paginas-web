# Auditoría — ART-014 Rust: propiedad, préstamos y lifetimes

Fecha: 2026-10-27 · Palabras editoriales: ver `manifiesto.json` (≈ 5.300) · Fuentes registradas: 6 (5 capítulos del libro oficial + 3 páginas del índice de errores)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Tres reglas de propiedad; pila y montículo; `drop` al cerrar la llave | Libro, cap. 4.1 | Verificado |
| Movimiento, `error[E0382]: borrow of moved value`, `clone`, tipos `Copy` y restricción con `Drop`, propiedad y funciones, «demasiada ceremonia» | Libro, cap. 4.1 | Verificado |
| Referencias, préstamo, inmutables por defecto (E0596), una mutable o varias inmutables (E0499, E0502), condiciones de una carrera de datos, alcance hasta el último uso, referencias colgantes (E0106) | Libro, cap. 4.2 | Verificado; el nombre «non-lexical lifetimes» se marcó como dato general porque la página no lo usa |
| Objetivo de los lifetimes, E0597, sintaxis `&'a`, `longest<'a>`, structs, tres reglas de elisión, `'static` y su advertencia, sin coste en ejecución | Libro, cap. 10.3 | Verificado |
| `Mutex`, `MutexGuard` (Deref + Drop), `Rc` no `Send`, `Arc`, atómicos y coste, mutabilidad interior, interbloqueos | Libro, cap. 16.3 | Verificado; `Sync` no definido (la página lo difiere) |
| `Rc` (un solo hilo), `Rc::clone`, `strong_count`/`weak_count`, solo lectura compartida, remite a `RefCell` y `Weak` | Libro, cap. 15.4 | Verificado; ciclos y `Weak` no desarrollados |
| E0505, E0507 y E0373: descripciones y correcciones | Índice de errores | Verificado; se dejó constancia de lo que las páginas no mencionan (`clone` en E0505/E0507; ejemplo corregido de `thread::spawn`) |
| Comparación con C++ (liberación, usar tras mover, copias, `shared_ptr`/`Rc`, carreras de datos) | Libro + `lab_cpp.md` + cppreference | Síntesis propia, declarada como tal |

### Correcciones hechas durante la revisión

1. Se evitó afirmar que el desbloqueo de un `Mutex` «no se puede hacer a mano»; ahora se dice que es automático al salir del ámbito.
2. Se limitó la afirmación de «programas libres de errores» a «código seguro» y se marcó como precisión propia, porque las páginas consultadas no tratan `unsafe`.
3. La comprobación en tiempo de ejecución de `RefCell` se declaró como dato general (no verificado en las páginas consultadas).
4. La tabla de errores distingue el texto documentado (código y titular) de la síntesis propia (causa típica y salidas habituales).
5. El texto avisa desde la introducción de que **ningún fragmento se compiló** y de que no se reproducen salidas completas del compilador.

### No ejecutado

No hay `rustc` ni `cargo` en el equipo: ningún fragmento de Rust se compiló ni ejecutó, no hay salidas de compilador propias y no se midió rendimiento ni tamaño de binarios. No se usó el Rust Playground ni otro servicio externo.

## Auditoría editorial

- 11 secciones, tabla de 9 errores del compilador, tabla comparativa con C++, 8 hábitos prácticos, 6 errores frecuentes, 7 preguntas frecuentes.
- Enlaza con Rust frente a C++, C++ moderno y memoria en Python.
- Es el artículo del lote 3 con menor margen sobre el mínimo de palabras.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
