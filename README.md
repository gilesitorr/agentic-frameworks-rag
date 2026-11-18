# Agentic AI en la práctica — RAG con tres frameworks

Demo de la charla **"Agentic AI en la práctica: Explorando Frameworks y sus Capacidades"**
(Demystifying AI Series — José Arenas y Gil Rodríguez).

Resolvemos **el mismo problema** —un RAG que resume el paper de ResNet a partir de
fragmentos recuperados por búsqueda semántica— con tres frameworks, para comparar
cómo cada uno maneja la ejecución, las validaciones y los reintentos.

| Framework | Carpeta | Responsable |
|---|---|---|
| Hugging Face smolagents | `smolagents_impl/` | Gil |
| LangGraph | `langgraph_impl/` | Gil |
| Pydantic AI | `pydantic_impl/` | José |
| Sin framework (baseline) | `baseline/` | referencia |

La comparación es justa porque **lo único que cambia es el framework**: todas usan el
mismo PDF, el mismo stack de RAG y el mismo modelo de generación, definidos en
[`rag_core/config.py`](rag_core/config.py).

## Estructura

```
rag_core/              # motor RAG compartido (igual para todas las implementaciones)
  config.py            # parámetros comunes (chunking, k, modelo, reintentos)
  loader.py            # PDF -> texto (normalizado) + lista de secciones
  index.py             # troceado -> fastembed -> ChromaDB
  retrieve.py          # búsqueda semántica
  schema.py            # resumen estructurado (parte 2): puntos con su sección
  validation.py        # criterio de validación compartido (parte 2)
smolagents_impl/
  part1_basic.py       # parte 1: resumen básico
  part2_validation.py  # parte 2: validación + reintentos (bucle a mano sobre el agente)
langgraph_impl/
  part1_basic.py       # parte 1: grafo recuperar -> generar
  part2_validation.py  # parte 2: ciclo generar -> validar -> (reintentar) en el grafo
baseline/
  summarize_plain.py   # el mismo flujo SIN framework (todo a mano)
data/                  # aquí va resnet.pdf (ver data/README.md)
```

## La demo tiene dos partes

1. **Básica** — recuperar fragmentos y generar el resumen. Se ve la estructura del
   código de cada framework y qué habría que hacer a mano sin uno (eso lo muestra
   `baseline/`).
2. **Validación + reintentos** — el resumen pasa a ser estructurado (`rag_core/schema.py`):
   cada punto cita una sección. El criterio (`rag_core/validation.py`) exige que cada
   sección citada **exista** en el documento y que se citen **al menos 3** distintas.
   Si falla, se reintenta (hasta `MAX_INTENTOS`).

   Lo interesante es **cómo cada framework orquesta ese reintento**:

   | | Cómo maneja el reintento |
   |---|---|
   | **baseline** | Un `for` a mano: generar → validar → repetir. |
   | **smolagents** | Igual, un bucle nuestro alrededor de `agent.run()`. El framework aporta el ciclo de herramientas, no la validación. |
   | **LangGraph** | Un **ciclo explícito en el grafo**: nodo `validar` + arista condicional que vuelve a `generar`. |
   | **Pydantic AI** (José) | Validadores de salida + reintento declarativo del propio framework. |

## Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env    # y pon tu OPENAI_API_KEY
```

Descarga el PDF de ResNet en `data/resnet.pdf` (ver [`data/README.md`](data/README.md)).

Corre una implementación **desde la raíz del proyecto**:

```powershell
python -m smolagents_impl.part1_basic
python -m smolagents_impl.part2_validation
python -m langgraph_impl.part1_basic
python -m langgraph_impl.part2_validation
python -m baseline.summarize_plain
```

## Stack

- **Embeddings:** fastembed (`BAAI/bge-small-en-v1.5`, local)
- **Base vectorial:** ChromaDB (en memoria)
- **Generación:** OpenAI (`gpt-4o-mini`)
