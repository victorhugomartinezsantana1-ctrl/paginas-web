#!/usr/bin/env python3
"""Recuento reproducible de palabras editoriales.

Cuenta las palabras del texto de un artículo y EXCLUYE:
  - bloques de código (<pre>) y código en línea (<code>)
  - anuncios (<aside>), navegación/índices (<nav>), <script> y <style>
  - la sección de referencias (todo lo que sigue a un elemento con id="referencias")
  - toda la plantilla global (cabecera, pie, barra lateral): solo se cuenta el cuerpo
    del artículo, es decir, el <div class="prose ..."> de las páginas publicadas

Incluye títulos, párrafos, listas, avisos, tablas y preguntas frecuentes.

Uso:
  python contar_palabras.py pagina1.html pagina2.html          # páginas publicadas
  python contar_palabras.py --fragmento cuerpo.html            # solo el cuerpo (sin plantilla)
  python contar_palabras.py --json ...                         # salida JSON
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PALABRA = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*", re.UNICODE)
EXCLUIR = {"pre", "code", "aside", "nav", "script", "style"}


class Extractor(HTMLParser):
    def __init__(self, fragmento):
        super().__init__(convert_charrefs=True)
        self.fragmento = fragmento
        self.dentro_prose = fragmento
        self.div_prose = 0      # profundidad de <div> dentro del bloque prose
        self.div_flags = []     # por cada <div> abierto: ¿es un bloque de código (se excluye entero)?
        self.excluir = 0
        self.referencias = False
        self.palabras = 0
        self.titulos = {"h2": 0, "h3": 0}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if not self.fragmento and not self.dentro_prose:
            if tag == "div" and "prose" in (a.get("class") or "").split():
                self.dentro_prose = True
                self.div_prose = 1
            return
        if tag == "div":
            es_codigo = "code-block" in (a.get("class") or "").split()
            self.div_flags.append(es_codigo)
            if es_codigo:
                self.excluir += 1   # excluye la etiqueta del lenguaje, el botón y el <pre>
            if not self.fragmento:
                self.div_prose += 1
        if a.get("id") == "referencias":
            self.referencias = True
        if tag in EXCLUIR:
            self.excluir += 1
        if tag in self.titulos and not self.referencias:
            self.titulos[tag] += 1

    def handle_endtag(self, tag):
        if not self.dentro_prose:
            return
        if tag in EXCLUIR and self.excluir:
            self.excluir -= 1
        if tag == "div":
            if self.div_flags and self.div_flags.pop() and self.excluir:
                self.excluir -= 1
            if not self.fragmento:
                self.div_prose -= 1
                if self.div_prose == 0:
                    self.dentro_prose = False

    def handle_data(self, data):
        if self.dentro_prose and not self.excluir and not self.referencias:
            self.palabras += len(PALABRA.findall(data))


def contar_html(texto, fragmento=False):
    p = Extractor(fragmento)
    p.feed(texto)
    return {"palabras": p.palabras, "h2": p.titulos["h2"], "h3": p.titulos["h3"]}


def contar(ruta, fragmento=False):
    r = contar_html(Path(ruta).read_text(encoding="utf-8"), fragmento)
    r["archivo"] = str(ruta)
    return r


if __name__ == "__main__":
    args = sys.argv[1:]
    fragmento = "--fragmento" in args
    como_json = "--json" in args
    rutas = [a for a in args if not a.startswith("--")]
    res = [contar(r, fragmento) for r in rutas]
    if como_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for r in res:
            print("%6d palabras  (h2=%d h3=%d)  %s" % (r["palabras"], r["h2"], r["h3"], r["archivo"]))
        if len(res) > 1:
            print("%6d total" % sum(r["palabras"] for r in res))
