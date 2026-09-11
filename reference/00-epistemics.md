# 00 — Epistemics

**Read this first. It overrides any module file it conflicts with.**

This instrument is a **descriptive coding tool**. It reads a transcript of a conversation
between romantic partners, marks observable interactional behavior, and maps that behavior
to named constructs from couples-psychology research.

It is not a therapist, not a diagnostician, and not a predictor.

---

## 1. What this instrument does and does not do

| Does | Does not |
| --- | --- |
| Code observable text behavior (what was said, in what sequence) | Assess mental health, personality, or pathology |
| Map behavior to named theoretical constructs | Assign clinical or diagnostic labels |
| Quote the span that supports each code | Assign dispositional traits (e.g. "an avoidant person") |
| State what it looked for and did not find | Predict divorce, breakup, or relationship stability |
| Offer competing readings of the same text | Adjudicate who is right, who started it, or who is at fault |

These are not stylistic preferences. Three of them are hard failure modes:

- **Dispositional inference.** A conversation samples *behavior in one context at one time*.
  Attachment style, differentiation of self, and personality are dispositional constructs
  measured with validated instruments across contexts. A transcript cannot yield them.
  The correct output is a *strategy observed in this exchange*, never a *type assigned to a person*.
- **Prediction.** See `20-gottman-levenson.md` §Calibration. No stability or dissolution
  prediction is ever emitted, at any confidence, under any phrasing, including hedged phrasing.
- **Symmetry violation.** In a dyadic frame, "who started it" is a framing artifact of where
  the transcript begins. Cycle descriptions are stated symmetrically. The one and only
  exception is the safety gate (`90-safety.md`), where symmetric framing is itself the harm.

## 2. Evidence tiers

Every indicator carries an `inference_level`:

- **`observed`** — the construct's operational definition is satisfied by a quoted span.
  The quote must contain the coded behavior itself, not context for it.
- **`inferred`** — the reading requires a step beyond the text (intent, internal state,
  history, causation). Permitted only when the module file licenses it, must name the
  inferential step in `rationale`, and is capped at `confidence` 0.65.
- **`unmeasured`** — the construct is part of the theory but has no text-observable
  indicator (e.g. physiological flooding). Reported as a named gap, never as a finding.

A claim with no quoted span is not an indicator. It does not go in the report as a finding.

## 3. Confidence scale

`confidence` is a declared scale, not a vibe. It answers one question: *how strongly does
this transcript's text support this code?* It does not encode importance or severity.

| Band | Range | Meaning | Reporting |
| --- | --- | --- | --- |
| `strong` | 0.80 – 1.00 | Multiple (≥2) unambiguous verbatim instances, each independently satisfying the operational definition. No credible competing reading of the spans. | Reported as a finding |
| `tentative` | 0.50 – 0.79 | Present but sparse (a single instance) **or** ambiguous (the span also supports a competing reading). | Reported as a finding, explicitly marked tentative, competing reading named |
| `insufficient` | 0.00 – 0.49 | Below the evidentiary floor: hinted at, contextual, or requiring inference not licensed by the module. | **Not a finding.** Reported under "insufficient evidence" with what was seen and what is missing |

Band boundaries are inclusive at the lower bound: 0.80 is `strong`, 0.79 is `tentative`.

### 3.1 Scoring procedure

Start from the count of qualifying spans, then apply penalties. Never apply a bonus.

```
base:  1 span  -> 0.55        2 spans -> 0.72        3+ spans -> 0.85
```

Penalties (cumulative, applied multiplicatively in this order):

| Condition | Factor |
| --- | --- |
| Any span also satisfies a competing construct's definition (ambiguity) | × 0.85 |
| `inference_level` = `inferred` | × 0.80, then cap at 0.65 |
| Speaker attribution for the span is uncertain (see §5) | × 0.80 |
| Transcript is under 8 turns total | × 0.85 |
| A same-module counter-indicator is present (e.g. a landed repair against escalation) | × 0.85 |

The floor is structural: **one instance of anything is a data point, not a pattern.** A single
span cannot reach `strong` (0.55 is the ceiling for one span before penalties). A module with
one sparse signal shrinks toward "no finding"; it never extrapolates a pattern from one turn.

### 3.2 Calibration duty

Declared confidence is checked against observed accuracy by `run_evals.py`. If codes declared
at 0.8+ are right less often than ~80% of the time on the eval set, the scale is miscalibrated
and the operational definitions — not the confidence numbers — are what must change.

## 4. Module independence

Each module codes the transcript **in isolation**. A module never reads another module's
indicators, and the modules have no shared mutable state during coding. Composition happens
only after every module has emitted its indicators.

This is enforced architecturally (`src/couples_analyst/compose.py` hands each module the
normalized transcript and nothing else) because the failure it prevents is real: a strong
signal in one frame otherwise recruits weak signals in the others into a single confirming
story. Convergence across modules is only evidence if the modules could have diverged.

The safety gate is the single exception, and it runs *before* everything, not alongside it.

## 5. Uncertain attribution

Misattributed turns invalidate the coding — a criticism coded to the wrong speaker inverts
the cycle description. When the normalizer cannot confidently assign a speaker or a turn
boundary, it marks the turn `attribution_uncertain`. Every indicator resting on such a turn
takes the §3.1 penalty and the report states the uncertainty in its own line under
"What this analysis cannot tell you".

## 6. Ruled out

The "Ruled out" section is mandatory and must be non-empty. An instrument that only reports
what it finds cannot be distinguished from one that finds whatever it looks for.

A construct is ruled out when it was actively searched, its operational definition was not
satisfied, **and** the transcript contained material where it would plausibly have appeared
(a conflict sequence without contempt markers; a repair attempt that was received). Record
the span that argues against it. "No evidence" in a transcript that had no occasion for the
construct is *absence of opportunity*, and is reported separately as `not_assessable`.

## 7. Competing readings

At least one alternative interpretation of the same transcript is mandatory, and it must
specify **what additional data would discriminate between the readings** (e.g. tone of voice,
what preceded the exchange, the other partner's account, base rates of this interaction).
A competing reading that cannot be tested by any obtainable evidence has been stated too
vaguely to be useful.

## 8. Language

The report is written in the transcript's own language. English and Spanish are supported.
Construct names keep their canonical English form with a translation on first use, so that
`analysis.json` is language-invariant and the prose is not.

## 9. Provenance

Every indicator names its `theory_source`. If a theory does not license a text-only
indicator for one of its constructs, the module file says so and no indicator is emitted.
Do not manufacture an operationalization that the source theory does not support.
