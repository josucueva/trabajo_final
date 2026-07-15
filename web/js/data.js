/* ============================================================
   data.js — Configuracion, ontologia y consultas predefinidas
   ============================================================ */

const CONFIG = {
    // SPARQL endpoint — configurar cuando GraphDB este disponible
    sparqlEndpoint: '',
    // Nombre del repositorio en GraphDB
    repository: 'videojuegos',
    // Indice de busqueda local (cargado bajo demanda)
    searchIndexUrl: 'js/search-index.json',
};

// Consulta de busqueda por nombre (usada desde la barra de busqueda)
const SEARCH_QUERY = `
PREFIX ex: <http://example.org/videojuegos#>
SELECT ?juego ?nombre
  (GROUP_CONCAT(DISTINCT ?plataforma; SEPARATOR=", ") AS ?plataformas)
  (GROUP_CONCAT(DISTINCT ?genero; SEPARATOR=", ") AS ?generos)
  (GROUP_CONCAT(DISTINCT ?desarrollador; SEPARATOR=", ") AS ?desarrolladores)
  (GROUP_CONCAT(DISTINCT ?editor; SEPARATOR=", ") AS ?editores)
  (GROUP_CONCAT(DISTINCT ?ventaStr; SEPARATOR=", ") AS ?ventasStr)
  (GROUP_CONCAT(DISTINCT ?fechaStr; SEPARATOR=", ") AS ?fechasStr)
WHERE {
  ?juego a ex:Videojuego ;
         ex:nombre ?nombre .
  OPTIONAL { ?juego ex:tieneLanzamiento ?l .
             ?l ex:enPlataforma ?p . ?p ex:nombre ?plataforma .
             OPTIONAL { ?l ex:publicadoPor ?e . ?e ex:nombre ?editor . }
             OPTIONAL { ?l ex:fechaLanzamiento ?lr . ?lr ex:fecha ?fecha .
                        BIND(STR(?fecha) AS ?fechaStr) }
             OPTIONAL { ?l ex:tieneVenta ?v . ?v ex:monto ?monto .
                        BIND(CONCAT(STR(?monto), "M") AS ?ventaStr) } }
  OPTIONAL { ?juego ex:perteneceAGenero ?g . ?g ex:nombre ?genero . }
  OPTIONAL { ?juego ex:desarrolladoPor ?d . ?d ex:nombre ?desarrollador . }
  FILTER (CONTAINS(LCASE(?nombre), LCASE(_QUERY_)))
}
GROUP BY ?juego ?nombre
ORDER BY ?nombre
LIMIT 30
`;

// Consulta para obtener detalles completos de un juego (por URI)
const DETAIL_QUERY = `
PREFIX ex: <http://example.org/videojuegos#>
SELECT ?propiedad ?valor ?tipo WHERE {
  { <_URI_> ?propiedad ?valor . }
  UNION
  { ?s ?propiedad <_URI_> . }
  OPTIONAL { ?valor a ?tipo . }
  FILTER (?propiedad != ex:nombre)
  FILTER (?propiedad != RDF.type || EXISTS { <_URI_> RDF.type ?tipo })
}
ORDER BY ?propiedad
LIMIT 50
`;

const STATS = {
    triples: '2,386,659',
    entities: '330,652',
    games: '100,376',
    classes: '10',
    properties: '19',
    sources: '3',
};

/* ----------------------------------------------------------
   Datos de la ontologia
   ---------------------------------------------------------- */
