"""
Analisis de colisiones de nombre en vgsales:
Nombres con brecha >= 10 anos entre lanzamientos.
Identifica posibles reboots/secuelas con mismo nombre.
"""
import pandas as pd
import json
from collections import defaultdict

df = pd.read_csv('../data/vgsales.csv')

name_years = defaultdict(list)
for _, row in df.iterrows():
    name = row['Name'].strip()
    year = row['Year']
    if pd.notna(year):
        name_years[name].append(int(year))

candidates = []
for name, years in name_years.items():
    unique_years = sorted(set(years))
    if len(unique_years) < 2:
        continue
    max_gap = max(unique_years) - min(unique_years)
    if max_gap >= 10:
        rows = df[df['Name'].str.strip() == name]
        platforms = rows['Platform'].unique()
        publishers = rows['Publisher'].dropna().unique()
        candidates.append((name, unique_years, max_gap, list(platforms), list(publishers)))

candidates.sort(key=lambda x: -x[2])

with open('../matcheo_data/matches.json') as f:
    matches = json.load(f)

print(f"=== Nombres con brecha >= 10 anos en vgsales: {len(candidates)} casos ===\n")

VERIFICADOS = {
    "Sonic the Hedgehog": "Juegos distintos (1991 original vs 2006 Sonic '06 reboot)",
    "Mortal Kombat":       "Juegos distintos (1992 arcade vs 2011 reboot)",
    "Syndicate":           "Juegos distintos (1992 isometrico vs 2012 FPS)",
    "Spider-Man":          "Juegos distintos (1981 Atari vs 2000 PS1 Neversoft)",
    "Battlezone":          "Juegos distintos (1982 arcade vs 2006 FPS)",
    "Defender":            "Juegos distintos (1980 arcade vs 2002 FPS Midway)",
    "Asteroids":           "Juegos distintos (1980 arcade vs 1998 remake 3D)",
    "Castlevania":         "Juegos distintos (1986 NES vs 1999 N64)",
    "Bomberman":           "Juegos distintos (1985 NES vs distintas entregas 2005-2008)",
    "NBA Jam":             "Juegos distintos (1992 GEN vs 2003 vs 2010)",
    "Ridge Racer":         "Juegos distintos (1994 PS vs 2004 PSP vs 2011 PSV)",
    "Frogger":             "Juegos distintos (1981 arcade vs 1997 3D)",
    "Resident Evil":       "Mismo juego (1996 PS original portado a SAT 1997 y PS3 2006)",
    "Final Fantasy":       "Mismo juego (1987 NES original portado a WonderSwan 2000)",
    "Monopoly":            "Mismo juego (distintos ports del mismo juego de mesa)",
}

print(f"{'#':<4} {'Nombre':<50} {'Años':<25} {'Gap':<5} {'Cruza fuentes?':<20} {'Verificacion':<60}")
print("=" * 170)
for i, (name, years, gap, platforms, publishers) in enumerate(candidates, 1):
    norm = name.lower().strip()
    norm = ''.join(c for c in norm if c not in '#.,():;!?\'"$*+\\/-')
    norm = ' '.join(norm.split())
    sources = set()
    if norm in matches:
        for src, ids in matches[norm].items():
            if ids and not any(v is None for v in (ids if isinstance(ids, list) else [ids])):
                sources.add(src)
    cross = len(sources) > 1
    cross_str = ', '.join(sorted(sources)) if cross else 'solo vgsales'
    verificacion = VERIFICADOS.get(name, '---')
    print(f"{i:<4} {name:<50} {str(years):<25} {gap:<5} {cross_str:<20} {verificacion:<60}")

print(f"\nDecision: Solo DOOM se separa manualmente en dos :Videojuego (1993 vs 2016).")
print(f"Los demas se tratan como 1 :Videojuego con multiples :Lanzamiento,")
print(f"justificado porque vgsales no distingue entregas bajo el mismo nombre.")
