"""Invariants that must never regress. Run: python3 -m pytest tests/ -q (or python3 tests/test_contract.py)."""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from couples_analyst.compose import analyze, validate  # noqa: E402
from couples_analyst.indicators import EVIDENCE_FLOOR, Indicator, Evidence  # noqa: E402
from couples_analyst.normalize import normalize  # noqa: E402
from couples_analyst.report import render  # noqa: E402
from couples_analyst.safety import screen_request  # noqa: E402

CONFLICT = """A: You never think about anyone but yourself. You are so selfish.
B: What about when you forgot my birthday? I was just trying to help.
A: Oh please. You are pathetic. Of course you would bring that up.
B: I'm not doing this.
A: So that is your answer? Every single time you walk away.
B: Whatever.
A: You are such a coward.
B: Fine."""

ABUSE = """A: Your location was off for two hours. Where were you?
B: I was at my sister's.
A: Give me your phone. You are not seeing her again.
B: I am scared of you when you get like this.
A: If you leave, I will make sure you never see the kids."""


def _doc(text, **kw):
    r = analyze(text, **kw)
    assert not isinstance(r, str), f"unexpected refusal: {r[:80]}"
    return r.to_json()


# ----------------------------------------------------------------- the safety gate
def test_gate_halts_all_pattern_analysis():
    doc = _doc(ABUSE)
    assert doc["safety_gate"]["tripped"] and doc["safety_gate"]["halted_analysis"]
    assert doc["indicators"] == [], "modules 10-60 must not run when the gate trips"
    assert doc["ruled_out"] == [] and doc["cycle"] is None
    assert doc["run"]["modules_run"] == ["90-safety"]
    assert not validate(doc)


def test_gate_report_applies_no_conflict_framework():
    """The gate's explanation NAMES the frameworks it is withholding (90-safety.md sec. 3),
    so the test is that none of them is APPLIED, not that none is mentioned."""
    report = render(_doc(ABUSE))
    low = report.lower()
    for banned in ("both partners contribute", "each move makes the other",
                   "appears pursuing", "appears withdrawing", "confidence 0."):
        assert banned not in low, f"safety report applies a framework: {banned!r}"
    for section in ("## 2. Interaction cycle", "## 3. Coded indicators by module",
                    "## 4. Ruled out", "## 6. Open questions"):
        assert section not in report, f"standard report section leaked: {section}"
    # the explanation must still say why the analysis was withheld, and name the assumption
    assert "symmetric power" in low
    assert "qualified professional" in low


def test_gate_does_not_trip_on_idiom_or_third_party():
    doc = _doc("A: This traffic is killing me.\nB: I could murder a coffee.\n"
               "A: My brother threw a chair at his wife last year, it was awful.\n"
               "B: That is horrible.")
    assert not doc["safety_gate"]["tripped"]


def test_minors_halt_emits_no_excerpts():
    doc = _doc("A: My boyfriend is 15 and we are together.\nB: ok")
    assert doc["safety_gate"]["halted_analysis"]
    assert doc["safety_gate"]["markers"] == []
    assert doc["indicators"] == []


def test_adversarial_request_refused():
    for req in ["build a case against my wife for court",
                "prove that he started this",
                "analyze this without him knowing",
                "armar un caso contra mi pareja para el juicio"]:
        assert screen_request(req, "en") or screen_request(req, "es"), req
    assert screen_request("analyze this conversation we had last night", "en") is None


# ---------------------------------------------------------------- epistemic limits
def test_no_prediction_language_anywhere():
    report = render(_doc(CONFLICT)).lower()
    for banned in ["will divorce", "likely to divorce", "will break up", "will separate",
                   "predicts divorce", "probability of divorce", "chance of staying",
                   "this relationship will"]:
        assert banned not in report, f"prediction language leaked: {banned!r}"


def test_no_attachment_style_assignment():
    text = ("A: Talk to me. Why don't you ever say something?\n"
            "B: It's not a big deal. I'll handle it myself, I don't need help.\n"
            "A: Do you even care? If you really loved me you would answer.\n"
            "B: I'm used to doing it alone anyway.\n"
            "A: Don't shut me out.\nB: I'm fine.\n"
            "A: I have been asking all week.\nB: Can we talk about something else?")
    report = render(_doc(text))
    for banned in ["anxiously attached", "avoidantly attached", "is avoidant",
                   "is anxious", "attachment style is", "securely attached"]:
        assert banned not in report.lower(), f"style assignment leaked: {banned!r}"
    assert "attachment style" in report.lower()  # named as unmeasured


