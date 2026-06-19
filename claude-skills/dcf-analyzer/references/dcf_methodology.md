# DCF Methodology

## Notazione

| Key | Type | Meaning |
|-----|------|---------|
| `FCFF` | list[float] | Free cash flow to the firm, one value per year (N = len(FCFF)) |
| `WACC` | float \| null | If null, it is computed from the components below |
| `g` | float | Terminal growth rate (must be < WACC) |
| `NetDebt` | float | Net debt, used to bridge Enterprise Value -> Equity Value |
| `NShares` | float | Number of shares outstanding |
| `E_V` | float \| null | Equity weight E/V (WACC component) |
| `Ke` | float \| null | Cost of equity (WACC component) |
| `D_V` | float \| null | Debt weight D/V (WACC component) |
| `Kd` | float \| null | Cost of debt (WACC component) |
| `t` | float \| null | Tax rate (WACC component) |
| `wacc_steps` | list[float] \| null | Absolute deltas applied to WACC for the sensitivity grid |
| `g_steps` | list[float] \| null | Absolute deltas applied to g for the sensitivity grid |

## WACC focus

WACC can be provided as a value or through its components. In the second case the
user provides the data to compute:

```
WACC = E_V·Ke + D_V·Kd·(1 − t)
```

The user provides the weights `E_V` and `D_V` directly (already E/V and D/V),
plus `Ke`, `Kd` and `t`. `Ke` and `Kd` are taken as given, not decomposed
(e.g. `Ke` is not rebuilt via CAPM).

## Sconto dei flussi

The future cash flows are discounted using the WACC at each year i from 1 to N:

```
PV = Σ  FCFFᵢ / (1 + WACC)^i        for i = 1 ... N
```

## Terminal value (Gordon)

The terminal value TV under the Gordon model is computed as:

```
TV = FCFF_N · (1 + g) / (WACC − g)
```

It is discounted with WACC using N (the last year) as the date. We require
`g < WACC` because if `g ≥ WACC` the denominator `(WACC − g) ≤ 0` and the TV is
undefined.

## Ponte EV → equity → share

After discounting the cash flows, the Enterprise Value EV is given by:

```
EV = ΣPV + PV(TV)
```

It is followed by the Equity Value:

```
Equity = EV − NetDebt
```

The chain is closed by:

```
FV/share = Equity / NShares
```

## Sensitivity

We provide a grid of different FV using the `wacc_steps` and `g_steps` provided
by the user (or the defaults) in order to give the reader a snapshot of small
variations of g, WACC or both. Cells where the perturbed `g ≥ WACC` are returned
as null.

## Limiti del metodo

This skill cannot be used for financial institutions, because for them the fair
value is:

- valued on equity cash flows (FCFE) or dividends (DDM), not FCFF;
- discounted at the cost of equity (Ke), not the WACC.
