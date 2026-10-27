#!/usr/bin/env python3
"""Auditoría técnica local y verificación pública de los artículos editoriales.

  python verificar.py local ART-001 ART-002 ...     # comprobaciones sobre los archivos
  python verificar.py local --todos
  python verificar.py publico ART-001 ...           # comprueba las URL publicadas (HTTP real)

Devuelve código de salida distinto de 0 si algún artículo no supera las comprobaciones.
No usa dependencias externas.
"""
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
EDITORIAL = RAIZ / "editorial"
sys.path.insert(0, str(AQUI))
from contar_palabras import contar_html  # noqa: E402

SITE_URL = "https://kind-mud-077d38b10.1.azurestaticapps.net"
MINIMO = 5000
VACIAS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SECRETOS = [r"ghp_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY", r"sk-[A-Za-z0-9]{20,}", r"xox[bp]-[A-Za-z0-9-]{10,}"]


class Analizador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila, self.errores, self.ids, self.enlaces, self.titulos, self.imgs = [], [], [], [], [], []
        self.title = None
        self._en_title = False
        self._en_h = None
        self.h1 = []
        self.meta = {}
        self.canonical = None
        self.ld = []
        self._en_ld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VACIAS:
            self.pila.append(tag)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and a.get("href") is not None:
            self.enlaces.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "title":
            self._en_title = True
            self.title = ""
        if tag in ("h1", "h2", "h3", "h4"):
            self._en_h = [tag, ""]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._en_ld = True
            self.ld.append("")

    def handle_endtag(self, tag):
        if tag in VACIAS:
            return
        if self.pila and self.pila[-1] == tag:
            self.pila.pop()
        else:
            self.errores.append("etiqueta de cierre inesperada </%s> (abierta: %s)" % (tag, self.pila[-1] if self.pila else "ninguna"))
            if tag in self.pila:
                while self.pila and self.pila.pop() != tag:
                    pass
        if tag == "title":
            self._en_title = False
        if tag in ("h1", "h2", "h3", "h4") and self._en_h:
            self.titulos.append((self._en_h[0], self._en_h[1].strip()))
            if self._en_h[0] == "h1":
                self.h1.append(self._en_h[1].strip())
            self._en_h = None
        if tag == "script":
            self._en_ld = False

    def handle_data(self, data):
        if self._en_title and self.title is not None:
            self.title += data
        if self._en_h:
            self._en_h[1] += data
        if self._en_ld:
            self.ld[-1] += data


def comprobar_pagina(ruta, esperado):
    """Devuelve (errores, avisos, info) de un archivo HTML publicado."""
    texto = ruta.read_text(encoding="utf-8")
    p = Analizador()
    p.feed(texto)
    err, avi = [], []

    if not texto.lstrip().lower().startswith("<!doctype html>"):
        err.append("falta DOCTYPE")
    if '<html lang="es"' not in texto:
        err.append("falta lang=\"es\"")
    if '<meta charset="UTF-8">' not in texto:
        err.append("falta meta charset UTF-8")
    if "viewport" not in p.meta:
        err.append("falta meta viewport")
    err += p.errores
    if p.pila:
        err.append("etiquetas sin cerrar: %s" % p.pila)
    if not p.title or not p.title.strip():
        err.append("título vacío")
    desc = p.meta.get("description", "")
    if not (50 <= len(desc) <= 175):
        avi.append("meta descripción de %d caracteres" % len(desc))
    if len(p.h1) != 1:
        err.append("hay %d <h1>" % len(p.h1))
    # jerarquía
    nivel = 1
    for t, _ in p.titulos:
        n = int(t[1])
        if n > nivel + 1:
            err.append("salto de encabezados %s tras h%d" % (t, nivel))
        nivel = n
    dup = {i for i in p.ids if p.ids.count(i) > 1}
    if dup:
        err.append("ids duplicados: %s" % sorted(dup))
    if not p.canonical or not p.canonical.startswith(SITE_URL + "/articulos/"):
        err.append("canonical ausente o incorrecto: %s" % p.canonical)
    for bloque in p.ld:
        try:
            json.loads(bloque)
        except Exception as e:  # noqa: BLE001
            err.append("JSON-LD inválido: %s" % e)
    if "TU-DOMINIO" in texto:
        err.append("quedan marcadores TU-DOMINIO")
    for pat in SECRETOS:
        if re.search(pat, texto):
            err.append("posible secreto en el HTML (%s)" % pat)
    for img in p.imgs:
        if not img.get("alt"):
            err.append("imagen sin alt: %s" % img.get("src"))
    # enlaces
    ids = set(p.ids)
    externos = 0
    for h in p.enlaces:
        if h.startswith("#"):
            if h[1:] and h[1:] not in ids:
                err.append("ancla interna inexistente: %s" % h)
        elif h.startswith("/"):
            destino = h.split("#")[0].split("?")[0]
            if destino == "/":
                continue
            f = RAIZ / destino.lstrip("/")
            if not f.exists() and not destino.startswith("/.auth"):
                err.append("enlace interno roto: %s" % h)
        elif h.startswith("http://"):
            avi.append("enlace externo sin https: %s" % h)
        elif h.startswith("https://"):
            externos += 1
    m_refs = re.search(r'<section id="referencias">(.*?)</section>', texto, re.S)
    refs = len(re.findall(r"<li", m_refs.group(1))) if m_refs else 0
    if refs < 5:
        err.append("pocas referencias visibles (%d)" % refs)
    palabras = contar_html(texto)["palabras"]
    if palabras < MINIMO:
        err.append("solo %d palabras editoriales (mínimo %d)" % (palabras, MINIMO))
    if esperado and palabras != esperado:
        err.append("recuento publicado %d != aprobado %d" % (palabras, esperado))
    return err, avi, {"palabras": palabras, "referencias": refs, "externos": externos, "h2": sum(1 for t, _ in p.titulos if t == "h2")}


