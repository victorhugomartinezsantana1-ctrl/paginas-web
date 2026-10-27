# Auditoría — ART-006 TCP en la práctica

Fecha: 2026-10-27 · Palabras editoriales: 6.711 · Fuentes registradas: 8

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| RFC 9293 (ago. 2022, STD 7) obsoleta RFC 793, 879, 2873, 6093, 6429, 6528, 6691 y actualiza 1011, 1122, 5961 | RFC 9293 | Verificado |
| Tres pasos de apertura, estados, TIME-WAIT = 2×MSL (MSL de 2 min), MSS por defecto 536/1220, Nagle (SHOULD) y desactivación (MUST), ACK retardado (< 0,5 s), sondeo de ventana cero, keepalive desactivado por defecto con intervalo ≥ 2 h | RFC 9293 (caracteres 0–200.000 de 252.501) | Verificado en la parte leída |
| RTO inicial 1 s, α = 1/8, β = 1/4, K = 4, mínimo 1 s (SHOULD), duplicación, Karn | RFC 6298 | Verificado |
| Ventana inicial 2/3/4 segmentos según SMSS; `ssthresh = max(FlightSize/2, 2×SMSS)`; ventana de pérdida de 1 segmento | RFC 5681 | Verificado |
| CUBIC: β = 0,7, C = 0,4, obsoleta RFC 8312 | RFC 9438 | Verificado |
| IW ≤ min(10×MSS, max(2×MSS, 14600)); advertencias | RFC 6928 (Experimental) | Verificado |
| Valores por defecto de `tcp_*` (syncookies, max_syn_backlog, keepalive 7200/75/9, retries2 = 15, rmem/wmem) y `TCP_USER_TIMEOUT` (desde 2.6.37) | tcp(7) | Verificado; los valores del kernel pueden variar por versión y distribución (el texto lo advierte) |
| Opciones de `ss` y campos de `-i`; opciones de `tcpdump` y letras de banderas | ss(8), tcpdump(1) | Verificado |
| Aritmética (RTO con RTT de 100 y 120 ms; 64 KB/100 ms ≈ 5,2 Mbit/s; 6,25 MB de producto ancho de banda por retardo; 29.200 B → ssthresh 14.600; 20×0,7 = 14) | Cálculo propio | Recalculada a mano |

### Correcciones hechas durante la revisión

1. Se eliminó la cita de que la RFC 6928 ilustra «2 rondas frente a 5» para 32 segmentos: no estaba registrada en `fuentes.md`; queda solo la cuenta simplificada propia, marcada como tal (3+6+12+24 en 4 rondas frente a 10+20+40 en 3).
2. Se eliminó la frase sobre que la RFC 6928 «exige monitorización» para no activarse por defecto: no figuraba en las notas de la fuente.
3. Se marcó como dato de experiencia general (no de las fuentes) que cortafuegos y balanceadores descartan conexiones inactivas tras unos minutos.
4. El significado de `Recv-Q`/`Send-Q`, `retrans`, BBR y el motivo de `tcp_fin_timeout` ya estaban señalados como conocimiento general.

### No ejecutado

Ningún comando (`ss`, `tcpdump`) ni el fragmento de Python se ejecutó: el equipo de redacción es Windows. No se muestran salidas.

## Auditoría editorial

- 19 secciones principales, tabla de síntomas y causas, tabla de ajustes del kernel, 8 preguntas frecuentes.
- Enlaza con contenedores, Kubernetes y (como continuación) TLS.

## Auditoría técnica (verificar.py local)

OK — sin errores ni avisos; recuento publicado = aprobado; 8 referencias.
