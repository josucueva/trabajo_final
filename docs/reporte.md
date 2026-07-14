# Reporte — Justificación de fuentes de datos

## 1. Datasets seleccionados

| Fuente | Formato | Registros | Aporte único | Errores conocidos |
|--------|---------|-----------|--------------|-------------------|
| Ventas globales (vgsales) | CSV | 16,598 | Ventas por región (NA, EU, JP, Other) | `Year` nulo (1.6%), `Publisher` = `"Unknown"` (1.2%) |
| Steam | CSV | 94,948 | Precio, reseñas, tiempo de juego, desarrollador | `metacritic_score=0` (96.2%), `estimated_owners="0 - 0"` (14.4%) |
| Consolas (Xbox, PS, Switch) | JSON | 2,279 / 1,151 / 1,043 | Fechas de lanzamiento por 4 regiones | `genre` vacío en Xbox (64.6%) y PS (87.1%), fechas `"Unreleased"` |

**Complementariedad:** Ninguna fuente por sí sola permite cruzar ventas + métricas digitales + fechas regionales.

## 2. Justificación del grafo de conocimiento

- **Relaciones parciales:** `desarrolladoPor` solo está en Steam/consolas; `publicadoPor` varía por plataforma; `perteneceAGenero` está ausente en 64-87% de consolas. Un grafo RDF maneja esto sin columnas NULL.
- **Jerarquía de dos niveles:** El mismo juego (Videojuego) puede tener múltiples Lanzamientos con distintos editores, fechas y ventas según la plataforma.
- **Inferencia nativa:** La jerarquía `Consola ⊑ Plataforma` permite consultas sobre todas las consolas sin enumerarlas explícitamente.

## 3. Problemas de calidad identificados

| Problema | Fuente(s) | Tratamiento |
|---|---|---|
| `Year` nulo | Ventas | Se omite la fecha |
| `Publisher` = "Unknown" o NaN | Ventas | No se añade editor |
| `metacritic_score = 0` (placeholder) | Steam | Se omite la propiedad |
| Listas serializadas (genres, developers) | Steam | Parseo con `ast.literal_eval` |
| `genre` vacío | Xbox (64.6%), PS (87.1%) | Se omite el género |
| Fechas "Unreleased"/"TBA" | Consolas (Japón 42-48%) | Se descartan |
| Publishers con prefijo regional | Switch | Limpieza de prefijos |
| Nombres con TM/®/apóstrofes Unicode | Steam | Normalización en matching |
| Duplicados de nombre+plataforma | Ventas | Deduplicación por clave compuesta |
| DOOM (1993) y DOOM (2016) | Todas | Desambiguación manual en código |

