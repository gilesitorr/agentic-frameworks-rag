# Puntos de comparación para la charla

Material de apoyo para presentar (secciones *Comparación de Frameworks* y *Conclusiones*).
Todo lo que está aquí sale de **construir y correr el mismo sistema** en los tres frameworks;
no es teoría de folleto.

---

## 0. El experimento controlado

Resolvimos **el mismo problema** (RAG que resume el paper de ResNet) con el **mismo stack**
(fastembed + ChromaDB + `gpt-4o-mini`), el **mismo PDF** y el **mismo criterio de validación**.
Lo único que cambia entre implementaciones es **el framework**.

> **Consecuencia importante para la charla:** como el modelo y el RAG son idénticos, la
> **calidad de los resúmenes es prácticamente la misma** en los tres. El framework **no
> mejora la salida**; cambia **cómo la construyes, la controlas y la mantienes**. La
> comparación es sobre *experiencia de desarrollo y control del flujo*, no sobre "cuál resume mejor".

---

## 1. ¿Qué aporta un framework? (lo que enseña el baseline)

El `baseline/` resuelve todo **sin framework**. Sirve para ver qué asume un framework por ti:

- El **ciclo de orquestación** (recuperar → generar → validar → reintentar).
- El **manejo del estado** entre pasos.
- El **parseo y la validación** de la salida del modelo.
- El **bucle de reintentos** con feedback.
- (Con herramientas) el ciclo **razonar ↔ llamar herramienta ↔ continuar**.

Sin framework todo esto lo escribes y lo mantienes tú. Un framework te da **abstracciones**
para una o varias de estas piezas.

---

## 2. Ficha por framework

### smolagents (Hugging Face)
- **Enfoque:** agente **ligero**. Tú defines herramientas con `@tool` y el agente decide
  cuándo usarlas; el ciclo razonar↔herramienta viene incluido. Su sello distintivo es el
  `CodeAgent` (el agente **escribe código Python** para orquestar las herramientas); nosotros
  usamos `ToolCallingAgent` (llamadas a herramienta en JSON) por simplicidad y comparabilidad.
- **Fortalezas:** mínimo *boilerplate*, se prototipa rapidísimo, muy poca ceremonia. Ideal
  para "dale herramientas a un modelo y deja que resuelva".
- **Limitaciones:** te da el ciclo de herramientas, **pero no** validación estructural ni
  reintentos declarativos → eso lo orquestas tú (en la parte 2 el reintento fue **un bucle
  nuestro** alrededor de `agent.run()`). Menos control explícito del flujo.
- **Detalle real que encontramos:** devuelve la salida ya **parseada como objeto de Python**
  (dict), no como texto JSON; hay que validarla como dict.

### LangGraph (LangChain)
- **Enfoque:** modelas el flujo como un **grafo de estados explícito** — nodos (funciones) +
  aristas, con **estado tipado compartido** y **ciclos** vía aristas condicionales.
- **Fortalezas:** **control total y explícito** del flujo. Los reintentos y ramificaciones son
  **ciclos naturales** en el grafo (nuestro `generar → validar → (reintentar | fin)`). Fácil de
  razonar sobre el flujo, inspeccionar el estado y crecer (más nodos, condiciones,
  *human-in-the-loop*, *checkpoints*).
- **Limitaciones:** más ceremonia para casos simples (defines estado, nodos y aristas aunque el
  flujo sea lineal); curva de aprendizaje mayor. Para "recupera y resume" es más verboso que
  smolagents.

### Pydantic AI (contexto — lo presenta José)
- **Enfoque:** agente centrado en **salidas tipadas y validadas** con Pydantic, con
  **validadores de salida** y **reintentos declarativos** (`ModelRetry`) integrados.
- **Fortalezas:** justo el requisito de la parte 2 (validación estructural + reintento)
  prácticamente **"de fábrica"**; salidas con tipos garantizados; muy pythónico.

---

## 3. La parte 2 como lente de comparación

