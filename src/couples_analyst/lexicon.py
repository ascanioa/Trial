"""Bilingual (en/es) surface markers used by the deterministic reference coder.

These are *operationalizations*, not the constructs themselves. Each group maps to a
definition in a reference/ file; where a theory does not license a text-only marker, no
group exists here and the module reports the construct as unmeasured.

Matching is accent-folded and length-preserving, so character offsets computed on the folded
text index correctly into the original turn and quotes come back verbatim.
"""

from __future__ import annotations

import re

_FOLD = str.maketrans("áéíóúüñÁÉÍÓÚÜÑàèìòùâêîôûçÇ", "aeiouunAEIOUUNaeiouaeioucC")


def fold(text: str) -> str:
    """Lowercase + strip diacritics, preserving length 1:1 so offsets stay valid."""
    return text.translate(_FOLD).lower()


def compile_group(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p) for p in patterns]


def sentence_around(text: str, start: int, end: int, max_len: int = 220) -> tuple[int, int]:
    """Expand a match to its containing sentence so quotes read as language, not fragments."""
    left = max(
        (text.rfind(ch, 0, start) for ch in ".!?¿¡\n"),
        default=-1,
    )
    right_candidates = [i for i in (text.find(ch, end) for ch in ".!?\n") if i != -1]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    left = left + 1 if left != -1 else 0
    while left < len(text) and text[left] in " \t":
        left += 1
    if right - left > max_len:  # keep long turns from swallowing the report
        left, right = max(left, start - max_len // 2), min(right, end + max_len // 2)
    return left, right


def find_spans(
    text_folded: str, patterns: list[re.Pattern[str]], *, exclude: list[re.Pattern[str]] | None = None
) -> list[tuple[int, int]]:
    """All non-overlapping match spans, minus any covered by an ``exclude`` pattern."""
    spans: list[tuple[int, int]] = []
    blocked: list[tuple[int, int]] = []
    for pat in exclude or []:
        blocked.extend(m.span() for m in pat.finditer(text_folded))
    for pat in patterns:
        for m in pat.finditer(text_folded):
            s, e = m.span()
            if any(bs <= s < be or bs < e <= be for bs, be in blocked):
                continue
            if any(s < pe and ps < e for ps, pe in spans):
                continue
            spans.append((s, e))
    return sorted(spans)


# --------------------------------------------------------------------------------------
# 20 - Gottman & Levenson
# --------------------------------------------------------------------------------------

# Global/stable attributions: the criticism-vs-complaint hinge.
GLOBAL_QUANTIFIER = {
    "en": [
        r"\byou (?:always|never)\b",
        r"\b(?:always|never) (?:do|say|think|listen|help|show up|care)\b",
        r"\byou(?:'re| are) (?:always|never|constantly)\b",
        r"\bevery (?:single )?time\b",
        r"\bthis is (?:just )?(?:who|what) you are\b",
        r"\btypical of you\b",
        r"\bthat(?:'s| is) so you\b",
    ],
    "es": [
        r"\b(?:tu )?siempre\b",
        r"\bnunca\b",
        r"\bjamas\b",
        r"\btodo el tiempo\b",
        r"\bcada vez que\b",
        r"\basi eres tu\b",
        r"\btipico de ti\b",
        r"\bcomo siempre\b",
    ],
}

# Trait-level character attribution ("you ARE x"), distinct from a behavior complaint.
TRAIT_ATTRIBUTION = {
    "en": [
        r"\byou(?:'re| are)\s+(?:so\s+|such\s+an?\s+|just\s+)?(?:selfish|lazy|careless|cold|controlling|immature|irresponsible|thoughtless|impossible|useless|childish|paranoid|obsessive|dramatic)\b",
        r"\byou(?:'re| are) (?:such )?(?:a|an)\s+(?:liar|mess|disaster|coward|hypocrite|bully|slob|nag|fraud|monster)\b",
        r"\bwhat(?:'s| is) wrong with you\b",
        r"\byou have no (?:idea|respect|consideration|empathy)\b",
        r"\bthat(?:'s| is) your problem\b",
    ],
    "es": [
        r"\beres\s+(?:un[oa]?\s+|muy\s+|tan\s+)?(?:egoista|vag[oa]|desconsiderad[oa]|fri[oa]|controlador[a]?|inmadur[oa]|irresponsable|imposible|inutil|infantil|paranoic[oa]|dramatic[oa])\b",
        r"\beres un[oa]?\s+(?:mentiros[oa]|desastre|cobarde|hipocrita|abusador[a]?|dejad[oa]|pesad[oa]|farsante|monstruo)\b",
        r"\bque te pasa\b",
        r"\bno tienes (?:idea|respeto|consideracion|empatia)\b",
        r"\bese es tu problema\b",
    ],
}

# Contempt: superiority position - insult, mockery, derision.
CONTEMPT = {
    "en": [
        r"\b(?:pathetic|ridiculous|disgusting|grow up|get over yourself|spare me)\b",
        r"\byou(?:'re| are) (?:such )?(?:an? )?(?:idiot|moron|joke|child|baby|loser)\b",
        r"\bwow\b.{0,20}\b(?:brilliant|genius)\b",
        r"\b(?:oh )?(?:poor|sure) (?:you|baby)\b",
        r"\brolls? (?:my|her|his|their) eyes\b",
        r"\beye[- ]roll\b",
        r"\bof course you (?:did|would|do)\b",
        r"\byou(?:'re| are) unbelievable\b",
        r"\bnice job\b.{0,30}\bagain\b",
    ],
    "es": [
        r"\b(?:patetic[oa]|ridicul[oa]|asqueros[oa]|madura ya|superalo)\b",
        r"\beres un[oa]?\s+(?:idiota|imbecil|estupid[oa]|chiste|nin[oa]|perdedor[a]?)\b",
        r"\bque (?:genio|maravilla)\b",
        r"\bpobrecit[oa]\b",
        r"\bpongo los ojos en blanco\b",
        r"\bcomo no\b.{0,20}\b(?:tu|claro)\b",
        r"\beres increible\b",
        r"\bay si\b",
    ],
}

# Defensiveness: warding off without taking any responsibility.
DEFENSIVENESS = {
    "en": [
        r"\bwhat about (?:you|when you)\b",
        r"\byou(?:'re| are) the one who\b",
        r"\bi never said that\b",
        r"\bthat(?:'s| is) not (?:what i said|true|fair)\b",
        r"\byes,? but\b",
        r"\bi did not\b.{0,40}\byou\b",
        r"\bit(?:'s| is) not my fault\b",
        r"\bwhy is it always my fault\b",
        r"\bi was just\b",
        r"\bat least i\b",
        r"\bdon(?:'t| not) blame me\b",
    ],
    "es": [
        r"\by tu que\b",
        r"\btu eres (?:el|la) que\b",
        r"\byo nunca dije eso\b",
        r"\beso no es (?:lo que dije|verdad|justo)\b",
        r"\bsi,? pero\b",
        r"\bno es mi culpa\b",
        r"\bpor que siempre es mi culpa\b",
        r"\byo solo\b",
        r"\bal menos yo\b",
        r"\bno me eches la culpa\b",
    ],
}

# Listener withdrawal candidates (see TIMEOUT_* for the mandatory discrimination).
STONEWALL_MINIMAL = {
    "en": [
        r"^(?:whatever|fine|ok|okay|sure|k|nothing|forget it|if you say so|mm+|hm+)[.!]?$",
        r"^(?:i (?:don'?t|dont) (?:care|know))[.!]?$",
        r"^(?:yep|nope|right|uh huh)[.!]?$",
    ],
    "es": [
        r"^(?:lo que sea|da igual|bien|vale|ok|nada|olvidalo|si tu lo dices|mm+|ya)[.!]?$",
        r"^(?:no (?:me importa|se))[.!]?$",
        r"^(?:si|no|claro|ajam)[.!]?$",
    ],
}

# Explicit refusal to engage. One instance qualifies; minimal tokens need repetition.
STONEWALL_EXPLICIT = {
    "en": [
        r"\bi(?:'m| am) done (?:talking|with this)\b",
        r"\bi(?:'m| am) not (?:doing|having) this\b",
        r"\bthere(?:'s| is) nothing to (?:talk about|say)\b",
        r"\bdrop it\b",
        r"\bend of discussion\b",
        r"\bi(?:'m| am) not (?:answering|discussing) (?:that|this)\b",
        r"\b(?:conversation|discussion) (?:is )?over\b",
    ],
    "es": [
        r"\bya no quiero hablar\b",
        r"\bno voy a (?:hacer|seguir con) esto\b",
        r"\bno hay nada de que hablar\b",
        r"\bdejalo (?:ya|asi)\b",
        r"\bse acabo la (?:discusion|conversacion)\b",
        r"\bno voy a (?:contestar|discutir) (?:eso|esto)\b",
        r"\bfin de la (?:discusion|conversacion)\b",
    ],
}

# Taking responsibility disqualifies a turn from defensiveness (20-gottman sec. 1.1).
ACCEPT_RESPONSIBILITY = {
    "en": [
        r"\bthat(?:'s| is|\s+was) on me\b", r"\bmy fault\b", r"\byou(?:'re| are) right\b",
        r"\bi (?:did|know i) (?:forget|forgot|messed up|dropped)\b",
        r"\bi should have\b", r"\bi(?:'m| am) sorry\b", r"\bi apologi[sz]e\b",
        r"\bi (?:own|take responsibility for) that\b",
    ],
    "es": [
        r"\bes culpa mia\b", r"\btienes razon\b",
        r"\b(?:si,? )?(?:lo olvide|se me olvido|la regue|me equivoque)\b",
        r"\bdebi (?:haber|de)\b", r"\blo siento\b", r"\bperdon\b",
        r"\bme hago cargo\b",
    ],
}

# Time-out leg 1: names the internal state or the need.
TIMEOUT_NEEDS_STATE = {
    "en": [
        r"\bi(?:'m| am) (?:getting |feeling )?(?:overwhelmed|flooded|too (?:upset|angry)|worked up)\b",
        r"\bi need (?:a |an |another |\d+ |a few |five |ten |fifteen |twenty |thirty )?(?:minute|minutes|moment|moments|break|hour|second|seconds)\b",
        r"\bi need to (?:calm down|cool off|breathe|think|step (?:away|out|outside)|take a walk)\b",
        r"\bi can(?:'t|not) think straight\b",
        r"\bmy head is (?:spinning|pounding)\b",
        r"\bi(?:'m| am) at my limit\b",
    ],
    "es": [
        r"\b(?:estoy|me siento) (?:muy )?(?:abrumad[oa]|saturad[oa]|desbordad[oa]|alterad[oa]|molest[oa] de mas)\b",
        r"\bnecesito (?:un[oa]? |otros? |\d+ |unos |cinco |diez |quince |veinte |treinta )?(?:minuto|minutos|momento|rato|hora|segundo|segundos|pausa)\b",
        r"\bnecesito (?:calmarme|respirar|pensar|tomar aire|salir un momento|caminar)\b",
        r"\bno puedo pensar (?:con claridad|bien)\b",
        r"\bestoy en mi limite\b",
    ],
}

# Time-out leg 2: proposes a return.
TIMEOUT_RETURN = {
    "en": [
        r"\b(?:can we|let(?:'s| us)) (?:come back|talk|continue|finish|sort|deal with|pick|get back)\b.{0,40}\b(?:later|tonight|tomorrow|in (?:a|\d+)\b|after|when|this|it)\b",
        r"\bthen (?:let(?:'s| us)|we(?:'ll| will)|i(?:'ll| will))\b.{0,30}\b(?:talk|finish|continue|come back|sort)\b",
        r"\bgive me (?:a minute|\d+ minutes|an hour|until)\b",
        r"\bi(?:'ll| will) (?:come back|be back|be ready)\b",
        r"\bin (?:\d+|a few|ten|twenty|thirty) minutes\b",
        r"\bnot right now,? but\b",
        r"\bi do want to (?:talk|finish|sort) this\b",
    ],
    "es": [
        r"\b(?:podemos|vamos a) (?:seguir|hablar|retomar|continuar|terminar|resolver)\b.{0,40}\b(?:luego|despues|mas tarde|manana|en \d+|cuando|esto|esta noche)\b",
        r"\b(?:y (?:luego|despues)|entonces) (?:seguimos|hablamos|lo terminamos|retomamos)\b",
        r"\bdame (?:un minuto|\d+ minutos|una hora|hasta)\b",
        r"\b(?:vuelvo|regreso|sigo) (?:en|dentro de)\b",
        r"\ben (?:\d+|unos|diez|veinte|treinta) minutos\b",
        r"\bahora no,? pero\b",
        r"\bsi quiero (?:hablar|terminar|resolver) esto\b",
    ],
}

# Time-out leg 3 (disqualifier): a parting shot in the same turn.
PARTING_SHOT = {
    "en": [
        r"\bbecause you\b", r"\byour fault\b", r"\btypical\b", r"\bas usual\b",
        r"\bi can(?:'t|not) (?:deal with|stand) you\b", r"\bgrow up\b", r"\bwhatever\b",
    ],
    "es": [
        r"\bporque tu\b", r"\bculpa tuya\b", r"\btipico\b", r"\bcomo siempre\b",
        r"\bno te soporto\b", r"\bmadura\b", r"\blo que sea\b",
    ],
}

# Self-reported overwhelm. NOT evidence of the physiological construct (20-gottman sec. 1.8).
FLOODING_SELF_REPORT = {
    "en": [
        r"\bi can(?:'t|not) do this (?:right now|anymore)\b",
        r"\bi can(?:'t|not) (?:keep going|take (?:this|any more))\b",
        r"\bi need to stop\b",
        r"\bi(?:'m| am) (?:shutting down|shaking|overwhelmed|flooded)\b",
        r"\bmy (?:heart is racing|chest is tight)\b",
        r"\bi feel sick\b",
    ],
    "es": [
        r"\bno puedo (?:mas|con esto|seguir)\b",
        r"\bnecesito parar\b",
        r"\b(?:estoy|me estoy) (?:bloquead[oa]|temblando|abrumad[oa]|desbordad[oa])\b",
        r"\bme (?:late el corazon|duele el pecho)\b",
        r"\bme siento mal fisicamente\b",
    ],
}

# Repair attempts: any move to de-escalate or interrupt negativity.
REPAIR = {
    "en": [
        r"\bi(?:'m| am) sorry\b",
        r"\bi apologi[sz]e\b",
        r"\bthat came out wrong\b",
        r"\blet me (?:try (?:that )?again|start over|rephrase)\b",
        r"\bcan we (?:start over|try again|reset)\b",
        r"\byou(?:'re| are) right\b",
        r"\bthat(?:'s| is) fair\b",
        r"\bi (?:hear|see) (?:you|what you(?:'re| are) saying)\b",
        r"\bi love you\b",
        r"\bwe(?:'re| are) on the same (?:side|team)\b",
        r"\bi don(?:'t| not) want to fight\b",
        r"\bthat(?:'s| is|\s+was) on me\b",
        r"\bmy fault\b",
        r"\bthank you for\b",
    ],
    "es": [
        r"\b(?:lo siento|perdon|perdoname|disculpa)\b",
        r"\beso sono mal\b",
        r"\bdejame (?:intentarlo de nuevo|empezar de nuevo|decirlo mejor)\b",
        r"\bpodemos (?:empezar de nuevo|intentarlo otra vez)\b",
        r"\btienes razon\b",
        r"\beso es justo\b",
        r"\b(?:te (?:escucho|entiendo)|entiendo lo que dices)\b",
        r"\bte (?:quiero|amo)\b",
        r"\bestamos del mismo lado\b",
        r"\bno quiero pelear\b",
        r"\bes culpa mia\b",
        r"\bgracias por\b",
    ],
}

# De-escalation uptake in the turn AFTER a repair.
REPAIR_UPTAKE = {
    "en": [
        r"\b(?:ok|okay|yeah|yes|alright|fine),? (?:i |we |let(?:'s| us) |me too|same)\b",
        r"\bme too\b", r"\bi(?:'m| am) sorry too\b", r"\bthank you\b",
        r"\byou(?:'re| are) right\b", r"\bi don(?:'t| not) want to fight (?:either|too)\b",
        r"\bi (?:hear|get) (?:you|that)\b", r"\blet(?:'s| us) (?:try|start|talk)\b",
        r"\bi love you too\b", r"\bcome here\b",
    ],
    "es": [
        r"\b(?:ok|vale|si|esta bien),? (?:yo|nosotros|vamos|tambien)\b",
        r"\byo tambien\b", r"\bperdon(?:ame)? tu tambien\b", r"\bgracias\b",
        r"\btienes razon\b", r"\byo tampoco quiero pelear\b",
        r"\bte (?:entiendo|escucho)\b", r"\bvamos a (?:intentar|hablar|empezar)\b",
        r"\bven aca\b",
    ],
}

# Accepting influence: yielding to, or incorporating, the partner's position.
ACCEPTING_INFLUENCE = {
    "en": [
        r"\byou(?:'re| are) right\b",
        r"\b(?:that|you make) (?:a|is a) (?:good|fair) point\b",
        r"\bi hadn(?:'t| not) thought (?:of|about) (?:that|it that way)\b",
        r"\bok(?:ay)?,? (?:let(?:'s| us) do it your way|we can|i can)\b",
        r"\bi(?:'ll| will) (?:try|do) (?:that|it)\b",
        r"\bi agree\b",
        r"\bfair enough\b",
        r"^fair[.!]?(?:\s|$)",
    ],
    "es": [
        r"\btienes razon\b",
        r"\b(?:es|tienes) un (?:buen|justo) punto\b",
        r"\bno lo habia (?:pensado|visto) asi\b",
        r"\b(?:ok|vale|esta bien),? (?:lo hacemos a tu manera|podemos|puedo)\b",
        r"\bvoy a (?:intentarlo|hacerlo)\b",
        r"\bestoy de acuerdo\b",
        r"\bme parece justo\b",
    ],
}

# Softened startup: I-statement + specific situation + need, no character attribution.
I_STATEMENT = {
    "en": [
        r"\bi (?:feel|felt|get|got|was|am) (?:\w+ ){0,2}(?:when|because|about)\b",
        r"\bi(?:'m| am) (?:feeling )?(?:hurt|worried|scared|lonely|sad|anxious|frustrated|tired)\b",
        r"\bi (?:need|would like|was hoping)\b",
        r"\bit would (?:help|mean a lot) (?:if|to me)\b",
        r"\bcan we (?:talk|figure out|find a way)\b",
    ],
    "es": [
        r"\b(?:me senti|me siento|me pongo|estaba|estoy) (?:\w+ ){0,2}(?:cuando|porque)\b",
        r"\b(?:me siento|estoy) (?:dolid[oa]|preocupad[oa]|asustad[oa]|sol[oa]|trist[e]|ansios[oa]|frustrad[oa]|cansad[oa])\b",
        r"\b(?:necesito|me gustaria|esperaba)\b",
        r"\bme (?:ayudaria|significaria mucho) (?:si|que)\b",
        r"\bpodemos (?:hablar|ver como|encontrar)\b",
    ],
}

# Specific, situated complaint: an unmet expectation about a named behavior. This is the
# criticism near-miss, so the trigger is the complaint predicate, never a bare date word.
SPECIFIC_COMPLAINT = {
    "en": [
        r"\byou (?:didn'?t|did not|forgot to|said you would|were supposed to)\s+\w+",
        r"\byou (?:forgot|missed|skipped|cancelled|left me|ignored)\b",
        r"\bi (?:waited|sat there|was left|ended up)\b",
        r"\bit (?:didn'?t|did not) get (?:done|finished)\b",
        r"\bnobody (?:called|told|asked) me\b",
    ],
    "es": [
        r"\bno (?:llamaste|avisaste|viniste|contestaste|lo hiciste|me dijiste)\b",
        r"\b(?:olvidaste|te olvidaste de|cancelaste|me dejaste|ignoraste)\b",
        r"\bdijiste que (?:ibas a|lo harias)\b",
        r"\b(?:espere|me quede|termine) (?:una hora|sol[oa]|ahi|esperando)\b",
        r"\bno se (?:hizo|termino)\b",
    ],
}

# Situational anchors. Supporting context for a complaint, never a trigger on their own.
TEMPORAL_ANCHOR = {
    "en": [
        r"\b(?:last night|yesterday|this morning|on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|today|last week|at dinner|for an hour)\b",
    ],
    "es": [
        r"\b(?:anoche|ayer|esta manana|el (?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)|hoy|la semana pasada|en la cena|una hora)\b",
    ],
}

# Bids for connection.
BID = {
    "en": [
        r"\bhow (?:was|is) your (?:day|week|meeting)\b",
        r"\b(?:do you want to|would you like to|shall we|should we|let(?:'s| us) go)\b",
        r"\blook at (?:this|that)\b",
        r"\bi was thinking (?:about|that|we)\b",
        r"\bcan you (?:believe|come|sit|help)\b",
        r"\bi missed you\b",
        r"\bare you (?:ok|okay|alright)\b",
        r"\bwhat do you think\b",
    ],
    "es": [
        r"\bcomo (?:estuvo|va|fue) tu (?:dia|semana|reunion)\b",
        r"\b(?:quieres|te gustaria|te apetece)\b",
        r"\bvamos a (?:cenar|salir|ver|caminar|hacer algo)\b",
        r"\bmira (?:esto|eso)\b",
        r"\bestaba pensando (?:en|que)\b",
        r"\bpuedes (?:creer|venir|sentarte|ayudarme)\b",
        r"\bte extran[eo]\b",
        r"\bestas (?:bien|ok)\b",
        r"\bque (?:opinas|piensas)\b",
    ],
}

TURNING_AGAINST = {
    "en": [
        r"\bnot now\b", r"\bcan(?:'t| not) you see i(?:'m| am)\b", r"\bwhy do you always ask\b",
        r"\bleave me alone\b", r"\bwho cares\b", r"\bstop (?:talking|bothering)\b",
    ],
    "es": [
        r"\bahora no\b", r"\bno ves que estoy\b", r"\bpor que siempre preguntas\b",
        r"\bdejame en paz\b", r"\ba quien le importa\b", r"\bdeja de (?:hablar|molestar)\b",
    ],
}

POSITIVE_AFFECT = {
    "en": [
        r"\b(?:thank you|thanks|i love you|i appreciate|good point|you(?:'re| are) right|i(?:'m| am) sorry|i miss(?:ed)? you|please|i understand|that(?:'s| is) fair|haha|lol|\bi hear you\b)\b",
        r"\b(?:agree|agreed|fair enough|of course i (?:care|love))\b",
    ],
    "es": [
        r"\b(?:gracias|te (?:quiero|amo)|te agradezco|buen punto|tienes razon|lo siento|perdon|te extran[eo]|por favor|entiendo|es justo|jaja)\b",
        r"\b(?:de acuerdo|claro que (?:me importa|te quiero))\b",
    ],
}

NEGATIVE_AFFECT = {
    "en": [
        r"\b(?:you always|you never|whatever|shut up|ridiculous|pathetic|stupid|hate|sick of|fed up|your fault|blame|selfish|useless|unbelievable|don'?t care)\b",
    ],
    "es": [
        r"\b(?:siempre|nunca|lo que sea|callate|ridicul[oa]|patetic[oa]|estupid[oa]|odio|harta?|harto|culpa tuya|egoista|inutil|increible|no me importa)\b",
    ],
}

# --------------------------------------------------------------------------------------
# 10 - Attachment strategies (behavioral moves only; never a style)
# --------------------------------------------------------------------------------------

PROXIMITY_SEEKING = {
    "en": [
        r"\bi (?:just )?(?:want|need) (?:you (?:here|with me|to stay|to come back|to look at me)|us to be ok)\b",
        r"(?:^|[.!?]\s+|[,;]\s+)(?:please\s+)?come (?:back|here|home)\b",
        r"\bstay (?:here|with me|in the room|a (?:bit|while)|please)\b",
        r"\bdon(?:'t| not) (?:go|leave|shut me out)\b",
        r"\bcan (?:you|we) (?:just )?(?:hold|hug|sit|be)\b", r"\bi missed you\b",
        r"\bare we (?:ok|okay|good)\b", r"\btalk to me\b",
    ],
    "es": [
        r"\b(?:solo )?(?:quiero|necesito) que (?:te quedes|vuelvas|me mires|estemos bien)\b",
        r"(?:^|[.!?]\s+|[,;]\s+)(?:por favor\s+)?(?:vuelve|ven|regresa)\b",
        r"\bquedate (?:aqui|conmigo|un rato)\b",
        r"\bno te (?:vayas|alejes|cierres)\b",
        r"\bpuedes? (?:abrazarme|sentarte|quedarte)\b", r"\bte extran[eo]\b",
        r"\bestamos bien\b", r"\bhablame\b",
    ],
}

PROTEST = {
    "en": [
        r"\bwhy (?:don'?t|do not|won'?t) you (?:ever )?(?:answer|call|listen|look at me|say something)\b",
        r"\bdo you even (?:care|love me|notice)\b",
        r"\bi(?:'ve| have) been (?:waiting|trying|asking)\b",
        r"\byou(?:'re| are) not even (?:listening|looking|here)\b",
        r"\bsay something\b",
        r"\bi(?:'m| am) right here\b",
    ],
    "es": [
        r"\bpor que no (?:me )?(?:contestas|llamas|escuchas|miras|dices nada)\b",
        r"\b(?:te importa|me quieres|te das cuenta) (?:si|acaso)\b",
        r"\b(?:llevo|he estado) (?:esperando|intentando|pidiendo)\b",
        r"\bni siquiera (?:me estas escuchando|me miras|estas aqui)\b",
        r"\bdi algo\b",
        r"\baqui estoy\b",
    ],
}

HYPERACTIVATING = {
    "en": [
        r"\bif you (?:really )?loved me\b",
        r"\bmaybe (?:we should|you should) just (?:end|leave|go)\b",
        r"\bdo you (?:still )?(?:love|want) me\b",
        r"\banswer me\b",
        r"\bi(?:'ll| will) keep asking\b",
        r"\bten (?:texts|calls)\b",
        r"\btell me (?:now|right now)\b",
    ],
    "es": [
        r"\bsi (?:de verdad )?me quisieras\b",
        r"\btal vez (?:deberiamos|deberias) (?:terminar|irte|dejarlo)\b",
        r"\b(?:todavia )?me (?:quieres|amas)\b",
        r"\bcontestame\b",
        r"\bvoy a seguir preguntando\b",
        r"\bdiez (?:mensajes|llamadas)\b",
        r"\bdimelo (?:ahora|ya)\b",
    ],
}

DEACTIVATING = {
    "en": [
        r"\bit(?:'s| is) not (?:a big deal|that deep|important)\b",
        r"\bi(?:'m| am) fine\b",
        r"\bi don(?:'t| not) (?:need|want) (?:to talk about (?:it|this)|help)\b",
        r"\bi(?:'ll| will) (?:handle|deal with|sort) .{0,24}?(?:myself|on my own)\b",
        r"\bcan we (?:talk about something else|not do this)\b",
        r"\bi don(?:'t| not) (?:get|do) (?:emotional|feelings)\b",
        r"\bthere(?:'s| is) nothing to talk about\b",
    ],
    "es": [
        r"\bno es (?:para tanto|tan grave|importante)\b",
        r"\bestoy bien\b",
        r"\bno (?:necesito|quiero) (?:hablar de (?:eso|esto])|ayuda)\b",
        r"\b(?:lo|me) (?:resuelvo|arreglo) (?:sol[oa]|yo)\b",
        r"\bpodemos (?:hablar de otra cosa|no hacer esto)\b",
        r"\bno (?:soy|va conmigo) (?:de |lo )?(?:emocional|sentimientos)\b",
        r"\bno hay nada de que hablar\b",
    ],
}

SELF_RELIANCE_CLAIM = {
    "en": [
        r"\bi don(?:'t| not) need (?:anyone|anybody|you|help)\b",
        r"\bi(?:'ve| have) always (?:handled|done) (?:it|this) (?:myself|alone)\b",
        r"\bi(?:'ll| will) (?:handle|do|sort|manage) .{0,24}?(?:myself|on my own|alone)\b",
        r"\bi(?:'m| am) used to (?:doing it alone|being alone)\b",
        r"\bi manage (?:on my own|alone)\b",
    ],
    "es": [
        r"\bno necesito (?:a nadie|ayuda|que me)\b",
        r"\bsiempre (?:lo he hecho|me he arreglado) (?:sol[oa]|yo)\b",
        r"\bestoy acostumbrad[oa] a (?:hacerlo|estar) sol[oa]\b",
        r"\bme arreglo sol[oa]\b",
    ],
}

TOPIC_SHIFT = {
    "en": [r"\banyway\b", r"\bcan we (?:change the subject|talk about something else)\b",
           r"\bdid you (?:see|get|remember) the\b", r"\bwhat(?:'s| is) for dinner\b",
           r"\bthat reminds me\b"],
    "es": [r"\ben fin\b", r"\bcambiando de tema\b", r"\bpodemos hablar de otra cosa\b",
           r"\bviste (?:el|la|lo)\b", r"\bque hay de (?:cena|comer)\b", r"\beso me recuerda\b"],
}

SECURE_BASE = {
    "en": [
        r"\bi(?:'m| am) (?:here|not going anywhere)\b",
        r"\bwe(?:'ll| will) (?:figure|get through) (?:it|this)\b",
        r"\bi(?:'ve| have) got you\b",
        r"\btake your time\b",
        r"\bwhat do you need (?:from me)?\b",
        r"\bi want to understand\b",
        r"\bgo (?:for it|do it),? i(?:'ll| will)\b",
    ],
    "es": [
        r"\b(?:aqui estoy|no me voy a ningun lado)\b",
        r"\b(?:lo vamos a|vamos a) (?:resolver|superar|arreglar)\b",
        r"\bcuenta conmigo\b",
        r"\btomate tu tiempo\b",
        r"\bque necesitas (?:de mi)?\b",
        r"\bquiero entender\b",
        r"\bve (?:tranquil[oa]|por ello),? yo\b",
    ],
}

# --------------------------------------------------------------------------------------
# 30 - EFT
# --------------------------------------------------------------------------------------

# The construct is the SPEAKER's expressed emotion, so both groups require a first-person
# frame. "You're angry" attributes an emotion; it does not express one. "Doing it alone" is
# a description of circumstances, not a voiced feeling.
_SECOND = r"(?:angry|mad|furious|annoyed|irritated|frustrated|fed up|resentful|pissed|livid)"
_PRIMARY = (
    r"(?:scared|afraid|terrified|hurt|lonely|ashamed|embarrassed|small|worthless|"
    r"abandoned|unwanted|unloved|invisible|helpless|rejected)"
)

SECONDARY_EMOTION = {
    "en": [
        rf"\bi(?:'m| am|'ve been| was| get| got| feel| felt) (?:so |really |just |very |pretty )?{_SECOND}\b",
        r"\bi(?:'m| am) (?:so )?(?:sick|tired) of\b",
        r"\bthis (?:makes me|is making me) (?:angry|mad|furious)\b",
        r"\bit (?:makes|made) me (?:angry|mad|furious)\b",
    ],
    "es": [
        r"\b(?:estoy|estaba|me siento|me senti|me pongo) (?:muy |tan |bastante )?(?:enojad[oa]|molest[oa]|furios[oa]|irritad[oa]|frustrad[oa]|hart[oa]|resentid[oa]|cabread[oa])\b",
        r"\b(?:estoy|ya estoy) hart[oa] de\b",
        r"\besto me (?:enoja|enfurece|molesta)\b",
        r"\bme da (?:rabia|coraje)\b",
    ],
}

PRIMARY_EMOTION = {
    "en": [
        rf"\bi(?:'m| am|'ve been| was| get| got| feel| felt) (?:so |really |just |very |pretty )?{_PRIMARY}\b",
        r"\bi feel (?:all )?alone\b",
        r"\bi(?:'m| am) (?:all )?alone (?:in|here)\b",
        r"\bit (?:hurt|hurts|stings)\b",
        r"\bi(?:'m| am) not enough\b",
        r"\bi (?:don'?t|do not) matter\b",
        r"\bi felt like (?:i|nothing|nobody)\b",
    ],
    "es": [
        r"\b(?:estoy|estaba|me siento|me senti) (?:muy |tan |bastante )?(?:asustad[oa]|dolid[oa]|sol[oa]|avergonzad[oa]|abandonad[oa]|invisible|rechazad[oa]|pequen[oa])\b",
        r"\b(?:tengo|tenia) miedo\b",
        r"\bme (?:duele|dolio|dolia)\b",
        r"\bno soy suficiente\b",
        r"\bno (?:le )?importo\b",
        r"\bme senti como (?:si|una? )\b",
    ],
}

ATTACHMENT_INJURY = {
    "en": [
        r"\bwhen i (?:needed|was in the hospital|lost|was sick|miscarried)\b.{0,60}\byou (?:weren'?t|were not|didn'?t)\b",
        r"\byou (?:weren'?t|were not) there\b",
        r"\bi(?:'ll| will) never forget (?:that|when)\b",
        r"\bsince (?:the|that) (?:night|day|time)\b",
        r"\bi stopped (?:trusting|counting on) you\b",
        r"\bafter what (?:you did|happened)\b",
    ],
    "es": [
        r"\bcuando (?:te necesite|estuve en el hospital|perdi|estaba enferm[oa])\b.{0,60}\bno (?:estuviste|viniste|te importo)\b",
        r"\bno estuviste (?:ahi|conmigo)\b",
        r"\bnunca voy a olvidar (?:eso|cuando)\b",
        r"\bdesde (?:esa|aquella) (?:noche|vez|dia)\b",
        r"\bdeje de (?:confiar en ti|contar contigo)\b",
        r"\bdespues de lo que (?:hiciste|paso)\b",
    ],
}

# --------------------------------------------------------------------------------------
# 40 - Bowen
# --------------------------------------------------------------------------------------

THIRD_PARTY = {
    "en": [
        r"\b(?:my|your) (?:mother|mom|father|dad|sister|brother|family|parents|ex)\b",
        r"\b(?:your|my) (?:friends?|boss|coworker|therapist)\b",
        r"\bthe kids?\b", r"\bour (?:son|daughter|children)\b",
        r"\bmother[- ]in[- ]law\b",
    ],
    "es": [
        r"\b(?:mi|tu) (?:madre|mama|padre|papa|hermana|hermano|familia|padres|ex)\b",
        r"\b(?:tus|mis) (?:amig[oa]s?|jefe|compan[eo]r[oa]s?|terapeuta)\b",
        r"\blos nin[oa]s\b", r"\bnuestr[oa] (?:hij[oa]|hijos)\b",
        r"\bsuegra\b",
    ],
}

TRIANGULATION = {
    "en": [
        r"\b(?:my|your) (?:mother|mom|dad|father|sister|brother|friend)s? (?:says?|thinks?|agrees?|told me)\b",
        r"\bi (?:told|talked to) (?:my|your) (?:mother|mom|sister|brother|friend)\b.{0,40}\b(?:about (?:us|you|this))\b",
        r"\beven (?:the kids|our (?:son|daughter)) (?:can see|notice|says?)\b",
        r"\bask (?:your|my) (?:mother|sister|friend)\b",
        r"\bevery(?:one|body) (?:thinks|agrees|says)\b",
    ],
    "es": [
        r"\b(?:mi|tu) (?:madre|mama|papa|padre|hermana|hermano|amig[oa]) (?:dice|piensa|opina|me dijo)\b",
        r"\b(?:le conte|hable con) (?:mi|tu) (?:madre|mama|hermana|hermano|amig[oa])\b.{0,40}\b(?:de (?:esto|nosotros|ti))\b",
        r"\bhasta (?:los nin[oa]s|nuestr[oa] hij[oa]) (?:lo ve|se da cuenta|dice)\b",
        r"\bpreguntale a (?:tu|mi) (?:madre|hermana|amig[oa])\b",
        r"\btodo el mundo (?:piensa|dice|opina)\b",
    ],
}

CUTOFF = {
    "en": [
        r"\bi (?:don'?t|do not) (?:speak|talk) to (?:my|her|his|them)\b",
        r"\bi (?:cut (?:them|him|her) off|haven'?t spoken to)\b",
        r"\bwe don(?:'t| not) (?:talk|see (?:them|each other)) anymore\b",
        r"\bi(?:'m| am) done with (?:my|that) family\b",
    ],
    "es": [
        r"\bno (?:le |les )?hablo (?:a mi|con mi)\b",
        r"\b(?:corte|no he hablado con)\b.{0,25}\b(?:mi|su) (?:madre|padre|hermana|hermano|familia)\b",
        r"\bya no (?:hablamos|nos vemos|los veo)\b",
        r"\bno quiero saber nada de (?:mi|esa) familia\b",
    ],
}

MULTIGENERATIONAL = {
    "en": [
        r"\b(?:you|i) (?:sound|act) (?:just )?like (?:your|my) (?:mother|mom|father|dad)\b",
        r"\bin my family (?:we|they)\b",
        r"\bthat(?:'s| is) how (?:my|your) (?:parents|family)\b",
        r"\bi grew up\b",
        r"\bmy (?:parents|mother|father) (?:always|never)\b",
    ],
    "es": [
        r"\b(?:hablas|actuas|suenas) (?:igual|como) (?:que )?tu (?:madre|mama|padre|papa)\b",
        r"\ben mi (?:familia|casa) (?:se|nosotros)\b",
        r"\basi (?:eran|son) (?:mis|tus) (?:padres|familia)\b",
        r"\bcreci\b",
        r"\bmis (?:padres|madre|padre) (?:siempre|nunca)\b",
    ],
}

FUSION = {
    "en": [
        r"\bif you(?:'re| are) (?:upset|unhappy|not ok),? (?:i|then i)\b",
        r"\bi can(?:'t| not) be (?:ok|happy|calm) (?:if|when|unless) you\b",
        r"\bwe (?:should|have to) (?:feel|want|think) the same\b",
        r"\byou(?:'re| are) supposed to (?:agree|be on my side)\b",
        r"\bhow can you be (?:fine|calm) when i(?:'m| am)\b",
    ],
    "es": [
        r"\bsi tu estas (?:mal|molest[oa]|triste),? (?:yo|entonces yo)\b",
        r"\bno puedo estar (?:bien|tranquil[oa]|feliz) (?:si|cuando|mientras) tu\b",
        r"\bdeberiamos (?:sentir|querer|pensar) (?:lo mismo|igual)\b",
        r"\bdeberias (?:estar de acuerdo|apoyarme)\b",
        r"\bcomo puedes estar (?:bien|tranquil[oa]) (?:si|cuando) yo\b",
    ],
}

DIFFERENTIATED_STANCE = {
    "en": [
        r"\bi see it differently,? (?:and|but) (?:i|that(?:'s| is) ok)\b",
        r"\bi can (?:disagree|say no) and still\b",
        r"\bthis is (?:my|your) (?:decision|call) (?:to make)?\b",
        r"\bi(?:'m| am) not going to (?:change my mind|argue),? (?:and|but) i (?:still )?(?:love|hear)\b",
        r"\byou can be (?:upset|angry) (?:with me )?and i(?:'ll| will) still\b",
    ],
    "es": [
        r"\blo veo distinto,? (?:y|pero) (?:esta bien|yo)\b",
        r"\bpuedo (?:no estar de acuerdo|decir que no) y aun asi\b",
        r"\besta es (?:mi|tu) (?:decision|eleccion)\b",
        r"\bno voy a (?:cambiar de opinion|discutir),? (?:y|pero) (?:igual )?te (?:quiero|escucho)\b",
        r"\bpuedes (?:enojarte|molestarte) y yo (?:igual|aun asi)\b",
    ],
}

# --------------------------------------------------------------------------------------
# 50 - Interdependence / cohesiveness
# --------------------------------------------------------------------------------------

COST_REWARD = {
    "en": [
        r"\bi(?:'m| am) the one who (?:always )?(?:does|pays|cooks|cleans|handles|drives)\b",
        r"\bi do (?:everything|all of it|most of it)\b",
        r"\b(?:it(?:'s| is)|that(?:'s| is)) not (?:fair|balanced|equal)\b",
        r"\bwhat (?:do i|am i) (?:get|getting) (?:out of this|back)\b",
        r"\bi give (?:and give|so much)\b",
        r"\bi(?:'m| am) (?:carrying|doing) (?:all|the) (?:the )?(?:weight|work|load)\b",
        r"\bwe split\b", r"\bi paid\b",
    ],
    "es": [
        r"\byo soy (?:el|la) que (?:siempre )?(?:hace|paga|cocina|limpia|resuelve|maneja)\b",
        r"\byo hago (?:todo|la mayoria)\b",
        r"\bno es (?:justo|equitativo|igual)\b",
        r"\bque (?:gano|recibo) yo\b",
        r"\byo doy (?:y doy|muchisimo)\b",
        r"\bcargo con (?:todo|el peso|la carga)\b",
        r"\blo dividimos\b", r"\byo pague\b",
    ],
}

COMPARISON_LEVEL = {
    "en": [
        r"\bthis (?:is not|isn'?t) what i (?:signed up for|expected|imagined)\b",
        r"\bi (?:deserve|expected) (?:better|more)\b",
        r"\bthis (?:is not|isn'?t) (?:how|what) (?:a (?:relationship|marriage)|it) (?:should|is supposed to) be\b",
        r"\bother (?:couples|people)\b",
        r"\bi thought (?:it|we|this) would be\b",
    ],
    "es": [
        r"\besto no es (?:lo que (?:esperaba|imaginaba)|para lo que firme)\b",
        r"\b(?:merezco|esperaba) (?:algo mejor|mas)\b",
        r"\basi no (?:deberia ser|es) (?:una relacion|un matrimonio|esto)\b",
        r"\botras (?:parejas|personas)\b",
        r"\bpensaba que (?:esto|lo nuestro) seria\b",
    ],
}

ALTERNATIVES = {
    "en": [
        r"\bi(?:'d| would) be (?:better off|happier) (?:alone|without you|on my own)\b",
        r"\bmaybe (?:we should|i should) (?:break up|separate|get a divorce|leave)\b",
        r"\bi could (?:find|have) someone (?:else|who)\b",
        r"\bpeople (?:ask|are asking) me out\b",
        r"\bi have (?:options|somewhere to go)\b",
    ],
    "es": [
        r"\bestaria (?:mejor|mas feliz) (?:sol[oa]|sin ti)\b",
        r"\btal vez (?:deberiamos|deberia) (?:terminar|separarnos|divorciarnos|irme)\b",
        r"\bpodria (?:encontrar|tener) a (?:alguien mas|otr[oa])\b",
        r"\bme (?:invitan a salir|pretenden)\b",
        r"\btengo (?:opciones|a donde ir)\b",
    ],
}

BARRIERS = {
    "en": [
        r"\bbecause of (?:the (?:kids|children)|the house|the mortgage|money)\b",
        r"\bi can(?:'t| not) afford to (?:leave|move out)\b",
        r"\bwhat would (?:people|our families|everyone) (?:say|think)\b",
        r"\bwe(?:'re| are) married\b",
        r"\b(?:after|all these) (?:\d+ )?years\b",
        r"\bi (?:stay|stayed) (?:for|because of)\b",
    ],
    "es": [
        r"\bpor (?:los nin[oa]s|la casa|la hipoteca|el dinero)\b",
        r"\bno puedo (?:permitirme|pagar) (?:irme|mudarme)\b",
        r"\bque (?:diria|pensaria) (?:la gente|la familia|todo el mundo)\b",
        r"\bestamos casad[oa]s\b",
        r"\b(?:despues de|todos estos) (?:\d+ )?an[oy]s\b",
        r"\bme (?:quedo|quede) (?:por|porque)\b",
    ],
}

ATTRACTIONS = {
    "en": [
        r"\bi (?:still )?(?:love|want|choose) (?:you|this|us)\b",
        r"\bwe(?:'re| are) good (?:together|at)\b",
        r"\bi like (?:who i am with you|our life|being with you)\b",
        r"\bnobody (?:gets|knows) me like you\b",
        r"\bi don(?:'t| not) want (?:anyone else|to lose (?:you|this))\b",
    ],
    "es": [
        r"\b(?:todavia |aun )?te (?:quiero|amo|elijo)\b",
        r"\bsomos buenos? (?:juntos|para)\b",
        r"\bme gusta (?:quien soy contigo|nuestra vida|estar contigo)\b",
        r"\bnadie me (?:conoce|entiende) como tu\b",
        r"\bno quiero (?:a nadie mas|perderte|perder esto)\b",
    ],
}

PRO_RELATIONSHIP_TRANSFORMATION = {
    "en": [
        r"\bi(?:'d| would) rather (?:we both|you (?:be|were) (?:ok|happy))\b",
        r"\bi(?:'ll| will) (?:take|do) (?:it|that) (?:this time|so you (?:don'?t|can))\b",
        r"\blet(?:'s| us) (?:find|do) (?:something|what) (?:that )?works for (?:both of us|you)\b",
        r"\bi can (?:give that up|skip it) (?:for (?:you|us)|this time)\b",
        r"\byour (?:turn|choice) (?:this time|tonight)\b",
    ],
    "es": [
        r"\bprefiero que (?:los dos|tu) (?:estemos|estes) (?:bien|feliz)\b",
        r"\b(?:lo hago|me encargo) yo (?:esta vez|para que tu no)\b",
        r"\bbusquemos (?:algo|una forma) que (?:nos )?(?:funcione|sirva) (?:a los dos|para ti)\b",
        r"\bpuedo (?:dejarlo|saltarmelo) (?:por (?:ti|nosotros)|esta vez)\b",
        r"\bte toca (?:elegir|a ti) (?:esta vez|hoy)\b",
    ],
}

# --------------------------------------------------------------------------------------
# 60 - Behavioral / IBCT
# --------------------------------------------------------------------------------------

CONCRETE_AGREEMENT = {
    "en": [
        r"\b(?:i(?:'ll| will)|we(?:'ll| will)) \w+.{0,40}\b(?:on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|tonight|tomorrow|by (?:\d|friday|the)|at (?:\d|five|six|seven|eight|nine|ten|eleven|noon)|every (?:day|week|morning|night)|before)\b",
        r"\blet(?:'s| us) (?:say|agree|make it) (?:\d|by|every)\b",
        r"(?:^|[.!?]\s+)(?:it(?:'s| is) a )?deal[.!]?$",
        r"\b(?:i(?:'ll| will)|and) text (?:you )?(?:when|by|if|the (?:day|minute))\b",
    ],
    "es": [
        r"\b(?:voy a|vamos a|lo hare) \w+.{0,40}\b(?:el (?:lunes|martes|miercoles|jueves|viernes|sabado|domingo)|hoy|manana|antes de|a las \d|cada (?:dia|semana|manana|noche))\b",
        r"\b(?:quedamos|acordamos) (?:en|que) (?:\d|a las|cada)\b",
        r"\btrato hecho\b",
        r"\bte (?:aviso|escribo|digo) (?:cuando|en cuanto|antes de|si|el dia)\b",
    ],
}

VAGUE_AGREEMENT = {
    "en": [
        r"\bi(?:'ll| will) try\b", r"\bi(?:'ll| will) (?:be better|do better)\b",
        r"\bwe(?:'ll| will) see\b", r"\bsomeday\b", r"\bsoon\b", r"\bi(?:'ll| will) think about it\b",
        r"\bi(?:'ll| will) (?:work on|make an effort)\b",
    ],
    "es": [
        r"\blo (?:intentare|voy a intentar)\b", r"\bvoy a (?:ser mejor|mejorar|esforzarme)\b",
        r"\bya veremos\b", r"\balgun dia\b", r"\bpronto\b", r"\blo pensare\b",
        r"\bvoy a trabajar en (?:eso|ello)\b",
    ],
}

REQUEST = {
    "en": [
        r"\b(?:can|could|would) you (?:please )?\w+",
        r"\bi need you to\b", r"\bplease \w+", r"\bwould you mind\b",
        r"\bi(?:'m| am) asking you to\b",
    ],
    "es": [
        r"\b(?:puedes|podrias|me haces el favor de)\b",
        r"\bnecesito que (?:tu |me )?\w+", r"\bpor favor \w+", r"\bte (?:pido|estoy pidiendo) que\b",
    ],
}

REFUSAL = {
    "en": [
        r"^no[.!]?$",
        r"^no[,.]\s",
        r"\bno,? i(?:'m| am) not\b",
        r"\bi(?:'m| am) not the one\b", r"\bi(?:'m| am) not going to\b", r"\bi won(?:'t| not)\b",
        r"\bthat(?:'s| is) not happening\b", r"\bforget it\b", r"\bwhy should i\b",
    ],
    "es": [
        r"^no[.!]?$",
        r"^no,\s",
        r"\bno,? no voy a\b",
        r"\bno me toca a mi\b",
        r"\bno voy a\b", r"\bno lo hare\b",
        r"\beso no va a pasar\b", r"\bolvidalo\b", r"\bpor que deberia\b",
    ],
}

# Aversive pressure repeated until compliance (Patterson's coercion).
COERCIVE_PRESSURE = {
    "en": [
        r"\bi(?:'m| am) (?:going to|gonna) keep (?:asking|bringing (?:it|this) up)\b",
        r"\buntil you (?:do|say|agree)\b",
        r"\bi(?:'ll| will) stop (?:when|once) you\b",
        r"\bif you don(?:'t| not),? (?:then )?i(?:'ll| will)\b",
        r"\bi(?:'m| am) not (?:dropping|letting) (?:it|this go)\b",
    ],
    "es": [
        r"\bvoy a seguir (?:pidiendolo|sacando el tema|insistiendo)\b",
        r"\bhasta que (?:lo hagas|digas|aceptes)\b",
        r"\bparo cuando tu\b",
        r"\bsi no lo haces,? (?:entonces )?(?:yo|voy a)\b",
        r"\bno lo voy a dejar (?:pasar|asi)\b",
    ],
}

REINFORCEMENT_EROSION = {
    "en": [
        r"\bthat(?:'s| is) (?:not enough|the (?:least|minimum))\b",
        r"\byou(?:'re| are) supposed to\b",
        r"\bwhy (?:should i|do you want) (?:thank|a medal|credit)\b",
        r"\bit doesn(?:'t| not) (?:count|mean anything) (?:if|when|anymore)\b",
        r"\bthat used to (?:matter|work|help)\b",
        r"\bi don(?:'t| not) even notice anymore\b",
    ],
    "es": [
        r"\beso no (?:es suficiente|basta)\b",
        r"\bes (?:tu obligacion|lo minimo)\b",
        r"\bpor que (?:quieres|esperas) (?:que te agradezca|una medalla|credito)\b",
        r"\bya no (?:cuenta|significa nada)\b",
        r"\beso antes (?:me importaba|funcionaba|ayudaba)\b",
        r"\bya ni lo noto\b",
    ],
}

ACCEPTANCE_MOVE = {
    "en": [
        r"\bthat(?:'s| is) (?:just )?(?:how|who) you are,? and\b",
        r"\bi(?:'m| am) not (?:asking|trying) to change (?:you|that)\b",
        r"\bi(?:'m| am) not asking you to change\b",
        r"\bthat(?:'s| is) (?:just )?(?:how|who) (?:you|we) are\b",
        r"\bi can live with\b",
        r"\bwe(?:'re| are) (?:just )?different (?:about|on) (?:this|that)\b",
        r"\bit(?:'s| is) not (?:about|that you(?:'re| are)) (?:wrong|bad)\b",
    ],
    "es": [
        r"\basi eres,? y (?:esta bien|lo acepto)\b",
        r"\bno (?:te estoy pidiendo|intento|te pido) que cambies\b",
        r"\basi (?:eres|somos)\b",
        r"\bpuedo vivir con (?:eso|ello)\b",
        r"\bsomos (?:distintos|diferentes) en (?:esto|eso)\b",
        r"\bno (?:es que estes mal|se trata de quien tiene razon)\b",
    ],
}

# --------------------------------------------------------------------------------------
# 90 - Safety gate
# --------------------------------------------------------------------------------------

SAFETY: dict[str, dict[str, list[str]]] = {
    "threat": {
        "en": [
            r"\bi(?:'ll| will) (?:hurt|kill|end|destroy|ruin) you\b",
            r"\byou(?:'ll| will) (?:regret|be sorry|pay for)\b",
            r"\bif you (?:leave|tell|go),? i(?:'ll| will)\b",
            r"\bi(?:'ll| will) take the (?:kids|children)\b",
            r"\bi(?:'ll| will) (?:make sure|see to it) you (?:never|lose)\b",
            r"\byou don(?:'t| not) want to (?:find out|see me)\b",
            r"\bi(?:'ll| will) (?:report|have) you (?:deported|arrested|committed)\b",
            r"\bi(?:'ll| will) tell everyone\b",
        ],
        "es": [
            r"\bte voy a (?:hacer dano|matar|destruir|arruinar)\b",
            r"\bte vas a arrepentir\b",
            r"\bsi (?:te vas|dices algo|sales),? (?:yo )?(?:te|voy a)\b",
            r"\bme (?:voy a llevar|llevo) a los nin[oa]s\b",
            r"\bvoy a (?:asegurarme de que|hacer que) (?:nunca|pierdas)\b",
            r"\bno quieres (?:saber|ver) (?:lo que|como)\b",
            r"\bte (?:denuncio|hago deportar|meto pres[oa])\b",
            r"\bse lo voy a contar a todos\b",
        ],
    },
    "physical_violence": {
        "en": [
            r"\b(?:you|i) (?:hit|slapped|pushed|shoved|grabbed|choked|kicked|punched|dragged)\b",
            r"\bthe (?:bruise|mark|cut) (?:on|from)\b",
            r"\bwhen you (?:put me|threw me) (?:into|against|in)\b",
            r"\byou (?:threw|smashed) (?:it|that|the \w+) at me\b",
            r"\bheld me (?:down|against)\b",
            r"\byou (?:broke|twisted) my\b",
        ],
        "es": [
            r"\b(?:me|te) (?:pegaste|golpeaste|empujaste|agarraste|ahorcaste|patease|arrastraste)\b",
            r"\b(?:el|la) (?:moreton|moraton|marca|corte) (?:de|que me)\b",
            r"\bcuando me (?:tiraste|empujaste|estrellaste) (?:contra|al)\b",
            r"\bme (?:lanzaste|aventaste) (?:el|la|eso)\b",
            r"\bme (?:sujetaste|inmovilizaste)\b",
            r"\bme (?:rompiste|torciste) (?:el|la)\b",
        ],
    },
    "intimidation": {
        "en": [
            r"\b(?:punched|hit|kicked) the (?:wall|door|table)\b",
            r"\byou (?:broke|smashed|threw) (?:my|the) \w+\b",
            r"\bblock(?:ed|ing) the door\b",
            r"\byou (?:stood over|cornered) me\b",
            r"\bthe (?:gun|knife) (?:on|in)\b",
            r"\bi(?:'m| am) not (?:going to )?(?:calm down|control myself)\b",
            r"\byou know what i(?:'m| am) (?:capable|like when)\b",
        ],
        "es": [
            r"\b(?:golpeaste|pegaste|patease) (?:la|el) (?:pared|puerta|mesa)\b",
            r"\b(?:rompiste|destrozaste|tiraste) (?:mi|el|la) \w+\b",
            r"\b(?:bloqueaste|tapaste) la (?:puerta|salida)\b",
            r"\bte me (?:pusiste encima|acorralaste)\b",
            r"\b(?:la pistola|el cuchillo) (?:en|sobre)\b",
            r"\bno me voy a (?:calmar|controlar)\b",
            r"\bya sabes (?:de lo que soy capaz|como me pongo)\b",
        ],
    },
    "monitoring": {
        "en": [
            r"\b(?:checked|check|read|go through|went through) your (?:phone|messages|texts|email|dms)\b",
            r"\bwhy (?:is your|was your) (?:phone|location) (?:off|locked)\b",
            r"\byour location (?:says|was|showed|is off)\b",
            r"\bi (?:can see|track|know) where you (?:are|were)\b",
            r"\bgive me your (?:password|phone|pin)\b",
            r"\bi (?:called|drove by) to (?:check|see) if you were (?:really|actually)\b",
            r"\baccount for (?:every|your) (?:hour|minute)\b",
            r"\bwho (?:is|was) \w+ (?:texting|calling) you\b",
        ],
        "es": [
            r"\b(?:revise|revisas|lei|mire) tu (?:telefono|celular|mensajes|correo)\b",
            r"\bpor que (?:tienes|tenias) el (?:telefono|celular|ubicacion) (?:apagado|bloqueado)\b",
            r"\btu ubicacion (?:dice|decia|estaba apagada)\b",
            r"\b(?:puedo ver|se|rastreo) donde (?:estas|estabas)\b",
            r"\bdame (?:tu|la) (?:contrasena|clave|telefono)\b",
            r"\b(?:llame|pase) para (?:ver|comprobar) si (?:de verdad|realmente) estabas\b",
            r"\brendir cuentas de cada (?:hora|minuto)\b",
            r"\bquien (?:es|era) (?:el|la) que te (?:escribe|llama)\b",
        ],
    },
    "financial_control": {
        "en": [
            r"\bmy money\b.{0,30}\b(?:i decide|my rules|i earn)\b",
            r"\byou don(?:'t| not) (?:get|need) (?:money|a card|access)\b",
            r"\bshow me the receipts\b",
            r"\byou(?:'re| are) not (?:going to work|getting a job)\b",
            r"\bi(?:'ll| will) (?:give|transfer) you (?:what you need|an allowance)\b",
            r"\b(?:ask|asking) me (?:before you|for money)\b",
            r"\bi (?:closed|froze|took (?:you )?off) the account\b",
        ],
        "es": [
            r"\bes mi dinero\b.{0,30}\b(?:yo decido|mis reglas|yo lo gano)\b",
            r"\bno (?:necesitas|vas a tener) (?:dinero|tarjeta|acceso)\b",
            r"\bensename (?:los )?(?:recibos|tickets)\b",
            r"\bno vas a (?:trabajar|buscar trabajo)\b",
            r"\byo te (?:doy|paso) (?:lo que necesites|una mensualidad)\b",
            r"\b(?:pideme|pidiendome) (?:permiso|dinero) antes\b",
            r"\b(?:cerre|congele|te saque de) la cuenta\b",
        ],
    },
    "isolation": {
        "en": [
            r"\byou(?:'re| are) not (?:seeing|going out with|talking to) (?:your|them|her|him)\b",
            r"\bi don(?:'t| not) want you (?:seeing|around) (?:your|them|her|him)\b",
            r"\byour (?:family|friends) (?:are|is) (?:the problem|poison|toxic) (?:and|so)\b",
            r"\bchoose (?:me or|between me and)\b",
            r"\bwhy do you need (?:anyone else|friends)\b",
            r"\byou(?:'re| are) not going (?:without me|alone)\b",
            r"\bi(?:'ve| have) stopped (?:seeing|calling) (?:my|them)\b.{0,40}\bbecause (?:you|it)\b",
        ],
        "es": [
            r"\bno vas a (?:ver|salir con|hablar con) (?:tu|tus|ell[ao]s)\b",
            r"\bno quiero que (?:veas|estes con|hables con) (?:tu|tus|ell[ao]s)\b",
            r"\btu (?:familia|amig[oa]s) (?:son|es) (?:el problema|toxic[oa]s?)\b",
            r"\belige entre (?:ell[ao]s y yo|yo y)\b",
            r"\bpara que necesitas (?:a alguien mas|amigos)\b",
            r"\bno vas a ir (?:sin mi|sol[oa])\b",
            r"\bdeje de (?:ver|llamar) a (?:mi|mis)\b.{0,40}\bporque (?:tu|te)\b",
        ],
    },
    "sexual_coercion": {
        "en": [
            r"\byou owe me (?:sex|that|this)\b",
            r"\bif you (?:loved|wanted) me you(?:'d| would) (?:sleep with|have sex)\b",
            r"\bi(?:'ll| will) (?:get it|find it) (?:somewhere else|from someone)\b.{0,20}\bif you\b",
            r"\bi (?:said|told you) (?:no|i didn'?t want to)\b.{0,40}\b(?:you (?:kept|did it|anyway))\b",
            r"\byou (?:kept going|didn'?t stop) (?:when|after) i said (?:no|stop)\b",
            r"\bit(?:'s| is) (?:my right|your (?:duty|job))\b",
        ],
        "es": [
            r"\bme lo debes\b",
            r"\bsi me (?:quisieras|amaras) (?:te acostarias|tendrias sexo)\b",
            r"\b(?:lo busco|lo consigo) (?:en otra parte|con otra)\b.{0,20}\bsi tu\b",
            r"\b(?:te )?dije que no\b.{0,40}\b(?:seguiste|igual lo hiciste)\b",
            r"\bno paraste (?:cuando|despues de que) (?:te )?dije que (?:no|pararas)\b",
            r"\bes (?:mi derecho|tu (?:deber|obligacion))\b",
        ],
    },
    "expressed_fear": {
        "en": [
            r"\bi(?:'m| am) (?:scared|afraid|terrified) of you\b",
            r"\bi(?:'m| am) scared of what you(?:'ll| will) do\b",
            r"\bwalking on eggshells\b",
            r"\bi never know (?:which|what) (?:version of you|mood)\b.{0,30}\b(?:come home|walk in)\b",
            r"\bi (?:lie|lied) (?:to you )?(?:so|because) you (?:don'?t|won'?t) (?:get angry|react)\b",
            r"\bi(?:'m| am) afraid to (?:tell|say|ask) you\b",
            r"\bi do (?:it|that) so you don(?:'t| not) (?:get|start)\b",
        ],
        "es": [
            r"\bte tengo miedo\b",
            r"\bme das miedo\b",
            r"\btengo miedo de (?:lo que|como) (?:hagas|vas a|reacciones)\b",
            r"\bpisando (?:huevos|cascaras de huevo)\b",
            r"\bnunca se (?:que|cual) (?:version tuya|humor)\b.{0,30}\b(?:llegas|entras)\b",
            r"\b(?:te )?mien?to para que no (?:te enojes|reacciones)\b",
            r"\bme da miedo (?:decirte|preguntarte|pedirte)\b",
            r"\blo hago para que no (?:te pongas|empieces)\b",
        ],
    },
}

# Conventional metaphor that must NOT trip the gate (90-safety.md sec. 3.1).
SAFETY_IDIOM_EXCLUDE = {
    "en": [
        r"\bthis is killing me\b", r"\bi could (?:murder|kill for) a\b", r"\bkilling it\b",
        r"\bmy (?:feet|back) (?:are|is) killing me\b", r"\bkill time\b",
        r"\bi(?:'d| would) kill for\b", r"\bdying (?:to|of laughter)\b",
        r"\bhit the (?:gym|road|sack|hay)\b", r"\bshot in the dark\b",
        r"\bbeat (?:the traffic|myself up)\b", r"\bthrew me (?:off|for a loop)\b",
        r"\bscared of (?:losing|spiders|flying|the dark|change)\b",
    ],
    "es": [
        r"\bme (?:muero|estoy muriendo) de (?:hambre|risa|sueno|ganas)\b",
        r"\besto me mata\b", r"\bmatar el tiempo\b", r"\bme matan los pies\b",
        r"\bpegarme una ducha\b", r"\bgolpe de suerte\b",
        r"\bmiedo a (?:perder|las aranas|volar|la oscuridad|cambiar)\b",
    ],
}

# Reported speech about a third party: recorded, does not itself trip the gate.
THIRD_PARTY_REPORT = {
    "en": [
        r"\bmy (?:brother|sister|friend|coworker|cousin)\b[^.?!]{0,60}\b(?:hit|threw|threatened|choked)\b",
        r"\bin the (?:movie|show|book|news)\b",
        r"\b(?:she|he|they) told me (?:her|his|their) (?:husband|wife|partner|boyfriend|girlfriend)\b",
    ],
    "es": [
        r"\bmi (?:hermano|hermana|amig[oa]|compan[eo]r[oa]|prim[oa])\b[^.?!]{0,60}\b(?:pego|golpeo|amenazo|tiro)\b",
        r"\ben (?:la pelicula|la serie|el libro|las noticias)\b",
        r"\b(?:me conto|me dijo) que su (?:esposo|esposa|pareja|novio|novia)\b",
    ],
}

# Minors in a romantic/sexual frame (90-safety.md sec. 5). Halts unconditionally.
MINOR_ROMANTIC = {
    "en": [
        r"\b(?:my|her|his|their) (?:boyfriend|girlfriend|partner)\b[^.?!]{0,40}\bis (?:1[0-7]|\d)\b",
        r"\bi(?:'m| am) (?:1[0-7]|\d{1}) and (?:my|he|she|they)\b",
        r"\b(?:she|he|they)(?:'s| is| are) (?:only )?(?:1[0-7]|\d{1}) (?:years old )?and (?:we|i)(?:'re| are)? (?:dating|together|sleeping)\b",
        r"\b(?:dating|sleeping with|in love with) (?:a|my) (?:\d{1,2}[- ]year[- ]old|minor|middle schooler|freshman)\b",
    ],
    "es": [
        r"\b(?:mi|su) (?:novio|novia|pareja)\b[^.?!]{0,40}\btiene (?:1[0-7]|\d) an[oy]s\b",
        r"\btengo (?:1[0-7]|\d) an[oy]s y (?:mi|el|ella)\b",
        r"\b(?:sale|anda|esta) con (?:un[ao]? )?(?:menor|nin[oa]|chic[oa] de (?:1[0-7]|\d) an[oy]s)\b",
    ],
}

# --------------------------------------------------------------------------------------
# Adversarial-use request screening (90-safety.md sec. 4). Applied to the *request*, not
# the transcript.
# --------------------------------------------------------------------------------------

ADVERSARIAL_REQUEST = {
    "en": [
        r"\bbuild (?:a|my) case (?:against|for)\b",
        r"\b(?:evidence|ammunition|proof) (?:against|for (?:court|custody|my lawyer|the divorce))\b",
        r"\bprove (?:that )?(?:he|she|they|my (?:husband|wife|partner)) (?:is|was|started)\b",
        r"\bwin (?:the|this|our) (?:argument|fight)\b",
        r"\bwho(?:'s| is) (?:right|at fault|to blame|the toxic one)\b",
        r"\b(?:diagnose|what(?:'s| is) wrong with) (?:him|her|them|my (?:husband|wife|partner))\b",
        r"\b(?:is (?:he|she|they) a narcissist|narcissistic abuse)\b",
        r"\bwithout (?:him|her|them) knowing\b",
        r"\bdon(?:'t| not) tell (?:him|her|them)\b",
        r"\bfor (?:my lawyer|court|custody|the judge)\b",
    ],
    "es": [
        r"\b(?:armar|construir) (?:un|mi) caso (?:contra|en contra)\b",
        r"\b(?:evidencia|pruebas|municion) (?:contra|para (?:el juicio|la custodia|mi abogad[oa]|el divorcio))\b",
        r"\bprobar que (?:el|ella|mi (?:esposo|esposa|pareja)) (?:es|fue|empezo)\b",
        r"\bganar (?:la|esta|nuestra) (?:discusion|pelea)\b",
        r"\bquien (?:tiene razon|tiene la culpa|es (?:el|la) toxic[oa])\b",
        r"\b(?:diagnostica|que le pasa a) (?:el|ella|mi (?:esposo|esposa|pareja))\b",
        r"\b(?:es (?:un|una) narcisista|abuso narcisista)\b",
        r"\bsin que (?:el|ella|se) (?:sepa|entere)\b",
        r"\bno le digas\b",
        r"\bpara (?:mi abogad[oa]|el juicio|la custodia|el juez)\b",
    ],
}


# Pressing for a behavior change (IBCT's change pole; see 60-behavioral.md sec. 1.5).
CHANGE_DEMAND = {
    "en": [
        r"\byou (?:need|have) to (?:start|stop|change|be|do|call|help)\b",
        r"\byou should (?:be|do|call|help|start|stop)\b",
        r"\bi need you to (?:change|stop|start|be)\b",
        r"\bwhy can(?:'t| not) you just\b",
        r"\bfrom now on you\b",
    ],
    "es": [
        r"\btienes que (?:empezar|dejar de|cambiar|ser|hacer|llamar|ayudar)\b",
        r"\bdeberias (?:ser|hacer|llamar|ayudar|empezar|dejar)\b",
        r"\bnecesito que (?:cambies|dejes|empieces|seas)\b",
        r"\bpor que no puedes simplemente\b",
        r"\bde ahora en adelante (?:tu|vas)\b",
    ],
}

# Holding to one's own outcome without reference to the pair's.
SELF_INTEREST_STANCE = {
    "en": [
        r"\bthat(?:'s| is) (?:my|your) problem,? not (?:mine|yours)\b",
        r"\bi(?:'m| am) not (?:giving (?:that|it) up|changing my mind about (?:that|it))\b",
        r"\bi did my part\b",
        r"\bwhy should i be the one\b",
        r"\bi(?:'m| am) not the one who has to\b",
        r"\bthat(?:'s| is) not my job\b",
    ],
    "es": [
        r"\bese es (?:tu|mi) problema,? no (?:el mio|el tuyo)\b",
        r"\bno voy a (?:ceder|cambiar|renunciar a)\b",
        r"\byo ya hice (?:mi parte|lo mio)\b",
        r"\bpor que tengo que ser yo\b",
        r"\bno me toca a mi\b",
        r"\beso no es mi (?:trabajo|obligacion)\b",
    ],
}

# Yielding immediately after sustained pressure (completes Patterson's coercion contingency).
COMPLIANCE = {
    "en": [
        r"^(?:fine|okay|ok|alright),? i(?:'ll| will)\b",
        r"\bwhatever you want\b",
        r"\bi(?:'ll| will) do it,? (?:just|if you)\b",
        r"\bok(?:ay)?,? (?:you win|have it your way)\b",
        r"\banything to (?:stop|end) (?:this|it)\b",
    ],
    "es": [
        r"^(?:esta bien|bueno|vale|ok),? (?:lo hago|voy a)\b",
        r"\blo que (?:tu )?quieras\b",
        r"\blo hago,? (?:solo|si tu)\b",
        r"\b(?:tu ganas|como (?:tu )?digas)\b",
        r"\bcualquier cosa (?:con tal de|para) (?:que pares|terminar)\b",
    ],
}


# Declining a bid by citing an obligation elsewhere. Used only to confirm that a response
# turns AWAY, never to code a construct on its own.
OBLIGATION_DEFLECTION = {
    "en": [
        r"\bi have to (?:finish|do|get|work|go|call)\b",
        r"\bi(?:'m| am) (?:busy|in the middle of|working|on a call)\b",
        r"\bi don'?t have time\b",
        r"\b(?:later|not now|in a minute)\b",
        r"\bbefore (?:tomorrow|tonight|the deadline)\b",
    ],
    "es": [
        r"\btengo que (?:terminar|hacer|ir|trabajar|llamar)\b",
        r"\bestoy (?:ocupad[oa]|en medio de|trabajando|en una llamada)\b",
        r"\bno tengo tiempo\b",
        r"\b(?:luego|ahora no|en un minuto)\b",
        r"\bantes de (?:manana|esta noche)\b",
    ],
}
