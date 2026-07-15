/* ============================================================
   sparql.js — Cliente SPARQL para GraphDB
   ============================================================ */

const SPARQL = (() => {

    /**
     * Ejecuta una consulta SPARQL SELECT contra GraphDB.
     * Retorna un objeto { success, data, error }.
     */
    async function querySelect(endpoint, sparqlQuery) {
        const url = endpoint + '?query=' + encodeURIComponent(sparqlQuery);
        const result = { success: false, data: null, error: null };

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/sparql-results+json',
                },
            });

            if (!response.ok) {
                const text = await response.text();
                result.error = `Error ${response.status}: ${text.slice(0, 300)}`;
                return result;
            }

            const json = await response.json();
            result.success = true;
            result.data = json;
        } catch (err) {
            result.error = 'Error de conexion: ' + err.message;
        }

        return result;
    }

    /**
     * Ejecuta una consulta SPARQL UPDATE (INSERT/DELETE).
     */
    async function queryUpdate(endpoint, sparqlUpdate) {
        const result = { success: false, error: null };

        try {
            const response = await fetch(endpoint + '/statements', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/sparql-update',
                },
                body: sparqlUpdate,
            });

            if (!response.ok) {
                const text = await response.text();
                result.error = `Error ${response.status}: ${text.slice(0, 300)}`;
                return result;
            }

            result.success = true;
        } catch (err) {
            result.error = 'Error de conexion: ' + err.message;
        }

        return result;
    }

    /**
     * Convierte resultados SPARQL JSON a un array de filas planas.
     */
    function resultadosToRows(sparqlJson) {
        if (!sparqlJson || !sparqlJson.results || !sparqlJson.results.bindings) {
            return { columns: [], rows: [] };
        }

        const vars = sparqlJson.head.vars;
        const bindings = sparqlJson.results.bindings;

        const rows = bindings.map(b => {
            const row = {};
            vars.forEach(v => {
                const val = b[v];
                row[v] = val ? val.value : '';
            });
            return row;
        });

        return { columns: vars, rows };
    }

    /**
     * Determina si una consulta es SELECT o UPDATE.
     */
    function tipoConsulta(query) {
        const q = query.trim().toUpperCase();
        if (q.startsWith('SELECT') || q.startsWith('ASK') || q.startsWith('CONSTRUCT') || q.startsWith('DESCRIBE')) {
            return 'READ';
        }
        if (q.startsWith('INSERT') || q.startsWith('DELETE') || q.startsWith('CLEAR') || q.startsWith('DROP') || q.startsWith('LOAD')) {
            return 'WRITE';
        }
        return 'UNKNOWN';
    }

    return {
        querySelect,
        queryUpdate,
        resultadosToRows,
        tipoConsulta,
    };
})();
