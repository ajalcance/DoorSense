"""Optional MediaPipe tasks, loaded locally after explicit owner configuration."""
import hashlib
import json
import os
from pathlib import Path
import time

import cv2
import mediapipe as mp

from .observations import Stabilizer, face_descriptions, pose_descriptions, observation_facts
from .vision import PersonDetector

ROOT = Path(__file__).resolve().parents[2]


def model_path(name):
    spec = json.loads((ROOT / 'assets/scene-models.json').read_text())[name]
    path = (ROOT / 'assets/models' / spec['filename']).resolve()
    if not path.is_relative_to((ROOT / 'assets/models').resolve()) or not path.is_relative_to(ROOT):
        raise ValueError('Model path escapes local assets')
    if not path.is_file():
        raise ValueError('Local model missing; use owner preparation. No automatic download.')
    receipt = json.loads((ROOT / '.runtime/scene-assets.json').read_text())[name]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if receipt['url'] != spec['url'] or receipt['path'] != 'assets/models/'+spec['filename'] or receipt['sha256'] != actual or receipt['bytes'] != path.stat().st_size:
        raise ValueError('Local model receipt/hash mismatch; inspect assets.')
    return path, actual


def create_task(name):
    path, digest = model_path(name)
    base = mp.tasks.BaseOptions(model_asset_path=str(path), delegate=mp.tasks.BaseOptions.Delegate.CPU)
    common = dict(base_options=base, running_mode=mp.tasks.vision.RunningMode.IMAGE)
    if name == 'face':
        options = mp.tasks.vision.FaceLandmarkerOptions(**common, num_faces=2,
            min_face_detection_confidence=.6, min_face_presence_confidence=.6, output_face_blendshapes=True)
        task = mp.tasks.vision.FaceLandmarker.create_from_options(options)
    else:
        options = mp.tasks.vision.PoseLandmarkerOptions(**common, num_poses=2,
            min_pose_detection_confidence=.6, min_pose_presence_confidence=.6, output_segmentation_masks=False)
        task = mp.tasks.vision.PoseLandmarker.create_from_options(options)
    return task, digest


class SceneDetector:
    def __init__(self, detector=None, enabled=None, task_factory=create_task):
        self.person = detector or PersonDetector(include_objects=os.environ.get('DOORSENSE_OBJECTS') == '1')
        self.model_sha256 = self.person.model_sha256
        self.tasks, self.features, self.stabilizers = {}, {}, {}
        enabled = enabled if enabled is not None else {name for name in ('face', 'pose') if os.environ.get('DOORSENSE_'+name.upper()) == '1'}
        self.cleanup_failed = False
        self.slow_frames = {'face': 0, 'pose': 0}
        for name in ('face', 'pose'):
            self.stabilizers[name] = Stabilizer()
            self.features[name] = dict(state='disabled', message='Not enabled. Requires local model and separate quality/resource checks.', model_sha256=None)
            if name in enabled:
                try:
                    task, digest = task_factory(name)
                    self.tasks[name] = task
                    self.features[name] = dict(state='waiting', message='Waiting for an assessed frame.', model_sha256=digest)
                except Exception:
                    self.features[name] = dict(state='unavailable', message='Local model missing, unverified or failed to load. Inspect owner preparation; restart to retry.', model_sha256=None)

    def reset(self):
        for value in self.stabilizers.values():
            value.reset()

    def detect(self, frame):
        began = time.perf_counter()
        observation = self.person.detect(frame)
        image = None
        features = {}
        for name, config in self.features.items():
            result = dict(config, descriptions=[], sequence=frame.sequence, captured_at=frame.captured_at, inference_ms=None)
            task = self.tasks.get(name)
            if task is not None:
                if len(observation['people']) != 1:
                    self.stabilizers[name].reset()
                    result.update(state='limited', message='Exactly one detected person is required; no personal association is inferred.')
                else:
                    started = time.perf_counter()
                    try:
                        if image is None:
                            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame.pixels, cv2.COLOR_BGR2RGB))
                        output = task.detect(image)
                        descriptions, limited = (face_descriptions if name == 'face' else pose_descriptions)(output)
                        result.update(state='limited' if limited else 'available', message=limited or 'Prototype descriptions; thresholds require held-out validation.',
                                      descriptions=self.stabilizers[name].update(descriptions, frame),
                                      inference_ms=(time.perf_counter()-started)*1000)
                        if name == 'face' and not limited:
                            points = output.face_landmarks[0]
                            result['box'] = [min(p.x for p in points), min(p.y for p in points),
                                             max(p.x for p in points), max(p.y for p in points)]
                        self.slow_frames[name] = self.slow_frames[name]+1 if result['inference_ms'] > 200 else 0
                        if result['inference_ms'] > 600 or self.slow_frames[name] >= 3:
                            result.update(state='unavailable', descriptions=[], message='Feature exceeded the prototype inference budget. Person detection continues; restart with fewer features enabled.')
                            self.tasks.pop(name)
                            self.stabilizers[name].reset()
                            try:
                                task.close()
                            except Exception:
                                self.cleanup_failed = True
                                result['message'] += ' Model cleanup failed; restart required.'
                            self.features[name] = dict(result)
                    except Exception:
                        result.update(state='unavailable', message='Model inference failed. Person detection continues; restart the console to retry.')
                        self.stabilizers[name].reset()
                        self.tasks.pop(name)
                        try:
                            task.close()
                        except Exception:
                            self.cleanup_failed = True
                            result['message'] += ' Model cleanup failed; restart required.'
                        self.features[name] = dict(result)
            features[name] = result
        observation['features'] = features
        observation['facts'] = [dict(id=identity, text=text, source=frame.source, observed_at=frame.captured_at)
                                for identity, text in observation_facts(observation)]
        observation['inference_ms'] = (time.perf_counter()-began)*1000
        return observation

    def close(self):
        failed = self.cleanup_failed
        tasks = [self.person, *self.tasks.values()]
        self.tasks = {}
        for task in tasks:
            try:
                task.close()
            except Exception:
                failed = True
        if failed:
            raise RuntimeError('One or more vision models failed to close; restart required.')