const ONTOLOGY = {
    classes: [
        {
            name: 'Videojuego',
            description: 'Obra intelectual, independiente de la plataforma',
            type: 'owl:Class',
            properties: ['perteneceAGenero', 'desarrolladoPor', 'tieneLanzamiento', 'tieneDemo', 'tienePlaytest']
        },
        {
            name: 'Lanzamiento',
            description: 'Edicion especifica de un videojuego en una plataforma concreta',
            type: 'owl:Class',
            superClass: null,
            properties: ['enPlataforma', 'publicadoPor', 'tieneVenta', 'fechaLanzamiento', 'precio', 'metacriticScore', 'resenasPositivas', 'resenasNegativas', 'tiempoJuego', 'peakCcu']
        },
        {
            name: 'Plataforma',
            description: 'Clase padre para todos los tipos de plataforma',
            type: 'owl:Class',
            properties: []
        },
        {
            name: 'Consola',
            description: 'Plataforma de tipo consola (Xbox, PlayStation, Switch)',
            type: 'owl:Class',
            superClass: 'Plataforma',
            properties: []
        },
        {
            name: 'PC',
            description: 'Plataforma de tipo PC (Windows, Mac, Linux)',
            type: 'owl:Class',
            superClass: 'Plataforma',
            properties: []
        },
        {
            name: 'Genero',
            description: 'Categoria o genero de un videojuego',
            type: 'owl:Class',
            properties: []
        },
        {
            name: 'Desarrollador',
            description: 'Estudio o empresa que desarrollo el videojuego',
            type: 'owl:Class',
            properties: []
        },
        {
            name: 'Editor',
            description: 'Empresa que publico el lanzamiento en una plataforma',
            type: 'owl:Class',
            properties: []
        },
        {
            name: 'VentaRegional',
            description: 'Ventas de un lanzamiento en una region especifica',
            type: 'owl:Class',
            properties: ['region', 'monto']
        },
        {
            name: 'LanzamientoRegional',
            description: 'Fecha de lanzamiento en una region especifica',
            type: 'owl:Class',
            properties: ['region', 'fecha']
        }
    ],
    objectProperties: [
        { name: 'perteneceAGenero', domain: 'Videojuego', range: 'Genero', description: 'Genero(s) al que pertenece el videojuego' },
        { name: 'desarrolladoPor', domain: 'Videojuego', range: 'Desarrollador', description: 'Estudio que desarrollo el videojuego' },
        { name: 'tieneLanzamiento', domain: 'Videojuego', range: 'Lanzamiento', description: 'Asocia un videojuego con sus lanzamientos' },
        { name: 'enPlataforma', domain: 'Lanzamiento', range: 'Plataforma', description: 'Plataforma en la que se publico el lanzamiento' },
        { name: 'publicadoPor', domain: 'Lanzamiento', range: 'Editor', description: 'Empresa que publico el lanzamiento' },
        { name: 'tieneVenta', domain: 'Lanzamiento', range: 'VentaRegional', description: 'Ventas regionales del lanzamiento' },
        { name: 'fechaLanzamiento', domain: 'Lanzamiento', range: 'LanzamientoRegional', description: 'Fecha(s) de lanzamiento por region' },
        { name: 'tieneDemo', domain: 'Videojuego', range: 'Lanzamiento', description: 'Version demo gratuita' },
        { name: 'tienePlaytest', domain: 'Videojuego', range: 'Lanzamiento', description: 'Version playtest' }
    ],
    dataProperties: [
        { name: 'nombre', domain: 'owl:Thing', range: 'xsd:string', description: 'Nombre legible de cualquier entidad' },
        { name: 'region', domain: 'owl:Thing', range: 'xsd:string', description: 'Codigo de region (NA, EU, JP, Other)' },
        { name: 'monto', domain: 'VentaRegional', range: 'xsd:decimal', description: 'Valor de ventas en millones de unidades' },
        { name: 'fecha', domain: 'LanzamientoRegional', range: 'xsd:date', description: 'Fecha de lanzamiento en formato ISO' },
        { name: 'precio', domain: 'Lanzamiento', range: 'xsd:decimal', description: 'Precio en USD' },
        { name: 'metacriticScore', domain: 'Lanzamiento', range: 'xsd:integer', description: 'Puntuacion Metacritic (1-100; 0=ausente)' },
        { name: 'resenasPositivas', domain: 'Lanzamiento', range: 'xsd:integer', description: 'Resenas positivas en Steam' },
        { name: 'resenasNegativas', domain: 'Lanzamiento', range: 'xsd:integer', description: 'Resenas negativas en Steam' },
        { name: 'tiempoJuego', domain: 'Lanzamiento', range: 'xsd:integer', description: 'Tiempo promedio jugado en minutos' },
        { name: 'peakCcu', domain: 'Lanzamiento', range: 'xsd:integer', description: 'Maximo de jugadores concurrentes en Steam' }
    ]
};

/* ----------------------------------------------------------
   Consultas SPARQL predefinidas
   ---------------------------------------------------------- */
