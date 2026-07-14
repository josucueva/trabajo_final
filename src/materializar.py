"""
Materializacion del grafo RDF a partir de matches.json + fuentes originales.
Genera output/datos_integrados.ttl
"""

import json
import os
import re
from collections import defaultdict

import pandas as pd
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/
PROJECT_DIR = os.path.dirname(BASE_DIR)  # raiz del proyecto
DATA_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
NS = Namespace("http://example.org/videojuegos#")

VGSALES_PLATFORMS = {
    "2600": ("Consola", "Atari 2600"),
    "3DO": ("Consola", "3DO"),
    "3DS": ("Consola", "Nintendo 3DS"),
    "DC": ("Consola", "Dreamcast"),
    "DS": ("Consola", "Nintendo DS"),
    "GB": ("Consola", "Game Boy"),
    "GBA": ("Consola", "Game Boy Advance"),
    "GC": ("Consola", "GameCube"),
    "GEN": ("Consola", "Genesis"),
    "GG": ("Consola", "Game Gear"),
    "N64": ("Consola", "Nintendo 64"),
    "NES": ("Consola", "NES"),
    "NG": ("Consola", "Neo Geo"),
    "PC": ("PC", "PC"),
    "PCFX": ("Consola", "PC-FX"),
    "PS": ("Consola", "PlayStation"),
    "PS2": ("Consola", "PlayStation 2"),
    "PS3": ("Consola", "PlayStation 3"),
    "PS4": ("Consola", "PlayStation 4"),
    "PSP": ("Consola", "PSP"),
    "PSV": ("Consola", "PS Vita"),
    "SAT": ("Consola", "Saturn"),
    "SCD": ("Consola", "Sega CD"),
    "SNES": ("Consola", "SNES"),
    "TG16": ("Consola", "TurboGrafx-16"),
    "WS": ("Consola", "WonderSwan"),
    "Wii": ("Consola", "Wii"),
    "WiiU": ("Consola", "Wii U"),
    "X360": ("Consola", "Xbox 360"),
    "XB": ("Consola", "Xbox"),
    "XOne": ("Consola", "Xbox One"),
}

CONSOLE_PLATFORMS = [
    ("xbox", "Xbox"),
    ("playstation", "PlayStation"),
    ("switch", "Nintendo Switch"),
]

STEAM_COLS = [
    "appid",
    "name",
    "release_date",
    "price",
    "metacritic_score",
    "developers",
    "publishers",
    "genres",
    "positive",
    "negative",
    "average_playtime_forever",
    "peak_ccu",
]

REGION_MAP = {
    "NorthAmerica": "NA",
    "Europe": "EU",
    "Japan": "JP",
    "Australia": "AU",
}


def slugify(name):
    import hashlib

    s = name.lower().strip()
    if any(ord(c) > 127 for c in s):
        return "u_" + hashlib.md5(name.encode("utf-8")).hexdigest()[:12]
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


DEV_NORMALIZE = {
    "CAPCOM Co., Ltd.": "Capcom",
    "EA Digital Illusions CE": "EA DICE",
    "EA Digital Illusions Creations Entertainment": "EA DICE",
}


def parse_list(val):
    if pd.isna(val) or not val:
        return []
    try:
        import ast

        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return parsed
        return []
    except (ValueError, SyntaxError):
        return []


def clean_publisher(pub):
    pub = pub.strip()
    for prefix in ["JP: ", "WW: "]:
        if pub.startswith(prefix):
            pub = pub[len(prefix) :].strip()
    return pub


def parse_console_date(date_str):
    if not date_str or date_str in ("Unreleased", "TBA", ""):
        return None
    try:
        from datetime import datetime

        dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def load_data():
    with open(os.path.join(PROJECT_DIR, "matching", "matches.json"), encoding="utf-8") as f:
        matches = json.load(f)
    vgsales = pd.read_csv(os.path.join(DATA_DIR, "vgsales.csv"), encoding="utf-8")
    steam = pd.read_csv(
        os.path.join(DATA_DIR, "games_march2025_full.csv"), usecols=STEAM_COLS, encoding="utf-8"
    )
    console_data = {}
    for src in ["xbox", "playstation", "switch"]:
        with open(os.path.join(DATA_DIR, f"{src}_games.json"), encoding="utf-8") as f:
            console_data[src] = json.load(f)
    return matches, vgsales, steam, console_data


