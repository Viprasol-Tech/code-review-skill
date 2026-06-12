# Code Review Skill

> Rigorous, prioritized code review for AI coding agents — correctness bugs first, then security (OWASP/CWE), performance, API design, tests, and maintainability. Severity-rated findings with concrete fixes, not nitpicks.

[![GitHub stars](https://img.shields.io/github/stars/Viprasol-Tech/code-review-skill?style=social)](https://github.com/Viprasol-Tech/code-review-skill/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](https://github.com/Viprasol-Tech/code-review-skill)
[![OWASP + CWE](https://img.shields.io/badge/OWASP%20%2B%20CWE-aware-green)](https://owasp.org/Top10/)
[![Version](https://img.shields.io/badge/version-1.0.0-informational)](CHANGELOG.md)

**Works with:** Claude Code · Codex · Cursor · Copilot · Gemini CLI · and 26+ agent tools that support portable Agent Skills.

---

## Quick Install

This is a portable **Agent Skill** — plain Markdown methodology, no dependencies.
Clone it where your agent looks for skills. The skill name is **`code-review`**.

```bash
# Claude Code (user-level skills)
git clone https://github.com/Viprasol-Tech/code-review-skill.git \
  ~/.claude/skills/code-review

# project-level (committed with your repo)
git clone https://github.com/Viprasol-Tech/code-review-skill.git \
  .claude/skills/code-review
```

For other tools (Cursor, Codex, Copilot, Gemini CLI, …), drop `skill.md` into the
folder that tool reads skills/rules from. The whole skill is a single Markdown
file — portable by design.

## Try It

````text
Review this PR — focus on correctness and security
````

…then paste a diff, a file, or a link. Or just:

````text
Audit this change before I merge it.
````

---

## Why This Exists

Ask a generic agent to "review my code" and you usually get a wall of shallow
nitpicks — rename this, add a comment there — while the actual SQL injection, the
missing auth check, and the N+1 query sail straight through.

A good human reviewer does the opposite: they find the issue that *matters*, rank
it honestly, and tell you exactly how to fix it. This skill encodes that
discipline — **correctness first, security by a recognized taxonomy, performance
by complexity, and a hard rule against blocking on style.**

## What It Does

Given a diff, a pull request, or a file, the skill:

1. **Scopes the change** — language, framework, runtime/security surface, tests.
2. **Runs prioritized passes** — correctness → security → performance → API/design
   → tests → maintainability, in that order.
3. **Rates every finding** by severity and **proposes a concrete fix** (with a
   code snippet where it helps).
4. **Outputs a verdict** (Approve / Approve-with-comments / Request-changes), a
   findings table, per-finding detail, and an honest "what's good" section.

## Features

- **Priority-ordered passes** — the highest-impact defects (logic, security)
  are reviewed first, so the most important comments come first.
- **OWASP + CWE security pass** — injection, broken access control, secrets,
  unsafe deserialization, SSRF, path traversal, XSS, weak crypto — each tagged
  to a recognized weakness class.
- **Big-O performance pass** — N+1 queries, accidental O(n²), unbounded growth,
  blocking I/O on hot paths — justified by complexity, not folklore.
- **Red-flag quick scan** — instant blockers (hardcoded secret, `eval` on input,
  SQL concat, disabled TLS verify, swallowed errors, committed `.env`).
- **Honest severity model** — nits are labeled and never block a merge.

### Severity model

| Severity     | Meaning                                                      | Blocks merge? |
|--------------|--------------------------------------------------------------|---------------|
| **Critical** | Data loss, security hole, crash, corruption in normal use.   | Yes           |
| **High**     | Wrong behavior / incorrect results for realistic inputs.     | Yes           |
| **Medium**   | Performance or design risk under load or over time.          | Usually       |
| **Low**      | Maintainability: clarity, duplication, naming, docs.         | No            |
| **Nit**      | Pure style a formatter/linter could settle.                  | No            |

---

## Examples

See [`examples/`](examples/) for full, realistic sample reviews:

- [`examples/python-api-review.md`](examples/python-api-review.md) — a FastAPI
  endpoint diff with SQL injection, a missing auth check, and an N+1 query.
- [`examples/react-component-review.md`](examples/react-component-review.md) — a
  React component with a `useEffect` dependency bug, XSS via
  `dangerouslySetInnerHTML`, and a missing error state.

---

**Pairs well with:**
[agentcheck](https://github.com/Viprasol-Tech/agentcheck) (regression-test your
agents in CI) and
[promptproof](https://github.com/Viprasol-Tech/promptproof) (red-team your
prompt-injection guards). Review the code, test the agent, harden the prompts.

---

## Contact — Viprasol Tech Private Limited
- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

> *Viprasol Tech — fintech software, AI agents, algorithmic trading systems, and B2B SaaS.*

## License
[MIT](LICENSE) © 2025 Viprasol Tech Private Limited
