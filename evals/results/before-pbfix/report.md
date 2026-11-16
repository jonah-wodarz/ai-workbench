# Eval report: before-pbfix

Ref `662e096` (662e096c880c), model trigger `-`, scenario `sonnet`.

## Scenarios

4 runs, isolation violations: 0, errors: 0.

| Skill | Scenario | Passed / total (all runs) |
|---|---|---|
| playbook | follow-existing | 12/16 |
| playbook | new-workflow | 15/16 |
| **playbook** | all | **27/32** |

### Failing assertions

- `playbook/follow-existing` **reads-first** (2/2 failed): The existing playbook was read before convert.py was first run.
  - run 1: index first=1 then=1
  - run 2: index first=1 then=1
- `playbook/follow-existing` **first-try-right** (2/2 failed): The first convert.py call already has OUT_DIR and the encoding flag.
  - run 1: first convert call: cd /home/claude/run/work/evals/tmp/run-3nhzg_ze/proj; ls -R . | grep -v '^./.claude/skills' | head -50; ls docs/playbooks docs/playbooks/runs 2>&1; head -5 data
  - run 2: first convert call: cd /home/claude/run/work/evals/tmp/run-kk08jmw3/proj; ls docs/playbooks docs/playbooks/runs 2>&1; ls; head -5 data/export.csv; sed -n 1,60p tools/convert.py
- `playbook/new-workflow` **generalized** (1/2 failed): The playbook uses placeholders instead of this run's file name.
  - run 2: pattern '<[a-z_-]+>' not found
