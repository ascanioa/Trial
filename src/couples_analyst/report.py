"""Markdown report generation, in the transcript's own language (en / es).

Section order is fixed by the output contract: what the analysis cannot tell you comes
FIRST, not last, and "Ruled out" is mandatory. Construct names keep their canonical English
form with a translation on first use, so analysis.json stays language-invariant while the
prose does not.
"""

from __future__ import annotations

from typing import Any

from .safety import CATEGORY_LABEL

T = {
    "title": {"en": "Conversation analysis", "es": "Análisis de la conversación"},
    "subtitle": {
        "en": "Descriptive coding of one transcript. Not a diagnosis, not a clinical "
              "assessment, not a prediction.",
        "es": "Codificación descriptiva de una transcripción. No es un diagnóstico, ni una "
              "evaluación clínica, ni una predicción.",
    },
    "cannot": {"en": "1. What this analysis cannot tell you",
               "es": "1. Lo que este análisis no puede decirte"},
    "cycle": {"en": "2. Interaction cycle", "es": "2. Ciclo de interacción"},
    "indicators": {"en": "3. Coded indicators by module",
                   "es": "3. Indicadores codificados por módulo"},
    "ruled_out": {"en": "4. Ruled out", "es": "4. Descartado"},
    "competing": {"en": "5. Competing readings", "es": "5. Lecturas alternativas"},
    "open_q": {"en": "6. Open questions", "es": "6. Preguntas abiertas"},
    "insufficient": {"en": "Insufficient evidence", "es": "Evidencia insuficiente"},
    "not_assessable": {"en": "Not assessable from this transcript",
                       "es": "No evaluable a partir de esta transcripción"},
    "evidence": {"en": "Evidence", "es": "Evidencia"},
    "turn": {"en": "turn", "es": "turno"},
    "confidence": {"en": "confidence", "es": "confianza"},
    "band_strong": {"en": "strong", "es": "sólida"},
    "band_tentative": {"en": "tentative", "es": "tentativa"},
    "inferred": {"en": "inference beyond the text", "es": "inferencia más allá del texto"},
    "observed": {"en": "observed in the text", "es": "observado en el texto"},
    "not_licensed": {"en": "Does not license", "es": "No permite concluir"},
    "competing_reading": {"en": "Competing reading", "es": "Lectura alternativa"},
    "discriminating": {"en": "What would discriminate", "es": "Qué permitiría distinguir"},
    "basis": {"en": "Basis", "es": "Base"},
    "counter_evidence": {"en": "Evidence against", "es": "Evidencia en contra"},
    "what_seen": {"en": "What was seen", "es": "Lo que se observó"},
    "what_missing": {"en": "What is missing", "es": "Lo que falta"},
    "consent": {
        "en": "**Consent.** Both partners should know this conversation is being analyzed. "
              "This instrument is built for a description both people can read, not for "
              "analyzing someone who has not been told.",
        "es": "**Consentimiento.** Ambas personas deberían saber que esta conversación se "
              "está analizando. Este instrumento está pensado para una descripción que "
              "ambas puedan leer, no para analizar a alguien sin su conocimiento.",
    },
    "ruled_out_empty": {
        "en": "No construct could be ruled out on this transcript. Ruling a construct out "
              "requires that the conversation gave it an occasion to appear; here the "
              "constructs that did not appear had no such occasion, and they are listed "
              "under *Not assessable* instead. Absence there is absence of opportunity, "
              "not evidence of absence.",
        "es": "No se pudo descartar ningún constructo en esta transcripción. Descartar algo "
              "exige que la conversación le haya dado ocasión de aparecer; aquí los "
              "constructos ausentes no tuvieron esa ocasión y figuran en *No evaluable*. "
              "Esa ausencia es falta de oportunidad, no evidencia de ausencia.",
    },
    "no_cycle": {
        "en": "No interaction cycle is visible in this transcript.",
        "es": "No se observa un ciclo de interacción en esta transcripción.",
    },
    # Safety-gate report
    "safety_title": {"en": "Safety screen", "es": "Detección de seguridad"},
    "safety_observed": {"en": "What was observed", "es": "Lo que se observó"},
    "safety_why": {"en": "Why the standard analysis does not apply",
                   "es": "Por qué no corresponde el análisis habitual"},
    "safety_next": {"en": "Support", "es": "Apoyo"},
    "direction": {"en": "as stated in the text", "es": "según lo dice el texto"},
    "ambiguous": {"en": "This marker is ambiguous", "es": "Este marcador es ambiguo"},
}

