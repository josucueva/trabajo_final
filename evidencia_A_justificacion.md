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
