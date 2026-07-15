#!/usr/bin/env python3
"""
Servidor local para probar la web del grafo de conocimiento.
Ejecuta: python server.py
Abre:    http://localhost:8000

Esto es necesario porque los navegadores bloquean fetch() y
carga dinamica de modulos al abrir archivos directamente (file://).
"""

import http.server
import os
import socketserver
import sys

PORT = 8000

os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.ttl': 'text/turtle',
    '.sparql': 'text/plain',
    '.json': 'application/json',
    '.js': 'application/javascript',
})

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor iniciado en http://localhost:{PORT}")
    print(f"Presiona Ctrl+C para detener.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        sys.exit(0)
