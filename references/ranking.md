# Skill Ranking Rubric

Rank candidates by these signals:

1. Direct fit: the skill description names the user's task or tool.
2. Workflow leverage: the skill removes repeated discovery, setup, validation, or deployment work.
3. Existing availability: installed skills usually rank above missing skills.
4. Source confidence: curated skills rank above experimental skills unless the experimental skill is clearly the only fit.
5. Scope control: narrow skills rank above broad skills for concrete tasks; broad router skills rank above narrow skills for vague exploratory requests.
6. Verification support: skills with scripts, render checks, browser checks, or external tool workflows rank higher for production work.
7. Evidence quality: prefer skills with clear frontmatter descriptions, maintained official sources, and concrete workflows over vague names or thin wrappers.
8. Task cost: recommend installing a missing skill only when it is likely to save more time or reduce more risk than using existing tools.

Filter out low-quality recommendations:

- Do not recommend a skill solely because one word weakly overlaps the query.
- Do not recommend experimental skills unless they are the only clear fit or the user explicitly asks for experimental options.
- Do not recommend broad skills when a narrow installed skill covers the task.
- Do not recommend install candidates with missing descriptions unless the name exactly matches the requested tool or domain.
- Do not show long catalogs by default. Return the best few choices and say when no strong candidate exists.

Common pairings:

- GitHub PR work: `gh-address-comments`, `gh-fix-ci`, `yeet`
- Frontend implementation and QA: `playwright`, `playwright-interactive`, `screenshot`, browser/plugin skills if installed
- OpenAI product questions: `openai-docs`
- Figma design work: `figma`, `figma-use`, `figma-implement-design`, `figma-generate-design`
- Deployment: `vercel-deploy`, `netlify-deploy`, `render-deploy`, `cloudflare-deploy`
- Documents and research capture: `pdf`, Notion skills, document/plugin skills if installed

Prefer saying "no obvious install needed" when the user's current installed skills already cover the job.
