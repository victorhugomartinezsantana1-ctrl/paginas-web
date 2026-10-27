# Auditoría — ART-010 Observabilidad

Fecha: 2026-10-27 · Palabras editoriales: 8.835 · Fuentes registradas: 12

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Series = nombre + etiquetas; regex de nombres; `__` reservado; muestras float64/histograma nativo con milisegundos; etiqueta vacía = ausente | Prometheus, Data model | Verificado |
| Cuatro tipos de métrica y forma de histograma/resumen | Prometheus, Metric types | Verificado |
| Convenciones de nombres y advertencia sobre etiquetas de alta cardinalidad | Prometheus, Naming | Verificado |
| Resumen calculado en el programa y no agregable; histograma calculado en el servidor, agregable si no cambian los cubos; cubos 0,1/0,2/0,3/0,45 para 300 ms; escenario 220 ms real / 295 ms estimado; error acotado por el ancho del cubo | Prometheus, Histograms and summaries | Verificado de nuevo en la auditoría |
| `rate`, `irate`, `increase`, `histogram_quantile`; `rate` para alertas por la cláusula `FOR` | Prometheus, Query functions | Verificado de nuevo en la auditoría |
| Alertar sobre síntomas, pocas y simples, con margen, enlazando a consolas | Prometheus, Alerting | Verificado |
| Señales, trazas (span, contexto, atributos, eventos, enlaces, estado, tipo), registros (modelo de datos, correlación), Collector (componentes, estabilidad mixta) | OpenTelemetry | Verificado |
| `traceparent` (55 caracteres, 16 + 8 bytes, bandera `01`), `tracestate`, ceros inválidos | W3C Trace Context | Verificado |
| SLI, SLO, SLA; SLIs típicos; percentiles; no basar el objetivo en el rendimiento actual; simplicidad; ejemplos 99 %, 99,999 %, 99,95 % | Google SRE, capítulo de SLO | Verificado |
| Cardinalidad (4×25×8 = 800; ×5.000 = 4.000.000; 13 series por combinación de histograma; 10.400; 325), interpolación (0,2 + 0,1×50/60 ≈ 0,283), reinicio (50+20+60 = 130), presupuestos (43.200 min), tasas de consumo (10×, 20×, 2×) | Cálculo propio | Recalculados a mano |

### Correcciones hechas durante la revisión

1. Se atribuía al capítulo de Google un indicador de «saturación» que el capítulo no lista como típico → sustituido por los que sí cita (latencia, errores, rendimiento, disponibilidad).
2. «Pocos» SLO se atribuía al capítulo → ahora solo «simples», y el resto como razonamiento propio.
3. Se retiraron detalles de `tracestate`, bits reservados y «ha decidido registrar» que no constaban en las notas de la fuente; la bandera se describe como «puede haber registrado datos».
4. El estado `Unset`/`Ok` se limita a lo registrado en la fuente.
5. Se quitó la frase «no son los de ninguna biblioteca» (cubos) por no verificada.
6. Se incorporaron datos verificados después de redactar: valor real de 220 ms, interpolación uniforme, `increase` como azúcar de `rate` y la relación de `irate` con `FOR`.
7. Se acortó la descripción meta de 179 a menos de 175 caracteres.

### No ejecutado

No se desplegó ningún Prometheus, Collector ni SDK. Los fragmentos de Python, PromQL y YAML son ilustrativos; no se validaron con `promtool` ni se muestran salidas. El caso de diagnóstico es ficticio y está declarado como tal.

## Auditoría editorial

- 19 secciones, caso de principio a fin (métricas → trazas → registros), 6 errores frecuentes y 7 preguntas frecuentes.
- Es el artículo más largo de la serie (8.835 palabras); el índice lateral ayuda a navegarlo.

## Auditoría técnica (verificar.py local)

OK — sin errores ni avisos; recuento publicado = aprobado; 12 referencias.
