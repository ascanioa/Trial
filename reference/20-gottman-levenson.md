# 20 — Gottman & Levenson: observational conflict research

**Unit of analysis:** the conflict interaction. Codes attach to *speech acts in this exchange*,
never to a person's character.

**Lineage.** Levenson & Gottman's laboratory paradigm (1983, 1985) recorded couples
discussing a conflict while collecting synchronized physiological data, then coded the
interaction behaviorally. The behavioral half of that paradigm is what is portable to text.
The physiological half is not, and is marked `unmeasured` throughout.

---

## 1. Core constructs and text-observable indicators

### 1.1 The Four Horsemen

| Construct | Operational definition (text) | Discriminated from |
| --- | --- | --- |
| **Criticism** `gottman.criticism` | A complaint framed as a **global, stable attribution about the partner's character or a trait-level pattern**. Markers: global quantifiers ("you always", "you never", "siempre", "nunca"), trait nouns ("you're selfish", "eres un egoísta"), "what is wrong with you", "this is who you are". | **Complaint** — a specific behavior, in a specific situation, with the speaker's own reaction. "You didn't call last night and I was worried" is a complaint. Complaints are *not* coded as criticism at any confidence. |
| **Contempt** `gottman.contempt` | Communication from a **position of superiority**: insult, mockery, name-calling, sarcasm aimed at the partner, derision, hostile humor, "you're pathetic", mimicry, eye-roll described in text. | **Anger** — hostility without the superiority position. "I'm furious with you" is anger, not contempt. |
| **Defensiveness** `gottman.defensiveness` | Warding off perceived attack rather than taking any responsibility: counter-complaint ("what about when *you*…"), innocent-victim stance, yes-but, denial of a specific behavior, blame-reversal. | **Disagreement with a factual claim**, and **accepting responsibility with context** ("I did forget — I had a bad day, but I forgot"). |
| **Stonewalling** `gottman.stonewalling` | Listener withdrawal from the interaction: monosyllabic/minimal responses across **consecutive** turns, refusal to engage, "whatever", "fine.", "I'm done talking", leaving without a return. | **A requested time-out** — see §1.2. This discrimination is the single most important one in the module. |

Each of the four requires the speaker's *own* turn to satisfy the definition. Coding a
horseman from the partner's description of it ("you're always so contemptuous") is a
report about the relationship, not an instance, and is coded at most as `inferred`.

### 1.2 Stonewalling vs. legitimate time-out — mandatory discrimination

Gottman's own clinical recommendation is that a partner who is flooded should *take a break*.
The instrument must therefore never code a well-formed break request as stonewalling.

A withdrawal is a **time-out, not stonewalling**, when it does **all three**:
1. **names the state or need** ("I'm getting overwhelmed", "necesito calmarme");
2. **proposes a return** — a time, a duration, or an explicit commitment to resume; and
3. **does not carry a parting shot** (no insult, blame, or dismissal in the same turn).

Failing any one of the three, the withdrawal is *eligible* for stonewalling coding, and still
requires the consecutive-turn evidence in §1.1. A withdrawal that names a need but proposes
no return is genuinely ambiguous: code at most `tentative`, and name the competing reading.

### 1.3 Startup

| Construct | Operational definition |
| --- | --- |
| **Harsh startup** `gottman.harsh_startup` | The **first substantive turn** raising the issue opens with criticism, contempt, blame, or an accusatory "you" frame. Position matters: the marker must be in the opening turn(s) of the issue, not anywhere in the transcript. |
| **Softened startup** `gottman.softened_startup` | The opening turn uses an I-statement about a specific situation, plus a positive-need expression ("I feel X about Y, I need Z"), without character attribution. |

Gottman, Coan, Carrere & Swanson (1998) reported that the opening minutes of a conflict
discussion carried substantial information about how the discussion went. The transcript
analogue is turn-position, which is coarser than a time window; the module says so rather
than pretending to minute-level resolution.

### 1.4 Bids and turning toward / away / against

From the observational work on everyday interaction (Driver & Gottman, 2004).

- **Bid** `gottman.bid` — a turn that seeks connection, attention, humor, support, or
  agreement. Includes questions about the partner's experience, invitations, disclosures.
- **Turning toward** `gottman.turning_toward` — the next turn engages the bid's content:
  answers, elaborates, accepts humor, acknowledges.
