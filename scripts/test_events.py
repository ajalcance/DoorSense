"""Synthetic clocks/pixels and in-process HTTP; no device, port or model calls."""
import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import sqlite3
import cv2
import httpx
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from doorsense.events import EventEngine
from doorsense.store import EventStore, FEEDBACK
from doorsense.console import Console, create_app
from doorsense.camera import Frame
from test_console import Camera, LLM


class Rules(unittest.TestCase):
    def setUp(self):
        self.store = EventStore()
        self.now = 0
        self.engine = EventEngine(self.store, clock=lambda: self.now)
    def tearDown(self):
        self.store.close()
    def pulse(self, kind, gap=.3):
        self.now += gap
        return self.engine.sensor(kind)
    def urgent(self):
        self.engine.arm(True)
        self.pulse('contact_closed')
        for _ in range(3):
            self.engine.observe(1, self.now, '2026-10-10T00:00:00Z')
            result = self.pulse('impact')
        return result['event']
    def test_disarmed_inputs_do_not_raise_or_carry_into_arming(self):
        self.pulse('contact_closed')
        for _ in range(4):
            self.pulse('bell')
            self.pulse('impact')
        self.pulse('contact_open')
        self.assertIsNone(self.engine.current())
        self.engine.arm(True)
        self.pulse('bell')
        self.assertIsNone(self.engine.current())
    def test_authoritative_progress_debounce_expiry_and_contact(self):
        self.assertIsNone(self.engine.simulation()['contact'])
        self.pulse('contact_closed')
        self.engine.arm(True)
        self.assertIsNone(self.engine.current())
        self.pulse('impact')
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 1)
        self.assertFalse(self.pulse('impact', .1)['accepted'])
        snapshot = self.engine.simulation()
        self.assertEqual(snapshot['progress']['impact']['count'], 1)
        self.assertFalse(snapshot['replies'][-1]['accepted'])
        self.assertAlmostEqual(snapshot['progress']['impact']['remaining_seconds'], 4.9)
        self.now += 5
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 0)
        self.engine.arm(False)
        self.assertEqual(self.engine.simulation()['contact']['kind'], 'contact_closed')
        self.assertEqual(self.engine.simulation()['replies'], [])
        self.engine.arm(True)
        self.assertFalse(self.pulse('contact_closed')['accepted'])
        for _ in range(3):
            self.engine.observe(1, self.now, '2026-10-10T00:00:00Z')
            self.pulse('impact')
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 3)
        self.assertEqual(self.engine.current()['severity'], 'urgent')
        self.engine.arm(False)
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 0)
        self.assertEqual(self.engine.current()['severity'], 'urgent')
    def test_progress_qualifying_deadline_rolling_windows_and_stale_occupancy(self):
        self.engine.arm(True)
        self.pulse('contact_closed')
        for _ in range(4):
            self.pulse('impact')
        self.assertAlmostEqual(self.engine.simulation()['progress']['impact']['remaining_seconds'], 4.4)
        self.now = 5.61
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 3)
        self.now = 5.91
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 2)
        self.engine.observe(1, self.now, stamp_for_test := '2026-10-10T00:00:00Z')
        self.now += .4
        self.engine.observe(1, self.now, stamp_for_test)
        self.assertAlmostEqual(self.engine.simulation()['occupancy']['elapsed_seconds'], .4)
        self.now += .81
        self.assertFalse(self.engine.simulation()['occupancy']['fresh'])
        self.assertEqual(self.engine.simulation()['occupancy']['elapsed_seconds'], 0)
    def test_open_before_arming_is_not_fresh_corroboration(self):
        self.pulse('contact_open')
        self.engine.arm(True)
        for _ in range(3):
            self.pulse('impact')
        self.assertFalse(self.pulse('contact_open')['accepted'])
        self.assertIsNone(self.engine.current())
        self.pulse('contact_closed')
        self.assertIsNone(self.engine.current())
        for _ in range(3):
            self.engine.observe(1, self.now, '2026-10-10T00:00:00Z')
            self.pulse('impact')
        self.assertEqual(self.engine.current()['severity'], 'urgent')
    def test_bells_debounce_evidence_and_no_duplicate_active_alert(self):
        self.engine.arm(True)
        self.pulse('bell')
        self.assertFalse(self.pulse('bell', .1)['accepted'])
        self.pulse('bell')
        self.assertIsNone(self.engine.current())
        event = self.pulse('bell')['event']
        self.assertEqual(event['severity'], 'review')
        self.assertEqual(event['facts'][0]['source'], 'simulated_sensor')
        for _ in range(4):
            self.pulse('bell')
        self.assertEqual(self.store.history()['total'], 1)
    def test_bells_outside_window(self):
        self.engine.arm(True)
        self.pulse('bell')
        self.pulse('bell', 11)
        self.pulse('bell', 11)
        self.assertIsNone(self.engine.current())
    def test_urgent_requires_corrob(self):
        self.engine.arm(True)
        for _ in range(3):
            self.pulse('impact')
        self.assertIsNone(self.engine.current())
        self.pulse('contact_open')
        self.assertIsNone(self.engine.current())
        self.pulse('contact_closed')
        for _ in range(2):
            self.pulse('impact')
            self.assertIsNone(self.engine.current())
        self.engine.observe(1, self.now, '2026-10-10T00:00:00Z')
        event = self.pulse('impact')['event']
        self.assertEqual(event['severity'], 'urgent')
        self.assertEqual(event['rule_id'], 'person_closed_door_impacts')
        self.assertIn('closed throughout', event['facts'][2]['text'])
        self.assertEqual(event['facts'][0]['source'], 'laptop_webcam')
    def test_combined_alert_needs_fresh_person_and_can_arrive_after_impacts(self):
        self.engine.arm(True)
        self.pulse('contact_closed')
        self.engine.observe(1, self.now, '2026-10-10T00:00:00Z')
        self.now += 1
        for _ in range(3):
            self.assertIsNone(self.pulse('impact')['event'])
        self.assertIsNone(self.engine.current())
        self.assertFalse(self.engine.simulation()['camera_evidence']['fresh'])
        self.assertIsNone(self.engine.observe(0, self.now, '2026-10-10T00:00:00Z'))
        event = self.engine.observe(1, self.now, '2026-10-10T00:00:00Z')
        self.assertEqual(event['severity'], 'urgent')
        self.assertEqual({fact['source'] for fact in event['facts']}, {'laptop_webcam', 'simulated_sensor'})
    def test_expired_impacts_cannot_fuse_with_new_detection(self):
        self.engine.arm(True)
        self.pulse('contact_closed')
        for _ in range(3):
            self.pulse('impact')
        self.now += 6
        self.assertIsNone(self.engine.observe(1, self.now, '2026-10-10T00:00:00Z'))
        self.assertIsNone(self.engine.current())
    def test_opening_breaks_closed_door_sequence_and_expiry_drops_impacts(self):
        self.engine.arm(True)
        self.pulse('contact_closed')
        for _ in range(2):
            self.pulse('impact')
        self.pulse('contact_open')
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 0)
        self.pulse('contact_closed')
        self.pulse('impact')
        self.assertIsNone(self.engine.current())
        self.pulse('impact', 6)
        self.pulse('impact')
        self.assertIsNone(self.engine.current())
    def test_duplicate_contact_does_not_refresh_window(self):
        self.engine.arm(True)
        self.pulse('contact_open')
        self.assertFalse(self.pulse('contact_open', 6)['accepted'])
        for _ in range(3):
            self.pulse('impact')
        self.assertIsNone(self.engine.current())
    def test_ack_and_disarm_preserve_severity_and_history(self):
        event = self.urgent()
        self.store.update(event['id'], acknowledge=True)
        self.engine.arm(False)
        self.assertEqual(self.engine.current()['severity'], 'urgent')
        self.assertIsNotNone(self.engine.current()['acknowledged_at'])
        self.assertEqual(self.store.history()['total'], 1)
    def test_opening_after_urgent_preserves_event_but_clears_pending_impacts(self):
        event = self.urgent()
        self.pulse('contact_open')
        self.assertEqual(self.engine.current()['id'], event['id'])
        self.assertEqual(self.engine.simulation()['progress']['impact']['count'], 0)
        self.assertEqual(self.engine.simulation()['contact']['kind'], 'contact_open')
    def test_expiry_preserves_history_changes_revision(self):
        event = self.urgent()
        revision = self.engine.revision
        self.now += 120
        self.assertIsNone(self.engine.current())
        self.assertGreater(self.engine.revision, revision)
        self.assertEqual(self.store.event(event['id'])['severity'], 'urgent')
    def test_review_cannot_mask_urgent(self):
        self.urgent()
        for _ in range(3):
            self.pulse('bell')
        self.assertEqual(self.engine.current()['severity'], 'urgent')
        self.assertEqual(self.store.history()['total'], 2)
    def test_occupancy_needs_fresh_continuity(self):
        self.engine.arm(True)
        self.engine.observe(1, 0, '2026-10-09T14:00:00Z')
        self.now = 30
        self.engine.observe(1, 30, '2026-10-09T14:00:30Z')
        self.assertIsNone(self.engine.current())
        for i in range(1, 152):
            self.now = 30 + i*.2
            self.engine.observe(1, self.now, '2026-10-09T14:01:00Z')
        self.assertEqual(self.engine.current()['rule_id'], 'sustained_occupancy')
        self.engine.observe(0, self.now, '2026-10-09T14:01:00Z')
        self.assertIsNone(self.engine.occupancy_start)
    def test_invalid_controls(self):
        with self.assertRaises(ValueError):
            self.engine.sensor('person')
        with self.assertRaises(ValueError):
            self.engine.arm('yes')
        with self.assertRaises(ValueError):
            EventEngine(self.store, bell_count=0)
    def test_storage_failure_does_not_hide_urgent(self):
        with patch.object(self.store, 'save_event', side_effect=sqlite3.OperationalError('fixture disk full')):
            event = self.urgent()
        self.assertFalse(event['persisted'])
        self.assertEqual(self.engine.current()['severity'], 'urgent')
        self.assertIn('session only', self.engine.storage_error)
        with patch.object(self.store, 'event', side_effect=sqlite3.OperationalError('fixture read failure')):
            self.assertEqual(self.engine.current()['severity'], 'urgent')
        self.assertEqual(self.store.history()['total'], 0)


