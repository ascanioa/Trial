# 50 — Interdependence and cohesiveness: Kelley & Thibaut, Levinger

**Unit of analysis:** what the partners **voice** about costs, rewards, fairness, standards,
and alternatives.

The hard constraint: this module codes **only what is said**. It does not compute a couple's
outcomes, estimate their satisfaction, or model their decision. Every construct below is
coded as *voiced content*, never as an assessed quantity.

---

## 1. Core constructs

### 1.1 Outcome interdependence

Thibaut & Kelley (1959): partners' outcomes depend jointly on both partners' behavior;
interaction can be described in terms of the outcomes each pattern of joint action produces.

| Indicator | Operational definition |
| --- | --- |
| `interdependence.voiced_costs_rewards` | A partner states what the relationship costs or gives them: effort, division of labor, money, time, fairness or imbalance. |

### 1.2 Comparison level (CL)

The standard against which a person evaluates a relationship's outcomes — what they believe
they deserve or expect, formed by past relationships and observed relationships.

| Indicator | Operational definition |
| --- | --- |
| `interdependence.comparison_level` | A partner voices a standard: "this isn't what I expected", "I deserve better", "this isn't how a marriage should be", comparison to other couples. |

**Satisfaction is not inferred.** CL is one input to satisfaction in the theory, and a
transcript contains neither the outcomes nor the standard with enough precision to compute
the comparison. A voiced standard is a voiced standard.

### 1.3 Comparison level for alternatives (CL-alt)

The lowest outcome a person will accept given their best alternative — the theoretical
determinant of *dependence* and stability, as distinct from satisfaction.

| Indicator | Operational definition |
| --- | --- |
| `interdependence.alternatives_voiced` | A partner refers to alternatives: being better off alone, someone else available, leaving, options. |

**Coded with particular care**, because this is where an instrument like this most easily
does harm:
- A statement about alternatives made **during** conflict is not a measure of CL-alt.
  Threatening to leave mid-argument is a speech act inside the conflict; it may be protest
  (see `10-attachment.md` §2.3), leverage, or genuine appraisal, and the text does not
  distinguish these.
- The module **never** treats such statements as a stability or dissolution signal. See
  `00-epistemics.md` §1 and `20-gottman-levenson.md` §3.
- Every `alternatives_voiced` indicator carries the competing reading above in its record.

### 1.4 Transformation of motivation

Kelley & Thibaut's account of how partners move from the "given matrix" (immediate
self-interest) to an "effective matrix" incorporating the partner's outcomes — the basis for
pro-relationship behavior.

| Indicator | Operational definition |
| --- | --- |
| `interdependence.pro_relationship_transformation` | A turn in which a partner visibly sets aside an immediate preference for the pair or for the other: yielding a choice, absorbing a cost, proposing a joint solution over a preferred one. |
| `interdependence.self_interest_stance` | A turn holding to individual outcome without reference to the pair's: insisting on a preference, scorekeeping, refusing to absorb any cost. |

The *transformation* is an internal process; what text shows is the behavior consistent with
it. Coded `observed` for the behavior, with the internal process marked unmeasured.

### 1.5 Levinger's cohesiveness model

Levinger (1965, 1976) modeled marital cohesiveness as the balance of three forces:

| Force | Indicator | Operational definition |
| --- | --- | --- |
| **Attractions** | `interdependence.attractions_voiced` | Rewards of the relationship as stated: affection, companionship, shared life, being known. |
| **Barriers** | `interdependence.barriers_voiced` | Restraints against leaving as stated: children, finances, property, religion, family opinion, years invested. |
| **Alternatives** | `interdependence.alternatives_voiced` | As above. |

The model's predictive claim — that cohesiveness is a function of these three — is **not
applied**. The module reports which forces the partners voiced and quotes them. It does not
compute a balance, score cohesiveness, or say what the balance implies. Doing so would be a
dissolution prediction wearing different vocabulary.

## 2. What this theory does not license concluding

- **No stability, dissolution, or "will they stay" inference of any kind**, including from
  barriers and alternatives, which is precisely what this framework is popularly misused for.
- **No satisfaction estimate.** CL is an input to satisfaction, not a measure of it.
- **No claim about what a partner's real alternatives are.** Only that they said something
  about alternatives.
- **No fairness verdict.** A voiced imbalance is one partner's account of the division of
  labor. The instrument does not adjudicate whether it is accurate.
- **No economic reading of the relationship.** The exchange vocabulary is a modeling choice
  in the theory, not a description of how partners experience each other.

## 3. Main empirical criticisms

- **Alternatives measure weakly.** In meta-analysis of the closely related investment model,
  quality of alternatives is the weakest of the predictors of commitment (Le & Agnew, 2003) —
  which is exactly the component people most want to read off a transcript.
- **Self-report circularity.** CL and CL-alt are assessed by asking people, and the answers
  are coloured by current satisfaction, so the "prediction" partly restates the outcome.
- **Exchange framing.** Costs–rewards vocabulary has been criticized as importing an economic
  model of intimacy, salient for who does which chores and poor for meaning, identity and love.
- **Static modeling.** The framework treats CL and CL-alt as relatively stable, while in
  practice they shift with mood, conflict, and the very conversation being coded.
- **Levinger's model is a framework, not a validated instrument**: it organizes findings
  rather than yielding measurements, and there is no established scoring procedure to apply.

## 4. Sources

- Kelley, H. H., & Thibaut, J. W. (1978). *Interpersonal Relations: A Theory of Interdependence*. Wiley.
- Le, B., & Agnew, C. R. (2003). Commitment and its theorized determinants: A meta-analysis of the investment model. *Personal Relationships, 10*(1), 37–57.
- Levinger, G. (1965). Marital cohesiveness and dissolution: An integrative review. *Journal of Marriage and the Family, 27*(1), 19–28.
- Levinger, G. (1976). A social psychological perspective on marital dissolution. *Journal of Social Issues, 32*(1), 21–47.
- Rusbult, C. E., & Van Lange, P. A. M. (2003). Interdependence, interaction, and relationships. *Annual Review of Psychology, 54*, 351–375.
- Thibaut, J. W., & Kelley, H. H. (1959). *The Social Psychology of Groups*. Wiley.
