# Informe técnico consolidado: Grafo de conocimiento sobre videojuegos

**Fecha:** 12 de julio de 2026
**Fuentes verificadas:** vgsales.csv, games_march2025_full.csv (Steam), xbox_games.json, playstation_games.json, switch_games.json

Este documento consolida los hallazgos obtenidos de la **inspección real** de los datos (no del informe teórico inicial), las decisiones de diseño tomadas a partir de esos hallazgos, la ontología confirmada, las validaciones SHACL propuestas y las consultas SPARQL planificadas. Cada afirmación distingue entre lo verificado con código sobre los datos reales y lo que aún está pendiente de confirmar.

---

## 1. Resumen ejecutivo

El informe teórico inicial de fuentes de datos describía la estructura y problemas de calidad de forma aproximada. Al inspeccionar los archivos reales se confirmaron varios de esos supuestos, se corrigieron otros que resultaron inexactos, y aparecieron hallazgos nuevos no anticipados. Este documento reemplaza al informe teórico como referencia para el desarrollo del proyecto.

**Fuentes finales seleccionadas:**
1. `vgsales.csv` (CSV, 16,598 filas, 11 columnas)
2. `games_march2025_full.csv` de Steam (CSV, 94,948 filas, 47 columnas — se usa un subconjunto de 12)
3. Conjunto de tres JSON de consolas: `xbox_games.json` (2,279 registros), `playstation_games.json` (1,151 registros), `switch_games.json` (1,043 registros) — mismo formato, misma API de origen

Esto cumple los requisitos del enunciado: 3 fuentes independientes, formatos CSV y JSON, ≥5 atributos por fuente, valores faltantes/erróneos genuinos y presencia de una entidad común (nombre del videojuego) para integración.

---

## 2. Hallazgos reales por fuente

### 2.1. Steam (`games_march2025_full.csv`)

| Campo | Lo que decía el informe teórico | Dato real verificado |
|---|---|---|
| `metacritic_score` | "0 si no tiene score" | **96.2% de los registros son 0** (91,372 de 94,948 filas). No es un caso ocasional, es el patrón dominante. |
| `estimated_owners` | rango estimado | **14.4% de los registros tienen el valor literal `"0 - 0"`** (13,656 de 94,948 filas) — un placeholder sin información real, disfrazado de rango válido |
| `genres` | "puede estar vacío" | 6.8% vacío (`[]`) en la versión `_full` (vs. 0.4% en la versión `_cleaned`, que resultó estar filtrada) |
| `developers` / `publishers` | "normalmente uno o varios nombres" | 6.8% / 7.2% vacíos en la versión `_full` |
| Nulos detectados por `pandas.isna()` en las 12 columnas núcleo usadas | — | **0% en ambas versiones del archivo** — esto no significa datos limpios, significa que los valores faltantes están representados como placeholders (`0`, `"0 - 0"`, `[]`) en lugar de `NaN` real |

**Decisión de diseño:** se usa `games_march2025_full.csv` en lugar de la versión `_cleaned`, porque tiene consistentemente más valores vacíos genuinos en `genres`, `developers` y `publishers` (relevante para las validaciones de obligatoriedad).

**Nota:** el archivo pesa ~450 MB con las 47 columnas originales; se debe leer con `pandas.read_csv(..., usecols=[...])` limitando a las 12 columnas que realmente se usan en el modelo (`STEAM_COLS` en `materializar.py`) para que el procesamiento sea manejable.

### 2.2. vgsales.csv

| Campo | Lo que decía el informe teórico | Dato real verificado |
|---|---|---|
| `Year` nulo | "~1-2%" | **1.63% (271 de 16,598 filas)** — coincide con lo esperado |
| `Publisher` nulo (`NaN` real) | "una minoría" | **0.35% (58 filas)** |
| `Publisher` con valor `"Unknown"` | no mencionado | **Hallazgo nuevo**: se cuantificó sobre el archivo completo: **203 filas (1.22%)** tienen `Publisher = "Unknown"` como string literal, no como `NaN`. Se tratan como equivalente a nulo. |
| Duplicados `Name + Platform` | no mencionado | **Hallazgo nuevo**: se cuantificó sobre el archivo completo: **10 filas duplicadas (5 casos)**, de las cuales solo 1 caso es idéntico en todos los campos (`Wii de Asobu: Metroid Prime`). Los otros 4 casos difieren en año o ventas y se conservan como lanzamientos separados. |
| Estructura por fila | "cada fila es un registro" | Confirmado y relevante: cada fila representa una combinación juego+plataforma (un "lanzamiento"), no el juego como concepto único — 16,598 filas mapean a solo 11,493 nombres únicos |

