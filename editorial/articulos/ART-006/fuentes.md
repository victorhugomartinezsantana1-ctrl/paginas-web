# Fuentes — ART-006 TCP en la práctica

Consulta: 2026-10-27. Las RFC indican su fecha de publicación; las páginas man no.

| # | Fuente | Organismo | URL | Respalda | Limitaciones |
|---|---|---|---|---|---|
| 1 | RFC 9293, «Transmission Control Protocol (TCP)», agosto de 2022 (STD 7) | IETF / RFC Editor | https://www.rfc-editor.org/rfc/rfc9293.html | Obsoleta RFC 793, 879, 2873, 6093, 6429, 6528 y 6691; actualiza 1011, 1122 y 5961; establecimiento de conexión en tres pasos; estados TCP; TIME-WAIT = 2×MSL con MSL de 2 minutos; formato de cabecera; MSS por defecto 536 (IPv4) y 1220 (IPv6); Nagle (SHOULD) y desactivable por aplicación (MUST); RTO según RFC 6298; ACK retardado (< 0,5 s; al menos cada 2 segmentos completos); síndrome de ventana tonta; sondeo de ventana cero; keep-alives (por defecto desactivados, intervalo ≥ 2 h) | Se leyeron los caracteres 0–200.000 de 252.501; faltan los últimos 52.501 (seguridad y apéndices). El tamaño máximo de cabecera (60 bytes) es una derivación del campo Data Offset, no una cita |
| 2 | RFC 5681, «TCP Congestion Control», septiembre de 2009 | IETF | https://www.rfc-editor.org/rfc/rfc5681.html | Los cuatro algoritmos; cwnd, ssthresh, rwnd; ventana inicial según SMSS (2, 3 o 4 segmentos); incremento de arranque lento; ~1 segmento por RTT en evitación de congestión; 3 ACK duplicados; `ssthresh = max(FlightSize/2, 2×SMSS)`; ventana de pérdida de 1 segmento tras RTO | La fecha de publicación no figuraba en el texto leído (se anota según el contenido de la RFC; verificar si se cita) |
| 3 | RFC 6298, «Computing TCP's Retransmission Timer» | IETF | https://www.rfc-editor.org/rfc/rfc6298.html | RTO inicial de 1 s; SRTT/RTTVAR; K = 4; alfa = 1/8 y beta = 1/4; RTO mínimo de 1 s (SHOULD); algoritmo de Karn; duplicación del RTO; máximo ≥ 60 s | — |
| 4 | RFC 9438, «CUBIC for Fast and Long-Distance Networks», agosto de 2023 | IETF | https://www.rfc-editor.org/rfc/rfc9438.html | Estándar; obsoleta RFC 8312 y actualiza RFC 5681; ventana cúbica respecto al tiempo desde el último evento de congestión; β_cubic = 0,7; C = 0,4; convergencia rápida; región compatible con Reno | — |
| 5 | RFC 6928, «Increasing TCP's Initial Window», abril de 2013 | IETF | https://www.rfc-editor.org/rfc/rfc6928.html | Experimental; IW ≤ min(10×MSS, max(2×MSS, 14600)); motivación (tráfico web); advertencias (desbordes en routers con poco búfer, RTO espurio) | Es un documento experimental |
| 6 | tcp(7) | Linux man-pages | https://man7.org/linux/man-pages/man7/tcp.7.html | Parámetros `/proc/sys/net/ipv4/*` y sus valores por defecto; opciones de socket `TCP_NODELAY`, `TCP_CORK`, `TCP_KEEPIDLE`, `TCP_USER_TIMEOUT`, `TCP_INFO` | `TCP_NODELAY` y otras no tienen "valor por defecto" propio en la página; los valores del kernel pueden diferir según versión y distribución |
| 7 | ss(8) | Linux man-pages (iproute2) | https://man7.org/linux/man-pages/man8/ss.8.html | Opciones `-t -u -l -n -p -i -e -o -s -H`; filtros de estado; campos de `-i`: rto, rtt, cwnd, ssthresh, mss, bytes_acked, bytes_received, segs_out, segs_in, send | **No** explica Recv-Q/Send-Q en la página; **no** lista `retrans` ni `bytes_sent` entre los campos de `-i` |
| 8 | tcpdump(1) | tcpdump.org | https://www.tcpdump.org/manpages/tcpdump.1.html | Opciones `-i -n -c -w -r -s -v -X -A`; letras de banderas TCP; filtros con `tcp[tcpflags]` y `tcp[13]` | `-nn` no figura en esa página (se omite o se describe sin cita) |

## Observaciones

- No se ejecutó ningún comando de red en este equipo para el artículo (el objetivo del artículo es explicar y los comandos son de Linux). Los ejemplos son instrucciones, no capturas.
- Conocimiento general (señalado): significado de Recv-Q y Send-Q, BBR, `sysctl`, comportamiento exacto de los valores por defecto del kernel de cada distribución.
