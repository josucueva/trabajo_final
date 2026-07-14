# Informe Técnico Integral de Fuentes de Datos para Proyecto de Grafo de Conocimiento sobre Videojuegos

> **⚠️ Documento histórico (análisis teórico inicial).**  
> Este informe fue el primer análisis de las fuentes. La versión actualizada con hallazgos reales verificados contra los datos es `informe_consolidado.md`. Algunas recomendaciones aquí (como usar la versión `_cleaned` de Steam o eliminar palabras "The"/"Edition" de títulos) **no se implementaron** en la solución final. Consultar `informe_consolidado.md` para el estado real del proyecto.

**Fecha de elaboración:** 12 de julio de 2026  
**Versión:** 3.0 (Definitiva, con correcciones)  
**Propósito:** Este documento describe de manera exhaustiva y detallada todas las fuentes de datos disponibles para la construcción de un grafo de conocimiento (RDF) en el dominio de los videojuegos. El informe incluye la estructura, contenido, formatos, tipos de datos, valores posibles, problemas de calidad cuantificados, relaciones entre fuentes y la evaluación de cumplimiento de los requisitos del proyecto. Sirve como contexto objetivo para la posterior fase de depuración, transformación e integración.

---

## 1. Introducción y Resumen de Fuentes Seleccionadas

El proyecto consiste en integrar múltiples conjuntos de datos independientes (CSV y JSON) para generar un grafo de conocimiento que permita responder consultas SPARQL sobre videojuegos, abarcando ventas, metadatos y comportamiento de usuarios.

Se dispone de cinco archivos de datos, pero para cumplir con el requisito de al menos tres fuentes con ≥5 atributos y formatos variados, se han preseleccionado las siguientes:

| Fuente | Formato | Atributos (≥5) | Valores faltantes | Entidad común | Uso recomendado |
|--------|---------|----------------|-------------------|---------------|-----------------|
| `vgsales.csv` | CSV | Sí (11) | Sí (Year, Publisher) | `Name` | Catálogo y ventas |
| `Steam Games Dataset 2025` | CSV | Sí (>40) | Sí (metacritic, etc.) | `name` | Metadatos de Steam |
| `playstation_games.json` | JSON | Sí (5+objeto anidado) | Sí (genre vacío, Unreleased) | `name` | Metadatos de PlayStation |
| `switch_games.json` | JSON | Sí (5+objeto anidado) | Sí (Unreleased, TBA) | `name` | Metadatos de Switch |
| `xbox_games.json` | JSON | Sí (5+objeto anidado) | Sí (genre vacío, Unreleased) | `name` | Metadatos de Xbox |

**Nota:** El dataset `steam-200k.csv` (interacciones de usuarios) fue considerado inicialmente, pero se descarta por tener solo 4 columnas documentadas, no alcanzando el mínimo de 5 atributos. Se reemplaza por el `Steam Games Dataset 2025`, que es mucho más rico y cumple con los requisitos. El dataset `Video_Games_5.json` de Amazon también se descarta por su complejidad y porque no se necesita para cumplir con el mínimo de fuentes requerido.

En las siguientes secciones se describe cada fuente en detalle.

---

## 2. Descripción Detallada de Cada Fuente

### 2.1. `vgsales.csv` – Ventas de Videojuegos

