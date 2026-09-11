"""30 - Emotionally Focused Therapy: the cycle is the unit of analysis.

Output is symmetric by construction. There is no "who started it" verdict anywhere in this
module: where a transcript begins is an artifact of recording, not a causal origin.
See reference/30-eft.md.
"""

from __future__ import annotations

from .. import lexicon as L
from ..indicators import Evidence, Indicator, ModuleResult, NotAssessable, RuledOut
from ..normalize import Transcript
from .base import dedupe, emit, emit_per_speaker, matches, scan, turn_hits

MODULE = "30-eft"
SRC_JOHNSON = "Johnson (2004); Greenberg & Johnson (1988)"
SRC_GREENBERG = "Greenberg & Safran (1987); Greenberg (2002)"
SRC_INJURY = "Johnson, Makinen & Millikin (2001)"
SRC_DW = "Christensen & Heavey (1990); Christensen & Sullaway (1984)"

# Attachment-relevant content words that license hypothesizing a primary emotion under
# expressed anger (reference/30-eft.md sec. 2, rule 2). Anger alone is not a hook.
HOOK = {
    "en": [
        r"\b(?:alone|lonely|waiting|notice|noticed|matter|care|there for me|left me|"
        r"shut out|invisible|ignored|abandoned|not enough|reach you)\b"
    ],
    "es": [
        r"\b(?:sol[oa]|soledad|esperando|notas|te importa|importo|estar ahi|me dejaste|"
        r"me cierras|invisible|ignorad[oa]|abandonad[oa]|no soy suficiente|llegar a ti)\b"
    ],
}

POSITION_LABEL = {
    "pursuing": {"en": "pursuing", "es": "en posición de búsqueda"},
    "withdrawing": {"en": "withdrawing", "es": "en posición de retirada"},
    "attacking": {"en": "escalating", "es": "en escalada"},
    "unclear": {"en": "not clearly positioned in the text", "es": "sin posición clara en el texto"},
}


def _position_scores(tr: Transcript, lang: str, spk: str) -> dict[str, int]:
    pursue = sum(
        len(scan(tr, g, lang, speakers=[spk]))
        for g in (L.PROTEST, L.PROXIMITY_SEEKING, L.HYPERACTIVATING, L.CHANGE_DEMAND)
    )
    withdraw = sum(
        len(scan(tr, g, lang, speakers=[spk]))
        for g in (L.DEACTIVATING, L.SELF_RELIANCE_CLAIM, L.TOPIC_SHIFT, L.STONEWALL_EXPLICIT)
    )
    withdraw += sum(
        1 for t in tr.turns_of(spk)
        if matches(t, L.STONEWALL_MINIMAL, lang) and not matches(t, L.POSITIVE_AFFECT, lang)
    )
    attack = sum(
        len(scan(tr, g, lang, speakers=[spk]))
        for g in (L.CONTEMPT, L.TRAIT_ATTRIBUTION, L.GLOBAL_QUANTIFIER)
    )
    return {"pursuing": pursue, "withdrawing": withdraw, "attacking": attack}


def _position(scores: dict[str, int]) -> str:
    top = max(scores, key=lambda k: scores[k])
    if scores[top] < 2:
        return "unclear"
    # A tie between two positions is alternation, not a winner-take-all call.
    if sorted(scores.values())[-1] == sorted(scores.values())[-2]:
        return "alternating"
    return top