### 2.3. JSON de consolas (Xbox, PlayStation, Switch)

| Campo | Lo que decía el informe teórico | Dato real verificado |
|---|---|---|
| `genre` vacío | "común en PlayStation y Xbox" | **Confirmado y mucho más severo de lo sugerido**: Xbox 64.63%, PlayStation 87.14%. Switch, en cambio, **0% vacío** — un contraste no anticipado por el informe teórico. |
| `developers` / `publishers` vacío | no se cuantificaba | **0% vacío en las tres consolas** — completamente poblado, contrario a lo que se podría asumir dado que `genre` sí tiene huecos masivos |
| `releaseDates` con `"Unreleased"`/`"TBA"` | mencionado como problema | Confirmado, pero desigual por región: Japón entre 42-48%, mientras que Norteamérica/Europa/Australia rondan 4-10% |
| Nombres duplicados | no mencionado | Mínimo: Xbox 1/2279, PlayStation 1/1151, Switch 2/1043 — no representa un problema significativo |
| Formato de `publishers` en Switch | no mencionado | **Hallazgo nuevo**: algunos valores mezclan región y nombre en el mismo string, ej. `["JP: G-Mode", "WW: Xseed Games"]` — requiere limpieza antes de extraer el nombre del editor |

---

## 3. Decisiones de preparación de datos derivadas de estos hallazgos

1. **Deduplicar vgsales por `Name + Platform`** antes de materializar — verificar el alcance real sobre el archivo completo y documentar los duplicados encontrados como el "error corregido manualmente" que exige el enunciado.
2. **Normalizar `publishers` de Switch** eliminando prefijos regionales (`"JP: "`, `"WW: "`) antes de cargar al grafo.
3. **Tratar `metacritic_score == 0` como valor ausente**, no como score real, en las validaciones y en las consultas de agregación que lo usen.
4. **Tratar `estimated_owners == "0 - 0"` como valor ausente.**
5. **Tratar `Publisher == "Unknown"` (vgsales) como equivalente a nulo**, junto con los `NaN` reales, al aplicar la validación de obligatoriedad.
6. ~~Aprovechar `developers`/`publishers` completos en las tres consolas como señal secundaria de desambiguación en el entity-linking por nombre~~ — **Descartado**: el matching final solo usa nombres normalizados (coincidencia exacta). Los developers/publishers no intervinieron en el enlace, solo se usan para poblar el grafo post-enlace.

---

## 4. Ontología confirmada

```
Videojuego
   ├─ perteneceAGenero → Genero
   ├─ desarrolladoPor → Desarrollador
   └─ tieneLanzamiento → Lanzamiento
                            ├─ enPlataforma → Plataforma (Consola | PC)
                            ├─ publicadoPor → Editor
                            ├─ tieneVenta → VentaRegional
                            │                  ├─ region (NA/EU/JP/Other)
                            │                  └─ monto (decimal)
                            ├─ fechaLanzamiento → LanzamientoRegional
                            │                     ├─ region
                            │                     └─ fecha
                            ├─ precio (decimal)
                            ├─ metacriticScore (integer, 1-100)
                            ├─ reseñasPositivas (integer) / reseñasNegativas (integer)
                            ├─ tiempoJuego (integer, minutos)
                            └─ peakCcu (integer)
   ├─ tieneDemo → Lanzamiento (demo gratuita)
   └─ tienePlaytest → Lanzamiento (playtest)
```

Jerarquía de clases para inferencia: `Consola ⊑ Plataforma`, `PC ⊑ Plataforma`.

### 4.1. Justificación de la separación `Videojuego` / `Lanzamiento`

`desarrolladoPor` permanece en `Videojuego` porque el estudio que desarrolla el juego no cambia según la plataforma. `publicadoPor`, en cambio, cuelga de `Lanzamiento` porque el editor sí puede variar por plataforma — confirmado con el ejemplo real del informe teórico original: el juego "#killallzombies" tiene el mismo desarrollador (Beatshapers) pero editores distintos en PlayStation ("Beatshapers", autopublicado) y en Xbox ("Digerati").

