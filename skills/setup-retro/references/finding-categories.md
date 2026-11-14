# Finding categories

| Category | Signal | Cheapest fix |
|---|---|---|
| Mechanical rule in prose | User corrected a pattern a script could catch | Deterministic check (doc-kit lint, script) |
| Trigger | Skill fired when it should not, or stayed silent when it should | Rewrite the description's trigger phrases; check `disable-model-invocation` |
| Overlap | Two skills claim a request or give conflicting rules | Assign one owner, point the other to it; merge only if bodies converge |
| Steering bloat | Long always-loaded preferences or descriptions | Move detail into a skill body or a doc behind a pointer |
| No-op | Instruction the model follows by default | Delete the sentence |
| Negation-only rule | Rule phrased only as "don't X" | State the positive target |
| Stale | References to removed skills, files, tools or product features | Update or delete; verify product facts by search |
| Information access | A needed file, folder, connector or tool was missing | Suggest the connection or folder |
| Tool economy | Repeated expensive calls for bulk data | A script that processes data outside the context |
| Gap | Same request repeated, no skill covers it | New skill (a preference line if one sentence suffices) |
| Ripe playbook | `current`, 3+ runs, steps unchanged in the last runs | Promote to a skill |
| Stale playbook | No run in about 6 months, or its tools changed | Re-verify on next use, or deprecate |
