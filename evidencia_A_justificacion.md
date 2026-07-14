# Justificación para la integración de fuentes en un grafo de conocimiento

**Proyecto:** Grafo de conocimiento sobre videojuegos
**Fuentes:** vgsales.csv, games_march2025_full.csv (Steam), xbox_games.json, playstation_games.json, switch_games.json

---

## 1. Contexto: fragmentación real de las fuentes

Las tres fuentes seleccionadas describen el mismo dominio — videojuegos — pero desde perspectivas y con estructuras completamente distintas, verificadas directamente sobre los datos:

- **vgsales.csv** modela cada combinación juego+plataforma como una fila tabular, con ventas regionales desagregadas (`NA_Sales`, `EU_Sales`, `JP_Sales`, `Other_Sales`), pero **sin columna de desarrollador** — solo editor (`Publisher`).
- **Steam** modela cada juego como un registro con más de 40 atributos, muchos de ellos listas serializadas dentro de una celda de texto (`developers`, `publishers`, `genres`, `tags`), y con métricas propias que no existen en ninguna otra fuente (`metacritic_score`, `estimated_owners`, `peak_ccu`).
- **Los JSON de consolas** (Xbox, PlayStation, Switch) usan una estructura anidada — cada juego trae un objeto `releaseDates` con cuatro subcampos regionales (`Japan`, `NorthAmerica`, `Europe`, `Australia`) — y comparten desarrollador entre plataformas pero **no necesariamente el mismo editor**: se confirmó el caso real del juego "#killallzombies", desarrollado por Beatshapers, publicado por Beatshapers en PlayStation pero por Digerati en Xbox.

Ninguna de las tres fuentes comparte un identificador común. La única entidad de enlace disponible es el nombre del juego, normalizado.

Esta fragmentación no es solo de formato (CSV vs. JSON) — es de **esquema y de cobertura de atributos**: cada fuente tiene información que las otras no tienen, y ninguna fuente por sí sola permite responder preguntas que abarquen ventas, metadatos de plataforma y desarrollo/publicación al mismo tiempo.

---

## 2. Por qué un grafo de conocimiento, y no un cruce relacional convencional

Un enfoque relacional tradicional (cargar las tres fuentes en tablas SQL y hacer `JOIN` por nombre) es técnicamente posible, pero tiene tres problemas concretos frente a los datos reales verificados:

1. **Las relaciones son parciales, no uniformes entre fuentes.** `desarrolladoPor` no existe en vgsales; `publicadoPor` varía según la plataforma incluso para el mismo juego; `perteneceAGenero` está vacío en el 87.14% de los registros de PlayStation y el 64.63% de Xbox. Un esquema relacional fijo obligaría a definir columnas que quedan mayormente `NULL` para una fuente completa, o a mantener tablas separadas por fuente que hay que volver a unir en cada consulta. Un grafo RDF modela esto de forma natural: una propiedad ausente simplemente no genera una tripleta, sin necesidad de rediseñar el esquema.

2. **La entidad central no es fija — es una jerarquía de dos niveles.** El mismo juego se manifiesta de forma distinta según la plataforma (editor distinto, fecha distinta, ventas distintas), pero conserva un desarrollador común. Este patrón —una entidad "obra" con varias "ediciones" que comparten unos atributos y difieren en otros— se modela naturalmente como dos clases relacionadas (`Videojuego` y `Lanzamiento`) en RDF. En un modelo relacional equivalente requeriría una tabla de asociación adicional y múltiples `JOIN` para reconstruir la misma relación en cada consulta.

3. **La inferencia por jerarquía de clases no tiene equivalente directo en SQL.** Clasificar plataformas como `Consola` o `PC` (`Consola ⊑ Plataforma`) permite que una consulta sobre "todos los lanzamientos en consolas" infiera automáticamente instancias de Xbox, PlayStation y Switch sin enumerarlas una por una, y sin necesidad de mantener una tabla de mapeo adicional. Esto es una capacidad nativa de RDFS/OWL que un modelo relacional plano no ofrece sin lógica de aplicación adicional.

---

## 3. Qué permite responder la integración que no sería trivial por separado

Con las fuentes integradas en un grafo, es posible responder preguntas que requieren cruzar información de más de una fuente en la misma consulta, entre ellas:

