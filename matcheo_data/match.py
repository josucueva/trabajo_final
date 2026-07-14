import json
import os
import re
from collections import defaultdict

import pandas as pd


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def normalize(name):
    name = name.strip().lower()
    name = re.sub(r"[#.,():;!?'\"$*+/\-]", "", name)
    name = re.sub(r"\s+", " ", name)
    name = name.strip()
    if not name or len(name) < 2:
        return None
    return name


def load_vgsales(path):
    df = pd.read_csv(path, usecols=["Name"], encoding="utf-8")

    groups = defaultdict(set)
    for _, row in df.iterrows():
        name = row["Name"]
        if pd.isna(name) or not str(name).strip():
            continue
        norm = normalize(str(name))
        if norm is None:
            continue
        groups[norm].add(str(name).strip())

    return {k: list(v) for k, v in groups.items()}


def load_steam(path):
    df = pd.read_csv(path, usecols=["appid", "name"], encoding="utf-8")

    groups = defaultdict(list)
    for _, row in df.iterrows():
        name = row["name"]
        appid = row["appid"]
        if pd.isna(name) or not str(name).strip():
            continue
        norm = normalize(str(name))
        if norm is None:
            continue
        groups[norm].append(int(appid))

    return {k: list(set(v)) for k, v in groups.items()}


def load_console(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    groups = defaultdict(list)
    for entry in data:
        name = entry.get("name", "")
        if not name or not str(name).strip():
            continue
        norm = normalize(str(name))
        if norm is None:
            continue
        groups[norm].append(entry["id"])

    return {k: list(set(v)) for k, v in groups.items()}


def build_matches(sources):
    all_keys = set()
    for data in sources.values():
        all_keys.update(data.keys())

    matches = {}
    for key in sorted(all_keys):
        entry = {}
        for src_name, src_data in sources.items():
            entry[src_name] = src_data.get(key, None)
        matches[key] = entry
    return matches


def print_summary(matches):
    total = len(matches)
    print(f"Total nombres unicos normalizados: {total}\n")

    src_names = list(list(matches.values())[0].keys())
    for src in src_names:
        count = sum(1 for v in matches.values() if v[src] is not None)
        print(f"  {src:15s} : {count:>6d} juegos")

    print()
    for n in range(1, 6):
        count = sum(
            1
            for v in matches.values()
            if sum(1 for src in v.values() if src is not None) == n
        )
        print(f"  En {n} fuente(s)  : {count:>6d} juegos")

    print()
    for i, src_a in enumerate(src_names):
        for src_b in src_names[i + 1 :]:
            a_set = {k for k, v in matches.items() if v[src_a] is not None}
            b_set = {k for k, v in matches.items() if v[src_b] is not None}
            print(f"  {src_a:15s} ∩ {src_b:15s} : {len(a_set & b_set):>6d}")


def save_matches(matches, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"\nmatches guardado en: {path}")


def main():
    data_dir = os.path.join(BASE, "data")

    print("Cargando vgsales...")
    vgsales = load_vgsales(os.path.join(data_dir, "vgsales.csv"))

    print("Cargando steam...")
    steam = load_steam(os.path.join(data_dir, "games_march2025_full.csv"))

    print("Cargando consolas...")
    xbox = load_console(os.path.join(data_dir, "xbox_games.json"))
    playstation = load_console(os.path.join(data_dir, "playstation_games.json"))
    switch = load_console(os.path.join(data_dir, "switch_games.json"))

    sources = {
        "vgsales": vgsales,
        "steam": steam,
        "xbox": xbox,
        "playstation": playstation,
        "switch": switch,
    }

    print("Construyendo matches...")
    matches = build_matches(sources)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    save_matches(matches, os.path.join(out_dir, "matches.json"))

    print_summary(matches)


if __name__ == "__main__":
    main()