### 4.2. Mapeo de campos reales a la ontología

| Clase / propiedad | vgsales.csv | Steam (subconjunto) | JSON consolas |
|---|---|---|---|
| `Videojuego` (nombre) | `Name` | `name` | `name` |
| `perteneceAGenero` | `Genre` (1 valor) | `genres` (lista) | `genre` (lista, con huecos importantes en Xbox/PlayStation) |
| `desarrolladoPor` | **no existe** | `developers` | `developers` (100% poblado) |
| `Lanzamiento.enPlataforma` | `Platform` (1 fila = 1 lanzamiento) | implícito (`windows`/`mac`/`linux`) | implícito por archivo (Xbox/PlayStation/Switch) |
| `Lanzamiento.publicadoPor` | `Publisher` | `publishers` | `publishers` (100% poblado, requiere limpieza en Switch) |
| `VentaRegional` | `NA_Sales`, `EU_Sales`, `JP_Sales`, `Other_Sales` | no existe | no existe |
| `LanzamientoRegional` | solo `Year` (sin desagregar) | `release_date` (fecha única) | `releaseDates` (por región: Japan/NorthAmerica/Europe/Australia) |

### 4.3. Limitaciones reconocidas de la ontología actual

- Atributos exclusivos de Steam (`precio`, `metacriticScore`, `reseñasPositivas`, `reseñasNegativas`, `tiempoJuego`, `peakCcu`) están modelados como propiedades de dato sobre `:Lanzamiento` en la ontología final. Esto permite que cada lanzamiento de Steam tenga sus propias métricas sin depender de clases adicionales.
- El género a nivel de `Videojuego` (y no de `Lanzamiento`) es una simplificación: distintas fuentes pueden reportar géneros distintos para el mismo juego. Se optó por **unión de valores** de todas las fuentes disponibles para maximizar la información, documentado en la evidencia A §5.4.

---

## 5. Validaciones SHACL (los 4 tipos exigidos, basados en hallazgos reales)

| Tipo de validación | Shape concreta | Evidencia real que la sustenta |
|---|---|---|
| Obligatoriedad (`sh:minCount`) | `Videojuego` debe tener `perteneceAGenero` | Xbox 64.63% y PlayStation 87.14% de `genre` vacío — casos abundantes y reales |
| Tipo de literal (`sh:datatype`) | `VentaRegional.monto` debe ser `xsd:decimal` | Confirmado: las 4 columnas de venta en vgsales son `float64` consistentes |
| Rango de valores (`sh:minInclusive` / `sh:maxInclusive`) | `Lanzamiento.metacriticScore` entre 1 y 100 (excluyendo 0 como "sin dato") | 96.2% de los registros de Steam son 0 (91,372 de 94,948 filas), confirmado sobre el archivo completo |
| Shape cerrada (`sh:closed true`) | `VentaRegional` solo puede tener `region` y `monto` | Decisión de diseño para evitar propiedades no previstas por errores de transformación |

---

## 6. Consultas SPARQL planificadas

Prefijo usado en los ejemplos: `PREFIX : <http://example.org/videojuegos#>`

### 6.1. Consulta libre
Top 10 videojuegos por venta global total, con plataforma y editor.

```sparql
SELECT ?nombreJuego ?plataforma ?editor (SUM(?monto) AS ?ventaTotal)
WHERE {
  ?juego a :Videojuego ; :nombre ?nombreJuego ; :tieneLanzamiento ?lanzamiento .
  ?lanzamiento :enPlataforma ?p ; :publicadoPor ?e ; :tieneVenta ?venta .
  ?venta :monto ?monto .
  ?p :nombre ?plataforma . ?e :nombre ?editor .
}
GROUP BY ?nombreJuego ?plataforma ?editor
ORDER BY DESC(?ventaTotal)
LIMIT 10
```

### 6.2. Agregación (SUM)
Venta total agrupada por plataforma.

```sparql
SELECT ?plataforma (SUM(?monto) AS ?ventaTotalPlataforma)
WHERE {
  ?lanzamiento :enPlataforma ?p ; :tieneVenta ?venta .
  ?venta :monto ?monto . ?p :nombre ?plataforma .
}
GROUP BY ?plataforma
ORDER BY DESC(?ventaTotalPlataforma)
```