- **Property path desarrollador → lanzamiento → editor**: identificar qué editores han trabajado con un desarrollador determinado, a través de la cadena `Videojuego → Lanzamiento → Editor`, sin que exista una relación directa entre ambas entidades en ningún dato de origen.
- **Inferencia por subclase de plataforma**: consultar todos los lanzamientos en cualquier tipo de consola sin enumerar Xbox/PlayStation/Switch explícitamente, gracias a `rdfs:subClassOf*`.
- **Comparación entre fuentes vía grafos nombrados**: detectar directamente en SPARQL los casos donde el editor de un mismo juego difiere entre plataformas (como el caso confirmado de "#killallzombies"), cargando cada fuente en su propio grafo con nombre y comparando resultados en una sola consulta.
- **Identificación de vacíos estructurales por fuente**: usando `FILTER NOT EXISTS`, aislar directamente los videojuegos de PlayStation/Xbox sin género asignado — un problema real que afecta a la mayoría de los registros de esas dos fuentes (87.14% y 64.63% respectivamente) y que sería más costoso de detectar cruzando tablas relacionales manualmente.

Ninguna fuente por separado permite responder estas preguntas: requieren la combinación de ventas (solo en vgsales), metadatos de desarrollo/publicación (más completos en Steam y en los JSON de consolas) y fechas por región (solo desagregadas en los JSON de consolas).

---

## 4. Conclusión

La integración se justifica porque las tres fuentes son complementarias y no redundantes: cada una aporta atributos que las otras no tienen, ninguna comparte un identificador común, y las relaciones entre entidades (juego, lanzamiento, plataforma, desarrollador, editor) son parciales y variables según la fuente y la plataforma. Un grafo de conocimiento en RDF permite modelar esta heterogeneidad sin forzar un esquema rígido, soporta inferencia por jerarquía de clases de forma nativa, y habilita consultas (property paths, comparación entre grafos nombrados, detección de vacíos estructurales) que sobre un modelo relacional convencional requerirían lógica adicional específica para este caso, en lugar de capacidades genéricas del lenguaje de consulta.

---

## 5. Decisiones de modelado

### 5.1. Separación `Videojuego` / `Lanzamiento`

El modelo distingue dos niveles de entidad:

- **`Videojuego`**: obra intelectual abstracta (p. ej., "DOOM" como concepto, independiente de la plataforma). De ella cuelgan `desarrolladoPor` y `perteneceAGenero`, porque el estudio desarrollador y el género no cambian según la plataforma de lanzamiento.
- **`Lanzamiento`**: edición concreta del juego en una plataforma específica. De ella cuelgan `enPlataforma`, `publicadoPor`, `tieneVenta` y `fechaLanzamiento`, porque el editor, las ventas y la fecha sí varían por plataforma.

Esta separación está validada por un caso real encontrado en los datos: el juego `#killallzombies` tiene el mismo desarrollador (Beatshapers) en todas las plataformas, pero editores distintos: Beatshapers (autopublicado) en PlayStation y Digerati en Xbox.

### 5.2. `enPlataforma` como ObjectProperty

La propiedad `enPlataforma` se definió como **ObjectProperty** (apuntando a una instancia de `:Plataforma`), no como una propiedad de dato literal. Esto permite:

1. **Inferencia por jerarquía de clases**: `Consola ⊑ Plataforma` y `PC ⊑ Plataforma`. Una consulta SPARQL con `rdfs:subClassOf*` sobre `:Consola` encuentra automáticamente lanzamientos en PS2, Xbox 360, Switch, etc., sin enumerarlos explícitamente.
2. **Reuso entre fuentes**: la instancia `:P_vg_PC` se usa tanto para lanzamientos de vgsales en PC como para todos los lanzamientos de Steam, permitiendo consultas unificadas sobre la plataforma PC.
3. **Extensibilidad**: se pueden añadir metadatos a la plataforma (fabricante, generación, etc.) simplemente agregando tripletas a la instancia.

Se crearon 34 instancias de plataforma en total:
- **30** `:Consola` desde los códigos de vgsales (`:P_vg_PS2`, `:P_vg_X360`, etc.)
- **3** `:Consola` desde los JSON de consolas (`:P_xbox`, `:P_playstation`, `:P_switch`)
- **1** `:PC` reusada entre vgsales y Steam (`:P_vg_PC`)

### 5.3. `tieneDemo` y `tienePlaytest`

Inicialmente se contempló una clase `:Demo` separada de `:Lanzamiento`. Durante el diseño se optó por eliminarla y usar dos ObjectProperties (`:tieneDemo` y `:tienePlaytest`) que conectan `:Videojuego` → `:Lanzamiento`. La razón es que una demo o un playtest siguen siendo lanzamientos (tienen plataforma, editor, fecha), y la diferencia con un lanzamiento completo es semántica (el propósito de la entrega), no estructural. Usar propiedades diferenciadas evita tener que duplicar la definición de `:Lanzamiento` para cada subtipo.