DIRECTION = {
    "A_toward_B": {"en": "described as A's conduct toward B", "es": "descrito como conducta de A hacia B"},
    "B_toward_A": {"en": "described as B's conduct toward A", "es": "descrito como conducta de B hacia A"},
    "mutual_as_stated": {"en": "described in both directions", "es": "descrito en ambas direcciones"},
    "unclear": {"en": "direction not established by the text", "es": "dirección no establecida por el texto"},
}

CATEGORY_ES = {
    "threat": "Amenaza",
    "physical_violence": "Violencia física o sus secuelas",
    "intimidation": "Intimidación",
    "monitoring": "Vigilancia / control de movimientos",
    "financial_control": "Control económico",
    "isolation": "Aislamiento de otras personas",
    "sexual_coercion": "Coerción sexual",
    "expressed_fear": "Miedo expresado por una de las partes",
}

# Construct translations, given on first use. The English name stays canonical so that
# analysis.json remains language-invariant.
CONSTRUCT_ES = {
    "gottman.criticism": "crítica",
    "gottman.complaint": "queja específica (no crítica)",
    "gottman.contempt": "desprecio",
    "gottman.defensiveness": "actitud defensiva",
    "gottman.stonewalling": "bloqueo / muro de piedra",
    "gottman.time_out_request": "pausa solicitada (no bloqueo)",
    "gottman.harsh_startup": "inicio áspero",
    "gottman.softened_startup": "inicio suavizado",
    "gottman.bid": "intento de conexión",
    "gottman.turning_toward": "acercamiento al intento de conexión",
    "gottman.turning_away": "desatención al intento de conexión",
    "gottman.turning_against": "rechazo del intento de conexión",
    "gottman.repair_attempt": "intento de reparación",
    "gottman.repair_received": "reparación acogida",
    "gottman.repair_not_received": "reparación no acogida",
    "gottman.accepting_influence": "aceptación de influencia",
    "gottman.rejecting_influence": "rechazo de influencia",
    "gottman.pos_neg_ratio": "proporción de actos positivos y negativos",
    "gottman.self_reported_flooding": "desbordamiento autoinformado",
    "attachment.proximity_seeking": "búsqueda de proximidad",
    "attachment.safe_haven_response": "respuesta de refugio seguro",
    "attachment.protest": "conducta de protesta",
    "attachment.hyperactivating": "estrategia hiperactivante",
    "attachment.deactivating": "estrategia desactivante",
    "attachment.self_reliance_claim": "afirmación de autosuficiencia",
    "eft.secondary_emotion": "emoción secundaria reactiva",
    "eft.primary_emotion_voiced": "emoción primaria expresada",
    "eft.primary_emotion_inferred": "emoción primaria inferida (hipótesis)",
    "eft.attachment_injury_referenced": "herida de apego mencionada",
    "bowen.triangulation": "triangulación",
    "bowen.third_party_present": "tercero mencionado (no triangulación)",
    "bowen.fusion": "fusión emocional",
    "bowen.differentiated_stance": "postura diferenciada",
    "bowen.cutoff": "corte emocional (referido)",
    "bowen.multigenerational_framing": "marco multigeneracional",
    "interdependence.voiced_costs_rewards": "costes y beneficios expresados",
    "interdependence.comparison_level": "nivel de comparación expresado",
    "interdependence.alternatives_voiced": "alternativas mencionadas",
    "interdependence.pro_relationship_transformation": "transformación pro-relación",
    "interdependence.self_interest_stance": "postura de interés propio",
    "interdependence.attractions_voiced": "atractivos expresados",
    "interdependence.barriers_voiced": "barreras expresadas",
    "behavioral.request": "petición",
    "behavioral.refusal": "negativa",
    "behavioral.concrete_agreement": "acuerdo concreto",
    "behavioral.vague_agreement": "acuerdo vago",
    "behavioral.reinforcement_erosion": "erosión del refuerzo",
    "behavioral.coercive_pressure": "presión coercitiva",
    "behavioral.coercion_cycle_completed": "contingencia coercitiva completa",
    "behavioral.exchange_asymmetry": "asimetría en el intercambio",
    "behavioral.acceptance_move": "movimiento de aceptación",
    "behavioral.change_demand": "demanda de cambio",
}

MODULE_TITLE = {
    "10-attachment": {"en": "10 — Attachment strategies", "es": "10 — Estrategias de apego"},
    "20-gottman-levenson": {"en": "20 — Conflict behavior (Gottman & Levenson)",
                            "es": "20 — Conducta en conflicto (Gottman y Levenson)"},
    "30-eft": {"en": "30 — Cycle and emotion (EFT)", "es": "30 — Ciclo y emoción (EFT)"},
    "40-bowen-systems": {"en": "40 — Family systems (Bowen)", "es": "40 — Sistemas familiares (Bowen)"},
    "50-interdependence": {"en": "50 — Interdependence and cohesiveness",
                           "es": "50 — Interdependencia y cohesión"},
    "60-behavioral": {"en": "60 — Behavioral exchange (IBCT)",
                      "es": "60 — Intercambio conductual (IBCT)"},
}