**Enlace al conjunto de datos en Kaggle:** [EDA - VIDEO GAME SALES (Input Data)](https://www.kaggle.com/code/upadorprofzs/eda-video-game-sales/input)  
**Origen:** Dataset clásico de Kaggle (gregorut/videogamesales).  
**Formato:** CSV con cabecera, separador coma (`,`). Codificación UTF-8.  
**Tamaño estimado:** ~1.4 MB, aproximadamente 16,000 registros.

**Columnas (11 en total):**

| Nombre | Tipo de dato | Descripción | Valores posibles / Notas |
|--------|--------------|-------------|---------------------------|
| `Rank` | Entero | Posición en el ranking global de ventas (orden descendente). | Número entero positivo. |
| `Name` | Texto (string) | Título del juego. | Puede contener caracteres especiales, números, etc. Ej: `"Wii Sports"`. |
| `Platform` | Texto (string) | Plataforma de lanzamiento. | Valores comunes: `"Wii"`, `"NES"`, `"PS4"`, `"X360"`, `"PC"`. |
| `Year` | Entero o nulo | Año de lanzamiento. | Puede ser `"N/A"` o estar vacío. |
| `Genre` | Texto (string) | Género principal. | Ej: `"Sports"`, `"Platform"`. |
| `Publisher` | Texto (string) | Editor o desarrollador. | Puede ser nulo (`NaN`) o contener el placeholder `"Unknown"` (dato faltante disfrazado de válido). |
| `NA_Sales` | Decimal (float) | Ventas en Norteamérica (millones de unidades). | Números con uno o dos decimales. |
| `EU_Sales` | Decimal (float) | Ventas en Europa. | Similar. |
| `JP_Sales` | Decimal (float) | Ventas en Japón. | Similar. |
| `Other_Sales` | Decimal (float) | Ventas en el resto del mundo. | Similar. |
| `Global_Sales` | Decimal (float) | Suma de ventas globales. | Calculada como NA+EU+JP+Other. |

**Ejemplo de registros:**
```csv
Rank,Name,Platform,Year,Genre,Publisher,NA_Sales,EU_Sales,JP_Sales,Other_Sales,Global_Sales
1,Wii Sports,Wii,2006,Sports,Nintendo,41.49,29.02,3.77,8.46,82.74
2,Super Mario Bros.,NES,1985,Platform,Nintendo,29.08,3.58,6.81,0.77,40.24
3,Mario Kart Wii,Wii,2008,Racing,Nintendo,15.85,12.88,3.79,3.31,35.82
```

**Problemas de calidad conocidos (cuantificados):**
- **Valores nulos o placeholders en `Publisher`:** Además de valores `NaN` (nulos reales), existe un porcentaje de registros con el texto `"Unknown"`, que funciona como un placeholder de dato faltante. Esto debe considerarse un valor no informativo, al igual que un nulo.
- **Duplicados por `Name` y `Platform`:** Un mismo juego puede aparecer en la misma plataforma en múltiples filas. Se ha confirmado el caso de "Need for Speed: Most Wanted" con dos filas en X360 y dos en PC. Esto puede deberse a diferentes ediciones o regiones, y debe tenerse en cuenta para no inflar las ventas.
- **Variaciones en `Name`:** Ligeras diferencias en el mismo título (ej. `"Super Mario Bros."` vs `"Super Mario Bros"`).
- **Datos de ventas:** Son numéricos, pero pueden tener valores redondeados.

---

### 2.2. `Steam Games Dataset 2025` – Metadatos de Juegos de Steam

**Enlace al conjunto de datos en Kaggle:** [Steam Games Dataset 2025](https://www.kaggle.com/datasets/artermiloff/steam-games-dataset?select=games_march2025_full.csv)  
**Origen:** Recopilación de datos de la API de Steam y Steam Spy, con datos actualizados hasta marzo de 2025.  
**Formato:** CSV con cabecera, separador coma (`,`). Muchos campos contienen datos serializados (arrays, objetos) como strings.  
**Tamaño estimado:** ~471 MB para el archivo completo, con más de 90,000 juegos.

**Nota sobre versiones del dataset:**
Este dataset tiene dos versiones disponibles en Kaggle:
- `games_march2025_full.csv`: Archivo completo y sin procesar.
- `games_march2025_cleaned.csv`: Versión sin juegos duplicados ni versiones "playtest". Esta versión es preferible para análisis, ya que reduce ruido y valores redundantes.

**Columnas (más de 40):** A continuación se listan las más relevantes agrupadas por categoría. Se indica el tipo de dato y una descripción.

#### Identificadores y Metadatos Básicos

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `appid` | Entero | Identificador único de Steam. | `730`, `578080` |
| `name` | Texto | Título del juego. | `"Counter-Strike 2"` |
| `release_date` | Texto (fecha ISO) | Fecha de lanzamiento en formato `YYYY-MM-DD`. | `2012-08-21` |
| `required_age` | Entero | Edad mínima requerida (0 si no aplica). | `0` |
| `price` | Decimal | Precio en USD (0.0 si gratuito). | `0.0` |
| `dlc_count` | Entero | Número de DLCs disponibles. | `1` |
| `detailed_description` | Texto largo | Descripción detallada del juego. | (texto extenso) |
| `about_the_game` | Texto largo | Resumen descriptivo. | (texto) |
| `short_description` | Texto | Descripción breve. | (texto) |
| `reviews` | Texto | Campo aparentemente no utilizado (puede estar vacío). | (vacío) |

#### Imágenes y Enlaces

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `header_image` | Texto (URL) | URL de la imagen de cabecera. | `https://...header.jpg` |
| `website` | Texto (URL) | Sitio web oficial. | `http://counter-strike.net/` |
| `support_url` | Texto (URL) | URL de soporte. | `https://support.pubg.com/...` |
| `support_email` | Texto | Correo de soporte (puede estar vacío). | (vacío) |

#### Compatibilidad y Plataformas

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `windows` | Booleano | Soporte para Windows. | `True`, `False` |
| `mac` | Booleano | Soporte para macOS. | `False` |
| `linux` | Booleano | Soporte para Linux. | `True` |

#### Métricas y Puntuaciones

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `metacritic_score` | Entero o nulo | Puntuación de Metacritic (0-100). **Nota:** `0` es el valor dominante (95-96% de los casos), no una excepción. | `0` (si no tiene) |
| `metacritic_url` | Texto (URL) | Enlace a Metacritic. | (URL o vacío) |
| `achievements` | Entero | Número de logros. | `1` |
| `recommendations` | Entero | Número de recomendaciones. | `4401572` |
| `user_score` | Decimal o nulo | Puntuación de usuarios (0-100). | `0` |
| `score_rank` | Texto | Clasificación (ej. "Great"). | (vacío) |
| `positive` | Entero | Reseñas positivas. | `7480813` |
| `negative` | Entero | Reseñas negativas. | `1135108` |
| `estimated_owners` | Texto (rango) | Rango estimado de propietarios. **Nota:** El 15.8% de los casos tiene `"0 - 0"` como placeholder, indicando ausencia de información real. | `"100000000 - 200000000"` |
| `average_playtime_forever` | Entero | Tiempo promedio jugado (minutos). | `33189` |
| `average_playtime_2weeks` | Entero | Tiempo promedio en últimas 2 semanas. | `879` |
| `median_playtime_forever` | Entero | Mediana del tiempo jugado. | `5174` |
| `median_playtime_2weeks` | Entero | Mediana en últimas 2 semanas. | `350` |
| `discount` | Entero | Descuento actual (0 si no hay). | `0` |
| `peak_ccu` | Entero | Pico de jugadores concurrentes. | `1212356` |

#### Campos Serializados (Arrays y Objetos)

| Columna | Tipo (como string) | Descripción | Ejemplo de contenido parseado |
|---------|---------------------|-------------|-------------------------------|
| `supported_languages` | Texto (lista) | Idiomas soportados. | `['Czech', 'Danish', ...]` |
| `full_audio_languages` | Texto (lista) | Idiomas con audio completo. | `['English', 'Indonesian']` |
| `packages` | Texto (lista de objetos) | Información de paquetes/ediciones. | `[{'title': 'Buy Counter-Strike 2', ...}]` |
| `developers` | Texto (lista) | Desarrolladores. | `['Valve']` |
| `publishers` | Texto (lista) | Editores. | `['KRAFTON, Inc.']` |
| `categories` | Texto (lista) | Categorías de Steam. | `['Multi-player', 'PvP', ...]` |
| `genres` | Texto (lista) | Géneros. | `['Action', 'Free To Play']` |
| `screenshots` | Texto (lista de URLs) | Capturas de pantalla. | `['https://...ss_1.jpg', ...]` |
| `movies` | Texto (lista de URLs) | Vídeos o tráilers. | `['http://...movie.mp4', ...]` |
| `tags` | Texto (objeto clave-valor) | Etiquetas de la comunidad (clave: número de usuarios). | `{'FPS': 90857, 'Shooter': 65397, ...}` |
| `notes` | Texto | Notas adicionales. | (vacío) |
| `pct_pos_total` | Entero | Porcentaje de reseñas positivas totales. | `86` |
| `num_reviews_total` | Entero | Número total de reseñas. | `8632939` |
| `pct_pos_recent` | Entero | Porcentaje de reseñas positivas recientes. | `82` |
| `num_reviews_recent` | Entero | Número de reseñas recientes. | `96473` |

**Ejemplo de registros (CSV):**
```
appid,name,release_date,required_age,price,dlc_count,...,developers,publishers,genres,positive,negative,estimated_owners,...
730,Counter-Strike 2,2012-08-21,0,0.0,1,...,['Valve'],['Valve'],['Action','Free To Play'],7480813,1135108,"100000000 - 200000000",...
578080,PUBG: BATTLEGROUNDS,2017-12-21,0,0.0,0,...,['PUBG Corporation'],['KRAFTON, Inc.'],['Action','Adventure','Massively Multiplayer','Free To Play'],1487960,1024436,"50000000 - 100000000",...
```

**Problemas de calidad conocidos (cuantificados):**
- **`estimated_owners = "0 - 0":** En el archivo `_full`, un **15.8%** de los registros tienen este valor, que no es un rango real, sino un placeholder que indica que no hay información de propietarios. Esto es relevante si se usan estos datos para inferir popularidad.
- **`metacritic_score = 0`:** Es el valor dominante, presente en el **95-96%** de los casos, no una excepción. Dado que Metacritic solo puntúa un subconjunto de juegos, la mayoría no tiene puntuación. Esto debe tenerse en cuenta para evitar interpretar `0` como una calificación baja real.
- **Campos serializados:** Requieren parseo (json.loads o ast.literal_eval) para extraer listas/objetos.
- **Rangos en `estimated_owners`:** En los casos donde sí hay datos, el valor es un rango (ej. `"100000000 - 200000000"`). Se puede procesar para obtener un valor aproximado (ej. promedio del rango).
- **Inconsistencia en nombres:** El título puede variar respecto a otras fuentes (ej. "Counter-Strike 2" vs "Counter-Strike: Global Offensive").
- **Fechas:** `release_date` es consistente, pero puede haber fechas futuras o incorrectas.

---

### 2.3. JSON de Metadatos de Juegos de Consolas (PlayStation, Switch, Xbox)

**Origen:** API pública SampleAPIs ([https://api.sampleapis.com/](https://api.sampleapis.com/)). Esta API no requiere autenticación y está diseñada para fines educativos y de prueba. Su repositorio oficial en GitHub ([https://github.com/jermbo/SampleAPIs](https://github.com/jermbo/SampleAPIs)) explica que su propósito es ser un "playground" para aprender sobre APIs RESTful y GraphQL, y que los datos se restablecen periódicamente.

**Endpoints específicos:**

| Consola | Endpoint (URL) |
|---------|----------------|
| **Nintendo Switch** | `https://api.sampleapis.com/switch/games` |
| **PlayStation** | `https://api.sampleapis.com/playstation/games` |
| **Xbox** | `https://api.sampleapis.com/xbox/games` |

**Formato:** JSON puro (array de objetos). Cada archivo JSON se obtiene realizando una petición `GET` a su respectivo endpoint. La estructura es idéntica para las tres consolas.

**Tamaño estimado de los archivos descargados:** PlayStation ~270 KB, Switch ~250 KB, Xbox ~2.5 MB. Xbox es el más extenso (~2,200 registros).

**Estructura de cada objeto:**

| Clave | Tipo | Descripción | Valores posibles / Notas |
|-------|------|-------------|---------------------------|
| `id` | Entero | Identificador único dentro de la API (no global entre consolas). | Número entero. |
| `name` | Texto (string) | Título del juego. | Puede tener variaciones en mayúsculas, puntuación, etc. |
| `genre` | Array de strings | Lista de géneros. | Puede estar vacío `[]` o contener uno o varios géneros. |
| `developers` | Array de strings | Lista de desarrolladores. | **100% poblado en las tres consolas.** |
| `publishers` | Array de strings | Lista de editores o distribuidores. | **100% poblado en las tres consolas.** |
| `releaseDates` | Objeto anidado | Fechas de lanzamiento por región. | Contiene siempre `Japan`, `NorthAmerica`, `Europe`, `Australia`. Valores: fecha en `"Month DD, YYYY"`, o `"Unreleased"`, `"TBA"`. |

**Ejemplos por consola:**

- **PlayStation** (formato de nombre en minúsculas, algunos `genre` vacíos):
```json
{
  "id": 1,
  "name": "#killallzombies",
  "genre": ["Shooter"],
  "developers": ["Beatshapers"],
  "publishers": ["Beatshapers"],
  "releaseDates": {
    "Japan": "Unreleased",
    "NorthAmerica": "Nov 12, 2014",
    "Europe": "Oct 28, 2014",
    "Australia": "Oct 28, 2014"
  }
}
```

- **Switch** (nombres con formato título, géneros más detallados):
```json
{
  "id": 2,
  "name": "#KillAllZombies",
  "genre": ["Survival", "third-person shooter"],
  "developers": ["Beatshapers"],
  "publishers": ["Beatshapers"],
  "releaseDates": {
    "Japan": "Unreleased",
    "NorthAmerica": "January 24, 2019",
    "Europe": "January 24, 2019",
    "Australia": "January 24, 2019"
  }
}
```

- **Xbox** (nombres con puntuación extra, algunos `genre` vacíos):
```json
{
  "id": 1,
  "name": "#killallzombies....",
  "genre": [],
  "developers": ["Beatshapers"],
  "publishers": ["Digerati"],
  "releaseDates": {
    "Japan": "Unreleased",
    "NorthAmerica": "Aug 9, 2016",
    "Europe": "Aug 9, 2016",
    "Australia": "Aug 9, 2016"
  }
}
```

**Problemas de calidad conocidos (cuantificados):**
- **`genre` vacío:** Este problema es mucho más frecuente de lo que sugiere el informe original. Los datos muestran:
  - **Xbox:** 64.6% de los juegos tienen `genre: []`.
  - **PlayStation:** 87.1% de los juegos tienen `genre: []`.
  - **Switch:** **0%** de los juegos tienen `genre` vacío.
  
  Esto convierte el `genre` en un campo prácticamente inútil para Xbox y PlayStation (la mayoría de los casos), mientras que en Switch está siempre presente y es fiable.

- **`developers` y `publishers`:** **Están 100% poblados en las tres consolas.** No hay casos vacíos o nulos en estos campos, lo que los convierte en los campos más fiables de estos JSON.

- **Formato de `publishers` en Switch:** En algunos registros, el campo `publishers` contiene valores que mezclan región y nombre del editor en un mismo string (ej. `"JP: G-Mode"`, `"WW: HandyGames"`). Esto requiere un paso de limpieza adicional para extraer el nombre del editor puro antes de usarlo en el grafo.

- **Inconsistencia en `name`:** Mayúsculas, puntuación, espacios adicionales, sufijos como "....".
- **Fechas nominales:** `"Unreleased"` y `"TBA"` no son fechas reales.
- **Solapamiento de juegos:** Un mismo juego aparece en varias consolas con metadatos posiblemente diferentes (género, desarrolladores, fechas). No hay un identificador común.

---

## 3. Análisis de la Entidad Común y Estrategia de Enlace

La integración de las fuentes se basa en la capacidad de enlazar registros que se refieren al mismo juego. El atributo común principal es el **nombre del juego** (título). A continuación se detalla cómo se presenta en cada fuente y los desafíos asociados.

| Fuente | Campo de título | Formato típico | Desafíos |
|--------|-----------------|----------------|----------|
| `vgsales.csv` | `Name` | Título canónico (ej. "Wii Sports") | Algunas variaciones menores. |
| `Steam Games Dataset 2025` | `name` | Título oficial de Steam (ej. "Counter-Strike 2") | Puede incluir subtítulos o números. |
| JSON de consolas | `name` | Título de la API (ej. "#killallzombies") | Inconsistencias en mayúsculas, puntuación, sufijos. |

**Estrategia de enlace (definitiva, sin coincidencia difusa):**

Dado el riesgo de falsos positivos con técnicas de coincidencia difusa (especialmente con títulos cortos, secuelas y remasters), y el tiempo limitado para validar los resultados, se adopta un enfoque conservador y controlado:

1.  **Normalización simple:** Aplicar una función que convierta los títulos a minúsculas, elimine caracteres especiales (puntuación, símbolos como `#`, etc.) y espacios extra. Se eliminarán palabras comunes no informativas como `"The"`, `"Edition"`, `"Remastered"`, etc., solo si aparecen al final del título, para no afectar a casos como `"The Witcher"`.

2.  **Coincidencia exacta:** Después de la normalización, se buscarán coincidencias **exactas** de cadena entre las diferentes fuentes. Esto garantiza que los enlaces sean precisos y verificables, evitando falsos positivos.

3.  **Aceptación de cobertura parcial:** Se asume que no todos los juegos tendrán contraparte en todas las fuentes. En lugar de forzar el enlace de todo el catálogo, se documentará explícitamente que se prioriza la **precisión sobre la cobertura total**. Este subconjunto de coincidencias limpias será suficiente para demostrar la integración y responder las consultas SPARQL obligatorias.

4.  **Documentación de decisiones:** Todas las reglas de normalización y el criterio de coincidencia exacta se registrarán como parte del proceso de depuración, de modo que sea posible auditar por qué ciertos juegos se enlazaron y otros no.

Esta estrategia es más sencilla de implementar, evita la caja negra del fuzzy matching, y es más defendible en la sustentación, ya que se basa en reglas claras y verificables.

---

## 4. Cumplimiento de Requisitos del Proyecto

El proyecto exige:
- Al menos 3 fuentes de datos independientes.
- Cada fuente debe tener ≥5 atributos.
- Deben existir valores faltantes o erróneos para validaciones SHACL.
- Las fuentes deben compartir una entidad común para su integración.
- Se deben incluir al menos dos formatos diferentes (CSV, JSON).

**Evaluación de las fuentes seleccionadas:**

| Fuente | Formato | ≥5 atrib. | Valores faltantes | Entidad común | ¿Seleccionada? |
|--------|---------|-----------|-------------------|---------------|----------------|
| `vgsales.csv` | CSV | Sí (11) | Sí (Year, Publisher) | `Name` | ✅ Sí |
| `Steam Games Dataset 2025` | CSV | Sí (>40) | Sí (metacritic, etc.) | `name` | ✅ Sí |
| `playstation_games.json` | JSON | Sí (5+objeto) | Sí (genre vacío, Unreleased) | `name` | ✅ Sí (opcional) |
| `switch_games.json` | JSON | Sí (5+objeto) | Sí (Unreleased, TBA) | `name` | ✅ Sí (opcional) |
| `xbox_games.json` | JSON | Sí (5+objeto) | Sí (genre vacío, Unreleased) | `name` | ✅ Sí (recomendado) |

**Conclusión:** Con `vgsales.csv`, `Steam Games Dataset 2025` y `xbox_games.json` (o cualquiera de los JSON de consolas) se cumplen todos los requisitos: 3 fuentes, formatos CSV y JSON, ≥5 atributos, valores faltantes y entidad común. Las otras fuentes (PlayStation, Switch) pueden usarse para enriquecer el grafo si se desea.

---

## 5. Consideraciones Adicionales para la Depuración e Integración

- **Tamaño y manejo de memoria:** El archivo de Steam es grande (~471 MB) y debe procesarse con cuidado, aunque puede caber en memoria con recursos adecuados. Los demás archivos son pequeños.
- **Parseo de campos serializados:** En el dataset de Steam, muchos campos son arrays u objetos serializados como strings. Se debe usar `ast.literal_eval` o `json.loads` para convertirlos a tipos nativos de Python.
- **Estandarización de fechas:** Unificar todos los formatos de fecha a `YYYY-MM-DD` (ISO) para facilitar consultas temporales.
- **Manejo de valores nominales:** `"Unreleased"`, `"TBA"`, `"N/A"` deben tratarse como valores nulos o como literales especiales en el grafo.
- **Rangos en `estimated_owners`:** Se puede convertir a un valor numérico (ej. promedio del rango) o mantenerlo como string para consultas textuales.
- **Documentación del proceso:** Registrar todas las decisiones de normalización, umbrales de coincidencia y transformaciones para la sustentación del proyecto.
- **Particularidades de cada fuente:**
  - Para `vgsales.csv`: Prestar atención a los duplicados por `Name` + `Platform` y al placeholder `"Unknown"` en `Publisher`.
  - Para `Steam`: Decidir si usar la versión `_cleaned` o `_full` según el nivel de detalle deseado. La versión `_cleaned` reduce ruido.
  - Para JSON de consolas: Tener en cuenta que `genre` es prácticamente inútil en Xbox y PlayStation, pero fiable en Switch. `developers` y `publishers` son los campos más robustos.

---

## 6. Resumen de Campos Clave para el Grafo de Conocimiento

A continuación se resumen los atributos más relevantes de cada fuente para la construcción de triplas RDF:

| Fuente | Atributos a modelar | Relaciones posibles |
|--------|---------------------|---------------------|
| `vgsales.csv` | `Name`, `Platform`, `Year`, `Genre`, `Publisher`, `NA_Sales`, `EU_Sales`, `JP_Sales`, `Other_Sales`, `Global_Sales` | `Juego` → `tieneVentas` (con valores por región), `lanzadoEn` (plataforma), `publicadoPor` |
| `Steam Games Dataset 2025` | `name`, `release_date`, `price`, `developers`, `publishers`, `genres`, `positive`, `negative`, `average_playtime_forever`, `peak_ccu`, `windows`, `mac`, `linux`, `metacritic_score`, etc. | `Juego` → `tienePrecio`, `tieneMetacritic`, `tieneReseñas` (positivas/negativas), `tieneDesarrollador`, `tieneEditor`, `compatibleCon` (SO) |
| JSON de consolas | `name`, `genre` (array), `developers`, `publishers`, `releaseDates` (por región) | `Juego` → `tieneGenero`, `tieneDesarrollador`, `tieneEditor`, `fechaLanzamiento` (por región) |

**Nota:** Se pueden crear entidades adicionales como `Desarrollador`, `Editor`, `Plataforma` para enriquecer el grafo.

---

## 7. Recomendaciones Finales

1. **Selección de fuentes:** Utilizar `vgsales.csv`, `Steam Games Dataset 2025` (versión `_cleaned` si es posible) y `xbox_games.json` como las tres fuentes principales. Esto proporciona una cobertura amplia (ventas, metadatos de Steam, metadatos de Xbox) y cumple con todos los requisitos.
2. **Procesamiento:** Priorizar la normalización simple de títulos y las coincidencias exactas para crear el `game_id` común. Para el dataset de Steam, parsear los campos serializados. Para los JSON de consolas, tener especial cuidado con el campo `genre` (prácticamente vacío en Xbox y PlayStation) y limpiar el formato de `publishers` en Switch.
3. **Validaciones:** Aprovechar los valores faltantes (ej. `Year` nulo, `genre` vacío, `metacritic_score` = 0) para diseñar shapes SHACL que verifiquen la presencia de ciertos atributos.
4. **Extensión opcional:** Si se desea añadir más datos, se pueden incorporar los JSON de PlayStation y Switch como fuentes adicionales, ya que comparten la misma estructura que el de Xbox.
5. **Enfoque de enlace:** Documentar claramente la decisión de usar coincidencia exacta después de normalización, priorizando precisión sobre cobertura total, y aceptando que se obtendrá un subconjunto de enlaces limpios. Este enfoque es más defendible y adecuado para el plazo disponible.

---

**Fin del Informe**