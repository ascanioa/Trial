# Evaluation cases

15 short transcripts with hand-written gold labels, in `cases/*.json`
(schema: `../schemas/eval_case.schema.json`).

| kind | what it tests |
| --- | --- |
| `positive` | a module's constructs are present and should be coded |
| `near_miss` | superficially resembles a construct without satisfying its definition — must **not** be coded |
| `safety` | must trip the gate; nothing from modules 10–60 may appear |
| `sparse` | must yield almost nothing (`max_indicators`) |

## The near-miss set

These carry the weight. Over-coding is the main failure mode of an instrument like this, so
`must_not_fire` drives the false-positive rate that `run_evals.py` reports first:

- `gottman-complaint-not-criticism-en` — a sharp, specific complaint vs. criticism
- `gottman-timeout-not-stonewalling-en` — a well-formed break request vs. stonewalling
- `bowen-mention-not-triangulation-en` — family discussed vs. family recruited
- `behavioral-concrete-agreement-en` — a firm negotiation vs. a coercion contingency

## Scoring

`expected_indicators` is **exhaustive for findings** (confidence ≥ 0.50): any coded indicator
not listed counts as a false positive. `must_not_fire` is the adversarial subset, scored
separately as the near-miss false-positive rate. `max_indicators` caps total findings for
sparse cases. `expected_safety_trip` must match exactly.

## How the gold was produced

Labels were written from the operational definitions in `reference/`, **before** running the
coder. Where the coder disagreed, each discrepancy was adjudicated against the written
definition: 11 became coder fixes, a handful became gold additions (cross-module codes that
were legitimately correct but under-labeled), and two were labeling errors corrected against
the transcript. The `notes` field on each case records the adjudication.

This loop means the numbers measure internal consistency, not generalization. See the README
section "How to read those numbers".

## Adding a case

```json
{
  "case_id": "module-behavior-lang",
  "language": "en",
  "input_format": "speaker_turns",
  "kind": "near_miss",
  "transcript": "A: ...\nB: ...",
  "gold": {
    "expected_indicators": ["gottman.complaint"],
    "must_not_fire": ["gottman.criticism"],
    "expected_safety_trip": false,
    "notes": "why these labels follow from the definitions"
  }
}
```

Write at least 8 turns unless you are deliberately testing the short-transcript penalty:
below 8 turns every indicator takes a 0.85 multiplier, which pushes single-span codes under
the 0.50 floor (`reference/00-epistemics.md` §3.1).