MODULE_ORDER = ["10-attachment", "20-gottman-levenson", "30-eft", "40-bowen-systems",
                "50-interdependence", "60-behavioral"]


def _t(key: str, lang: str) -> str:
    return T[key][lang]


def _name(indicator_id: str, construct: str, lang: str, seen: set[str]) -> str:
    """Canonical English name, with the Spanish gloss on first use."""
    if lang != "es":
        return construct
    gloss = CONSTRUCT_ES.get(indicator_id)
    if gloss and indicator_id not in seen:
        seen.add(indicator_id)
        return f"{construct} ({gloss})"
    return construct


def _quote(ev: dict[str, Any], lang: str) -> str:
    mark = " ⚠" if ev.get("attribution_uncertain") else ""
    return f"  > _{_t('turn', lang)} {ev['turn']} · {ev['speaker']}{mark}_ — “{ev['quote']}”"


def render(doc: dict[str, Any]) -> str:
    lang = doc["run"]["language"]
    if doc["safety_gate"]["halted_analysis"]:
        return _render_safety(doc, lang)
    return _render_standard(doc, lang)


# ------------------------------------------------------------------------ safety report
def _render_safety(doc: dict[str, Any], lang: str) -> str:
    gate = doc["safety_gate"]
    out = [f"# {_t('safety_title', lang)}", ""]

    if not gate["markers"]:  # minors halt
        out += [gate["statement"] or "", ""]
        return "\n".join(out)

    out += [f"## {_t('safety_observed', lang)}", ""]
    for m in gate["markers"]:
        label = CATEGORY_ES[m["category"]] if lang == "es" else CATEGORY_LABEL[m["category"]]
        direction = DIRECTION.get(m["direction"], DIRECTION["unclear"])[lang]
        out.append(f"**{label}** — {direction}")
        out.append("")
        for ev in m["evidence"]:
            out.append(_quote(ev, lang))
        if m["ambiguous"] and m.get("competing_reading"):
            out += ["", f"  _{_t('ambiguous', lang)}: {m['competing_reading']}_"]
        out.append("")

    out += [f"## {_t('safety_why', lang)}", "", gate["statement"] or "", ""]
    out += [f"## {_t('safety_next', lang)}", ""]
    out.append(
        "Talking this through with a qualified professional — a couples or individual "
        "therapist, a domestic-violence advocacy service, or a local support line — would "
        "give you something this tool cannot: someone who can ask questions, hear both "
        "accounts, and respond to your actual situation. Many such services are free and "
        "confidential, and speaking to one commits you to nothing."
        if lang == "en" else
        "Hablar de esto con alguien cualificado — terapia de pareja o individual, un "
        "servicio de atención a víctimas de violencia doméstica, o una línea de apoyo "
        "local — ofrece algo que esta herramienta no puede: alguien que puede preguntar, "
        "escuchar ambas versiones y responder a tu situación concreta. Muchos de esos "
        "servicios son gratuitos y confidenciales, y consultarlos no compromete a nada."
    )
    out += ["", "---", "", _t("consent", lang), ""]
    out.append(
        "_This screen is a conservative heuristic, not a validated instrument. It does not "
        "establish that abuse occurred, does not assess danger, and its silence would not "
        "have meant safety._"
        if lang == "en" else
        "_Esta detección es una heurística conservadora, no un instrumento validado. No "
        "establece que haya habido maltrato, no evalúa peligrosidad, y su silencio tampoco "
        "habría significado seguridad._"
    )
    return "\n".join(out)


