import requests
import json
import time

# Lista de consolas y sus URLs
consolas = {
    "switch": "https://api.sampleapis.com/switch/games",
    "playstation": "https://api.sampleapis.com/playstation/games",
    "xbox": "https://api.sampleapis.com/xbox/games"
}

for nombre, url in consolas.items():
    try:
        print(f"Descargando {nombre}...")
        respuesta = requests.get(url)
        time.sleep(2)  # Pausa para evitar rate limiting (código 429)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            with open(f'{nombre}_games.json', 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            print(f"✅ {nombre}: {len(datos)} juegos guardados en {nombre}_games.json")
        else:
            print(f"❌ Error en {nombre}: Código {respuesta.status_code}")
    except Exception as e:
        print(f"❌ Error al descargar {nombre}: {e}")