def jpeg_frame():
    _, pixels = cv2.imencode('.jpg', np.zeros((10, 10, 3), np.uint8))
    return dict(image=base64.b64encode(pixels).decode(), captured_at=datetime.now(timezone.utc).isoformat(), sequence=1, width=10, height=10)


class Storage(unittest.TestCase):
    def test_restart_feedback_replay_delete_and_pagination(self):
        with tempfile.TemporaryDirectory(prefix='doorsense-test-') as folder:
            path = Path(folder)/'events.sqlite3'
            store = EventStore(path)
            engine = EventEngine(store)
            event = engine.emit('test', 'review', 'Fixture rule', [dict(id='bell', text='Synthetic bell.', source='simulated_sensor', observed_at=datetime.now(timezone.utc).isoformat())])
            self.assertIsNone(event['feedback'])
            updated = store.update(event['id'], acknowledge=True, feedback=FEEDBACK[0])
            frame = jpeg_frame()
            media = store.save_media(event['id'], 'snapshot', [frame])
            store.close()
            reopened = EventStore(path)
            self.assertEqual(reopened.event(event['id'])['acknowledged_at'], updated['acknowledged_at'])
            self.assertEqual(reopened.event(event['id'])['feedback'], FEEDBACK[0])
            self.assertEqual(reopened.media(media['id'])['frames'][0], frame)
            reopened.update(event['id'], feedback=FEEDBACK[1])
            self.assertEqual(len(reopened.event(event['id'])['media']), 1)
            self.assertIsNone(EventEngine(reopened).current())
            self.assertTrue(reopened.delete_media(media['id']))
            self.assertIsNone(reopened.media(media['id']))
            self.assertEqual(reopened.event(event['id'])['media'], [])
            self.assertFalse(reopened.delete_media(media['id']))
            for i in range(27):
                reopened.save_event({**event, 'id': str(i)})
            first = reopened.history()
            self.assertEqual(len(first['events']), 25)
            self.assertEqual(first['next_offset'], 25)
            self.assertEqual(len(reopened.history(25)['events']), 3)
            newest = reopened.history()['events'][0]['id']
            reopened.update(event['id'], acknowledge=True)
            self.assertEqual(reopened.history()['events'][0]['id'], newest)
            with self.assertRaises(ValueError):
                reopened.update(event['id'], feedback='Harmless')
            with self.assertRaises(ValueError):
                reopened.save_media(event['id'], 'snapshot', [{**frame, 'image': 'notjpeg'}])
            reopened.close()


