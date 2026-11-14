---
name: "layered-design-facilitation"
description: "Facilitate open-ended design, brainstorming, and ideation by decomposing the problem into layers of abstraction and working top-down by default, one layer at a time. Use whenever the user is designing or thinking through something open-ended and exploratory — game design, system architecture, product concepts, requirements, research directions — especially early on before details are settled, and especially in Claude Cowork. Proactively propose a layered model sized to the problem, keep work anchored at the current layer, and gate premature descent into concrete detail — whether it comes from Claude's own output OR from the user jumping ahead — while offering deliberate moves between layers (park, probe, ascend). Trigger at the start of any exploratory design session, and whenever the discussion drifts into specifics before the higher layers are resolved."
---

# Layered Design Facilitation

Open-ended design fails in a predictable way: the thinking drifts *downward* through levels of abstraction one small step at a time. Each step feels like progress, but concrete decisions get made before the structure that should govern them exists.

Run exploratory design **top-down by default**: establish the layers, work one layer at a time, and make every change of layer a deliberate, announced move. Top-down is the default order, and the moves in section 3 are how a session leaves it on purpose: lower layers answer questions for the layers above and can overturn them.

## 0. Project conventions win

If the project defines its own conventions (e.g. `docs/CONVENTIONS.md`), they override this skill wherever the two differ. Read them at the start of a session.

## 1. Decompose early, sized to the problem

Early in an exploratory session, propose a **layered model** of the problem, fitted to its scale. Sketch it, name the layers, and confirm the shape before proceeding.

The default stack is shared with the **design-capture** skill, so conversation and documentation use the same vocabulary:

| Layer | Question it answers | In a game | In software or requirements work |
|---|---|---|---|
| **L0 Vision** | What outcome, for whom, on which pillars? | The feeling the game should create | Goals and success criteria |
| **L1 Intent** | Which systems produce it, and what is each one for? | Combat, progression, economy | Capabilities, components and their responsibilities |
| **L2 Mechanics** | How does each system behave: rules and interactions? | How a weapon upgrade works | Behaviour rules, workflows, interfaces |
| **L3 Parameters** | Which numbers, formulas, thresholds? | Damage values, drop rates | Limits, quotas, performance targets |
| **L4 Implementation** | How is it built? | Code, data files, config | Architecture, code, deployment |

Name the layers in the project's own words (a requirements project may call L2 "Behaviour") and adapt the count to the problem's size. The L-numbers and the questions stay fixed, so capture and facilitation stay aligned.

## 2. Anchor the current layer

At any moment, know and state **which layer you are working at**, per system: different systems can sit at different layers.

**Keep the top layers fresh.** The vision is the layer most likely to drift unnoticed while work happens below it. Re-read it at the start of a session, and run this check before the first system leaves L1, at every layer change of a system, and after a run of narrowly scoped sessions:

- Every pillar of the vision names the system that owns it. A pillar without an owner becomes an open question at L1.
- The vision still describes what the settled systems say. Where it has drifted, ascend (section 3).

## 3. Moves between layers

| Move | Use it when | What happens |
|---|---|---|
| **Stay** | Default | Answer at the current layer |
| **Park** | An idea belongs to another layer or system and the current work can proceed without it | One line in the parking lot; return to the current layer |
| **Descend** | The layer's blocking questions are resolved | Announce it and confirm; the system's layer moves down |
| **Probe** | A current-layer question can only be answered by trying something concrete: sketched rules, trial numbers, a prototype, a play-test | Name the question the probe serves and what will be tried. Work below. Record the findings as provisional. Return and answer or reword the question. The system's layer stays where it was |
| **Ascend** | A finding at a lower layer contradicts or outgrows a rule above it | Name the upper rule and reopen it at its own layer. Resolve it there, then sweep everything that traced to it |

A parked idea goes to the **parking lot** (format and location defined by **design-capture**), so the user sees it was captured and only its timing is deferred. An idea the user rules out goes to design-capture's *Out of scope* list.

Returning to upper layers after rounds of building is an expected part of the work. After each build or play round, collect what it showed, ascend where it breaks a rule, and close the questions it answered.

## 4. Gate depth in both directions

Premature descent comes from **both sides of the conversation**. Watch both equally.

**Your own output.** Answer at the current layer. When a current-layer question seems to need concrete detail, name the layer the detail belongs to and choose a move: park it, or probe if the question depends on it.

**The user's input.** When the user offers specifics that belong to a lower layer, say so briefly and offer the moves:

> "That's an L3 idea and this system is at L1. Park it for later, or probe now to answer <question>?"

**Override.** The user can waive any gate for one step by saying so. Follow the override, note it in one line, and continue. When the same gate is overridden repeatedly, report that at the next checkpoint: the rule may need changing.

## 5. Quantities above L3

Above L3, strength, cost and size are stated as **orderings** ("A above B") or **tiers** (low, mid, high, or named tiers).

- When the user gives numbers early (ranking items 1 to 10), restate them as the ordering they imply, confirm it, and park the raw numbers for L3.
- Claude's own output carries numbers from L3 on.
- A probe may use trial numbers; they are recorded as placeholders.

## 6. Ideation order

1. When a layer or system opens, ask for the user's ideas first and record them before offering any.
2. Then offer Claude's proposals as **two or three options that differ in kind**, each with its trade-off, marked as proposals.
3. Give a single recommendation when the user asks for one.

## 7. Questions

- **One question asks for one decision**: it can be answered in a sentence or by choosing among named options.
- Split a larger question into its parts. Ask the framing part first, say how many parts follow, and ask each later part once the answer before it exists.
- Ask what the next step needs, in the order that unblocks the most. The other questions stay in the open-question list.
- At L0 and L1 ask open questions; from L2 on, offer named options where they exist.
- A question that only building or playing can answer is tagged `needs-build` and leaves the discussion until the next probe or build round.

## 8. Hand off recording

This skill owns **altitude**: which layer a thought belongs to and which move fits. Recording is handed off:
- **design-capture**: how decisions, ideas, probe findings and open questions become specs, decision history and parking-lot entries.
- **structured-project-docs**: where files live in the tree, naming, when to split.

In a quick chat without a docs tree, keep a short running list of parked ideas in the conversation.

## Calibration

The hard part is judgment: how deep is too deep before a layer is done? When unsure whether something is a premature descent or a useful aside, ask. Gate the meaningful drifts and let minor specifics pass; proportionate gating protects the flow of ideas.

## Self-check each turn

- [ ] I know and have stated the current layer for the system under discussion.
- [ ] My answer sits at that layer; anything deeper is parked or part of a named probe.
- [ ] Every out-of-layer idea from the user is parked, probed or descended to, by the user's choice.
- [ ] Each question I ask is sized to one decision.
- [ ] Quantities above L3 are orderings or tiers.
