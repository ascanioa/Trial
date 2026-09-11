"""40 - Bowen family systems theory.

The least operationalized framework here, so the module is deliberately conservative:
differentiation is never scored, mention of a third party is never read as triangulation,
and four of Bowen's eight concepts are reported as not implemented rather than approximated.
See reference/40-bowen-systems.md.
"""

from __future__ import annotations

from .. import lexicon as L
from ..indicators import ModuleResult, NotAssessable, RuledOut
from ..normalize import Transcript
from .base import dedupe, emit_per_speaker, scan

MODULE = "40-bowen-systems"
SRC = "Bowen (1978); Kerr & Bowen (1988)"

CULTURE_NOTE = (
    "In many family-centered and collectivist contexts, the involvement of extended family "
    "that this framework reads as fusion or triangulation is ordinary and functional. A "
    "lexical coder cannot tell those apart."
)


def code(tr: Transcript, lang: str) -> ModuleResult:
    res = ModuleResult(module=MODULE)
    dyad = tr.dyad
    if not dyad:
        return res

    triangulation = emit_per_speaker(
        res, tr, lang, dyad, L.TRIANGULATION,
        module=MODULE, indicator_id="bowen.triangulation",
        construct="Triangulation", theory_source=SRC,
        rationale=(
            "A third party is brought into the dyad's tension — invoked as ally, authority, "
            "confidant for this conflict, or witness."
        ),
        not_licensed=(
            "Does not establish that the third party did or said what is reported, or that "
            "they consented to the position. " + CULTURE_NOTE
        ),
    )
    triangulated_turns = {e.turn for i in triangulation for e in i.evidence}

    # Mentioning your mother is not triangulating. This is the module's main near-miss.
    mention = emit_per_speaker(
        res, tr, lang, dyad, L.THIRD_PARTY,
        module=MODULE, indicator_id="bowen.third_party_present",
        construct="Third party mentioned (not triangulation)", theory_source=SRC,
        rationale=(
            "A third party appears in the conversation as subject matter, without being "
            "recruited into the couple's tension as ally, authority or judge."
        ),
        not_licensed=(
            "Explicitly NOT triangulation. Talking about family, children or friends is "
            "ordinary content and carries no systemic implication on its own."
        ),
        exclude_turns=triangulated_turns,
    )

    emit_per_speaker(
        res, tr, lang, dyad, L.FUSION,
        module=MODULE, indicator_id="bowen.fusion",
        construct="Emotional fusion", theory_source=SRC,
        rationale=(
            "Separate emotional states are treated as impermissible: one partner's state is "
            "required to track the other's, or difference is framed as disloyalty."
        ),
        not_licensed=(
            "Does not measure either partner's differentiation of self, which this module "
            "never scores. " + CULTURE_NOTE
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.DIFFERENTIATED_STANCE,
        module=MODULE, indicator_id="bowen.differentiated_stance",
        construct="Differentiated stance (turn-level behavior)", theory_source=SRC,
        rationale=(
            "A turn that holds a position and maintains connection at the same time: "
            "disagreeing without withdrawing or attacking."
        ),
        not_licensed=(
            "A turn-level behavior, NOT a level of differentiation. Bowen's construct is a "
            "lifelong, cross-context characteristic; the instrument does not score it and "
            "does not describe either partner as more or less differentiated."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.CUTOFF,
        module=MODULE, indicator_id="bowen.cutoff",
        construct="Emotional cutoff (reported)", theory_source=SRC,
        rationale="A partner describes ending or sharply limiting contact with family of origin.",
        not_licensed=(
            "Codes a REPORTED estrangement. Bowen's explanatory claim — that cutoff manages "
            "unresolved fusion — is a theoretical commitment, not an observation. "
            "Estrangement can equally be a considered, protective decision."
        ),
        competing_reading=(
            "Reduced contact with a family of origin is frequently a deliberate and "
            "protective choice rather than a symptom of anything in this couple."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.MULTIGENERATIONAL,
        module=MODULE, indicator_id="bowen.multigenerational_framing",
        construct="Multigenerational framing invoked", theory_source=SRC,
        rationale="A partner invokes family-of-origin patterns to explain the present exchange.",
        not_licensed=(
            "Codes that the partners ARE USING this frame. It does not establish that a "
            "pattern is being transmitted across generations: the transcript contains no data "
            "on the prior generation."
        ),
    )

    found = {i.indicator_id for i in res.indicators if i.evidence}
    if mention and "bowen.triangulation" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Triangulation",
                basis=(
                    "Third parties appear in the conversation, but none is recruited into the "
                    "couple's tension: no third party is quoted as an ally, appealed to as an "
                    "authority, or positioned as a judge. Mention is not recruitment."
                ),
                counter_evidence=dedupe([e for i in mention for e in i.evidence])[:2],
            )
        )
    if "bowen.differentiated_stance" in found and "bowen.fusion" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Emotional fusion",
                basis=(
                    "Difference is tolerated in this exchange: a position is held without "
                    "requiring the partner to share the speaker's state, and disagreement is "
                    "not treated as disloyalty."
                ),
                counter_evidence=dedupe(
                    scan(tr, L.DIFFERENTIATED_STANCE, lang, speakers=dyad)
                )[:2],
            )
        )
    family_in_play = bool(found & {"bowen.third_party_present", "bowen.triangulation"})
    if family_in_play and "bowen.cutoff" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Emotional cutoff",
                basis=(
                    "Family and other third parties are part of this conversation, and "
                    "neither partner describes ending or sharply limiting contact with a "
                    "family of origin. Contact is live, whatever its quality."
                ),
                counter_evidence=dedupe(
                    scan(tr, L.THIRD_PARTY, lang, speakers=dyad)
                    + scan(tr, L.TRIANGULATION, lang, speakers=dyad)
                )[:2],
            )
        )
    if family_in_play and "bowen.multigenerational_framing" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Multigenerational framing",
                basis=(
                    "Family is discussed as present-day participants only. Neither partner "
                    "invokes a family-of-origin pattern to explain what is happening between "
                    "them — no 'you sound like your mother', no 'in my family we did X'."
                ),
                counter_evidence=dedupe(
                    scan(tr, L.THIRD_PARTY, lang, speakers=dyad)
                    + scan(tr, L.TRIANGULATION, lang, speakers=dyad)
                )[:2],
            )
        )

    if not found:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Bowen constructs generally",
                reason=(
                    "The exchange stays inside the dyad and the present: no third party, no "
                    "family of origin, and no demand that the partners share one emotional "
                    "state. This framework's constructs have no occasion here."
                ),
            )
        )

    res.not_assessable.extend([
        NotAssessable(
            module=MODULE,
            construct="Differentiation of self (as a level or score)",
            reason=(
                "Deliberately not assessed. Bowen described differentiation as a lifelong, "
                "cross-context characteristic, and the available measure (Skowron & "
                "Friedlander's DSI, 1998) is a 43-item questionnaire, not a behavioral code. "
                "Bowen held it could not be reliably assigned from short observation."
            ),
            measurement_layer="unmeasured",
        ),
        NotAssessable(
            module=MODULE,
            construct="Multigenerational transmission process",
            reason=(
                "Requires a multigenerational family history. A couple's conversation contains "
                "no data on the prior generation."
            ),
            measurement_layer="unmeasured",
        ),
        NotAssessable(
            module=MODULE,
            construct="Sibling position, societal emotional process, family projection process, nuclear family emotional system",
            reason=(
                "Not implemented. Birth-order effects on personality have very weak empirical "
                "support; the others operate at the level of the family unit over time or of "
                "society, and no text-only indicator for them is licensed by the theory."
            ),
            measurement_layer="unmeasured",
        ),
    ])
    res.open_questions.extend([
        "When this conflict happens, who else ends up hearing about it, and what part do they play?",
        "How did each partner's family of origin handle disagreement?",
    ])
    return res
