"""
Genera un indice de busqueda compacto a partir del TTL.
El indice se carga en el navegador para busqueda local sin GraphDB.
"""

import json
import os
import re
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL_PATH = os.path.join(PROJECT_DIR, "output", "datos_integrados.ttl")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "web", "js", "search-index.json")
NS = "http://example.org/videojuegos#"


def parse_ttl_rapido(path):
    """
    Parseo rapido del TTL para extraer:
    - Entidades con su tipo y nombre
    - Relaciones (desarrolladoPor, perteneceAGenero, tieneLanzamiento)
    - Plataforma de cada lanzamiento
    """
    entidades = {}   # uri_abrev -> { type, nombre }
    relaciones = {}  # uri_abrev -> { desarrolladores: [], generos: [], lanzamientos: [] }
    lanz_plataforma = {}  # uri_lanz -> nombre_plataforma

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    bloque_actual = None
    bloque_lines = []

    for line in lines:
        stripped = line.strip()
        # Saltar comentarios, directivas de prefijo y base
        if stripped.startswith("@") or stripped.startswith("#") or stripped == "":
            continue
        if stripped.startswith("Prefix") or stripped.startswith("prefix"):
            continue

        # Acumular lineas del bloque
        bloque_lines.append(stripped)

        # El bloque termina con " ."
        if stripped.endswith("."):
            bloque_text = " ".join(bloque_lines)
            bloque_lines = []

            # Extraer el sujeto
            sujeto_match = re.match(r'^(\S+)\s+', bloque_text)
            if not sujeto_match:
                continue
            sujeto = sujeto_match.group(1)

            # Extraer tipo
            tipo_match = re.search(r'\ba\s+(\S+)', bloque_text)
            tipo = tipo_match.group(1) if tipo_match else None

            # Extraer nombre
            nombre_match = re.search(r':nombre\s+"([^"]+)"', bloque_text)
            nombre = nombre_match.group(1) if nombre_match else None

            if tipo:
                entidades[sujeto] = {"type": tipo, "nombre": nombre}

            # Extraer relaciones para Videojuego (limpiar comas/punto y coma finales)
            if tipo == NS + "Videojuego" or tipo == ":Videojuego":
                devs = [d.rstrip(',;') for d in re.findall(r':desarrolladoPor\s+(\S+)', bloque_text)]
                gens = [g.rstrip(',;') for g in re.findall(r':perteneceAGenero\s+(\S+)', bloque_text)]
                lanzs = [l.rstrip(',;') for l in re.findall(r':tieneLanzamiento\s+(\S+)', bloque_text)]
                if devs or gens or lanzs:
                    relaciones[sujeto] = {
                        "desarrolladores": devs,
                        "generos": gens,
                        "lanzamientos": lanzs,
                    }

            # Extraer plataforma de Lanzamiento (limpiar comas finales)
            if tipo == NS + "Lanzamiento" or tipo == ":Lanzamiento":
                plat_match = re.search(r':enPlataforma\s+(\S+)', bloque_text)
                if plat_match:
                    lanz_plataforma[sujeto] = plat_match.group(1).rstrip(',;')

    return entidades, relaciones, lanz_plataforma


def resolver_nombre(uri_abrev, entidades):
    """Resuelve una URI abreviada a su nombre legible."""
    if uri_abrev in entidades and entidades[uri_abrev]["nombre"]:
        return entidades[uri_abrev]["nombre"]
    return uri_abrev


def main():
    print("Parseando TTL...")
    entidades, relaciones, lanz_plataforma = parse_ttl_rapido(TTL_PATH)
    print(f"  Entidades: {len(entidades)}")
    print(f"  Videojuegos con relaciones: {len(relaciones)}")
    print(f"  Lanzamientos con plataforma: {len(lanz_plataforma)}")

    # Construir indice
    indice = []
    for vid, rel in relaciones.items():
        nombre = resolver_nombre(vid, entidades)
        if not nombre:
            continue

        # Resolver desarrolladores (limpiar prefijos :D_ y comas sueltas)
        desarrolladores = []
        for d in rel["desarrolladores"]:
            dev_name = resolver_nombre(d, entidades)
            if dev_name:
                # Limpiar formato como ":D_future_crayon," -> "Future Crayon"
                clean = re.sub(r'^:D_', '', dev_name)
                clean = re.sub(r'_', ' ', clean)
                clean = clean.strip(',').strip()
                if clean:
                    desarrolladores.append(clean)

        # Resolver generos (limpiar prefijos :G_ y comas sueltas)
        generos = []
        for g in rel["generos"]:
            gen_name = resolver_nombre(g, entidades)
            if gen_name:
                # Limpiar formato como ":G_action," -> "Action"
                clean = re.sub(r'^:G_', '', gen_name)
                clean = clean.strip(',').strip()
                if clean:
                    generos.append(clean)

        # Resolver plataformas desde los lanzamientos
        plataformas = set()
        for l in rel["lanzamientos"]:
            plat_uri = lanz_plataforma.get(l)
            if plat_uri:
                plat_name = resolver_nombre(plat_uri, entidades)
                if plat_name:
                    plataformas.add(plat_name)

        # Compactar: arrays planos, sin claves largas
        indice.append([
            nombre,
            sorted(plataformas) if plataformas else [],
            sorted(generos) if generos else [],
            sorted(desarrolladores) if desarrolladores else [],
        ])

    print(f"  Entradas en indice: {len(indice)}")

    # Ordenar por nombre
    indice.sort(key=lambda x: x[0].lower())

    # Escribir como JSON compacto
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"  Escrito JSON: {OUTPUT_PATH} ({size_kb:.0f} KB, {len(indice)} entradas)")

    # Escribir tambien como JS para carga directa sin fetch()
    js_path = OUTPUT_PATH.replace('.json', '.js')
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.SEARCH_INDEX=")
        json.dump(indice, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";")

    size_js_kb = os.path.getsize(js_path) / 1024
    print(f"  Escrito JS:   {js_path} ({size_js_kb:.0f} KB, {len(indice)} entradas)")


if __name__ == "__main__":
    main()
