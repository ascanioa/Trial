"""50 - Interdependence and cohesiveness: Kelley & Thibaut, Levinger.

Codes only what partners VOICE about costs, rewards, standards and alternatives. It computes
no outcomes, estimates no satisfaction, and emits no stability inference of any kind.
See reference/50-interdependence.md.
"""

from __future__ import annotations

from .. import lexicon as L
from ..indicators import ModuleResult, NotAssessable, RuledOut
from ..normalize import Transcript
from .base import dedupe, emit_per_speaker, scan

MODULE = "50-interdependence"
SRC_KT = "Thibaut & Kelley (1959); Kelley & Thibaut (1978)"
SRC_LEV = "Levinger (1965, 1976)"

NO_PREDICTION = (
    "Carries NO implication about whether this relationship will continue. Voicing this is a "
    "speech act inside a conversation, not a measurement of the underlying construct."
)


def code(tr: Transcript, lang: str) -> ModuleResult:
    res = ModuleResult(module=MODULE)
    dyad = tr.dyad
    if not dyad:
        return res

    emit_per_speaker(
        res, tr, lang, dyad, L.COST_REWARD,
        module=MODULE, indicator_id="interdependence.voiced_costs_rewards",
        construct="Costs and rewards voiced", theory_source=SRC_KT,
        rationale="A partner states what the relationship costs or gives them: effort, labor, money, time, or fairness.",
        not_licensed=(
            "Codes the claim, not its accuracy. The instrument does not adjudicate whether "
            "the division of labor described is real or fair. " + NO_PREDICTION
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.COMPARISON_LEVEL,
        module=MODULE, indicator_id="interdependence.comparison_level",
        construct="Comparison level (CL) voiced", theory_source=SRC_KT,
        rationale="A partner voices a standard for what a relationship should give them.",
        not_licensed=(
            "Satisfaction is NOT inferred from this. CL is one input to satisfaction in the "
            "theory, and a transcript contains neither the outcomes nor the standard with "
            "the precision the comparison would need. " + NO_PREDICTION
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.ALTERNATIVES,
        module=MODULE, indicator_id="interdependence.alternatives_voiced",
        construct="Alternatives (CL-alt) voiced", theory_source=SRC_KT,
        rationale="A partner refers to what is available outside the relationship, or to leaving.",
        not_licensed=(
            "This is NOT a measure of CL-alt and NOT a dissolution signal. A statement about "
            "alternatives made during conflict is a move inside the conflict. " + NO_PREDICTION
        ),
        competing_reading=(
            "Raising alternatives mid-argument may be protest aimed at getting a response, "
            "leverage, or a genuine appraisal. The text does not distinguish these, and "
            "treating it as an appraisal is the least supported of the three."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.PRO_RELATIONSHIP_TRANSFORMATION,
        module=MODULE, indicator_id="interdependence.pro_relationship_transformation",
        construct="Pro-relationship transformation of motivation", theory_source=SRC_KT,
        rationale=(
            "A partner sets aside an immediate preference for the pair or for the other — "
            "yielding a choice, absorbing a cost, or proposing a joint solution."
        ),
        not_licensed=(
            "The transformation itself is an internal process and is unmeasured. What is "
            "coded is the behavior consistent with it."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.SELF_INTEREST_STANCE,
        module=MODULE, indicator_id="interdependence.self_interest_stance",
        construct="Self-interest stance", theory_source=SRC_KT,
        rationale="A turn holding to individual outcome without reference to the pair's.",
        not_licensed=(
            "Not a moral judgment. Holding a position is not a failure, and the theory treats "
            "the given matrix as the ordinary starting point, not as a defect."
        ),
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.ATTRACTIONS,
        module=MODULE, indicator_id="interdependence.attractions_voiced",
        construct="Attractions voiced (Levinger)", theory_source=SRC_LEV,
        rationale="Rewards of the relationship stated directly: affection, companionship, being known.",
        not_licensed=NO_PREDICTION,
    )
    emit_per_speaker(
        res, tr, lang, dyad, L.BARRIERS,
        module=MODULE, indicator_id="interdependence.barriers_voiced",
        construct="Barriers voiced (Levinger)", theory_source=SRC_LEV,
        rationale="Restraints against leaving stated directly: children, finances, family opinion, years invested.",
        not_licensed=(
            "The cohesiveness model's balance of attractions, barriers and alternatives is "
            "NOT computed. Doing so would be a dissolution prediction in different vocabulary. "
            + NO_PREDICTION
        ),
    )

    found = {i.indicator_id for i in res.indicators if i.evidence}
    voiced_forces = [
        n for n, k in (
            ("attractions", "interdependence.attractions_voiced"),
            ("barriers", "interdependence.barriers_voiced"),
            ("alternatives", "interdependence.alternatives_voiced"),
        ) if k in found
    ]
    if voiced_forces:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Cohesiveness (the balance of attractions, barriers and alternatives)",
                reason=(
                    "Deliberately not computed. The report lists which forces the partners "
                    f"voiced ({', '.join(voiced_forces)}) and quotes them; weighing them into "
                    "a balance would be a stability prediction under another name."
                ),
                measurement_layer="unmeasured",
            )
        )

    if "interdependence.voiced_costs_rewards" in found and "interdependence.comparison_level" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Comparison level (CL) voiced",
                basis=(
                    "Costs and contributions are disputed, but neither partner invokes a "
                    "standard for what a relationship ought to give them — no appeal to what "
                    "they deserve, expected, or see in other couples."
                ),
                counter_evidence=dedupe(scan(tr, L.COST_REWARD, lang, speakers=dyad))[:2],
            )
        )
    if "interdependence.voiced_costs_rewards" in found and "interdependence.alternatives_voiced" not in found:
        res.ruled_out.append(
            RuledOut(
                module=MODULE,
                construct="Alternatives (CL-alt) voiced",
                basis=(
                    "The dispute is about the terms inside the relationship. Neither partner "
                    "raises being better off alone, someone else, or leaving — the exchange "
                    "stays inside the pair even while contesting its costs."
                ),
                counter_evidence=dedupe(scan(tr, L.COST_REWARD, lang, speakers=dyad))[:2],
            )
        )
    if not found:
        res.not_assessable.append(
            NotAssessable(
                module=MODULE,
                construct="Interdependence constructs generally",
                reason=(
                    "Neither partner voices anything about costs, rewards, fairness, standards "
                    "or alternatives. This module codes only what is said about those, so it "
                    "has nothing to work from here."
                ),
            )
        )

    res.not_assessable.append(
        NotAssessable(
            module=MODULE,
            construct="Actual outcomes, satisfaction, CL and CL-alt as quantities",
            reason=(
                "These are assessed with questionnaires administered to each partner "
                "separately. Nothing in a transcript measures them, and what partners say "
                "during conflict is coloured by the conflict."
            ),
            measurement_layer="unmeasured",
        )
    )
    res.open_questions.extend([
        "How would each partner describe the division of work if asked separately, on a calm day?",
        "What does each partner think the other most values about the relationship?",
    ])
    return res
