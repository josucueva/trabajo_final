"""
Ejecutar LOCALMENTE (no en el chat) sobre games_march2025_cleaned.csv
Requiere: pip install pandas

Genera:
  1. Un reporte de texto con columnas, tipos y % de nulos reales
  2. Un CSV pequeño de muestra (500 filas, solo columnas núcleo) para subir al chat
"""

import pandas as pd

RUTA = "games_march2025_full.csv"  # ajusta la ruta si es necesario

# Columnas núcleo que discutimos (ajusta si tu archivo tiene nombres distintos)
COLUMNAS_NUCLEO = [
    "appid", "name", "release_date", "required_age", "price", "dlc_count",
    "windows", "mac", "linux", "metacritic_score", "developers", "publishers",
    "genres", "categories", "tags", "positive", "negative",
    "estimated_owners", "average_playtime_forever", "peak_ccu"
]

print(f"Revisando archivo: {RUTA}")
# --- 1. Leer solo el encabezado primero para ver qué columnas existen REALMENTE ---
encabezado = pd.read_csv(RUTA, nrows=0)
print("Columnas encontradas en el archivo real:")
print(list(encabezado.columns))
print(f"\nTotal de columnas: {len(encabezado.columns)}")

# Verificar cuáles de las columnas núcleo sí existen
existentes = [c for c in COLUMNAS_NUCLEO if c in encabezado.columns]
faltantes = [c for c in COLUMNAS_NUCLEO if c not in encabezado.columns]
print(f"\nColumnas núcleo que SÍ existen: {existentes}")
print(f"Columnas núcleo que NO existen (revisar nombre): {faltantes}")

# --- 2. Leer el archivo completo pero SOLO esas columnas (mucho más liviano) ---
df = pd.read_csv(RUTA, usecols=existentes)

print(f"\nTotal de filas: {len(df)}")
print("\nTipos de datos:")
print(df.dtypes)

print("\nPorcentaje de valores nulos/vacíos por columna:")
print((df.isna().sum() / len(df) * 100).round(2))

# --- 3. Guardar reporte de texto ---
with open("reporte_steam.txt", "w", encoding="utf-8") as f:
    f.write(f"Columnas reales: {list(encabezado.columns)}\n\n")
    f.write(f"Total filas: {len(df)}\n\n")
    f.write("Tipos de datos:\n")
    f.write(df.dtypes.to_string())
    f.write("\n\nPorcentaje de nulos:\n")
    f.write((df.isna().sum() / len(df) * 100).round(2).to_string())

# --- 4. Guardar una muestra pequeña (500 filas) para subir al chat ---
df.sample(min(500, len(df)), random_state=42).to_csv("muestra_salida.csv", index=False)

print("\n✅ Listo. Se generaron dos archivos:")
print("   - reporte_steam.txt   (súbelo al chat)")
print("   - muestra_steam_500.csv   (súbelo al chat)")
