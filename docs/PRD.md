# Product Requirements Document — Multi-Agent Task Solver

| Field | Value |
|---|---|
| **Product** | Multi-Agent Task Solver (MATS) |
| **Document status** | Draft v1.0 (productization PRD, supersedes interview brief) |
| **Owner** | Engineering (Lalit) |
| **Last updated** | 2026-06-25 |
| **Origin** | Wand AI engineering challenge — *Challenge 1: Multi-Agent Task Solver* (24h solo build, Oct 2025) |
| **Related docs** | [WIKI.md](../WIKI.md) · [critical-analysis.md](./critical-analysis.md) · [implementation-plan.md](./implementation-plan.md) · [testing-plan.md](./testing-plan.md) · [README.md](../README.md) |

> This PRD reframes the original interview challenge (preserved verbatim in **Appendix A**) as a proper product spec we can iterate on. It separates *what the product must do* (requirements, here) from *how we build it* (see [implementation-plan.md](./implementation-plan.md)) and *how good it is today* (see [critical-analysis.md](./critical-analysis.md)). Requirement IDs (`FR-*`, `NFR-*`) are stable handles that the [testing plan](./testing-plan.md) maps test cases onto.

---

## 1. Executive summary

The Multi-Agent Task Solver accepts a high-level business request in plain language (e.g. *“Summarize the last 3 quarters’ financial trends and create a chart”*), **plans** it into subtasks, dispatches those subtasks to **specialized AI agents** that can use **tools** (web search, code execution, file I/O), and **aggregates** their outputs into a single structured answer — while streaming **progress/status** back to the user.

An initial working prototype exists (FastAPI + LangGraph, dual LLM support, cascading web search, code-exec sandbox, simple polling UI). This PRD defines the target product the prototype evolves toward, and the bar each capability must clear to be considered "done."

## 2. Background & context

- The product began as a 24-hour solo interview challenge (Appendix A). The submitted prototype (`MSP-1`) is real and runnable but makes deliberate 24h trade-offs (local-only, no persistence, insecure code-exec, sequential execution).
- We are now treating it as a real product: hardening it, closing the gap to a modern agentic system, and building iteratively against this PRD. The forward direction is captured in [implementation-plan.md](./implementation-plan.md); the honest gap assessment is in [critical-analysis.md](./critical-analysis.md).

## 3. Problem statement

Knowledge workers routinely have **compound, multi-step requests** that a single LLM call handles poorly: they need fresh facts (search), computation/plots (code), synthesis (summarization), and a coherent final deliverable — with **visibility** into what the system is doing and **trust** that it isn't hallucinating. A single prompt to a chat model conflates planning, retrieval, computation, and writing, and gives the user no transparency. We need an orchestrated system of specialized agents that decomposes the request, executes subtasks with the right tools, and returns a structured, attributable result.

## 4. Goals & non-goals

### 4.1 Goals
- **G1** — Turn one plain-language business request into a correct, structured, multi-part deliverable without the user pre-decomposing it.
- **G2** — Use *specialized* agents with clear roles and real tool access (search, code, files), sharing context with each other.
- **G3** — Give the user live visibility into planning and per-agent progress.
- **G4** — Actively reduce LLM failure modes (hallucination, repetition, silent error) rather than just hoping the model behaves.
- **G5** — Handle ambiguous/incomplete requests by asking clarifying questions instead of guessing (the "High Marks" bar).
- **G6** — Be safe and operable enough to run beyond a single trusted laptop (sandboxing, persistence, observability).

