# Auditoría — ART-001 Git por dentro

Fecha: 2026-10-27 · Palabras editoriales: 5.790 (mínimo 5.000) · Fuentes registradas: 7

## Auditoría factual

| Afirmación del artículo | Respaldo | Resultado |
|---|---|---|
| Cabecera `<tipo> <tamaño>\0` + zlib + ruta `.git/objects/xx/…` | Pro Git (fuente 1) y laboratorio (SHA-1 calculado con Python = `24db42b…`; objeto descomprimido = `b'blob 11\x00hola mundo\n'`) | Verificado dos veces |
| Modos de tree 100644/100755/120000/040000 | Pro Git | Verificado en fuente |
| gc.auto = 6700, autoPackLimit = 50, reflog 90/30 días, prune 2 semanas, aggressive window 250 / depth 50 | `git-gc` (fuente 6) | Verificado en fuente |
| Pro Git redondea a "unos 7.000" | Pro Git vs `git-gc` | Discrepancia señalada en el texto |
| Delta: versión nueva completa, antigua como delta de 18 bytes | Laboratorio (`verify-pack`) | Verificado por ejecución |
| Reflog, `reset --hard HEAD@{1}`, `fsck` colgante, `prune=now` (6→3 objetos) | Laboratorio | Verificado por ejecución |
| Merge con dos padres; etiqueta anotada; `packed-refs` con línea `^` | Laboratorio | Verificado por ejecución |
| SHA-256: 64 hex, `objectformat=sha256`, versión de formato 1 | Laboratorio + documento de transición | Verificado |
| "SHA-256 será el predeterminado" | La fuente **no** lo dice | El artículo NO lo afirma (hay un aviso explícito) |

### Correcciones hechas durante la revisión

1. Atribución a "la documentación" de que `reflog`/`ORIG_HEAD` deshacen un rebase: no estaba en las fuentes → reformulada como mecanismo general.
2. Explicación causal de por qué la base del delta fue la versión antigua en el primer intento de laboratorio: no verificada → reescrita; el intento se descartó por contaminación CRLF.
3. Errata "La columnas" → "Las columnas".
4. Medición de packfile repetida con LF para eliminar el artefacto de saltos de línea.

### Pendiente / no verificado

- Heurísticas internas de elección de base de deltas: solo observación del laboratorio, no regla.
- `filter-branch`: se describe lo que dice el libro; no se compara con alternativas modernas.

## Auditoría editorial

- Estructura: introducción, puntos clave, 14 secciones, preguntas frecuentes (8), conclusión, referencias.
- Sin párrafos de relleno detectados; cada sección aporta un concepto o un experimento.
- Diferenciación: complementa (no repite) el artículo de rebase interactivo existente (enlazado).
- Gramática y ortografía: revisión manual completa; una errata corregida.

## Auditoría técnica (verificar.py local)

OK — HTML bien formado, un `<h1>`, jerarquía h2/h3 correcta, ids únicos, canonical correcto, JSON-LD válido, sin enlaces internos rotos, 7 referencias, aparece en la cuadrícula y en sitemap.xml; recuento publicado = recuento aprobado.
