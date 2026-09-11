# 10 — Attachment: Bowlby, Ainsworth, Hazan & Shaver

**Unit of analysis:** behavioral strategies visible in this exchange.

**The hard constraint of this module:** it may use the vocabulary of attachment *strategies*.
It may never assign an attachment *style* to a person.

---

## 1. Why no style assignment

Bowlby (1969/1982) described attachment as a behavioral system regulating proximity to a
caregiver under threat. Ainsworth et al. (1978) operationalized individual differences in the
Strange Situation — a standardized 20-minute laboratory procedure with eight scripted
episodes, coded by trained raters on interactive behavior at reunion. Hazan & Shaver (1987)
extended the framework to adult romantic bonds, initially with a three-category self-report
measure; the field has since largely moved to two continuous dimensions, anxiety and
avoidance (Brennan, Clark & Shaver, 1998; Fraley, Waller & Brennan, 2000).

Every one of those measurements is either a standardized procedure or a validated
questionnaire, administered outside the interaction being studied. None of them is a
conversation transcript.

Further, the two main measurement traditions — the Adult Attachment Interview and
self-report romantic attachment scales — converge only weakly with each other (Roisman et
al., 2007). If two validated instruments built to measure the same construct agree that
poorly, a lexical reading of one conversation has no claim to measure it at all.

**Therefore:** this module codes *moves* — what a partner does when connection feels
threatened in this exchange. It never outputs "A is anxiously attached", "B is avoidant", or
any phrasing that assigns a person to a category, however hedged. A partner who deactivates
in this conversation may hyperactivate in another; strategies are context-sensitive and
partner-specific, and a single transcript cannot distinguish a strategy from a state.

## 2. Core constructs and text-observable indicators

### 2.1 Safe haven and secure base

Two functions of the attachment figure (Bowlby; Ainsworth):

- **Safe haven** — turning to the partner for comfort when distressed.
- **Secure base** — the partner's availability supporting exploration and autonomy.

| Indicator | Operational definition |
| --- | --- |
| `attachment.proximity_seeking` | A turn that seeks contact, reassurance, or presence: asking the partner to stay, come back, talk, hold; naming missing them; asking whether the pair is all right. |
| `attachment.safe_haven_response` | A turn that offers availability in response to distress: "I'm here", "we'll get through this", "what do you need", "take your time". |
| `attachment.secure_base_support` | A turn that supports the partner's autonomy or exploration without withdrawing connection. Rare in conflict transcripts; frequently `not_assessable`. |

### 2.2 Protest behavior

Bowlby's protest–despair–detachment sequence described a child's response to separation.
The text-observable analogue in adults is **protest**: escalated signaling aimed at
re-establishing responsiveness — "why won't you answer me", "do you even care", "say
something", "I'm right here".

`attachment.protest` codes the escalated bid. **Despair and detachment are not coded.**
They are longitudinal phases of a separation response, not utterances, and nothing in a
single conversation distinguishes detachment from disinterest, fatigue, or a bad day.

### 2.3 Secondary strategies: hyperactivating and deactivating

Mikulincer & Shaver's (2007/2016) terms for what happens when the primary bid does not work.

| Indicator | Operational definition | Discriminated from |
| --- | --- | --- |
| `attachment.hyperactivating` | Escalating the bid to force a response: repetition, testing ("if you really loved me"), ultimatum-as-probe, demands for immediate answer, threats to leave used to elicit reassurance. | **A direct request** — "please answer me" once is a request; the marker is escalation *after* non-response. |
| `attachment.deactivating` | Down-regulating the attachment signal: minimizing ("it's not a big deal"), self-reliance claims, topic shift away from the bond, withdrawal framed as not needing. | **Genuine disagreement about a topic**, and **a requested break** (see 20-gottman §1.2). |
| `attachment.self_reliance_claim` | Explicit claims of not needing the partner or of having always managed alone. Coded separately because it is the most distinctive deactivating marker in text. |

### 2.4 Sequence matters

The informative unit is **bid → response → adjustment**: what each partner does *after* the
other's move. A hyperactivating move following non-response, and the same words opening a
conversation, are different data. Where the transcript does not show the preceding bid, the
module says the sequence is incomplete rather than inferring it.

## 3. What this theory does not license concluding

- **No style, type, or category for either person.** Not "anxious", not "avoidant", not
  "secure", not "disorganized", not "leaning toward" any of them.
- **No childhood inference.** Nothing about either partner's parents, upbringing, or early
  caregiving. Adult romantic attachment is not a readout of infancy, and the transcript
  contains no developmental data whatsoever.
- **No pathology framing.** Hyperactivating and deactivating are regulation strategies, not
  disorders and not deficits. Both were adaptive in some caregiving environment.
- **No pairing claim.** The "anxious–avoidant trap" is a popular description, not a licensed
  inference from one exchange, and it requires the style assignment this module refuses.
- **No causal claim** that one partner's strategy caused the other's.

## 4. Main empirical criticisms

- **Categories vs. dimensions.** Taxometric work indicates adult attachment is better
  modeled as continuous dimensions than as types (Fraley & Waller, 1998), so any categorical
  output is a discretization the data do not support.
- **Weak convergence across instruments** between the AAI and self-report measures
  (Roisman et al., 2007) — evidence that "attachment" names more than one measured thing.
- **Moderate stability.** Adult attachment security is moderately stable at best and moves
  with relationship events (Fraley, 2002), which undercuts treating it as a fixed trait.
- **Relationship-specificity.** People show different patterns with different partners, so a
  global style is an aggregation that a single dyadic transcript cannot recover.
- **Cross-cultural validity.** Strange Situation distributions vary by culture, and the
  normative status of the "secure" category has been contested.

## 5. Sources

- Ainsworth, M. D. S., Blehar, M. C., Waters, E., & Wall, S. (1978). *Patterns of Attachment*. Erlbaum.
- Bowlby, J. (1969/1982). *Attachment and Loss, Vol. 1: Attachment*. Basic Books.
- Bowlby, J. (1973). *Attachment and Loss, Vol. 2: Separation*. Basic Books.
- Brennan, K. A., Clark, C. L., & Shaver, P. R. (1998). Self-report measurement of adult romantic attachment. In J. A. Simpson & W. S. Rholes (Eds.), *Attachment Theory and Close Relationships*. Guilford.
- Fraley, R. C. (2002). Attachment stability from infancy to adulthood. *Personality and Social Psychology Review, 6*(2), 123–151.
- Fraley, R. C., & Waller, N. G. (1998). Adult attachment patterns: A test of the typological model. In J. A. Simpson & W. S. Rholes (Eds.), *Attachment Theory and Close Relationships*. Guilford.
- Fraley, R. C., Waller, N. G., & Brennan, K. A. (2000). An item response theory analysis of self-report measures of adult attachment. *Journal of Personality and Social Psychology, 78*(2), 350–365.
- Hazan, C., & Shaver, P. (1987). Romantic love conceptualized as an attachment process. *Journal of Personality and Social Psychology, 52*(3), 511–524.
- Mikulincer, M., & Shaver, P. R. (2016). *Attachment in Adulthood* (2nd ed.). Guilford.
- Roisman, G. I., Holland, A., Fortuna, K., Fraley, R. C., Clausell, E., & Clarke, A. (2007). The Adult Attachment Interview and self-reports of attachment style. *Journal of Personality and Social Psychology, 92*(4), 678–697.
