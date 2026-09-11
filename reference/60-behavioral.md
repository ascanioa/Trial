# 60 — Behavioral couple therapy: Jacobson, Gurman, IBCT

**Unit of analysis:** observable exchanges — requests, refusals, negotiations, agreements —
and the contingencies between them.

This is the most directly observable module in the repository: its constructs were built for
behavioral observation in the first place. Its risk is the opposite of the others — not
over-inference, but treating surface behavior as the whole story, which is the critique
Gurman has pressed against behavioral couple therapy for decades.

---

## 1. Core constructs

### 1.1 Reinforcement erosion

Jacobson & Margolin (1979): behaviors that were reinforcing early in a relationship lose
reinforcing value through habituation, so the same behavior no longer produces the same
response.

| Indicator | Operational definition |
| --- | --- |
| `behavioral.reinforcement_erosion` | A partner states that behavior which previously mattered no longer registers, or that a positive act is now merely expected: "that used to help", "it doesn't count anymore", "you're supposed to do that", "why do you want a medal". |

Coded as a **voiced report** of erosion. The process itself unfolds over months or years and
is not observable in a transcript; only the partner's statement about it is.

### 1.2 Coercion cycles

Patterson's (1982) coercion theory, developed in family research: aversive behavior is
negatively reinforced when it succeeds in terminating something unpleasant, so both partners
are trained into escalation — the one who escalates gets compliance, the one who complies
gets relief.

| Indicator | Operational definition |
| --- | --- |
| `behavioral.coercive_pressure` | Aversive pressure sustained or escalated until the partner yields: repeating a demand after refusal, explicit "I'll keep bringing this up", conditional threats to withhold. |
| `behavioral.compliance_under_pressure` | The partner yields **immediately after** sustained pressure — the contingency that completes the cycle. |

The **cycle** requires both halves in sequence: pressure, then compliance (or escalation).
A single demand is not a coercion cycle, and is not coded as one.

**Boundary with the safety gate:** coercion in Patterson's sense is a learning process present
in ordinary distressed couples. It is *not* coercive control in the sense of `90-safety.md`,
which concerns domination through fear, surveillance, and restriction of liberty. When the
safety gate trips, this module does not run at all, so the two can never be conflated in one
report — and that separation is deliberate.

### 1.3 Behavior-exchange asymmetry

| Indicator | Operational definition |
| --- | --- |
| `behavioral.exchange_asymmetry` | Explicit scorekeeping or asymmetry claims about who does, gives, or concedes more. |

Codes the claim, not its accuracy. Note the overlap with `50-interdependence.md`
(`voiced_costs_rewards`): the same utterance can be evidence for two constructs from two
frameworks. Because modules code independently, this is convergence rather than
double-counting — but the report states plainly that the two indicators may rest on the
same span.

### 1.4 Requests, refusals, and the concreteness of agreements

The behavioral tradition's most practical contribution: whether an agreement specifies who
does what, when.

| Indicator | Operational definition |
| --- | --- |
| `behavioral.request` | A direct request for a behavior change. |
| `behavioral.refusal` | A refusal of a request. |
| `behavioral.concrete_agreement` | An agreement specifying behavior **and** a time, frequency, or trigger: "I'll text you when I know I'm running late", "Thursday at seven". |
| `behavioral.vague_agreement` | An agreement with no specified behavior, time, or trigger: "I'll try", "I'll do better", "we'll see", "soon". |

The concrete/vague discrimination is coded on the **agreement turn only**, and says nothing
about whether the agreement will be kept. "I'll try" may be perfectly sincere; the code
concerns its specificability, not the speaker's intention or character.

### 1.5 Acceptance and change (IBCT)

Jacobson & Christensen's (1996) integrative behavioral couple therapy added *emotional
acceptance* to the change-oriented methods of traditional behavioral couple therapy, after
evidence that change-only approaches showed relapse at follow-up.

| Indicator | Operational definition |
| --- | --- |
| `behavioral.acceptance_move` | A turn that accepts a difference rather than contesting it: "that's how you are and I can live with it", "I'm not asking you to change", framing a difference as difference rather than fault. |
| `behavioral.change_demand` | A turn pressing for behavior change. Not negative in itself — IBCT holds that couples need both. |

The module reports the **balance of the two as voiced in this conversation**. It does not
say which the couple needs, which is a clinical judgment made with the couple present.

## 2. What this theory does not license concluding

- **No prediction** of whether an agreement will be kept, or whether the couple will change.
- **No verdict on who is more reasonable**; requests and refusals are coded symmetrically.
- **No claim that scorekeeping claims are accurate.**
- **No treatment indication.** That a transcript shows change demands without acceptance
  moves does not indicate IBCT, or any therapy, for this couple.
- **No reading of motive.** Behavioral coding is deliberately agnostic about intention, and
  the instrument keeps that agnosticism rather than smuggling motive in through rationales.
- **No equating of `coercive_pressure` with abuse.** See §1.2.

## 3. Main empirical criticisms

- **Relapse after traditional BCT.** Follow-up studies found meaningful deterioration of
  gains in a substantial minority of couples (e.g. Jacobson, Schmaling & Holtzworth-Munroe,
  1987), which is what motivated IBCT's acceptance component.
- **Gurman's critique.** Gurman has long argued that behavioral models under-address affect,
  meaning, and the couple's implicit relational contract, and that their efficacy data rest
  on narrow outcome measures (see Gurman & Fraenkel, 2002, for the historical account).
- **IBCT vs. TBCT is not a clean win.** The largest direct comparison found both treatments
  produced substantial improvement with no reliable overall difference at termination
  (Christensen et al., 2004), and differences at follow-up were modest (Christensen et al.,
  2010). The acceptance-vs-change framing is clinically useful; it is not a demonstrated
  superiority.
- **Ecological validity of behavior counts.** Frequency counts of requests and compliance in
  a recorded session correspond imperfectly to what happens at home.
- **Reinforcement language is metaphorical here.** Applying operant terms to adult
  conversation is an analogy, not a demonstrated mechanism; nothing in a transcript shows a
  reinforcement schedule.

## 4. Sources

- Christensen, A., Atkins, D. C., Berns, S., Wheeler, J., Baucom, D. H., & Simpson, L. E. (2004). Traditional versus integrative behavioral couple therapy for significantly and chronically distressed married couples. *Journal of Consulting and Clinical Psychology, 72*(2), 176–191.
- Christensen, A., Atkins, D. C., Baucom, B., & Yi, J. (2010). Marital status and satisfaction five years following a randomized clinical trial comparing traditional versus integrative behavioral couple therapy. *Journal of Consulting and Clinical Psychology, 78*(2), 225–235.
- Gurman, A. S., & Fraenkel, P. (2002). The history of couple therapy: A millennial review. *Family Process, 41*(2), 199–260.
- Jacobson, N. S., & Christensen, A. (1996). *Integrative Couple Therapy: Promoting Acceptance and Change*. Norton.
- Jacobson, N. S., & Margolin, G. (1979). *Marital Therapy: Strategies Based on Social Learning and Behavior Exchange Principles*. Brunner/Mazel.
- Jacobson, N. S., Schmaling, K. B., & Holtzworth-Munroe, A. (1987). Component analysis of behavioral marital therapy: Two-year follow-up and prediction of relapse. *Journal of Marital and Family Therapy, 13*(2), 187–195.
- Patterson, G. R. (1982). *Coercive Family Process*. Castalia (Eugene, OR).
