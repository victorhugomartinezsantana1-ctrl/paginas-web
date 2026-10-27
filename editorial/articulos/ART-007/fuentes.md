# Fuentes — ART-007 HTTPS y TLS 1.3

Consulta: 2026-10-27.

| # | Fuente | Organismo | URL | Respalda | Limitaciones |
|---|---|---|---|---|---|
| 1 | RFC 8446, «The Transport Layer Security (TLS) Protocol Version 1.3», agosto de 2018 | IETF | https://www.rfc-editor.org/rfc/rfc8446.html | Estándar; obsoleta RFC 5077, 5246 y 6961; diferencias con TLS 1.2 (§1.2); flujo del handshake (§2); 0-RTT y sus límites (§2.3, §8, Apéndice E); suites obligatorias y recomendadas (§9.1) y las cinco del Apéndice B.4; extensiones obligatorias (§9.2); calendario de claves (§7.1); marcas de protección contra degradación (§4.1.3); vida máxima de tickets de 7 días (§4.6.1) | Página de 372.676 caracteres; se leyeron los rangos 0–150.000 y 200.000–372.676 (el rango 150.000–200.000 no). La RFC no enuncia el número de viajes de ida y vuelta: se deduce de la Figura 1. El nombre "DOWNGRD" no figura en la RFC (lo dicen los bytes ASCII) |
| 2 | RFC 6797, «HTTP Strict Transport Security (HSTS)», noviembre de 2012 | IETF | https://www.rfc-editor.org/rfc/rfc6797.html | Estándar; cabecera; `max-age` obligatoria; `includeSubDomains` opcional; solo se acepta por transporte seguro sin errores (§8.1); el agente de usuario sustituye http por https (§8.3); errores de TLS terminan la conexión (§8.4); sin recurso para el usuario (§12.1, no normativa); vulnerabilidad de la primera visita (§14.6); lista precargada de navegadores (§12.3); ejemplo `max-age=15768000 ; includeSubDomains` | La RFC no define una directiva `preload`; se leyeron 100.000 de 115.923 caracteres |
| 3 | TLSRef, «Server-Side TLS» (sucesor de las guías de Mozilla) | Proyecto TLSRef | https://docs.tlsref.org/server-side-tls.html | Perfiles Modern e Intermediate; suites; curvas (X25519MLKEM768, X25519, prime256v1, secp384r1); certificado ECDSA P-256 o RSA 2048; vida 90 días (hasta 366 en Intermediate); `ffdhe2048`; `max-age=63072000`; historial: versión 6.0 quitó el perfil Old | Sin fecha en la página; no trata OCSP stapling ni `includeSubDomains`/`preload`. La página wiki de Mozilla indica que su contenido se trasladó (última edición 11-06-2026) |
| 4 | Let's Encrypt, FAQ | Let's Encrypt (ISRG) | https://letsencrypt.org/docs/faq/ | Validez por defecto de 90 días; certificados de 6 días opcionales; renovar cada 60 días (90 días) o cada 3 días (6 días); los comodines exigen DNS-01 | No menciona certificados de 45 días ni calendario de reducción; solo nombra DNS-01 (los otros desafíos no aparecen en esta página) |
| 5 | Ballot SC-081v3: Introduce Schedule of Reducing Validity and Data Reuse Periods | CA/Browser Forum | https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/ | Votación del 4 al 11-04-2025; propuesta de Clint Wilson (Apple); la validez máxima baja de 398 a 47 días y la reutilización de datos de validación de SAN de 398 a 10 días; reducciones de marzo de 2026 a marzo de 2029; resultado: emisores 25 sí / 0 no / 5 abstenciones, consumidores 4 sí | La página **no** lista los pasos intermedios. Los pasos de 200 días (15-03-2026) y 100 días (15-03-2027) proceden de búsquedas en blogs de proveedores (fuentes secundarias, con discrepancias menores en otros detalles); el artículo los presenta como tales |

## Verificaciones adicionales de la auditoría (27-10-2026)

- Let's Encrypt FAQ: confirmado «There is no way to adjust these lifetimes, there are no exceptions», certificados de 6 días opcionales, renovar cada 60 y cada 3 días, comodines con DNS-01.
- TLSRef: confirmado que el perfil Intermediate cita la RFC 7525 para fijar TLS 1.2 como mínimo; Modern solo TLS 1.3; vida de 90 días (hasta 366 en Intermediate); HSTS `max-age=63072000`.
- CA/B Forum SC-081v3: confirmados los consumidores que votaron a favor (Apple, Google, Microsoft, Mozilla), 25/0/5 en emisores, proponente Clint Wilson (Apple); la página habla de «SAN validation data» (398 → 10 días), no de «datos de validación de dominio»; no menciona pasos de 200 y 100 días.

## Observaciones

- No se ejecutó ningún comando de red ni de OpenSSL para el artículo; los comandos son instrucciones. El único código (Python, biblioteca estándar) está marcado como no ejecutado.
- Conocimiento general (señalado): cadena de certificados y almacenes de confianza, verificación del nombre, protocolo ACME, comportamiento de `curl -v`, sintaxis de nginx.
