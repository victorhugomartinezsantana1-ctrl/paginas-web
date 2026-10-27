# Fuentes — ART-003 PostgreSQL por dentro

Consulta: 2026-10-27. Todas las páginas pertenecen a la documentación oficial de PostgreSQL, versión 18 (la página de introducción a MVCC muestra "PostgreSQL 18" y "18.6 Documentation"). No indican fecha de publicación.

| # | Fuente | URL | Respalda | Limitaciones |
|---|---|---|---|---|
| 1 | 13.1 Introduction (MVCC) | https://www.postgresql.org/docs/current/mvcc-intro.html | Principio MVCC: los bloqueos de lectura no entran en conflicto con los de escritura; "leer nunca bloquea escribir" | Página muy breve |
| 2 | 13.2 Transaction Isolation | https://www.postgresql.org/docs/current/transaction-iso.html | Cuatro niveles, tres comportamientos reales; Read Uncommitted = Read Committed; nivel por defecto; tabla de fenómenos; instantánea por sentencia (RC) y por transacción (RR); error `could not serialize access due to concurrent update`; SSI, bloqueos SIRead, SQLSTATE 40001, reintentos; recomendaciones de ajuste; no transaccionalidad de secuencias | — |
| 3 | 24.1 Routine Vacuuming | https://www.postgresql.org/docs/current/routine-vacuuming.html | Motivos de VACUUM; VACUUM vs VACUUM FULL; autovacuum y su fórmula de umbral; wraparound de XID de 32 bits; congelación; `vacuum_freeze_min_age`; `autovacuum_freeze_max_age` (200 millones); avisos a 40 millones y rechazo con menos de 3 millones; mapa de visibilidad | **No** indica los valores por defecto de `autovacuum_vacuum_threshold` (50) ni `autovacuum_vacuum_scale_factor` (0,2): se anotan como conocimiento general no verificado en esta fuente |
| 4 | 66.6 Database Page Layout | https://www.postgresql.org/docs/current/storage-page-layout.html | Página de 8 kB; PageHeaderData de 24 bytes; ItemIdData de 4 bytes; cabecera de tupla (xmin, xmax, cid, ctid, infomask2, infomask, hoff) de 23 bytes | No describe cómo UPDATE usa xmax y ctid; esa parte se presenta como interpretación general |
| 5 | 14.1 Using EXPLAIN | https://www.postgresql.org/docs/current/using-explain.html | Formato de coste/filas/anchura; fórmula de coste secuencial con `seq_page_cost`=1,0 y `cpu_tuple_cost`=0,01; ejemplo 345 páginas y 10.000 filas = 445,00; con filtro = 470,00; nodos de escaneo y de unión con las cifras del ejemplo; EXPLAIN ANALYZE; aviso de que ejecuta la consulta; patrón BEGIN/ROLLBACK | `cpu_operator_cost` se deduce de la diferencia 470−445; el valor 0,0025 se anota como consistente, no citado |
| 6 | 14.2 Statistics Used by the Planner | https://www.postgresql.org/docs/current/planner-stats.html | `reltuples`/`relpages`; `pg_statistic`/`pg_stats`; `default_statistics_target` = 100; estadísticas extendidas (dependencies, ndistinct, mcv); ejemplo de zipcodes con coeficientes 1,0 y 0,423130; limitaciones | `histogram_bounds` y `correlation` solo se mencionan; la página remite al capítulo 69 |

## Observaciones

- No se ejecutó ninguna sentencia: no hay PostgreSQL instalado en el equipo de redacción. Los ejemplos SQL del artículo son ilustrativos y están señalados como no ejecutados; las cifras de salida son exclusivamente las de los ejemplos de la documentación.
- Las reglas simplificadas de visibilidad de tuplas, el comportamiento de HOT y la relación entre transacciones largas y vacuum se presentan como explicación general (no contenida en las páginas consultadas) y así se indica en el texto.