### 4.2 Non-goals (for now)
- Not a general autonomous agent that takes real-world actions (sending email, making purchases, modifying prod systems).
- Not a fine-tuning / model-training platform — we orchestrate hosted/served models.
- Not a full BI/dashboarding product — chart/code output is a capability, not the product surface.
- Not multi-tenant SaaS with billing in the near-term milestones (revisit — see [WIKI Open Questions](../WIKI.md#open-questions)).

## 5. Target users & personas

| Persona | Description | Primary need |
|---|---|---|
| **Operator (primary)** | Analyst / ops / founder issuing compound business questions | Get a trustworthy structured answer without writing code or doing manual research |
| **Builder** | Engineer extending agents/tools | Add an agent or tool without rewiring the whole system |
| **Reviewer / auditor** | Someone validating an answer | Trace which agent produced what, from which source, with what tool calls |

## 6. Use cases & user stories

- **UC1 — Research + synthesis:** *“Summarize the latest news on AI advancements and give key market-growth statistics.”* → researcher(s) search, summarizer condenses, aggregator produces a cited brief.
- **UC2 — Data + computation + chart:** *“Summarize the last 3 quarters’ financial trends and create a chart.”* → data analyst writes/executes code, produces a chart artifact, summarizer narrates it.
- **UC3 — Live fact + calculation:** *“Find NVDA’s current price and compute its 5-day moving average.”* → researcher fetches price, code executor computes, aggregator reports.
- **UC4 — Ambiguous request (High Marks):** *“Make me a report on our performance.”* → system detects missing scope (which metric? which period?) and asks a clarifying question before planning.
- **UC5 — Multi-turn refinement (Stretch):** after a first answer, *“now redo it for EMEA only and add a chart”* → system refines using prior context.
- **UC6 — Live conversation (Stretch):** user chats with the orchestrator mid-execution to steer it.

## 7. Scope & release strategy

The original brief frames build levels (`MSP-1` → features → submission). We keep that staged philosophy:

| Stage | Theme | Status |
|---|---|---|
| **M0 — MSP-1 prototype** | Plan → execute (sequential) → aggregate; tools; polling UI; dual LLM | ✅ Built (Oct 2025) |
| **M1 — Correctness & trust** | Structured outputs, real tool-calling loop, error recovery, partial results, eval harness | ⏳ Planned |
| **M2 — Safety & ops** | Sandboxed code-exec, persistence, auth/limits, observability/tracing, cost accounting | ⏳ Planned |
| **M3 — Intelligence** | Clarifying questions, reflection/verification, parallel execution, dynamic replanning | ⏳ Planned |
| **M4 — Interaction (stretch)** | Multi-turn refinement, live conversation/steering, SSE/WebSocket streaming | ⏳ Planned |

Detailed sequencing, dependencies, and effort are in [implementation-plan.md](./implementation-plan.md).

## 8. Functional requirements

Each requirement has a stable ID, a priority (**P0** must-have / **P1** should / **P2** stretch), and a verifiable acceptance criterion. The original brief's five core requirements are FR-1…FR-5.

### Core pipeline
- **FR-1 — Natural-language input (P0).** The system accepts a free-text business request via UI and API. *Accept:* a request submitted via UI or `POST /api/tasks` returns a task id and begins processing.
- **FR-2 — Planning / decomposition (P0).** A planner decides which agents are needed and what each does, producing an ordered (later: dependency-aware) set of subtasks. *Accept:* for a compound request, the plan contains ≥2 subtasks each naming an agent and its tools; the plan is inspectable.
- **FR-3 — Specialized execution (P0).** Each subtask is executed by a role-specialized agent that may invoke tools. *Accept:* an agent assigned `web_search_tool` actually performs a search and its result feeds downstream; agent role is recorded per subtask.
- **FR-4 — Aggregation (P0).** Subtask results are combined into a single, coherent, structured final answer referencing the original request. *Accept:* final answer is non-empty, addresses the request, and reflects ≥1 subtask result.
- **FR-5 — Progress visibility (P0).** The user sees per-stage / per-agent status updates as the task runs. *Accept:* progress log shows distinct, informative entries for planning and each subtask (not empty placeholders).

### Agent design expectations
- **FR-6 — Clear role definitions (P0).** Each agent type (researcher, summarizer, data analyst, code executor, …) has a distinct, specialized system prompt. *Accept:* changing the agent type measurably changes behavior/tooling.
- **FR-7 — Context sharing (P0).** Agents can see relevant prior subtask results. *Accept:* a downstream agent's output demonstrably uses an upstream result; context passed is relevant (not the entire unbounded history once M1 lands).
- **FR-8 — Tool usage (P0).** Agents can call a Python code executor, a web-search API, and file I/O, with correct argument schemas. *Accept:* each tool is invokable by an agent with valid inputs and its result is captured; a malformed tool call is handled gracefully, not crashed.
- **FR-9 — Iterative tool reasoning (P1).** An agent can call a tool, observe the result, and reason/act again within a bounded loop (ReAct-style), rather than a single one-shot probe. *Accept:* an agent can do search→reason→search, or run-code→see-error→fix, within a step budget.

### Reliability & trust
- **FR-10 — Hallucination/repetition mitigation (P0).** The system uses structured outputs, grounding, and verification to reduce fabrication and looping. *Accept:* search-grounded answers cite sources; a verification/aggregation step is present; outputs are schema-validated.
- **FR-11 — Graceful failure & partial results (P1).** A failed subtask does not abort the whole task; the user gets partial results plus a clear error. *Accept:* injecting a failure in one subtask still yields a final answer covering the others.
- **FR-12 — Structured machine-readable output (P1).** Final and intermediate outputs are available as structured JSON (not just prose). *Accept:* API returns a structured result object (answer + per-agent trace + sources).

### High-marks & stretch
- **FR-13 — Clarifying questions for ambiguity (P1, "High Marks").** When the request is underspecified, the system asks a targeted question before (or instead of) producing a low-confidence plan. *Accept:* a deliberately vague request triggers a clarification rather than a hallucinated plan.
- **FR-14 — Multi-turn refinement (P2, stretch).** The user can modify the request after the first output and the system refines using prior context. *Accept:* a follow-up request reuses prior task context and updates the result.
- **FR-15 — Live conversation / mid-run steering (P2, stretch).** The user can chat with the orchestrator during execution to adjust direction. *Accept:* a mid-run message changes subsequent agent behavior.
- **FR-16 — Model selection (P1).** The user/operator can select the LLM backend (e.g. GPT-class, Gemini-class) per request. *Accept:* selection is honored end-to-end; "both" has defined semantics (documented, not silently ignored).

## 9. Non-functional requirements

- **NFR-1 — Security / sandboxing (P0).** Untrusted code execution and file I/O must be isolated (no host RCE, no arbitrary path read/write) before any non-trusted exposure. *Accept:* code-exec runs in an isolated, resource-limited sandbox; file I/O is confined to a workspace dir; endpoints enforce auth + input size limits.
- **NFR-2 — Reliability (P1).** Transient LLM/search/tool failures are retried with backoff; the system degrades gracefully. *Accept:* injected transient failures recover without task abort.
- **NFR-3 — Persistence & durability (P1).** Task state survives process restart and is safe across multiple workers. *Accept:* a task in flight or completed is retrievable after a restart.
- **NFR-4 — Observability (P1).** Every run is traceable: per-agent prompts, tool calls, tokens, latency, cost, and errors. *Accept:* a run produces a trace and per-run token/cost totals.
- **NFR-5 — Performance / latency (P2).** Independent subtasks may run concurrently; the system honors a concurrency setting. *Accept:* independent subtasks execute in parallel; wall-clock < sum of subtask times for a parallelizable plan.
- **NFR-6 — Cost control (P2).** Per-task token/cost budgets are enforceable. *Accept:* a configurable budget caps spend per task.
- **NFR-7 — Extensibility (P1).** Adding an agent or tool requires changes in one place, not scattered edits. *Accept:* registering a new tool wires it into planner awareness, agent availability, and schema validation via a single registration point.
- **NFR-8 — Usability (P1).** The UI clearly shows plan, live progress, final answer, and any rendered artifacts (charts/files). *Accept:* artifacts produced by agents are surfaced, not just text.
- **NFR-9 — Configuration integrity (P1).** Declared config (models, keys, limits) matches actual runtime behavior and documentation. *Accept:* no config keys that are read but never used; docs and defaults agree.

## 10. System overview

```
User ──> UI (web) / API
            │  POST /api/tasks
            ▼
      Orchestrator (LangGraph state machine)
        ├─ Planner agent        → subtasks [{description, agent, tools}]
        ├─ [Clarifier]          → ask user if ambiguous   (target)
        ├─ Executor(s)          → role-specialized agents w/ tool loop
        │     └─ Tools: web search · code executor · file I/O
        ├─ [Verifier/Reflection]→ check outputs            (target)
        └─ Aggregator           → final structured answer
            │  progress events (poll today → SSE/WS target)
            ▼
        Task store (in-memory today → durable store target)
```
Detailed component design, state schema, and the target graph topology live in [implementation-plan.md](./implementation-plan.md).

## 11. Agent & tool catalog

**Agents (roles):** `planner`, `researcher` (web search), `summarizer` (synthesis, no tools), `data_analyst` (code/plots), `code_executor` (run code), `aggregator`. Target additions: `clarifier`, `verifier/critic`.

**Tools:** `web_search_tool` (cascading Tavily → Perplexity → DuckDuckGo), `python_executor_tool` (sandboxed — see NFR-1), `file_io_tool` (workspace-confined read/write/append). Each tool must declare an explicit input schema that the planner and agents are aware of (FR-8, NFR-7).

## 12. Success metrics

- **Task success rate** — % of runs that return a correct, on-request structured answer (graded by an eval harness / LLM-as-judge + spot human review).
- **Plan validity rate** — % of planner outputs that parse and are executable on the first try (target: ≥99% with structured outputs).
- **Tool-call success rate** — % of attempted tool calls with valid args that execute without error.
- **Grounding/citation rate** — % of factual claims in search-backed answers traceable to a returned source.
- **Robustness** — % of injected-failure runs that still return useful partial results (FR-11).
- **Latency & cost** — median wall-clock and median token/cost per task, tracked per release.
- **Clarification precision** — clarifying questions asked only when genuinely ambiguous (low false-positive rate) (FR-13).

## 13. Risks & mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Insecure `exec()` code path is web-reachable | RCE / data loss | NFR-1 sandboxing is a release gate before any exposure; see [critical-analysis.md](./critical-analysis.md) |
| Brittle hand-parsed LLM JSON | Task aborts, poor UX | Move to native structured outputs / function calling (FR-2, FR-10) |
| Unbounded context sharing | Cost blowup, context overflow | Context selection/compaction (FR-7, NFR-6) |
| Docs overstate capabilities (e.g. "parallel") | Lost trust | Reconcile docs to code (NFR-9); tracked in critical-analysis |
| Single-LLM-vendor coupling / auth drift | Outages, broken Gemini path | Validate config integrity, abstract the LLM layer (FR-16, NFR-9) |

## 14. Open questions

Tracked and prioritized in [WIKI.md → Open Questions](../WIKI.md#open-questions). Highlights: target deployment surface (single-tenant vs SaaS); whether to adopt an off-the-shelf agent framework vs the current bespoke LangGraph wiring; sandbox technology choice; eval dataset ownership.

## 15. Out of scope (this PRD)

Real-world side-effecting actions; model fine-tuning; enterprise SSO/RBAC and billing; mobile clients; offline/local-LLM hosting (explicitly deferred in the original 24h trade-offs).

---

## Appendix A — Original challenge brief (verbatim source of truth)

> **Wand AI — Engineering Challenges.** Build a system that accepts a high-level business request in plain language (e.g. *“Summarize the last 3 quarters’ financial trends and create a chart”*), then uses **multiple specialized AI agents** to break down the task, execute subtasks, and return a final structured result.
>
> **Core Requirements (all roles):** (1) **Input** — user enters a business request in text. (2) **Planning** — the system decides which agents are needed and what each should do. (3) **Execution** — agents complete their tasks and share results. (4) **Aggregation** — the system combines results into a final answer. (5) **Visibility** — user sees progress/status updates for each agent.
>
> **Expectations:** design agents with clear role definitions (specialized prompts), context sharing between agents, and tool usage (e.g. Python code executor, search API). Demonstrate orchestration logic that avoids common LLM pitfalls (hallucination, repetition). **High Marks:** agents can handle ambiguous or incomplete tasks by asking clarifying questions.
>
> **Stretch goals:** add a "live conversation" mode where the user can chat with the orchestrator mid-execution; support multi-turn refinement (user modifies request after first output).
>
> **General deliverables:** working prototype (local or hosted); README (design decisions, 24h trade-offs incl. local hosting / local LLM, how to run/test); short Loom/screen-recording demo (≤5 min); code in a GitHub repo.
>
> *Constraints noted at interview:* solo, 24 hours; MSP-1 first (agentic stack + AI backend engineering), then features (MCP?, asynchronous), with ~1h reserved for submission packaging (GitHub, README/report/how-to-test, demo link). Round-1 interview emphasis: code & logic of MSP-1, then concepts around it, with a learning spirit.

## Appendix B — Current implementation snapshot (as of this PRD)

- **Stack:** FastAPI (`main.py`), LangGraph orchestrator (`orchestrator.py`), tools (`tools.py`), config (`config.py`), static polling UI (`static/index.html`).
- **Graph:** `planner → agent_executor (self-looping, sequential) → aggregator → END`.
- **LLMs:** OpenAI (`ChatOpenAI`) and Gemini via **Vertex AI** (`ChatVertexAI`); selection via request flags.
- **Tools:** cascading web search (Tavily → Perplexity → DuckDuckGo); `exec()`-based Python runner (explicitly insecure); unrestricted file I/O.
- **State:** in-memory `task_storage` dict; background-task processing; UI polls every 3s.
- **Known status vs this PRD:** FR-1…FR-8 partially met; FR-9/FR-11/FR-13 and most NFRs are **not yet met**. The detailed, evidence-backed gap analysis is in [critical-analysis.md](./critical-analysis.md), and the remediation sequence is in [implementation-plan.md](./implementation-plan.md).

## Glossary

- **Orchestrator** — the LangGraph state machine coordinating planning, execution, aggregation.
- **Agent** — an LLM invocation specialized by role/system-prompt, optionally tool-enabled.
- **Tool** — a callable capability (search, code, file) an agent can invoke.
- **Subtask** — one unit of the plan, assigned to an agent with a tool set.
- **Aggregation** — synthesis of subtask results into the final deliverable.
- **MSP-1** — the first minimal shippable product (the Oct 2025 prototype).
