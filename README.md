# SKILL.md Validator

A free, no-install, browser-only validator and safety checker for Agent Skills `SKILL.md` files.
Main keyword: **skill.md validator**. Everything runs client-side — the file being checked never leaves the visitor's browser.

Files in this folder (zero dependencies, zero build step):

| File | Purpose |
|---|---|
| `index.html` | The page: tool + explanatory content + compatibility table + FAQ |
| `style.css` | Styling (dark theme, mobile-friendly) |
| `app.js` | The validator (frontmatter parser, spec checks, token estimate, security scan) and UI wiring |
| `robots.txt` | Crawler rules + sitemap pointer |
| `sitemap.xml` | Sitemap (single URL for the MVP) |

> ✅ **Domain set:** `index.html` (canonical + og:url), `robots.txt` and `sitemap.xml` now use `https://skillmdvalidator.com/`. Placeholder replacement was done on 2026-10-24; the remaining DNS/HTTPS steps are in the checklist below.

## Deploy to GitHub Pages

1. Create a **new GitHub repository** (e.g. `skillmd-validator`).
2. Push the contents of this folder to the repository root:
   ```bash
   cd skillmd-validator
   git init && git add -A && git commit -m "SKILL.md Validator MVP"
   git branch -M main
   git remote add origin https://github.com/<your-user>/skillmd-validator.git
   git push -u origin main
   ```
   (Or upload the files via the GitHub web UI.)
3. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
4. Wait ~1 minute; the site is live at `https://<your-user>.github.io/skillmd-validator/`.
5. Optional: add a custom domain under Settings → Pages, then update the placeholder URLs (next section).

No build command, no framework, no environment variables are needed — it is plain static files, same as the gefei-quest station-one playbook flow.

## Post-launch checklist (owner TODO)

- [ ] **Real domain:** `skillmdvalidator.com` — decided 2026-10-24, files already point at it (canonical/og/sitemap/robots). Still to do: register it on Porkbun, point DNS at GitHub Pages, wait for HTTPS.
- [ ] **Analytics:** add Google Analytics 4 **or** Microsoft Clarity snippet to `index.html` (the station-one playbook uses one of the two) and confirm hits are recorded.
- [ ] **Google Search Console:** verify the property (DNS or HTML-tag method), then submit `sitemap.xml`.
- [ ] **Indexing:** use GSC URL Inspection on the homepage and request indexing (playbook Day 6 step).
- [ ] **Station log:** register the site in the gefei-quest site ledger (`#me-sites`) and check `site:<domain>` after a few days (playbook Day 7).
- [ ] Re-check the rules against <https://agentskills.io/specification> after spec updates — the spec page is a living document.

## Validation rules and their sources

Checked 2026-10-23 against the official specification: **<https://agentskills.io/specification>**.

### Enforced as ERRORS — direct official spec rules

| Rule | Spec source |
|---|---|
| SKILL.md must contain YAML frontmatter | Spec, “SKILL.md format” (“must contain YAML frontmatter followed by Markdown content”) |
| `name` is required, 1–64 characters | Spec, name field list |
| `name`: lowercase letters, numbers, hyphens only | Spec, name field list (“unicode lowercase alphanumeric characters (a-z, 0-9) and hyphens”). This tool checks the ASCII set `a-z0-9-` |
| `name` must not start or end with a hyphen | Spec, name field list |
| `name` must not contain consecutive hyphens (`--`) | Spec, name field list |
| `name` must match the parent directory name | Spec, name field list (“Must match the parent directory name”) — checked when the visitor enters a folder name |
| `description` is required, non-empty, 1–1,024 characters | Spec, frontmatter table + description field list |
| `compatibility`, if provided, must be 1–500 characters | Spec, frontmatter table + compatibility field list (“Must be 1-500 characters if provided”) |

### Checked as WARNINGS — spec-adjacent format checks

| Rule | Basis |
|---|---|
| `license` empty | Spec defines the field’s purpose; an empty value carries no information |
| `metadata` is not a key–value map | Spec: “A map from string keys to string values”. This parser only checks the shape roughly (indented `key: value` lines) |

### SUGGESTIONS — best practice, NOT official spec rules

| Suggestion | Basis |
|---|---|
| Description should say when to use the skill (“Use when…”) | The spec says a description **should** describe what + when and include keywords — advisory wording in the spec, not a hard rule |
| Remove `<` / `>` from the description | **Not in the agentskills.io spec.** Comes from other validators (e.g. OpenAI's skill validator rejects angle brackets in frontmatter). Labelled as a suggestion in the report for exactly this reason |
| Keep SKILL.md under 500 lines | The spec **recommends** this (“Keep your main SKILL.md under 500 lines”) — a recommendation, not a validity rule |
| `allowed-tools` should be space-separated, not comma-separated | Spec defines it as a “space-separated string” (experimental field) |
| Unknown frontmatter fields | Informational only: the base spec defines six fields; individual agents add their own and ignore unrecognised ones |

### Security scan — heuristics, NOT spec rules at all

These are the tool’s own safety heuristics (warning level), with no spec basis claimed:

- `curl … | bash` / `wget … | sh` style piped remote execution
- `rm -rf` style recursive force-delete
- `sudo` commands
- Invisible Unicode characters (U+200B–U+200D, U+FEFF mid-file, U+202A–U+202E directional overrides, U+2066–U+2069 isolates, U+2060, U+00AD)
- Over-broad `allowed-tools`: any wildcard `*`, especially `Bash(*)`

### Token cost estimate — rough by design

Standing cost = characters of `name` + `description` ÷ 4 (≈4 characters/token for English text), rounded up. The spec’s progressive-disclosure section puts typical metadata at ~100 tokens loaded at startup; the estimate exists to flag outliers, not to count tokens exactly.

### Cross-platform folder table (homepage)

Paths cross-checked 2026-10-23 against multiple public sources (Augment’s skills docs location list; open-source multi-agent skill installers’ per-vendor path tables; vendor comparison write-ups) which agree on: Claude Code `~/.claude/skills/` + `.claude/skills/`; Codex `~/.agents/skills/` + `.agents/skills/`; Cursor `~/.cursor/skills/` + `.cursor/skills/` (also reads `.agents/skills/`); Gemini CLI `~/.gemini/skills/` (also `.agents/skills/`); GitHub Copilot `~/.copilot/skills/` / `.github/skills/`. The page itself carries a “paths can change between versions — check your agent’s docs” caveat. No path was written from a single unverified source.

## Known limitations of the MVP

- The frontmatter parser is a small hand-written parser for the spec’s flat fields (plain/quoted/block scalars, one level of nesting). It is **not** a full YAML parser — exotic YAML (anchors, multi-document files, complex nested structures under `metadata`) can be misread. Fields are matched case-sensitively, as in the spec examples.
- Only the pasted `SKILL.md` text is checked. Referenced files (`scripts/`, `references/`, `assets/`), the folder’s other contents, and per-agent extension fields are out of scope.
- Security scanning is pattern-based on visible text; it cannot prove a skill is safe (the FAQ on the page says this explicitly).

## Self-test

The validator core in `app.js` exports `validateSkill` for Node. The MVP was verified with Node assertions covering: the built-in valid example passes with 0 errors; the built-in flawed example produces the name error plus both security warnings; missing frontmatter, over-long name (>64), over-long description (>1024), over-long compatibility (>500), folder/name mismatch, `rm -rf`, `sudo`, and invisible-Unicode inputs are each flagged; the token estimate equals ⌈(name+description chars)/4⌉.
