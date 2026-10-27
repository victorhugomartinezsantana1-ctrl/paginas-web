# Auditoría — ART-002 Contenedores Linux por dentro

Fecha: 2026-10-27 · Palabras editoriales: 7.122 · Fuentes registradas: 9

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| 8 tipos de namespace y flags; versiones (3.0, 3.8, 4.6, 5.6) | namespaces(7) | Verificado en fuente |
| Límites `max_*_namespaces` desde 4.9 (time 5.7), `ENOSPC`, valores por defecto | namespaces(7) | Verificado |
| uid_map: formato, escritura única, 340 líneas (4.16), CAP_SETFCAP (5.12), setgroups (3.19) | user_namespaces(7) | Verificado |
| cgroup v2: archivos y valores por defecto de memoria, CPU, PIDs, E/S, PSI | docs.kernel.org (primeros 100.000 caracteres) | Verificado |
| seccomp: modos, precedencia, no_new_privs, Linux 3.17 / 4.14 / 5.0 | seccomp(2) | Verificado |
| Docker: 14 capacidades por defecto, `--privileged`, ~44 de 300+ syscalls bloqueadas, ejemplos | Docs de Docker | Verificado |
| Kubernetes: cgroup v2 estable en 1.25, kernel 5.8, cgroup v1 obsoleto en 1.35, `failCgroupV1` | kubernetes.io | Verificado |
| Campos de la sección Linux de OCI | runtime-spec (rama main) | Verificado |

### Correcciones hechas durante la revisión

1. Curiosidad histórica sobre `CLONE_NEWNS` presentada como hecho → marcada como conocimiento general.
2. Atribución a "la documentación de Docker" de la idea de capas de imagen (no consultada) → reformulada.
3. Usos de los namespaces de tiempo (migración de contenedores): no respaldados → eliminados; se indica que no se contrastaron.
4. Irreversibilidad de los filtros seccomp: no contrastada en la página consultada → señalada como detalle conocido no contrastado.
5. No se cita el identificador CVE que menciona la página de Docker (no verificado de forma independiente).

### Marcado como conocimiento general (no verificado en las fuentes)

PID 1 y señales/zombis, `veth`/puentes en redes de contenedores, `overlayfs`, `systemd-run`, `capsh`, jerarquía Docker/containerd/runc, alternativas de aislamiento más fuerte.

### No ejecutado

Ningún comando se ejecutó (sin Linux ni daemon de Docker en el equipo de redacción). El artículo lo declara en la introducción y no incluye salidas inventadas.

## Auditoría editorial

- 15 secciones, 9 preguntas frecuentes, lista de verificación de endurecimiento, tablas de namespaces, memoria y capacidades.
- Enlaza con los artículos de Docker multi-stage y Kubernetes ya publicados.

## Auditoría técnica (verificar.py local)

OK — sin errores; recuento publicado = aprobado; 9 referencias.