# ---------------------------------------------------------------------- standard report
def _render_standard(doc: dict[str, Any], lang: str) -> str:
    seen: set[str] = set()
    out = [f"# {_t('title', lang)}", "", f"_{_t('subtitle', lang)}_", ""]

    tr = doc["transcript"]
    speakers = ", ".join(f"{s['id']} ({s['turn_count']})" for s in tr["speakers"])
    meta = (
        f"{tr['turn_count']} turns · {speakers} · input: {doc['run']['input_format']} · "
        f"language: {doc['run']['language']}"
        if lang == "en" else
        f"{tr['turn_count']} turnos · {speakers} · entrada: {doc['run']['input_format']} · "
        f"idioma: {doc['run']['language']}"
    )
    out += [f"_{meta}_", ""]

    # 1 — limitations first
    out += [f"## {_t('cannot', lang)}", ""]
    for lim in doc["limitations"]:
        out.append(f"- {lim}")
    out += ["", _t("consent", lang), ""]

    # 2 — cycle
    out += [f"## {_t('cycle', lang)}", ""]
    cycle = doc.get("cycle")
    if cycle and cycle["pattern"] != "no_clear_cycle":
        out += [cycle["symmetric_statement"], ""]
        out.append(
            f"_Pattern: `{cycle['pattern']}` · {_t('confidence', lang)} {cycle['confidence']:.2f}_"
            if lang == "en" else
            f"_Patrón: `{cycle['pattern']}` · {_t('confidence', lang)} {cycle['confidence']:.2f}_"
        )
        out.append("")
        for ev in cycle.get("evidence", [])[:6]:
            out.append(_quote(ev, lang))
        out.append("")
    else:
        out += [cycle["symmetric_statement"] if cycle else _t("no_cycle", lang), ""]

    # 3 — indicators by module
    out += [f"## {_t('indicators', lang)}", ""]
    by_module: dict[str, list[dict[str, Any]]] = {}
    for ind in doc["indicators"]:
        by_module.setdefault(ind["module"], []).append(ind)
    for mod in MODULE_ORDER:
        inds = by_module.get(mod, [])
        gaps = [g for g in doc["insufficient_evidence"] if g["module"] == mod]
        na = [n for n in doc["not_assessable"] if n["module"] == mod]
        if not (inds or gaps or na):
            continue
        out += [f"### {MODULE_TITLE[mod][lang]}", ""]
        for ind in sorted(inds, key=lambda i: -i["confidence"]):
            band = _t(f"band_{ind['confidence_band']}", lang)
            level = _t(ind["inference_level"], lang)
            who = f" — **{ind['speaker']}**" if ind["speaker"] else " — **dyad**" if lang == "en" else " — **díada**"
            out.append(
                f"**{_name(ind['indicator_id'], ind['construct'], lang, seen)}**{who}  "
                f"`{ind['confidence']:.2f}` {band} · {level}"
            )
            out += ["", f"{ind['rationale']}", ""]
            for ev in ind["evidence"][:4]:
                out.append(_quote(ev, lang))
            if ind.get("counter_evidence"):
                out.append("")
                for ev in ind["counter_evidence"][:2]:
                    out.append(_quote(ev, lang))
            out.append("")
            if ind.get("competing_reading"):
                out += [f"_{_t('competing_reading', lang)}: {ind['competing_reading']}_", ""]
            out += [f"_{_t('not_licensed', lang)}: {ind['not_licensed']}_", "",
                    f"_{ind['theory_source']}_", "", "---", ""]
        if gaps:
            out += [f"#### {_t('insufficient', lang)}", ""]
            for g in gaps:
                out.append(f"- **{g['construct']}** (`{g.get('confidence', 0):.2f}`)")
                out.append(f"  - {_t('what_seen', lang)}: {g['what_was_seen']}")
                out.append(f"  - {_t('what_missing', lang)}: {g['what_is_missing']}")
            out.append("")
        if na:
            out += [f"#### {_t('not_assessable', lang)}", ""]
            for n in na:
                tag = " *(unmeasured)*" if n.get("measurement_layer") == "unmeasured" else ""
                out.append(f"- **{n['construct']}**{tag} — {n['reason']}")
            out.append("")

    # 4 — ruled out (mandatory)
    out += [f"## {_t('ruled_out', lang)}", ""]
    if doc["ruled_out"]:
        out.append(
            "Constructs actively searched for and not found, in a transcript that gave them "
            "an occasion to appear."
            if lang == "en" else
            "Constructos buscados activamente y no encontrados, en una transcripción que sí "
            "les dio ocasión de aparecer."
        )
        out.append("")
        for r in doc["ruled_out"]:
            out.append(f"**{r['construct']}** — _{r['module']}_")
            out += ["", f"{_t('basis', lang)}: {r['basis']}", ""]
            for ev in r["counter_evidence"][:2]:
                out.append(_quote(ev, lang))
            out.append("")
    else:
        out += [_t("ruled_out_empty", lang), ""]

    # 5 — competing readings
    out += [f"## {_t('competing', lang)}", ""]
    for c in doc["competing_readings"]:
        out.append(f"- {c['reading']}")
        out.append(f"  - **{_t('discriminating', lang)}:** {c['discriminating_data']}")
    out.append("")

    # 6 — open questions
    out += [f"## {_t('open_q', lang)}", ""]
    out.append(
        "What a clinician would need to ask. These are not for one partner to answer about "
        "the other."
        if lang == "en" else
        "Lo que un profesional necesitaría preguntar. No son preguntas para que una persona "
        "responda por la otra."
    )
    out.append("")
    for q in doc["open_questions"]:
        out.append(f"- {q}")
    out.append("")
    return "\n".join(out)
