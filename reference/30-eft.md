# 30 — Emotionally Focused Therapy: Johnson, Greenberg

**Unit of analysis: the cycle, not the person.**

This is the module's defining constraint. EFT's central move is to externalize the pattern —
the problem is the cycle, not either partner. A module output that names a culprit has
misapplied the theory, not merely been impolite.

---

## 1. The negative interaction cycle

A self-maintaining sequence in which each partner's coping move triggers the other's.

| Cycle | Positions | Text signature |
| --- | --- | --- |
| **Pursue–withdraw** | One partner escalates to get engagement; the other withdraws to lower intensity | Escalating bids, protest, criticism from one side; minimizing, topic shift, disengagement from the other |
| **Withdraw–withdraw** | Both partners disengage | Short turns, no repair attempts, topic avoidance on both sides, long silences noted in the transcript |
| **Attack–attack** | Both escalate | Mutual criticism, counter-attack, escalating volume markers on both sides |

`eft.cycle` carries `pattern`, each partner's `position`, and a **symmetric statement**.

**Symmetry rules, enforced in code:**
- No "who started it" verdict. Where a transcript begins is an artifact of recording, not a
  causal origin. The instrument does not name a first mover even when the first turn is
  aggressive.
- Both positions are described in the same register, with the same amount of text.
- Neither position is described as a reaction *to a person*; both are described as moves
  *within a pattern*.
- Where one partner's position is clear and the other's is not, the output says so rather
  than inferring the complement.

### 1.1 Provenance of pursue–withdraw

The pursue–withdraw (demand–withdraw) pattern is not originally EFT's: it was developed and
measured in behavioral and social-psychological research on couples (Christensen & Sullaway's
Communication Patterns Questionnaire, 1984; Christensen & Heavey, 1990). EFT adopts it and
reads it through attachment. The module cites it accordingly rather than attributing it to
EFT alone.

## 2. Primary and secondary emotions

From Greenberg's experiential tradition (Greenberg & Safran, 1987; Greenberg, 2002).

- **Secondary reactive emotions** — what is expressed: anger, frustration, irritation,
  resentment, contempt-adjacent hostility.
- **Primary attachment emotions** — what the theory holds lies underneath: fear, shame,
  loneliness, sadness, feeling unwanted or not enough.

| Indicator | Definition |
| --- | --- |
| `eft.secondary_emotion` | The speaker expresses reactive emotion. `observed` — the words are there. |
| `eft.primary_emotion_voiced` | The speaker **names** a primary emotion themselves ("I was scared", "I feel invisible"). `observed`. |
| `eft.primary_emotion_inferred` | A primary emotion is **hypothesized** beneath expressed anger without the speaker naming it. |

**`eft.primary_emotion_inferred` is the most inference-heavy code in this repository.** Rules:

1. It is always `inference_level: inferred` and therefore capped at confidence 0.65.
2. It requires a *textual hook* — an attachment-relevant content word in the same or an
   adjacent turn (alone, waiting, notice, matter, care, there for me). Anger alone is not a
   hook.
3. It is phrased as a hypothesis to be checked with the speaker, never as a discovery about
   them. The clinical move in EFT is to *ask*, and the instrument is not in a position to ask.
4. If no hook is present, the module reports "the primary emotion under this anger is not
   visible in the text" — a stated gap, not an inference.

The theory's claim that anger is secondary to a primary attachment emotion is a *model*, not
an observation. It is not falsifiable from a transcript, and the module does not treat it as
confirmed by the transcript it was used to read.

## 3. Attachment injury

Johnson, Makinen & Millikin (2001): a specific incident of abandonment or betrayal at a
moment of acute need, which becomes a recurring impasse and blocks repair until addressed.

`eft.attachment_injury_referenced` codes a **reference** to such an incident: a named past
event, invoked as still-live, in which the partner was unavailable at a moment of need
("when I was in the hospital and you didn't come", "I stopped counting on you after that").

What is coded is that **an injury is being referenced in this conversation** — not that an
injury occurred, not that the account is accurate, and not that it is unresolved as a
clinical matter. Both partners' accounts of the same event usually differ, and the
transcript contains one framing of it at most.

## 4. What this theory does not license concluding

- **No blame, no first cause, no "who is the problem".**
- **No claim about what a partner "really" feels.** Inferred primary emotion is a hypothesis
  for the partners to confirm or reject, and they are the authority on it.
- **No stage or progress claim.** EFT's stages and steps describe a therapy process with a
  therapist present, not a conversation.
- **No claim that an attachment injury is real, unresolved, or the cause of the cycle.**
- **No treatment recommendation.** The instrument does not prescribe EFT, or any therapy.

## 5. Main empirical criticisms

- **Developer allegiance.** Much of the early efficacy evidence comes from trials conducted
  by the model's developers; the influential Johnson et al. (1999) meta-analysis rests on a
  small number of small trials, and its effect size has been described as optimistic.
- **Small samples, selective populations.** Trials have tended to use motivated,
  non-violent, mildly-to-moderately distressed couples, limiting generalization.
- **Construct testability.** "Primary emotion beneath secondary emotion" is difficult to
  falsify: absence of the primary emotion can always be attributed to defense. A framework
  that cannot fail an observation should be used cautiously as a coding scheme, which is why
  the inference cap in §2 exists.
- **Attachment-theoretic grounding is contested.** Whether adult couple distress is
  usefully explained by attachment processes specifically, rather than by general emotion
  regulation or learning processes, remains debated.

## 6. Sources

- Christensen, A., & Heavey, C. L. (1990). Gender and social structure in the demand/withdraw pattern of marital conflict. *Journal of Personality and Social Psychology, 59*(1), 73–81.
- Greenberg, L. S. (2002). *Emotion-Focused Therapy: Coaching Clients to Work Through Their Feelings*. APA.
- Greenberg, L. S., & Johnson, S. M. (1988). *Emotionally Focused Therapy for Couples*. Guilford.
- Greenberg, L. S., & Safran, J. D. (1987). *Emotion in Psychotherapy*. Guilford.
- Johnson, S. M. (2004). *The Practice of Emotionally Focused Couple Therapy* (2nd ed.). Brunner-Routledge.
- Johnson, S. M., Hunsley, J., Greenberg, L., & Schindler, D. (1999). Emotionally focused couples therapy: Status and challenges. *Clinical Psychology: Science and Practice, 6*(1), 67–79.
- Johnson, S. M., Makinen, J. A., & Millikin, J. W. (2001). Attachment injuries in couple relationships. *Journal of Marital and Family Therapy, 27*(2), 145–155.
