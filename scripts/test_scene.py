"""Injected model outputs only: no camera, task construction or genuine inference."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR'] = str(ROOT / '.runtime/matplotlib')
os.environ['XDG_CACHE_HOME'] = str(ROOT / '.runtime/cache')
sys.path.insert(0, str(ROOT / 'backend'))
import numpy as np
from doorsense.camera import Frame
from doorsense.observations import Stabilizer, face_descriptions, pose_descriptions, observation_facts, observation_key
from doorsense.scene import SceneDetector, model_path


def face(**scores):
    return NS(face_landmarks=[[NS(x=.5, y=.5) for _ in range(478)]], face_blendshapes=[[NS(category_name=k, score=v) for k, v in scores.items()]])


def pose(visibility=1, left=.2, right=.2):
    points = [NS(x=.5, y=.5, presence=1, visibility=visibility) for _ in range(33)]
    points[15].y, points[16].y = left, right
    return NS(pose_landmarks=[points])


class Person:
    model_sha256 = 'fixture'
    def __init__(self, count=1):
        self.count, self.closed = count, False
    def detect(self, frame):
        return dict(people=[{}]*self.count, objects=[], sequence=frame.sequence, captured_at=frame.captured_at, inference_ms=1)
    def close(self):
        self.closed = True


class Task:
    def __init__(self, output=None, fail=False, close_fail=False):
        self.output, self.fail, self.close_fail, self.closed = output, fail, close_fail, False
    def detect(self, image):
        if self.fail:
            raise ValueError('fixture inference failure')
        return self.output
    def close(self):
        self.closed = True
        if self.close_fail:
            raise ValueError('fixture cleanup failure')


class Tests(unittest.TestCase):
    def frame(self, seq=1, clock=1):
        return Frame(seq, '2026-10-09T00:00:00+00:00', clock, np.zeros((4, 4, 3), np.uint8))

    def test_face_threshold_and_bilateral_requirements(self):
        self.assertEqual(len(face_descriptions(face(jawOpen=.8))[0]), 1)
        self.assertEqual(face_descriptions(face(jawOpen=.64, mouthSmileLeft=.9))[0], [])
        self.assertEqual(len(face_descriptions(face(mouthSmileLeft=.8, mouthSmileRight=.8))[0]), 1)
        self.assertEqual(face_descriptions(face(jawOpen=float('nan')))[0], [])
        self.assertEqual(face_descriptions(face(jawOpen=1.1))[0], [])

    def test_missing_or_multiple_faces_are_limited(self):
        output = face(jawOpen=.9)
        output.face_landmarks.append([])
        self.assertIsNotNone(face_descriptions(output)[1])
        self.assertIsNotNone(face_descriptions(NS(face_landmarks=[], face_blendshapes=[]))[1])
        output = face(jawOpen=.9)
        output.face_landmarks[0][0].x = -1
        self.assertIsNotNone(face_descriptions(output)[1])

    def test_pose_requires_in_frame_visible_wrists_and_shoulders(self):
        self.assertIn('both wrists', pose_descriptions(pose())[0][0])
        self.assertIn('one wrist', pose_descriptions(pose(right=.6))[0][0])
        self.assertEqual(pose_descriptions(pose(left=.6, right=.6))[0], [])
        self.assertIsNotNone(pose_descriptions(pose(visibility=.3))[1])
        output = pose()
        output.pose_landmarks[0][15].x = -1
        self.assertIsNotNone(pose_descriptions(output)[1])

    def test_stabilization_gap_disappearance_and_restart(self):
        stabilizer = Stabilizer()
        self.assertEqual(stabilizer.update(['mouth'], self.frame()), [])
        self.assertEqual(stabilizer.update(['mouth'], self.frame(2, 1.2)), ['mouth'])
        self.assertEqual(stabilizer.update([], self.frame(3, 1.4)), [])
        self.assertEqual(stabilizer.update(['mouth'], self.frame(4, 1.6)), [])
        self.assertEqual(stabilizer.update(['mouth'], self.frame(5, 3)), [])
        stabilizer.reset()
        self.assertEqual(stabilizer.update(['mouth'], self.frame(6, 3.2)), [])

    def test_disabled_features_never_construct_optional_models(self):
        detector = SceneDetector(Person(), enabled=set(), task_factory=lambda name: self.fail('unexpected task'))
        result = detector.detect(self.frame())
        self.assertEqual(result['features']['face']['state'], 'disabled')
        self.assertEqual(result['features']['pose']['descriptions'], [])

    def test_missing_model_does_not_break_person_or_other_feature(self):
        def factory(name):
            if name == 'face':
                raise ValueError('fixture missing file')
            return Task(pose()), 'fixture-pose'
        detector = SceneDetector(Person(), enabled={'face', 'pose'}, task_factory=factory)
        result = detector.detect(self.frame())
        self.assertEqual(len(result['people']), 1)
        self.assertEqual(result['features']['face']['state'], 'unavailable')
        self.assertEqual(result['features']['pose']['state'], 'available')

    def test_optional_inference_failure_isolated_and_not_retried(self):
        task = Task(fail=True)
        detector = SceneDetector(Person(), enabled={'face'}, task_factory=lambda name: (task, 'fixture'))
        result = detector.detect(self.frame())
        self.assertEqual(len(result['people']), 1)
        self.assertEqual(result['features']['face']['state'], 'unavailable')
        self.assertTrue(task.closed)
        self.assertNotIn('face', detector.tasks)
        self.assertEqual(detector.detect(self.frame(2, 1.2))['features']['face']['state'], 'unavailable')

    def test_multi_person_clears_stabilized_descriptions(self):
        person = Person()
        detector = SceneDetector(person, enabled={'face'}, task_factory=lambda name: (Task(face(jawOpen=.9)), 'fixture'))
        self.assertFalse(detector.detect(self.frame())['features']['face']['descriptions'])
        self.assertTrue(detector.detect(self.frame(2, 1.2))['features']['face']['descriptions'])
        person.count = 2
        self.assertEqual(detector.detect(self.frame(3, 1.4))['features']['face']['state'], 'limited')
        person.count = 1
        self.assertFalse(detector.detect(self.frame(4, 1.6))['features']['face']['descriptions'])

    def test_close_attempts_all_tasks_even_after_failure(self):
        person = Person()
        face_task, pose_task = Task(close_fail=True), Task()
        detector = SceneDetector(person, enabled={'face', 'pose'}, task_factory=lambda name: (face_task if name == 'face' else pose_task, 'fixture'))
        with self.assertRaises(RuntimeError):
            detector.close()
        self.assertTrue(person.closed and face_task.closed and pose_task.closed)

    def test_slow_optional_model_releases_and_preserves_person_detection(self):
        task = Task(face(jawOpen=.9))
        detector = SceneDetector(Person(), enabled={'face'}, task_factory=lambda name: (task, 'fixture'))
        with patch('doorsense.scene.time.perf_counter', side_effect=[0, 0, .7, .71]):
            result = detector.detect(self.frame())
        self.assertEqual(result['features']['face']['state'], 'unavailable')
        self.assertTrue(task.closed)
        self.assertEqual(len(detector.detect(self.frame(2, 1.2))['people']), 1)

    def test_facts_bound_and_signature_change_without_person_count_change(self):
        observation = dict(people=[{}], objects=[{'label': 'handbag'}], features={'face':dict(state='available', descriptions=['Visible movement.'])})
        facts = observation_facts(observation)
        self.assertEqual(facts[0][1], 'The detector reported 1 person in this frame.')
        self.assertIn('ownership', facts[1][1])
        signature = observation_key(observation)
        observation['features']['face']['state'] = 'unavailable'
        self.assertNotEqual(signature, observation_key(observation))
        self.assertEqual(len(observation_facts(observation)), 2)


if __name__ == '__main__':
    unittest.main()