El agregar *validación + reintentos* es donde los frameworks se diferencian de verdad:

| Implementación | ¿Cómo maneja el reintento? |
|---|---|
| **baseline** | Un `for` a mano: generar → validar → repetir con feedback. |
| **smolagents** | Igual, **un bucle nuestro** sobre `agent.run()`. El framework aporta el ciclo de herramientas, no la validación. |
| **LangGraph** | Un **ciclo explícito en el grafo**: nodo `validar` + arista condicional que regresa a `generar`. |
| **Pydantic AI** | **Validadores declarativos** + reintento del propio framework. |

**Confirmado en vivo:** subiendo el umbral de secciones, el intento 1 falla
(*"cita 8, se requieren 10"*) y el intento 2 lo corrige con el feedback. El mecanismo funciona.

---

## 4. Dato duro: tamaño del código

Tamaño de archivo (incluye comentarios y docstrings didácticos; son una referencia, no un *benchmark*):

| | Parte 1 (básica) | Parte 2 (validación + reintentos) |
|---|---|---|
| **baseline** | — | **76** |
| **smolagents** | **51** | **97** |
| **LangGraph** | **67** | **106** |

> **El punto más honesto de la charla:** en la parte 2, **hacerlo a mano (76) es más corto que
> con framework** (97 y 106). Para un caso simple, el framework **cuesta** líneas, no las ahorra.
> El retorno **no** está en el ejemplo de juguete: aparece cuando el flujo crece (más ramas,
> estado, herramientas, *human-in-the-loop*, observabilidad, reintentos en varios puntos).

---

## 5. Criterios para elegir (conclusiones)

- **smolagents** → prototipos rápidos y agentes con herramientas donde el **agente decide** el
  flujo y quieres **mínimo código**. Menos indicado cuando necesitas control fino del flujo o
  garantías fuertes sobre la salida.
- **LangGraph** → flujos con **estado, ciclos y ramas**, control **explícito**, observabilidad y
  producción con lógica elaborada (*human-in-the-loop*, *checkpoints*). *Overkill* para algo
  lineal y simple.
- **Pydantic AI** → cuando la **salida tipada/validada** y los **reintentos** son el centro y
  quieres resolverlos con mínimo esfuerzo.
- **Sin framework** → casos tan simples que el framework es puro *overhead*… pero no escala.

Regla práctica: **la complejidad del flujo** manda. Flujo simple → poco framework.
Flujo con decisiones, ciclos y estado → el framework se paga solo.

---

## 6. Observaciones honestas (vividas al construir)

1. El **RAG es idéntico y "aburrido"** en los tres; el diferenciador es la **orquestación**.
2. La **calidad del resumen es igual** entre frameworks (mismo modelo + mismo RAG).
3. Para un caso simple, el framework puede costar **más** líneas que hacerlo a mano.
4. smolagents entrega la salida como **dict ya parseado** (no JSON): detalle de integración.
5. `gpt-4o-mini` resultó **muy obediente**: la validación casi nunca falló sola; tuvimos que
   **forzar el umbral** para ver el reintento. Lección: validar + reintentar es **barato** y te
   cubre justo cuando el modelo sí se equivoca.
6. smolagents **reintenta ante errores de API** con *backoff* largo (~11 min): hay que
   configurarlo para una demo en vivo.

---

## 7. Posibles preguntas del público (para el Q&A)

- *"¿Cuál es el mejor?"* → Ninguno; depende de la **complejidad del flujo** y de qué quieras que
  el framework resuelva por ti (herramientas, estado, validación, reintentos).
- *"¿No es lo mismo con un `for` y requests?"* → Para esto, casi; mira el baseline. La diferencia
  se nota cuando el flujo crece.
- *"¿El framework mejora la respuesta del modelo?"* → No. Mejora cómo **orquestas y controlas**,
  no la calidad de la generación.
- *"¿Puedo cambiar de modelo/proveedor?"* → Sí en los tres; aquí todo usa OpenAI por
  estandarización, pero son agnósticos al proveedor.
