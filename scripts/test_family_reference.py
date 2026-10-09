"""Private reference persistence checks with temporary SQLite and synthetic JPEGs."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from doorsense.store import EventStore
from test_events import jpeg_frame


class FamilyReference(unittest.TestCase):
    def test_reference_survives_reopen_and_delete_preserves_events(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'events.sqlite3'
            store = EventStore(path)
            event = dict(id='saved', revision=1, severity='review', facts=[], feedback='Useful alert')
            store.save_event(event)
            frame = jpeg_frame()
            store.save_family_reference(frame)
            store.close()
            store = EventStore(path)
            try:
                self.assertEqual(store.family_reference(include_frame=True)['frame'], frame)
                self.assertTrue(store.delete_family_reference())
                self.assertIsNone(store.family_reference())
                self.assertEqual(store.event('saved')['feedback'], 'Useful alert')
                self.assertEqual(store.history()['total'], 1)
            finally:
                store.close()
    def test_invalid_image_cannot_be_registered(self):
        store = EventStore()
        try:
            with self.assertRaises(ValueError):
                store.save_family_reference({**jpeg_frame(), 'image':'invalid JPEG'})
            self.assertIsNone(store.family_reference())
        finally:
            store.close()
