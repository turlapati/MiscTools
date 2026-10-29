---
name: architecture-guide
description: Write docs/ARCHITECTURE.md — an explanation of how this codebase works, written for a developer joining the team.
argument-hint: "[folder to focus on — empty = whole repo]"
agent: agent
---

# Write the architecture guide for a new developer

You are the senior engineer who knows this codebase best, writing the guide you wish you'd had in your first week. The reader is a competent developer who has never seen this code. After one read, they should be able to explain to a colleague what the system does, how its main parts fit together, how the important flows work, and where to make a typical change — before opening the code.

**Scope:** ${input:scope:folder to focus on (leave empty for the whole repo)} — if empty, the whole repo
**Output:** `docs/ARCHITECTURE.md` (or `<folder>/docs/ARCHITECTURE.md` when a folder is given).

## Part 1 — Understand first (research; none of this appears in the document)

Build a real understanding before writing a word. Read the important code in full; skimming produces vague documents.

If Graphify is installed, use it to decide *what to read*: `graphify query "<question>"`, `graphify path <A> <B>` and `graphify explain <thing>` quickly show which code is connected to what. Then read that code. The graph is a research aid only: its vocabulary (communities, nodes, edges, god nodes, EXTRACTED/INFERRED) never appears in the document.

Answer these for yourself:
1. What problem does this system solve, and for whom? What calls it, and what does it call?
2. What are the core domain concepts (the nouns)? How do they relate, and what states do they move through? Which project-specific terms will a newcomer not know?
3. What are the major components, by responsibility? What does each own, and what does it deliberately not do? How do they talk (in-process calls, HTTP, queues, shared database)?
4. Which 2–3 flows matter most to the business? Trace each end to end through the actual code: validation, business rules, persistence, side effects, failure handling.
5. Where does data live, who owns it, and how do schema changes happen?
6. What conventions does the code follow? Where do validation, auth, error handling, transactions, logging and config live? What pattern does a new endpoint, handler or job follow?
7. Why is it built this way? Look in ADRs, README, design docs, code comments and commit messages (`git log --grep=<topic>`). If you can't find the reason, record it as unknown; never invent one.
8. How do you run and test it, and what trips people up? Look at manifests, CI config, docker-compose and `.env.example`; CI is the most reliable source for real commands.

Large codebase → depth over breadth. The core domain and the main flows deserve the words; peripheral utilities get a sentence.

## Part 2 — Write the document

Use these sections. If one doesn't apply, say so in a single line.

1. **What this system is.** One short paragraph: purpose, users, place in the wider landscape. Then a context diagram (Mermaid `flowchart`): the system as one box, the people and external systems around it, arrows labeled with what flows between them. Business names, not file paths.
2. **Key concepts.** The domain model in prose: the main entities, how they relate, their lifecycle and states. Add a Mermaid `classDiagram`, `erDiagram` or `stateDiagram` if it helps (≤10 boxes). End with a glossary of project-specific terms.
3. **How the code is organized.** The major components, named by what they do ("Order intake", "Pricing engine", "Notification worker"). For each: its responsibility, what it deliberately does not do, what it depends on, and where it lives (one path). A component diagram showing how they talk. Name the architectural style and explain how the code follows it, and where it doesn't.
4. **How the important things work.** 2–3 walkthroughs of the key flows, told as numbered steps: what happens at each step and *why*, what can fail and how that's handled. Name the class or function where it matters; put the file path at the end of the step for the reader who wants to open it. One Mermaid `sequenceDiagram` per flow, with components as participants.
5. **Data.** Where state lives and who owns it; the important tables or collections and how they relate; how migrations work; the consistency and transaction approach; caches.
6. **Cross-cutting concerns.** Whichever exist: auth, validation, error handling, logging and observability, configuration, background jobs, feature flags. For each: the approach, and the one place to look.
7. **Design decisions and trade-offs.** The non-obvious choices, why they were made (if known), and what they cost. Mark unknown reasons as "(rationale not documented)".
8. **Making common changes.** Recipes for the 2–3 most common changes (e.g. "Add an API endpoint", "Add a field to an entity", "Add a background job"): the files to touch, in order, the conventions to follow, and the tests to add.
9. **Running it locally.** Prerequisites with versions; setup, run and test commands, taken from CI or scripts; required environment variables (names and what each is for, never values).
10. **Gotchas.** Things that will cost a newcomer an afternoon, each with the fix.
11. **Where to go next.** The 5 files to read first, in order, and what each one teaches. Then open questions for the team.

## Writing rules

- **Explain, then point.** Every paragraph says how or why something works. A path is a signpost at the end, at most one or two per paragraph. A sentence whose only content is file paths gets deleted.
- **Name things by what they do**, not by their folder.
- **Diagrams show concepts and responsibilities**: 5–12 boxes, labeled arrows. Never diagram files or import graphs.
- **No metrics in the document**: no churn counts, fan-in, line ranges, node counts, confidence tags or "evidence" columns. They mean nothing to the reader.
- **Short, real code excerpts** (≤15 lines) are welcome where they show a pattern the reader must follow, such as how a handler is structured.
- **Be concrete.** Write "checkout reserves stock before charging the card, so a failed payment releases the reservation immediately", not "the system handles inventory consistency".
- **Be honest about uncertainty.** "Appears to", "(not confirmed)", or move it to Open questions. Never invent behavior or rationale.
- **Length follows the code.** A small service may need 3 pages; a large system 15. Depth in the core, a line for the periphery.

What to avoid:
> **OrderService** (`src/services/order.service.ts:12–188`) — domain · fan-in 14 · churn #2 · community 3. Depends on `src/repos/order.repo.ts`, `src/clients/stripe.ts`.

What to write:
> **Order processing** turns a cart into a paid order. It re-prices the cart first (prices can change between add-to-cart and checkout, so the stored cart total is never trusted), reserves stock, then charges the card. If the charge fails, the reservation is released immediately instead of waiting for the nightly cleanup job, which is why `OrderService.place()` wraps both steps in one try/finally. Lives in `src/services/order.service.ts`.

## Part 3 — Review before saving

Reread the document as the new developer, and fix what fails:
- Could I explain each key flow to someone after reading it once? If not, the walkthrough is too thin.
- Does any section just list names or files without saying what they do? Rewrite it or cut it.
- Does every diagram make sense without knowing the folder structure?
- Is every behavior I describe something I saw in the code, not assumed? Does every path I mention exist (`git ls-files <path>`)?
- Is anything a newcomer needs on day one missing: the main concept, the main flow, how to run it?

Save the file; don't commit. Reply with a two-sentence summary of the system, the sections you're least confident in, and the open questions.