- **Turning away** `gottman.turning_away` — the next turn ignores the bid's content entirely
  (topic continues as if unsaid, or no uptake).
- **Turning against** `gottman.turning_against` — the next turn responds to the bid with
  irritation, dismissal, or hostility.

Coded as **adjacency pairs**: a bid in turn *n* and the response in turn *n+1*. A bid with no
following turn (transcript ends) is `not_assessable`, never `turning_away`.

### 1.5 Repair attempts

- **Repair attempt** `gottman.repair_attempt` — any turn that tries to de-escalate or
  interrupt negativity: apology, humor that lowers tension, taking responsibility,
  softening, "let me try that again", "can we start over", expressions of affection or
  appreciation mid-conflict, meta-comments about the conversation itself.
- **Repair received** `gottman.repair_received` — the next turn takes up the repair
  (de-escalates, accepts, reciprocates).
- **Repair not received** `gottman.repair_not_received` — the next turn continues or
  escalates negativity despite the repair.

Whether repair *lands* is the informative part, and it is a property of the **dyad**
(`unit: dyad`), not of either partner. Gottman's clinical claim is that the presence of
repair attempts distinguishes couples more than the presence of conflict does.

### 1.6 Accepting influence

`gottman.accepting_influence` — a turn that yields to, incorporates, or is visibly moved by
the partner's position: agreement with a point, concession, "you're right about that",
adopting the partner's framing, asking for and using their preference.

`gottman.rejecting_influence` — persistent refusal to yield on any point across the exchange,
countering every proposal, no uptake of the partner's position anywhere in the transcript.

The original finding (Gottman et al., 1998) was specific to husbands' rejection of wives'
influence in heterosexual newlywed couples. **This instrument codes the behavior for either
partner and does not reproduce the gendered claim**, because generalizing a
sample-specific association to an individual couple of any composition is not licensed.

### 1.7 Positive-to-negative ratio

`gottman.pos_neg_ratio` — the count of positively-valenced speech acts against
negatively-valenced ones **during the conflict segment**.

Reported as a **raw count pair with the classification of every counted turn listed**, not as
a bare number, and never as a pass/fail against the 5:1 figure. Reasons:
- The 5:1 ratio (Gottman, 1993) was derived from trained coders using a validated coding
  system (SPAFF) on video, with access to affect, tone, and face. A lexical count over text
  is a different measurement with unknown correspondence to it.
- Applying a threshold derived from group-level analyses to a single conversation is a
  base-rate error.

The indicator therefore reports the ratio as **descriptive context**, marked
`inference_level: observed` for the counts and explicitly `not_licensed` for any threshold
interpretation.

### 1.8 Flooding and physiological arousal — mostly unmeasured

Levenson's contribution was physiological: diffuse physiological arousal (DPA) during
conflict, and the finding that arousal levels during interaction related to later
satisfaction change (Levenson & Gottman, 1983, 1985).

**None of this is observable in text.** Heart rate, skin conductance, and the physiological
linkage between partners have no textual proxy, and no indicator is emitted for them. They
appear in `not_assessable` with `measurement_layer: "unmeasured"` on every run.

The one permitted textual indicator is:
- `gottman.self_reported_flooding` — the speaker **states** overwhelm or the need to stop
  ("I can't do this right now", "no puedo más", "I need to stop", "my head is spinning").
  This is a self-report of a subjective state, coded `observed` for the utterance and
  explicitly **not** evidence of the physiological construct. The report states that the
  physiological layer is unmeasured every time this indicator fires.

## 2. What this theory does not license concluding

- **No prediction.** Not of divorce, separation, stability, satisfaction trajectory, or
  "how this couple will do". See §3.
- **No trait attribution.** "A criticizes" describes turns in this transcript. It does not
  make A "a critical person", and does not generalize to other conversations.
- **No threshold verdicts.** Not the 5:1 ratio, not "four horsemen present = distressed".
  The constructs were developed and validated at the level of group differences, and
  single-couple threshold application is unlicensed.
- **No causal claim** that a horseman caused an outcome within the conversation. Sequence is
  observable; causation is not.
- **No inference from absence.** Absent contempt in one conversation is not "this couple does
  not do contempt".