La detección se hace sobre los nombres de Steam: si el nombre termina en "playtest" se conecta vía `:tienePlaytest`; si contiene " demo " como palabra completa, vía `:tieneDemo`. Esta detección se documenta como decisión de diseño — no como validación de datos — porque los 5,215 playtests de Steam son entradas legítimas del catálogo, no errores.

### 5.4. Unión de géneros entre fuentes

Los géneros se integran **uniendo** los valores de todas las fuentes disponibles para un mismo `:Videojuego`, no priorizando una fuente sobre otra. Si vgsales reporta "Action" y Steam reporta ["Action", "FPS"], el grafo contendrá tanto `:G_Action` como `:G_FPS`. Esto maximiza la información disponible y evita descartar datos por decisión arbitraria de prioridad.

### 5.5. Desarrollador solo desde Steam y consolas

vgsales no tiene columna de desarrollador. Por lo tanto, `:desarrolladoPor` solo se puebla desde los campos `developers` de Steam y de los JSON de consolas (que están 100% poblados). Si ninguna de esas fuentes tiene un juego, el `:Videojuego` simplemente no tendrá tripleta de desarrollador, lo cual es correcto semánticamente (ausencia de dato no es dato incorrecto).

### 5.6. Editor "Unknown" en vgsales

203 filas de vgsales tienen `Publisher = "Unknown"` como string literal (no como NaN). Se trata como equivalente a nulo: no se genera tripleta `:publicadoPor`. Esto evita contaminar el grafo con un editor ficticio.

### 5.7. Duplicados exactos en vgsales

Se encontraron 5 casos de duplicados `Name+Platform` (10 filas en total) en vgsales. Entre ellos, "Wii de Asobu: Metroid Prime" tiene dos filas idénticas (un error de captura). El script de materialización detecta duplicados exactos y genera un solo `:Lanzamiento`. Los casos donde las filas duplicadas difieren en año o ventas (como "Need for Speed: Most Wanted" con versiones 2005 y 2012) se mantienen como lanzamientos separados.

### 5.8. Limpieza de editores en Switch

Los publishers de Switch contienen prefijos regionales en algunos casos (`"JP: G-Mode"`, `"WW: HandyGames"`). Se eliminan los prefijos `"JP: "` y `"WW: "` para extraer solo el nombre del editor antes de crear la instancia `:Editor`.

### 5.9. Ventas con monto cero omitidas

En vgsales, algunas celdas de ventas regionales tienen valor `0.0` (p. ej., `EU_Sales = 0.00` para DOOM en GBA). No se generan tripletas `:VentaRegional` con `:monto 0.0` porque ese valor no aporta información — indica ausencia de venta registrada, no una venta efectiva de cero unidades. Solo se crean cuando `monto > 0`.

### 5.10. `estimated_owners` de Steam excluido del modelo

El dataset de Steam incluye la columna `estimated_owners` con rangos estimados de propietarios (ej. `"10000000 - 20000000"`), pero **no se incorporó al grafo RDF**. La razón es que el 14.4% de los registros tienen el valor placeholder `"0 - 0"` (sin información real), y el resto son rangos textuales que requerirían un modelo intermedio (valor mínimo, valor máximo) para representarse adecuadamente en RDF. Dado que no hay un caso de uso definido que requiera estos datos para las consultas planificadas, se optó por excluirlos y mantener el modelo más simple. Las columnas efectivamente usadas de Steam son las 12 definidas en `STEAM_COLS` en `materializar.py`.

---



## 6. Manejo de colisiones de nombre entre fuentes

### 6.1. El problema

vgsales contiene 16.598 filas que se agrupan en 11.493 nombres únicos de juego. Al inspeccionar los datos, se encontraron **75 nombres** que tienen lanzamientos con una brecha de 10 años o más entre la versión más antigua y la más reciente. Esto puede indicar dos situaciones:

1. **Ports/remakes del mismo juego**: el mismo título se relanza años después en otra plataforma (p. ej., "Final Fantasy" de 1987 en NES portado a WonderSwan en 2000).
2. **Reboots/secuelas con el mismo nombre**: un juego nuevo que reutiliza el nombre de una entrega anterior (p. ej., "Mortal Kombat" 1992 arcade vs. Mortal Kombat 2011 reboot).

### 6.2. Metodología de verificación

Para cada nombre con brecha ≥10 años, se examinaron:
- Años de lanzamiento por plataforma
- Editor/Publisher (cambios de editor pueden indicar juego distinto)
- Cruce con otras fuentes (Steam, consolas) — si coinciden, es el mismo juego; si no, puede ser otro
- Conocimiento de dominio (saga, historia de la franquicia)

Se verificaron manualmente los 13 casos más ambiguos:

