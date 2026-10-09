"""Synthetic bundle/receipt integrity checks; no model acquisition or inference."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import prepare_scene_models as preparation


class Tests(unittest.TestCase):
    def test_offline_transfer_records_and_rechecks_bytes_without_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'assets').mkdir()
            spec = {'face':dict(filename='face.task',url='https://storage.googleapis.com/mediapipe-models/synthetic-test',licence_status='test only')}
            (root/'assets/scene-models.json').write_text(json.dumps(spec))
            bundle = root/'synthetic.task'
            with zipfile.ZipFile(bundle, 'w') as archive:
                archive.writestr('detector.tflite', b'0000TFL3synthetic')
                archive.writestr('landmarker.tflite', b'0000TFL3synthetic')
            with patch.object(preparation, 'ROOT', root):
                record = preparation.acquire('face', import_file=bundle)
                self.assertEqual(record['acquisition'], 'offline transfer')
                self.assertEqual(preparation.acquire('face', import_file=bundle)['sha256'], record['sha256'])
                (root/'assets/models/face.task').write_bytes(b'corrupt fixture')
                with self.assertRaisesRegex(ValueError, 'Existing model'):
                    preparation.acquire('face', import_file=bundle)
                self.assertEqual((root/'assets/models/face.task').read_bytes(), b'corrupt fixture')

    def test_explicit_acquisition_required_and_destination_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'assets').mkdir()
            (root/'assets/scene-models.json').write_text(json.dumps({'face':dict(filename='face.task',url='synthetic')}))
            with patch.object(preparation, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Explicit owner'):
                    preparation.acquire('face')
                with self.assertRaises(ValueError):
                    preparation.inside(root/'.git/model.task')

    def test_non_model_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'synthetic.task'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('a.tflite', 'not a model')
                archive.writestr('b.tflite', 'not a model')
            with self.assertRaises(ValueError):
                preparation.verify_bundle(path)


if __name__ == '__main__':
    unittest.main()
