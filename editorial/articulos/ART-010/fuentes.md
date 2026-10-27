# Fuentes — ART-010 Observabilidad

Consulta: 2026-10-27.

| # | Fuente | Organismo | URL | Respalda | Limitaciones |
|---|---|---|---|---|---|
| 1 | Data model | Prometheus | https://prometheus.io/docs/concepts/data_model/ | Serie temporal = nombre de métrica + etiquetas; notación; expresiones regulares recomendadas de nombres; etiquetas `__` reservadas; cada combinación de etiquetas es una serie nueva; muestras con valor float64 o histograma nativo y marca de tiempo en milisegundos; etiquetas vacías equivalen a ausentes | La página no usa la palabra "cardinalidad" ni da la advertencia (la da la página de nombres) |
| 2 | Metric types | Prometheus | https://prometheus.io/docs/concepts/metric_types/ | Contador, medidor (gauge), histograma (`_bucket{le}`, `_sum`, `_count`, cubo `+Inf`), resumen (`quantile`); histogramas nativos más eficientes | No dice dónde se calculan los cuantiles del resumen ni si es agregable (se tomó de la fuente 4) |
| 3 | Metric and label naming | Prometheus | https://prometheus.io/docs/practices/naming/ | Prefijo de aplicación; unidades base (segundos, bytes); sufijos (`_total`); una sola unidad y cantidad; razones 0–1; que `sum()` o `avg()` tengan sentido; advertencia sobre etiquetas de alta cardinalidad (ID de usuario, correos) | — |
| 4 | Histograms and summaries | Prometheus | https://prometheus.io/docs/practices/histograms/ | Comparativa histograma/resumen; elegir cubos junto al objetivo de nivel de servicio; los resúmenes no se pueden agregar; `histogram_quantile()` y error acotado por el ancho del cubo (ejemplo del p95 estimado en 295 ms dentro de un cubo de 200–300 ms) | — |
| 5 | Query functions | Prometheus | https://prometheus.io/docs/prometheus/latest/querying/functions/ | `rate`, `irate`, `increase`, `histogram_quantile` y sus reglas; `rate` para alertas | **No** contiene la regla "ventana ≥ 4 veces el intervalo de recolección" que se había buscado; el artículo no la afirma |
| 6 | Alerting | Prometheus | https://prometheus.io/docs/practices/alerting/ | Alertar sobre síntomas; pocas alertas y simples; evitar avisos sin acción posible; margen para pequeños picos; enlazar a consolas; avisar de errores visibles para el usuario | No trata `for`, ventanas de `rate`, runbooks ni "fatiga de alertas" (no se atribuyen a la fuente) |
| 7 | Signals | OpenTelemetry | https://opentelemetry.io/docs/concepts/signals/ | Señales: trazas, métricas, registros, baggage; perfiles y eventos en desarrollo | — |
| 8 | Traces | OpenTelemetry | https://opentelemetry.io/docs/concepts/signals/traces/ | Traza, span, span raíz, hijos; contexto del span (trace ID, span ID, banderas, trace state); atributos, eventos, enlaces; estado (Unset, Error, Ok); tipo (Client, Server, Internal, Producer, Consumer; por defecto Internal) | — |
| 9 | Logs | OpenTelemetry | https://opentelemetry.io/docs/concepts/signals/logs/ | Registros estructurados preferidos; correlación con trazas mediante TraceId/SpanId; campos del modelo de datos; adaptadores de bibliotecas de registro | — |
| 10 | OpenTelemetry Collector | OpenTelemetry | https://opentelemetry.io/docs/collector/ | Implementación independiente del proveedor para recibir, procesar y exportar telemetría; componentes (receptores, procesadores, exportadores, conectores, extensiones); estabilidad "mixta" | No define OTLP ni describe patrones de despliegue |
| 11 | Trace Context, Nivel 1 | W3C | https://www.w3.org/TR/trace-context/ | Recomendación del 23-11-2021; formato de `traceparent` (versión, trace-id de 16 bytes, parent-id de 8 bytes, banderas); ceros inválidos; bandera de muestreo (`01`); `tracestate`; ejemplo oficial | — |
| 12 | Service Level Objectives | Google, *Site Reliability Engineering* | https://sre.google/sre-book/service-level-objectives/ | Definiciones de SLI, SLO y SLA; SLIs típicos; percentiles frente a medias; presupuestos de error; no fijar objetivos a partir del rendimiento actual; simplicidad; ejemplos de disponibilidad (99 %, 99,999 %, 99,95 %) | El capítulo no usa 99,9 % como ejemplo |

## Observaciones

- No se ejecutó ningún código ni consulta. Los ejemplos de Python (prometheus_client y OpenTelemetry) y de PromQL son ilustrativos y están señalados.
- Las cifras de presupuesto de error y de cardinalidad son aritmética propia (indicada en el texto).
- Conocimiento general (señalado): diferencia entre monitorización y observabilidad, muestreo, `for` en reglas de alerta, estructura de un archivo de reglas, `/metrics` como ruta habitual.

## Verificaciones adicionales de la auditoría (27-10-2026)

- Histograms and summaries: confirmado que el resumen calcula cuantiles dentro del programa instrumentado y «Not aggregatable»; que `histogram_quantile()` se calcula en el servidor y los histogramas clásicos se agregan si no cambian los límites de los cubos; escenario del objetivo de 300 ms con cubos 0,1/0,2/0,3/0,45; valor real 220 ms frente a estimación de 295 ms, con el valor real garantizado entre 200 y 300 ms; «Error is limited by the width of the bucket the quantile is located in».
- Query functions: confirmado `rate()` (media por segundo, ajuste de reinicios, extrapolación, solo contadores); `irate()` solo para gráficos de contadores volátiles y `rate()` para alertas porque cambios breves pueden reiniciar la cláusula `FOR`; `increase()` descrita como azúcar sintáctico de `rate()` por los segundos de la ventana; `histogram_quantile()` supone distribución uniforme dentro del cubo; ejemplo con `sum by (le)` y ventana de 10 m.
