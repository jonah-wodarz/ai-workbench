---
name: "layered-design-facilitation"
description: "Facilitate open-ended design, brainstorming, and ideation by decomposing the problem into layers of abstraction and working top-down by default, one layer at a time. Use whenever the user is designing or thinking through something open-ended and exploratory — game design, system architecture, product concepts, requirements, research directions — especially early on before details are settled, and especially in Claude Cowork. Proactively propose a layered model sized to the problem, keep work anchored at the current layer, and gate premature descent into concrete detail — whether it comes from Claude's own output OR from the user jumping ahead — while offering deliberate moves between layers (park, probe, ascend). Trigger at the start of any exploratory design session, and whenever the discussion drifts into specifics before the higher layers are resolved."
---

# Layered Design Facilitation

Open-ended design drifts downward one small step at a time, until concrete decisions exist without the structure that should govern them. Work **top-down by default**, one layer at a time, and change layers only through a named move.

Project conventions (e.g. `docs/CONVENTIONS.md`) override this skill. Read them at the start of a session.

## 1. Layers

Early in the session, propose a layered model sized to the problem and confirm it. Default stack, shared with **design-capture**:

| Layer | Question it answers | In a game | In software or requirements work |
|---|---|---|---|
| **L0 Vision** | What outcome, for whom, on which pillars? | The feeling the game should create | Goals and success criteria |
| **L1 Intent** | Which systems produce it, and what is each one for? | Combat, progression, economy | Capabilities, components, responsibilities |
| **L2 Mechanics** | How does each system behave: rules and interactions? | How a weapon upgrade works | Behaviour rules, workflows, interfaces |
| **L3 Parameters** | Which numbers, formulas, thresholds? | Damage values, drop rates | Limits, quotas, performance targets |
| **L4 Implementation** | How is it built? | Code, data files, config | Architecture, code, deployment |

Name the layers in the project's own words and adapt the count to the problem. The L-numbers and the questions stay fixed.

## 2. Each turn

1. State the layer of the system under discussion. Systems can sit at different layers.
2. Answer at that layer.
3. Give anything that belongs to another layer a move from section 3, whether it comes from Claude's own draft or from the user. Name the layer and offer the choice: "That's an L3 idea and this system is at L1. Park it, or probe now to answer <question>?"
4. The user can waive a gate for one step. Follow the override, note it in one line, and report repeated overrides of the same gate at the next checkpoint.

Gate the drifts that matter and let minor specifics pass. When unsure which it is, ask.

## 3. Moves

| Move | Use it when | What happens |
|---|---|---|
| **Park** | An idea belongs to another layer or system and the current work can proceed without it | One line in the parking lot; return to the current layer |
| **Descend** | The layer's blocking questions are resolved | Announce it and confirm; the system's layer moves down |
| **Probe** | A current-layer question can only be answered by trying something concrete: sketched rules, trial numbers, a prototype, a play-test | Name the question and what will be tried. Work below. Record the findings as provisional. Return and answer or reword the question. The system's layer stays where it was |
| **Ascend** | A lower-layer finding contradicts or outgrows a rule above it | Name the upper rule, reopen it at its own layer, resolve it, then sweep everything that traced to it |

A parked idea goes to the parking lot, so the user sees it was captured and only its timing is deferred. An idea the user rules out goes to the *Out of scope* list. **design-capture** owns both formats.

After each build or play round, collect what it showed, ascend where it breaks a rule, and close the questions it answered. Returning to upper layers is an expected part of the work.

## 4. Rules per layer

**Ideas.** When a layer or system opens, ask for the user's ideas first and record them. Then offer two or three options that differ in kind, each with its trade-off, marked as proposals. Give a single recommendation when asked.

**Quantities.** Above L3, strength, cost and size are **orderings** ("A above B") or **tiers**. Restate early numbers as the ordering they imply, confirm it, and park the raw numbers for L3. A probe may use trial numbers; they are recorded as placeholders.

**Questions.** One question asks for one decision: answerable in a sentence or by choosing among named options. Split a larger question, ask the framing part first, and say how many parts follow. Ask what the next step needs; the rest stays in the open-question list. Ask open questions at L0 and L1, and offer named options from L2 on. A question only building or playing can answer is tagged `needs-build` and waits for the next probe or build round.

**Interfaces.** At L1, name for each system what it provides to other systems and what it needs from them. From L2 on, a system relies on other systems only through those interfaces. Keep the dependencies of each system few. Resolve a dependency cycle before descending: merge the systems, or move the shared part into a system of its own.

**Vision.** Re-read the vision at the start of a session. Before a system leaves L1 and at every layer change, check two things: every pillar names the system that owns it (an unowned pillar becomes an L1 question), and the vision still matches what the settled systems say (where it has drifted, ascend).

## 5. Recording

This skill owns altitude: which layer a thought belongs to and which move fits. **design-capture** records decisions, probe findings and questions; **structured-project-docs** places the files. Without a docs tree, keep a short running list of parked ideas in the conversation.
