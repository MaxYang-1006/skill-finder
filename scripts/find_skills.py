#!/usr/bin/env python3
"""List local and OpenAI skills, optionally filtered by query terms."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


CURATED_API = "https://api.github.com/repos/openai/skills/contents/skills/.curated?ref=main"
EXPERIMENTAL_API = "https://api.github.com/repos/openai/skills/contents/skills/.experimental?ref=main"
RAW_BASE = "https://raw.githubusercontent.com/openai/skills/main"


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def read_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def read_frontmatter_text(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def local_skills() -> list[dict[str, str | bool]]:
    roots = [
        codex_home() / "skills",
        codex_home() / "skills" / ".system",
    ]
    found: dict[str, dict[str, str | bool]] = {}
    for root in roots:
        if not root.exists():
            continue
        for skill_md in root.glob("*/SKILL.md"):
            meta = read_frontmatter(skill_md)
            name = meta.get("name") or skill_md.parent.name
            found[name] = {
                "name": name,
                "source": "installed",
                "installed": True,
                "description": meta.get("description", ""),
                "path": str(skill_md.parent),
            }
    return sorted(found.values(), key=lambda item: str(item["name"]))


def fetch_github_dirs(api_url: str, source: str) -> list[dict[str, str | bool]]:
    req = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "codex-skill-finder",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    return [
        {
            "name": item["name"],
            "source": source,
            "installed": False,
            "description": "",
            "path": item.get("html_url", ""),
        }
        for item in data
        if item.get("type") == "dir"
    ]


def fetch_remote_description(name: str, source: str) -> str:
    folder = ".experimental" if source == "experimental" else ".curated"
    url = f"{RAW_BASE}/skills/{folder}/{name}/SKILL.md"
    req = urllib.request.Request(url, headers={"User-Agent": "codex-skill-finder"})
    with urllib.request.urlopen(req, timeout=12) as response:
        text = response.read().decode("utf-8")
    return read_frontmatter_text(text).get("description", "")


def match_score(item: dict[str, str | bool], terms: list[str]) -> int:
    haystack = f"{item.get('name', '')} {item.get('description', '')}".lower()
    tokens = [part for part in re.split(r"[-_\s`.,;:/()]+", haystack) if part]
    value = 0
    for term in terms:
        if len(term) < 3:
            if term in tokens:
                value += 3
        elif term in haystack:
            value += 3
        else:
            parts = [part for part in re.split(r"[-_\s]+", haystack) if len(part) >= 3]
            if any(part.startswith(term) or term.startswith(part) for part in parts):
                value += 1
    return value


DOMAIN_ALIASES = {
    "frontend": ["playwright", "screenshot"],
    "testing": ["playwright", "screenshot"],
    "ui": ["figma", "playwright", "screenshot"],
    "design": ["figma", "screenshot"],
    "github": ["gh-", "yeet"],
    "pr": ["gh-", "yeet"],
    "ci": ["gh-fix-ci"],
    "deploy": ["vercel", "netlify", "render", "cloudflare"],
    "security": ["security-"],
    "openai": ["openai-docs", "chatgpt-apps"],
    "docs": ["pdf", "notion", "openai-docs"],
    "document": ["pdf", "notion"],
    "data": ["jupyter", "pdf"],
}


def name_or_alias_score(item: dict[str, str | bool], terms: list[str]) -> int:
    name = str(item.get("name", "")).lower()
    name_parts = [part for part in name.split("-") if part]
    value = 0
    for term in terms:
        if len(term) < 3:
            if term in name_parts:
                value += 3
        elif term in name:
            value += 3
        for alias in DOMAIN_ALIASES.get(term, []):
            if alias in name:
                value += 2
    return value


def quality_adjustment(item: dict[str, str | bool], terms: list[str]) -> int:
    name = str(item.get("name", "")).lower()
    source = str(item.get("source", ""))
    description = str(item.get("description", ""))
    value = 0
    if item.get("installed"):
        value += 2
    elif source == "curated":
        value += 1
    elif source == "experimental":
        value -= 1
    if description:
        value += 1
    if any(term == name or term in name.split("-") for term in terms):
        value += 3
    for term in terms:
        for alias in DOMAIN_ALIASES.get(term, []):
            if alias in name:
                value += 2
    return value


def rank_score(item: dict[str, str | bool], terms: list[str]) -> int:
    return match_score(item, terms) + quality_adjustment(item, terms)


def is_meta_skill_noise(item: dict[str, str | bool], terms: list[str]) -> bool:
    name = str(item.get("name", "")).lower()
    if name not in {"skill-finder", "skill-installer", "skill-creator"}:
        return False
    return not any(term in {"skill", "skills", "install", "installer", "finder"} for term in terms)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Task keywords used to filter and rank skills.")
    parser.add_argument("--include-experimental", action="store_true", help="Include OpenAI experimental skills.")
    parser.add_argument("--local-only", action="store_true", help="Only inspect locally installed skills.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum results to print. Use 0 for all.")
    parser.add_argument("--deep", action="store_true", help="Fetch descriptions for all remote skills before filtering. Slower but broader.")
    parser.add_argument("--with-remote-descriptions", action="store_true", help="Fetch descriptions for name or alias matched remote candidates.")
    parser.add_argument("--no-remote-descriptions", action="store_true", help="Skip fetching remote SKILL.md descriptions.")
    args = parser.parse_args()
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.query)]

    installed = local_skills()
    installed_names = {str(item["name"]) for item in installed}
    results = list(installed)
    warnings: list[str] = []

    if not args.local_only:
        for api_url, source in [(CURATED_API, "curated")] + (
            [(EXPERIMENTAL_API, "experimental")] if args.include_experimental else []
        ):
            try:
                for item in fetch_github_dirs(api_url, source):
                    if str(item["name"]) in installed_names:
                        continue
                    should_fetch_description = (
                        not args.no_remote_descriptions
                        and (args.deep or args.with_remote_descriptions)
                        and (args.deep or not terms or name_or_alias_score(item, terms) > 0)
                    )
                    if should_fetch_description:
                        try:
                            item["description"] = fetch_remote_description(str(item["name"]), source)
                        except (urllib.error.URLError, TimeoutError, UnicodeDecodeError):
                            item["description"] = ""
                    results.append(item)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                warnings.append(f"Could not fetch {source} skills: {exc}")

    if terms:
        ranked = [(max(match_score(item, terms), name_or_alias_score(item, terms)), item) for item in results]
        results = [item for item_score, item in ranked if item_score > 0]
        results = [item for item in results if not is_meta_skill_noise(item, terms)]
        results.sort(key=lambda item: (-rank_score(item, terms), str(item["source"]), str(item["name"])))
    else:
        results.sort(key=lambda item: (str(item["source"]), str(item["name"])))

    if args.limit > 0:
        results = results[: args.limit]

    payload = {"query": args.query, "warnings": warnings, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if warnings:
            for warning in warnings:
                print(f"Warning: {warning}", file=sys.stderr)
        heading = f"Skills matching {args.query!r}" if args.query else "Available skills"
        print(heading)
        for item in results:
            status = "installed" if item.get("installed") else str(item["source"])
            description = f" - {item['description']}" if item.get("description") else ""
            print(f"- {item['name']} [{status}]{description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
