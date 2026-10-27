# Auditoría — ART-005 Seguridad en GitHub Actions

Fecha: 2026-10-27 · Palabras editoriales: 6.504 · Fuentes registradas: 10

## Auditoría factual

| Afirmación | Respaldo | Resultado |
|---|---|---|
| `GITHUB_TOKEN`: caduca al terminar el trabajo o a la vida máxima (6 h alojados; hasta 24 h de renovación en autoalojados) | concepto github_token | Verificado |
| Recomendación de token de solo lectura por defecto y elevar por trabajo | secure-use | Verificado |
| Ámbitos de `permissions`, valores, "no especificados = none", `read-all`, `write-all`, `{}`, `id-token: write` | workflow-syntax (primeros 100.000 caracteres) | Verificado |
| Secretos: mínimo privilegio, no estructurados, `::add-mask::`, valores derivados, rotar si se filtran | secure-use | Verificado |
| Inyección de scripts y mitigación con variable de entorno intermedia | secure-use | Verificado |
| `pull_request` vs `pull_request_target`; pwn request; `persist-credentials: false`; patrón `workflow_run`; etiquetas y condición de carrera | Security Lab + secure-use | Verificado |
| Etiquetas movibles; fijar por SHA (comprobando que no es de una bifurcación); CODEOWNERS; Dependabot no alerta de acciones fijadas por SHA; Scorecards | secure-use | Verificado |
| Política: bloqueo con `!` y exigencia de SHA (15-08-2025) | changelog | Verificado |
| Lockfiles: `.github/workflows/actions.lock`, `gh actions-lock`, owner_id/repo_id, transitivas; vista previa pública | workflow-dependency-lockfiles | Verificado y marcado como vista previa |
| OIDC: flujo, reclamaciones, `sub`, emisor | concepto OIDC | Verificado |
| OIDC con Azure: `azure/login@v2`, secretos, secretos de entorno, audiencia por defecto | Microsoft Learn | Verificado |
| tj-actions/changed-files: ventanas, v46.0.1, reviewdog, rotación, alerta 18-03-2025 (revisada 26-03) | CISA | Verificado; sin atribuir recomendaciones que la alerta no hace |
| SHAs de `actions/checkout@v7.0.1` y `Azure/static-web-apps-deploy@v1` | API de GitHub, 27-10-2026 | Verificado (valores a fecha de consulta) |

### Correcciones hechas durante la revisión

1. Texto decía "tres acciones" con SHA; en el artículo aparecen dos → corregido.
2. El ejemplo de "cuenta borrada y nombre reutilizado" para justificar `owner_id/repo_id` era razonamiento propio → marcado como tal.
3. Se aclara que CISA **no** recomienda explícitamente fijar por SHA; esa recomendación viene de la guía de GitHub.
4. No se describe el mecanismo del código malicioso más allá de la divulgación de secretos (límite de la fuente).

### No ejecutado

Los flujos YAML son ilustrativos (sin `actionlint` ni validador YAML en el equipo de redacción). Los ajustes propuestos para el flujo de este sitio no se han probado con la acción de Azure.

## Auditoría editorial

- 14 secciones, 9 preguntas frecuentes, lista de verificación de 12 controles, análisis aplicado a este sitio.
- Enlaza con los artículos de caché de Actions, Azure Static Web Apps y Terraform.

## Auditoría técnica (verificar.py local)

OK — sin errores; recuento publicado = aprobado; 10 referencias.
