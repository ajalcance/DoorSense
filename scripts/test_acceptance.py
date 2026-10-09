"""Synthetic acceptance records cannot establish genuine/offline acceptance."""
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from acceptance import template, review, destination
from reproduction_check import inventory


class Tests(unittest.TestCase):
    def test_blank_report_cannot_pass(self):
        self.assertFalse(review(template(), None)['acceptance_ready'])

    def test_pass_requires_concrete_evidence_and_time(self):
        document = template()
        document['checks']['face_quality']['outcome'] = 'passed'
        with self.assertRaises(ValueError):
            review(document, None)

    def test_fixture_report_rejected(self):
        document = template()
        document['evidence_kind'] = 'fixture'
        with self.assertRaises(ValueError):
            review(document, None)

    def test_owner_claims_without_runtime_are_not_complete(self):
        document = template()
        document['tested_at'] = datetime.now(timezone.utc).isoformat()
        for row in document['checks'].values():
            row.update(outcome='passed', evidence='Synthetic owner evidence for schema testing only.')
        report = review(document, {'generated_at':document['tested_at'], 'camera':{'assessed_frames':2}})
        self.assertFalse(report['acceptance_ready'])
        self.assertIn('accepted_local_qwen_response_missing', report['blockers'])
        self.assertIn('face_runtime_evidence_missing', report['blockers'])

    def test_failed_checkpoint_keeps_report_incomplete(self):
        document = template()
        document['checks']['storage_restart'].update(outcome='failed', evidence='Injected storage failure.')
        self.assertIn('storage_restart', review(document, None)['blockers'])

    def test_current_acceptance_needs_face_demo_checks_not_pose_or_sensors(self):
        document = template()
        self.assertIn('unknown_after_deletion', document['checks'])
        self.assertIn('child_safety_mode', document['checks'])
        self.assertNotIn('pose_quality', document['checks'])
        self.assertNotIn('urgent_event', document['checks'])
        runtime = {'generated_at': datetime.now(timezone.utc).isoformat(),
                   'camera': {'assessed_frames': 1},
                   'genuine_qwen_selection_observed': True,
                   'scene_features': {'face': {'assessed_frames': 1, 'model_sha256': 'synthetic'}}}
        report = review(document, runtime)
        self.assertNotIn('pose_runtime_evidence_missing', report['blockers'])
        self.assertFalse(report['acceptance_ready'])

    def test_old_reports_remain_explicitly_historical(self):
        document = template()
        document['schema'] = 'doorsense-owner-acceptance-v1'
        report = review(document, None)
        self.assertEqual(report['demonstration_scope'], 'historical sensor/pose workflow')
        self.assertIn('urgent_event', report['blockers'])

    def test_output_cannot_escape_ignored_runtime(self):
        with self.assertRaises(ValueError):
            destination(Path('/private/tmp/acceptance.json'))

    def test_source_inventory_excludes_sensitive_and_obsolete_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('README.md', 'data/events.sqlite3', 'assets/models/face.task', '.runtime/private.json',
                         'frontend/src/main.jsx', 'frontend/src/fixtures.js', 'scripts/console_preview.py'):
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic')
            names = {row['path'] for row in inventory(root)}
            self.assertEqual(names, {'README.md', 'frontend/src/main.jsx'})


if __name__ == '__main__':
    unittest.main()
