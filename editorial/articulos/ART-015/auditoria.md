# Auditoría — ART-015 Índices en bases de datos

Fecha: 2026-10-27 · Palabras editoriales: ver `manifiesto.json` (≈ 6.200) · Fuentes registradas: 9 (5 páginas de PostgreSQL, 3 de SQLite y laboratorio propio)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| PostgreSQL: función de un índice, `CREATE INDEX`, sincronización, planificador, `ANALYZE`, sobrecoste, borrar índices poco usados, beneficio en `UPDATE`/`DELETE`/joins | Indexes: Introduction | Verificado; no se atribuyó «sobre el sistema en su conjunto» ni los comandos concretos que la página no nombra |
| B-tree por defecto, operadores, ordenación, `LIKE` anclado, otros tipos (Hash, GiST, SP-GiST, GIN, BRIN, `bloom`) | Index Types | Verificado |
| Índices de varias columnas: límite, regla de las columnas de la izquierda, *skip scan*, moderación | Multicolumn Indexes | Verificado; la versión en que apareció el *skip scan* no se comprobó y se dice |
| Recorridos solo de índice: restricciones, `INCLUDE`, mapa de visibilidad | Index-Only Scans | Verificado; la página no menciona `VACUUM`, `EXPLAIN` ni `Heap Fetches` y el texto no los afirma |
| Índices parciales: predicado, beneficios, regla de implicación, único parcial | Partial Indexes | Verificado |
| SQLite: búsqueda binaria y tabla de índice, índices compuestos, cobertura (≈ mitad de búsquedas), ordenar con índices, redundancia, `ANALYZE` | Query Planning | Verificado |
| `SCAN`/`SEARCH`/`COVERING INDEX`/`USE TEMP B-TREE`/`MULTI-INDEX OR`; el formato cambió en 3.24.0 y 3.36.0 | EXPLAIN QUERY PLAN | Verificado |
| Términos utilizables, sin huecos, *skip-scan* con `ANALYZE` (~18 repeticiones), condiciones de `LIKE`, cobertura (≈ el doble de rápido), índices automáticos | Optimizer Overview | Verificado; la página no dice que una función anule el índice (el texto lo declara) |
| Todas las medidas y planes (264×; tamaños; composición; 25×; `LIKE`; 1,34×; `ORDER BY`; 43×; `ANALYZE`; parcial; escrituras) | `lab_indices.md` | Ejecutadas y copiadas de la salida real |
| Aritmética: log₂ 300.000 ≈ 18,2; 300.000 / 18 ≈ 16.000; 5 ms × 10⁶ = 5 s y × 10⁹ = 83 min; 0,49/0,07 = 7×; 3,41/0,07 ≈ 49×; 1.895,7/43,8 ≈ 43× | Cálculo propio | Recalculada |

### Correcciones hechas durante la revisión

1. La introducción decía «50 minutos con mil millones» para una extrapolación lineal de 5 ms por mil filas; el cálculo correcto es 5.000 s ≈ 83 minutos, y se redactó como hipótesis condicional («si el coste crece en proporción...»).
2. «Decenas de miles de comprobaciones» se sustituyó por la cuenta explícita (300.000 / 18 ≈ 16.000).
3. Se marcó como no comprobado que la caché del sistema influya en la medida de selectividad, la hipótesis sobre columnas que crecen ordenadas y la práctica de crear índices tras una carga masiva.
4. Se evitó atribuir a PostgreSQL el comportamiento observado en SQLite (el planificador eligió un índice malo incluso tras `ANALYZE`): el texto lo limita a SQLite 3.50.4 y declara que no se investigó el motivo.
5. Se sustituyó el plan inicial de «medir con PostgreSQL» por SQLite, declarándolo en la introducción y en `fuentes.md`; los tamaños de índice se midieron por diferencia de tamaño de archivo porque `dbstat` no está disponible.
6. El primer tramo del borrador se cortó dentro de un bloque de código y se reensambló en tramos; se comprobó el equilibrio de las etiquetas HTML.

### No ejecutado

No se ejecutó ninguna consulta ni plan en PostgreSQL. No se midieron condiciones con `OR`, índices sobre varias tablas ni concurrencia. Los datos son sintéticos con una distribución elegida; los tiempos son de una ejecución en este equipo con la tabla en caché.

## Auditoría editorial

- 15 secciones, método de 8 pasos, 7 errores frecuentes, 7 preguntas frecuentes, 3 tablas.
- Enlaza con PostgreSQL (MVCC/VACUUM/planificador) y con observabilidad.
- Es el artículo del lote que más depende de medidas propias; el script está guardado para reproducirlo.

## Auditoría técnica (verificar.py local)

OK — verificar.py local sin errores ni avisos; recuento publicado = aprobado.
