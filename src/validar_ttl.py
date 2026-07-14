"""
Validador sintáctico de archivos Turtle usando rdflib.
Útil para archivos grandes que no caben en validadores web.

Uso:
    python validar_ttl.py ontologia.ttl
    python validar_ttl.py output/datos_integrados.ttl
"""

import sys
from rdflib import Graph


def validar_ttl(path):
    print(f"Validando: {path} ...")
    g = Graph()
    try:
        g.parse(path, format="turtle")
        print(f"  OK: {len(g)} tripletas cargadas correctamente.")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python validar_ttl.py <archivo.ttl> [archivo2.ttl ...]")
        sys.exit(1)

    todos_ok = True
    for path in sys.argv[1:]:
        if not validar_ttl(path):
            todos_ok = False

    sys.exit(0 if todos_ok else 1)
