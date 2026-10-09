# Slice 4: local Qwen evidence-selection spike

Status: fifteen injected HTTP/application-boundary checks passed. Genuine v3 ran
four supported examples successfully; model-only identity abstention still failed.
The bounded event adapter is ready for integration. General model-question quality,
live failure acceptance and offline acceptance remain incomplete.
No model responses are claimed from fixtures. No dependencies were installed.

## Owner Terminal test

Keep the foreground Ollama Terminal running. Use the other Terminal:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
.venv/bin/python scripts/llm_spike.py --run --cold --with-vision
```

The incidental browser `/favicon.ico` 404 is not a generation failure.
This command explicitly unloads pinned Qwen before the first request, then sends
four genuine local calls on synthetic records: person observation, repeated bell,
impacts/contact with unavailable camera and a repeated bell example for warm timing.
The unsupported identity question is now an application guard check, not a model
call. Even records labelled laptop webcam are
synthetic in this runner. Concurrent genuine detector calls use blank pixels at
up to 5 Hz. No camera, downloads, services or media storage are started.
The full report is saved to ignored `.runtime/llm-session.json`; paste the output
back for review. Each complete adapter request has a 45-second deadline.
No Codex or Ollama restart is needed.

Without `--run`, the script prints its plan only. Omit `--with-vision` to isolate
Qwen if graphics initialization fails. Without `--cold`, first-request timing
does not establish a cold load.

## Response contract

[local_llm.py](../backend/doorsense/local_llm.py) uses only
`http://127.0.0.1:11434`, ignores proxies and refuses redirects. It verifies the
pinned daemon version and served model digest before generation. It never pulls
models, uses cloud inference or supplies frames/tools. Settings are `think: false`,
`stream: false`, `num_ctx: 2048`, `num_predict: 128`, temperature 0 and keep-alive
60 seconds. Input is bounded to eight timestamped facts, their provenance,
existing rule severity/reason, uncertainties and a short question.

Prompt `evidence-selection-v3` requests only `fact_ids` under a dynamic JSON schema.
The explicit marker `["unavailable"]` means no supported answer. It must be selected
alone, cannot be a supplied fact ID and is normalized to an empty evidence list.
The app derives `answer_kind`; empty wire lists and mixed marker/fact selections fail.
Validation rejects invented/duplicate IDs, extra fields, inconsistent
answers, malformed JSON, thinking/tool calls, wrong model, incomplete/truncated
generation and responses above 64 KiB. Qwen selects relevant records; DoorSense
renders their exact original wording and source labels. Output source is
`qwen_evidence_selection`, with `wording_source: supplied_facts_and_template`.
This initial contract provides model-selected evidence, not unrestricted generated
prose. Original severity, rule reason and uncertainties remain authoritative.

Existing IDs can still be irrelevant to a question. Schema validity does not
prove semantic relevance, completeness or correctness of supplied records.
The runner checks required selections on these examples; broader held-out tests
and manual review remain necessary. Event history retrieval and console integration
are future work. Identity and intent are not established.

## Failures and concurrency

Missing model, daemon failure, HTTP error, timeout or unsupported output returns
labelled `template_fallback`, the reason, original evidence and uncertainties.
Fallback never counts as Qwen generation. One request per adapter instance may
run at a time; overlapping calls receive busy fallback rather than entering a
queue. The application must share one instance and schedule its async calls
separately from camera/event processing. Live application responsiveness is pending.

Expired contexts and changed event revisions are discarded before/after generation.
Integrated callers must supply `is_current` to check the active event ID/revision;
the spike uses fixed contexts with a 60-second expiry. Cancellation releases the
client slot. Client timeout does not prove server inference stopped; the prepared
Ollama daemon separately bounds parallel inference/model loading to one slot.

## Evidence boundaries

[Fixture tests](../scripts/test_local_llm.py) run without a daemon or networking:

```sh
.venv/bin/python scripts/test_local_llm.py
```

The owner report records synthetic input, question, selected facts, source,
expected-selection result, wall latency and Ollama load/evaluation timings/counts.
`passed_bounded_examples` requires four genuine generation cases plus one explicit
application guard to meet expectations; check_kind/source distinguish them.
Rejected output/fallback requires review. Offline acceptance remains separate.

Memory distinguishes spike process peak RSS from sampled aggregate RSS of the
repository Ollama daemon and child runners. Missing samples are unavailable,
not zero; sampling can miss peaks. Shared/GPU mappings mean these values must
not be summed as actual physical unified RAM. Loaded-model size/VRAM metadata is
recorded separately. Concurrent blank-pixel timings do not prove camera quality,
live webcam responsiveness or performance of the complete application.

