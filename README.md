# couples-analyst

A **descriptive coding instrument** for transcripts of conversations between romantic
partners. It marks observable interactional behavior, maps it to named constructs from
couples-psychology research, anchors every claim to a quoted span, and reports what the
evidence rules *out* as explicitly as what it rules in.

It is not a therapist, not a diagnostician, and not a predictor. Those are not disclaimers
bolted onto a tool that would otherwise do those things — they are the constraints the whole
design follows from.

---

## What it does and does not do

| Does | Does not |
| --- | --- |
| Code observable text behavior, turn by turn | Assess mental health, personality, or pathology |
| Map behavior to named theoretical constructs | Assign clinical or diagnostic labels |
| Quote the verbatim span supporting every code | Assign dispositional traits ("an avoidant person") |
| State what it looked for and did not find | Predict divorce, breakup, or stability |
| Offer competing readings of the same text | Adjudicate who is right or who started it |
| Halt when it sees markers of abuse | Apply "both partners contribute" to coercive control |

### Intended use

A symmetric description of one conversation that **both partners could read** — as a
starting point for a conversation with each other, or with a clinician who can ask the
questions this tool only lists.

### Not intended, and refused

Building a case against a partner; evidence for a dispute, custody matter, or legal
proceeding; winning an argument; diagnosing someone who is not present; analyzing a partner
covertly. The agent declines these and says why (`reference/90-safety.md` §4).

### Consent

**Both partners should know the transcript is being analyzed.** The tool cannot verify this
and does not try. It states the expectation in every report, and refuses requests that are
explicitly covert.

---

## The Gottman predictive-accuracy caveat

You will have seen the claim that this line of research predicts divorce with ~90% accuracy.
**This instrument emits no stability or dissolution prediction, at any confidence, in any
phrasing, even if asked directly.** The reasons are methodological, not squeamish:

1. **No cross-validation.** Heyman & Smith Slep (2001) showed the headline accuracies came
   from models fitted to the same sample they were evaluated on. Cross-validated on
   independent data, accuracy dropped substantially. A percentage obtained by fitting and
   testing on one small sample describes that sample; it is not a prediction rule.
2. **Small samples, model selection.** The predictive studies used tens of couples with
   several candidate variable sets; the published figures are the best-fitting selections.
3. **Base rates.** An accuracy figure for an imbalanced binary outcome is uninterpretable
   without the base rate and the error split, which the headline figure omits.
4. **Different data entirely.** The original coding used video, audio, facial affect and
   synchronized physiology. A text transcript has none of those channels.
5. **Aggregate → individual.** Even a well-validated group-level model would not license a
   claim about one couple — and the direction of the communication–satisfaction relationship
   is itself contested (Lavner, Karney & Bradbury, 2016).

Full treatment in `reference/20-gottman-levenson.md` §3. Each module file carries the same
kind of section: what the theory does **not** license, and the main empirical criticisms of
it — including for the frameworks this repository otherwise relies on.

---

## The safety gate

`reference/90-safety.md` runs **before** any pattern analysis and can halt the run.

It screens for threat, physical violence or its aftermath, intimidation,
monitoring/surveillance, financial control, isolation, sexual coercion, and expressed fear.
If any marker appears, the conflict-pattern analysis is **withheld, not qualified**: no
cycle, no Four Horsemen, no "both partners contribute". The output is only what was
observed, why the standard analysis does not apply, and a recommendation to consult a
qualified professional.

Every conflict framework here assumes two partners with roughly symmetric power to influence
each other. Where one partner controls the other through fear, surveillance or restriction of
liberty, that assumption fails, and cycle language reframes coercion as a mutual dynamic
(Johnson, 1995, 2008; Stark, 2007; Bograd & Mederos, 1999).

The gate errs toward tripping: a false positive costs a withheld analysis, a false negative
costs a harmful one. **It is a conservative heuristic, not a validated instrument** — no
validated screen for IPV from conversation text alone is known to us. It does not determine
that abuse occurred, does not assess danger, and produces no risk score. Its silence is not
evidence of safety, and every report says so.

Transcripts indicating a minor in a romantic or sexual relationship halt unconditionally,
with nothing coded or excerpted.

---

## Install and run

Python 3.10+, no dependencies.

```bash
python3 -m couples_analyst transcript.txt          # writes analysis.json + report.md
python3 -m couples_analyst chat.txt --stdout       # also print the report
python3 -m couples_analyst t.txt --keep-names      # don't anonymize to A / B
python3 -m couples_analyst t.txt --language es     # override language detection
python3 -m couples_analyst t.txt --strict          # non-zero exit on contract violation
cat t.txt | python3 -m couples_analyst             # stdin
```

Run from the repo root, or `pip install -e .` for the `couples-analyst` command.

**Input formats**, auto-detected: plain text, `Speaker: text` turns, chat exports
(WhatsApp-style timestamped lines), and subtitles (SRT / WebVTT). Everything is normalized to
numbered turns with speaker ids, anonymized to A / B by default. Where a speaker or a turn
boundary cannot be established — plain text and subtitles especially — the turn is flagged,
affected indicators are penalized, and the report says so. Misattributed turns invert the
coding, so this is never smoothed over.

