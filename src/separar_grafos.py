#!/usr/bin/env python3
"""
Separa el grafo integrado en subgrafos independientes por fuente de datos.
Genera archivos en output/:
  - grafo_ontologia.ttl
  - grafo_vgsales.ttl
  - grafo_steam.ttl
  - grafo_xbox.ttl
  - grafo_playstation.ttl
  - grafo_switch.ttl
"""

import os, sys
from collections import defaultdict
from rdflib import Graph, Namespace, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATOS = os.path.join(RAIZ, "output", "datos_integrados.ttl")
RUTA_ONTOLOGIA = os.path.join(RAIZ, "ontology", "ontologia.ttl")
DIR_SALIDA = os.path.join(RAIZ, "output")

NS = Namespace("http://example.org/videojuegos#")

FUENTES = {
    "vgsales":     "L_vg_",
    "steam":       "L_steam_",
    "xbox":        "L_xbox_",
    "playstation": "L_playstation_",
    "switch":      "L_switch_",
}

def local_name(uri):
    s = str(uri)
    if "#" in s:
        return s.split("#", 1)[1]
    return s.rstrip("/").rsplit("/", 1)[1]

def fuente_de_launch(uri):
    if not isinstance(uri, URIRef):
        return None
    name = local_name(uri)
    for clave, prefijo in FUENTES.items():
        if name.startswith(prefijo):
            return clave
    return None

# Cargar
print("Cargando datos...", flush=True)
g = Graph()
g.parse(RUTA_DATOS, format="turtle")
print(f"  datos_integrados.ttl: {len(g)} triples", flush=True)

onto = Graph()
onto.parse(RUTA_ONTOLOGIA, format="turtle")
triples_ontologia = list(onto)
print(f"  ontologia.ttl: {len(onto)} triples", flush=True)

# Agrupar lanzamientos por fuente
lanzamientos_por_fuente = defaultdict(set)
for s in g.subjects(RDF.type, NS.Lanzamiento):
    if isinstance(s, URIRef):
        fuente = fuente_de_launch(s)
        if fuente:
            lanzamientos_por_fuente[fuente].add(s)

print("\nLanzamientos por fuente:", flush=True)
for f in sorted(FUENTES):
    print(f"  {f}: {len(lanzamientos_por_fuente[f])}", flush=True)

# Construir subgrafo por fuente
def construir_grafo_fuente(fuente, launches):
    sg = Graph()
    sg.bind("", NS)
    sg.bind("rdf", RDF)
    sg.bind("rdfs", RDFS)
    sg.bind("owl", OWL)

    visitados = set()

    def expandir(sujeto):
        if sujeto in visitados:
            return
        visitados.add(sujeto)
        for s, p, o in g.triples((sujeto, None, None)):
            sg.add((s, p, o))
            if isinstance(o, BNode):
                expandir(o)

    # 1. Ontologia
    for t in triples_ontologia:
        sg.add(t)

    # 2. Lanzamientos de la fuente
    for launch in launches:
        expandir(launch)

    # 3. Editores y Plataformas
    for launch in launches:
        for _, _, o in g.triples((launch, NS.publicadoPor, None)):
            if isinstance(o, URIRef):
                expandir(o)
        for _, _, o in g.triples((launch, NS.enPlataforma, None)):
            if isinstance(o, URIRef):
                expandir(o)

    # 4. Videojuegos vinculados
    for launch in launches:
        for v in g.subjects(None, launch):
            if isinstance(v, URIRef) and (v, RDF.type, NS.Videojuego) in g:
                expandir(v)

    # 5. Generos y Desarrolladores de esos Videojuegos
    for v in list(visitados):
        if not isinstance(v, URIRef):
            continue
        if (v, RDF.type, NS.Videojuego) not in g:
            continue
        for _, _, obj in g.triples((v, None, None)):
            if isinstance(obj, URIRef) and obj not in visitados:
                expandir(obj)

    return sg

# Generar archivos
for fuente, launches in sorted(lanzamientos_por_fuente.items()):
    print(f"\nConstruyendo grafo {fuente} ...", flush=True)
    sg = construir_grafo_fuente(fuente, launches)
    archivo = os.path.join(DIR_SALIDA, f"grafo_{fuente}.ttl")
    sg.serialize(archivo, format="turtle")
    print(f"  -> {archivo}: {len(sg)} triples", flush=True)

# Grafo de solo ontologia
print("\nConstruyendo grafo ontologia ...", flush=True)
go = Graph()
go.bind("", NS)
go.bind("rdf", RDF)
go.bind("rdfs", RDFS)
go.bind("owl", OWL)
for t in triples_ontologia:
    go.add(t)
archivo_onto = os.path.join(DIR_SALIDA, "grafo_ontologia.ttl")
go.serialize(archivo_onto, format="turtle")
print(f"  -> {archivo_onto}: {len(go)} triples", flush=True)

# Resumen
print("\n" + "=" * 55)
print("  RESUMEN DE TRIPLES POR GRAFO")
print("=" * 55)
nombres = ["grafo_ontologia.ttl"] + [f"grafo_{f}.ttl" for f in sorted(FUENTES)]
total = 0
for archivo in nombres:
    path = os.path.join(DIR_SALIDA, archivo)
    g_tmp = Graph()
    g_tmp.parse(path, format="turtle")
    print(f"  {archivo:30s} {len(g_tmp):>8d} triples")
    total += len(g_tmp)
print("-" * 55)
print(f"  {'TOTAL':30s} {total:>8d} triples")
print("¡Hecho!")
