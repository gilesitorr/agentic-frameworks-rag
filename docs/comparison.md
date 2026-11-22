# Comparison points for the talk

All of this comes from building and running the same system in the three frameworks.

## The controlled experiment

Same problem (summarize ResNet), same stack (fastembed + ChromaDB + `gpt-4o-mini`),
same PDF. Besides the framework, the implementations differ in pattern: the baseline and
LangGraph are **workflows** (one fixed query, then one LLM call), while smolagents and
Pydantic AI are **agents** (the LLM decides what to search, through a tool).

> The model and the RAG are identical, so the framework does not make the LLM write better.
> What shows in the output is the pattern: the agents search several times and cover more
> sections, while the workflows only see the 5 chunks of their single query.

## The frameworks at a glance

| | Approach | Strong at | Costs |
|---|---|---|---|
| **smolagents** | Lightweight agent with tools; the agent decides when to use them. | Fast prototyping, little code. | No validation or retries built in: you add them. |
| **LangGraph** | Flow as an explicit state graph, with cycles. | Flow control, retry as a natural cycle, state. | More ceremony for simple cases. |
| **Pydantic AI** | Agent with tools, typed output, validators and declarative retries. | Validated output and retries "out of the box"; dependency injection. | Less explicit flow control than a graph. |
| **No framework** | Everything by hand. | Zero dependencies, full control. | You write and maintain everything. |

## Part 2 is where the difference shows

Adding *validate that the summary cites real sections + retry* is solved differently:

- **baseline:** a hand-written `for`.
- **smolagents:** a loop of ours around `agent.run()`.
- **LangGraph:** a cycle in the graph (`validate` node + conditional edge).
- **Pydantic AI:** an `@agent.output_validator` that raises `ModelRetry`; the framework runs the retry.

## The honest number: lines of code (part 2, with docstrings)

| baseline | smolagents | LangGraph | Pydantic AI |
|---|---|---|---|
| 59 | 79 | 81 | 69 |

For a simple case, **the framework costs lines, it does not save them** (by hand it is 59).
The payoff appears when the flow grows: more branches, state, tools, retries at several
points. (smolagents adds lines because you have to normalize its output, which is not
structured by default.)

## How to choose

- **smolagents** → prototypes and tool-using agents, with minimal code.
- **LangGraph** → flows with state, cycles and branches; explicit control.
- **Pydantic AI** → when validated output and retries are the center.
- **No framework** → trivial cases; does not scale.

Rule of thumb: **the complexity of the flow rules**. Simple → little framework; with
decisions, cycles and state → the framework pays for itself.

## Details we lived while building

- The RAG is identical in the three; the differentiator is the orchestration.
- `gpt-4o-mini` is very obedient: to see a retry we had to raise the section threshold.
  Validate + retry is cheap and covers exactly when the model fails.
- smolagents returns the output as an already-parsed dict (not JSON) and retries on API
  errors with a long backoff (~11 min): two things to watch in a live demo.
- baseline and LangGraph part 2 parse the JSON outside the retry loop: a schema mismatch
  stops the run. smolagents catches it by hand; Pydantic AI retries it automatically.
