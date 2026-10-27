# Auditoría — ART-009 systemd

Fecha: 2026-10-27 · Palabras editoriales: 5.539 · Fuentes registradas: 7

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| Valores de `Type=`, `Restart=` (por defecto `no`), `RestartSec` 100 ms, `WatchdogSec`, `Type=idle` con 5 s | systemd.service(5) | Verificado (y comprobado de nuevo) |
| Valores por defecto 90 s de arranque/parada, 10 s y 5 de límite de arranque, drop-ins y prefijos | systemd-system.conf(5) | Verificado |
| Ubicaciones y precedencia, drop-ins, `Wants`/`Requires`/`Requisite`/`BindsTo`/`PartOf`/`Conflicts`, orden independiente, `[Install]`, plantillas | systemd.unit(5) (100.000 de 107.832) | Verificado en la parte leída |
| Directivas de aislamiento y su semántica | systemd.exec(5) (200.000 de 244.377) | Verificado en la parte leída; la lista completa de `@system-service` no se leyó |
| Temporizadores: `Persistent`, `AccuracySec` (1 min), `RandomizedDelaySec`, `WakeSystem` | systemd.timer(5) | Verificado |
| Opciones de `journalctl` | journalctl(1) | Verificado |
| `blame` excluye `Type=simple`; puntuación 0,0–10,0; `critical-chain` con «@» y «+»; `calendar --iterations`; alcance de `verify` | systemd-analyze(1) | Verificado de nuevo en la auditoría |
| Aritmética del límite de arranque (4 intervalos de 100 ms ≈ 400 ms) | Cálculo propio | Recalculada |

### Correcciones hechas durante la revisión

1. El texto decía a la vez «un par de segundos» y «medio segundo» para alcanzar el límite de arranque → unificado: «menos de un segundo (unos 400 ms de esperas más el tiempo del proceso)».
2. La comparación con `cron` se declara como valoración propia (las páginas no comparan).
3. Ya estaban señalados como conocimiento general: `systemctl edit` y `daemon-reload`, `StateDirectory=`, que stdout/stderr van al diario, que una unidad activa no se inicia a sí misma.

### No ejecutado

Ninguna unidad se escribió en un equipo con systemd; las unidades son ilustrativas y no hay salidas de comandos.

## Auditoría editorial

- 18 secciones, caso completo cron → temporizador, método de diagnóstico, 8 preguntas frecuentes.
- Enlaza con contenedores, FreeRTOS y (como continuación) observabilidad.

## Auditoría técnica (verificar.py local)

OK — sin errores ni avisos; recuento publicado = aprobado; 7 referencias.
