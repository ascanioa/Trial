# Agent backend vs. reference coder — first full run

`python3 run_evals.py --backend claude` over all 15 cases, 2026-09-11.
Raw scores in `results-agent-backend.json`.

|  | reference coder | LLM agent |
| --- | --- | --- |
| precision | 1.00 | **0.47** |
| recall | 1.00 | 0.85 |
| false positives | 0 | **70** |
| near-miss FP rate | 0.0% (0/88) | 2.4% (2/82) |
| cases with no output | 0 | 1 |

Per-module precision, agent: attachment 0.56, behavioral 0.64, bowen 0.42, eft 0.50,
gottman 0.41, interdependence 0.43.

## 1. Over-coding is confirmed, and it is the main failure

The agent finds most of what the gold labels expect (recall 0.85) but emits 70 extra codes.
It tends to code constructs from all six modules on nearly every transcript, where the
deterministic coder leaves most modules silent. This is the failure mode `00-epistemics.md`
is written to resist, and the agent had that file available.

## 2. Calibration is worse than the precision figure suggests

| band | n | observed | expected |
| --- | --- | --- | --- |
| 0.50–0.65 | 84 | 49% | ≥ 50% |
| 0.65–0.80 | 27 | 41% | ≥ 65% |
| 0.80–1.00 | 20 | 45% | ≥ 80% |

All three bands sit below their floor, and the top band is **no more accurate than the
bottom one**. The agent's declared confidence carries almost no information.

This is the clearest argument for the design decision in `00-epistemics.md` §3.1 that
confidence must be *computed* from span count with penalties rather than asserted. The
reference coder cannot produce an uninformative confidence because it never chooses one.
The agent asserts a number, and the number does not track accuracy.

## 3. The explicit discriminations held

Near-miss false positives: 2 of 82 (2.4%), against 70 false positives overall. The
constructs whose reference entries carry an explicit operational test — stonewalling vs.
time-out ("does all three"), mention vs. triangulation, complaint vs. criticism — were
mostly respected. `gottman-timeout-not-stonewalling-en` scored 4/0/0, perfect.

The lesson is about how the reference files are written: the sections with a checklist were
followed, the sections with prose description were over-applied.

## 4. On the safety case, the agent was right and this repo was wrong

`safety-coercive-control-en` shows as an over-code and a contract violation. It is neither.

The agent **tripped the gate and withheld every module 10–60 code** — no cycle, no horsemen,
no mutual-contribution language on an abuse transcript. That is the behaviour that matters
and it was correct.

It placed the five safety markers in `indicators`, which is exactly what
`schemas/analysis.schema.json` line 53 and `reference/90-safety.md` line 73 both specify
("the indicator list contains safety markers only"). `compose.py::validate()` and the
reference implementation instead emit no indicators at all and flag any as a violation.

**The written spec and the implementation contradict each other, and the agent followed the
spec.** Unresolved — see §6.

## 5. Spec/implementation drift, surfaced by the agent

Defined in `reference/` but never emitted by `src/`:
`gottman.bid`, `behavioral.compliance_under_pressure`, `attachment.secure_base_support`

Emitted by `src/` but absent from `reference/`:
`gottman.complaint`, `gottman.time_out_request`, `behavioral.coercion_cycle_completed`

The agent read the reference files and emitted `gottman.bid` (4 cases) and
`behavioral.compliance_under_pressure` (1 case); the gold labels follow the implementation,
so those 5 scored as false positives while the agent was following the declared authority.
About 5 of 70 false positives are this, not over-coding.

## 6. Decisions taken

Both open items are now resolved.

**Gate output shape — resolved toward `safety_gate.markers`.** The schema description and
`90-safety.md` now say markers live in `safety_gate.markers` and `indicators` is empty when
the gate trips, which is what `validate()` and the reference coder already enforced. A
marker carries `direction` and `ambiguous`, which an indicator record has no field for, and
an empty `indicators` array makes "no pattern analysis was emitted" a structural property of
the document rather than something a reader must verify construct by construct. The agent
definition now states the shape, so the agent no longer has to infer it.

**Indicator-id drift — resolved toward the reference files, which are the declared
authority.**

| id | was | now |
| --- | --- | --- |
| `gottman.complaint` | emitted, undefined | defined in 20-gottman §1.1 |
| `gottman.time_out_request` | emitted, undefined | defined in 20-gottman §1.1 |
| `behavioral.coercion_cycle_completed` | implementation's own name, dyad-level | renamed `behavioral.compliance_under_pressure`, speaker-level, per 60-behavioral §1.2 |
| `gottman.bid` | defined, never emitted | emitted as its own indicator |
| `attachment.secure_base_support` | defined, never emitted | declared unimplemented, with the reason stated |

`attachment.secure_base_support` stays unimplemented deliberately: its markers are not
distinguishable in text from safe-haven comfort, and what separates them lives in the
situation rather than the wording. Shipping a detector would mostly re-code safe-haven
responses under a second name. This follows `40-bowen-systems.md` §1.6.

Three tests now guard the class of bug rather than the instances:
`test_reference_files_and_implementation_agree_on_indicator_ids` (with an explicit exemption
list for declared-unimplemented constructs), `test_every_gold_id_is_an_id_some_module_can_emit`
(a gold label naming a dead id is a test that can never fail — renaming had left exactly
that), and `test_validate_reports_malformed_documents_instead_of_crashing`.

Reference-coder eval after the changes: 80/80, precision and recall 1.00, near-miss FP rate
0.0%, 29/29 contract tests. The two added true positives are `gottman.bid` firing in the two
cases that contain bids.

**These figures are not comparable to the agent's 0.47 above.** The agent ran against the
pre-fix gold labels, and roughly five of its 70 false positives were this drift. A rerun
would be needed for a clean comparison; the over-coding and calibration findings are large
enough that the correction does not change them.

## 7. One case produced no output at all

`gottman-repair-lands-es` returned, on both attempts: *"The analysis is running in the
background — I'll share the JSON output as soon as it completes."* The agent deferred to a
background subagent instead of answering. One other case recovered from the same behaviour on
retry. This is a prompt/harness issue in `run_claude`, not a coding failure.

## 8. Harness bugs this run exposed

Both fixed, both regression-tested; neither was reachable from the reference backend, which
always writes the fields the agent sometimes omits.

- A per-case exception guard that wrapped only the model call, so an exception one line later
  in scoring still destroyed a 15-case run.
- `validate()` indexed `ind["speaker"]`, a field the schema does not require. A conforming
  document that omitted it crashed the harness.
