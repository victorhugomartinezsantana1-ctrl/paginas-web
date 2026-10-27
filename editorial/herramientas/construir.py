#!/usr/bin/env python3
"""Construye las páginas publicadas de los artículos editoriales.

Entrada, por artículo:  editorial/articulos/ART-xxx/meta.json  y  cuerpo.html
Salida:                  articulos/<slug>.html, tarjeta en index.html y sitemap.xml

Uso:
  python construir.py ART-001 ART-002        # construye esos artículos
  python construir.py --todos                # construye todos los que tengan meta.json
  python construir.py --recalcular-lecturas  # corrige "min de lectura" de TODAS las páginas y tarjetas

El cuerpo (cuerpo.html) es un fragmento HTML con <h2>, <h3>, <p>, <ul>, <ol>, <table>,
<div class="alert|alert-success|alert-danger"> y bloques de código:
    <pre data-lang="python"><code>código SIN escapar</code></pre>
El constructor escapa el código, envuelve los bloques, genera los ids, el índice, los
huecos de anuncios y los artículos relacionados. Las referencias van en
<h2 id="referencias">Referencias</h2> al final (no cuentan para el recuento de palabras).
"""
import argparse
import html
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
EDITORIAL = RAIZ / "editorial"
PUBLICADOS = RAIZ / "articulos"
sys.path.insert(0, str(AQUI))
from contar_palabras import contar  # noqa: E402

# Cambiar aquí (y en robots.txt/sitemap) cuando el sitio tenga dominio propio.
SITE_URL = "https://kind-mud-077d38b10.1.azurestaticapps.net"
PALABRAS_POR_MINUTO = 200
BARRAS = {
    "indigo": "bg-accent", "ambar": "bg-amber-400", "morado": "bg-purple-500",
    "rosa": "bg-rose-600", "azul": "bg-blue-500", "verde": "bg-emerald-500", "cielo": "bg-sky-500",
    "naranja": "bg-orange-500", "turquesa": "bg-teal-500",
}

BLOQUE = """<div class="code-block not-prose">
          <div class="code-block__bar">
            <span>{lang}</span>
            <button type="button" class="code-block__copy">copiar</button>
          </div>
          <pre><code>{codigo}</code></pre>
        </div>"""

ANUNCIO = """
        <!-- AdSense Slot: {nombre} -->
        <aside class="ad-slot not-prose" aria-label="Publicidad">
          <span class="ad-label">publicidad</span>
          <!-- <ins class="adsbygoogle"
               style="display:block; text-align:center;"
               data-ad-layout="in-article"
               data-ad-format="fluid"
               data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
               data-ad-slot="{slot}"></ins>
          <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script> -->
        </aside>

"""

ANUNCIO_FINAL = ANUNCIO.format(nombre="article-bottom", slot="0000000004")


def slugify(texto):
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = html.unescape(texto)
    texto = re.sub(r"^\s*\d+[.)]\s*", "", texto)
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto[:40].strip("-") or "seccion"


