# Puntos de comparación para la charla

Todo esto sale de construir y correr el mismo sistema en los tres frameworks.

## El experimento controlado

Mismo problema (resumir ResNet), mismo stack (fastembed + ChromaDB + `gpt-4o-mini`),
mismo PDF. Lo único que cambia es el framework.

> Como el modelo y el RAG son idénticos, **los tres resumen igual de bien**. El framework
> no mejora la salida; cambia **cómo la construyes y la controlas**.

## Los frameworks de un vistazo

| | Enfoque | Fuerte en | Cuesta |
|---|---|---|---|
| **smolagents** | Agente ligero con herramientas; el agente decide cuándo usarlas. | Prototipar rápido, poco código. | No trae validación ni reintentos: los pones tú. |
| **LangGraph** | Flujo como grafo de estados explícito, con ciclos. | Control del flujo, reintento como ciclo natural, estado. | Más ceremonia para lo simple. |
| **Pydantic AI** | Salidas tipadas con validadores y reintentos declarativos. | Validación y reintentos "de fábrica". | (lo detalla José) |
| **Sin framework** | Todo a mano. | Cero dependencias, control total. | Tú escribes y mantienes todo. |

## La parte 2 es donde se nota la diferencia

Agregar *validar que el resumen cite secciones reales + reintentar* se resuelve distinto:

- **baseline:** un `for` a mano.
- **smolagents:** un bucle nuestro alrededor de `agent.run()`.
- **LangGraph:** un ciclo en el grafo (nodo `validar` + arista condicional).
- **Pydantic AI:** validadores + reintento del framework.

## El dato honesto: líneas de código (parte 2, con docstrings)

| baseline | smolagents | LangGraph |
|---|---|---|
| 55 | 79 | 79 |

Para un caso simple, **el framework cuesta líneas, no las ahorra** (hacerlo a mano son 55).
El retorno aparece cuando el flujo crece: más ramas, estado, herramientas, reintentos en
varios puntos. (smolagents suma líneas porque hay que normalizar su salida, que no es
estructurada por defecto.)

## Cómo elegir

- **smolagents** → prototipos y agentes con herramientas, con mínimo código.
- **LangGraph** → flujos con estado, ciclos y ramas; control explícito.
- **Pydantic AI** → cuando la salida validada y los reintentos son el centro.
- **Sin framework** → casos triviales; no escala.

Regla práctica: **la complejidad del flujo manda**. Simple → poco framework; con
decisiones, ciclos y estado → el framework se paga solo.

## Detalles que vivimos construyendo

- El RAG es idéntico en los tres; el diferenciador es la orquestación.
- `gpt-4o-mini` es muy obediente: para ver un reintento tuvimos que subir el umbral de
  secciones. Validar + reintentar es barato y cubre justo cuando el modelo falla.
- smolagents entrega la salida como dict ya parseado (no JSON) y reintenta ante errores
  de API con *backoff* largo (~11 min): dos cosas a cuidar en una demo en vivo.