### 6.3. GROUP BY + HAVING
Géneros con más de N videojuegos asociados (N se ajusta según el volumen real del grafo cargado).

```sparql
SELECT ?genero (COUNT(DISTINCT ?juego) AS ?totalJuegos)
WHERE {
  ?juego a :Videojuego ; :perteneceAGenero ?g .
  ?g :nombre ?genero .
}
GROUP BY ?genero
HAVING (COUNT(DISTINCT ?juego) > 20)
ORDER BY DESC(?totalJuegos)
```

### 6.4. Property paths (con componente de inferencia)

```sparql
SELECT DISTINCT ?desarrollador ?editor
WHERE {
  ?juego :desarrolladoPor ?d ; :tieneLanzamiento/:publicadoPor ?e .
  ?d :nombre ?desarrollador . ?e :nombre ?editor .
}
```

Variante con inferencia real por subclases (`Consola ⊑ Plataforma`):

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?nombreJuego ?tipoPlataforma
WHERE {
  ?juego :nombre ?nombreJuego ; :tieneLanzamiento/:enPlataforma ?p .
  ?p a ?tipoPlataforma .
  ?tipoPlataforma rdfs:subClassOf* :Consola .
}
```

### 6.5. MINUS / FILTER NOT EXISTS
Videojuegos de PlayStation o Xbox sin género asignado (caso real, confirmado con 64.63%/87.14% de vacíos).

```sparql
SELECT ?nombreJuego
WHERE {
  ?juego a :Videojuego ; :nombre ?nombreJuego ; :tieneLanzamiento ?lanzamiento .
  ?lanzamiento :enPlataforma ?p .
  FILTER NOT EXISTS { ?juego :perteneceAGenero ?g . }
}
```

### 6.6. INSERT / DELETE / UPDATE
Corrección de un `Publisher = "Unknown"` detectado en validación, tras revisión manual.

```sparql
DELETE { ?lanzamiento :publicadoPor ?editorViejo . }
INSERT { ?lanzamiento :publicadoPor :EditorCorregido . }
WHERE {
  ?juego :nombre "Dinotopia: The Sunstone Odyssey" ; :tieneLanzamiento ?lanzamiento .
  ?lanzamiento :publicadoPor ?editorViejo .
  ?editorViejo :nombre "Unknown" .
}
```

### 6.7. Opcional: grafos nombrados
Comparar si el editor reportado para el mismo juego difiere entre fuentes (caso real documentado: "#killallzombies" con editores distintos en PlayStation y Xbox).

```sparql
SELECT ?nombreJuego ?editorXbox ?editorPlaystation
WHERE {
  GRAPH :xbox { ?juego :nombre ?nombreJuego ; :tieneLanzamiento/:publicadoPor ?eXbox . }
  GRAPH :playstation { ?juego :tieneLanzamiento/:publicadoPor ?ePs . }
  ?eXbox :nombre ?editorXbox . ?ePs :nombre ?editorPlaystation .
  FILTER (?editorXbox != ?editorPlaystation)
}
```

---

## 7. Verificaciones pendientes (aún no confirmadas con datos)

- ~~Cuantificar sobre el archivo completo de vgsales: total de duplicados `Name + Platform` y total de `Publisher == "Unknown"`.~~ **Resuelto: 203 Unknown, 10 filas duplicadas (5 casos).**
- ~~Confirmar si los duplicados de vgsales son idénticos en todos los campos (error de captura) o difieren en algún valor (ediciones/regionales distintas).~~ **Resuelto: solo 1 caso idéntico (Wii de Asobu: Metroid Prime); los otros 4 difieren en año/ventas.**
- Definir el umbral N para la validación `HAVING` una vez cargado el grafo completo.
- Confirmar que ninguna de las cinco fuentes coincide con las usadas durante las prácticas del curso.

---

## 8. Plan de trabajo sugerido (orden de prioridad hacia el viernes 17 de julio)

1. Redactar la ontología formal en Turtle/OWL a partir de la sección 4.
2. Escribir el script de materialización (Python + rdflib) que aplique las correcciones de la sección 3.
3. Definir las shapes SHACL en Turtle a partir de la sección 5.
4. Cargar esquema + datos en Fuseki o GraphDB.
5. Ejecutar y ajustar las consultas de la sección 6 contra el grafo cargado.
6. Redactar el reporte de justificación (evidencia A) usando los hallazgos de las secciones 1-3 como respaldo.
