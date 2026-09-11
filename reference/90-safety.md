# 90 — Safety gate

**This module runs first, before any pattern analysis. Its output can halt the run.**

It is not a module among modules. It is a precondition on whether the other modules are
applicable at all.

---

## 1. Why the gate exists

Every conflict framework in this repository — Gottman's Four Horsemen, EFT's negative cycle,
Bowen's fusion, behavioral coercion cycles — assumes **two partners with roughly symmetric
power, each of whom can influence and be influenced by the other**. That assumption is what
licenses symmetric, both-contribute language.

Where one partner controls the other through violence, threat, surveillance, economic
control, or isolation, the assumption fails. Applying cycle language there is not merely
inaccurate, it is harmful: it reframes coercion as a mutual dynamic, distributes
responsibility to the person being harmed, and reproduces what the controlling partner
already says. Michael P. Johnson's typology (1995, 2008) distinguishes *situational couple
violence* from *intimate terrorism* precisely because conflating them makes both invisible;
Stark (2007) describes coercive control as a liberty harm whose components are individually
non-violent and only legible as a pattern. Clinical practice guidance is correspondingly
explicit that conjoint conflict-focused work is contraindicated where coercive violence is
present (Bograd & Mederos, 1999).

So: **the gate does not "add a warning" to the standard analysis. It replaces it.**

## 2. Screening categories

Screened before any other coding. Categories follow the coercive-control domains described
in the Duluth Power and Control model (Pence & Paymar, 1993) and Stark (2007).

| Category | Text-observable markers |
| --- | --- |
| **Threat** | Explicit or conditional threats of harm to the partner, self, children, pets, or property; threats to expose, deport, or take children |
| **Physical violence or aftermath** | Reference to hitting, pushing, grabbing, choking, restraining, throwing objects at a person; injuries; "the last time you put me in the wall" |
| **Intimidation** | Displays intended to frighten — punching walls, breaking things, blocking exits, looming, weapon references |
| **Monitoring / surveillance** | Checking phone or messages, location tracking, demanding account access, accounting for every hour, showing up to verify |
| **Financial control** | Withholding money, controlling all accounts, forbidding work, requiring receipts or permission to spend, confiscating earnings |
| **Isolation** | Restricting contact with family, friends, or support; controlling movement; framing outside relationships as betrayal |
| **Sexual coercion** | Pressure, obligation framing, or force regarding sex; consent overridden or treated as owed |
| **Expressed fear** | One partner states fear of the other, of their reaction, or describes managing behavior to avoid a reaction ("walking on eggshells") |

### 2.1 Speaker asymmetry is part of the signal

Record **who** the marker is directed at. A marker voiced by A about B's behavior toward A,
and the same words voiced as a mutual exchange, are different data. The gate does not
attempt to adjudicate which partner is the aggressor — it reports the direction of the
markers as stated in the text, and where the transcript is directionally ambiguous it says so.

### 2.2 What the gate does not do

- It does **not** determine that abuse occurred. A transcript cannot establish that.
- It does **not** classify into Johnson's types. That requires history and context the text lacks.
- It does **not** produce a risk score, lethality assessment, or danger rating. Validated
  instruments for that (e.g. structured danger assessment) require a trained interviewer and
  information not present in a conversation transcript. Inventing a numeric risk output here
  would be both unlicensed and dangerous.
- It does **not** counsel the user to leave, stay, confront, or document.

## 3. Gate behavior

```
run safety screen
   |
   +-- no markers ------------------> proceed to modules 10-60, standard report
   |
   +-- markers present -------------> HALT. Emit safety-only report.
                                      Modules 10-60 are NOT run.
                                      analysis.json: safety_gate.tripped = true,
                                      safety_gate.markers = what was observed,
                                      indicators = [] (EMPTY).
```

**Markers go in `safety_gate.markers`, never in `indicators`.** Two reasons. A marker
carries `direction` and `ambiguous`, which an indicator record has no field for, and
direction is the part that must not be lost. And an empty `indicators` array makes "no
pattern analysis was emitted" a structural property of the document rather than a
convention a reader has to verify construct by construct.

When the gate trips, the **only** output is:

1. **What was observed** — the markers, quoted verbatim, with turn numbers and direction.
2. **Why the standard analysis does not apply** — the symmetry assumption, stated plainly,
   in one short paragraph. Not hedged, not buried.
3. **A recommendation to consult a qualified professional or local support service**, framed
   as information rather than instruction, without directing a specific course of action.