Official references checked 2026-10-09: [chat API](https://docs.ollama.com/api/chat),
[structured outputs](https://docs.ollama.com/capabilities/structured-outputs),
[thinking](https://docs.ollama.com/capabilities/thinking).

## First owner run and diagnostic rerun

The following run/version sections preserve history. Earlier rerun requests are
superseded by the final application question boundary below and the
[Slice 5 handoff](HANDOFF_SLICE_5.md). No routine spike rerun is required to begin
console design; the latest model-only failure remains recorded honestly.

The first report (`needs_review`) met arrival and urgent example expectations.
Cold first-request wall time was 2914.58 ms (2072.74 ms model load); accepted warm
urgent wall time was 599.09 ms. Bell, identity question and warm bell each produced
invalid/unsupported-response fallback. Their rejection cause was not recorded,
so it is not established. Fallback latency is not successful-answer latency.
Concurrent blank-pixel vision: 24 calls, median 17.71 ms, P95 22.62 ms, no errors.
Spike peak RSS was 172.9 MB; sampled daemon/children max RSS was 546.5 MB. Complete
application responsiveness and physical unified memory remain unverified.

The original aggregate report is preserved locally at ignored
`.runtime/llm-session-first-run.json`. The runner now requests bounded rejection
diagnostics (raw content, completion reason and validation error) only for its
synthetic records. Diagnostics are opt-in and unvalidated; they must never be used
as resident-facing answer text. Response validation remains unchanged.

Repeat the command above and return the rejection diagnostics/final report.
No restart or installation is required. Prompt/schema changes should follow the
actual rejection evidence rather than assuming a cause from these timings.

## Confirmed v1 rejection and v2 correction

The diagnostic owner rerun again met 2/5 expectations. All three rejections
combined unavailable with nonempty fact IDs (bell/person), with valid completion
and no thinking/tool calls. This contradicted the two-field v1 response contract.
Cold first request took 2250.98 ms; accepted warm urgent took 586.88 ms. Concurrent
blank vision: 20 samples, median 18.84 ms, P95 41.89 ms, no errors.

V2 removes the redundant model-generated answer_kind field, explicitly permits
empty lists and adds one-fact bell and unsupported-identity examples. Invented IDs,
duplicates, extra fields and old contradictory v1 outputs still fail validation.
Twelve fixture checks pass; genuine v2 selections await the owner rerun. The v1
diagnostic report is preserved in ignored `.runtime/llm-session-v1-diagnostics.json`.
Repeat the owner command above; the new report must show `evidence-selection-v2`.
No restart or installation is needed.

## V2 semantic result and v3 correction

The genuine v2 run met arrival, bell, urgent and warm bell expectations (4/5).
It still selected person-presence evidence for a name question. That is schema-valid
but does not answer identity; no name was invented, and acceptance remains failed.
Cold wall time was 1921.97 ms; accepted warm bell 170.67/177.91 ms and urgent
299.07 ms. Concurrent blank vision: 14 samples, median 18.64 ms, P95 38.62 ms,
no errors. Spike peak RSS 174.5 MB; sampled Ollama/children max RSS 442.1 MB.

V3 provides an explicit unavailable token instead of asking for an empty wire list.
It cannot mix with facts, and the input cannot use it as a fact ID. Fourteen fixture
checks pass, including these boundaries. Actual v3 semantics await the owner run;
the runner still requires the identity question to return unavailable with no
evidence. The expected result has not been weakened or relabelled as a pass.
The v2 report is preserved locally in ignored `.runtime/llm-session-v2.json`.
Repeat the command above; the report must show `evidence-selection-v3`.

## V3 limitation and application question boundary

The genuine v3 run again met 4/5 model-only expectations. Name-question abstention
still failed: the model selected presence evidence. Supported cold request took
1951.31 ms; warm bell 172.08/168.62 ms; urgent 285.70 ms. Concurrent blank vision:
14 samples, median 18.83 ms, P95 38.41 ms, no errors. Spike peak RSS 174.2 MB;
sampled daemon/children max RSS 419.1 MB. The failed v3 model report is preserved
in ignored `.runtime/llm-session-v3.json`; it is not retroactively marked passed.

The application now supports exactly four question presets (case/outer whitespace
normalized): Explain this event; What was observed; Why does this event require
review; Which evidence supports the existing urgent event. The actual strings and
punctuation are in QUESTION_PRESETS. All other questions return unavailable before
any daemon metadata/generation request, with source `application_unavailable`,
empty evidence and no model claim. This includes names, intent, emotion and door
permission. This is an application capability boundary, not proof the model learned
to abstain. Free-text/event-history QA is deferred until retrieval and semantic
grounding are validated; future UI must expose only these supported presets.

Fifteen fixture checks passed, including unsupported questions making zero HTTP
requests and preserving severity/uncertainties. The supported Qwen generation
prompt/schema are unchanged from the genuine v3 run. Another owner rerun is not
needed to prove this deterministic application guard. An optional owner rerun
would now explicitly report four generation checks and one application guard.
Offline, live failure and complete-application responsiveness remain separate.
