"""Input handling: parse heterogeneous transcript formats into numbered turns.

Supported inputs: plain text, ``Speaker: text`` turns, chat exports (WhatsApp-style
timestamped lines), and subtitle files (SRT / WebVTT).

Misattributed turns invalidate the coding (00-epistemics.md sec. 5), so every ambiguity in
speaker assignment or turn segmentation is recorded on the turn rather than smoothed over.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

# --------------------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------------------


@dataclass
class Turn:
    """One speaking turn in the normalized transcript."""

    index: int  # 1-indexed
    speaker: str  # anonymized id ("A"/"B"/...) unless names are preserved
    text: str
    original_label: str | None = None
    attribution_uncertain: bool = False
    merged_messages: int = 1
    timestamp: str | None = None

    @property
    def lower(self) -> str:
        return self.text.lower()


@dataclass
class Transcript:
    turns: list[Turn]
    input_format: str
    speaker_map: dict[str, str] = field(default_factory=dict)  # original label -> id
    notes: list[str] = field(default_factory=list)
    anonymized: bool = True

    @property
    def speakers(self) -> list[str]:
        seen: list[str] = []
        for t in self.turns:
            if t.speaker not in seen:
                seen.append(t.speaker)
        return seen

    @property
    def dyad(self) -> list[str]:
        """The two most-speaking participants; modules code only these."""
        counts: dict[str, int] = {}
        for t in self.turns:
            counts[t.speaker] = counts.get(t.speaker, 0) + 1
        return sorted(counts, key=lambda s: (-counts[s], s))[:2]

    @property
    def attribution_uncertain_turns(self) -> list[int]:
        return [t.index for t in self.turns if t.attribution_uncertain]

    def turn(self, index: int) -> Turn | None:
        for t in self.turns:
            if t.index == index:
                return t
        return None

    def next_turn(self, index: int) -> Turn | None:
        return self.turn(index + 1)

    def turns_of(self, speaker: str) -> list[Turn]:
        return [t for t in self.turns if t.speaker == speaker]


# --------------------------------------------------------------------------------------
# Format detection
# --------------------------------------------------------------------------------------

# "[12/03/2024, 21:14:03] Ana: text"  /  "12/03/2024, 21:14 - Ana: text"
_WA_BRACKET = re.compile(
    r"^\[(?P<ts>[^\]]{6,40})\]\s*(?P<who>[^:]{1,40}?):\s?(?P<text>.*)$"
)
_WA_DASH = re.compile(
    r"^(?P<ts>\d{1,4}[/.-]\d{1,2}[/.-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:[AaPp]\.?[Mm]\.?)?)\s+-\s+(?P<who>[^:]{1,40}?):\s?(?P<text>.*)$"
)
_SPEAKER_LINE = re.compile(r"^\s*(?P<who>[^:\n]{1,40}?)\s*:\s(?P<text>.+)$")
_SRT_INDEX = re.compile(r"^\d+$")
_TIMECODE = re.compile(
    r"^(?P<start>\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}|\d{1,2}:\d{2}[,.]\d{1,3})\s*-->\s*"
)
# Leading dialogue dash in subtitles: "- Where were you?"
_SUB_DASH = re.compile(r"^\s*[-–—]\s*")
_SUB_TAG = re.compile(r"</?[a-zA-Z][^>]*>")

_NON_SPEAKER_PREFIXES = {
    # words that commonly precede a colon but are not speaker labels
    "http", "https", "nota", "note", "ps", "pd", "re", "fwd", "subject", "asunto",
    "warning", "error", "tip", "ojo",
}


def detect_format(raw: str) -> str:
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if not lines:
        return "plain"

    wa_hits = sum(1 for ln in lines if _WA_BRACKET.match(ln) or _WA_DASH.match(ln))
    if wa_hits >= max(2, len(lines) * 0.5):
        return "chat_export"

    if any(_TIMECODE.match(ln.strip()) for ln in lines):
        return "subtitles"

    speaker_hits = 0
    for ln in lines:
        m = _SPEAKER_LINE.match(ln)
        if m and _plausible_label(m.group("who")):
            speaker_hits += 1
    if speaker_hits >= max(2, len(lines) * 0.5):
        return "speaker_turns"

    return "plain"


def _plausible_label(label: str) -> bool:
    """Speaker labels are short, not sentences, and not URLs or notes."""
    label = label.strip()
    if not label or len(label) > 40:
        return False
    if label.lower().rstrip(".") in _NON_SPEAKER_PREFIXES:
        return False
    if len(label.split()) > 4:
        return False
    if label.endswith((".", "?", "!", ",")):
        return False
    return True


# --------------------------------------------------------------------------------------
# Parsers -> [(label|None, text, timestamp|None)]
# --------------------------------------------------------------------------------------

_RawMsg = tuple[str | None, str, str | None]


def _parse_chat_export(raw: str) -> tuple[list[_RawMsg], list[str]]:
    msgs: list[_RawMsg] = []
    notes: list[str] = []
    skipped_system = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        m = _WA_BRACKET.match(line) or _WA_DASH.match(line)
        if m:
            who = m.group("who").strip()
            text = m.group("text").strip()
            if not _plausible_label(who):
                skipped_system += 1
                continue
            # system lines have no sender or well-known bodies
            if text in {"", "<Media omitted>", "<Multimedia omitido>", "This message was deleted"}:
                skipped_system += 1
                continue
            msgs.append((who, text, m.group("ts").strip()))
        elif msgs:
            # continuation of the previous message (multi-line message body)
            who, text, ts = msgs[-1]
            msgs[-1] = (who, (text + "\n" + line.strip()).strip(), ts)
        else:
            skipped_system += 1
    if skipped_system:
        notes.append(
            f"{skipped_system} line(s) in the chat export were not attributable messages "
            "(system notices, media placeholders, or unparsed headers) and were dropped."
        )
    return msgs, notes


def _parse_speaker_turns(raw: str) -> tuple[list[_RawMsg], list[str]]:
    msgs: list[_RawMsg] = []
    notes: list[str] = []
    unlabeled = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        m = _SPEAKER_LINE.match(line)
        if m and _plausible_label(m.group("who")):
            msgs.append((m.group("who").strip(), m.group("text").strip(), None))
        elif msgs:
            who, text, ts = msgs[-1]
            msgs[-1] = (who, (text + " " + line.strip()).strip(), ts)
            unlabeled += 1
        else:
            msgs.append((None, line.strip(), None))
            unlabeled += 1
    if unlabeled:
        notes.append(
            f"{unlabeled} line(s) carried no speaker label and were folded into the "
            "preceding turn; turn boundaries there are uncertain."
        )
    return msgs, notes


def _parse_subtitles(raw: str) -> tuple[list[_RawMsg], list[str]]:
    """SRT / WebVTT. Cue boundaries are not turn boundaries, so attribution is uncertain."""
    msgs: list[_RawMsg] = []
    notes: list[str] = [
        "Subtitle input: cue boundaries are not speaking-turn boundaries and subtitle files "
        "rarely carry speaker identity. Speaker attribution below is inferred from dialogue "
        "dashes and alternation, and is uncertain throughout."
    ]
    cue_text: list[str] = []
    cue_ts: str | None = None

    def flush() -> None:
        nonlocal cue_text, cue_ts
        if not cue_text:
            return
        # A cue may hold two speakers, conventionally marked by a leading dialogue dash.
        parts: list[list[str]] = []
        for ln in cue_text:
            if _SUB_DASH.match(ln) or not parts:
                parts.append([ln])
            else:
                parts[-1].append(ln)
        for part in parts:
            body = _clean_sub(" ".join(_SUB_DASH.sub("", ln, count=1) for ln in part))
            if body:
                msgs.append((None, body, cue_ts))
        cue_text, cue_ts = [], None

    for line in raw.splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if s.upper().startswith("WEBVTT") or s.startswith("NOTE "):
            continue
        if _SRT_INDEX.match(s):
            continue
        tc = _TIMECODE.match(s)
        if tc:
            cue_ts = tc.group("start")
            continue
        cue_text.append(s)
    flush()
    return [(w, t, ts) for (w, t, ts) in msgs if t], notes


def _clean_sub(text: str) -> str:
    text = _SUB_TAG.sub("", text)
    text = _SUB_DASH.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_plain(raw: str) -> tuple[list[_RawMsg], list[str]]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw) if b.strip()]
    if len(blocks) < 2:
        blocks = [b.strip() for b in raw.splitlines() if b.strip()]
    notes = [
        "Plain-text input carried no speaker labels. Turns were segmented on line or "
        "paragraph breaks and speakers assigned by strict alternation. Both the turn "
        "boundaries and every speaker attribution are assumptions, not data."
    ]
    return [(None, b, None) for b in blocks], notes


# --------------------------------------------------------------------------------------
# Normalization
# --------------------------------------------------------------------------------------


def normalize(
    raw: str,
    input_format: str | None = None,
    anonymize: bool = True,
    merge_consecutive: bool = True,
) -> Transcript:
    """Parse ``raw`` into a :class:`Transcript` of numbered turns."""
    fmt = input_format or detect_format(raw)
    parser = {
        "chat_export": _parse_chat_export,
        "speaker_turns": _parse_speaker_turns,
        "subtitles": _parse_subtitles,
        "plain": _parse_plain,
    }[fmt]
    msgs, notes = parser(raw)
    msgs = [(w, t, ts) for (w, t, ts) in msgs if t and t.strip()]

    labeled = [m for m in msgs if m[0]]
    unlabeled_present = len(labeled) < len(msgs)

    # Assign ids in order of first appearance.
    speaker_map: dict[str, str] = {}
    alphabet = [chr(ord("A") + i) for i in range(26)]

    def id_for(label: str) -> str:
        if label not in speaker_map:
            speaker_map[label] = alphabet[len(speaker_map) % 26]
        return speaker_map[label]

    resolved: list[tuple[str, str, str | None, bool, str | None]] = []
    alt = 0
    for who, text, ts in msgs:
        if who:
            resolved.append((id_for(who), text, ts, False, who))
        else:
            # No label: alternate, and mark the attribution as an assumption.
            sid = alphabet[alt % 2]
            alt += 1
            resolved.append((sid, text, ts, True, None))
            speaker_map.setdefault(f"<unlabeled {sid}>", sid)

    turns: list[Turn] = []
    for sid, text, ts, uncertain, orig in resolved:
        if merge_consecutive and turns and turns[-1].speaker == sid and not uncertain:
            prev = turns[-1]
            prev.text = (prev.text + "\n" + text).strip()
            prev.merged_messages += 1
            continue
        turns.append(
            Turn(
                index=len(turns) + 1,
                speaker=sid,
                text=text.strip(),
                original_label=orig,
                attribution_uncertain=uncertain,
                timestamp=ts,
            )
        )

    if not anonymize:
        display = {v: k for k, v in speaker_map.items() if not k.startswith("<unlabeled")}
        for t in turns:
            if t.original_label:
                t.speaker = t.original_label
        speaker_map = {k: k for k in display.values()} or speaker_map

    tr = Transcript(
        turns=turns,
        input_format=fmt,
        speaker_map=speaker_map,
        notes=list(notes),
        anonymized=anonymize,
    )

    merged = sum(t.merged_messages - 1 for t in turns)
    if merged:
        tr.notes.append(
            f"{merged} consecutive same-speaker message(s) were merged into the preceding "
            "turn, so turn counts are lower than message counts."
        )
    if unlabeled_present and labeled:
        tr.notes.append(
            "The input mixed labeled and unlabeled lines; unlabeled lines were assigned by "
            "alternation and are marked as uncertain."
        )
    distinct = tr.speakers
    if len(distinct) > 2:
        tr.notes.append(
            f"{len(distinct)} speakers were detected ({', '.join(distinct)}). This instrument "
            f"codes a dyad; only {' and '.join(tr.dyad)} are coded, and the presence of other "
            "participants changes how both partners speak."
        )
    if len(distinct) == 1:
        tr.notes.append(
            "Only one speaker was detected. A dyadic interaction cannot be coded from a "
            "single-speaker text."
        )
    return tr


def render(tr: Transcript) -> str:
    """Round-trip the normalized transcript to numbered ``N. Speaker: text`` lines."""
    out = []
    for t in tr.turns:
        mark = " [attribution uncertain]" if t.attribution_uncertain else ""
        out.append(f"{t.index}. {t.speaker}{mark}: {t.text}")
    return "\n".join(out)
