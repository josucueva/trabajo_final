# Reporte — Grafo de conocimiento sobre videojuegos

## 1. Datasets seleccionados

Se usan 3 fuentes independientes, dos formatos (CSV, JSON), todas con ≥5 atributos y valores erróneos/faltantes reales.

| Fuente | Formato | Registros | Aporte único | Errores conocidos |
|--------|---------|-----------|--------------|-------------------|
| `vgsales.csv` | CSV | 16,598 | Ventas por región (NA, EU, JP, Other) | `Year` nulo (1.6%), `Publisher` = `"Unknown"` (1.2%) y NaN (0.35%), 5 duplicados |
| `games_march2025_full.csv` (Steam) | CSV | 94,948 | Precio, reseñas, tiempo de juego, `peak_ccu`, desarrollador | `metacritic_score=0` (96.2% — no es nota real), `estimated_owners="0 - 0"` (14.4%), campos serializados que requieren parseo |
| `xbox_games.json` / `playstation_games.json` / `switch_games.json` | JSON | 2,279 / 1,151 / 1,043 | Fechas de lanzamiento por 4 regiones, `developers`/`publishers` 100% poblados | `genre` vacío en Xbox (64.6%) y PS (87.1%), fechas `"Unreleased"`/`"TBA"` (42-48% en Japón), publishers de Switch con prefijo regional |

**Complementariedad:** Ninguna fuente sola permite cruzar ventas + métricas digitales + fechas regionales. La entidad común es el nombre del juego, normalizado para matching exacto.