def build_indices(vgsales, steam, console_data):
    steam_by_appid = {}
    for _, row in steam.iterrows():
        steam_by_appid[row["appid"]] = row
    vgsales_by_name = defaultdict(list)
    for _, row in vgsales.iterrows():
        vgsales_by_name[row["Name"].strip()].append(row)
    console_by_id = {}
    for src, data in console_data.items():
        console_by_id[src] = {}
        for game in data:
            console_by_id[src][game["id"]] = game
    return steam_by_appid, dict(vgsales_by_name), console_by_id


def get_display_name(src_data, vgsales_by_name, steam_by_appid, console_by_id):
    if src_data.get("vgsales"):
        return src_data["vgsales"][0]
    if src_data.get("steam"):
        row = steam_by_appid.get(src_data["steam"][0])
        if row is not None:
            return row["name"]
    for src, key in [("xbox", "name"), ("playstation", "name"), ("switch", "name")]:
        if src_data.get(src):
            game = console_by_id[src].get(src_data[src][0])
            if game:
                return game["name"]
    return ""


def get_genres(src_data, vgsales_by_name, steam_by_appid, console_by_id):
    genres = set()
    if src_data.get("vgsales"):
        for orig_name in src_data["vgsales"]:
            for row in vgsales_by_name.get(orig_name, []):
                if pd.notna(row["Genre"]) and row["Genre"]:
                    genres.add(row["Genre"].strip())
    if src_data.get("steam"):
        for appid in src_data["steam"]:
            row = steam_by_appid.get(appid)
            if row is not None:
                for g in parse_list(row["genres"]):
                    if g:
                        genres.add(g.strip())
    for src in ["xbox", "playstation", "switch"]:
        if src_data.get(src):
            for gid in src_data[src]:
                game = console_by_id[src].get(gid)
                if game:
                    for g in game.get("genre", []):
                        if g:
                            genres.add(g.strip())
    return sorted(genres)


def get_developers(src_data, steam_by_appid, console_by_id):
    devs = set()
    if src_data.get("steam"):
        for appid in src_data["steam"]:
            row = steam_by_appid.get(appid)
            if row is not None:
                for d in parse_list(row["developers"]):
                    if d:
                        devs.add(DEV_NORMALIZE.get(d.strip(), d.strip()))
    for src in ["xbox", "playstation", "switch"]:
        if src_data.get(src):
            for gid in src_data[src]:
                game = console_by_id[src].get(gid)
                if game:
                    for d in game.get("developers", []):
                        if d:
                            devs.add(DEV_NORMALIZE.get(d.strip(), d.strip()))
    return sorted(devs)


def get_or_create(g, cache, prefix, rdf_type, name):
    key = slugify(name)
    if key in cache:
        return cache[key]
    uri = NS[f"{prefix}_{key}"]
    g.add((uri, RDF.type, rdf_type))
    g.add((uri, NS.nombre, Literal(name)))
    cache[key] = uri
    return uri


def create_platforms(g):
    platform_uris = {}
    for code, (type_name, label) in VGSALES_PLATFORMS.items():
        uri = NS[f"P_vg_{code}"]
        g.add((uri, RDF.type, getattr(NS, type_name)))
        g.add((uri, NS.nombre, Literal(label)))
        platform_uris[code] = uri
    for src, label in CONSOLE_PLATFORMS:
        uri = NS[f"P_{src}"]
        g.add((uri, RDF.type, NS.Consola))
        g.add((uri, NS.nombre, Literal(label)))
        platform_uris[f"_{src}"] = uri
    return platform_uris