def code(tr: Transcript, lang: str) -> ModuleResult:
    res = ModuleResult(module=MODULE)
    dyad = tr.dyad
    if len(dyad) < 2:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Negative interaction cycle",
                reason="A cycle needs two participants; this transcript has fewer.",
            )
        )
        return res
    a, b = dyad[0], dyad[1]

    # ------------------------------------------------------------------- the cycle
    sa, sb = _position_scores(tr, lang, a), _position_scores(tr, lang, b)
    pa, pb = _position(sa), _position(sb)
    pair = {pa, pb}
    if pair == {"pursuing", "withdrawing"}:
        pattern = "pursue_withdraw"
    elif pa == pb == "withdrawing":
        pattern = "withdraw_withdraw"
    elif pa == pb == "attacking" or pair == {"attacking", "pursuing"}:
        pattern = "attack_attack" if pa == pb else "mixed"
    elif "unclear" in pair and len(pair) > 1:
        pattern = "mixed"
    elif pa == "unclear" and pb == "unclear":
        pattern = "no_clear_cycle"
    else:
        pattern = "mixed"

    # Evidence is gathered per speaker and capped equally. A cycle description that quotes
    # one partner four times and the other never is not symmetric, whatever its wording says.
    per_speaker: dict[str, list[Evidence]] = {}
    for spk, pos in ((a, pa), (b, pb)):
        groups = {
            "pursuing": (L.PROTEST, L.HYPERACTIVATING, L.PROXIMITY_SEEKING, L.CHANGE_DEMAND),
            "withdrawing": (L.DEACTIVATING, L.SELF_RELIANCE_CLAIM, L.TOPIC_SHIFT,
                            L.STONEWALL_EXPLICIT),
            "attacking": (L.CONTEMPT, L.TRAIT_ATTRIBUTION, L.GLOBAL_QUANTIFIER),
            "alternating": (L.PROTEST, L.DEACTIVATING, L.CONTEMPT, L.GLOBAL_QUANTIFIER),
        }.get(pos, ())
        evs: list[Evidence] = []
        for g in groups:
            evs.extend(scan(tr, g, lang, speakers=[spk]))
        if not evs and pos == "withdrawing":
            # Withdrawal often shows up as minimal turns rather than as any phrase.
            evs = [
                Evidence.from_turn(t, t.text)
                for t in tr.turns_of(spk)
                if matches(t, L.STONEWALL_MINIMAL, lang)
            ]
        per_speaker[spk] = dedupe(evs)[:3]

    cycle_ev = [e for spk in (a, b) for e in per_speaker[spk]]
    one_sided = bool(per_speaker[a]) != bool(per_speaker[b])

    if pattern == "no_clear_cycle":
        statement = (
            "No negative interaction cycle is visible in this transcript. Neither partner's "
            "turns settle into a consistent position, and a cycle is a repeating sequence, "
            "not a single exchange."
            if lang == "en" else
            "No se observa un ciclo de interacción negativa en esta transcripción. Ninguna de "
            "las dos partes sostiene una posición consistente, y un ciclo es una secuencia que "
            "se repite, no un intercambio aislado."
        )
    else:
        la = POSITION_LABEL.get(pa, POSITION_LABEL["unclear"])[lang]
        lb = POSITION_LABEL.get(pb, POSITION_LABEL["unclear"])[lang]
        if lang == "es":
            statement = (
                f"En este intercambio, {a} aparece {la} y {b} aparece {lb}. Cada movimiento "
                f"vuelve más probable el del otro: la posición de {a} hace que la de {b} "
                f"resulte más necesaria, y la de {b} hace lo mismo con la de {a}. Ninguna de "
                "las dos inicia el patrón; el punto donde empieza la transcripción no marca "
                "un origen."
            )
        else:
            statement = (
                f"In this exchange {a} appears {la} and {b} appears {lb}. Each move makes the "
                f"other's more likely: {a}'s position makes {b}'s feel more necessary, and "
                f"{b}'s does the same for {a}'s. Neither partner starts the pattern; where "
                "the transcript begins is not an origin."
            )

    conf = 0.0
    if pattern != "no_clear_cycle":
        n = len(cycle_ev)
        conf = 0.85 if n >= 3 else (0.72 if n == 2 else 0.55)
        conf *= 0.8  # a cycle is a repeating sequence read from one sample
        if "unclear" in pair or "alternating" in pair:
            conf *= 0.85
        if one_sided:
            # One partner's position rests on evidence the other's does not have.
            conf *= 0.85
        if len(tr.turns) < 8:
            conf *= 0.85
    if pattern != "no_clear_cycle" and one_sided:
        quiet = a if not per_speaker[a] else b
        addendum = (
            f" Note that {quiet}'s position is read from the shape of the exchange rather "
            f"than from any turn quoted here, so it rests on weaker evidence than {a if quiet == b else b}'s."
            if lang == "en" else
            f" Conviene notar que la posición de {quiet} se infiere de la forma del "
            f"intercambio y no de ningún turno citado, por lo que se apoya en evidencia más "
            f"débil que la de {a if quiet == b else b}."
        )
        statement += addendum

    res.cycle = {
        "pattern": pattern,
        "positions": {"A": pa if a == "A" else pb, "B": pb if b == "B" else pa},
        "symmetric_statement": statement,
        "confidence": round(conf, 3),
        "evidence": [e.to_json() for e in cycle_ev],
    }

    # -------------------------------------------------------------------- emotions
    emit_per_speaker(
        res, tr, lang, dyad, L.SECONDARY_EMOTION,
        module=MODULE, indicator_id="eft.secondary_emotion",
        construct="Secondary reactive emotion", theory_source=SRC_GREENBERG,
        rationale="Reactive emotion expressed on the surface of the exchange.",
        not_licensed=(
            "'Secondary' is a position in a theoretical model, not an observation. It does "
            "not mean the emotion is less real or less important."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.PRIMARY_EMOTION,
        module=MODULE, indicator_id="eft.primary_emotion_voiced",
        construct="Primary attachment emotion, voiced by the speaker", theory_source=SRC_GREENBERG,
        rationale="The speaker names a primary attachment emotion themselves.",
        not_licensed="The speaker's own words; not an interpretation and not to be re-read as something else.",
    )

    # The most inference-heavy code in the repository: capped, hook-gated, phrased as a
    # hypothesis for the partners to confirm or reject.
    voiced = {i.speaker for i in res.indicators
              if i.indicator_id == "eft.primary_emotion_voiced" and i.evidence}
    for spk in dyad:
        if spk in voiced:
            continue
        anger = scan(tr, L.SECONDARY_EMOTION, lang, speakers=[spk])
        if not anger:
            continue
        hooks = scan(tr, HOOK, lang, speakers=[spk])
        if not hooks:
            res.not_assessable.append(
                NotAssessable(
                    module=MODULE,
                    construct=f"Primary emotion beneath {spk}'s expressed anger",
                    reason=(
                        "Anger is expressed, but nothing in the text points to what might sit "
                        "under it. The model says a primary attachment emotion is there; the "
                        "transcript does not show one, and inventing it would be unlicensed."
                    ),
                    measurement_layer="unmeasured",
                )
            )
            continue
        emit(
            res,
            Indicator(
                indicator_id="eft.primary_emotion_inferred",
                module=MODULE,
                construct="Possible primary emotion beneath expressed anger (hypothesis)",
                theory_source=SRC_GREENBERG,
                unit="speaker",
                speaker=spk,
                evidence=dedupe(anger[:2] + hooks[:2]),
                inference_level="inferred",
                rationale=(
                    "Anger is expressed alongside attachment-relevant content (being alone, "
                    "unnoticed, or not mattering). EFT would treat the anger as secondary to a "
                    "primary emotion of that kind. This is a hypothesis to put to the speaker, "
                    "not a finding about them — the clinical move is to ask, and this "
                    "instrument cannot ask."
                ),
                not_licensed=(
                    "Does not establish what the speaker feels. The model's claim that anger "
                    "is secondary to a primary attachment emotion is not falsifiable from a "
                    "transcript and is not confirmed by the transcript it was used to read."
                ),
                competing_reading=(
                    "The anger may be exactly what it appears to be — a response to the "
                    "situation under discussion — with nothing underneath it that the speaker "
                    "would recognize."
                ),
            ),
            transcript_turns=len(tr.turns),
        )

    emit_per_speaker(
        res, tr, lang, dyad, L.ATTACHMENT_INJURY,
        module=MODULE, indicator_id="eft.attachment_injury_referenced",
        construct="Attachment injury referenced", theory_source=SRC_INJURY,
        rationale=(
            "A past moment of need in which the partner is described as unavailable is "
            "invoked as still live in this conversation."
        ),
        not_licensed=(
            "Codes that an injury is being REFERENCED, not that one occurred, not that this "
            "account is accurate, and not that it is clinically unresolved. Partners' accounts "
            "of the same event usually differ and only one framing appears here."
        ),
        competing_reading=(
            "Raising a past event during conflict can be argumentative leverage rather than a "
            "live injury; the text does not distinguish these."
        ),
    )

    # ------------------------------------------------------------------ ruled out
    found = {i.indicator_id for i in res.indicators if i.evidence}
    if "eft.secondary_emotion" in found and "eft.primary_emotion_voiced" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Primary attachment emotion voiced directly",
                basis=(
                    "Reactive emotion is expressed, but neither partner names fear, shame, "
                    "loneliness or feeling unwanted in their own words. The exchange stays at "
                    "the secondary level throughout."
                ),
                counter_evidence=dedupe(scan(tr, L.SECONDARY_EMOTION, lang, speakers=dyad))[:2],
            )
        )
    if pattern != "no_clear_cycle" and "eft.attachment_injury_referenced" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Attachment injury",
                basis=(
                    "The conflict runs on a current issue. No past moment of unavailability at "
                    "a point of need is invoked, which is what an attachment injury reference "
                    "would look like in text."
                ),
                counter_evidence=cycle_ev[:2],
            )
        )
    if pattern == "no_clear_cycle":
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Negative interaction cycle",
                reason=(
                    "No sustained positions are visible. A cycle is a repeating sequence, and "
                    "one short exchange may simply not contain enough of it."
                ),
            )
        )

    res.competing_readings.append(
        {
            "reading": (
                "The positions may be topic-specific rather than a cycle: partners often "
                "pursue on one subject and withdraw on another, and this transcript covers one "
                "subject."
                if lang == "en" else
                "Las posiciones pueden depender del tema y no constituir un ciclo: es común "
                "buscar en un asunto y retirarse en otro, y esta transcripción cubre un solo "
                "asunto."
            ),
            "applies_to": ["eft.cycle"],
            "discriminating_data": (
                "The same pair discussing two or three different disagreements. A cycle "
                "reproduces across topics; a topic-specific position does not."
                if lang == "en" else
                "La misma pareja hablando de dos o tres desacuerdos distintos. Un ciclo se "
                "reproduce entre temas; una posición ligada al tema, no."
            ),
        }
    )
    res.open_questions.extend([
        "What does each partner believe the other is trying to do when the pattern starts?",
        "What does each partner most fear the other will conclude about them in that moment?",
        "Has either partner seen the other step out of this sequence, and what did that look like?",
    ])
    return res
