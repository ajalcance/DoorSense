"""In-process service checks: fake camera/LLM; no ports, device or model opened."""
import asyncio
import base64
import cv2
from datetime import datetime, timezone
from pathlib import Path
import sys
import threading
import time
import unittest
import httpx
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from doorsense.camera import Frame
from doorsense.console import Console, create_app


class Camera:
    release_completed = True
    def __init__(self):
        self.state = "paused"
        self.started_thread = None
    def snapshot(self):
        return self.state, "Fixture camera", None
    def start(self):
        self.started_thread = threading.current_thread()
        self.state = "monitoring"
    def stop(self):
        self.state = "paused"
        return True


class LLM:
    def __init__(self):
        self.calls = 0
        self.hook = None
        self.closed = False
    async def close(self):
        self.closed = True
    async def explain(self, context, question, is_current):
        self.calls += 1
        if self.hook:
            await self.hook()
        return {"source": "template_fallback" if is_current(context.event_id, context.revision) else "discarded",
                "text": "Injected fixture", "evidence": []}


class FaceOnlyTests(unittest.IsolatedAsyncioTestCase):
    async def test_parent_toggle_controls_guidance_without_enabling_activity_engine(self):
        bridge=Console(camera=Camera(), llm=LLM())
        headers={'x-doorsense-token':bridge.token}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(bridge)),base_url='http://127.0.0.1:8765') as client:
            self.assertEqual((await client.post('/api/armed',json={'armed':True})).status_code,403)
            self.assertEqual((await client.post('/api/armed',headers=headers,json={'armed':'true'})).status_code,422)
            enabled=await client.post('/api/armed',headers=headers,json={'armed':True})
            self.assertTrue(enabled.json()['armed'])
            self.assertFalse(bridge.engine.armed)
            self.assertIsNone(enabled.json()['simulation'])
            disabled=await client.post('/api/armed',headers=headers,json={'armed':False})
            self.assertFalse(disabled.json()['armed'])
            await client.post('/api/armed',headers=headers,json={'armed':True})
            await bridge.stop()
            self.assertFalse(bridge.status()['armed'])
        bridge.store.close()

    async def test_production_demo_rejects_sensors_arming_and_ignores_old_activity(self):
        bridge = Console(camera=Camera(), llm=LLM())
        bridge.engine.arm(True)
        bridge.engine.sensor('contact_closed')
        bridge.engine.sensor('bell')
        bridge.engine.emit('old', 'urgent', 'Legacy simulation', [])
        headers = {'x-doorsense-token': bridge.token}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(bridge)), base_url='http://127.0.0.1:8765') as client:
            for path, body in [('/api/sensors', {'kind':'impact'}), ('/api/visitor-confirmation', {'label':'Family member'})]:
                self.assertEqual((await client.post(path, headers=headers, json=body)).status_code, 410)
            status = (await client.get('/api/status')).json()
            self.assertEqual(status['demo_mode'], 'face_enrollment')
            self.assertIsNone(status['simulation'])
            self.assertIsNone(status['rules'])
            self.assertIsNone(status['event'])
            self.assertFalse(status['armed'])
            self.assertEqual(status['learning']['example_count'], 0)
            self.assertEqual(bridge.sensor_facts(), ())
        bridge.store.close()

    async def test_face_enrollment_live_match_delete_clears_model_and_preserves_history(self):
        camera = Camera()
        camera.state = 'monitoring'
        bridge = Console(camera=camera, llm=LLM())
        pixels = np.random.default_rng(42).integers(0,255,(128,128,3),dtype=np.uint8)
        frame = Frame(1, datetime.now(timezone.utc).isoformat(), time.monotonic(), pixels)
        observation = dict(sequence=1,captured_at=frame.captured_at,people=[{'box':[0,0,128,128]}],inference_ms=1,
                           features={'face':{'state':'available','box':[0,0,1,1]}})
        image = base64.b64encode(cv2.imencode('.jpg',pixels)[1]).decode('ascii')
        bridge.result = (frame,observation,image)
        headers = {'x-doorsense-token':bridge.token}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(bridge)),base_url='http://127.0.0.1:8765') as client:
            self.assertEqual((await client.post('/api/family-reference/save',headers=headers,json={})).status_code,200)
            self.assertIsNone(bridge.status()['recognition'])
            observation['recognition'] = bridge.matcher.assess(pixels,observation,bridge.store.family_reference(include_frame=True))
            bridge.result = (frame,observation,image)
            self.assertEqual(bridge.status()['recognition']['category'],'Family member')
            self.assertIn('visitor', [fact.id for fact in bridge.context().facts])
            bridge.store.save_event(dict(id='old',revision=1,severity='review',facts=[]))
            result=await client.post('/api/family-reference/delete',headers=headers,json={})
            self.assertEqual(result.status_code,200)
            self.assertIsNone(result.json()['recognition'])
            self.assertIsNone(bridge.matcher.model)
            self.assertIsNone(bridge.matcher.sample)
            self.assertEqual(bridge.store.history()['total'],1)
            self.assertEqual(bridge.matcher.assess(pixels,observation,None)['category'],'Unknown')
        bridge.store.close()


