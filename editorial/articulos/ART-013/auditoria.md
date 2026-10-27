# Auditoría — ART-013 C++ moderno

Fecha: 2026-10-27 · Palabras editoriales: ver `manifiesto.json` (≈ 6.400) · Fuentes registradas: 7 (5 de cppreference, Core Guidelines y laboratorio)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Definición de RAII (constructor adquiere o lanza; destructor libera y no lanza), orden inverso, desenrollado de pila, clases no RAII (`open/close`, `lock/unlock`), recursos a los que no aplica, clases estándar RAII | cppreference, RAII | Verificado |
| `unique_ptr`: propiedad exclusiva, copia prohibida / movimiento permitido, deleter por defecto y personalizado, arrays, usos, tipos incompletos, conversión derivada→base y destructor virtual | cppreference, unique_ptr | Verificado |
| `shared_ptr`: bloque de control (contenido), una asignación con `make_shared`, contadores atómicos con orden relajado, seguridad entre hilos de las funciones miembro sobre objetos distintos | cppreference, shared_ptr | Verificado; se dejó constancia de lo que la página NO dice (ciclos, aproximación de `use_count`, frase del bloque de control) |
| Reglas de tres, cinco y cero; un destructor, copia o asignación declarados impiden el movimiento implícito | cppreference, rule of three | Verificado |
| `std::move` como `static_cast` a referencia de rvalue, estado «válido pero no especificado», `std::forward` | cppreference, move | Verificado; el caso `const` no figura en la página y se declara como conocimiento general |
| Directrices C.20, C.21, C.22, C.30, C.31, C.32; R.1, R.3, R.5, R.11, R.12, R.20, R.21, R.22, R.24, R.32, R.34, R.37; títulos de C.35, C.36, C.37, C.64, C.66, C.127, C.150, R.2, R.23, R.30, R.33, E.6, E.16, E.25–E.27, CP.20 | C++ Core Guidelines | Verificado (R.30 solo por su título; remite a F.7, no leído) |
| Salidas de los 12 experimentos y el error de compilación | `lab_cpp.md` (g++ 16.1.0, `-std=c++20 -Wall -Wextra`; compilación sin avisos) | Ejecutadas y copiadas de la salida real |
| Aritmética: 1+2+4 = 7 elementos movidos o copiados al crecer 8 elementos | Cálculo propio coherente con la medida (7) | Verificado |

### Correcciones hechas durante la revisión

1. Se declaró como conocimiento general (no de cppreference) que `std::move` sobre un `const` acaba en copia y el mecanismo de `std::move_if_noexcept`; los resultados siguen siendo medidas reales.
2. Se retiró la comparación implícita «la asignación es una sola en ambos casos» entre `make_unique` y `new`, porque solo se midió `make_unique`.
3. Se evitó atribuir a cppreference las frases «el bloque de control es seguro pero el objeto no» y «`use_count` es aproximado», que la página no contiene.
4. Se marcó como simulación el recurso de hardware (no hay placa) y como conocimiento general las excepciones desactivadas en entornos embebidos y la pareja `initscr`/`endwin`.
5. Se corrigió «se libera sola» por «se libera solo».

### No ejecutado

Solo se probó g++ 16.1.0; no clang ni MSVC, ni modos -O2/-O3, ni otras plataformas. No hay hardware real. No se probó qué ocurre si un destructor lanza una excepción.

## Auditoría editorial

- 12 secciones, 8 errores frecuentes, 7 preguntas frecuentes, tabla de firmas de parámetros.
- Enlaza con Rust frente a C++, ncurses y FreeRTOS.
- El borrador se escribió en cinco tramos y se ensambló; se comprobó el equilibrio de etiquetas HTML.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
