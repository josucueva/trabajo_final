import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # sube a trabajo_final/

for f in ['xbox_games.json', 'playstation_games.json', 'switch_games.json']:
    path = os.path.join(BASE, f)
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    print(f'--- {f} ---')
    print(f'  Registros: {len(data)}')
    if not data:
        print('  (vacio)')
        continue
    print(f'  Claves: {list(data[0].keys())}')

    vacios_genre = sum(1 for r in data if isinstance(r.get('genre'), list) and len(r['genre']) == 0)
    print(f'  genre vacio: {vacios_genre} ({vacios_genre/len(data)*100:.2f}%)')

    for campo in ['developers', 'publishers']:
        vacios = sum(1 for r in data if isinstance(r.get(campo), list) and len(r[campo]) == 0)
        print(f'  {campo} vacio: {vacios} ({vacios/len(data)*100:.2f}%)')

    regiones = ['Japan', 'NorthAmerica', 'Europe', 'Australia']
    for rgn in regiones:
        no_fecha = sum(1 for r in data
                       if isinstance(r.get('releaseDates'), dict)
                       and r['releaseDates'].get(rgn) in ['Unreleased', 'TBA'])
        print(f'  releaseDates.{rgn} Unreleased/TBA: {no_fecha} ({no_fecha/len(data)*100:.2f}%)')

    # names duplicados
    names = [r.get('name','') for r in data]
    dups = len(names) - len(set(names))
    print(f'  Nombres duplicados: {dups} de {len(data)}')

    # publishers con prefijo regional (Switch)
    if f == 'switch_games.json':
        prefijos = sum(1 for r in data
                       if any(isinstance(p, str) and (p.startswith('JP:') or p.startswith('WW:')) for p in r.get('publishers', [])))
        print(f'  publishers con prefijo regional: {prefijos}')

    print()
