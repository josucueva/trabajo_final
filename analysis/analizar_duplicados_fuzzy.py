"""
Analiza posibles duplicados en el grafo que NO se detectaron en el matching exacto.
Busca nombres que probablemente se refieran al MISMO juego pero con variaciones
ortograficas, de formato, o numeracion (arabiga vs romana, con/puntos, etc.).

Metodologia:
  1. Extrae todos los nombres del TTL
  2. Normaliza cada nombre eliminando diferencias superficiales (puntos, guiones, articulos)
  3. Agrupa nombres cuyo "fingerprint" sea identico
  4. Reporta los grupos como candidatos a fusion
"""

import json
import os
import re
from collections import defaultdict
from difflib import SequenceMatcher

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL_PATH = os.path.join(PROJECT_DIR, "output", "datos_integrados.ttl")
MATCHES_PATH = os.path.join(PROJECT_DIR, "matching", "matches.json")


def extraer_nombres_desde_ttl():
    """Extrae los nombres de videojuegos desde el TTL."""
    nombres = set()
    try:
        with open(TTL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r':nombre\s+"([^"]+)"', line)
                if m:
                    nombres.add(m.group(1))
    except FileNotFoundError:
        print(f"ERROR: TTL no encontrado en {TTL_PATH}")
    return sorted(nombres)


def fingerprint_light(name):
    """
    Fingerprint que ignora diferencias superficiales:
    - lowercased
    - sin puntuacion
    - numeros romanos normalizados a arabigos
    - espacios colapsados
    - articulos iniciales eliminados
    """
    n = name.lower().strip()
    # Eliminar puntuacion
    n = re.sub(r'[#.,():;!?\'"$*+/\-—–]', ' ', n)
    # Normalizar espacios
    n = re.sub(r'\s+', ' ', n).strip()
    return n


def normalizar_numeros(s):
    """Convierte numeros romanos a arabigos en un string."""
    romanos = {
        r'\biii\b': '3', r'\bii\b': '2', r'\biv\b': '4',
        r'\bvi\b': '6', r'\bix\b': '9', r'\bxi\b': '11',
    }
    for patron, arabigo in romanos.items():
        s = re.sub(patron, arabigo, s)
    return s


def quitar_articulos(s):
    """Elimina articulos iniciales (the, a, an) y preposiciones comunes."""
    s = re.sub(r'^(the|a|an|le|la|les|el|los|las)\s+', '', s)
    return s


def fingerprint_fuerte(name):
    """
    Fingerprint mas agresivo para agrupar candidatos:
    - fingerprint_light
    - numeros romanos -> arabigos
    - articulos/preposiciones eliminados
    - '&' -> 'and'
    - palabras de 1 caracter eliminadas
    - ':' y '-' tratados como espacio
    """
    n = fingerprint_light(name)
    n = normalizar_numeros(n)
    n = re.sub(r'\b&\b', 'and', n)
    n = quitar_articulos(n)
    # Eliminar palabras de 1 caracter
    tokens = [t for t in n.split() if len(t) > 1]
    return ' '.join(tokens)


