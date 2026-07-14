"""
Ejecutar LOCALMENTE sobre los 3 JSON de consolas.
Requiere: pip install pandas

Ajusta los nombres de archivo si difieren de los reales.
"""

import json
import pandas as pd

ARCHIVOS = {
    "xbox": "xbox_games.json",
    "playstation": "playstation_games.json",  # ojo: nombre tal como lo diste, revisa si es un typo real del archivo
    "switch": "switch_games.json",             # idem
}

resumen = []

for consola, ruta in ARCHIVOS.items():
    print(f"\n{'='*50}\n{consola.upper()} — {ruta}\n{'='*50}")
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total de registros: {len(data)}")

    if len(data) == 0:
        print("Archivo vacío, revisar.")
        continue

    # Ver las claves del primer registro
    print(f"Claves del primer registro: {list(data[0].keys())}")

    df = pd.json_normalize(data)
    print(f"\nColumnas tras normalizar: {df.columns.tolist()}")

    # genre vacío (puede venir como lista vacía)
    if "genre" in df.columns:
        vacios_genre = df["genre"].apply(lambda x: isinstance(x, list) and len(x) == 0).sum()
        print(f"Registros con 'genre' vacío ([]): {vacios_genre} ({vacios_genre/len(df)*100:.2f}%)")

    # developers / publishers vacíos
    for campo in ["developers", "publishers"]:
        if campo in df.columns:
            vacios = df[campo].apply(lambda x: isinstance(x, list) and len(x) == 0).sum()
            print(f"Registros con '{campo}' vacío ([]): {vacios} ({vacios/len(df)*100:.2f}%)")

    # releaseDates: contar cuántos son "Unreleased" o "TBA" por región
    cols_fecha = [c for c in df.columns if c.startswith("releaseDates.")]
    print(f"\nColumnas de fecha por región: {cols_fecha}")
    for c in cols_fecha:
        no_fecha = df[c].isin(["Unreleased", "TBA"]).sum()
        print(f"  {c}: {no_fecha} registros con 'Unreleased'/'TBA' ({no_fecha/len(df)*100:.2f}%)")

    # nombres duplicados
    if "name" in df.columns:
        print(f"\nNombres duplicados: {df['name'].duplicated().sum()} de {len(df)}")

    resumen.append({"consola": consola, "total_registros": len(data), "columnas": df.columns.tolist()})

    # Guardar muestra pequeña
    df.sample(min(200, len(df)), random_state=42).to_csv(f"muestra_{consola}_200.csv", index=False)
    print(f"\n✅ muestra_{consola}_200.csv generado")

print("\n\nResumen final:")
for r in resumen:
    print(r)
