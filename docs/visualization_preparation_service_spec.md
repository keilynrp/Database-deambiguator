# Visualization Preparation Service - Technical Specification

## Contexto y Motivación

En plataformas analíticas avanzadas como UKIP, los grafos de conocimiento a menudo involucran miles de nodos y millones de aristas. Los navegadores web (utilizando motores JavaScript/WebGL) son excelentes para el renderizado visual, pero sufren cuellos de botella significativos o caídas de cuadros (FPS) cuando intentan calcular _layouts_ topológicos en tiempo real (por ejemplo, algoritmos Force-Directed, Fruchterman-Reingold) o ejecutar algoritmos de detección de comunidades complejos sobre sus hilos de sistema.

Para resolver este desafío, se propone delegar los cálculos matemáticos (distribución en planos, métricas de centralidad, detección de comunidades) a un **Visualization Preparation Service** backend ultrarrápido y asíncrono, escrito en lenguajes de bajo nivel compilados (Rust o C++). Esto libera el hilo principal del navegador (`main thread`) y multiplica el rendimiento computacional hasta por 100x aprovechando el uso de múltiples núcleos, la vectorización SIMD y un manejo estricto de memoria sin Garbage Collection.

## Arquitectura de la Solución

El microservicio se puede implementar aplicando uno de los dos candidatos siguientes:

### Candidato 1: Rust (con `petgraph` y `axum`)

**Recomendado para:** Equipos modernos que demandan alta mantenibilidad, desarrollo ergonómico, e integraciones robustas contra _data races_ utilizando concurrencia garantizada en multinúcleo.

**Stack Tecnológico:**
- **Servidor:** `axum` sobre un runtime `tokio` (para puertos de API HTTP REST) o un RPC bidireccional estándar con `tonic`. 
- **Cálculo Topográfico:** `petgraph` (core graph layer) extendido con `rayon` para concurrencia funcional, y librerías adicionales en diseño de fuerzas (`fdg`).
- **Respuesta:** Envoltorios de JSON binario extremadamente ligeros generados a través de la librería `serde` o buffers puros (FlatBuffers).

**Ejecución:**
1. La API acepta parámetros en bloque de grafos primarios JSON de parte de los integradores frontend.
2. Levanta en memoria el grafo con soporte matricial (`petgraph::Graph`). 
3. Procesa rutas más cortas, layouts en capas e integraciones algorítmicas en concurrencia (procesamiento distribuido en hilos con `rayon`).
4. Retorna eficientemente coordenadas geográficas precomputadas con ejes en `[x,y,z]` listos para graficarse a coste cero de proceso en frontend.  

### Candidato 2: C++ (con `igraph` y `Drogon`/`gRPC`)

**Recomendado para:** Rendimiento matemático absoluto y despliegue avanzado en grafos hipermasivos en donde el ecosistema completo científico ya ha sido construido anteriormente.

**Stack Tecnológico:**
- **Core Server:** `Drogon` (framework C++ web líder en capacidad masiva de I/O) o un entorno simple pero directo gRPC asíncrono.
- **Motor Científico Analítico:** La imbatible biblioteca `igraph` (C core con extensiones de array matricial C++). 
- **Pivote Central:** Uso de algoritmos de agrupamiento de comunidades optimizados por hardware: Louvain, Leiden, y cálculos integrados rápidos originarios de academia con `igraph_layout_fruchterman_reingold(...)`.

**Ejecución:**
1. A nivel de abstracción bajo (punteros en memoria zero-copy) se recibe el `Vector` numérico de nodos. 
2. Las llamadas se ejecutan convirtiendo directamente un array sin copias innecesarias en `igraph_vector_t`.
3. Invocación de rutinas ultra optimizadas en un cálculo matemático monolítico con un acceso contiguo al caché del CPU que aplasta a cualquier abstracción de alto nivel.
4. Exporta las coordenadas en memoria para retorno en un `HttpResponse` comprimido de los índices de la malla calculada.

## Matriz de Decisión / Comparativa

| Criterio Estratégico | C++ / C con `igraph` | Rust con `petgraph` |
|----------------------|----------------------|---------------------|
| **Potencial Funcional Ecosistemas** | **Imbatible.** Implementaciones maduras (20+ años) en Clústeres Reales (comunidades complejas como Leiden). | **Robusto pero nuevo.** Librería potente para cálculos matemáticos tradicionales de gráficos numéricos, pero con menor catálogo para la distribución del layout de layouts especializados. |
| **Rendimiento Puro Límite** | Máxima compresión de CPU de hardware y límites en asignación de RAM por arreglos continuos C. | Extraordinariamente veloz. Posiblemente parejo a C salvo en casos de algoritmos propietarios específicos de iGraph. |
| **Esfuerzo de Ingeniería / Developer Experience (DX)** | Curva pronunciada (requiere `CMake`, control total y riguroso de memoria con RAII, debugging más tardado). | Desarrollo placentero por compilador riguroso (zero _mem leaks/data races_ resueltos preventivamente). |
| **Portabilidad a Compuesto Web (Wasm)** | Transversal a Wasm (EMSCRIPTEN) pero puede escalar la complejidad del binario final. | Herramientas `wasm-pack` nativas con excelente mapeo directo de funciones en un hilo frontal (Threads). |

## Recomendaciones Directas Futuras

Sea quien ganase la balanza para instanciar el Visualization Preparation Service, deberían asumirse invariablemente para UKIP los siguientes patrones adicionales para lograr un estado Enterprise:

1. **Protocolo Websocket & Iteración Incremental (Server-Sent Events)**: Nunca deben esperarse ciclos de un proceso de red enteros bloqueando la respuesta. Devuelve lotes de `Float32Array` y ArrayBuffers minúsculos de las posiciones calculadas (Ej., cada iteración 5 de fuerza de los nodos). Esto hará un pre-rendering con _Efecto Wow_ donde el grafo estalla en vivo para los usuarios mientras se desenreda visualmente.
2. **Exclusión Expresa del DOM en UI**: Jamás pintar esto con SVG y React Components estándar. Exigir de lado web el uso imperioso de APIs renderizadoras a GPU WebGL de manera exclusiva (Deck.gl / Sigma.js / vis.gl).