def add_vgsales_lanzamientos(
    g, vj_uri, src_data, vgsales_by_name, platform_uris, editor_cache
):
    if not src_data.get("vgsales"):
        return
    dedup_seen = set()
    for orig_name in src_data["vgsales"]:
        for row in vgsales_by_name.get(orig_name, []):
            idx = row.name
            plat = row["Platform"]
            year = row["Year"]
            pub = row["Publisher"]
            na, eu, jp, other = (
                row["NA_Sales"],
                row["EU_Sales"],
                row["JP_Sales"],
                row["Other_Sales"],
            )
            dedup_key = (
                plat,
                int(year) if pd.notna(year) else None,
                str(pub) if pd.notna(pub) else "",
                na,
                eu,
                jp,
                other,
            )
            if dedup_key in dedup_seen:
                continue
            dedup_seen.add(dedup_key)
            lz_uri = NS[f"L_vg_{idx}"]
            g.add((lz_uri, RDF.type, NS.Lanzamiento))
            g.add((lz_uri, NS.enPlataforma, platform_uris[plat]))
            g.add((vj_uri, NS.tieneLanzamiento, lz_uri))
            if pd.notna(pub) and pub != "Unknown":
                e_uri = get_or_create(g, editor_cache, "E", NS.Editor, pub.strip())
                g.add((lz_uri, NS.publicadoPor, e_uri))
            if pd.notna(year):
                lr = BNode()
                g.add((lz_uri, NS.fechaLanzamiento, lr))
                g.add((lr, RDF.type, NS.LanzamientoRegional))
                g.add((lr, NS.region, Literal("WW")))
                g.add((lr, NS.fecha, Literal(f"{int(year)}-01-01", datatype=XSD.date)))
            for region, campo in [("NA", na), ("EU", eu), ("JP", jp), ("Other", other)]:
                if pd.notna(campo) and campo > 0:
                    vr = BNode()
                    g.add((lz_uri, NS.tieneVenta, vr))
                    g.add((vr, RDF.type, NS.VentaRegional))
                    g.add((vr, NS.region, Literal(region)))
                    g.add((vr, NS.monto, Literal(campo, datatype=XSD.decimal)))


def add_steam_lanzamientos(g, vj_uri, src_data, steam_by_appid, pc_uri, editor_cache):
    if not src_data.get("steam"):
        return
    for appid in src_data["steam"]:
        row = steam_by_appid.get(appid)
        if row is None:
            continue
        lz_uri = NS[f"L_steam_{appid}"]
        g.add((lz_uri, RDF.type, NS.Lanzamiento))
        g.add((lz_uri, NS.enPlataforma, pc_uri))
        name_lower = row["name"].strip().lower() if pd.notna(row["name"]) else ""
        if name_lower.endswith("playtest"):
            g.add((vj_uri, NS.tienePlaytest, lz_uri))
        elif re.search(r'\bdemo\b', name_lower):
            g.add((vj_uri, NS.tieneDemo, lz_uri))
        else:
            g.add((vj_uri, NS.tieneLanzamiento, lz_uri))
        for pub in parse_list(row["publishers"]):
            if pub:
                e_uri = get_or_create(g, editor_cache, "E", NS.Editor, pub.strip())
                g.add((lz_uri, NS.publicadoPor, e_uri))
        if pd.notna(row["price"]):
            g.add((lz_uri, NS.precio, Literal(row["price"], datatype=XSD.decimal)))
        if pd.notna(row["metacritic_score"]) and row["metacritic_score"] > 0:
            g.add(
                (
                    lz_uri,
                    NS.metacriticScore,
                    Literal(int(row["metacritic_score"]), datatype=XSD.integer),
                )
            )
        if pd.notna(row["positive"]):
            g.add(
                (
                    lz_uri,
                    NS.reseñasPositivas,
                    Literal(int(row["positive"]), datatype=XSD.integer),
                )
            )
        if pd.notna(row["negative"]):
            g.add(
                (
                    lz_uri,
                    NS.reseñasNegativas,
                    Literal(int(row["negative"]), datatype=XSD.integer),
                )
            )
        if pd.notna(row["average_playtime_forever"]):
            g.add(
                (
                    lz_uri,
                    NS.tiempoJuego,
                    Literal(int(row["average_playtime_forever"]), datatype=XSD.integer),
                )
            )
        if pd.notna(row["peak_ccu"]):
            g.add(
                (
                    lz_uri,
                    NS.peakCcu,
                    Literal(int(row["peak_ccu"]), datatype=XSD.integer),
                )
            )
        if pd.notna(row["release_date"]) and row["release_date"].strip():
            lr = BNode()
            g.add((lz_uri, NS.fechaLanzamiento, lr))
            g.add((lr, RDF.type, NS.LanzamientoRegional))
            g.add((lr, NS.region, Literal("WW")))
            g.add(
                (lr, NS.fecha, Literal(row["release_date"].strip(), datatype=XSD.date))
            )