def comprobar_listado(slug):
    err = []
    idx = (RAIZ / "index.html").read_text(encoding="utf-8")
    if 'href="/articulos/%s.html"' % slug not in idx:
        err.append("no aparece en la cuadrícula de index.html")
    sm = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
    if "/articulos/%s.html" % slug not in sm:
        err.append("no aparece en sitemap.xml")
    return err


def cargar_manifiesto():
    return json.loads((EDITORIAL / "manifiesto.json").read_text(encoding="utf-8"))


def ids_a_revisar(args):
    if "--todos" in args:
        return sorted(p.parent.name for p in (EDITORIAL / "articulos").glob("ART-*/meta.json"))
    return [a for a in args if a.startswith("ART-")]


def cmd_local(args):
    ok = True
    man = {a["id"]: a for a in cargar_manifiesto()["articulos"]}
    for art in ids_a_revisar(args):
        meta = json.loads((EDITORIAL / "articulos" / art / "meta.json").read_text(encoding="utf-8"))
        esperado = (man.get(art) or {}).get("palabras_editoriales")
        f = RAIZ / "articulos" / (meta["slug"] + ".html")
        if not f.exists():
            print("FALLA %s: no existe %s" % (art, f))
            ok = False
            continue
        err, avi, info = comprobar_pagina(f, esperado)
        err += comprobar_listado(meta["slug"])
        estado = "OK   " if not err else "FALLA"
        print("%s %s  %s  palabras=%d h2=%d refs=%d enlaces_ext=%d" % (estado, art, meta["slug"], info["palabras"], info["h2"], info["referencias"], info["externos"]))
        for e in err:
            print("      ERROR:", e)
        for v in avi:
            print("      aviso:", v)
        ok = ok and not err
    return 0 if ok else 1


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "devlog-verificador/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "replace")


def cmd_publico(args):
    ok = True
    man = {a["id"]: a for a in cargar_manifiesto()["articulos"]}
    try:
        _, portada = descargar(SITE_URL + "/")
    except Exception as e:  # noqa: BLE001
        print("No se pudo leer la portada:", e)
        return 1
    for art in ids_a_revisar(args):
        meta = json.loads((EDITORIAL / "articulos" / art / "meta.json").read_text(encoding="utf-8"))
        url = "%s/articulos/%s.html" % (SITE_URL, meta["slug"])
        err = []
        try:
            status, cuerpo = descargar(url)
        except Exception as e:  # noqa: BLE001
            print("FALLA %s %s: %s" % (art, url, e))
            ok = False
            continue
        p = Analizador()
        p.feed(cuerpo)
        titulo_esperado = re.sub(r"<[^>]+>", "", meta["titulo"])
        if status != 200:
            err.append("HTTP %d" % status)
        if not p.h1 or p.h1[0] != titulo_esperado.replace("&", "&") and p.h1[0] != titulo_esperado:
            err.append("h1 distinto: %r" % (p.h1[:1],))
        if titulo_esperado not in (p.title or ""):
            err.append("title distinto: %r" % p.title)
        palabras = contar_html(cuerpo)["palabras"]
        esperado = (man.get(art) or {}).get("palabras_editoriales")
        if esperado and palabras != esperado:
            err.append("palabras públicas %d != aprobadas %d" % (palabras, esperado))
        if palabras < MINIMO:
            err.append("contenido público incompleto: %d palabras" % palabras)
        if 'href="/articulos/%s.html"' % meta["slug"] not in portada:
            err.append("no aparece en la portada pública")
        # enlaces internos públicos
        rotos = []
        for h in sorted({h for h in p.enlaces if h.startswith("/") and not h.startswith("/.auth") and h != "/"}):
            try:
                s, _ = descargar(SITE_URL + h.split("#")[0])
                if s != 200:
                    rotos.append(h)
            except Exception:  # noqa: BLE001
                rotos.append(h)
        if rotos:
            err.append("enlaces internos que no responden 200: %s" % rotos)
        print("%s %s  %s  HTTP=%s palabras=%d" % ("OK   " if not err else "FALLA", art, url, status, palabras))
        for e in err:
            print("      ERROR:", e)
        ok = ok and not err
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("local", "publico"):
        print(__doc__)
        sys.exit(2)
    sys.exit((cmd_local if sys.argv[1] == "local" else cmd_publico)(sys.argv[2:]))