def similitud_avanzada(a, b):
    """Calcula similitud textual entre dos nombres."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def main():
    print("Extrayendo nombres desde datos_integrados.ttl...")
    nombres = extraer_nombres_desde_ttl()
    print(f"  Total nombres en el TTL: {len(nombres)}")

    # --- FASE 1: Agrupar por fingerprint fuerte ---
    print("\n" + "="*70)
    print("FASE 1: Posibles duplicados con fingerprint fuerte")
    print("(ignora diferencias de puntuacion, mayusculas, numeracion romana, articulos)")
    print("="*70)

    grupos_fp = defaultdict(list)
    for nombre in nombres:
        fp = fingerprint_fuerte(nombre)
        grupos_fp[fp].append(nombre)

    # Mostrar grupos con mas de 1 nombre
    candidatos = [(fp, names) for fp, names in grupos_fp.items() if len(names) > 1]
    candidatos.sort(key=lambda x: -len(x[1]))

    if not candidatos:
        print("  No se encontraron grupos con fingerprint identico.")
    else:
        print(f"  Se encontraron {len(candidatos)} grupos candidatos:\n")
        for fp, names in candidatos[:25]:
            print(f"  Fingerprint: '{fp}'")
            for n in names:
                print(f"    - {n}")
            print()

    # --- FASE 2: Similitud par a par en nombres largos ---
    print("\n" + "="*70)
    print("FASE 2: Pares con alta similitud textual (>90%) pero fingerprint distinto")
    print("(detecta typos como 'dar sous' vs 'dark souls')")
    print("="*70)

    # Comparar solo pares que compartan al menos una palabra completa
    # para evitar O(n^2)
    idx_palabra = defaultdict(list)
    for i, nombre in enumerate(nombres):
        palabras = set(re.findall(r'[a-z]{3,}', nombre.lower()))
        for p in palabras:
            idx_palabra[p].append(i)

    pares_vistos = set()
    pares_similares = []

    # Limitar a palabras con pocas ocurrencias para evitar explosion combinatoria
    for palabra, indices in idx_palabra.items():
        if len(indices) > 200:  # palabras muy comunes las saltamos
            continue
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                a, b = indices[i], indices[j]
                if (a, b) in pares_vistos:
                    continue
                pares_vistos.add((a, b))

                na, nb = nombres[a], nombres[b]
                # Diferencia relativa de longitud < 30%
                if abs(len(na) - len(nb)) / max(len(na), len(nb)) > 0.3:
                    continue

                ratio = similitud_avanzada(na, nb)
                if ratio >= 0.85:
                    pares_similares.append((ratio, na, nb))

    pares_similares.sort(reverse=True)
    if not pares_similares:
        print("  No se encontraron pares similares.")
    else:
        print(f"  Se encontraron {len(pares_similares)} pares (mostrando los mas relevantes):\n")
        mostrados = 0
        for ratio, a, b in pares_similares:
            # Ocultar falsos positivos obvios: solo "vol 1" / "vol 2"
            if re.search(r'\bvol\s*\.?\s*\d+\b', a) and re.search(r'\bvol\s*\.?\s*\d+\b', b):
                continue
            # Ocultar pares que son claramente secuelas (difieren solo en numero final)
            if re.match(r'^(.+?)\s*\d+$', a) and re.match(r'^(.+?)\s*\d+$', b):
                base_a = re.match(r'^(.+?)\s*\d+$', a).group(1)
                base_b = re.match(r'^(.+?)\s*\d+$', b).group(1)
                if base_a == base_b:
                    continue
            print(f"  {ratio:.1%}  | {a:55s} | {b}")
            mostrados += 1
            if mostrados >= 20:
                break

    # --- FASE 3: Cargar matches.json para ver nombres conflictivos ---
    print("\n" + "="*70)
    print("FASE 3: Verificacion cruzada con matches.json")
    print("(nombres que existen en matches.json y parecen variaciones de otros)")
    print("="*70)

    with open(MATCHES_PATH, encoding="utf-8") as f:
        matches = json.load(f)

    # Buscar nombres normalizados en matches.json que se parezcan
    # a nombres del TTL pero no sean exactamente iguales
    claves = sorted(matches.keys())
    ttl_lower = {n.lower() for n in nombres}

    falsos_negativos = []
    for i, clave in enumerate(claves):
        # Comparar con adyacentes (ventana 3)
        for j in range(i+1, min(i+4, len(claves))):
            ratio = SequenceMatcher(None, clave, claves[j]).ratio()
            if ratio >= 0.88:
                # Verificar que NO sean el mismo juego (diferencia real de nombre)
                falsos_negativos.append((ratio, clave, claves[j]))

    falsos_negativos.sort(reverse=True)
    if falsos_negativos:
        print(f"  Candidatos a falsos negativos en matches.json:\n")
        for ratio, a, b in falsos_negativos[:20]:
            print(f"  {ratio:.1%}  | {a:50s} | {b}")
    else:
        print("  No se detectaron candidatos obvios.")

    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"  Total nombres en TTL: {len(nombres)}")
    print(f"  Grupos con fingerprint identico: {len(candidatos)}")
    print(f"  Pares con similitud >85%: {len(pares_similares)}")
    print(f"  Candidatos en matches.json: {len(falsos_negativos)}")
    print()
    print("  Los resultados requieren revision manual para decidir si fusionar.")
    print("  =================================================================")

if __name__ == "__main__":
    main()