def add_console_lanzamientos(
    g, vj_uri, src_data, console_by_id, console_src, plat_uri, editor_cache
):
    if not src_data.get(console_src):
        return
    for gid in src_data[console_src]:
        game = console_by_id[console_src].get(gid)
        if game is None:
            continue
        lz_uri = NS[f"L_{console_src}_{gid}"]
        g.add((lz_uri, RDF.type, NS.Lanzamiento))
        g.add((lz_uri, NS.enPlataforma, plat_uri))
        g.add((vj_uri, NS.tieneLanzamiento, lz_uri))
        for pub in game.get("publishers", []):
            clean = clean_publisher(pub)
            if clean:
                e_uri = get_or_create(g, editor_cache, "E", NS.Editor, clean)
                g.add((lz_uri, NS.publicadoPor, e_uri))
        release_dates = game.get("releaseDates", {})
        if isinstance(release_dates, dict):
            for api_region, rdf_region in REGION_MAP.items():
                date_str = release_dates.get(api_region, "")
                iso_date = parse_console_date(date_str)
                if iso_date:
                    lr = BNode()
                    g.add((lz_uri, NS.fechaLanzamiento, lr))
                    g.add((lr, RDF.type, NS.LanzamientoRegional))
                    g.add((lr, NS.region, Literal(rdf_region)))
                    g.add((lr, NS.fecha, Literal(iso_date, datatype=XSD.date)))


