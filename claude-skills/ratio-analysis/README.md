# ratio-analysis

A Claude Agent **Skill** that computes the core financial ratios of a company
from its financial statements: liquidity, leverage, profitability and efficiency.

It triggers when the user asks for a company's ratios and provides
balance-sheet / income-statement items. It is intentionally **not** used for
intrinsic / DCF valuation — that is the job of
[`dcf-analyzer`](../dcf-analyzer/). The two skills are separated at the
description level so the agent picks the right one.

## Ratios

| Family | Ratios |
|--------|--------|
| Liquidity | current ratio, quick ratio |
| Leverage | debt-to-equity, interest coverage |
| Profitability | ROE, ROA, net margin |
| Efficiency | asset turnover |

Formulas and conventions are in
[`references/ratio_methodology.md`](references/ratio_methodology.md).

## How it works

1. The agent collects the figures (from the message or a CSV) and writes them to
   an `input.json` following the [Contract](SKILL.md#contract).
2. It runs the engine via Bash: `python scripts/ratio.py input.json`.
3. The engine prints a JSON object to stdout; the agent formats it into a table
   plus a short comment.

A ratio whose numerator or denominator is missing (`null`), or whose denominator
is `0`, is returned as `null` — the other ratios are still computed, so one
missing figure never breaks the whole analysis.

## Layout

```
ratio-analysis/
├── SKILL.md                        # frontmatter + procedure + JSON contract
├── scripts/ratio.py                # ratio engine (validation, safe_div, core)
├── references/ratio_methodology.md # formulas and conventions
└── tests/                          # JSON examples + pytest suite
```

## Example

Input (`tests/example_full.json`):

```json
{"Revenue": 1000, "NetIncome": 120, "EBIT": 200, "InterestExpense": 40,
 "TotalAssets": 1500, "CurrentAssets": 600, "Inventory": 150,
 "CurrentLiabilities": 300, "TotalDebt": 500, "TotalEquity": 800}
```

Run:

```bash
python scripts/ratio.py tests/example_full.json
```

Output:

```json
{"ok": true, "current_ratio": 2.0, "quick_ratio": 1.5, "debt_to_equity": 0.62,
 "interest_coverage": 5.0, "ROE": 0.15, "ROA": 0.08, "net_margin": 0.12,
 "asset_turnover": 0.67}
```

## Tests

```bash
pytest
```

Four tests cover the full computation, the missing-value / zero-denominator
behaviour (ratios returned as `null`), `safe_div`, and sign validation.