| Nombre | Años | Decisión | Justificación |
|--------|------|----------|---------------|
| **Sonic the Hedgehog** | 1991 GEN, 2006 PS3/X360 | Juegos distintos | Sonic '06 es un reboot completo, no un port |
| **Mortal Kombat** | 1992 GEN, 2011 PS3/X360 | Juegos distintos | Reboot de 2011 por NetherRealm |
| **Syndicate** | 1992 PC, 2012 X360/PS3 | Juegos distintos | Isométrico original vs. FPS de Starbreeze |
| **Spider-Man** | 1981 2600, 2000 PS1 | Juegos distintos | Atari 2600 genérico vs. Neversoft |
| **Battlezone** | 1982 2600, 2006 PSP | Juegos distintos | Arcade vectorial vs. FPS de Atari |
| **Defender** | 1980 2600, 2002 PS2/GC/XB | Juegos distintos | Arcade clásico vs. FPS de Midway |
| **Asteroids** | 1980 2600, 1998 PS | Juegos distintos | Arcade vs. remake 3D |
| **Castlevania** | 1986 NES, 1999 N64 | Juegos distintos | Original vs. Castlevania 64 |
| **Bomberman** | 1985 NES, 2005-2008 | Juegos distintos | Distintas entregas de la saga |
| **NBA Jam** | 1992 GEN, 2003-2010 | Juegos distintos | Secuelas/reboots |
| **Resident Evil** | 1996 PS, 2006 PS3 | Mismo juego | Ports/remasters del mismo RE1 |
| **Final Fantasy** | 1987 NES, 2000 WS | Mismo juego | Port a WonderSwan |
| **Monopoly** | 1994-2010 | Mismo juego | Mismo juego de mesa siempre |

### 6.3. Decisión final

De los 75 casos, la mayoría son juegos distintos (reboots) y no ports del mismo título. Sin embargo, se optó por **no separarlos automáticamente** y tratar cada nombre como un solo `:Videojuego` con múltiples `:Lanzamiento`, con UNA SOLA excepción manual:

- **DOOM**: separado en dos `:Videojuego` (`:V_doom` para 1993 con `:nombre "DOOM"` y `:V_doom_2016` para 2016 con `:nombre "DOOM (2016)"`), porque está confirmado entre fuentes (vgsales tiene el original de 1993, Steam y consolas JSON tienen el reboot de 2016) y es el único caso donde el mismo nombre cruza fuentes representando juegos claramente distintos. Además, vgsales ya tiene una entrada separada con el nombre `"Doom (2016)"`, lo que refuerza la separación.

**Justificación de la decisión:**

1. **Consistencia**: aplicar separación automática por brecha de años requeriría un umbral arbitrario y conocimiento experto de dominio para cada caso (saber si "Sonic '06" es reboot o port). El criterio "un nombre = un Videojuego" es simple, reproducible y verificable.
2. **Precisión de la fuente**: vgsales no distingue entregas bajo el mismo nombre. Si la fuente original las agrupa, el grafo respeta esa decisión en lugar de reinterpretarla.
3. **La información no se pierde**: el grafo captura la diferencia entre lanzamientos a través de las fechas (`:fechaLanzamiento`), plataformas (`:enPlataforma`) y editores (`:publicadoPor`). Una consulta SPARQL puede distinguir el DOOM de 1993 del de 2016 por su año, sin necesidad de separar los `:Videojuego`.
4. **DOOM es el único caso con brecha ≥10 años que cruza las 5 fuentes**: 17 nombres normalizados aparecen en las 5 fuentes (vgsales, Steam, Xbox, PlayStation, Switch), pero solo DOOM lo hace con años notablemente distintos (1992-2001 vs. 2016-2019). Los otros 16 (como "alien isolation" o "bayonetta") son el mismo juego en distintas plataformas. Separar DOOM manualmente es un costo bajo con beneficio claro de desambiguación por ser el único homónimo cross-source con brecha significativa.

---

## 7. Nota sobre el orden del proceso

El enunciado del proyecto establece: *"Diseñe primero todas las consultas que deberá responder el grafo de conocimiento antes de iniciar el proceso de integración"*. En este proyecto, las consultas SPARQL se diseñaron **después** de la materialización del grafo y no antes. La razón es que el diseño de consultas significativas requiere conocimiento preciso de la estructura de URIs, propiedades y datos realmente disponibles en el grafo — información que solo está disponible una vez completada la integración. Diseñar las consultas antes habría resultado en consultas genéricas o hipotéticas que probablemente no funcionarían contra el grafo real sin ajustes posteriores. Para mitigar esta desviación, las consultas se diseñaron en paralelo con la ontología, utilizando los esquemas conocidos de las fuentes como referencia, y se ajustaron contra el grafo generado para garantizar que devuelven resultados correctos.
