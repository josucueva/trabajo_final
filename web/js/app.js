/* ============================================================
   app.js — Router y renderizado de paginas
   ============================================================ */

(function () {
    'use strict';

    const $content = document.getElementById('page-content');

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function getRoute() {
        const hash = location.hash || '#home';
        return hash.slice(1) || 'home';
    }

    /* ---- Inicio ---- */
    function renderHome() {
        const html = `<div class="page" id="page-home">
            <div class="page-header">
                <h1>Grafo de conocimiento sobre videojuegos</h1>
                <p>Integracion de tres fuentes de datos independientes en un grafo RDF para consultas SPARQL con inferencia ontologica.</p>
            </div>
            <div class="stats-row">
                <div class="stat-card"><div class="stat-number">${STATS.games}</div><div class="stat-label">Videojuegos</div></div>
                <div class="stat-card"><div class="stat-number">${STATS.triples}</div><div class="stat-label">Tripletas RDF</div></div>
                <div class="stat-card"><div class="stat-number">${STATS.entities}</div><div class="stat-label">Entidades totales</div></div>
                <div class="stat-card"><div class="stat-number">${STATS.classes}</div><div class="stat-label">Clases OWL</div></div>
                <div class="stat-card"><div class="stat-number">${STATS.properties}</div><div class="stat-label">Propiedades</div></div>
                <div class="stat-card"><div class="stat-number">${STATS.sources}</div><div class="stat-label">Fuentes integradas</div></div>
            </div>
            <div class="card">
                <h2>Que es este grafo?</h2>
                <p>Este grafo de conocimiento integra datos de <strong>ventas globales de videojuegos</strong> (vgsales), <strong>metadatos de Steam</strong> (precio, resenas, tiempo de juego, desarrolladores) y <strong>fechas de lanzamiento regionales</strong> de consolas (Xbox, PlayStation, Switch).</p>
                <p>El modelo ontologico distingue entre la obra intelectual (<em>Videojuego</em>) y sus ediciones concretas en cada plataforma (<em>Lanzamiento</em>).</p>
            </div>
        </div>`;
        $content.innerHTML = html;
    }

    /* ---- Ontologia ---- */
    function renderOntologia() {
        let treeHtml = '';
        const rootClasses = ONTOLOGY.classes.filter(function(c) { return !c.superClass; });
        const subClasses = ONTOLOGY.classes.filter(function(c) { return c.superClass; });

        rootClasses.forEach(function(cls) {
            treeHtml += '<li><span class="class-node">' + cls.name + '</span> <span class="text-muted">' + cls.description + '</span>';
            var hijos = subClasses.filter(function(s) { return s.superClass === cls.name; });
            if (hijos.length) {
                treeHtml += '<ul class="children">';
                hijos.forEach(function(h) {
                    treeHtml += '<li><span class="class-node">' + h.name + '</span> <span class="tag tag-subclass">subClassOf</span> <span class="text-muted">' + h.description + '</span></li>';
                });
                treeHtml += '</ul>';
            }
            treeHtml += '</li>';
        });

        var objPropsHtml = '';
        ONTOLOGY.objectProperties.forEach(function(p) {
            objPropsHtml += '<div class="prop-card"><h4>:' + p.name + '</h4>';
            objPropsHtml += '<div class="prop-meta">' + p.domain + ' &rarr; ' + p.range + '</div>';
            objPropsHtml += '<div class="prop-desc">' + p.description + '</div></div>';
        });

        var dataPropsHtml = '';
        ONTOLOGY.dataProperties.forEach(function(p) {
            dataPropsHtml += '<div class="prop-card"><h4>:' + p.name + '</h4>';
            dataPropsHtml += '<div class="prop-meta">' + p.domain + ' &rarr; ' + p.range + '</div>';
            dataPropsHtml += '<div class="prop-desc">' + p.description + '</div></div>';
        });

        $content.innerHTML = '<div class="page" id="page-ontologia">' +
            '<div class="page-header"><h1>Ontologia</h1><p>Modelo OWL que define las clases, propiedades y relaciones del dominio de videojuegos.</p></div>' +
            '<div class="card"><h2>Jerarquia de clases</h2><ul class="onto-tree">' + treeHtml + '</ul></div>' +
            '<div class="card"><h2>Propiedades de objeto</h2><div class="prop-grid">' + objPropsHtml + '</div></div>' +
            '<div class="card"><h2>Propiedades de dato</h2><div class="prop-grid">' + dataPropsHtml + '</div></div>' +
            '<div class="card"><h2>Namespace</h2><p>Todas las entidades usan el prefijo <code>http://example.org/videojuegos#</code>.</p>' +
            '<div class="query-editor">PREFIX ex: &lt;http://example.org/videojuegos#&gt;</div></div></div>';
    }

    /* ---- Consultas SPARQL ---- */
    function renderQueries() {
        var selectOpts = '';
        QUERIES.forEach(function(q, i) {
            selectOpts += '<option value="' + i + '">' + q.label + '</option>';
        });

        $content.innerHTML = '<div class="page" id="page-queries">' +
            '<div class="page-header"><h1>Consultas SPARQL</h1><p>Consultas predefinidas de referencia. Para ejecutarlas necesitas una instancia de GraphDB con el grafo cargado.</p></div>' +
            '<div class="card">' +
            '<div class="endpoint-config"><label for="endpoint-url">Endpoint SPARQL (opcional):</label><input type="url" id="endpoint-url" value="" placeholder="http://localhost:7200/repositories/videojuegos"></div>' +
            '<div class="query-controls"><select id="query-select">' + selectOpts + '</select><button id="query-run">Ejecutar consulta</button></div>' +
            '<div class="query-editor" id="query-display"></div>' +
            '<div class="query-status" id="query-status"></div>' +
            '<div id="query-results"></div>' +
            '<div class="card" style="margin-top:16px"><p style="font-size:0.85rem;color:var(--color-muted)"><strong>Nota:</strong> La ejecucion de consultas requiere una instancia de GraphDB corriendo localmente o en un servidor accesible. Sin endpoint, esta seccion funciona como referencia de las consultas SPARQL utilizadas en el proyecto.</p></div></div></div>';

        var $select = document.getElementById('query-select');
        var $display = document.getElementById('query-display');
        var $run = document.getElementById('query-run');
        var $status = document.getElementById('query-status');
        var $results = document.getElementById('query-results');
        var $endpoint = document.getElementById('endpoint-url');

        function showQuery() {
            var idx = parseInt($select.value);
            var q = QUERIES[idx];
            $display.textContent = q.query;
            $status.className = 'query-status';
            $status.style.display = 'none';
            $results.innerHTML = '';
        }

        $select.addEventListener('change', showQuery);

        $run.addEventListener('click', async function() {
            var idx = parseInt($select.value);
            var q = QUERIES[idx];
            var endpoint = $endpoint.value.trim();
            if (!endpoint) {
                $status.className = 'query-status info';
                $status.style.display = 'block';
                $status.textContent = 'Para ejecutar consultas, ingresa la URL de un endpoint SPARQL (ej. http://localhost:7200/repositories/videojuegos). Sin endpoint, puedes ver las consultas como referencia.';
                return;
            }
            $run.disabled = true;
            $run.textContent = 'Ejecutando...';
            $status.className = 'query-status loading';
            $status.style.display = 'block';
            $status.textContent = 'Ejecutando consulta...';
            $results.innerHTML = '';
            var tipo = SPARQL.tipoConsulta(q.query);
            try {
                if (tipo === 'READ') {
                    var res = await SPARQL.querySelect(endpoint, q.query);
                    if (res.success) {
                        var parsed = SPARQL.resultadosToRows(res.data);
                        var columns = parsed.columns;
                        var rows = parsed.rows;
                        $status.className = 'query-status success';
                        $status.style.display = 'block';
                        $status.textContent = 'Consulta exitosa. ' + rows.length + ' resultados.';
                        if (rows.length === 0) {
                            $results.innerHTML = '<p class="text-muted">La consulta no devolvio resultados.</p>';
                        } else {
                            var tableHtml = '<div class="results-wrapper"><table><thead><tr>';
                            columns.forEach(function(c) { tableHtml += '<th>' + escapeHtml(c) + '</th>'; });
                            tableHtml += '</tr></thead><tbody>';
                            rows.forEach(function(row) {
                                tableHtml += '<tr>';
                                columns.forEach(function(c) { tableHtml += '<td>' + escapeHtml(row[c] || '') + '</td>'; });
                                tableHtml += '</tr>';
                            });
                            tableHtml += '</tbody></table></div>';
                            tableHtml += '<div class="results-info">' + rows.length + ' fila(s) en ' + columns.length + ' columna(s)</div>';
                            $results.innerHTML = tableHtml;
                        }
                    } else {
                        $status.className = 'query-status error';
                        $status.style.display = 'block';
                        $status.textContent = res.error;
                    }
                } else if (tipo === 'WRITE') {
                    var res2 = await SPARQL.queryUpdate(endpoint, q.query);
                    if (res2.success) {
                        $status.className = 'query-status success';
                        $status.style.display = 'block';
                        $status.textContent = 'Actualizacion ejecutada correctamente.';
                    } else {
                        $status.className = 'query-status error';
                        $status.style.display = 'block';
                        $status.textContent = res2.error;
                    }
                } else {
                    $status.className = 'query-status error';
                    $status.style.display = 'block';
                    $status.textContent = 'Error: Tipo de consulta no reconocido. Usa SELECT o INSERT/DELETE.';
                }
            } catch (err) {
                $status.className = 'query-status error';
                $status.style.display = 'block';
                $status.textContent = 'Error inesperado: ' + err.message;
            }
            $run.disabled = false;
            $run.textContent = 'Ejecutar consulta';
        });
        showQuery();
    }

    /* ---- Busqueda ---- */
    function renderBuscar() {
        var params = new URLSearchParams(location.hash.split('?')[1] || '');
        var query = (params.get('q') || '').trim();
        $content.innerHTML = '<div class="page" id="page-buscar">' +
            '<div class="page-header"><h1>Buscar videojuegos</h1>' +
            '<p>Resultados para: <strong>' + escapeHtml(query || '(sin consulta)') + '</strong></p></div>' +
            '<div id="search-results"></div></div>';
        if (!query) return;
        ejecutarBusqueda(query);
    }

    var searchIndex = null;
    var searchIndexPromise = null;

    async function cargarIndice() {
        if (searchIndex) return searchIndex;
        if (searchIndexPromise) return searchIndexPromise;

        // Si ya se cargo mediante un tag <script> externo
        if (window.SEARCH_INDEX) {
            searchIndex = window.SEARCH_INDEX;
            return searchIndex;
        }

        // Carga dinamica: crea un <script> para search-index.js
        // Esto funciona con file:// y HTTP (GitHub Pages)
        searchIndexPromise = new Promise(function(resolve, reject) {
            var script = document.createElement('script');
            script.src = CONFIG.searchIndexUrl.replace('.json', '.js');
            script.onload = function() {
                if (window.SEARCH_INDEX) {
                    searchIndex = window.SEARCH_INDEX;
                    resolve(searchIndex);
                } else {
                    searchIndexPromise = null;
                    reject(new Error('El indice no se definio correctamente.'));
                }
            };
            script.onerror = function() {
                // Fallback: intentar fetch del JSON (solo funciona con HTTP)
                fetch(CONFIG.searchIndexUrl)
                    .then(function(r) {
                        if (!r.ok) throw new Error('Error HTTP ' + r.status);
                        return r.json();
                    })
                    .then(function(data) {
                        searchIndex = data;
                        resolve(data);
                    })
                    .catch(function() {
                        searchIndexPromise = null;
                        reject(new Error(
                            'No se pudo cargar el indice de busqueda. ' +
                            'Para desarrollo local, ejecuta: python -m http.server 8000 en la carpeta web'
                        ));
                    });
            };
            document.head.appendChild(script);
        });
        return searchIndexPromise;
    }

    function buscarEnIndice(query, indice) {
        var q = query.toLowerCase();
        var resultados = [];
        for (var i = 0; i < indice.length; i++) {
            var entry = indice[i];
            if (entry[0].toLowerCase().indexOf(q) !== -1) {
                resultados.push(entry);
                if (resultados.length >= 30) break;
            }
        }
        return resultados;
    }

    async function ejecutarBusqueda(query) {
        var $results = document.getElementById('search-results');
        if (!$results) return;
        $results.innerHTML = '<div class="query-status loading" style="display:block">Cargando indice de busqueda...</div>';
        try {
            var indice = await cargarIndice();
            $results.innerHTML = '<div class="query-status loading" style="display:block">Buscando...</div>';
            await new Promise(function(r) { setTimeout(r, 50); });
            var resultados = buscarEnIndice(query, indice);
            if (resultados.length === 0) {
                $results.innerHTML = '<div class="no-results"><p>No se encontraron videojuegos que coincidan con <strong>' + escapeHtml(query) + '</strong>.</p></div>';
                return;
            }
            var cardsHtml = '<p class="search-query-info">' + resultados.length + ' resultado(s) para <strong>' + escapeHtml(query) + '</strong>.</p>';
            for (var i = 0; i < resultados.length; i++) {
                var entry = resultados[i];
                var nombre = entry[0];
                var plataformas = entry[1];
                var generos = entry[2];
                var desarrolladores = entry[3];
                cardsHtml += '<div class="search-result-card">';
                cardsHtml += '<h3>' + escapeHtml(nombre) + '</h3>';
                cardsHtml += '<div class="result-meta">';
                if (plataformas.length) {
                    cardsHtml += '<span><span class="label">Plataformas:</span> ' + escapeHtml(plataformas.join(', ')) + '</span>';
                }
                if (desarrolladores.length) {
                    cardsHtml += '<span><span class="label">Desarrollador:</span> ' + escapeHtml(desarrolladores.join(', ')) + '</span>';
                }
                cardsHtml += '</div>';
                cardsHtml += '<div class="result-meta">';
                if (generos.length) {
                    cardsHtml += '<span><span class="label">Generos:</span> ' + escapeHtml(generos.join(', ')) + '</span>';
                }
                cardsHtml += '</div>';
                cardsHtml += '</div>';
            }
            $results.innerHTML = cardsHtml;
        } catch (err) {
            $results.innerHTML = '<div class="query-status error" style="display:block">Error: ' + escapeHtml(err.message) + '</div>';
        }
    }

    /* ---- Datos ---- */
    function renderDatos() {
        var sourcesHtml = '';
        DATA_SOURCES.forEach(function(src) {
            var issuesHtml = '';
            src.issues.forEach(function(iss) { issuesHtml += '<li>' + iss + '</li>'; });
            sourcesHtml += '<div class="source-card"><h3>' + src.name + '</h3>';
            sourcesHtml += '<div class="source-format">' + src.format + ' &mdash; ' + src.records + ' registros</div>';
            sourcesHtml += '<p><strong>Aporte:</strong> ' + src.contribution + '</p>';
            sourcesHtml += '<p><strong>Problemas de calidad:</strong></p><ul>' + issuesHtml + '</ul></div>';
        });
        $content.innerHTML = '<div class="page" id="page-datos">' +
            '<div class="page-header"><h1>Fuentes de datos</h1><p>Tres fuentes independientes en formatos CSV y JSON, integradas mediante matching por nombre normalizado.</p></div>' +
            sourcesHtml +
            '<div class="card"><h2>Proceso de integracion</h2>' +
            '<p>Las fuentes se integraron mediante <strong>entity linking</strong> basado en el nombre del juego, normalizado (lowercase, sin puntuacion, sin simbolos de marca, sin apostrofes unicode).</p>' +
            '<p>La ontologia distingue entre <em>Videojuego</em> (obra) y <em>Lanzamiento</em> (edicion en una plataforma).</p>' +
            '<p class="mb-md"><strong>Validacion SHACL</strong> con 4 tipos de restricciones:</p>' +
            '<ul><li>Obligatoriedad: todo Videojuego debe tener al menos un genero</li>' +
            '<li>Tipo de literal: VentaRegional.monto debe ser xsd:decimal</li>' +
            '<li>Rango: metacriticScore entre 1 y 100</li>' +
            '<li>Shape cerrada: VentaRegional solo puede tener region y monto</li></ul></div></div>';
    }

    /* ---- Descargas ---- */
    function renderDescargas() {
        var itemsHtml = '';
        DOWNLOADS.forEach(function(d) {
            var sizeHtml = d.size ? '<span class="file-size">' + d.size + '</span>' : '';
            var url = d.local || d.repo;
            var label = d.local ? 'Descargar' : 'Ver en repositorio';
            itemsHtml += '<li><div class="file-info"><div class="file-name">' + d.name + '</div><div class="file-desc">' + d.description + '</div></div>' + sizeHtml + '<a href="' + url + '" class="btn-download" target="_blank" rel="noopener">' + label + '</a></li>';
        });
        $content.innerHTML = '<div class="page" id="page-descargas">' +
            '<div class="page-header"><h1>Descargas</h1><p>Archivos del proyecto disponibles para descarga directa o consulta en el repositorio.</p></div>' +
            '<div class="card"><ul class="download-list">' + itemsHtml + '</ul></div></div>';
    }

    /* ---- Acerca ---- */
    function renderAcerca() {
        $content.innerHTML = '<div class="page" id="page-acerca">' +
            '<div class="page-header"><h1>Acerca del proyecto</h1><p>Proyecto final de Representacion del Conocimiento.</p></div>' +
            '<div class="card"><h2>Descripcion</h2>' +
            '<p>Grafo de conocimiento que integra datos de videojuegos provenientes de tres fuentes independientes: ventas globales (vgsales), metadatos de Steam y fechas de lanzamiento de consolas (Xbox, PlayStation, Switch).</p>' +
            '<p>El modelo ontologico en OWL permite consultas con inferencia sobre la jerarquia de clases y property paths.</p></div>' +
            '<div class="card"><h2>Tecnologias</h2>' +
            '<ul><li><strong>Python</strong> + rdflib para la materializacion RDF</li>' +
            '<li><strong>GraphDB</strong> para almacenamiento, inferencia y consultas</li>' +
            '<li><strong>SHACL</strong> para validacion de datos</li>' +
            '<li><strong>Ontotext Refine</strong> para limpieza y transformacion</li></ul></div></div>';
    }

    /* ---- Router ---- */
    var routes = {
        home: renderHome,
        ontologia: renderOntologia,
        queries: renderQueries,
        buscar: renderBuscar,
        datos: renderDatos,
        descargas: renderDescargas,
        acerca: renderAcerca
    };

    function router() {
        var route = getRoute().split('?')[0];
        var render = routes[route] || routes.home;
        render();
        document.querySelectorAll('[data-nav]').forEach(function(el) {
            var href = el.getAttribute('href');
            if (href === '#' + route) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
    }

    /* ---- Inicializacion ---- */
    window.addEventListener('hashchange', router);
    window.addEventListener('DOMContentLoaded', function() {
        router();
        var toggle = document.querySelector('.nav-toggle');
        var nav = document.querySelector('.main-nav');
        if (toggle && nav) {
            toggle.addEventListener('click', function() { nav.classList.toggle('open'); });
            nav.querySelectorAll('a').forEach(function(a) {
                a.addEventListener('click', function() { nav.classList.remove('open'); });
            });
        }
        var searchForm = document.getElementById('search-form');
        var searchInput = document.getElementById('search-input');
        if (searchForm && searchInput) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                var q = searchInput.value.trim();
                if (q) {
                    location.hash = '#buscar?q=' + encodeURIComponent(q);
                }
            });
        }
    });
})();
