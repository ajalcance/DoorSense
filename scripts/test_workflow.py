"""Integrated synthetic service/SQLite workflow. No camera, network or Qwen inference."""
import base64
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import httpx
import numpy as np
from test_console import Camera, LLM
from doorsense.camera import Frame
from doorsense.console import Console, create_app
from doorsense.store import EventStore


class Workflow(unittest.IsolatedAsyncioTestCase):
    async def test_rules_scene_context_media_feedback_and_database_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'events.sqlite3'
            store = EventStore(path)
            camera, llm = Camera(), LLM()
            bridge = Console(camera=camera, llm=llm, store=store, legacy_activity=True)
            clock = [0]
            bridge.engine.clock = lambda: clock[0]
            headers = {'x-doorsense-token': bridge.token}
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(bridge)), base_url='http://127.0.0.1:8765') as client:
                self.assertEqual((await client.post('/api/armed', headers=headers, json={'armed':True})).status_code, 200)
                for kind in ('bell', 'bell', 'bell'):
                    clock[0] += .3
                    response = await client.post('/api/sensors', headers=headers, json={'kind':kind})
                self.assertEqual(response.json()['event']['severity'], 'review')
                camera.state = 'monitoring'
                assessed = Frame(1, datetime.now(timezone.utc).isoformat(), time.monotonic(), np.zeros((8,8,3), np.uint8))
                bridge.result = (assessed, dict(people=[{'box':[0,0,8,8]}], inference_ms=1), 'in-process frame')
                for kind in ('contact_closed', 'impact', 'impact', 'impact'):
                    clock[0] += .3
                    bridge.engine.observe(1, clock[0], datetime.now(timezone.utc).isoformat())
                    response = await client.post('/api/sensors', headers=headers, json={'kind':kind})
                event = response.json()['event']
                self.assertEqual(event['severity'], 'urgent')
                self.assertEqual({f['source'] for f in event['facts']}, {'laptop_webcam', 'simulated_sensor'})
                pixels = np.zeros((8, 8, 3), np.uint8)
                frame = Frame(1, datetime.now(timezone.utc).isoformat(), time.monotonic(), pixels)
                encoded = base64.b64encode(cv2.imencode('.jpg', pixels)[1]).decode('ascii')
                camera.state = 'monitoring'
                bridge.result = (frame, dict(people=[{'box':[0,0,8,8]}], inference_ms=1,
                    features={'face':dict(state='available', descriptions=['The face model suggests raised mouth corners.'])}), encoded)
                # Appearance never weakens an urgent sensor event or enters its rule facts.
                self.assertEqual(bridge.status()['event']['severity'], 'urgent')
                self.assertFalse(any(f.id.startswith('face') for f in bridge.context().facts))
                answer = await client.post('/api/explain', headers=headers, json={'question':'Explain this event.'})
                self.assertEqual(answer.json()['source'], 'template_fallback')
                media_ids = []
                for action in ('snapshot', 'record', 'stop'):
                    result = await client.post(f'/api/events/{event["id"]}/media/{action}', headers=headers)
                    self.assertEqual(result.status_code, 200, result.text)
                    if action != 'record':
                        media_ids.append(result.json()['id'])
                for media_id in media_ids:
                    result = await client.get('/api/media/'+media_id, headers=headers)
                    self.assertEqual(result.json()['frames'][0]['image'], encoded)
                    self.assertEqual(result.json()['source'], 'recorded_laptop_webcam')
                acknowledged = await client.post(f'/api/events/{event["id"]}/acknowledge', headers=headers)
                self.assertEqual(acknowledged.status_code, 200)
                feedback = await client.post(f'/api/events/{event["id"]}/feedback', headers=headers, json={'feedback':'Useful alert'})
                self.assertEqual(feedback.status_code, 200)
                await client.post('/api/camera/stop', headers=headers)
                self.assertEqual(bridge.status()['event']['severity'], 'urgent')
                self.assertEqual(camera.state, 'paused')
                store.close()
            reopened = EventStore(path)
            try:
                saved = reopened.event(event['id'])
                self.assertEqual(saved['feedback'], 'Useful alert')
                self.assertIsNotNone(saved['acknowledged_at'])
                self.assertEqual(len(saved['media']), 2)
                self.assertEqual(reopened.history()['total'], 2)
                self.assertTrue(reopened.delete_media(media_ids[0]))
                self.assertIsNone(reopened.media(media_ids[0]))
                self.assertEqual(reopened.event(event['id'])['severity'], 'urgent')
            finally:
                reopened.close()


if __name__ == '__main__':
    unittest.main()