**As a Claude Code subagent:** `.claude/agents/couples-analyst.md` drives the same procedure
from the `reference/` files. The deterministic pipeline above is the reference implementation
the agent checks itself against; where they disagree, `reference/` is the authority.

---

## Output

Two artifacts per run.

**`analysis.json`** — conforms to `schemas/analysis.schema.json`. Every indicator carries:

```json
{
  "indicator_id": "gottman.contempt",
  "module": "20-gottman-levenson",
  "construct": "Contempt",
  "theory_source": "Gottman (1999); Gottman & Levenson (1992)",
  "unit": "speaker",
  "speaker": "A",
  "evidence": [{ "turn": 3, "speaker": "A", "quote": "You are pathetic.", "char_span": [11, 28] }],
  "inference_level": "observed",
  "confidence": 0.72,
  "confidence_band": "tentative",
  "confidence_factors": ["2 qualifying span(s) -> base 0.72"],
  "rationale": "Communication from a position of superiority...",
  "competing_reading": "...",
  "not_licensed": "Does not establish the speaker's intent..."
}
```

**The markdown report**, in the transcript's own language (English or Spanish, detected):

1. **What this analysis cannot tell you** — first, not last
2. **Interaction cycle** — dyadic, symmetric, no first cause
3. **Coded indicators by module** — verbatim evidence, confidence, and what each does not license
4. **Ruled out** — mandatory: constructs actively searched for and not found, with the evidence against them
5. **Competing readings** — at least one, each with what data would discriminate
6. **Open questions** — what a clinician would need to ask

---

## Architecture

A **modular indicator model**, not one holistic judgment.

```
transcript ─► normalize ─► safety gate ─┬─► TRIPPED ──► safety-only report
                                        │
                                        └─► 10  20  30  40  50  60   (independent)
                                              └───┴───┴───┴───┴──► compose ─► analysis.json
                                                                            └► report.md
```

**Modules never see each other's conclusions during coding.** Each receives the normalized
transcript and nothing else; composition happens only after all coding is done. This is
enforced in `src/couples_analyst/compose.py` because the failure it prevents is real: a
strong signal in one frame otherwise recruits weak signals in the others into a single
confirming story. Convergence across modules is only evidence if the modules could have
diverged.

| Module | Theory | File |
| --- | --- | --- |
| 00 | Epistemics — evidence tiers, confidence scale, module independence | `reference/00-epistemics.md` |
| 10 | Attachment — Bowlby, Ainsworth, Hazan & Shaver | `reference/10-attachment.md` |
| 20 | Conflict behavior — Gottman & Levenson | `reference/20-gottman-levenson.md` |
| 30 | EFT — Johnson, Greenberg | `reference/30-eft.md` |
| 40 | Family systems — Bowen | `reference/40-bowen-systems.md` |
| 50 | Interdependence — Kelley & Thibaut, Levinger | `reference/50-interdependence.md` |
| 60 | Behavioral / IBCT — Jacobson, Gurman | `reference/60-behavioral.md` |
| 90 | Safety gate — runs first | `reference/90-safety.md` |

### Confidence is computed, not asserted

Declared in `reference/00-epistemics.md` §3, implemented in `indicators.py`:

| Band | Range | Meaning |
| --- | --- | --- |
| `strong` | 0.80–1.00 | ≥2 unambiguous verbatim instances, no credible competing reading |
| `tentative` | 0.50–0.79 | present but sparse or ambiguous; competing reading named |
| `insufficient` | < 0.50 | **not a finding** — reported as a gap, with what is missing |

Scoring starts from the number of qualifying spans and applies **penalties only, never
bonuses**: ambiguity, inference, uncertain attribution, short transcript, counter-indicators.
Every penalty applied is recorded in `confidence_factors` so the number can be audited rather
than trusted. A single span cannot reach `strong` under any circumstances — **one instance of
anything is a data point, not a pattern.**

---

## Evaluation

```bash
python3 run_evals.py                    # all 15 hand-labeled cases
python3 run_evals.py --module gottman   # one module's indicators
python3 run_evals.py --backend claude   # score the LLM agent instead of the reference coder
python3 run_evals.py --json out.json
python3 tests/test_contract.py          # 26 invariant tests
```

`evals/cases/` holds 15 short transcripts with hand-written gold labels: clear positives per
module, **near-miss negatives** (a sharp complaint that is *not* criticism; withdrawal that is
a legitimate time-out and *not* stonewalling; family discussed but *not* triangulated; a firm
negotiation that is *not* coercion), one safety case that must trip the gate, and one sparse
case that must yield almost nothing.

Current results, reference coder:

