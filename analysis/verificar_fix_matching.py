"""
Verifica que los casos de falsos negativos detectados anteriormente
se hayan resuelto con la nueva normalizacion en match.py.
"""

import os
import re
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATCHES_PATH = os.path.join(PROJECT_DIR, "matching", "matches.json")
TTL_PATH = os.path.join(PROJECT_DIR, "output", "datos_integrados.ttl")

# Casos que antes eran falsos negativos (detectados en FASE 3 del analisis)
CASOS_ANTERIORES = [
    ("shadow of the templars", "shadows of the templars"),
    ("power up kit hd", "powerup kit hd"),
    ("dont eat flamingos", "don't eat flamingos"),
    ("plants vs zombies battle for neighborville", "plants vs zombies battle for neighborville™"),
    ("silent hunter 5 battle of the atlantic", "silent hunter 5® battle of the atlantic"),
    ("tom clancys ghost recon future soldier", "tom clancys ghost recon future soldier™"),
    ("infinite combat", "infinite combate"),
]


def normalize(name):
    """Misma normalizacion que en match.py."""
    name = name.strip().lower()
    name = re.sub(r"[\u2018\u2019\u201A\u201B\u2032\u2035\u02BC\u02BB\u02BD\u02BE\u0060\u00B4]", "'", name)
    name = re.sub(r"[\u2122\u00AE\u00A9\u00B0\u2022\u00B7\u25CF\u25CB\u25A0\u25A1\u2665\u2660\u2663\u2666\u2605\u2606]", "", name)
    name = re.sub(r"[#.,():;!?'\"$*+/\u2014\u2013\u2010\-]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def main():
    print("=== VERIFICACION DE CASOS DETECTADOS ===\n")
    print(f"{'Caso':55s} {'Antes':10s} {'Ahora':10s}")
    print("-"*80)

    with open(MATCHES_PATH, encoding="utf-8") as f:
        matches = json.load(f)

    total_antes_separados = 0
    total_ahora_unidos = 0

    for nombre_a, nombre_b in CASOS_ANTERIORES:
        norm_a = normalize(nombre_a)
        norm_b = normalize(nombre_b)

        en_matches_a = norm_a in matches
        en_matches_b = norm_b in matches
        mismo_grupo = norm_a == norm_b

        if mismo_grupo:
            estado = "✅ UNIDOS"
            total_ahora_unidos += 1
        elif en_matches_a and en_matches_b:
            estado = "❌ SEPARADOS"
            total_antes_separados += 1
        else:
            estado = "? NO ENCONTRADO"

        print(f"  {norm_a[:50]:50s} {'separados':10s} {estado:10s}")
        print(f"  {norm_b[:50]:50s} {'':10s}")
        print()

    # Buscar si hay casos nuevos de TM/R que antes estaban separados
    print("\n=== BUSCANDO NUEVAS FUSIONES POR TM/R ===\n")
    total_tm = 0
    for key in matches:
        if "\u2122" in key or "\u00AE" in key:
            total_tm += 1
    print(f"  Keys con TM/R en matches.json: {total_tm} (0 = se limpiaron bien)")

    # Verificar en el TTL nombres con TM
    print("\n=== BUSCANDO TM/R EN EL TTL ===\n")
    tm_count = 0
    with open(TTL_PATH, encoding="utf-8") as f:
        for line in f:
            if "\u2122" in line or "\u00AE" in line:
                tm_count += 1
    print(f"  Lineas con TM/R en datos_integrados.ttl: {tm_count}")


if __name__ == "__main__":
    main()
