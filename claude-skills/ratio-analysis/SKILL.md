---
name: ratio-analysis
description: Compute liquidity, leverage, profitability and efficiency ratios of a company from balance-sheet / income-statement items. Trigger if user asks for financial ratios. Not for DCF — see dcf-analyzer.
license: MIT
allowed-tools: Read, Write, Bash
---

# ratio-analysis

## Quando usare questa skill

Compute liquidity, leverage, profitability and efficiency ratios of a company
from its financial statements (current, quick, D/E, ROE, ROA...). Use when the
user asks for a company's financial ratios and provides balance-sheet /
income-statement items. Do not use for intrinsic/DCF valuation — see
dcf-analyzer.

## Input

1. Revenue (float | null)
2. NetIncome (float | null)
3. EBIT (float | null)
4. InterestExpense (float | null)
5. TotalAssets (float | null)
6. CurrentAssets (float | null)
7. Inventory (float | null)
8. CurrentLiabilities (float | null)
9. TotalDebt (float | null)
10. TotalEquity (float | null)

The user may provide the data in the message or a CSV; the skill assembles them
into input.json following the Contract.

## Procedura

1. Validate the input values, considering their metric, values and sign
   (e.g. no negative revenues).
2. If all the inputs are correct, convert the ones that need it
   (e.g. scientific notation, 1e3 -> 1000).
3. Write the inputs to a temp JSON, run `scripts/ratio.py <path>` via Bash,
   parse the JSON from stdout.

## Output

Return a table with the following financial ratios: current, quick, D/E,
interest coverage, ROE, ROA, net margin, asset turnover. Followed by a brief
comment of the results.

## Casi limite

- If any denominator is equal to 0, the related ratio is returned as null and a
  warning is added; the other ratios are still computed.
- If there are missing values, ask the user whether they are missing and what
  values to use instead.
- Any other error during the computation must return a warning explaining the
  problem.

## Contract

The skill writes `input.json`, which is the input for the Python script
`scripts/ratio.py`. Run it via Bash: `python scripts/ratio.py input.json`.

INPUT schema (keys):

```json
{
  "Revenue": float | null,
  "NetIncome": float | null,
  "EBIT": float | null,
  "InterestExpense": float | null,
  "TotalAssets": float | null,
  "CurrentAssets": float | null,
  "Inventory": float | null,
  "CurrentLiabilities": float | null,
  "TotalDebt": float | null,
  "TotalEquity": float | null
}
```

Use `null` for any missing value.

The script prints a JSON object to stdout, which the skill parses.

OUTPUT schema (success):

```json
{
  "ok": true, "error": null, "field": null,
  "current_ratio": float | null,
  "quick_ratio": float | null,
  "debt_to_equity": float | null,
  "interest_coverage": float | null,
  "ROE": float | null,
  "ROA": float | null,
  "net_margin": float | null,
  "asset_turnover": float | null
}
```

OUTPUT schema (error):

```json
{"ok": false, "error": "<message>", "field": "<key>"}
```

## Riferimenti

For all the formulas use `references/ratio_methodology.md`.
