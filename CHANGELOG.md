# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-12

### Added
- Initial release of the **code-review** Agent Skill.
- `skill.md`: full methodology — When to Activate, Step 1 Scope & Context,
  Step 2 Severity model, Step 3 prioritized review passes (correctness,
  security via OWASP/CWE, performance via Big-O, API/design, tests,
  maintainability), Step 4 red-flag quick scan, Step 5 output format.
- `examples/python-api-review.md`: a FastAPI endpoint review (SQL injection,
  missing authorization / IDOR, N+1 query).
- `examples/react-component-review.md`: a React component review
  (`dangerouslySetInnerHTML` XSS, `useEffect` dependency bug, missing error
  state).
- `README.md`, `LICENSE` (MIT), `.gitignore`.
- CI: `scripts/validate_skill.py` validator and a GitHub Actions workflow that
  runs it on push and pull request.

[1.0.0]: https://github.com/Viprasol-Tech/code-review-skill/releases/tag/v1.0.0