No cycle description. No Four Horsemen coding. No "both partners contribute". No competing
readings that normalize the markers. The "Ruled out" section is omitted, because ruling
constructs in or out is exactly the analysis that has been suspended.

### 3.1 Ambiguity policy

The gate is deliberately **asymmetric in its errors**: a false positive costs a withheld
analysis, a false negative costs a harmful one. Where a marker is genuinely ambiguous
(hyperbole, a joke, a quoted third party, a movie plot), the gate trips and *says it is
ambiguous*, naming the competing reading. It does not silently resolve ambiguity toward
"probably fine".

Two bounded exceptions, because a gate that trips on everything gets ignored:
- **Reported speech about a third party** ("my brother threw a chair at his wife") is recorded
  but does not trip the gate, unless it is used as a threat or the dyad is implicated.
- **Non-violent conventional metaphor** ("this is killing me", "me muero de hambre",
  "I could murder a coffee") does not trip the gate. Idiom lists are maintained in
  `src/couples_analyst/lexicon.py` and are language-specific.

## 4. Adversarial use

The agent declines and explains why, when the request is to:

- build a case against a partner, or gather evidence for a dispute, custody matter, or legal proceeding;
- win, settle, or score an argument;
- analyze a partner covertly, or profile someone who has not been told;
- obtain a diagnosis, label, or "what's wrong with them" for a third party.

The refusal is short, non-moralizing, states the reason (the instrument codes dyadic
interaction descriptively; used as ammunition it produces exactly the asymmetric,
blame-assigning output it is built not to produce), and names what the tool can do instead
— e.g. a symmetric description both partners could read.

## 5. Minors

If the transcript indicates a romantic or sexual relationship involving a minor, the agent
stops and does not analyze. It does not code, summarize, or excerpt the content. This is
unconditional and is not subject to the ambiguity policy in §3.1 — it halts on uncertainty.
(Children *mentioned* in an adult couple's conversation are not this case; they are ordinary
transcript content, and are handled as possible triangulation material in `40-bowen-systems.md`.)

## 6. Consent

Both partners should know the conversation is being analyzed. The README states this and the
report carries it as a standing note. The agent does not verify consent — it cannot — but it
does not present covert analysis as a supported use, and §4 covers requests that are
explicitly covert.

## 7. What this module does not license concluding

- That a relationship is or is not abusive.
- That a partner is or is not dangerous, or that the markers are or are not "serious".
- That the absence of markers means the relationship is safe. A transcript is a sample;
  many couples do not discuss controlling behavior in front of a recorder, and one
  conversation cannot establish absence. The report states this explicitly whenever the
  gate does *not* trip.

## 8. Main empirical criticisms

- **Typology boundaries are contested.** Johnson's distinction between situational couple
  violence and intimate terrorism is influential but its measurement — usually by control
  scales applied retrospectively — is debated, and samples drawn from shelters vs. community
  surveys yield different type distributions.
- **Gender symmetry debate.** Survey instruments (notably the Conflict Tactics Scales,
  Straus, 1979) report near-symmetric rates of partner violence, while agency and injury data
  do not. Much of the disagreement is attributed to the CTS counting acts without context,
  motive, or consequence. This instrument takes no position, and codes no rates at all.
- **Screening validity.** Screening for IPV from *conversation text alone* has, to our
  knowledge, no validated instrument behind it. The categories above are drawn from clinical
  and advocacy frameworks, not from a validated text classifier. This gate is therefore a
  conservative heuristic, not a measurement, and is documented as such in the README.

## Sources

- Bograd, M., & Mederos, F. (1999). Battering and couples therapy: Universal screening and selection of treatment modality. *Journal of Marital and Family Therapy, 25*(3), 291–312.
- Johnson, M. P. (1995). Patriarchal terrorism and common couple violence: Two forms of violence against women. *Journal of Marriage and the Family, 57*(2), 283–294.
- Johnson, M. P. (2008). *A Typology of Domestic Violence*. Northeastern University Press.
- Pence, E., & Paymar, M. (1993). *Education Groups for Men Who Batter: The Duluth Model*. Springer Publishing.
- Stark, E. (2007). *Coercive Control: How Men Entrap Women in Personal Life*. Oxford University Press.
- Straus, M. A. (1979). Measuring intrafamily conflict and violence: The Conflict Tactics (CT) Scales. *Journal of Marriage and the Family, 41*(1), 75–88.
