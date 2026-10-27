#!/usr/bin/env python3
"""Actualiza manifiesto.json y progreso.json con evidencia comprobable.

Ejemplos:
  python estado.py ART-001 ART-002 --recontar --estado EN_REVISION
  python estado.py ART-001 --auditoria-editorial "OK 2026-10-27" --auditoria-tecnica "OK 2026-10-27" --estado APROBADO
  python estado.py ART-001 --estado PUBLICADO_VERIFICADO --verificacion "HTTP 200, 5790 palabras (2026-10-27)" --publicado
  python estado.py --proxima-accion "Lote 2: investigar ART-006..ART-010" --despliegue "commit abc1234, run OK"

--recontar vuelve a calcular las palabras (cuerpo.html) y cuenta las fuentes de fuentes.md.
Sin ids, solo regenera progreso.json a partir del manifiesto.
"""
import argparse
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
ED = RAIZ / "editorial"
sys.path.insert(0, str(AQUI))
from contar_palabras import contar  # noqa: E402

ESTADOS = ["PLANIFICADO", "INVESTIGANDO", "BORRADOR", "EN_REVISION", "CORRECCIONES_PENDIENTES", "APROBADO",
           "INTEGRADO", "DESPLEGADO", "PUBLICADO_VERIFICADO", "BLOQUEADO"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--estado", choices=ESTADOS)
    ap.add_argument("--recontar", action="store_true")
    ap.add_argument("--auditoria-editorial")
    ap.add_argument("--auditoria-tecnica")
    ap.add_argument("--verificacion")
    ap.add_argument("--publicado", action="store_true")
    ap.add_argument("--obs")
    ap.add_argument("--proxima-accion")
    ap.add_argument("--despliegue")
    a = ap.parse_args()

    ruta_man = ED / "manifiesto.json"
    man = json.loads(ruta_man.read_text(encoding="utf-8"))
    por_id = {x["id"]: x for x in man["articulos"]}

    for i in a.ids:
        x = por_id[i]
        carpeta = ED / "articulos" / i
        if a.recontar:
            x["palabras_editoriales"] = contar(carpeta / "cuerpo.html", fragmento=True)["palabras"]
            f = carpeta / "fuentes.md"
            x["fuentes_registradas"] = len(re.findall(r"^\|\s*\d+\s*\|", f.read_text(encoding="utf-8"), re.M)) if f.exists() else 0
            meta = json.loads((carpeta / "meta.json").read_text(encoding="utf-8"))
            x["titulo"] = re.sub(r"<[^>]+>", "", meta["titulo"])
            x["slug"] = meta["slug"]
            x["ruta_archivo"] = "articulos/%s.html" % meta["slug"]
            x["url_publica"] = "%s/articulos/%s.html" % (man["sitio"], meta["slug"])
        if a.estado:
            x["estado"] = a.estado
        if a.auditoria_editorial:
            x["auditoria_editorial"] = a.auditoria_editorial
        if a.auditoria_tecnica:
            x["auditoria_tecnica"] = a.auditoria_tecnica
        if a.verificacion:
            x["verificacion_publica"] = a.verificacion
        if a.publicado:
            x["fecha_publicacion"] = json.loads((carpeta / "meta.json").read_text(encoding="utf-8"))["fecha"]
        if a.obs is not None:
            x["observaciones"] = a.obs
    ruta_man.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # progreso.json derivado del manifiesto
    ruta_pro = ED / "progreso.json"
    pro = json.loads(ruta_pro.read_text(encoding="utf-8"))
    arts = man["articulos"]
    ids = lambda f: [x["id"] for x in arts if f(x)]  # noqa: E731
    pro["investigados"] = ids(lambda x: x["fuentes_registradas"])
    pro["redactados"] = ids(lambda x: x["palabras_editoriales"])
    pro["html_creados"] = ids(lambda x: (RAIZ / x["ruta_archivo"]).exists() and x["palabras_editoriales"])
    pro["auditoria_superada"] = ids(lambda x: (x["auditoria_editorial"] or "").startswith("OK") and (x["auditoria_tecnica"] or "").startswith("OK"))
    pro["desplegados"] = ids(lambda x: x["estado"] in ("DESPLEGADO", "PUBLICADO_VERIFICADO"))
    pro["url_verificadas"] = ids(lambda x: x["estado"] == "PUBLICADO_VERIFICADO")
    pro["pendientes"] = ids(lambda x: x["estado"] != "PUBLICADO_VERIFICADO")
    completados = pro["url_verificadas"]
    pro["ultimo_articulo_completado"] = completados[-1] if completados else None
    lotes = sorted({x["lote"] for x in arts if x["estado"] == "PUBLICADO_VERIFICADO"})
    pro["ultimo_lote_procesado"] = lotes[-1] if lotes else 0
    if a.proxima_accion:
        pro["proxima_accion"] = a.proxima_accion
    if a.despliegue:
        pro["estado_ultimo_despliegue"] = a.despliegue
    pro["actualizado"] = __import__("datetime").date.today().isoformat()
    ruta_pro.write_text(json.dumps(pro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for x in arts:
        if x["id"] in a.ids:
            print("%s  %-22s palabras=%s fuentes=%s" % (x["id"], x["estado"], x["palabras_editoriales"], x["fuentes_registradas"]))


if __name__ == "__main__":
    main()
