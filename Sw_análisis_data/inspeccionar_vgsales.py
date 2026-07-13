"""
Ejecutar LOCALMENTE sobre vgsales.csv
Requiere: pip install pandas
"""

import pandas as pd

RUTA = "vgsales.csv"

df = pd.read_csv(RUTA)

print(f"Total de filas: {len(df)}")
print("\nTipos de datos:")
print(df.dtypes)

print("\nPorcentaje de valores nulos/vacíos por columna:")
print((df.isna().sum() / len(df) * 100).round(2))

print("\nValores únicos en 'Year' (primeros y últimos 5 ordenados):")
print(sorted(df['Year'].dropna().unique())[:5], "...", sorted(df['Year'].dropna().unique())[-5:])

print("\n¿Cuántos 'Year' son NaN?", df['Year'].isna().sum())
print("¿Cuántos 'Publisher' son NaN?", df['Publisher'].isna().sum())

print("\nNombres duplicados (mismo Name, distinto Platform es normal, pero revisemos):")
print("Filas totales:", len(df), "| Nombres únicos:", df['Name'].nunique())

print("\nEjemplo de un juego con varias plataformas (para verificar que cada fila = un lanzamiento):")
ejemplo = df[df['Name'] == df['Name'].value_counts().index[0]]
print(ejemplo[['Name', 'Platform', 'Year', 'Publisher', 'Global_Sales']])

# Guardar reporte + muestra
with open("reporte_vgsales.txt", "w", encoding="utf-8") as f:
    f.write(f"Total filas: {len(df)}\n\n")
    f.write("Tipos de datos:\n")
    f.write(df.dtypes.to_string())
    f.write("\n\nPorcentaje de nulos:\n")
    f.write((df.isna().sum() / len(df) * 100).round(2).to_string())

df.sample(min(500, len(df)), random_state=42).to_csv("muestra_vgsales_500.csv", index=False)

print("\n✅ Listo: reporte_vgsales.txt y muestra_vgsales_500.csv generados. Súbelos al chat.")
