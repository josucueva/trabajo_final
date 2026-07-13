```
Proyecto final- Representación del Conocimiento
```
El objetivo del proyecto es crear un grafo de conocimiento a partir de al menos tres fuentes de datos
estructuradas. Este trabajo será evaluado de acuerdo con los siguientes criterios:

- 25%: propuesta de datos
- 65%: solución técnica
- 10 %: presentación

El proyecto podrá ser realizado en grupos de hasta dos personas. Las evidencias que respalden el
desarrollo del proyecto serán sustentadas del lunes 14 al jueves 17 de julio (previo sorteo)

**Descripción:**

El proyecto requiere trabajar con al menos tres fuentes de datos independientes en diferentes
formatos, como CSV y JSON. En primer lugar, se deberá desarrollar una ontología que modele los
datos a integrar en el grafo de conocimiento. Luego, se llevará a cabo un proceso de transformación
de las fuentes estructuradas a un formato de tripletas (materialización), utilizando el vocabulario
definido en la ontología. Los datos transformados deberán ser validados antes de ser cargados en
el grafo.

Una vez completado el proceso de transformación, se cargarán tanto el esquema del grafo como los
datos convertidos en una base de tripletas. Posteriormente, se ejecutarán consultas en SPARQL para
extraer información específica de las fuentes de datos.

- Siéntase libre de utilizar cualquier método disponible para llevar a cabo las tareas solicitadas.
- Diseñe primero todas las consultas que deberá responder el grafo de conocimiento antes de iniciar
el proceso de integración.

**Restricciones** :

- Las fuentes de datos utilizadas deberán contener al menos cinco atributos o campos.
- No se permite el uso de fuentes de datos similares a las usadas durante las prácticas del curso.
- Las fuentes de datos deben incluir valores faltantes o erróneos que requieran una validación
posterior.
- El proceso de validación de los datos transformados debe incluir al menos cuatro tipos diferentes
de validaciones (por ejemplo: obligatoriedad de una propiedad, un literal de un tipo específico, un
valor dentro de ciertos rangos, o una entidad que posea solo propiedades definidas).
- Si es necesario, puede alterar manualmente el archivo con las fuentes integradas en formato RDF
para probar la validación.
- Antes de poblar el grafo con los datos integrados puede corregir manualmente los errores
detectados durante la validación.


- El grafo de conocimiento debe responder al menos seis consultas diferentes en SPARQL, basadas
en datos presentes en las tres fuentes integradas. Las consultas deberán tener algún proceso de
inferencia:
- Una consulta de formato LIBRE.
- Una consulta que utilice una función de agregación, como SUM, COUNT, AVG, MIN, o MAX.
- Una consulta que incluya GROUP BY y HAVING.
- Una consulta que utilice PROPERTY PATHS.
- Una consulta que use MINUS o FILTER NOT EXISTS.
- Una consulta que emplee INSERT, DELETE, o UPDATE.
- Opcional: una consulta que involucre grafos nombrados.

**Evidencias:**

Registre en la plataforma virtual lo siguiente:

A. Un reporte donde indique la justificación para integrar las fuentes seleccionadas en un grafo de
conocimiento

B. Todos los scripts, código o algoritmos necesarios que permitan replicar toda la ejecución de esta
práctica.

C. El archivo en formato Turtle que representa la fuente de datos transformada

D. El código SPARQL de las consultas solicitadas


