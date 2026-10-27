# Auditoría — ART-008 DNS de extremo a extremo

Fecha: 2026-10-27 · Palabras editoriales: 5.712 · Fuentes registradas: 10

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Tres componentes, zonas, delegación con NS, CNAME sin otros datos, resolución iterativa/recursiva, caché | RFC 1034 (100.000 de 128.880 caracteres) | Verificado |
| UDP de 512 octetos, bit TC, prefijo de 2 bytes en TCP, RCODE 0–5, límites 63/255, tipos y campos de SOA | RFC 1035 (100.000 de 125.646) | Verificado |
| Caché negativa: TTL = mínimo entre SOA MINIMUM y TTL del SOA; 1–3 h bien, > 1 día problemático | RFC 2308 | Verificado (cifras como orientación) |
| EDNS(0): OPT tipo 41, < 512 se trata como 512, 4096 «buen compromiso», 1280–1410 razonable | RFC 6891 | Verificado |
| TCP obligatorio en implementaciones generales | RFC 7766 | Verificado |
| DoH: `application/dns-message`, GET/POST, 65.535 bytes, HTTP/2 | RFC 8484 | Verificado |
| DNSSEC: autenticación de origen e integridad; sin confidencialidad ni protección DoS; RRSIG/DNSKEY/DS/NSEC; estados Secure/Insecure/Bogus/Indeterminate; AD y CD | RFC 4033 | Verificado |
| `resolv.conf`: 3 servidores, `timeout` 5 s (máx. 30), `attempts` 2 (máx. 5), `ndots` 1, lista de búsqueda | resolv.conf(5) | Verificado |
| Pod con `ndots:5` y lista de búsqueda del clúster | Kubernetes, DNS for Services and Pods | Verificado; el multiplicador de consultas (hasta 8 = 4 nombres × A/AAAA) es cuenta propia señalada como tal |
| Opciones de `dig` | Documentación de BIND 9 (100.000 de 388.160) | Verificado en la parte leída |

### Correcciones hechas durante la revisión

1. Se eliminó que la RFC 1034 «sugería valores del orden de días» para el TTL: no estaba registrado en las notas de la fuente.
2. Se quitó el detalle de «dos servidores raíz y dos del dominio local» en la lista de arranque (SBELT): la cifra no estaba verificada; queda «servidores raíz y del dominio local».
3. Se quitó que `dig +trace` «desactiva la recursión»: no figuraba en las notas de la fuente.
4. Ya estaban señalados como conocimiento general: AAAA, ALIAS/ANAME, `SERVFAIL` ante datos Bogus, mitigación con punto final, y que la salida de `dig` no se leyó.

### No ejecutado

Ningún comando de `dig` ni el programa de Python se ejecutó. No se muestran salidas.

## Auditoría editorial

- 16 secciones, método de diagnóstico en 7 pasos, 8 errores frecuentes, 7 preguntas frecuentes.
- Enlaza con TLS, Azure Static Web Apps y Kubernetes.

## Auditoría técnica (verificar.py local)

OK — sin errores ni avisos; recuento publicado = aprobado; 10 referencias.
