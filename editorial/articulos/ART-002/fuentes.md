# Fuentes — ART-002 Contenedores Linux por dentro

Consulta: 2026-10-27. Ninguna de estas páginas muestra fecha de publicación (se anota "no indicada"; las páginas man y la documentación del kernel son documentos vivos).

| # | Fuente | Organismo | URL | Respalda | Limitaciones |
|---|---|---|---|---|---|
| 1 | namespaces(7) | Linux man-pages (man7.org) | https://man7.org/linux/man-pages/man7/namespaces.7.html | Los 8 tipos de namespace y sus flags `CLONE_NEW*`; versiones de kernel (cgroup 4.6, IPC 3.0, net 3.0, mount 3.8, PID 3.8, time 5.6, user 3.8, UTS 3.0); enlaces `/proc/<pid>/ns`; `clone`, `setns`, `unshare`, `ioctl_nsfs`; ciclo de vida; límites `max_*_namespaces` (4.9; time 5.7), error `ENOSPC` | La tabla de la página no lista versiones; se tomaron de la sección /proc |
| 2 | Control Group v2 | Documentación del kernel (docs.kernel.org) | https://docs.kernel.org/admin-guide/cgroup-v2.html | Jerarquía unificada; regla "no internal process"; `cgroup.subtree_control`; `memory.max/high/min/low/current/events/oom.group`; `cpu.max` (por defecto `max 100000`), `cpu.weight` (1–10000, por defecto 100), `cpu.stat`, `io.max`, `pids.max`, PSI | La página es muy larga; se leyeron los primeros 100.000 caracteres (el resto no) |
| 3 | seccomp(2) | Linux man-pages | https://man7.org/linux/man-pages/man2/seccomp.2.html | Modos STRICT y FILTER; requisito de `no_new_privs` o `CAP_SYS_ADMIN`; acciones de retorno y su precedencia; `struct seccomp_data`; comprobación de `arch`; lista blanca recomendada; Linux 3.17 | — |
| 4 | capabilities(7) | Linux man-pages | https://man7.org/linux/man-pages/man7/capabilities.7.html | Los 5 conjuntos (permitted, effective, inheritable, bounding, ambient); capacidades clave; `CAP_SYS_ADMIN` sobrecargada y capacidades separadas de ella | — |
| 5 | user_namespaces(7) | Linux man-pages | https://man7.org/linux/man-pages/man7/user_namespaces.7.html | Formato de `uid_map`/`gid_map`; capacidades dentro del namespace; creación sin privilegios desde 3.8; límite de 32 niveles; `setgroups`; límites de seguridad | — |
| 6 | OCI Runtime Specification, config-linux.md | Open Container Initiative (GitHub) | https://raw.githubusercontent.com/opencontainers/runtime-spec/main/config-linux.md | Campos de configuración Linux: `namespaces`, `uidMappings`, `cgroupsPath`, `resources`, `seccomp`, `maskedPaths`, `readonlyPaths`, `rootfsPropagation`, `sysctl` | Se consultó la rama `main` (puede cambiar) |
| 7 | About cgroup v2 | Kubernetes (kubernetes.io) | https://kubernetes.io/docs/concepts/architecture/cgroups/ | cgroup v2 estable desde Kubernetes 1.25; requisitos (kernel 5.8, containerd 1.4, cri-o 1.20, driver systemd); comando de comprobación; cgroup v1 obsoleto en 1.35 y kubelet que no arranca en v1 por defecto (`failCgroupV1`) | Los últimos 417 caracteres no se leyeron |
| 8 | Seccomp security profiles for Docker | Docker Docs | https://docs.docker.com/engine/security/seccomp/ | Perfil por defecto: lista blanca con acción `SCMP_ACT_ERRNO`; bloquea unas 44 de más de 300 llamadas; ejemplos de llamadas bloqueadas; `--security-opt seccomp=...` | No se cita el CVE que menciona la página (no verificado de forma independiente) |
| 9 | Running containers (runtime privilege and capabilities) | Docker Docs | https://docs.docker.com/engine/containers/run/ | 14 capacidades por defecto; `--cap-add`, `--cap-drop`, `--privileged`, `--device`; `--memory`, `--memory-swap`, `--cpus` | No cubre `--pids-limit` |

## Observaciones

- No se ejecutó ningún comando de este artículo (sin Linux ni daemon de Docker en el equipo de redacción). Las salidas que aparecen en el artículo son únicamente las que reproducen el formato descrito por las páginas man; el texto lo indica.
- Conocimiento general no verificado en estas fuentes (señalado en el texto como tal): papel especial del PID 1, uso de `veth`/puentes en redes de contenedores, `overlayfs` en capas de imagen, `systemd-run`, `capsh`.
