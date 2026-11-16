# Giveaways

## Length and detail parity

The most common tell: the key is longer, more qualified and more precise than terse distractors.

- Keep options within a few words of each other. If the key needs a qualifier, give comparable qualifiers to the distractors or make the key crisp.
- Match grammatical structure and specificity: a key that names a mechanism gets distractors that name other mechanisms, not hand-waves.

Bad (the detailed option is the key):
- A) It's fast.
- B) Isolation ensures that concurrently executing transactions produce a result equivalent to some serial execution, so intermediate states are never visible to others.
- C) It saves space.
- D) It uses SQL.

Good (every option is a specific, comparable claim; the item now tests the difference between the four ACID properties):
- A) Durability ensures committed changes survive a crash by persisting them to non-volatile storage.
- B) Isolation ensures concurrent transactions don't see each other's intermediate, uncommitted state.
- C) Atomicity ensures a transaction either fully completes or leaves no effect at all.
- D) Consistency ensures every transaction moves the database between valid states that satisfy all defined constraints.

## Enumeration count parity

When the answer is a set, the correct list often has N items and the distractors N-1. Give every option N items and build distractors by swapping in plausible wrong members of the same granularity and category. Keep the count out of the prompt unless the count is itself taught.

Bad (the three-item option stands out): A) Physical, Data Link, Network; B) Physical, Data Link; C) Physical.
Good (all three-item): A) Physical, Data Link, Network; B) Physical, Data Link, Session; C) Physical, Transport, Network; D) Data Link, Network, Transport.

## Plausible distractors

A distractor that is false for a reason unrelated to the tested concept is free elimination. For "normalization removes redundancy", "indexing removes redundancy" is a good distractor because people confuse the two.

## Sorting and matching

- **Elimination by exclusion**: with equal counts and one-to-one pairs the last pair is free. Add extra right-hand items, or let some right-hand items fit two left-hand items for different reasons.
- **Presentation order**: show items in an order unrelated to the key (not alphabetical, not by length, not already sorted). Start with no item pre-placed.
- **Bucket sizes**: in sorting into categories, uneven bucket sizes that mirror the key give it away; state no counts.
- **Partner echo**: paired texts share no rare word, and partner length does not correlate with position.
- **Ordering tasks**: avoid items that carry their own ordinals or connectives ("then", "finally").

## Secondary cues

- Answer position: spread the key over all slots; the widget shuffle is not a substitute.
- Hedge and absolute words: see the table in SKILL.md.