class Tests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.camera = Camera()
        self.llm = LLM()
        self.bridge = Console(camera=self.camera, llm=self.llm, legacy_activity=True)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(self.bridge)), base_url="http://127.0.0.1:8765")
        self.headers = {"x-doorsense-token": self.bridge.token}
    async def asyncTearDown(self):
        await self.client.aclose()
    def packet(self, age=0, count=1):
        frame = Frame(1, datetime.now(timezone.utc).isoformat(), time.monotonic()-age, np.zeros((4,4,3), dtype=np.uint8))
        self.camera.state = "monitoring"
        self.bridge.result = (frame, {"sequence":1,"captured_at":frame.captured_at,"people":[{"box":[0,0,1,1]}]*count,"inference_ms":1}, "fixture")
    async def test_start_requires_token_and_main_thread(self):
        self.assertEqual(self.camera.state, "paused")
        self.assertEqual((await self.client.post('/api/camera/start')).status_code,403)
        self.assertIsNone(self.camera.started_thread)
        response = await self.client.post('/api/camera/start',headers=self.headers)
        self.assertEqual(response.status_code,200)
        self.assertIs(self.camera.started_thread,threading.main_thread())
    async def test_origin_and_host_rejected(self):
        response = await self.client.post('/api/camera/start',headers={**self.headers,"origin":"https://example.com"})
        self.assertEqual(response.status_code,403)
        self.assertEqual((await self.client.get('/api/status',headers={"host":"example.com"})).status_code,400)
        self.assertIsNone(self.camera.started_thread)
    async def test_reset_stops_camera_clears_live_alert_and_preserves_history(self):
        self.packet()
        self.bridge.engine.arm(True)
        self.bridge.engine.sensor('contact_open')
        self.bridge.engine.sensor('impact')
        event = self.bridge.engine.emit('test_rule', 'urgent', 'Test-only alert', [dict(id='test', text='Test-only evidence', source='simulated_sensor', observed_at=datetime.now(timezone.utc).isoformat())])
        await self.client.post('/api/visitor-confirmation', headers=self.headers, json={'label':'Family member'})
        denied = await self.client.post('/api/session/reset', json={})
        self.assertEqual(denied.status_code, 403)
        result = await self.client.post('/api/session/reset', headers=self.headers, json={})
        self.assertEqual(result.status_code, 200)
        status = result.json()
        self.assertEqual(status['camera'], 'paused')
        self.assertFalse(status['armed'])
        self.assertIsNone(status['event'])
        self.assertIsNone(status['confirmation'])
        self.assertIsNotNone(self.bridge.engine.record(event['id']))
        self.assertEqual(len(self.bridge.engine.inputs), 0)
        self.assertIsNone(status['simulation']['contact'])
        self.assertEqual(status['simulation']['replies'], [])
        self.assertEqual(status['simulation']['progress']['impact']['count'], 0)
    async def test_sensor_reply_and_refresh_share_authoritative_state(self):
        self.bridge.engine.sensor('contact_closed')
        await self.client.post('/api/armed', headers=self.headers, json={'armed': True})
        result = (await self.client.post('/api/sensors', headers=self.headers, json={'kind': 'impact'})).json()
        self.assertTrue(result['accepted'])
        self.assertEqual(result['status']['simulation']['progress']['impact']['count'], 1)
        self.assertIsNone(result['status']['event'])
        refreshed = (await self.client.get('/api/status')).json()
        self.assertEqual(refreshed['simulation']['replies'], result['status']['simulation']['replies'])
        self.assertEqual(refreshed['simulation']['progress']['impact']['count'], 1)
        ignored = (await self.client.post('/api/sensors', headers=self.headers, json={'kind': 'impact'})).json()
        self.assertFalse(ignored['accepted'])
        self.assertFalse(ignored['status']['simulation']['replies'][-1]['accepted'])
    async def test_stale_frame_and_stop_clear_evidence(self):
        self.packet(age=1)
        self.assertIsNone((await self.client.get('/api/status')).json()['frame'])
        self.packet()
        self.assertIsNotNone(self.bridge.status()['frame'])
        await self.client.post('/api/camera/stop',headers=self.headers)
        self.assertIsNone(self.bridge.result)
        self.assertEqual(self.camera.state,'paused')
    async def test_questions_without_review_make_no_llm_call(self):
        self.packet()
        response=await self.client.post('/api/explain',headers=self.headers,json={"question":"Why does this event require review?"})
        self.assertEqual(response.json()['source'],'application_unavailable')
        response=await self.client.post('/api/explain',headers=self.headers,json={"question":"Who is this?"})
        self.assertEqual(response.status_code,422)
        self.assertEqual(self.llm.calls,0)
    async def test_stop_supersedes_pending_answer(self):
        self.packet()
        self.llm.hook=self.bridge.stop
        response=await self.client.post('/api/explain',headers=self.headers,json={"question":"What was observed?"})
        self.assertEqual(response.json()['source'],'discarded')
    async def test_count_change_supersedes_pending_answer(self):
        self.packet()
        async def change():
            self.packet(count=0)
        self.llm.hook=change
        response=await self.client.post('/api/explain',headers=self.headers,json={"question":"What was observed?"})
        self.assertEqual(response.json()['source'],'discarded')
    async def test_scene_change_supersedes_answer_without_person_count_change(self):
        self.packet()
        self.bridge.result[1]['features'] = {'face': {'state': 'available', 'descriptions': ['Visible movement.']}}
        async def change():
            self.bridge.result[1]['features']['face']['descriptions'] = []
        self.llm.hook = change
        response = await self.client.post('/api/explain', headers=self.headers, json={'question':'What was observed?'})
        self.assertEqual(response.json()['source'], 'discarded')
    async def test_scene_facts_reach_context_with_frame_provenance(self):
        self.packet()
        self.bridge.result[1]['features'] = {'face': {'state': 'available', 'descriptions': ['The face model suggests an open mouth.']}}
        context = self.bridge.context()
        self.assertEqual(len(context.facts), 2)
        self.assertEqual(context.facts[1].source, 'laptop_webcam')
        self.assertEqual(context.facts[1].observed_at, self.bridge.result[0].captured_at)
    async def test_owner_confirmation_is_snapshot_provenance_not_recognition(self):
        self.packet()
        denied = await self.client.post('/api/visitor-confirmation', json={'label':'Family member'})
        self.assertEqual(denied.status_code, 403)
        response = await self.client.post('/api/visitor-confirmation', headers=self.headers, json={'label':'Family member'})
        self.assertEqual(response.status_code, 200)
        context = self.bridge.context()
        self.assertTrue(context.event_id.startswith('owner-confirmation-'))
        self.assertEqual(context.facts[-1].source, 'owner_label')
        self.assertIn('not camera recognition', context.facts[-1].text)
        self.assertEqual(self.bridge.store.history()['total'], 0)
        answer = await self.client.post('/api/explain', headers=self.headers, json={'question':'What was observed?'})
        self.assertEqual(answer.json()['observation_source'], 'owner_confirmed_snapshot')
    async def test_snapshot_context_includes_sensor_evidence_and_discards_changed_activity(self):
        self.packet()
        self.bridge.confirm_visitor('Family member')
        self.bridge.engine.arm(True)
        self.bridge.engine.sensor('contact_closed')
        self.bridge.engine.sensor('bell')
        context = self.bridge.context()
        context.validate()
        self.assertLessEqual(len(context.facts), 8)
        self.assertEqual({fact.source for fact in context.facts}, {'laptop_webcam', 'owner_label', 'simulated_sensor'})
        self.assertIn('pending_bell', {fact.id for fact in context.facts})
        async def change():
            self.bridge.engine.sensor('impact')
        self.llm.hook = change
        response = await self.client.post('/api/explain', headers=self.headers, json={'question':'What was observed?'})
        self.assertEqual(response.json()['source'], 'discarded')
    async def test_explicit_family_reference_save_preview_reset_delete(self):
        path = '/api/family-reference/save'
        self.assertEqual((await self.client.post(path, json={})).status_code, 403)
        self.assertEqual((await self.client.get('/api/family-reference')).status_code, 403)
        self.assertEqual((await self.client.post(path, headers=self.headers, json={})).status_code, 409)
        self.packet()
        self.assertEqual((await self.client.post(path, headers=self.headers, json={})).status_code, 409)
        frame, observation, _ = self.bridge.result
        frame = Frame(frame.sequence, frame.captured_at, frame.captured_monotonic, np.zeros((128,128,3), dtype=np.uint8))
        observation['features'] = {'face': {'state':'available','box':[0,0,1,1]}}
        image = base64.b64encode(cv2.imencode('.jpg', frame.pixels)[1]).decode('ascii')
        self.bridge.result = (frame, observation, image)
        response = await self.client.post(path, headers=self.headers, json={})
        self.assertEqual(response.status_code, 200)
        reference = response.json()['family_reference']
        self.assertEqual(reference['category'], 'Family member')
        self.assertTrue(reference['automatic_matching'])
        self.assertNotIn('frame', reference)
        self.assertNotIn(image, str(self.bridge.evidence()))
        preview = await self.client.get('/api/family-reference', headers=self.headers)
        self.assertEqual(preview.json()['frame']['image'], image)
        self.assertEqual((await self.client.post(path, headers=self.headers, json={})).status_code, 409)
        reset = await self.client.post('/api/session/reset', headers=self.headers, json={})
        self.assertIsNotNone(reset.json()['family_reference'])
        self.assertEqual(self.bridge.store.history()['total'], 0)
        self.packet()
        self.bridge.confirm_visitor('Family member')
        self.assertEqual((await self.client.post('/api/family-reference/delete', json={})).status_code, 403)
        deleted = await self.client.post('/api/family-reference/delete', headers=self.headers, json={})
        self.assertIsNone(deleted.json()['family_reference'])
        self.assertIsNone(deleted.json()['confirmation'])
        self.assertEqual((await self.client.get('/api/family-reference', headers=self.headers)).status_code, 404)
    async def test_owner_confirmation_clears_on_expiry_count_loss_and_stop(self):
        for change in ('expiry', 'count', 'stop'):
            self.packet()
            self.bridge.confirm_visitor('Unknown')
            if change == 'expiry':
                self.bridge.confirmation['_monotonic'] -= 61
            elif change == 'count':
                self.packet(count=0)
            else:
                await self.bridge.stop()
            self.assertIsNone(self.bridge.status()['confirmation'])
    async def test_owner_confirmation_requires_one_fresh_person_and_supported_label(self):
        for count in (0, 2):
            self.packet(count=count)
            response = await self.client.post('/api/visitor-confirmation', headers=self.headers, json={'label':'Family member'})
            self.assertEqual(response.status_code, 409)
        self.packet()
        response = await self.client.post('/api/visitor-confirmation', headers=self.headers, json={'label':'Friendly stranger'})
        self.assertEqual(response.status_code, 422)
        for label in ('Parent', 'Expected visitor'):
            response = await self.client.post('/api/visitor-confirmation', headers=self.headers, json={'label':label})
            self.assertEqual(response.status_code, 422)
    async def test_replacing_owner_annotation_discards_pending_qwen_selection(self):
        self.packet()
        self.bridge.confirm_visitor('Family member')
        async def change():
            self.bridge.confirm_visitor('Unknown')
        self.llm.hook = change
        response = await self.client.post('/api/explain', headers=self.headers, json={'question':'What was observed?'})
        self.assertEqual(response.json()['source'], 'discarded')
    async def test_actual_response_source_is_preserved(self):
        self.packet()
        response=await self.client.post('/api/explain',headers=self.headers,json={"question":"What was observed?"})
        self.assertEqual(response.json()['source'],'template_fallback')
        self.assertIn('observation_captured_at',response.json())
    async def test_no_detector_loaded_while_paused(self):
        calls=[]
        self.bridge.factory=lambda: calls.append(True)
        task=asyncio.create_task(self.bridge.worker())
        await asyncio.sleep(0.01)
        self.bridge.running=False
        await task
        self.assertEqual(calls,[])
    async def test_worker_discards_frame_from_stopped_session(self):
        self.packet()
        frame=self.bridge.result[0]
        self.bridge.result=None
        self.camera.snapshot=lambda: (self.camera.state,'Fixture',frame)
        began=threading.Event()
        finish=threading.Event()
        class Detector:
            def detect(self,frame):
                began.set()
                finish.wait(2)
                return {"sequence":frame.sequence,"people":[]}
            def close(self):
                pass
        self.bridge.detector=Detector()
        task=asyncio.create_task(self.bridge.worker())
        try:
            self.assertTrue(await asyncio.to_thread(began.wait,2))
            await self.bridge.stop()
        finally:
            finish.set()
            self.bridge.running=False
            await task
        self.assertIsNone(self.bridge.result)
    async def test_prior_session_detector_failure_does_not_poison_restart(self):
        self.packet()
        frame=self.bridge.result[0]
        self.bridge.result=None
        self.camera.snapshot=lambda: (self.camera.state,'Fixture',frame)
        began=threading.Event()
        finish=threading.Event()
        class Detector:
            def detect(self,frame):
                began.set()
                finish.wait(2)
                raise RuntimeError('Old fixture session failed')
            def close(self):
                pass
        self.bridge.detector=Detector()
        task=asyncio.create_task(self.bridge.worker())
        try:
            self.assertTrue(await asyncio.to_thread(began.wait,2))
            await self.bridge.stop()
            await self.bridge.start()
        finally:
            finish.set()
            self.bridge.running=False
            await task
        self.assertIsNone(self.bridge.detector_error)
    async def test_detector_cleanup_failure_is_visible_and_worker_survives(self):
        self.packet()
        frame=self.bridge.result[0]
        self.bridge.result=None
        self.camera.snapshot=lambda: (self.camera.state,'Fixture',frame)
        closed=threading.Event()
        class Detector:
            def detect(self,frame):
                raise RuntimeError('Fixture failure')
            def close(self):
                closed.set()
                raise RuntimeError('Fixture close failure')
        self.bridge.detector=Detector()
        task=asyncio.create_task(self.bridge.worker())
        try:
            self.assertTrue(await asyncio.to_thread(closed.wait,2))
            await asyncio.sleep(0.01)
        finally:
            self.bridge.running=False
            await task
        self.assertTrue(self.bridge.detector_cleanup_failed)
        await self.bridge.stop()
        await self.bridge.start()
        self.assertIn('Restart the console',self.bridge.detector_error)
    async def test_shutdown_releases_even_when_control_busy(self):
        app=create_app(self.bridge)
        async with app.router.lifespan_context(app):
            self.camera.state='monitoring'
            self.bridge.control_busy=True
        self.assertEqual(self.camera.state,'paused')
        self.assertTrue(self.llm.closed)
    async def test_oversized_and_malformed_questions_make_no_llm_call(self):
        for body,code in [(b'x'*1025,413),(b'[]',422),(b'{',422),(b'{}',422)]:
            response=await self.client.post('/api/explain',headers=self.headers,content=body)
            self.assertEqual(response.status_code,code)
        self.assertEqual(self.llm.calls,0)


if __name__ == '__main__':
    unittest.main()
