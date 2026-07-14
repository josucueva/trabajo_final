"""
Analisis de plataformas en vgsales:
- Lista las 31 plataformas unicas con su conteo de juegos
- Clasifica cada una como :Consola o :PC
"""
import pandas as pd

df = pd.read_csv('../data/vgsales.csv')
platforms = sorted(df['Platform'].unique())

print(f"=== Plataformas en vgsales: {len(platforms)} ===")
consolas = []
pc_list = []
for p in platforms:
    count = len(df[df['Platform'] == p])
    tipo = 'PC' if p.upper() == 'PC' else 'Consola'
    if tipo == 'PC':
        pc_list.append((p, count))
    else:
        consolas.append((p, count))
    print(f"  :P_vg_{p:<6}  rdf:type  :{tipo:<8}  ;  :nombre \"{p}\"  .  # {count:>5} juegos")

print(f"\nTotal Consolas: {len(consolas)}")
print(f"Total PC: {len(pc_list)}")
