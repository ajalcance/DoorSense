"""Local console, deterministic events and explicitly requested evidence storage."""
import asyncio
import base64
from datetime import datetime, timezone
import json
import sqlite3
from collections import deque
import resource
import sys
import math
import statistics
from contextlib import asynccontextmanager
from pathlib import Path
import secrets
import time

import cv2
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .camera import Webcam, frame_is_fresh
from .local_llm import LocalLLM, EventContext, Fact, QUESTION_PRESETS, MODEL, DIGEST

from .events import EventEngine
from .store import EventStore, FEEDBACK
from .recognition import FamilyMatcher, encode_sample, THRESHOLD, METHOD
from .observations import observation_facts, observation_key

ROOT = Path(__file__).resolve().parents[2]


def detector_factory():
    from .scene import SceneDetector
    return SceneDetector(enabled={'face'})


class Console:
    def __init__(self, camera=None, factory=detector_factory, llm=None, store=None, *, legacy_activity=False):
        # Legacy mode is only for injected historical regression; production is face-only.
        self.legacy_activity = legacy_activity
        self.camera = camera or Webcam()
        self.factory = factory
        self.llm = llm
        self.store = store or EventStore()
        self.engine = EventEngine(self.store)
        self.recording = None
        self.recording_timer = None
        self.media_error = None
        self.token = secrets.token_urlsafe(32)
        self.detector = None
        self.detector_error = None
        self.detector_cleanup_failed = False
        self.result = None
        self.revision = 0
        self.running = True
        self.control_busy = False
        self.last_response = None
        self.inference_samples = deque(maxlen=512)
        self.assessed_frames = 0
        self.response_log = deque(maxlen=20)
        self.feature_samples = {name: deque(maxlen=512) for name in ('face', 'pose')}
        self.feature_frames = {name: 0 for name in ('face', 'pose')}
        self.confirmation = None
        self.matcher = FamilyMatcher()
        self.child_safety_mode = False

    async def start(self):
        if self.control_busy:
            raise HTTPException(409, "Camera operation already in progress")
        if self.camera.snapshot()[0] not in ('paused', 'unavailable') or not self.camera.release_completed:
            raise HTTPException(409, 'Stop and release the camera before starting again')
        self.control_busy = True
        try:
            self.revision += 1
            self.result = self.last_response = None
            self.confirmation = None
            self.detector_error = "Detector cleanup failed. Restart the console before retrying assessment." if self.detector_cleanup_failed else None
            # Async endpoint runs on uvicorn's main event-loop thread, not a sync worker.
            self.camera.start()
            # The current demonstration uses face enrollment only, not activity alerts.
            self.engine.arm(False)
            self.inference_samples.clear()
            self.assessed_frames = 0
            for name in self.feature_samples:
                self.feature_samples[name].clear()
                self.feature_frames[name] = 0
        finally:
            self.control_busy = False

    async def stop(self):
        if self.control_busy:
            raise HTTPException(409, "Camera operation already in progress")
        self.control_busy = True
        try:
            self.revision += 1
            self.result = self.last_response = None
            self.confirmation = None
            self.finish_recording()
            self.engine.arm(False)
            await asyncio.to_thread(self.camera.stop)
            self.child_safety_mode = False
        finally:
            self.control_busy = False

    async def worker(self):
        last_sequence = -1
        detector_revision = None
        while self.running:
            state, _, frame = self.camera.snapshot()
            revision = self.revision
            if frame_is_fresh(frame, state, time.monotonic()) and frame.sequence != last_sequence and not self.detector_error:
                try:
                    if self.detector is None:
                        self.detector = await asyncio.to_thread(self.factory)
                    if detector_revision != revision and hasattr(self.detector, 'reset'):
                        await asyncio.to_thread(self.detector.reset)
                    detector_revision = revision
                    observation = await asyncio.to_thread(self.detector.detect, frame)
                    if revision != self.revision:
                        continue
                    reference = self.store.family_reference(include_frame=True)
                    observation['recognition'] = await asyncio.to_thread(self.matcher.assess, frame.pixels, observation, reference, self.matcher.generation)
                    observation['facts'] = [dict(id=identity, text=text, source=frame.source, observed_at=frame.captured_at)
                                            for identity, text in observation_facts(observation)]
                    success, jpeg = await asyncio.to_thread(cv2.imencode, ".jpg", frame.pixels, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if not success:
                        raise ValueError("Frame encoding failed")
                    if revision == self.revision and frame_is_fresh(frame, self.camera.snapshot()[0], time.monotonic()):
                        if len(observation['people']) != 1:
                            self.confirmation = None
                        if self.result and observation_key(self.result[1]) != observation_key(observation):
                            self.revision += 1
                            self.last_response = None
                        detector_revision = self.revision
                        self.result = (frame, observation, base64.b64encode(jpeg).decode("ascii"))
                        self.assessed_frames += 1
                        self.inference_samples.append(observation['inference_ms'])
                        for name, feature in observation.get('features', {}).items():
                            if name in self.feature_samples and feature.get('inference_ms') is not None:
                                self.feature_samples[name].append(feature['inference_ms'])
                                self.feature_frames[name] += 1
                        if self.legacy_activity:
                            self.engine.observe(len(observation['people']), frame.captured_monotonic, frame.captured_at)
                        self.capture_recording()
                    last_sequence = frame.sequence
                except Exception:
                    if revision == self.revision:
                        self.result = self.last_response = None
                        self.detector_error = "Person assessment unavailable. Stop and retry monitoring."
                    await self.close_detector()
            if self.recording and (not self.fresh_result() or time.monotonic()-self.recording['started'] >= 10):
                self.finish_recording()
            await asyncio.sleep(0.2)

    async def close_detector(self):
        detector, self.detector = self.detector, None
        if detector:
            try:
                await asyncio.to_thread(detector.close)
            except Exception:
                self.detector_cleanup_failed = True
                self.detector_error = "Detector cleanup failed. Restart the console before retrying assessment."

    def fresh_result(self):
        state = self.camera.snapshot()[0]
        return self.result if self.result and frame_is_fresh(self.result[0], state, time.monotonic()) else None

    def media_frame(self):
        result = self.fresh_result()
        if not result:
            raise HTTPException(409, 'Fresh camera evidence is unavailable')
        return dict(image=result[2], captured_at=result[0].captured_at,
                    sequence=result[0].sequence, width=result[0].pixels.shape[1], height=result[0].pixels.shape[0])

    def capture_recording(self):
        if not self.recording:
            return
        if time.monotonic()-self.recording['started'] >= 10:
            self.finish_recording()
            return
        frame = self.media_frame()
        frames = self.recording['frames']
        if not frames or frames[-1]['sequence'] != frame['sequence']:
            frames.append(frame)
        if len(frames) >= 50 or sum(len(f['image']) for f in frames) >= 26*1024*1024:
            self.finish_recording()

    def finish_recording(self):
        if self.recording_timer:
            self.recording_timer.cancel()
            self.recording_timer = None
        recording, self.recording = self.recording, None
        if recording and recording['frames']:
            try:
                return self.store.save_media(recording['event_id'], 'clip', recording['frames'])
            except Exception:
                # Storage failure must not stop monitoring or camera release.
                self.media_error = 'Recording could not be saved locally. Check storage and retry.'
        return None

    def status(self):
        state, message, _ = self.camera.snapshot()
        result = self.fresh_result()
        confirmation = self.current_confirmation() if self.legacy_activity else None
        if state == "monitoring" and result is None and not self.detector_error:
            message = "Waiting for fresh person assessment."
        event = self.engine.current() if self.legacy_activity else None
        recognition = result[1].get('recognition') if result else None
        try:
            history_total = self.store.history(limit=1)['total']
            family_reference = self.store.family_reference()
        except (sqlite3.Error, OSError):
            history_total = None
            family_reference = None
            self.engine.storage_error = 'Local history unavailable. Active alerts remain in this session.'
        return {"mode": "live", "demo_mode": "legacy_activity" if self.legacy_activity else "face_enrollment", "event": event, "event_revision": self.engine.revision,
                "recognition": result[1].get("recognition") if result else None,
                "confirmation": {key:value for key,value in confirmation.items() if not key.startswith('_')} if confirmation else None,
                "features": result[1].get('features', {}) if result else {
                    name: dict(value, state='waiting' if value['state'] == 'waiting' and state == 'monitoring' else value['state'], descriptions=[])
                    for name, value in getattr(self.detector, 'features', {}).items()},
                "armed": self.engine.armed if self.legacy_activity else self.child_safety_mode,
                "rules": self.engine.config if self.legacy_activity else None,
                "simulation": self.engine.simulation() if self.legacy_activity else None,
                "history_total": history_total, "family_reference": family_reference,
                "learning": dict(method=METHOD, threshold=THRESHOLD, example_count=int(bool(family_reference and family_reference['automatic_matching']))),
                "storage_error": self.engine.storage_error,
                "recording": {"event_id": self.recording['event_id'], "frames": len(self.recording['frames']),
                              "seconds": round(time.monotonic()-self.recording['started'], 1)} if self.recording else None,
                "media_error": self.media_error, "camera": state, "message": message,
                "assessment": "unavailable" if self.detector_error else "available" if result else "waiting",
                "assessment_message": self.detector_error, "release_completed": self.camera.release_completed,
                "revision": self.revision, "severity": (event["severity"] if event else "monitoring" if self.engine.armed else None) if self.legacy_activity else "monitoring" if recognition and recognition['state'] == 'matched' else None,
                "rule_reason": (event["rule_reason"] if event else "Child safety mode is on. No configured alert condition detected." if self.engine.armed else "Child safety mode is off. Camera viewing remains available.") if self.legacy_activity else recognition['message'] if recognition else "Waiting for fresh local face analysis.",
                "frame": {"image": result[2], "width": result[0].pixels.shape[1], "height": result[0].pixels.shape[0],
                          "age_seconds": time.monotonic() - result[0].captured_monotonic, **result[1]} if result else None,
                "questions": list(QUESTION_PRESETS.values()), "token": self.token,
                "diagnostics": {"configured_qwen": MODEL, "configured_digest": DIGEST,
                                "vision_hash": self.detector.model_sha256 if self.detector else None,
                                "assessed_frames": self.assessed_frames,
                                "scene_features": result[1].get('features', {}) if result else {},
                                "last_response": self.last_response}}

    def evidence(self):
        status = self.status()
        samples = sorted(self.inference_samples)
        response = self.last_response
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return dict(generated_at=datetime.now(timezone.utc).isoformat(),
                    scope='Actual current service session; no images, private token or test data.',
                    camera=dict(state=status['camera'], release_completed=status['release_completed'],
                                assessed_frames=self.assessed_frames,
                                latest_captured_at=self.result[0].captured_at if self.result else None,
                                vision_sha256=status['diagnostics']['vision_hash']),
                    vision=dict(sample_count=len(samples), median_ms=statistics.median(samples) if samples else None,
                                p95_ms=samples[math.ceil(len(samples)*.95)-1] if samples else None,
                                p95_method='nearest rank; last 512 accepted observations'),
                    scene_features={name: dict(assessed_frames=self.feature_frames[name],
                        model_sha256=getattr(self.detector, 'features', {}).get(name, {}).get('model_sha256'),
                        sample_count=len(values), median_ms=statistics.median(values) if values else None,
                        p95_ms=sorted(values)[math.ceil(len(values)*.95)-1] if values else None)
                        for name, values in self.feature_samples.items()},
                    app_process_peak_rss_bytes=peak if sys.platform == 'darwin' else peak*1024,
                    memory_scope='Application process high-water mark only; excludes Ollama and system unified-memory accounting.',
                    event=status['event'], history_total=status['history_total'], last_response=response,
                    response_log=list(self.response_log),
                    genuine_qwen_selection_observed=any(row['response'].get('source') == 'qwen_evidence_selection' and
                        row['response'].get('model') == MODEL and row['response'].get('model_digest') == DIGEST for row in self.response_log),
                    offline_acceptance='Not established by this report; requires disconnected restart and external-request inspection.')

    def sensor_facts(self):
        if not self.legacy_activity:
            return ()
        simulation = self.engine.simulation()
        facts = []
        if self.engine.contact:
            contact = self.engine.contact
            facts.append(Fact('door', f"The simulated door contact currently indicates {'closed' if contact['kind'] == 'contact_closed' else 'open'}.", 'simulated_sensor', contact['observed_at']))
        for kind in ('bell', 'impact'):
            progress = simulation['progress'][kind]
            if progress['count']:
                last = next(entry for entry in reversed(self.engine.inputs) if entry['kind'] == kind)
                facts.append(Fact('pending_'+kind, f"{progress['count']} accepted simulated {kind} inputs are within the current {self.engine.config[kind+'_window']}-second rule window.", 'simulated_sensor', last['observed_at']))
        return tuple(facts)

    def context(self, event_id=None):
        event = self.store.event(event_id) if event_id else self.engine.current() if self.legacy_activity else None
        if event_id and not event:
            raise HTTPException(404, 'Event not found')
        if event:
            age = max(0, datetime.now(timezone.utc).timestamp()-datetime.fromisoformat(event['created_at']).timestamp())
            if age > 60:
                raise HTTPException(409, 'Recorded event exceeds the 60-second explanation window; read its saved facts.')
            return EventContext(event['id'], event['revision'], event['severity'], event['rule_reason'],
                                tuple(Fact(**fact) for fact in event['facts']), tuple(event['uncertainties']),
                                received_monotonic=time.monotonic()-age)

        result = self.fresh_result()
        if not result:
            raise HTTPException(409, "Fresh person assessment is unavailable")
        frame, observation, _ = result
        confirmation = self.current_confirmation() if self.legacy_activity else None
        if confirmation:
            return EventContext(confirmation['id'], 1, 'monitoring',
                'Parent-confirmed visitor category in a captured snapshot; no automatic identity recognition.',
                tuple(Fact(**fact) for fact in [*confirmation['facts'][:-1][:4], confirmation['facts'][-1]]) + self.sensor_facts(),
                ('Owner annotation applies only to the referenced snapshot, not later frames.',
                 'A familiar or expected visitor does not establish safety or permission to open.'),
                received_monotonic=confirmation['_monotonic'])
        return EventContext("camera-session", self.revision, "monitoring",
                            "Current sampled camera observations; no configured event is selected.",
                            tuple(Fact(identity, text, 'laptop_webcam', frame.captured_at) for identity, text in observation_facts(observation)[:5]) + self.sensor_facts(),
                            ("LBPH appearance matching uses one parent-labeled example; false matches and missed matches are possible. It does not establish intent or safety.",
                             "Facial movements and posture do not establish emotion or a security incident.",
                             "Undetected objects or landmarks may be outside the frame or missed."))

    def current_confirmation(self):
        result = self.fresh_result()
        if self.confirmation and (time.monotonic()-self.confirmation['_monotonic'] >= 60 or not result or len(result[1]['people']) != 1):
            self.confirmation = None
        return self.confirmation

    def confirm_visitor(self, label):
        if label is None:
            self.confirmation = None
            self.revision += 1
            self.last_response = None
            return
        if label not in ('Family member', 'Unknown'):
            raise HTTPException(422, 'Select an owner confirmation label')
        result = self.fresh_result()
        if not result or len(result[1]['people']) != 1:
            raise HTTPException(409, 'One freshly assessed person is required for an owner snapshot annotation')
        frame, observation, _ = result
        facts = [dict(id=identity, text=text, source='laptop_webcam', observed_at=frame.captured_at)
                 for identity,text in observation_facts(observation)[:7]]
        facts.append(dict(id='owner', text=f'An owner marked the visitor in frame {frame.sequence} as {label}; this is not camera recognition.',
                          source='owner_label', observed_at=datetime.now(timezone.utc).isoformat()))
        self.confirmation = dict(id='owner-confirmation-'+secrets.token_hex(12), label=label,
            captured_at=frame.captured_at, sequence=frame.sequence, facts=facts, source='owner_label',
            expires_in_seconds=60, _monotonic=time.monotonic())
        self.revision += 1
        self.last_response = None


def create_app(console=None):
    bridge = console or Console()

    @asynccontextmanager
    async def lifespan(app):
        if console is None:
            bridge.store.close()
            bridge.store = EventStore(ROOT / 'data/events.sqlite3')
            bridge.engine = EventEngine(bridge.store)
        bridge.llm = bridge.llm or LocalLLM()
        worker = asyncio.create_task(bridge.worker())
        try:
            yield
        finally:
            bridge.finish_recording()
            bridge.running = False
            bridge.revision += 1
            bridge.result = bridge.last_response = None
            try:
                await asyncio.to_thread(bridge.camera.stop)
            finally:
                try:
                    await worker
                finally:
                    await bridge.close_detector()
                    try:
                        await bridge.llm.close()
                    finally:
                        bridge.store.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    @app.exception_handler(sqlite3.Error)
    async def storage_failure(request, error):
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail': 'Local storage operation failed. Check disk/storage in the owner Terminal.'}, status_code=503)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin and origin != f"http://{request.headers.get('host')}":
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Cross-origin requests are unavailable"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'"
        return response

    def authorize(request):
        if not secrets.compare_digest(request.headers.get("x-doorsense-token", ""), bridge.token):
            raise HTTPException(403, "Console control token required")

    @app.get("/api/status")
    async def status():
        return bridge.status()

    @app.get('/api/evidence')
    async def evidence(request: Request):
        authorize(request)
        return bridge.evidence()

    @app.post("/api/camera/{action}")
    async def control(action: str, request: Request):
        authorize(request)
        if action == "start":
            await bridge.start()
        elif action == "stop":
            await bridge.stop()
        else:
            raise HTTPException(404, "Unknown camera action")
        return bridge.status()

    @app.post("/api/explain")
    async def explain(request: Request):
        authorize(request)
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > 1024:
                raise HTTPException(413, "Question request too large")
            body.extend(chunk)
        try:
            payload = json.loads(body)
            question = payload['question']
            if question not in QUESTION_PRESETS.values():
                raise ValueError()
            event_id = payload.get('event_id')
            if event_id is not None and (not isinstance(event_id, str) or len(event_id) != 32):
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            raise HTTPException(422, "Select a supported question preset and event")
        try:
            context = bridge.context(event_id)
        except HTTPException as error:
            if error.status_code != 409:
                raise
            return {'source': 'application_unavailable', 'text': error.detail, 'evidence': []}
        if ((question == list(QUESTION_PRESETS.values())[2] and context.severity != 'review') or
            (question == list(QUESTION_PRESETS.values())[3] and context.severity != 'urgent')):
            return {'source': 'application_unavailable', 'text': 'The selected context has no event of the required severity.', 'evidence': []}
        frame_result = bridge.fresh_result()
        signature = observation_key(frame_result[1]) if frame_result else None
        engine_revision = bridge.engine.revision
        sensor_signature = bridge.sensor_facts()
        def current(identity, revision):
            if identity.startswith('owner-confirmation-'):
                confirmation = bridge.current_confirmation()
                return bool(confirmation and confirmation['id'] == identity and not bridge.engine.current() and bridge.sensor_facts() == sensor_signature)
            if identity != 'camera-session':
                bridge.engine.current()  # Expiry invalidates an in-flight live-event response.
                saved = bridge.engine.record(identity)
                return bool(saved and saved['revision'] == revision and
                            (event_id or bridge.engine.revision == engine_revision))
            result = bridge.fresh_result()
            return bridge.revision == revision and result is not None and observation_key(result[1]) == signature and bridge.engine.revision == engine_revision and bridge.sensor_facts() == sensor_signature
        result = await bridge.llm.explain(context, question, is_current=current)
        result['observation_captured_at'] = context.facts[0].observed_at
        result['observation_source'] = 'owner_confirmed_snapshot' if context.event_id.startswith('owner-confirmation-') else 'saved_event' if context.event_id != 'camera-session' else 'laptop_webcam'
        bridge.last_response = result
        bridge.response_log.append(dict(returned_at=datetime.now(timezone.utc).isoformat(), question=question, response=result))
        return result

    async def small_json(request):
        authorize(request)
        body = bytearray()
        async for chunk in request.stream():
            if len(body)+len(chunk) > 1024:
                raise HTTPException(413, 'Request too large')
            body.extend(chunk)
        try:
            value = json.loads(body)
            if not isinstance(value, dict):
                raise ValueError()
            return value
        except (ValueError, TypeError):
            raise HTTPException(422, 'JSON object required')

    @app.post('/api/visitor-confirmation')
    async def visitor_confirmation(request: Request):
        payload = await small_json(request)
        if not bridge.legacy_activity:
            raise HTTPException(410, 'Manual visitor selection is removed. Enroll a face for local recognition.')
        if 'label' not in payload:
            raise HTTPException(422, 'Owner label required; null clears the annotation')
        bridge.confirm_visitor(payload['label'])
        return bridge.status()

    @app.post('/api/family-reference/save')
    async def save_family_reference(request: Request):
        await small_json(request)
        if bridge.store.family_reference():
            raise HTTPException(409, 'A family reference is already saved. Delete it explicitly before saving another.')
        result = bridge.fresh_result()
        if not result or len(result[1]['people']) != 1 or result[1].get('features', {}).get('face', {}).get('state') != 'available':
            raise HTTPException(409, 'Show exactly one person with available face analysis in a fresh assessed frame.')
        frame = bridge.media_frame()
        try:
            frame['face_sample'] = encode_sample(result[0].pixels, result[1])
            bridge.store.save_family_reference(frame)
        except ValueError as error:
            raise HTTPException(422, str(error))
        bridge.revision += 1
        bridge.result = bridge.last_response = None
        bridge.confirmation = None
        return bridge.status()

    @app.get('/api/family-reference')
    async def family_reference(request: Request):
        authorize(request)
        reference = bridge.store.family_reference(include_frame=True)
        if not reference:
            raise HTTPException(404, 'No family reference is saved')
        return reference

    @app.post('/api/family-reference/delete')
    async def delete_family_reference(request: Request):
        await small_json(request)
        bridge.revision += 1
        bridge.store.delete_family_reference()
        bridge.matcher.clear()
        bridge.result = bridge.last_response = None
        if bridge.confirmation and bridge.confirmation['label'] == 'Family member':
            bridge.confirm_visitor(None)
        bridge.revision += 1
        return bridge.status()

    @app.post('/api/armed')
    async def arm(request: Request):
        payload = await small_json(request)
        if not bridge.legacy_activity:
            if bridge.control_busy:
                raise HTTPException(409, 'Wait for the camera operation to finish before changing Child safety mode.')
            if type(payload.get('armed')) is not bool:
                raise HTTPException(422, 'Child safety mode requires a boolean.')
            bridge.child_safety_mode = payload['armed']
            return bridge.status()
        if bridge.control_busy:
            raise HTTPException(409, 'Wait for camera release before changing armed state')
        try:
            bridge.engine.arm(payload.get('armed'))
        except ValueError as error:
            raise HTTPException(422, str(error))
        return bridge.status()

    @app.post('/api/session/reset')
    async def reset_session(request: Request):
        await small_json(request)
        await bridge.stop()
        bridge.engine.inputs.clear()
        bridge.engine.last.clear()
        bridge.engine.contact = None
        bridge.engine.replies.clear()
        bridge.engine.input_revision += 1
        bridge.engine.active.clear()
        bridge.engine.occupancy_start = bridge.engine.occupancy_last = None
        bridge.engine.occupancy_fired = False
        bridge.engine.person_evidence = None
        bridge.engine.revision += 1
        return bridge.status()

    @app.post('/api/sensors')
    async def sensor(request: Request):
        payload = await small_json(request)
        if not bridge.legacy_activity:
            raise HTTPException(410, 'Sensor simulations are removed. This demo uses face recognition only.')
        try:
            if bridge.fresh_result() is None:
                bridge.engine.person_evidence = None
            result = bridge.engine.sensor(payload.get('kind'))
            return {**result, 'status': bridge.status()}
        except (ValueError, TypeError) as error:
            raise HTTPException(422, str(error))

    @app.get('/api/events')
    async def history(request: Request, offset: int = 0):
        authorize(request)
        if not 0 <= offset <= 1000000:
            raise HTTPException(422, 'Invalid history offset')
        return bridge.store.history(offset)

    @app.post('/api/events/{event_id}/acknowledge')
    async def acknowledge(event_id: str, request: Request):
        authorize(request)
        try:
            return bridge.store.update(event_id, acknowledge=True)
        except KeyError:
            raise HTTPException(404, 'Event not found')

    @app.post('/api/events/{event_id}/feedback')
    async def feedback(event_id: str, request: Request):
        payload = await small_json(request)
        try:
            if payload.get('feedback') not in FEEDBACK:
                raise ValueError('Select a supported feedback label')
            return bridge.store.update(event_id, feedback=payload['feedback'])
        except KeyError:
            raise HTTPException(404, 'Event not found')
        except ValueError as error:
            raise HTTPException(422, str(error))

    @app.post('/api/events/{event_id}/media/{action}')
    async def capture(event_id: str, action: str, request: Request):
        authorize(request)
        if not bridge.store.event(event_id):
            raise HTTPException(404, 'Event not found')
        if action == 'stop':
            if not bridge.recording or bridge.recording['event_id'] != event_id:
                raise HTTPException(409, 'No recording for this event')
            saved = bridge.finish_recording()
            if not saved:
                raise HTTPException(503, bridge.media_error or 'Recording has no frames')
            return saved
        if action not in ('snapshot', 'record'):
            raise HTTPException(404, 'Unknown media action')
        active = bridge.engine.current()
        if not active or active['id'] != event_id:
            raise HTTPException(409, 'New media can be saved only for the current active event')
        if bridge.recording:
            raise HTTPException(409, 'A recording is already in progress')
        frame = bridge.media_frame()
        if datetime.fromisoformat(frame['captured_at']) < datetime.fromisoformat(active['created_at']):
            raise HTTPException(409, 'Wait for a fresh camera frame captured after the event')
        bridge.media_error = None
        if action == 'snapshot':
            return bridge.store.save_media(event_id, 'snapshot', [frame])
        bridge.recording = dict(event_id=event_id, started=time.monotonic(), frames=[frame])
        bridge.recording_timer = asyncio.get_running_loop().call_later(10, bridge.finish_recording)
        return {'recording': True, 'maximum_seconds': 10}

    @app.get('/api/media/{media_id}')
    async def read_media(media_id: str, request: Request):
        authorize(request)
        media = bridge.store.media(media_id)
        if not media:
            raise HTTPException(404, 'Media not found')
        return media

    @app.post('/api/media/{media_id}/delete')
    async def delete_media(media_id: str, request: Request):
        authorize(request)
        if not bridge.store.delete_media(media_id):
            raise HTTPException(404, 'Media not found')
        return {'deleted': True}

    build = ROOT / "frontend/dist"
    if (build / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=build / "assets"), name="assets")

    @app.get("/")
    async def index():
        if not (build / "index.html").is_file():
            raise HTTPException(503, "Build frontend first using the documented Node 22 command")
        return FileResponse(build / "index.html")

    return app