- **No clinical severity rating.** The instrument has no calibrated severity scale and does
  not invent one.

## 3. Calibration note — the predictive-accuracy figures

The widely-cited claim that this line of work predicts divorce with ~90% accuracy should not
be reproduced by this instrument, and the README says so. The reasons are methodological:

1. **Post-hoc model fitting without cross-validation.** Heyman & Smith Slep (2001) showed
   that the reported accuracies came from models fitted to the same sample they were
   evaluated on. When they cross-validated such models on independent data, accuracy dropped
   substantially. A percentage obtained by fitting and testing on one small sample is a
   description of that sample, not a prediction rule.
2. **Small samples, multiple models.** The predictive studies used modest samples (tens of
   couples) with several candidate variable sets; the reported figures are best-fitting
   selections among them.
3. **Base-rate sensitivity.** Accuracy figures for a base-rate-imbalanced binary outcome are
   not interpretable without the base rate and the error split, which the headline figure omits.
4. **Multimodal source.** The original coding used video, audio, affect and synchronized
   physiology. A text transcript has none of those channels.
5. **Aggregate → individual.** Even a well-cross-validated group-level model does not license
   a statement about one couple, and the direction of the communication–satisfaction
   relationship is itself contested (Lavner, Karney & Bradbury, 2016, report that
   satisfaction predicts later communication at least as well as the reverse).

**Operational consequence:** the agent emits no stability or divorce prediction at any
confidence, in any phrasing, hedged or otherwise, even if the user asks directly. It declines
and names this section as the reason.

## 4. Main empirical criticisms of the framework

- **Cross-validation failures** in the predictive claims (Heyman & Smith Slep, 2001).
- **The research-to-intervention bridge.** Stanley, Bradbury & Markman (2000) argued that
  conflict-behavior findings had been over-extended into intervention content without the
  intermediate evidence that changing those behaviors changes outcomes.
- **Directionality.** Communication behavior may be a *consequence* of satisfaction as much as
  a cause (Lavner, Karney & Bradbury, 2016).
- **Generalizability.** Foundational samples were predominantly white, middle-class,
  heterosexual, and US-based; conflict-expression norms vary across cultures, and directness
  or raised voices carry different meaning in different speech communities. This matters
  directly for a lexical coder and is listed in the report's limitations.
- **Coding-system dependence.** The constructs were operationalized for SPAFF over video.
  Text-only re-operationalization (what this module does) is a re-instrumentation, and its
  agreement with SPAFF is unknown and not assumed.

## 5. Sources

- Driver, J. L., & Gottman, J. M. (2004). Daily marital interactions and positive affect during marital conflict among newlywed couples. *Family Process, 43*(3), 301–314.
- Gottman, J. M. (1993). A theory of marital dissolution and stability. *Journal of Family Psychology, 7*(1), 57–75.
- Gottman, J. M. (1999). *The Marriage Clinic*. Norton.
- Gottman, J. M., Coan, J., Carrere, S., & Swanson, C. (1998). Predicting marital happiness and stability from newlywed interactions. *Journal of Marriage and the Family, 60*(1), 5–22.
- Gottman, J. M., & Levenson, R. W. (1992). Marital processes predictive of later dissolution: Behavior, physiology, and health. *Journal of Personality and Social Psychology, 63*(2), 221–233.
- Heyman, R. E., & Smith Slep, A. M. (2001). The hazards of predicting divorce without crossvalidation. *Journal of Marriage and Family, 63*(2), 473–479.
- Lavner, J. A., Karney, B. R., & Bradbury, T. N. (2016). Does couples' communication predict marital satisfaction, or does marital satisfaction predict communication? *Journal of Marriage and Family, 78*(3), 680–694.
- Levenson, R. W., & Gottman, J. M. (1983). Marital interaction: Physiological linkage and affective exchange. *Journal of Personality and Social Psychology, 45*(3), 587–597.
- Levenson, R. W., & Gottman, J. M. (1985). Physiological and affective predictors of change in relationship satisfaction. *Journal of Personality and Social Psychology, 49*(1), 85–94.
- Stanley, S. M., Bradbury, T. N., & Markman, H. J. (2000). Structural flaws in the bridge from basic research on marriage to interventions for couples. *Journal of Marriage and the Family, 62*(1), 256–264.