const QUERIES = [
    {
        id: '01_libre',
        label: 'Libre — Juegos con fechas y ventas por region',
        description: 'Videojuegos con sus fechas de lanzamiento regionales y ventas asociadas.',
        query: `PREFIX ex: <http://example.org/videojuegos#>
SELECT ?nombre ?plataforma ?region ?fecha ?ventas WHERE {
  ?juego a ex:Videojuego ;
         ex:nombre ?nombre .
  ?juego ex:tieneLanzamiento ?lanz .
  ?lanz ex:enPlataforma ?plat .
  ?plat ex:nombre ?plataforma .
  ?lanz ex:fechaLanzamiento ?lr .
  ?lr ex:region ?region ;
      ex:fecha ?fecha .
  OPTIONAL {
    ?lanz ex:tieneVenta ?v .
    ?v ex:monto ?ventas .
  }
}
ORDER BY ?nombre ?region
LIMIT 30`
    },
    {
        id: '02_agregacion',
        label: 'Agregacion (SUM) — Top 10 juegos mas vendidos',
        description: 'Los 10 videojuegos con mayores ventas totales agregadas, con su desarrollador.',
        query: `PREFIX ex: <http://example.org/videojuegos#>
SELECT ?nombre (SUM(?monto) AS ?ventas_totales) ?desarrollador WHERE {
  ?juego a ex:Videojuego ;
         ex:nombre ?nombre ;
         ex:desarrolladoPor ?dev .
  ?dev ex:nombre ?desarrollador .
  ?juego ex:tieneLanzamiento ?lanz .
  ?lanz ex:tieneVenta ?v .
  ?v ex:monto ?monto .
}
GROUP BY ?nombre ?desarrollador
ORDER BY DESC(?ventas_totales)
LIMIT 10`
    },
    {
        id: '03_groupby_having',
        label: 'GROUP BY + HAVING — Estudios multiplataforma',
        description: 'Desarrolladores que han publicado juegos en al menos 2 plataformas distintas.',
        query: `PREFIX ex: <http://example.org/videojuegos#>
SELECT ?desarrollador (COUNT(DISTINCT ?plataforma) AS ?plataformas) WHERE {
  ?dev a ex:Desarrollador ;
       ex:nombre ?desarrollador .
  ?juego ex:desarrolladoPor ?dev ;
         ex:tieneLanzamiento ?lanz .
  ?lanz ex:enPlataforma ?plataforma .
}
GROUP BY ?desarrollador
HAVING (?plataformas >= 2)
ORDER BY DESC(?plataformas)
LIMIT 20`
    },
    {
        id: '04_property_paths',
        label: 'Property Paths — Desarrolladores que se autopublican',
        description: 'Desarrolladores que tambien actuan como editores de sus propios juegos, usando property paths.',
        query: `PREFIX ex: <http://example.org/videojuegos#>
SELECT DISTINCT ?dev ?nombre WHERE {
  ?dev a ex:Desarrollador ; ex:nombre ?nombre .
  ?juego ex:desarrolladoPor ?dev .
  ?juego ex:tieneLanzamiento / ex:publicadoPor / ex:nombre ?nombre .
}
LIMIT 20`
    },
    {
        id: '04b_inferencia',
        label: 'Property Paths con inferencia — Juegos en consolas',
        description: 'Lanzamientos en consolas usando la jerarquia \'Consola ⊑ Plataforma\' con rdfs:subClassOf*.',
        query: `PREFIX ex:  <http://example.org/videojuegos#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?nombreJuego ?tipoPlataforma WHERE {
  ?juego ex:nombre ?nombreJuego ;
         ex:tieneLanzamiento / ex:enPlataforma ?p .
  ?p a ?tipoPlataforma .
  ?tipoPlataforma rdfs:subClassOf* ex:Consola .
}
LIMIT 30`
    },
    {
        id: '05_filter_not_exists',
        label: 'FILTER NOT EXISTS — Juegos sin genero',
        description: 'Videojuegos que no tienen ningun genero asignado en el grafo (comun en fuentes PlayStation y Xbox).',
        query: `PREFIX ex: <http://example.org/videojuegos#>
SELECT ?juego ?nombre WHERE {
  ?juego a ex:Videojuego ;
         ex:nombre ?nombre .
  FILTER NOT EXISTS { ?juego ex:perteneceAGenero ?genero . }
}
LIMIT 20`
    },
    {
        id: '06_insert_delete',
        label: 'INSERT/DELETE — Corregir venta de Wii Sports',
        description: 'Actualiza el monto de venta regional de Wii Sports en Norteamerica (41.49 a 41.50).',
        query: `PREFIX ex: <http://example.org/videojuegos#>
DELETE { ?v ex:monto 41.49 }
INSERT { ?v ex:monto 41.50 }
WHERE {
  ?juego ex:nombre "Wii Sports" .
  ?juego ex:tieneLanzamiento ?lanz .
  ?lanz ex:tieneVenta ?v .
  ?v ex:monto 41.49 .
}`
    },
    {
        id: '07_grafos_nombrados',
        label: 'Grafos nombrados — Editores distintos por plataforma',
        description: 'Compara editores entre Xbox y PlayStation para el mismo juego, usando grafos nombrados.',
        query: `PREFIX ex: <http://example.org/videojuegos#>
SELECT ?nombreJuego ?editorXbox ?editorPlaystation WHERE {
  GRAPH ex:xbox {
    ?juego ex:nombre ?nombreJuego ;
           ex:tieneLanzamiento / ex:publicadoPor ?eXbox .
  }
  GRAPH ex:playstation {
    ?juego ex:tieneLanzamiento / ex:publicadoPor ?ePs .
  }
  ?eXbox ex:nombre ?editorXbox .
  ?ePs ex:nombre ?editorPlaystation .
  FILTER (?editorXbox != ?editorPlaystation)
}
LIMIT 20`
    }
];

