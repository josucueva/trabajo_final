# Grafo de Conocimiento sobre Videojuegos

Proyecto final — Web Semantica

Integración de tres fuentes de datos independientes (vgsales, Steam, consolas) en un grafo RDF para consultas SPARQL con inferencia.

## Estructura del proyecto

```
trabajo_final/
├── src/                    # Codigo fuente principal
│   ├── materializar.py     # Materializacion de datos a RDF
│   ├── match.py            # Entity linking por nombre normalizado
│   └── validar_ttl.py      # Validador sintactico de Turtle
├── ontology/               # Ontologia y validacion
│   ├── ontologia.ttl       # Esquema OWL del grafo
│   └── validacion_shacl.ttl # Shapes SHACL (4 validaciones)
├── data/                   # Fuentes de datos originales
│   ├── vgsales.csv
│   ├── games_march2025_full.csv
│   ├── xbox_games.json
│   ├── playstation_games.json
│   └── switch_games.json
├── output/                 # Datos generados
│   └── datos_integrados.ttl # Grafo RDF materializado
├── queries/                # Consultas SPARQL
│   ├── 01_libre.sparql
│   ├── 02_agregacion.sparql
│   ├── 03_groupby_having.sparql
│   ├── 04_property_paths.sparql
│   ├── 04b_property_paths_inferencia.sparql
│   ├── 05_filter_not_exists.sparql
│   ├── 06_insert_delete.sparql
│   ├── 06_verificacion_update.sparql
│   └── 07_grafos_nombrados.sparql
├── matching/               # Datos de matching entre fuentes
│   └── matches.json
├── analysis/               # Scripts de analisis exploratorio
│   ├── inspeccionar_vgsales.py
│   ├── inspeccionar_steam.py
│   ├── inspeccionar_consolas.py
│   └── ...
├── docs/                   # Documentacion
│   └── reporte.md
├── evidence/               # Capturas de pantalla (GraphDB, OpenRefine)
├── problem.md              # Enunciado del proyecto
└── requirements.txt        # Dependencias Python
```

## Requisitos

- Python 3.13+
- GraphDB Free (para carga, validacion SHACL y consultas)
- OpenRefine (opcional, para limpieza exploratoria)

```bash
pip install -r requirements.txt
```

## Uso

1. **Materializar**: `python src/materializar.py`
2. **Validar TTL**: `python src/validar_ttl.py ontology/ontologia.ttl`
3. **Cargar en GraphDB**: importar `ontology/ontologia.ttl` + `output/datos_integrados.ttl`
4. **Validar SHACL**: cargar `ontology/validacion_shacl.ttl` en Validate → SHACL
5. **Consultar**: ejecutar los archivos `.sparql` en el SPARQL editor de GraphDB

## Evidencias para entrega

| Evidencia | Archivo |
|---|---|
| A — Justificacion | `docs/reporte.md` |
| B — Scripts | `src/`, `analysis/` |
| C — Turtle | `output/datos_integrados.ttl` |
| D — Consultas SPARQL | `queries/` |