def preparar_cuerpo(cuerpo):
    """Envuelve el código, pone ids a los <h2> e inserta los anuncios. Devuelve (html, titulos)."""

    def envolver(m):
        lang = m.group(1) or "texto"
        # Tolerante: acepta código escrito sin escapar o ya escapado (&lt; &gt; &amp;)
        codigo = html.escape(html.unescape(m.group(2).strip("\n")), quote=False)
        return BLOQUE.format(lang=html.escape(lang), codigo=codigo)

    cuerpo = re.sub(r'<pre(?: data-lang="([^"]*)")?><code>(.*?)</code></pre>', envolver, cuerpo, flags=re.S)

    # Las tablas anchas se desplazan dentro de su contenedor en lugar de desbordar la página móvil
    cuerpo = re.sub(r"<table>", '<div class="tabla-scroll"><table>', cuerpo)
    cuerpo = re.sub(r"</table>", "</table></div>", cuerpo)

    titulos = []

    def poner_ids(m):
        sid = m.group(1) or "%d-%s" % (len(titulos) + 1, slugify(m.group(2)))
        titulos.append((sid, re.sub(r"<[^>]+>", "", m.group(2)).strip()))
        return '<h2 id="%s">%s</h2>' % (sid, m.group(2))

    cuerpo = re.sub(r'<h2(?: id="([^"]+)")?>(.*?)</h2>', poner_ids, cuerpo, flags=re.S)
    ids = [t[0] for t in titulos]
    assert len(ids) == len(set(ids)), "ids de <h2> duplicados: %s" % ids

    # Anuncios: tras la primera sección, hacia el 50 % y el 75 % del texto, y antes de las referencias.
    pos = [m.start() for m in re.finditer(r"<h2 id=", cuerpo)]
    n = len(pos)
    cuerpo_idx = [i for i, t in enumerate(titulos) if t[0] != "referencias"]
    n_c = len(cuerpo_idx)
    puntos = []
    if n_c >= 3:
        puntos.append((cuerpo_idx[1], "article-top", "0000000002"))
    if n_c >= 6:
        puntos.append((cuerpo_idx[n_c // 2], "article-middle", "0000000003"))
    if n_c >= 10:
        puntos.append((cuerpo_idx[(3 * n_c) // 4], "article-late", "0000000006"))
    inserts = [(pos[i], ANUNCIO.format(nombre=nom, slot=slot)) for i, nom, slot in puntos]
    if "referencias" in ids:
        inserts.append((pos[ids.index("referencias")], ANUNCIO_FINAL))
    else:
        cuerpo = cuerpo + "\n" + ANUNCIO_FINAL
    for p, bloque in sorted(inserts, reverse=True):
        cuerpo = cuerpo[:p] + bloque.lstrip("\n") + "        " + cuerpo[p:]
    return cuerpo.strip("\n"), titulos


def datos_publicados(slug):
    f = PUBLICADOS / (slug + ".html")
    if not f.exists():
        return None
    s = f.read_text(encoding="utf-8")
    tag = re.search(r'<p class="text-xs text-warm mb-3">\[(.*?)\]</p>', s)
    h1 = re.search(r"<h1[^>]*>\s*(.*?)\s*</h1>", s, re.S)
    if not (tag and h1):
        return None
    return {"slug": slug, "tag": tag.group(1), "titulo": h1.group(1)}


def html_relacionados(slugs):
    out = []
    for s in slugs:
        d = datos_publicados(s)
        if not d:
            print("  aviso: relacionado no encontrado:", s)
            continue
        out.append(
            '          <li><a href="/articulos/%s.html" class="block border border-line bg-surface rounded-lg p-4 hover:border-accent">\n'
            '            <span class="text-xs text-warm">[%s]</span>\n'
            '            <span class="block mt-1 text-head font-bold leading-snug">%s</span>\n'
            "          </a></li>" % (d["slug"], d["tag"], d["titulo"])
        )
    return "\n".join(out)


def construir(art_id):
    carpeta = EDITORIAL / "articulos" / art_id
    meta = json.loads((carpeta / "meta.json").read_text(encoding="utf-8"))
    cuerpo_src = (carpeta / "cuerpo.html").read_text(encoding="utf-8")
    palabras = contar(carpeta / "cuerpo.html", fragmento=True)["palabras"]
    minutos = max(1, math.ceil(palabras / PALABRAS_POR_MINUTO))

    cuerpo, titulos = preparar_cuerpo(cuerpo_src)
    toc = "\n".join(
        '            <li><a href="#%s" class="text-muted hover:text-accent">%s</a></li>' % (sid, t) for sid, t in titulos
    )
    toc_inline = (
        '<details class="mb-8 rounded-lg border border-line bg-surface p-4 lg:hidden">\n'
        '        <summary class="cursor-pointer font-semibold text-head">Contenido del artículo</summary>\n'
        '        <ol class="mt-3 list-decimal space-y-1.5 pl-5 text-sm">\n%s\n        </ol>\n      </details>'
        % "\n".join('          <li><a href="#%s" class="text-accent hover:underline">%s</a></li>' % (sid, t) for sid, t in titulos)
    )
    slug = meta["slug"]
    ruta = "articulos/%s.html" % slug
    titulo_plano = re.sub(r"<[^>]+>", "", meta["titulo"])
    ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": titulo_plano,
        "description": meta["descripcion"],
        "inLanguage": "es",
        "datePublished": meta["fecha"],
        "dateModified": meta["fecha"],
        "wordCount": palabras,
        "keywords": ", ".join([meta["palabra_clave"]] + meta.get("secundarias", [])),
        "author": {"@type": "Person", "name": meta.get("autor", "Victor Martinez")},
        "publisher": {"@type": "Organization", "name": "devlog"},
        "mainEntityOfPage": "%s/%s" % (SITE_URL, ruta),
    }
    jsonld = '\n  <script type="application/ld+json">\n  %s\n  </script>\n' % json.dumps(ld, ensure_ascii=False, indent=2).replace("\n", "\n  ")

    plantilla = (AQUI / "plantilla_articulo.html").read_text(encoding="utf-8")
    pagina = plantilla
    reemplazos = {
        "TITLE": html.escape(titulo_plano, quote=True),
        "DESC": html.escape(meta["descripcion"], quote=True),
        "HEAD_EXTRA": '  <link rel="canonical" href="%s/%s">' % (SITE_URL, ruta),
        "SITE": SITE_URL,
        "PATH": ruta,
        "DATE": meta["fecha"],
        "JSONLD": jsonld,
        "TAG": meta["etiqueta"],
        "H1": meta["titulo"],
        "SUBTITLE": meta["descripcion"],
        "MIN": str(minutos),
        "AUTOR": meta.get("autor", "Victor Martinez"),
        "BODY": cuerpo,
        "RELATED": html_relacionados(meta.get("relacionados", [])),
        "TOC": toc,
        "TOC_INLINE": toc_inline,
    }
    for k, v in reemplazos.items():
        pagina = pagina.replace("@@%s@@" % k, v)
    assert "@@" not in pagina, "quedan marcadores sin sustituir"
    (PUBLICADOS / (slug + ".html")).write_text(pagina, encoding="utf-8", newline="\n")
    print("  %s -> articulos/%s.html  (%d palabras, %d min)" % (art_id, slug, palabras, minutos))
    return meta, palabras, minutos


def tarjeta(meta, minutos):
    barra = BARRAS[meta.get("barra", "indigo")]
    titulo = re.sub(r"<[^>]+>", "", meta["titulo"])
    return f'''        <article class="group relative flex flex-col border border-line bg-surface rounded-lg overflow-hidden shadow-sm hover:border-accent hover:shadow-md transition">
          <div class="h-1 {barra}"></div>
          <div class="p-5 flex flex-col flex-1">
            <div class="flex items-center justify-between text-xs text-muted mb-3">
              <span class="text-warm">[{meta["etiqueta"]}]</span>
              <time datetime="{meta["fecha"]}">{meta["fecha"]}</time>
            </div>
            <h3 class="text-lg font-bold text-head leading-snug group-hover:text-accent">
              <a href="/articulos/{meta["slug"]}.html" class="after:absolute after:inset-0">{titulo}</a>
            </h3>
            <p class="mt-3 text-sm text-ink/80 leading-relaxed flex-1">
              {meta["descripcion"]}
            </p>
            <p class="mt-4 text-xs text-muted">⏱ {minutos} min de lectura</p>
          </div>
        </article>
'''


def actualizar_indice(nuevas):
    """nuevas: lista de (meta, minutos). Sustituye o añade tarjetas y reordena por fecha."""
    idx = RAIZ / "index.html"
    s = idx.read_text(encoding="utf-8")
    g0 = s.index('<div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">')
    g1 = s.index("    </section>", g0)
    existentes = re.findall(r'        <article class="group.*?</article>\n', s[g0:g1], flags=re.S)
    tarjetas = {}
    orden = {}
    for b in existentes:
        slug = re.search(r'href="/articulos/([^"]+)\.html"', b).group(1)
        tarjetas[slug] = b
        orden[slug] = 10**6
    for meta, minutos in nuevas:
        tarjetas[meta["slug"]] = tarjeta(meta, minutos)
        orden[meta["slug"]] = int(meta["id"].split("-")[1])

    def clave(slug):
        fecha = re.search(r'datetime="([\d-]+)"', tarjetas[slug]).group(1)
        return (fecha, -orden[slug])

    ordenados = sorted(tarjetas, key=clave, reverse=True)
    grid = '<div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">\n\n' + "\n".join(tarjetas[x] for x in ordenados) + "      </div>\n"
    idx.write_text(s[:g0] + grid + s[g1:], encoding="utf-8", newline="\n")
    print("  index.html: %d tarjetas" % len(ordenados))


def actualizar_sitemap():
    urls = [("", "")]
    for f in sorted(PUBLICADOS.glob("*.html")):
        m = re.search(r'datePublished": "(\d{4}-\d{2}-\d{2})"', f.read_text(encoding="utf-8"))
        urls.append(("articulos/%s.html" % f.stem, m.group(1) if m else ""))
    urls += [("privacidad.html", ""), ("contacto.html", "")]
    hoy = max(d for _, d in urls if d)
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, d in urls:
        xml.append("  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>" % (SITE_URL, p, d or hoy))
    xml.append("</urlset>")
    (RAIZ / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8", newline="\n")
    print("  sitemap.xml: %d URLs" % len(urls))


def recalcular_lecturas():
    """Sustituye los 'N min de lectura' de páginas y tarjetas por valores calculados del texto real."""
    idx = RAIZ / "index.html"
    s = idx.read_text(encoding="utf-8")
    cambios = []
    for f in sorted(PUBLICADOS.glob("*.html")):
        palabras = contar(f)["palabras"]
        minutos = max(1, round(palabras / PALABRAS_POR_MINUTO))
        t = f.read_text(encoding="utf-8")
        t2 = re.sub(r"⏱ \d+ min de lectura", "⏱ %d min de lectura" % minutos, t)
        if t2 != t:
            f.write_text(t2, encoding="utf-8", newline="\n")
        # tarjeta correspondiente
        patron = re.compile(r'(href="/articulos/%s\.html".*?⏱ )\d+( min de lectura)' % re.escape(f.stem), re.S)
        s, n = patron.subn(lambda m: m.group(1) + str(minutos) + m.group(2), s, count=1)
        cambios.append((f.stem, palabras, minutos, n))
    idx.write_text(s, encoding="utf-8", newline="\n")
    for slug, p, m, n in cambios:
        print("  %-40s %5d palabras -> %2d min %s" % (slug, p, m, "" if n else "(sin tarjeta)"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--recalcular-lecturas", action="store_true")
    a = ap.parse_args()
    if a.recalcular_lecturas:
        recalcular_lecturas()
        sys.exit(0)
    ids = a.ids
    if a.todos:
        ids = sorted(p.parent.name for p in (EDITORIAL / "articulos").glob("ART-*/meta.json"))
    if not ids:
        ap.error("indica ids de artículo o --todos")
    resultados = [construir(i) for i in ids]
    actualizar_indice([(m, mins) for m, _, mins in resultados])
    actualizar_sitemap()
    print("ok")
