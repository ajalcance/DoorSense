"""Local SQLite metadata and explicitly requested JPEG media. No automatic footage."""
import base64
import json
from pathlib import Path
import sqlite3
import uuid
from .events import stamp

FEEDBACK = ('Useful alert', 'Unnecessary alert', 'Incorrect detection')


class EventStore:
    def __init__(self, path=':memory:'):
        if str(path) != ':memory:':
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA secure_delete=ON')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS inputs (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS media (id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES events(id),
            kind TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS family_reference (id INTEGER PRIMARY KEY CHECK(id=1), created_at TEXT NOT NULL, payload TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    def family_reference(self, *, include_frame=False):
        row = self.db.execute('SELECT created_at,payload FROM family_reference WHERE id=1').fetchone()
        if not row:
            return None
        frame = json.loads(row[1])
        result = dict(category='Family member', source='owner_saved_reference', created_at=row[0],
                      captured_at=frame['captured_at'], sequence=frame['sequence'], automatic_matching=bool(frame.get('face_sample')),
                      method='OpenCV LBPH' if frame.get('face_sample') else None)
        if include_frame:
            result['frame'] = frame
        return result

    def save_family_reference(self, frame):
        pixels = base64.b64decode(frame['image'], validate=True)
        if not pixels.startswith(b'\xff\xd8') or not pixels.endswith(b'\xff\xd9') or len(pixels) > 2*1024*1024:
            raise ValueError('Reference must be a JPEG within the 2 MiB budget')
        with self.db:
            self.db.execute('INSERT INTO family_reference VALUES (1,?,?)', (stamp(), json.dumps(frame)))
        return self.family_reference()

    def delete_family_reference(self):
        with self.db:
            return self.db.execute('DELETE FROM family_reference WHERE id=1').rowcount == 1

    def save_event(self, event):
        with self.db:
            self.db.execute('INSERT INTO events VALUES (?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', (event['id'], json.dumps(event)))

    def save_input(self, record):
        with self.db:
            self.db.execute('INSERT INTO inputs VALUES (?,?)', (record['id'], json.dumps(record)))
            self.db.execute('DELETE FROM inputs WHERE rowid NOT IN (SELECT rowid FROM inputs ORDER BY rowid DESC LIMIT 10000)')

    def event(self, event_id):
        row = self.db.execute('SELECT payload FROM events WHERE id=?', (event_id,)).fetchone()
        if not row:
            return None
        event = json.loads(row[0])
        event['media'] = [dict(id=row[0], kind=row[1], created_at=row[2]) for row in self.db.execute(
            'SELECT id,kind,created_at FROM media WHERE event_id=? ORDER BY rowid DESC', (event_id,))]
        return event

    def history(self, offset=0, limit=25):
        ids = self.db.execute('SELECT id FROM events ORDER BY rowid DESC LIMIT ? OFFSET ?', (limit+1, offset)).fetchall()
        return {'events': [self.event(row[0]) for row in ids[:limit]], 'offset': offset,
                'next_offset': offset+limit if len(ids)>limit else None,
                'total': self.db.execute('SELECT count(*) FROM events').fetchone()[0]}

    def update(self, event_id, *, acknowledge=False, feedback=None):
        event = self.event(event_id)
        if not event:
            raise KeyError('Event not found')
        if feedback is not None and feedback not in FEEDBACK:
            raise ValueError('Select a supported feedback label')
        event.pop('media', None)
        if acknowledge:
            event['acknowledged_at'] = event['acknowledged_at'] or stamp()
        if feedback is not None:
            event['feedback'] = feedback
            event['feedback_at'] = stamp()
        self.save_event(event)
        return self.event(event_id)

    def save_media(self, event_id, kind, frames):
        if not self.event(event_id):
            raise KeyError('Event not found')
        if kind not in ('snapshot', 'clip') or not 1 <= len(frames) <= 50:
            raise ValueError('Invalid media request')
        if kind == 'snapshot' and len(frames) != 1:
            raise ValueError('Snapshot must have one frame')
        size = 0
        for frame in frames:
            pixels = base64.b64decode(frame['image'], validate=True)
            if not pixels.startswith(b'\xff\xd8') or not pixels.endswith(b'\xff\xd9'):
                raise ValueError('Media must contain encoded JPEG frames')
            size += len(pixels)
        if size > 20*1024*1024:
            raise ValueError('Clip exceeds 20 MiB budget')
        media_id, created = uuid.uuid4().hex, stamp()
        with self.db:
            self.db.execute('INSERT INTO media VALUES (?,?,?,?,?)', (media_id, event_id, kind, created, json.dumps(frames)))
        return dict(id=media_id, event_id=event_id, kind=kind, created_at=created)

    def media(self, media_id):
        row = self.db.execute('SELECT event_id,kind,created_at,payload FROM media WHERE id=?', (media_id,)).fetchone()
        return dict(id=media_id, event_id=row[0], kind=row[1], created_at=row[2], frames=json.loads(row[3]), source='recorded_laptop_webcam') if row else None

    def delete_media(self, media_id):
        with self.db:
            return self.db.execute('DELETE FROM media WHERE id=?', (media_id,)).rowcount == 1
