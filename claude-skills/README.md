# Claude Skills — Agentic finance tools for buy-side workflows

Custom **Claude Agent Skills** that package buy-side finance competences so an
agent can discover and apply them reliably. Each skill is a self-contained
folder (`SKILL.md` + scripts, references and tests) covering a task an analyst
runs repeatedly: company valuation, ratio screening, interview prep.

A skill exposes only its `name` and `description` to the agent up front, and
loads the full procedure and resources on demand — so the agent picks the right
skill from the description and pulls in detail only when needed.

> Internal code comments are in Italian (study notes); READMEs and `SKILL.md`
> files are in English.

---

## Skills

| Skill | What it does | Key concepts | Status |
|-------|--------------|--------------|--------|
| [`dcf-analyzer`](dcf-analyzer/) | DCF valuation of a company: EV → equity → fair value per share, with a WACC × g sensitivity grid | JSON contract, deterministic engine, FCFF/WACC, Gordon terminal value | ✅ complete |
| [`ratio-analysis`](ratio-analysis/) | Compute liquidity, leverage, profitability and efficiency ratios of a company from its financial statements | relative/accounting analysis vs intrinsic DCF, per-ratio null on missing/zero | ✅ complete |
| [`interview-answer-formatter`](interview-answer-formatter/) | Structure a technical buy-side answer: definition → intuition → formula → use case → pitfalls | pure prompt design, no engine (SKILL.md only) | ✅ complete |

---

## Skill structure

```
<skill-name>/
├── SKILL.md        # frontmatter (name, description, license, allowed-tools) + procedure + contract
├── scripts/        # executable, unit-tested code (the deterministic core)
├── references/     # detailed formulas / edge cases, loaded only when needed
└── tests/          # input examples + pytest suite
```

## Code-backed vs prompt-only skills

`dcf-analyzer` and `ratio-analysis` are **code-backed**: the procedure writes
an `input.json` following a documented contract, runs a Python engine via Bash
(`python scripts/<engine>.py input.json`), parses the JSON stdout and formats
the result. This keeps the math in deterministic, testable Python and lets the
agent focus on input validation and explanation.

`interview-answer-formatter` is **prompt-only** (no scripts, no engine). Its
competence lives entirely in the template, the style guide and the worked
example inside `SKILL.md`. It runs no calculations on purpose — those are the
other two skills' job.

## How to run a skill's engine

Each skill's numeric work lives in a tested script. For `dcf-analyzer`:

```bash
cd dcf-analyzer
python scripts/dcf.py tests/example_wacc.json   # prints the valuation as JSON
pytest                                           # runs the test suite
```

See each skill's own `README.md` for its input/output contract and examples.

---

## Design principles

- **Description-driven triggering** — the `description` states what the skill
  does and *when* to use it, with concrete triggers, so the agent fires it on
  the right requests and not on the wrong ones.
- **Least privilege** — `allowed-tools` lists only what the skill needs
  (e.g. `Read, Write, Bash`).
- **Deterministic core** — numbers come from a tested script, not from the
  model's reasoning, so results are reproducible and verifiable.
- **Progressive disclosure** — heavy detail goes into `references/`, keeping
  `SKILL.md` lean.

---

## Dependencies

- **Python 3.10+** for the skill engines (standard library only; `pytest` for
  the test suites)
- **Claude Code** (or any Agent-Skills-compatible runner) to load the skills

---

## Notes on hooks and MCP servers

This folder contains **skills only**, not hooks or MCP servers. A separate
[`Cheatsheet_Skills_Hooks_MCP.html`](../Cheatsheet_Skills_Hooks_MCP.html) in the
parent folder documents the three mechanisms side-by-side. For my buy-side use
case skills cover the relevant ground; hooks and MCP servers were studied but
intentionally not implemented in this repo.

---

## Related Projects

- [Markowitz MVO](../python/markowitz) — Mean-Variance portfolio optimization (Python)
- [VaR & ES](../python/var-cvar) — risk estimation on the Tangency Portfolio (Python)
- [Factor Models](../python/factor-models) — CAPM & Fama-French regression (Python)
- [SQL Module](../sql) — synthetic SQLite finance DB + buy-side analytics queries
- [VBA Toolkit](../vba) — Excel macros and UDFs for analytics