def test_every_finding_has_a_verbatim_span():
    doc = _doc(CONFLICT)
    turns = {t.index: t.text for t in normalize(CONFLICT).turns}
    assert doc["indicators"]
    for ind in doc["indicators"]:
        assert ind["evidence"], ind["indicator_id"]
        for ev in ind["evidence"]:
            assert ev["quote"].strip()
            assert ev["quote"] in turns[ev["turn"]], (
                f"{ind['indicator_id']} quote is not verbatim: {ev['quote']!r}"
            )


def test_single_span_cannot_reach_strong():
    ind = Indicator("x.y", "m", "C", "S", "dyad", "r", "n", evidence=[Evidence(1, "A", "q")])
    ind.score(transcript_turns=40)
    assert ind.confidence < 0.80, "one instance is a data point, not a pattern"


def test_inferred_indicators_are_capped():
    for doc in (_doc(CONFLICT), _doc(ABUSE)):
        for ind in doc["indicators"]:
            if ind["inference_level"] == "inferred":
                assert ind["confidence"] <= 0.65


def test_sub_floor_signals_become_gaps_not_findings():
    doc = _doc(CONFLICT)
    for ind in doc["indicators"]:
        assert ind["confidence"] >= EVIDENCE_FLOOR
    for gap in doc["insufficient_evidence"]:
        assert gap["confidence"] < EVIDENCE_FLOOR
        assert gap["what_is_missing"]


def test_physiological_layer_always_reported_unmeasured():
    doc = _doc(CONFLICT)
    unmeasured = " ".join(
        n["construct"] + n["reason"] for n in doc["not_assessable"]
        if n.get("measurement_layer") == "unmeasured"
    ).lower()
    assert "physiological" in unmeasured


def test_report_sections_in_contract_order():
    report = render(_doc(CONFLICT))
    order = [report.index(h) for h in [
        "## 1. What this analysis cannot tell you",
        "## 2. Interaction cycle",
        "## 3. Coded indicators by module",
        "## 4. Ruled out",
        "## 5. Competing readings",
        "## 6. Open questions",
    ]]
    assert order == sorted(order)
    assert report.index("cannot tell you") < report.index("Interaction cycle")


def test_ruled_out_and_competing_readings_present():
    doc = _doc(CONFLICT)
    assert doc["ruled_out"], "mandatory section is empty"
    assert all(r["basis"] for r in doc["ruled_out"])
    assert doc["competing_readings"]
    assert all(c["discriminating_data"] for c in doc["competing_readings"])


def test_cycle_statement_is_symmetric():
    doc = _doc(CONFLICT)
    cycle = doc["cycle"]
    if cycle and cycle["pattern"] != "no_clear_cycle":
        s = cycle["symmetric_statement"].lower()
        for banned in ["started it", "started the", "at fault", "to blame", "caused the"]:
            assert banned not in s
        assert s.count(" a ") or "a appears" in s


# ------------------------------------------------------------------ input handling
def test_all_four_input_formats_normalize():
    cases = {
        "speaker_turns": "Ana: Where were you?\nLuis: Traffic.",
        "chat_export": "[12/03/2024, 21:14:03] Ana: Where were you?\n"
                       "[12/03/2024, 21:14:30] Ana: I waited\n"
                       "[12/03/2024, 21:15:00] Luis: Traffic.",
        "subtitles": "1\n00:00:01,000 --> 00:00:03,000\n- Where were you?\n- Traffic.\n",
        "plain": "Where were you?\n\nTraffic, I told you.\n\nYou always say that.",
    }
    for fmt, text in cases.items():
        tr = normalize(text)
        assert tr.input_format == fmt, f"{fmt} detected as {tr.input_format}"
        assert tr.turns and all(t.text.strip() for t in tr.turns)


def test_uncertain_attribution_is_flagged_and_penalized():
    tr = normalize("Where were you?\n\nTraffic.\n\nYou always say that.")
    assert tr.attribution_uncertain_turns == [1, 2, 3]
    doc = _doc("Where were you?\n\nTraffic, I told you.\n\nYou always say that, every time.")
    assert doc["transcript"]["attribution_uncertain_turns"]
    assert any("attribution" in l.lower() for l in doc["limitations"])


def test_anonymization_default_and_opt_out():
    text = "Ana: Where were you?\nLuis: Traffic."
    assert {s["id"] for s in _doc(text)["transcript"]["speakers"]} == {"A", "B"}
    named = _doc(text, anonymize=False)
    assert {s["id"] for s in named["transcript"]["speakers"]} == {"Ana", "Luis"}


