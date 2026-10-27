# Fuentes — ART-001 Git por dentro

Fecha de consulta de todas las fuentes: 2026-10-27. Ninguna página muestra su fecha de publicación (se anota "no indicada").

| # | Fuente | Organismo / autor | URL | Respalda | Limitaciones |
|---|---|---|---|---|---|
| 1 | Pro Git, "Git Internals - Git Objects" | Scott Chacon y Ben Straub, git-scm.com | https://git-scm.com/book/en/v2/Git-Internals-Git-Objects | Almacén direccionable por contenido; cabecera `<tipo> <tamaño>\0`; compresión zlib; ruta `.git/objects/xx/yyyy…`; modos de tree (100644, 100755, 120000, 040000); campos de un commit | El libro usa SHA-1; los hashes del libro difieren de los reales |
| 2 | Pro Git, "Git Internals - Packfiles" | git-scm.com | https://git-scm.com/book/en/v2/Git-Internals-Packfiles | Objetos sueltos vs packfile; `git gc`; deltas con la versión más nueva como base; `.pack`/`.idx`; columnas de `verify-pack` | No da umbrales numéricos de gc (se tomaron de `git-gc`) |
| 3 | Pro Git, "Git Internals - Git References" | git-scm.com | https://git-scm.com/book/en/v2/Git-Internals-Git-References | `refs/heads`, `refs/tags`, `refs/remotes`; `update-ref`; HEAD como referencia simbólica; `symbolic-ref`; etiquetas ligeras y anotadas | — |
| 4 | Pro Git, "Git Internals - Maintenance and Data Recovery" | git-scm.com | https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery | Reflog; recuperación con `git branch` sobre un SHA; `git fsck --full`; `git prune`; `count-objects -v`; eliminación de objetos grandes | Redondea gc.auto a "unos 7.000 objetos"; los plazos de expiración se tomaron de `git-gc` |
| 5 | Documentación de Git, "hash-function-transition" | Proyecto Git | https://git-scm.com/docs/hash-function-transition | Motivación de pasar de SHA-1 a SHA-256; extensiones `objectFormat`/`compatObjectFormat`; interoperabilidad; elección de SHA-256 en 2018 | Es un documento de diseño: no indica qué está implementado en cada versión ni fija SHA-256 como predeterminado |
| 6 | Documentación de Git, "git-gc" | Proyecto Git | https://git-scm.com/docs/git-gc | Valores por defecto: `gc.auto`=6700, `gc.autoPackLimit`=50, `gc.reflogExpire`=90 días, `gc.reflogExpireUnreachable`=30 días, `gc.pruneExpire`=2 semanas; `--aggressive` (ventana 250, profundidad 50) | — |
| 7 | Laboratorio propio con Git 2.56.0 (Windows) | Autor | `editorial/fuentes/lab_git.md` | Todas las salidas de comandos mostradas en el artículo (hashes, `verify-pack`, reflog, merge, etiquetas, `packed-refs`, SHA-256) | Los hashes dependen de identidad y fechas fijadas; no son los del libro |

## Notas de verificación

- Discrepancia detectada entre fuentes: Pro Git indica "unos 7.000 objetos sueltos" y `git-gc` documenta 6700. El artículo cita 6700 (documentación de referencia).
- El libro afirma que la versión más reciente se guarda completa y la antigua como delta; el laboratorio lo confirma en un archivo que crece (base = versión nueva, delta de 18 bytes).
- No se afirma que SHA-256 sea ya el formato por defecto: la fuente 5 no lo establece.
