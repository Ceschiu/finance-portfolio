# interview-answer-formatter

A Claude Agent **Skill** that structures the answer to a technical buy-side /
finance interview question, following a fixed pedagogical template:
**definition → intuition → formula → use case → pitfalls**.

Unlike [`dcf-analyzer`](../dcf-analyzer/) and [`ratio-analysis`](../ratio-analysis/),
this skill runs **no calculations** — it is a pure prompt-design skill, made of
`SKILL.md` alone (no scripts, no engine). The whole competence lives in the
instructions and in the worked example the agent imitates.

## How it works

The skill triggers when the user asks to prepare, structure or rehearse an
answer to a technical question. It produces a single structured answer in
Italian, around 30 lines by default, in a clear (non-formal) register.

It does **not** trigger for requests to value a company or compute ratios —
those are handled by the other two skills. The boundary is set in the
`description`.

## Layout

```
interview-answer-formatter/
└── SKILL.md     # frontmatter + template + style guide + worked example
```

No `scripts/`, `references/` or `tests/`: a text-only skill needs none. Its
quality is judged on the template and the in-skill example, not on code.

## The template

| Step | Content |
|------|---------|
| Definizione | Precise, textbook definition |
| Intuizione | Plain-words explanation + why/where it is asked |
| Formula | Formula with its components, when applicable |
| Caso d'uso | A concrete buy-side example |
| Trappole | The typical mistake or subtlety that separates real understanding |

See [`SKILL.md`](SKILL.md) for the full template and a worked example
(Enterprise Value vs Equity Value).
