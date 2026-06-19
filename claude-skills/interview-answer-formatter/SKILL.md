---
name: interview-answer-formatter
description: Structure a technical answer for the user as if it were an interview answer. Use when the user asks to prepare, structure, or rehearse an answer to a technical buy-side / finance interview question. Do not use to compute a valuation or financial ratios (see dcf-analyzer / ratio-analysis); this skill formats an explanation, it does not run calculations.
license: MIT
---

# interview-answer-formatter

## Quando usare

Structure a technical answer for the user as if it were an interview answer. Use
when the user asks to prepare, structure, or rehearse an answer to a technical
buy-side / finance interview question. Do not use to compute a valuation or
financial ratios (see dcf-analyzer / ratio-analysis); this skill formats an
explanation, it does not run calculations.

## Struttura della risposta (il template)

1. **Definizione** — technical definition of the asked topic/subject.
2. **Intuizione** — a discursive comment on the definition, plus why someone
   would ask the question and where the concept is used.
3. **Formula** — if applicable, the formula with a brief description of its
   components.
4. **Caso d'uso** — a practical, buy-side example of the subject.
5. **Trappole** — the typical mistakes or subtleties one incurs on the topic.

## Linee guida di stile

Answer in Italian. By default the answer is around 30 lines, unless the user
asks otherwise. Do not use overly formal language: the key points must be clear
and understandable.

## Esempio

**Question:** Qual è la differenza tra Enterprise Value ed Equity Value?

**Answer:**

**Definizione.** L'Enterprise Value è il valore dell'intera azienda operativa,
cioè per tutti i finanziatori (debito + equity); l'Equity Value è la parte che
spetta ai soli azionisti.

**Intuizione.** L'EV misura quanto vale "la macchina che genera cassa", a
prescindere da come è finanziata; l'Equity è ciò che resta agli azionisti dopo
aver ripagato i creditori. Te lo chiedono per vedere se sai separare l'operativo
dalla struttura finanziaria.

**Formula.** `Equity Value = EV − Net Debt`, dove `Net Debt = debito − cassa`.

**Caso d'uso.** In un DCF: scontando l'FCFF al WACC ottieni l'EV; per arrivare al
prezzo per azione togli il debito netto e dividi per il numero di azioni.

**Trappole.** Confondere EV ed Equity (es. usare l'equity in un multiplo
`EV/EBITDA`); dimenticare la cassa nel net debt; e ricordare che per le banche
EV/WACC non si applica.

## Casi limite

- If the question bundles more themes, ask the user to split it into
  sub-questions and propose a possible scheme.
- If the question is vague or not technical, ask the user to rephrase it so it
  can be answered technically.
