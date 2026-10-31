---
name: "interrogate"
description: "Interview the user in focused rounds until a plan is fully decided or a message's core is pinned down. Use when the user asks to be interrogated, grilled, questioned or stress-tested (\"interrogate me\", \"grill me\", \"frag mich aus\", \"help me figure out what I want to say\")."
---

# Interrogate

Question the user, round by round, until nothing important is left unresolved or silently assumed. Two modes, same loop.

| Mode | Use when | Ends with |
|---|---|---|
| **Decide** | A plan, design or choice has open branches | Every branch decided |
| **Articulate** | The user roughly knows what they mean but not how to say it (email, argument, thesis claim, prompt) | A confirmed **core statement** |

Name the mode in the first round. If unclear, ask that first.

## When to run

- Run when the user asks for it.
- When a request is vague *and* expensive to get wrong, you may offer it in one line ("Want me to interrogate you on this first?"). Start only when the user says yes.

## The loop

1. **Map the tree.** Decide mode: decisions and the decisions that depend on them. Articulate mode: intent, audience, the one key point, what the reader should do or think afterwards, constraints (tone, length, channel).
2. **Ask the frontier.** The frontier is every question whose prerequisites are already answered. Ask **at most 4 per round**, picking the ones that unblock the most. A question that depends on another open question waits for a later round.
3. **Facts are your job, decisions are the user's.** Look up anything you can find yourself (files, docs, web, memory). Put only judgments and preferences to the user.
4. **Update and repeat.** Each answer reshapes the tree: settled questions open new ones, some become moot. Recompute the frontier and run the next round.
5. **Stop** when the frontier is empty. Act on the result once the user confirms the summary.

## Asking well

- **Format:** use the multiple-choice question UI when the answers can be enumerated; numbered text questions when they're open. Mix within a round if needed.
- **Decide mode:** give a recommended answer for each question, phrased so "yes" accepts it. Put the recommendation first among options.
- **Articulate mode:** give **no** recommended answer. A pick plants your framing, which defeats the purpose. Offer contrasting options, or reflect the user's own words back ("You said X twice: is that the point?").
- One concept per question, short and neutrally phrased.
- Push on vagueness: if an answer is "it depends" or abstract, ask for the concrete case or an example.

## Working with other skills

- **layered-design-facilitation:** inside a layered design session, ask only about the current layer. Deeper questions go to the parking lot, not the frontier.
- **design-capture:** in a project with a docs tree, the confirmed decisions are recorded through it.

## Before each round

- [ ] Every question is one only the user can answer.
- [ ] At most 4 questions, none depending on another in the same round.
- [ ] Articulate mode: options contrast without favoring my phrasing.

## Finish

Give a short summary for the user to confirm:

- **Decide mode:** decisions made (one line each), anything parked, open risks.
- **Articulate mode:** the **core statement** in one sentence, plus audience, intended effect, and constraints.

After confirmation, hand off (design-capture, or the actual writing/task).