```
module               TP   FP   FN   prec recall    F1
10-attachment         9    0    0   1.00   1.00  1.00
20-gottman-levenson  31    0    0   1.00   1.00  1.00
30-eft                6    0    0   1.00   1.00  1.00
40-bowen-systems      6    0    0   1.00   1.00  1.00
50-interdependence    7    0    0   1.00   1.00  1.00
60-behavioral        19    0    0   1.00   1.00  1.00
ALL                  78    0    0   1.00   1.00  1.00

near-miss false-positive rate: 0/88  (0.0%)

calibration    n   observed   expected
0.50-0.65     43       100%     >= 50%
0.65-0.80     21       100%     >= 65%
0.80-1.00     14       100%     >= 80%
```

### How to read those numbers — they are weaker than they look

The transcripts, the gold labels and the coder were written by the same author, and **the
coder was corrected whenever it disagreed with a label**. That loop is how the instrument was
built: 11 real over-coding bugs were found and fixed this way (a bare `\bdeal\b` matching
"it's not a big deal"; `\bstay\b` matching "the kids would rather stay home"; a bare question
coded as accepting influence; a counter-complaint double-coded as a complaint; a day-of-week
word alone coded as a complaint). Two gold labels turned out to be wrong and were corrected
against the transcripts rather than the code.

But the result is that these figures measure **internal consistency between the `reference/`
definitions and their implementation** — not accuracy on real conversations, and not agreement
with trained human coders. Treat a perfect score as evidence that the suite is too small and
too friendly. The evaluation that would matter is independently written transcripts, labeled
by someone who has not seen the code, scored against a human-coded reference such as SPAFF.
`run_evals.py` prints this caveat with every run.

Gold is **exhaustive for findings**: any coded indicator not in the gold list counts as a
false positive, which is what makes precision meaningful here. Over-coding is the main failure
mode of an instrument like this, so the near-miss false-positive rate is the number to watch.

---

## Deliberately not implemented

Stated rather than approximated, because a plausible-looking output for these would be worse
than none:

- **Attachment styles** for either partner. Measured with validated instruments across
  contexts; the two main traditions converge only weakly with each other (Roisman et al.,
  2007). The module codes *strategies in this exchange* and never a type.
- **Differentiation of self as a level or score.** Bowen described it as a lifelong,
  cross-context characteristic and held it could not be reliably assigned from short
  observation.
- **Sibling position, societal emotional process, family projection process, nuclear family
  emotional system** (Bowen). Weak empirical support or no text-observable indicator.
- **Physiological arousal, flooding, physiological linkage** (Levenson). No textual proxy.
  Self-reported overwhelm is coded as a *self-report* and explicitly not as evidence of the
  physiological construct.
- **The 5:1 positive-to-negative ratio as a threshold.** The counts are reported as counts;
  the ratio came from trained coders using SPAFF on video, and applying a group-level
  threshold to one conversation is a base-rate error.
- **Cohesiveness as a computed balance** of attractions, barriers and alternatives. That
  would be a dissolution prediction in different vocabulary.
- **Any risk, danger, or lethality score** in the safety gate.

`eft.primary_emotion_inferred` is the most inference-heavy code in the repository. It is
capped at 0.65, requires an attachment-relevant textual hook (anger alone is not one), and is
phrased as a hypothesis to put to the speaker — because the clinical move in EFT is to *ask*,
and this instrument cannot ask.

---

## Limitations

Text only: no tone, volume, pacing, face, gesture, or touch — the channels that carry sarcasm,
warmth and contempt. One conversation, one moment, one framing. No history, no intent, no
partner's account. The research these constructs come from drew predominantly on white,
middle-class, heterosexual US samples, and norms for directness and conflict expression vary
widely; the Spanish lexicon is not a validated translation of any coding scheme. The coder is
lexical, so it under-detects anything phrased unusually and cannot see meaning carried by
implication.

## Citations

Each `reference/` file ends with its sources. **All 50 were checked against primary and
publisher records** (journal, volume, issue, page range, title, publisher) — Wiley, APA,
JSTOR, ERIC, Annual Reviews, Guilford/Routledge/Norton catalogue entries, and university
repositories. Three were wrong and are corrected:

| Citation | Was | Is |
| --- | --- | --- |
| Bograd & Mederos (1999) | "selection of treatment **modalities**" | "selection of treatment **modality**" |
| Fraley, Waller & Brennan (2000) | *JPSP, 78*(2), 350–**365** | *JPSP, 78*(2), 350–**364** |
| Brennan, Clark & Shaver (1998) | "Self-report measurement of adult **romantic** attachment" | "Self-report measurement of adult attachment: An integrative overview" (pp. 46–76) |

Thirteen others were made more precise (restored subtitles, chapter page ranges, Carrère's
diacritic, Springer Publishing rather than Springer). The remaining 34 were confirmed exactly
as written.

Two page ranges are worth knowing about if you check them yourself: reference aggregators
give Fraley et al. (2000) as 350–365, but the Illinois and Minnesota institutional
repositories and the APA record all give 350–364. Jacobson, Schmaling & Holtzworth-Munroe
(1987) appears in some sources as "*A* component analysis"; the journal's own title has no
leading article, which is what is used here.

Where a theory does not license a text-only indicator, the reference file says so instead of
manufacturing one.

## Licence

Not specified. Add one before distributing.
