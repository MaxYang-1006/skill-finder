# Skill Finder

A Codex skill that proactively finds, ranks, and recommends high-quality skills for each task.

## What It Does

Skill Finder acts as a lightweight router for Codex skills. It helps Codex decide when a specialized skill would improve quality or speed, then recommends the smallest useful set of installed or installable skills.

It is designed to:

- Discover locally installed Codex skills
- Search OpenAI curated skill candidates
- Rank skills by task fit and quality
- Avoid weak or noisy recommendations
- Suggest installation only when a missing skill is likely worth it

## Files

- `SKILL.md`: Main Codex skill instructions and trigger description
- `scripts/find_skills.py`: Local and remote skill discovery helper
- `references/ranking.md`: Recommendation quality rubric
- `agents/openai.yaml`: Codex UI metadata
- `assets/skill-finder-icon.svg`: Custom skill icon

## Usage

Install this folder into your Codex skills directory:

```text
~/.codex/skills/skill-finder
```

Then restart Codex so the skill can be discovered.

You can also run the discovery helper directly:

```bash
python scripts/find_skills.py --query "github pr ci"
python scripts/find_skills.py --query "frontend testing playwright"
```

## Notes

Remote search uses the public OpenAI skills repository. Use `--with-remote-descriptions` for stronger evidence, or `--deep` for broader discovery when speed matters less.
