# VBA — Macro e funzioni per analytics di portafoglio

5 esercizi progressivi di VBA finance, dai pattern base alle ottimizzazioni performance su 1000+ strumenti.

## Esercizi

| # | File | Concetti chiave | Difficoltà |
|---|------|-----------------|------------|
| 1 | [`Es1_CalcolaPnL.bas`](./src/Es1_CalcolaPnL.bas) | Range/Cells, For loop, If/Else, formattazione condizionata, idempotenza | ⭐ |
| 2 | [`Es2_ArricchisciPortafoglio.bas`](./src/Es2_ArricchisciPortafoglio.bas) | Multi-sheet, `Application.Match` + `IsError`, `Select Case`, classificazione rating | ⭐⭐ |
| 3 | [`Es3_BondPricingDuration.bas`](./src/Es3_BondPricingDuration.bas) | Functions/UDF, composizione di funzioni, pricing bond, Duration di Macaulay e Modificata | ⭐⭐ |
| 4 | [`Es4_AggiornaPrezziEReport.bas`](./src/Es4_AggiornaPrezziEReport.bas) | File I/O esterno (Workbooks.Open/Close), path dinamici, error handling robusto, performance | ⭐⭐⭐ |
| 5 | [`Es5_AnalizzaPortafoglio.bas`](./src/Es5_AnalizzaPortafoglio.bas) | Range-to-array, bulk write, Dictionary per aggregazioni, Large/Small, timing | ⭐⭐⭐⭐⭐ |

## Pattern coperti

- **Lookup robusto multi-foglio**: `Application.Match` + `IsError` invece di `WorksheetFunction.Match`
- **UDF (User-Defined Functions)** chiamabili come formule native di Excel
- **File I/O** con apertura/chiusura workbook esterni e path relativi via `ThisWorkbook.Path`
- **Error handling professionale**: `On Error GoTo` + `CleanExit` + `Resume` per cleanup garantito
- **Performance optimization**: range-to-array, bulk write, `ScreenUpdating/Calculation/EnableEvents/DisplayAlerts`
- **Aggregazioni efficienti** con `Scripting.Dictionary` (hash map O(1))

## Come usare

1. Scarica [`demo/File_per_ripasso_VBA.xlsm`](./demo/File_per_ripasso_VBA.xlsm) e [`demo/MarketData.xlsx`](./demo/MarketData.xlsx)
2. Tieni i due file **nella stessa cartella** (Es 4 usa path relativi)
3. Apri il file `.xlsm`, abilita le macro
4. Premi `Alt+F8` e lancia la macro che vuoi testare

I file `.bas` in `src/` sono i moduli VBA esportati: già presenti dentro `.xlsm`, ma versionati separatamente per code review e riusabilità.

## Performance benchmark (Es 5)

Macro `AnalizzaPortafoglio` su 1000 strumenti random:
- Esecuzione tipica: **< 0.3 secondi**
- Stesso lavoro con loop cella-per-cella: ~5-8 secondi
- **Speedup ~20-30x** grazie al pattern range-to-array