def process_doom(
    g,
    norm_name,
    src_data,
    vgsales_by_name,
    steam_by_appid,
    console_by_id,
    platform_uris,
    pc_uri,
    editor_cache,
    genero_cache,
    desarrollador_cache,
):
    if norm_name == "doom":
        vj_orig = NS.V_doom
        vj_2016 = NS.V_doom_2016
        g.add((vj_orig, RDF.type, NS.Videojuego))
        g.add((vj_orig, NS.nombre, Literal("DOOM")))
        g.add((vj_2016, RDF.type, NS.Videojuego))
        g.add((vj_2016, NS.nombre, Literal("DOOM (2016)")))
        genres_orig = set()
        genres_2016 = set()
        devs_2016 = set()
        if src_data.get("vgsales"):
            for orig_name in src_data["vgsales"]:
                for row in vgsales_by_name.get(orig_name, []):
                    if pd.notna(row["Genre"]) and row["Genre"]:
                        genres_orig.add(row["Genre"].strip())
        if src_data.get("steam"):
            for appid in src_data["steam"]:
                row = steam_by_appid.get(appid)
                if row is not None:
                    for gen in parse_list(row["genres"]):
                        if gen:
                            genres_2016.add(gen.strip())
                    for dev in parse_list(row["developers"]):
                        if dev:
                            devs_2016.add(DEV_NORMALIZE.get(dev.strip(), dev.strip()))
        for src in ["xbox", "playstation", "switch"]:
            if src_data.get(src):
                for gid in src_data[src]:
                    game = console_by_id[src].get(gid)
                    if game:
                        for gen in game.get("genre", []):
                            if gen:
                                genres_2016.add(gen.strip())
                        for dev in game.get("developers", []):
                            if dev:
                                devs_2016.add(
                                    DEV_NORMALIZE.get(dev.strip(), dev.strip())
                                )
        for gen in sorted(genres_orig):
            g_uri = get_or_create(g, genero_cache, "G", NS.Genero, gen)
            g.add((vj_orig, NS.perteneceAGenero, g_uri))
        for gen in sorted(genres_2016):
            g_uri = get_or_create(g, genero_cache, "G", NS.Genero, gen)
            g.add((vj_2016, NS.perteneceAGenero, g_uri))
        devs_all = set(devs_2016)
        for dev in sorted(devs_all):
            d_uri = get_or_create(g, desarrollador_cache, "D", NS.Desarrollador, dev)
            g.add((vj_orig, NS.desarrolladoPor, d_uri))
            g.add((vj_2016, NS.desarrolladoPor, d_uri))
        add_vgsales_lanzamientos(
            g, vj_orig, src_data, vgsales_by_name, platform_uris, editor_cache
        )
        steam_only = {"steam": src_data.get("steam")}
        add_steam_lanzamientos(
            g, vj_2016, steam_only, steam_by_appid, pc_uri, editor_cache
        )
        for src in ["xbox", "playstation", "switch"]:
            if src_data.get(src):
                sub = {src: src_data[src]}
                add_console_lanzamientos(
                    g,
                    vj_2016,
                    sub,
                    console_by_id,
                    src,
                    platform_uris[f"_{src}"],
                    editor_cache,
                )
    elif norm_name == "doom 2016":
        vj_2016 = NS.V_doom_2016
        if (vj_2016, None, None) not in set(g.triples((vj_2016, RDF.type, None))):
            g.add((vj_2016, RDF.type, NS.Videojuego))
            g.add((vj_2016, NS.nombre, Literal("DOOM (2016)")))
        add_vgsales_lanzamientos(
            g, vj_2016, src_data, vgsales_by_name, platform_uris, editor_cache
        )
        for orig_name in src_data.get("vgsales") or []:
            for row in vgsales_by_name.get(orig_name, []):
                if pd.notna(row["Genre"]) and row["Genre"]:
                    g_uri = get_or_create(
                        g, genero_cache, "G", NS.Genero, row["Genre"].strip()
                    )
                    g.add((vj_2016, NS.perteneceAGenero, g_uri))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Cargando datos...")
    matches, vgsales, steam, console_data = load_data()
    steam_by_appid, vgsales_by_name, console_by_id = build_indices(
        vgsales, steam, console_data
    )
    print(f"  matches: {len(matches)} entradas")
    print(f"  vgsales: {len(vgsales)} filas")
    print(f"  steam:   {len(steam)} filas")
    print(f"  xbox:    {len(console_data['xbox'])} juegos")
    print(f"  ps:      {len(console_data['playstation'])} juegos")
    print(f"  switch:  {len(console_data['switch'])} juegos")
    g = Graph()
    g.bind("", str(NS))
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.parse(os.path.join(PROJECT_DIR, "ontology", "ontologia.ttl"), format="turtle")
    print("Creando plataformas...")
    platform_uris = create_platforms(g)
    pc_uri = platform_uris["PC"]
    editor_cache = {}
    genero_cache = {}
    desarrollador_cache = {}
    total = len(matches)
    print(f"Procesando {total} entradas...")
    DOOM_NAMES = {"doom", "doom 2016"}
    for i, (norm_name, src_data) in enumerate(matches.items(), 1):
        if i % 10000 == 0:
            print(f"  {i}/{total}...")
        if norm_name in DOOM_NAMES:
            process_doom(
                g,
                norm_name,
                src_data,
                vgsales_by_name,
                steam_by_appid,
                console_by_id,
                platform_uris,
                pc_uri,
                editor_cache,
                genero_cache,
                desarrollador_cache,
            )
            continue
        is_playtest = False
        parent_norm = None
        if norm_name.endswith(" playtest"):
            candidate = norm_name[:-9]
            if candidate not in DOOM_NAMES:
                is_playtest = True
                parent_norm = candidate
        if is_playtest:
            vj_uri = NS[f"V_{slugify(parent_norm)}"]
            if parent_norm not in matches:
                g.add((vj_uri, RDF.type, NS.Videojuego))
                pt_name = get_display_name(
                    src_data, vgsales_by_name, steam_by_appid, console_by_id
                )
                if pt_name:
                    pt_name = (
                        pt_name.replace(" Playtest", "")
                        .replace(" playtest", "")
                        .strip()
                    )
                if not pt_name:
                    pt_name = parent_norm
                g.add((vj_uri, NS.nombre, Literal(pt_name)))
        else:
            slug = slugify(norm_name)
            vj_uri = NS[f"V_{slug}"]
            g.add((vj_uri, RDF.type, NS.Videojuego))
            display_name = get_display_name(
                src_data, vgsales_by_name, steam_by_appid, console_by_id
            )
            if display_name:
                g.add((vj_uri, NS.nombre, Literal(display_name)))
            for gen in get_genres(
                src_data, vgsales_by_name, steam_by_appid, console_by_id
            ):
                g_uri = get_or_create(g, genero_cache, "G", NS.Genero, gen)
                g.add((vj_uri, NS.perteneceAGenero, g_uri))
            for dev in get_developers(src_data, steam_by_appid, console_by_id):
                d_uri = get_or_create(
                    g, desarrollador_cache, "D", NS.Desarrollador, dev
                )
                g.add((vj_uri, NS.desarrolladoPor, d_uri))
            add_vgsales_lanzamientos(
                g, vj_uri, src_data, vgsales_by_name, platform_uris, editor_cache
            )
        add_steam_lanzamientos(
            g, vj_uri, src_data, steam_by_appid, pc_uri, editor_cache
        )
        if not is_playtest:
            for src in ["xbox", "playstation", "switch"]:
                if src_data.get(src):
                    add_console_lanzamientos(
                        g,
                        vj_uri,
                        src_data,
                        console_by_id,
                        src,
                        platform_uris[f"_{src}"],
                        editor_cache,
                    )
    output_path = os.path.join(OUTPUT_DIR, "datos_integrados.ttl")
    print(f"Serializando a {output_path}...")
    g.serialize(output_path, format="turtle", base=str(NS)[:-1])
    triple_count = len(g)
    print(f"Listo: {output_path} ({triple_count} tripletas)")


if __name__ == "__main__":
    main()
