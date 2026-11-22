# Flow diagrams

One **generic** picture of what the RAG system does, then a **detailed** diagram per
example that mirrors the generic one but adds the real functions and their order.
(GitHub renders Mermaid automatically.)

---

## 1. Generic — what RAG does

Two phases: build the index once, then answer a query.

```mermaid
flowchart LR
    subgraph Indexing["Indexing (once)"]
        PDF[PDF] --> CHUNK[Chunk]
        CHUNK --> EMBED[Embed]
        EMBED --> STORE[(Vector store)]
    end
    subgraph Querying["Querying"]
        Q[Question] --> RET[Retrieve top-k]
        STORE --> RET
        RET --> GEN[LLM generate]
        GEN --> ANS[Answer]
    end
```

**Part 2** adds a check: the answer must be valid; if not, generate again.

```mermaid
flowchart LR
    Q[Question] --> RET[Retrieve] --> GEN[Generate] --> VAL{Valid?}
    VAL -- no --> GEN
    VAL -- yes --> ANS[Answer]
```

Everything above the frameworks is **shared** (`rag_core`): `build_rag` does
PDF → chunk → embed → store, and `Rag.retrieve` does the top-k lookup. What changes per
framework is only **how the query/validation/retry flow is wired**.

---

## 2. smolagents

The RAG lives in a tool; the agent decides when to call it.

### Part 1 — basic

```mermaid
flowchart TD
    BUILD["build_rag('data/resnet.pdf')"] --> RAG[(Rag: ChromaDB + sections)]
    RUN["agent.run(task)"] --> AGENT{{ToolCallingAgent<br/>reason ↔ act loop}}
    AGENT -- calls --> TOOL["search_document(query)"]
    TOOL --> RETR["rag.retrieve(query)"]
    RETR --> RAG
    RETR -- chunks --> AGENT
    AGENT -- final answer --> OUT[Summary]
```

### Part 2 — validation + retry (our loop around `agent.run`)

```mermaid
flowchart TD
    START([start]) --> TASK["task(problems)"]
    TASK --> RUN["agent.run(task)"]
    RUN --> AGENT{{ToolCallingAgent + search_document}}
    AGENT --> NORM["normalize: dict or json.loads"]
    NORM --> MV["DocumentSummary.model_validate"]
    MV --> VS["validate_summary(summary, rag.sections)"]
    VS --> CHK{problems?}
    CHK -- "yes, attempts < MAX_ATTEMPTS" --> TASK
    CHK -- "no / MAX_ATTEMPTS" --> OUT[Print points]
```

---

## 3. LangGraph

The flow is an explicit state graph; the retry is a cycle in the graph.

### Part 1 — basic

```mermaid
flowchart LR
    START((START)) --> RET["retrieve(state)"]
    RET --> GEN["generate(state)"]
    GEN --> END((END))
    RET -. "rag.retrieve" .-> RAG[(Rag)]
    GEN -. "client.chat.completions" .-> OAI[OpenAI]
```

### Part 2 — validation + retry (conditional edge)

```mermaid
flowchart TD
    START((START)) --> RET["retrieve(state)"]
    RET --> GEN["generate(state)"]
    GEN --> VAL["validate(state)"]
    VAL --> ROUTE{"route(state)"}
    ROUTE -- retry --> GEN
    ROUTE -- end --> END((END))
```

State carries `context`, `summary`, `problems`, `attempts`. `route` returns `"retry"` or
`"end"` based on `problems` and `attempts`.

---

## 4. No framework (baseline)

The same part 2, written by hand: a `for` loop with the retry inline.

```mermaid
flowchart TD
    CTX["context = rag.retrieve(...)"] --> LOOP{{"for attempt in 1..MAX_ATTEMPTS"}}
    LOOP --> GEN["client.chat.completions.create (json)"]
    GEN --> MV["DocumentSummary.model_validate_json"]
    MV --> VS["validate_summary(summary, rag.sections)"]
    VS --> CHK{problems?}
    CHK -- yes --> LOOP
    CHK -- no --> OUT[Print points]
```

---

## 5. Pydantic AI

The RAG lives in a tool, like smolagents, but the output is typed and the retry is
**declarative**: an output validator raises `ModelRetry` and the framework re-asks the model.

### Part 1 — basic

```mermaid
flowchart TD
    BUILD["build_rag('data/resnet.pdf')"] --> RAG[(Rag: ChromaDB + sections)]
    RUN["agent.run_sync(prompt, deps=rag)"] --> AGENT{{"Agent(output_type=DocumentSummary)<br/>reason ↔ act loop"}}
    AGENT -- calls --> TOOL["search_document(ctx, query)"]
    TOOL --> RETR["ctx.deps.retrieve(query)"]
    RETR --> RAG
    RETR -- chunks --> AGENT
    AGENT -- "final answer, validated against the schema" --> OUT["result.output: DocumentSummary"]
```

### Part 2 — validation + retry (handled by the framework)

```mermaid
flowchart TD
    RUN["agent.run_sync(prompt, deps=rag)"] --> INS["@agent.instructions<br/>valid_sections(ctx)"]
    INS --> AGENT{{"Agent + search_document"}}
    AGENT --> SCHEMA{"matches DocumentSummary?"}
    SCHEMA -- "no: framework re-asks" --> AGENT
    SCHEMA -- yes --> VAL["@agent.output_validator<br/>check_sections → validate_summary"]
    VAL --> CHK{problems?}
    CHK -- "yes: raise ModelRetry (up to retries)" --> AGENT
    CHK -- no --> OUT["result.output"]
```

The loop in the diagram is not code we wrote: `ModelRetry` and the schema check feed the
problems back to the model, up to `retries=MAX_ATTEMPTS - 1` times.
