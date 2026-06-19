# Ratio Analysis Methodology

## Notazione

| Key | Meaning |
|-----|---------|
| `Revenue` | Total sales of the period (top line of the income statement) |
| `NetIncome` | Bottom-line profit, after all costs, interest and taxes |
| `EBIT` | Earnings before interest and taxes (operating profit) |
| `InterestExpense` | Interest paid on debt during the period |
| `TotalAssets` | All assets on the balance sheet |
| `CurrentAssets` | Assets with maturity shorter than 12 months |
| `Inventory` | Stock / goods held |
| `CurrentLiabilities` | Liabilities with maturity shorter than 12 months |
| `TotalDebt` | Financial debt, short-term + long-term |
| `TotalEquity` | Shareholders' equity (book value) |

## Formule

**Liquidity**
- Current ratio = `Current Assets / Current Liabilities` — short-term coverage
- Quick ratio (acid test) = `(Current Assets − Inventory) / Current Liabilities` — stricter, excludes the less-liquid inventory

**Leverage**
- debt_to_equity = `Total Debt / Total Equity` — debt per unit of equity
- Interest coverage = `EBIT / Interest Expense` — how many times operating profit covers interest

**Profitability**
- ROE = `Net Income / Total Equity` — return on shareholders' equity
- ROA = `Net Income / Total Assets` — return on every unit of assets
- Net margin = `Net Income / Revenue` — profit per unit of revenue

**Efficiency**
- Asset turnover = `Revenue / Total Assets` — revenue generated per unit of assets

## Convenzioni

- The `debt_to_equity` ratio uses `TotalDebt` as the numerator, which we take as
  the company's total **financial** debt (not total liabilities).
- For the quick ratio we assume there are no other non-liquid current assets
  besides inventory, so `(Current Assets − Inventory)` is a good liquid proxy.

## Missing values

If some values are missing, the skill computes the other ratios and returns as
null the ones whose numerator or denominator is missing. The same applies when
a denominator is 0.
