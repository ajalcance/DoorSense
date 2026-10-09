"""Real LBPH fit/predict on synthetic textures, not human recognition accuracy."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import numpy as np
from doorsense.recognition import FamilyMatcher, encode_sample, face_crop


def observation(**changes):
    return dict(dict(sequence=1, captured_at='2026-10-10T00:00:00Z', people=[{}],
                     features={'face': {'state': 'available', 'box': [0, 0, 1, 1]}}), **changes)


class Recognition(unittest.TestCase):
    def setUp(self):
        self.image = np.random.default_rng(42).integers(0, 255, (128, 128, 3), dtype=np.uint8)
        self.obs = observation()
        self.reference = {'frame': {'face_sample': encode_sample(self.image, self.obs)}}

    def test_enrollment_match_rejection_deletion_reenrollment(self):
        matcher = FamilyMatcher()
        self.assertEqual(matcher.assess(self.image, self.obs, None)['category'], 'Unknown')
        matched = matcher.assess(self.image, self.obs, self.reference)
        self.assertEqual(matched['category'], 'Family member')
        self.assertAlmostEqual(matched['distance'], 0)
        self.assertEqual(matched['trained_examples'], 1)
        self.assertGreaterEqual(matched['training_ms'], 0)
        self.assertGreaterEqual(matched['inference_ms'], 0)
        self.assertEqual(matcher.assess(np.zeros_like(self.image), self.obs, self.reference)['category'], 'Unknown')
        self.assertEqual(matcher.assess(self.image, self.obs, None)['state'], 'no_reference')
        self.assertIsNone(matcher.model)
        self.assertEqual(matcher.assess(self.image, self.obs, self.reference)['state'], 'matched')

    def test_missing_multi_person_small_and_invalid_faces_abstain(self):
        matcher = FamilyMatcher()
        for obs in [observation(people=[]), observation(people=[{}, {}]),
                    observation(features={'face': {'state': 'limited'}}),
                    observation(features={'face': {'state': 'available', 'box': [0, 0, .1, .1]}}),
                    observation(features={'face': {'state': 'available', 'box': [0, 0, float('nan'), 1]}})]:
            with self.assertRaises(ValueError):
                face_crop(self.image, obs)
            self.assertEqual(matcher.assess(self.image, obs, self.reference)['category'], 'Unknown')

    def test_legacy_photo_and_corrupt_sample_abstain(self):
        matcher = FamilyMatcher()
        self.assertEqual(matcher.assess(self.image, self.obs, {'frame': {}})['state'], 'no_reference')
        self.assertEqual(matcher.assess(self.image, self.obs, {'frame': {'face_sample': 'bad'}})['state'], 'limited')

    def test_deleted_enrollment_cannot_be_reloaded_by_an_old_inflight_comparison(self):
        matcher=FamilyMatcher()
        generation=matcher.generation
        matcher.clear()
        result=matcher.assess(self.image,self.obs,self.reference,generation)
        self.assertEqual(result['state'],'limited')
        self.assertIsNone(matcher.model)
        self.assertIsNone(matcher.sample)

    def test_decision_and_displayed_distance_use_the_same_precision(self):
        matcher=FamilyMatcher()
        matcher.assess(self.image,self.obs,self.reference)
        matcher.model=Mock()
        matcher.model.predict.return_value=(1,65.004)
        accepted=matcher.assess(self.image,self.obs,self.reference)
        self.assertEqual(accepted['distance'],65.00)
        self.assertEqual(accepted['category'],'Family member')
        matcher.model.predict.return_value=(1,65.006)
        rejected=matcher.assess(self.image,self.obs,self.reference)
        self.assertEqual(rejected['distance'],65.01)
        self.assertEqual(rejected['category'],'Unknown')


if __name__ == '__main__':
    unittest.main()