class Integration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.camera = Camera()
        self.llm = LLM()
        self.bridge = Console(camera=self.camera, llm=self.llm, legacy_activity=True)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(self.bridge)), base_url='http://127.0.0.1:8765')
        self.headers = {'x-doorsense-token': self.bridge.token}
    async def asyncTearDown(self):
        await self.client.aclose()
        self.bridge.store.close()
    def event(self):
        self.bridge.engine.arm(True)
        return self.bridge.engine.emit('test', 'urgent', 'Synthetic impact/contact fixture.', [dict(id='impact', text='Three simulated impacts.', source='simulated_sensor', observed_at=datetime.now(timezone.utc).isoformat())])
    def packet(self):
        self.camera.state = 'monitoring'
        pixels = np.zeros((10, 10, 3), np.uint8)
        frame = Frame(1, datetime.now(timezone.utc).isoformat(), time.monotonic(), pixels)
        self.bridge.result = (frame, dict(people=[], sequence=1, captured_at=frame.captured_at, inference_ms=1), jpeg_frame()['image'])
    async def test_sensor_token_validation_arming(self):
        self.assertEqual((await self.client.post('/api/armed', json={'armed': True})).status_code, 403)
        self.assertEqual((await self.client.post('/api/armed', headers=self.headers, json={'armed': 'yes'})).status_code, 422)
        self.assertEqual((await self.client.post('/api/sensors', headers=self.headers, json={'kind': 'vision'})).status_code, 422)
        self.assertEqual((await self.client.post('/api/sensors', headers=self.headers, content=b'x'*1025)).status_code, 413)
        self.assertTrue((await self.client.post('/api/armed', headers=self.headers, json={'armed': True})).json()['armed'])
        response = await self.client.post('/api/sensors', headers=self.headers, json={'kind': 'bell'})
        self.assertEqual(response.json()['input']['source'], 'simulated_sensor')
        self.assertEqual(self.llm.calls, 0)
    async def test_urgent_survives_camera_loss_stop_and_explains(self):
        event = self.event()
        self.camera.state = 'unavailable'
        self.assertEqual(self.bridge.status()['severity'], 'urgent')
        self.assertIsNone(self.bridge.status()['frame'])
        answer = await self.client.post('/api/explain', headers=self.headers, json={'question': 'Which evidence supports the existing urgent event?'})
        self.assertEqual(answer.json()['source'], 'template_fallback')
        self.assertEqual(self.llm.calls, 1)
        await self.client.post('/api/camera/stop', headers=self.headers)
        self.assertEqual(self.bridge.status()['severity'], 'urgent')
        self.assertFalse(self.bridge.engine.armed)
        self.assertEqual((await self.client.post(f"/api/events/{event['id']}/acknowledge", headers=self.headers)).status_code, 200)
        self.assertEqual(self.bridge.status()['severity'], 'urgent')
    async def test_old_history_makes_no_qwen_call(self):
        event = self.event()
        event['created_at'] = (datetime.now(timezone.utc)-timedelta(seconds=61)).isoformat()
        self.bridge.store.save_event(event)
        result = await self.client.post('/api/explain', headers=self.headers, json={'question': 'Explain this event.', 'event_id': event['id']})
        self.assertEqual(result.json()['source'], 'application_unavailable')
        self.assertEqual(self.llm.calls, 0)
    async def test_new_event_discards_pending_answer(self):
        self.event()
        async def change():
            self.bridge.engine.emit('new', 'review', 'New fixture event.', [dict(id='bell', text='New simulated bell.', source='simulated_sensor', observed_at=datetime.now(timezone.utc).isoformat())])
        self.llm.hook = change
        response = await self.client.post('/api/explain', headers=self.headers, json={'question': 'Explain this event.'})
        self.assertEqual(response.json()['source'], 'discarded')
    async def test_explicit_snapshot_replay_delete(self):
        event = self.event()
        self.packet()
        self.bridge.capture_recording()
        self.assertEqual(self.bridge.store.event(event['id'])['media'], [])
        path = f"/api/events/{event['id']}/media/snapshot"
        self.assertEqual((await self.client.post(path)).status_code, 403)
        saved = (await self.client.post(path, headers=self.headers)).json()
        media_path = f"/api/media/{saved['id']}"
        self.assertEqual((await self.client.get(media_path)).status_code, 403)
        media = (await self.client.get(media_path, headers=self.headers)).json()
        self.assertEqual(media['source'], 'recorded_laptop_webcam')
        self.assertEqual(len(media['frames']), 1)
        self.assertEqual((await self.client.post(media_path+'/delete', headers=self.headers)).json(), {'deleted': True})
        self.assertEqual((await self.client.get(media_path, headers=self.headers)).status_code, 404)
        await self.bridge.stop()
        self.assertEqual((await self.client.post(path, headers=self.headers)).status_code, 409)
    async def test_record_stop_saves_once(self):
        event = self.event()
        self.packet()
        path = f"/api/events/{event['id']}/media/record"
        self.assertEqual((await self.client.post(path, headers=self.headers)).status_code, 200)
        self.assertEqual((await self.client.post(path, headers=self.headers)).status_code, 409)
        self.assertEqual(self.bridge.store.event(event['id'])['media'], [])
        await self.bridge.stop()
        self.assertIsNone(self.bridge.recording)
        self.assertEqual(len(self.bridge.store.event(event['id'])['media']), 1)
        self.bridge.finish_recording()
        self.assertEqual(len(self.bridge.store.event(event['id'])['media']), 1)
    async def test_history_feedback_validation(self):
        event = self.event()
        self.assertEqual((await self.client.get('/api/events')).status_code, 403)
        self.assertEqual((await self.client.get('/api/events', headers=self.headers)).json()['total'], 1)
        path = f"/api/events/{event['id']}/feedback"
        self.assertEqual((await self.client.post(path, headers=self.headers, json={'feedback': 'Safe'})).status_code, 422)
        self.assertEqual((await self.client.post(path, headers=self.headers, json={'feedback': FEEDBACK[2]})).json()['feedback'], FEEDBACK[2])
        self.assertEqual(self.llm.calls, 0)
    async def test_media_rejects_frame_before_event_and_old_record(self):
        self.packet()
        event = self.event()
        path = f"/api/events/{event['id']}/media/snapshot"
        response = await self.client.post(path, headers=self.headers)
        self.assertEqual(response.status_code, 409)
        self.assertIn('after the event', response.json()['detail'])
        self.packet()
        self.bridge.engine.active.clear()
        self.assertEqual((await self.client.post(path, headers=self.headers)).status_code, 409)
        self.assertEqual(self.bridge.store.event(event['id'])['media'], [])
    async def test_clip_timer_and_frame_budget_and_write_failure(self):
        event = self.event()
        self.packet()
        await self.client.post(f"/api/events/{event['id']}/media/record", headers=self.headers)
        self.assertIsNotNone(self.bridge.recording_timer)
        self.bridge.recording['frames'] = [jpeg_frame() for _ in range(50)]
        self.bridge.capture_recording()
        self.assertIsNone(self.bridge.recording)
        self.assertIsNone(self.bridge.recording_timer)
        self.assertEqual(len(self.bridge.store.event(event['id'])['media']), 1)
        self.bridge.recording = dict(event_id=event['id'], started=time.monotonic()-10.1, frames=[jpeg_frame()])
        with patch.object(self.bridge.store, 'save_media', side_effect=sqlite3.OperationalError('fixture disk full')):
            await self.bridge.stop()
        self.assertEqual(self.camera.state, 'paused')
        self.assertIsNone(self.bridge.recording)
        self.assertIn('could not be saved', self.bridge.media_error)
        self.assertEqual(self.bridge.status()['severity'], 'urgent')
    async def test_storage_fault_reports_503_without_erasing_alert(self):
        self.event()
        with patch.object(self.bridge.store, 'history', side_effect=sqlite3.OperationalError('fixture read failure')):
            self.assertEqual(self.bridge.status()['severity'], 'urgent')
            response = await self.client.get('/api/events', headers=self.headers)
            self.assertEqual(response.status_code, 503)
        self.assertIsNotNone(self.bridge.status()['storage_error'])
    async def test_evidence_export_has_no_images_token_or_offline_success_claim(self):
        self.assertEqual((await self.client.get('/api/evidence')).status_code, 403)
        self.packet()
        self.bridge.inference_samples.extend([10, 20])
        self.bridge.assessed_frames = 2
        await self.client.post('/api/explain', headers=self.headers, json={'question': 'What was observed?'})
        await self.bridge.stop()
        evidence = (await self.client.get('/api/evidence', headers=self.headers)).json()
        self.assertEqual(evidence['camera']['assessed_frames'], 2)
        self.assertEqual(evidence['vision']['median_ms'], 15)
        self.assertEqual(evidence['response_log'][0]['response']['source'], 'template_fallback')
        self.assertFalse(evidence['genuine_qwen_selection_observed'])
        self.assertIn('Not established', evidence['offline_acceptance'])
        self.assertNotIn('image', str(evidence['camera']))
        self.assertNotIn(self.bridge.token, str(evidence))


if __name__ == '__main__':
    unittest.main()
