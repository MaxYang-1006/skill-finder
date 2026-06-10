---
name: skill-finder
description: Proactively find, compare, recommend, and install Codex skills for a user task. Use when the user asks which skill to use, wants to discover available skills, asks to search curated or experimental skills, wants missing capabilities installed, wants a skills setup recommendation, or asks Codex to improve its skill toolkit for a workflow. Also use automatically at the start of complex, unfamiliar, multi-step, cross-tool, business-domain, design, data, document, deployment, GitHub, browser-testing, or workflow-automation tasks when a specialized skill may improve quality or speed.
---

# Skill Finder

## Overview

Discover available Codex skills, compare them with the user's goal, recommend a short ranked set, and install approved skills through the existing `skill-installer` workflow. Act as a lightweight skill router for complex work, not only as an answer to explicit skill-search questions.

Prefer a practical answer over a complete catalog. The best result is usually 3-7 recommendations with clear fit, source, installed status, and next action.

## Workflow

1. Decide whether routing is worth it. Use this skill proactively for complex, unfamiliar, multi-step, cross-tool, or business-domain tasks. Skip it for tiny direct answers, obvious single-command tasks, and requests already covered by an active named skill.
2. Clarify only when the task domain is ambiguous or installation would be risky. Otherwise infer the likely workflow from the user's request.
3. Inspect local skills and official candidates with `scripts/find_skills.py`.
4. Rank candidates using the rubric in `references/ranking.md`.
5. Recommend the smallest useful set:
   - Already-installed skills to use now
   - Missing curated or experimental skills worth installing
   - Gaps where a custom skill would be better than installing one
6. For already-installed skills, use them directly when the next step is obvious. Mention the routing briefly only when it helps the user understand why a skill is being used.
7. Ask before installing unless the user explicitly requested installation.
8. Install approved skills with `skill-installer` scripts, then tell the user to restart Codex to pick up new skills.

## Discovery

Run the bundled script from this skill directory:

```bash
python scripts/find_skills.py --query "<task keywords>"
```

Useful options:

```bash
python scripts/find_skills.py --query "frontend testing playwright" --include-experimental
python scripts/find_skills.py --query "frontend testing playwright" --with-remote-descriptions
python scripts/find_skills.py --query "unfamiliar domain" --deep
python scripts/find_skills.py --local-only
python scripts/find_skills.py --json
```

Default remote search is fast and name/alias based. Use `--with-remote-descriptions` when the initial results look plausible but need stronger evidence. Use `--deep` only for broad discovery, because it fetches many remote skill descriptions and can be slow.

If `python` is unavailable, use the bundled Codex Python runtime when present. If network access is blocked, request approval and rerun. If remote listing still fails, continue with local results and say the remote catalog could not be checked.

## Recommendation Style

For each recommendation, include:

- Skill name
- Status: installed, curated, experimental, or custom-needed
- Why it matches the user's task
- Whether to use now or install

Avoid recommending multiple overlapping skills unless they cover different phases. For example, recommend either `playwright` or `playwright-interactive` first unless the user needs both automation and interactive debugging.

## Installation

Use the system `skill-installer` skill for installs. Typical commands are:

```bash
python <skill-installer>/scripts/install-skill-from-github.py --repo openai/skills --path skills/.curated/<skill-name>
python <skill-installer>/scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>
```

When installing multiple skills from the same source, pass multiple `--path` values in one call.

After installation, always say: `Restart Codex to pick up new skills.`

## Custom Skill Guidance

Suggest a custom skill when:

- The user repeats a project-specific workflow
- No available skill fits the domain
- The task requires local conventions, private APIs, or company process
- The available skill is too broad and the user needs a narrow trigger

For custom skills, route through `skill-creator`.
