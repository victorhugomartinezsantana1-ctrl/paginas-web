# Auditoría — ART-007 HTTPS y TLS 1.3

Fecha: 2026-10-27 · Palabras editoriales: 5.356 · Fuentes registradas: 5 (más la página de traslado de Mozilla)

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| RFC 8446 (ago. 2018) obsoleta 5077, 5246, 6961; diferencias con TLS 1.2; flujo del handshake; 0-RTT y sus límites; suites; extensiones obligatorias; calendario de claves; marcas de degradación; vida de tickets de 7 días | RFC 8446 (rangos 0–150.000 y 200.000–372.676; el rango 150.000–200.000 no se leyó) | Verificado en la parte leída |
| Número de viajes de ida y vuelta (1 RTT de handshake; ≈ 200 ms / 300 ms con RTT de 100 ms) | Deducido de la Figura 1 de la RFC, con cuenta propia ideal | Marcado como deducción |
| HSTS: `max-age` obligatoria, `includeSubDomains`, solo por canal seguro, sustitución http→https, errores fatales, primera visita, lista precargada, sin `preload` en la RFC | RFC 6797 (100.000 de 115.923 caracteres) | Verificado |
| Perfiles Modern/Intermediate, curvas, vida del certificado (90 días; hasta 366), `max-age=63072000`, TLS 1.2 mínimo según RFC 7525 | TLSRef | Verificado de nuevo en la auditoría |
| Let's Encrypt: 90 días por defecto, 6 días opcional, renovar a 60 y 3 días, «no hay forma de ajustar, no hay excepciones», comodines con DNS-01 | FAQ de Let's Encrypt | Verificado de nuevo en la auditoría |
| SC-081v3: 398 → 47 días, de marzo de 2026 a marzo de 2029; votos 25/0/5 y 4 consumidores (Apple, Google, Microsoft, Mozilla); proponente Clint Wilson (Apple) | Acta del CA/B Forum | Verificado de nuevo en la auditoría |
| Pasos intermedios de 200 y 100 días | Solo fuentes secundarias | Presentados como probables, no como verificados (recuadro del propio texto) |

### Correcciones hechas durante la revisión

1. El acta habla de «datos de validación de SAN» (398 → 10 días); el texto decía «de nombres de dominio» → corregido.
2. La afirmación de que las suites CCM se destinan a entornos con recursos limitados no procede de la RFC → marcada como dato general.
3. Se aclaró que `ChangeCipherSpec` se conserva solo por compatibilidad con intermediarios.
4. Ya constaba como dato general: cadena de certificados y almacenes de confianza, ACME, sintaxis de nginx, comportamiento de `curl -v`.

### No ejecutado

Los comandos de `openssl` y `curl`, el fragmento de nginx y el programa de Python son ilustrativos y no se ejecutaron.

## Auditoría editorial

- 16 secciones, 9 preguntas frecuentes, tabla de suites y tabla de perfiles.
- Enlaza con el artículo de TCP y con el de DNS (siguiente).

## Auditoría técnica (verificar.py local)

OK — sin errores ni avisos; recuento publicado = aprobado; 6 referencias.
