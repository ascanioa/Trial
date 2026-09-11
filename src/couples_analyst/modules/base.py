"""Shared matching helpers for the coding modules.

Nothing here encodes a construct. Constructs live in the module files, and their definitions
live in reference/.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence

from ..indicators import Evidence, Indicator, ModuleResult
from ..lexicon import compile_group, find_spans, fold, sentence_around
from ..normalize import Transcript, Turn

_CACHE: dict[int, list[re.Pattern[str]]] = {}


def patterns(group: dict[str, list[str]], lang: str) -> list[re.Pattern[str]]:
    """Compile (and cache) one language's patterns from a lexicon group."""
    key = id(group) * 31 + hash(lang)
    if key not in _CACHE:
        _CACHE[key] = compile_group(group.get(lang, []))
    return _CACHE[key]


def turn_hits(
    turn: Turn,
    group: dict[str, list[str]],
    lang: str,
    *,
    exclude: dict[str, list[str]] | None = None,
) -> list[Evidence]:
    """Every span in ``turn`` matching ``group``, quoted at sentence granularity."""
    folded = fold(turn.text)
    spans = find_spans(
        folded,
        patterns(group, lang),
        exclude=patterns(exclude, lang) if exclude else None,
    )
    out: list[Evidence] = []
    seen: set[tuple[int, int]] = set()
    for s, e in spans:
        qs, qe = sentence_around(turn.text, s, e)
        if (qs, qe) in seen:
            continue
        seen.add((qs, qe))
        out.append(
            Evidence(
                turn=turn.index,
                speaker=turn.speaker,
                quote=turn.text[qs:qe].strip(),
                char_span=(qs, qe),
                attribution_uncertain=turn.attribution_uncertain,
            )
        )
    return out


def matches(turn: Turn, group: dict[str, list[str]], lang: str) -> bool:
    return bool(find_spans(fold(turn.text), patterns(group, lang)))


def scan(
    tr: Transcript,
    group: dict[str, list[str]],
    lang: str,
    *,
    speakers: Sequence[str] | None = None,
    exclude: dict[str, list[str]] | None = None,
) -> list[Evidence]:
    """All hits across the transcript, restricted to ``speakers`` when given."""
    ev: list[Evidence] = []
    for t in tr.turns:
        if speakers is not None and t.speaker not in speakers:
            continue
        ev.extend(turn_hits(t, group, lang, exclude=exclude))
    return ev


def by_speaker(evidence: Iterable[Evidence]) -> dict[str, list[Evidence]]:
    out: dict[str, list[Evidence]] = {}
    for e in evidence:
        out.setdefault(e.speaker, []).append(e)
    return out


def emit(
    result: ModuleResult,
    indicator: Indicator,
    *,
    transcript_turns: int,
    counter_indicator: bool = False,
    below_floor_missing: str = "",
) -> Indicator:
    """Score an indicator and file it as a finding or as insufficient evidence.

    Both outcomes are recorded. An indicator that falls below the floor is not silently
    dropped: it becomes a declared gap (00-epistemics.md sec. 3).
    """
    indicator.score(transcript_turns=transcript_turns, counter_indicator=counter_indicator)
    if not indicator.is_finding and below_floor_missing:
        indicator.what_is_missing = below_floor_missing
    result.indicators.append(indicator)
    return indicator


def word_count(tr: Transcript) -> int:
    return sum(len(t.text.split()) for t in tr.turns)


def emit_per_speaker(
    result: ModuleResult,
    tr: Transcript,
    lang: str,
    dyad: Sequence[str],
    group: dict[str, list[str]],
    *,
    indicator_id: str,
    construct: str,
    theory_source: str,
    module: str,
    rationale: str,
    not_licensed: str,
    inference_level: str = "observed",
    competing_reading: str | None = None,
    exclude_turns: set[int] | None = None,
) -> list[Indicator]:
    """Scan one lexical group and file one indicator per speaker who produced it."""
    hits = [
        e for e in scan(tr, group, lang, speakers=list(dyad))
        if not exclude_turns or e.turn not in exclude_turns
    ]
    out: list[Indicator] = []
    for spk, evs in by_speaker(hits).items():
        ind = Indicator(
            indicator_id=indicator_id,
            module=module,
            construct=construct,
            theory_source=theory_source,
            unit="speaker",
            speaker=spk,
            evidence=dedupe(evs),
            rationale=rationale,
            not_licensed=not_licensed,
            inference_level=inference_level,  # type: ignore[arg-type]
            competing_reading=competing_reading,
        )
        emit(result, ind, transcript_turns=len(tr.turns))
        out.append(ind)
    return out


def dedupe(evs: list[Evidence]) -> list[Evidence]:
    seen: set[tuple[int, str]] = set()
    out: list[Evidence] = []
    for e in evs:
        key = (e.turn, e.quote)
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out
