# Fuentes — ART-009 systemd

Consulta: 2026-10-27. Todas son páginas del manual de systemd en freedesktop.org (rama `latest`); no muestran fecha de publicación y cambian con las versiones.

| # | Fuente | URL | Respalda | Limitaciones |
|---|---|---|---|---|
| 1 | systemd.service(5) | https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html | Valores de `Type=` y cuándo se considera iniciada la unidad; `ExecStart/ExecStop/ExecReload`; `Restart=` y sus valores (por defecto `no`); `RestartSec` (100 ms); `WatchdogSec`; `RemainAfterExit`; SIGTERM y después SIGKILL | La página no da el valor de `TimeoutStartSec` por defecto (se tomó de systemd-system.conf); `KillMode` se remite a systemd.kill(5) |
| 2 | systemd.unit(5) | https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html | Ubicaciones de archivos y precedencia; drop-ins (`foo.service.d/`); `Wants`, `Requires`, `Requisite`, `BindsTo`, `PartOf`, `Conflicts`; `Before`/`After` (el orden es independiente de los requisitos); `[Install]` y `systemctl enable`; plantillas e instancias (`%i`) | No describe `systemctl edit`; se leyeron 100.000 de 107.832 caracteres |
| 3 | systemd.exec(5) | https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html | Directivas de aislamiento: `User`, `DynamicUser`, `NoNewPrivileges`, `ProtectSystem`, `ProtectHome`, `PrivateTmp`, `PrivateDevices`, `ProtectKernelTunables/Modules`, `ProtectControlGroups`, `ProtectClock`, `RestrictAddressFamilies`, `RestrictNamespaces`, `LockPersonality`, `MemoryDenyWriteExecute`, `SystemCallFilter`, `@system-service`, `SystemCallArchitectures`, `RestrictSUIDSGID`, `CapabilityBoundingSet`, `AmbientCapabilities`, `ReadWritePaths`/`ReadOnlyPaths`, `EnvironmentFile` | Se leyeron los caracteres 0–200.000 de 244.377; falta el final. El inicio de `PrivateDevices=` se recuperó entre las dos lecturas; la lista completa de llamadas de `@system-service` no se leyó |
| 4 | systemd.timer(5) | https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html | Temporizadores de reloj (`OnCalendar`) y monótonos; `Persistent` (solo con `OnCalendar`); `AccuracySec` (1 min); `RandomizedDelaySec`; `Unit=`; `WakeSystem` | No compara con cron |
| 5 | journalctl(1) | https://www.freedesktop.org/software/systemd/man/latest/journalctl.html | Opciones `-u -b -f -n -p --since --until -o -k -r --disk-usage --vacuum-size --vacuum-time -x`; el diario guarda entradas estructuradas | — |
| 6 | systemd-system.conf(5) | https://www.freedesktop.org/software/systemd/man/latest/systemd-system.conf.html | `DefaultTimeoutStartSec` y `DefaultTimeoutStopSec` (90 s), `DefaultRestartSec` (100 ms), `DefaultStartLimitIntervalSec` (10 s), `DefaultStartLimitBurst` (5), `DefaultTasksMax` (15 %); ubicaciones y precedencia de los drop-ins | — |
| 7 | systemd-analyze(1) | https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html | Subcomandos `security` (puntuación de 0,0 a 10,0), `blame`, `critical-chain`, `verify`, `calendar` | — |

## Verificaciones adicionales de la auditoría (27-10-2026)

- systemd-analyze(1): confirmado que `blame` no muestra servicios `Type=simple` («considers such services to be started immediately»); `security` puntúa de 0,0 a 10,0 y una exposición alta indica poco aislamiento aplicado; `critical-chain` usa «@» para el instante de activación y «+» para la duración; `calendar --iterations` por defecto 1; `verify` detecta secciones/directivas desconocidas, dependencias obligatorias ausentes, páginas de manual de `Documentation=` no encontradas y órdenes de `ExecStart=` ausentes o no ejecutables.
- systemd.service(5): confirmado que `TimeoutStartSec=` toma `DefaultTimeoutStartSec=` salvo en `Type=oneshot`, donde el plazo está desactivado por defecto (la página no dice literalmente «infinito»); `Restart=no`, `RestartSec` 100 ms, `WatchdogSec=0`, terminación con `SIGABRT` o `WatchdogSignal=`, `Type=idle` con límite de 5 s.

## Observaciones

- No se ejecutó ningún comando de systemd (el equipo de redacción es Windows). Las unidades de ejemplo están escritas con la sintaxis documentada y se marcan como no probadas; no se muestran salidas.
- Conocimiento general (señalado): `systemctl edit` y `daemon-reload`, `reset-failed`, `systemctl cat`/`show`/`list-dependencies`, tipos de unidad distintos de service y timer, comparación con cron, uso de cgroups por systemd.