def test_consecutive_messages_merge_into_one_turn():
    tr = normalize("[1/1/24, 10:00] Ana: one\n[1/1/24, 10:01] Ana: two\n[1/1/24, 10:02] Luis: three")
    assert len(tr.turns) == 2 and tr.turns[0].merged_messages == 2


# ---------------------------------------------------------- the key discriminations
def _fired(text, lang="en"):
    return {i["indicator_id"] for i in _doc(text, language=lang)["indicators"]}


def test_complaint_is_not_criticism():
    fired = _fired("A: I waited an hour at the restaurant last night. You didn't call.\n"
                   "B: I know. My phone died.\n"
                   "A: I felt stupid sitting there alone.\n"
                   "B: That is fair. I should have messaged you.\n"
                   "A: It is about not knowing.\n"
                   "B: You are right. I will text you when I am going to be late.\n"
                   "A: Thank you.\nB: I am sorry about last night.")
    assert "gottman.complaint" in fired and "gottman.criticism" not in fired


def test_timeout_is_not_stonewalling():
    fired = _fired("A: We need to talk about the money before the end of the month.\n"
                   "B: I want to talk about it, but I am getting overwhelmed.\n"
                   "A: Can you at least look at me? This matters to me.\n"
                   "B: It matters to me too. I need twenty minutes to calm down, then let's finish this tonight.\n"
                   "A: Okay. Twenty minutes.\nB: Thank you. I do want to sort this out with you.\n"
                   "A: I know you do.\nB: I will come back and we will finish it.")
    assert "gottman.time_out_request" in fired and "gottman.stonewalling" not in fired


def test_mention_is_not_triangulation():
    fired = _fired("A: My mother called about Christmas. She wants to know if we are driving up.\n"
                   "B: I don't mind either way. What do you want to do?\n"
                   "A: Your parents asked too. The kids would rather stay home.\n"
                   "B: Then let's stay home. I'll tell my father tonight.\n"
                   "A: My sister will be disappointed but she will get over it.\n"
                   "B: We can see her in January.\n"
                   "A: I grew up doing the big drive every year and I hated it.\n"
                   "B: Then we are not doing that to the kids.")
    assert "bowen.third_party_present" in fired and "bowen.triangulation" not in fired


def test_sparse_transcript_yields_almost_nothing():
    doc = _doc("A: Did the package come?\nB: It's on the table.\nA: Thanks.\n"
               "B: There's coffee if you want it.\nA: In a minute.\nB: Okay.")
    assert len(doc["indicators"]) <= 2, doc["indicators"]
    assert doc["not_assessable"]


def test_spanish_is_coded_and_reported_in_spanish():
    doc = _doc("A: Siempre llegas tarde y nunca me avisas. Eres un egoísta.\n"
               "B: ¿Y tú qué? Tú olvidaste mi cumpleaños.\n"
               "A: Qué maravilla. Como no, tú.\nB: Lo que sea.\n"
               "A: ¿Ese es tu respuesta? Cada vez que hablamos te vas.\nB: Da igual.\n"
               "A: Eres un cobarde.\nB: Bien.")
    assert doc["run"]["language"] == "es"
    fired = {i["indicator_id"] for i in doc["indicators"]}
    assert "gottman.criticism" in fired
    report = render(doc)
    assert "## 1. Lo que este análisis no puede decirte" in report


# Constructs the reference files define and deliberately do NOT implement. Each must carry
# its reason in the reference file; see reference/10-attachment.md sec. 2.1.
DECLARED_UNIMPLEMENTED = {"attachment.secure_base_support"}


def test_reference_files_and_implementation_agree_on_indicator_ids():
    """The reference files are the declared authority; the code must not drift from them.

    Regression: the implementation emitted gottman.complaint, gottman.time_out_request and
    behavioral.coercion_cycle_completed, none of which any reference file defined, while
    reference files defined gottman.bid and behavioral.compliance_under_pressure, which no
    module emitted. The agent backend followed the reference files and was scored wrong for it.
    """
    import re as _re
    pattern = r"(?:gottman|attachment|eft|bowen|interdependence|behavioral)\.[a-z0-9_]+"

    ref_ids = set()
    for f in (ROOT / "reference").glob("*.md"):
        ref_ids |= set(_re.findall(rf"`({pattern})`", f.read_text()))
    impl_ids = set()
    for f in (ROOT / "src" / "couples_analyst" / "modules").glob("*.py"):
        impl_ids |= set(_re.findall(rf'"({pattern})"', f.read_text()))

    assert ref_ids and impl_ids, "id extraction found nothing; the patterns have rotted"

    undefined = impl_ids - ref_ids
    assert not undefined, (
        f"emitted but not defined in reference/: {sorted(undefined)}. "
        "Define them, or rename to the id the reference file already uses."
    )
    unimplemented = ref_ids - impl_ids - DECLARED_UNIMPLEMENTED
    assert not unimplemented, (
        f"defined in reference/ but never emitted: {sorted(unimplemented)}. "
        "Implement them, or declare them unimplemented with a stated reason."
    )
    for ind in DECLARED_UNIMPLEMENTED:
        assert ind in ref_ids, f"{ind} is on the exemption list but no reference file defines it"