/* ----------------------------------------------------------
   Datos de las fuentes
   ---------------------------------------------------------- */
const DATA_SOURCES = [
    {
        name: 'vgsales',
        format: 'CSV',
        records: '16,598',
        contribution: 'Ventas regionales desagregadas (NA, EU, JP, Other)',
        issues: [
            'Year nulo en 1.63% de los registros',
            'Publisher "Unknown" en 1.22% de los registros',
            '5 casos de duplicados Name + Platform'
        ]
    },
    {
        name: 'Steam',
        format: 'CSV',
        records: '94,948',
        contribution: 'Precio, resenas, tiempo de juego, pico de concurrentes, desarrollador',
        issues: [
            'metacritic_score = 0 en 96.2% de los registros (placeholder)',
            'estimated_owners = "0 - 0" en 14.4%',
            '6.8% de registros sin genero ni desarrollador'
        ]
    },
    {
        name: 'Consolas (Xbox, PlayStation, Switch)',
        format: 'JSON',
        records: '2,279 / 1,151 / 1,043',
        contribution: 'Fechas de lanzamiento por 4 regiones, desarrolladores y editores completos',
        issues: [
            'Genero vacio en 64.6% de Xbox y 87.1% de PlayStation',
            'Fechas "Unreleased" o "TBA" en Japon (42-48%)',
            'Publishers de Switch con prefijo regional ("JP: ", "WW: ")'
        ]
    }
];

/* ----------------------------------------------------------
   Descargas
   ---------------------------------------------------------- */
const DOWNLOADS = [
    {
        name: 'ontologia.ttl',
        description: 'Ontologia OWL del grafo de conocimiento (10 clases, 19 propiedades)',
        size: '6 KB',
        local: 'downloads/ontologia.ttl',
        repo: '../ontology/ontologia.ttl'
    },
    {
        name: 'validacion_shacl.ttl',
        description: 'Shapes SHACL con 4 tipos de validacion (obligatoriedad, tipo, rango, cerrada)',
        size: '3.7 KB',
        local: 'downloads/validacion_shacl.ttl',
        repo: '../ontology/validacion_shacl.ttl'
    },
    {
        name: 'datos_integrados.ttl',
        description: 'Grafo RDF completo con 2.4 millones de tripletas (68 MB)',
        size: '68 MB',
        local: null,
        repo: '../output/datos_integrados.ttl'
    },
    {
        name: 'Consultas SPARQL',
        description: '9 consultas predefinidas en archivos .sparql individuales',
        size: null,
        local: null,
        repo: '../queries/'
    },
    {
        name: 'Script de materializacion',
        description: 'materializar.py - Transforma fuentes CSV/JSON a RDF con rdflib',
        size: null,
        local: null,
        repo: '../src/materializar.py'
    }
];
