# Auditoría — ART-003 PostgreSQL por dentro

Fecha: 2026-10-27 · Palabras editoriales: 6.512 · Fuentes registradas: 6

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Principio MVCC (lectura no bloquea escritura) | mvcc-intro (PG 18) | Verificado |
| 4 niveles, 3 comportamientos reales; defecto Read Committed; tabla de fenómenos | transaction-iso | Verificado |
| Errores `could not serialize access…`, SQLSTATE 40001, SSI, SIRead, DEFERRABLE | transaction-iso | Verificado |
| Página de 8 kB, cabecera de página 24 B, puntero de línea 4 B, cabecera de tupla 23 B | storage-page-layout | Verificado |
| Motivos de VACUUM; VACUUM FULL con ACCESS EXCLUSIVE; fórmula de autovacuum | routine-vacuuming | Verificado |
| XID de 32 bits, ~2.000 millones, freeze, 200 millones por defecto, avisos a 40 M, rechazo < 3 M | routine-vacuuming | Verificado |
| Fórmula de coste secuencial, 445,00 y 470,00, cifras de nodos y de unión | using-explain | Verificado |
| default_statistics_target = 100; estadísticas extendidas; coeficientes 1,0 y 0,423130; 0,35 % frente a 0,0027 % | planner-stats | Verificado |

### Correcciones hechas durante la revisión

1. Frase sobre por qué los TID apuntan a punteros de línea: era una consecuencia del diseño presentada como cita → reformulada indicando que es inferencia.
2. Valores por defecto de `autovacuum_vacuum_threshold` (50) y `scale_factor` (0,2): la página **no** los da → el artículo lo dice y pide confirmarlos.
3. `cpu_operator_cost` (0,0025): se deduce de 470−445=25; se indica que no se cita expresamente.
4. Relación entre transacciones largas y vacuum: marcada como consecuencia lógica del modelo, no cita.

### Conocimiento general (señalado)

Regla simplificada de visibilidad de tuplas, comportamiento de HOT (descartado el detalle), consultas de `pg_stat_*` y de `pageinspect`.

### No ejecutado

Ninguna sentencia SQL (sin PostgreSQL en el equipo). Las únicas salidas mostradas son las de la documentación y están atribuidas.

## Auditoría editorial

- 15 secciones, 9 preguntas frecuentes, guía de diagnóstico, errores comunes.
- Enlaza con el artículo de Terraform (servidor PostgreSQL flexible).

## Auditoría técnica (verificar.py local)

OK — sin errores; recuento publicado = aprobado; 6 referencias.
