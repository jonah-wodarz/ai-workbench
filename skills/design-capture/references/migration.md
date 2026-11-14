# Migrating an existing doc set

Bring older docs under conventions one file or small domain at a time.

1. Read the file. Search the tree for its key terms to find every file that restates its facts. List the contradictions; settle those a newer ruling covers and take the rest to the user.
2. Write the new spec from the template: current state only, with IDs and tags.
3. Create the mirrored decision history. Backfill only pivotal decisions that still explain a current rule or keep a rejected idea from returning, and mark them `backfilled`.
4. Delete changelogs, struck text, resolved-question lists, reviews and debate from the old version.
5. Fix every file that restated the migrated facts: link by ID or delete.
6. Where a rule cites another system's rule ID, add an interface item to that system's spec and cite the item.
7. Run the lint until clean. The user reviews and commits. From that commit on, IDs are permanent.
