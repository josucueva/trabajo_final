"""
Validador SHACL para datos_integrados.ttl usando pyshacl.
Ejecuta las 4 reglas definidas en ontology/validacion_shacl.ttl
y guarda el resultado en docs/resultado_validacion_shacl.txt

Uso:
    python src/validar_shacl.py
"""

import os
import sys
from pyshacl import validate
from rdflib import Graph

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
ONTO_PATH = os.path.join(PROJECT_DIR, "ontology", "validacion_shacl.ttl")
DATA_PATH = os.path.join(PROJECT_DIR, "output", "datos_integrados.ttl")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "docs", "resultado_validacion_shacl.txt")


def main():
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: No se encuentra {DATA_PATH}")
        sys.exit(1)
    if not os.path.exists(ONTO_PATH):
        print(f"ERROR: No se encuentra {ONTO_PATH}")
        sys.exit(1)

    print(f"Shapes: {ONTO_PATH}")
    print(f"Datos:  {DATA_PATH}")
    print("Validando...")

    shapes_g = Graph()
    shapes_g.parse(ONTO_PATH, format="turtle")
    data_g = Graph()
    data_g.parse(DATA_PATH, format="turtle")

    conforms, results_graph, results_text = validate(
        data_g,
        shacl_graph=shapes_g,
        ont_graph=None,
        inference=None,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        advanced=False,
    )

    lines = []
    lines.append("=" * 60)
    lines.append("VALIDACION SHACL — datos_integrados.ttl")
    lines.append("=" * 60)
    lines.append(f"Conforms: {conforms}")
    lines.append("")

    violations = list(results_graph.subjects())
    lines.append(f"Total violaciones: {len(violations)}")
    lines.append("")

    # Agrupar violaciones por tipo para un resumen claro
    from collections import Counter
    tipos = Counter()
    muestras = []
    for r in violations:
        path = None
        msg = None
        for s, p, o in results_graph.triples((r, None, None)):
            pname = str(p).split("#")[-1] if "#" in str(p) else str(p).split("/")[-1]
            if pname == "resultPath":
                path = str(o).split("#")[-1] if "#" in str(o) else str(o)
            if pname == "resultMessage":
                msg = str(o)
        key = f"{path}: {msg}" if msg else str(path)
        tipos[key] += 1
        if len(muestras) < 5:
            focus = None
            for s, p, o in results_graph.triples((r, None, None)):
                pname = str(p).split("#")[-1] if "#" in str(p) else str(p).split("/")[-1]
                if pname == "focusNode":
                    focus = str(o)
            muestras.append(f"  focusNode={focus}, path={path}, msg={msg}")

    lines.append("Resumen por tipo de violacion:")
    for tipo, count in tipos.most_common():
        lines.append(f"  - [{count:>6}x] {tipo}")
    lines.append("")
    lines.append("Muestras de violaciones (primeras 5):")
    for m in muestras:
        lines.append(m)
    lines.append("")
    lines.append("NOTA: La regla 1 (Videojuego sin genero) genera ~30K violaciones")
    lines.append("porque Xbox (64.6%) y PlayStation (87.1%) no tienen dato de genero.")
    lines.append("Esto es un problema conocido de calidad de fuente, no del codigo.")

    output = "\n".join(lines)
    print(output)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"\nResultado guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
