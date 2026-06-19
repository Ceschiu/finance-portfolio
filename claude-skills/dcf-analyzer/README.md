# dcf-analyzer

A Claude Agent **Skill** that builds a Discounted Cash Flow (DCF) valuation of a
company — with input validation (e.g. `g < WACC`, sign checks) and a WACC × g
sensitivity grid.

It triggers when the user provides free cash flows and a WACC, or asks for a
company's intrinsic value / fair value per share. It is intentionally **not**
used for financial institutions, which require an equity-side method
(FCFE / DDM) — see [`references/dcf_methodology.md`](references/dcf_methodology.md).

## How it works

The skill is a thin orchestration layer over a deterministic Python engine:

1. The agent collects the inputs (from the message or a CSV) and writes them to
   an `input.json` following the [Contract](SKILL.md#contract).
2. It runs the engine via Bash: `python scripts/dcf.py input.json`.
3. The engine prints a JSON object to stdout; the agent formats it into a table
   plus a short comment.

Keeping the numbers in a tested script (not in the model's head) makes the
valuation **deterministic and reproducible**.

## Layout

```
dcf-analyzer/
├── SKILL.md                      # frontmatter + procedure + JSON contract
├── scripts/dcf.py                # DCF engine (validation, WACC, core, sensitivity)
├── references/dcf_methodology.md # formulas and method limits (progressive disclosure)
└── tests/                        # JSON examples + pytest suite
```

## Example

Input (`tests/example_wacc.json`):

```json
{"FCFF": [100, 110, 120, 125, 130], "WACC": 0.09, "g": 0.02,
 "NetDebt": 250, "NShares": 50}
```

Run:

```bash
python scripts/dcf.py tests/example_wacc.json
```

Output (truncated):

```json
{"ok": true, "enterprise_value": 1681.19, "equity_value": 1431.19,
 "fair_value_per_share": 28.6238, "sensitivity": [ ... 3x3 grid ... ]}
```

## Tests

```bash
pytest
```

Five tests cover the core valuation, WACC reconstruction from components, input
validation, the end-to-end `g ≥ WACC` rejection, and the sensitivity grid.
