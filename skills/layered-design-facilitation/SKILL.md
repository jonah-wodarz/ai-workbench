---
name: "layered-design-facilitation"
description: "Facilitate open-ended design, brainstorming, and ideation by decomposing the problem into layers of abstraction and working top-down, one layer at a time. Use whenever the user is designing or thinking through something open-ended and exploratory — game design, system architecture, product concepts, research directions — especially early on before details are settled, and especially in Claude Cowork. Proactively propose a layered framework sized to the problem, keep work anchored at the current layer, and actively stop premature descent into concrete detail — whether it comes from Claude's own output OR from the user jumping ahead — even if the user doesn't ask for structure. Trigger at the start of any exploratory design session, and whenever the discussion starts drifting into implementation specifics before the higher layers are resolved."
---

# Layered Design Facilitation

Open-ended design fails in a predictable way: the thinking drifts *downward* through levels of abstraction one small step at a time. Each step feels like progress — more detail — but the drift means concrete decisions get made before the structure that should govern them exists. The result is feature creep and a pile of specifics with no frame around them.

Run exploratory design **top-down**: establish the layers first, resolve each layer before descending, and make every descent a deliberate, announced move. Apply this proactively whenever the user is designing something open-ended.

## 0. Project conventions win

If the project defines its own conventions (e.g. `docs/CONVENTIONS.md`), they override this skill wherever the two differ. Read them at the start of a session.

## 1. Decompose early, sized to the problem

Early in an exploratory session, before deep work, propose a **layered model** of the problem — a stack from most abstract to most concrete — fitted to the problem's actual scale. Sketch it, name the layers, and confirm the shape fits before proceeding.

The default stack is shared with the **design-capture** skill, so conversation and documentation use the same vocabulary:

| Layer | Question it answers | Game example |
|---|---|---|
| **L0 Vision** | What experience / outcome, which pillars? | The feeling the game should create |
| **L1 Intent** | Which systems or domains produce it, and what is each one for? | Combat, progression, economy — and their purpose |
| **L2 Mechanics** | How does each system work — rules and interactions? | How a weapon upgrade works |
| **L3 Parameters** | Which numbers, formulas, thresholds? | Damage values, drop rates |
| **L4 Implementation** | How is it built? | Code, data files, config |

Adapt the count and names to the domain and its size — a small problem may collapse to three layers, a large one may split a layer. Keep the L-numbering so capture and facilitation stay aligned. Propose the stack as scaffolding and refine it as the domain's shape emerges; once a working stack exists, use it.

## 2. Anchor the current layer

At any moment, know and state **which layer you are working at** — per system, since different systems can sit at different layers. Resolve a layer's important open questions before moving down. When the layer is "done enough" to descend, say so explicitly and confirm — descent is a decision, not a slide.

## 3. Gate depth — in both directions (the core)

Premature descent comes from **both sides of the conversation**. Watch both equally; a gate that only checks one side fails.

**Your own output.** Answer at the current layer. If a current-layer question seems to need concrete detail to answer — someone asks about balance while you're still defining systems — that is the signal the detail belongs *below*. Name the layer it belongs to and defer it.

**The user's input.** When the user offers concrete implementations, parameters, or specifics that belong to a lower layer than the current one, **stop them** — briefly and directly:

> "That's an L3 parameter idea and we're still at L1 for this system. Want me to park it for when we get there, or drop to that layer on purpose now?"

This protects the current layer's thinking from premature commitment and keeps the user from unwittingly descending. Be firm and brief, and offer the choice.

**Descent is always deliberate and announced** — by either party.

## 4. Park every out-of-layer idea

File it in the **parking lot** (format and location defined by **design-capture**: one line, filed under its system and target layer), then return to the current layer. The user should feel the idea was *captured* — only *when* it gets worked on is deferred. Captured ideas keep the user volunteering them, which is what feeds the ideation loop. Ideas the user rules out entirely go to design-capture's *Out of scope* list instead.

## 5. Hand off recording

This skill owns **altitude**: which layer a thought belongs to and whether it's time to work on it. Recording is handed off:
- **design-capture** — how decisions, ideas and open questions become specs, decision history and parking-lot entries.
- **structured-project-docs** — where files live in the tree, naming, when to split.

If the project has no docs tree (a quick chat), keep a short running list of parked ideas in the conversation instead.

## Calibration

The hard part is judgment: *how deep is too deep before a layer is done?* When you're unsure whether something is a genuine premature descent or a useful aside, ask. Gate the meaningful drifts and let minor specifics pass — proportionate gating protects the ideation flow. Proportionality is part of the skill.

## Self-check each turn

- [ ] I know and have stated the current layer for the system under discussion.
- [ ] My answer sits at that layer; anything deeper is named and parked.
- [ ] Every out-of-layer idea from the user is parked or deliberately descended to, with the user's choice.