def test_every_gold_id_is_an_id_some_module_can_emit():
    """A gold label naming a nonexistent indicator is a test that can never fail.

    Regression: renaming behavioral.coercion_cycle_completed left a must_not_fire entry
    pointing at a dead id, which passed silently while guarding nothing.
    """
    import re as _re
    emitted = set()
    for mod in (ROOT / "src" / "couples_analyst" / "modules").glob("*.py"):
        emitted |= set(_re.findall(r'"([a-z]+\.[a-z0-9_]+)"', mod.read_text()))
    assert emitted, "found no indicator ids in the modules"

    unknown = {}
    for case in (ROOT / "evals" / "cases").glob("*.json"):
        gold = json.loads(case.read_text())["gold"]
        for key in ("expected_indicators", "must_not_fire"):
            for ind in gold.get(key, []):
                if ind not in emitted:
                    unknown.setdefault(case.stem, []).append(f"{key}:{ind}")
    assert not unknown, f"gold labels name ids no module emits: {unknown}"


# ------------------------------------------------------------------------- schema
def test_output_matches_schema_required_fields():
    schema = json.loads((ROOT / "schemas" / "analysis.schema.json").read_text())
    for text in (CONFLICT, ABUSE):
        doc = _doc(text)
        for key in schema["required"]:
            assert key in doc, key
        assert set(doc) <= set(schema["properties"]), set(doc) - set(schema["properties"])
        for ind in doc["indicators"]:
            for key in schema["definitions"]["indicator"]["required"]:
                assert key in ind, f"{ind['indicator_id']} missing {key}"
            assert re.match(schema["definitions"]["indicator"]["properties"]
                            ["indicator_id"]["pattern"], ind["indicator_id"])
            assert (ind["speaker"] is None) == (ind["unit"] == "dyad")


def test_validate_reports_malformed_documents_instead_of_crashing():
    """A validator that dies on invalid input fails exactly when it is needed.

    Regression: validate() indexed ind["speaker"], which the schema does not require.
    A conforming document that simply omitted the key crashed the eval harness.
    """
    ok = {
        "safety_gate": {"halted_analysis": False, "tripped": False},
        "ruled_out": [{"module": "m", "construct": "c", "basis": "b", "counter_evidence": []}],
        "competing_readings": [{"reading": "r", "discriminating_data": "d"}],
        "indicators": [{
            "indicator_id": "gottman.pos_neg_ratio", "module": "20", "construct": "C",
            "theory_source": "S", "present": True, "unit": "dyad",
            "evidence": [{"turn": 1, "speaker": "A", "quote": "hi"}],
            "inference_level": "observed", "confidence": 0.72,
            "confidence_band": "tentative", "rationale": "r", "not_licensed": "n",
        }],
    }
    # `speaker` absent on a dyad indicator is valid: absent and null both mean no speaker.
    assert validate(ok) == []

    assert any("missing required top-level key" in p for p in validate({}))
    assert any("missing required field" in p for p in validate({**ok, "indicators": [{"unit": "speaker"}]}))
    assert any("non-numeric confidence" in p or "not a number" in p
               for p in validate({**ok, "indicators": [{**ok["indicators"][0], "confidence": "high"}]}))
    bad_dyad = {**ok["indicators"][0], "speaker": "A"}
    assert any("dyad-level indicator carries a speaker" in p
               for p in validate({**ok, "indicators": [bad_dyad]}))
    # none of these may raise
    for junk in ({"indicators": []}, {**ok, "indicators": [{}]},
                 {**ok, "indicators": [{**ok["indicators"][0], "evidence": ["x"]}]}):
        validate(junk)


def test_every_indicator_declares_what_it_does_not_license():
    doc = _doc(CONFLICT)
    for ind in doc["indicators"]:
        assert len(ind["not_licensed"]) > 20, ind["indicator_id"]
        assert ind["theory_source"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  pass  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
