# Espacio de trabajo editorial

Proyecto: 30 investigaciones originales de ≥ 5.000 palabras para devlog.
Este directorio **no se sirve en la web** (regla 404 en `staticwebapp.config.json`), pero sí se versiona en git.

## Estructura

```
editorial/
  README.md                 este archivo
  auditoria_inicial.md      arquitectura, hallazgos y problemas del sitio
  plan_editorial.csv        plan de 30 artículos (ART-001 … ART-030)
  manifiesto.json           un registro por artículo (estado, palabras, auditorías, verificación pública)
  progreso.json             estado del proyecto y próxima acción (se reanuda desde aquí)
  herramientas/
    contar_palabras.py      recuento reproducible de palabras editoriales
    construir.py            meta.json + cuerpo.html -> articulos/<slug>.html + tarjeta + sitemap
    verificar.py            auditoría técnica local y verificación pública (HTTP real)
    plantilla_articulo.html plantilla de página (estilo del sitio)
  articulos/ART-xxx/
    meta.json               título, slug, etiqueta, fecha, descripción, palabra clave, relacionados
    cuerpo.html             texto del artículo (fragmento HTML; fuente de verdad)
    fuentes.md              fuentes consultadas, con fecha de consulta y afirmaciones que respaldan
    auditoria.md            resultado de la auditoría factual, editorial y técnica
```

La página independiente publicada se genera en `articulos/<slug>.html` (la ruta que sirve el sitio).

## Flujo por artículo

1. Investigar y anotar fuentes en `fuentes.md` (solo fuentes realmente consultadas).
2. Redactar `cuerpo.html` (bloques de código: `<pre data-lang="bash"><code>…</code></pre>`, sin escapar).
3. `python -I editorial/herramientas/construir.py ART-001 …`
4. `python -I editorial/herramientas/verificar.py local ART-001 …`
5. Commit y push a `main` (GitHub Actions despliega en Azure Static Web Apps).
6. `python -I editorial/herramientas/verificar.py publico ART-001 …` y actualizar el manifiesto.

## Recuento de palabras

`contar_palabras.py` cuenta el texto del cuerpo del artículo y excluye código (bloques e inline), anuncios,
índices/navegación, scripts, estilos, la sección `id="referencias"` y toda la plantilla global. Las palabras se
definen como secuencias de letras/dígitos (las compuestas con guion o apóstrofo cuentan como una).
Tiempo de lectura: palabras / 200, redondeado hacia arriba.

## Cambiar de dominio

Cuando el sitio tenga dominio propio: cambiar `SITE_URL` en `construir.py` y `verificar.py`, y reemplazar la URL
actual de `azurestaticapps.net` en `index.html`, `robots.txt`, `sitemap.xml` y las páginas existentes.
