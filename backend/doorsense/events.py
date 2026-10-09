"""Deterministic, configurable prototype rules. Sensors are explicitly simulated."""
from collections import deque
from datetime import datetime, timezone
import time
import uuid
import math
import sqlite3


def stamp():
    return datetime.now(timezone.utc).isoformat()


class EventEngine:
    def __init__(self, store, *, clock=time.monotonic, bell_count=3, bell_window=10,
                 impact_count=3, impact_window=5, occupancy_seconds=30,
                 debounce_seconds=.25, review_seconds=60, urgent_seconds=120):
        self.store, self.clock = store, clock
        self.config = dict(bell_count=bell_count, bell_window=bell_window,
                           impact_count=impact_count, impact_window=impact_window,
                           occupancy_seconds=occupancy_seconds, debounce_seconds=debounce_seconds,
                           review_seconds=review_seconds, urgent_seconds=urgent_seconds)
        if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in self.config.values()):
            raise ValueError('Rule thresholds must be positive')
        if type(bell_count) is not int or type(impact_count) is not int:
            raise ValueError('Sensor count thresholds must be integers')
        self.armed = False
        self.inputs = deque(maxlen=128)
        self.last = {}
        self.contact = None
        self.replies = deque(maxlen=6)
        self.input_revision = 0
        self.active = {}
        self.revision = 0
        self.storage_error = None
        self.occupancy_start = self.occupancy_last = None
        self.occupancy_fired = False
        self.person_evidence = None

    def arm(self, value):
        if type(value) is not bool:
            raise ValueError('Armed must be a boolean')
        if value != self.armed:
            self.armed = value
            self.inputs.clear()
            self.last.clear()
            self.replies.clear()
            self.input_revision += 1
            self.occupancy_start = self.occupancy_last = None
            self.occupancy_fired = False
            self.person_evidence = None
            self.revision += 1
        # Disarming never erases a previously raised alert.

    def simulation(self):
        """Session state calculated from the same monotonic inputs as the rules."""
        now = self.clock()
        progress = {}
        for kind in ('bell', 'impact'):
            window, required = self.config[kind+'_window'], self.config[kind+'_count']
            entries = [entry for entry in self.inputs if self.armed and entry['kind'] == kind
                       and (kind != 'impact' or entry.get('door_closed'))
                       and 0 <= now-entry['monotonic'] <= window]
            # Time until the count drops below the requirement (or the first
            # pending input expires). No browser click/log reconstruction.
            anchor = entries[-required] if len(entries) >= required else entries[0] if entries else None
            progress[kind] = dict(count=len(entries), required=required,
                                  remaining_seconds=max(0, window-(now-anchor['monotonic'])) if anchor else 0)
        fresh = self.armed and self.occupancy_last is not None and 0 <= now-self.occupancy_last < .8
        elapsed = max(0, self.occupancy_last-self.occupancy_start) if fresh else 0
        person_fresh = bool(self.person_evidence and 0 <= now-self.person_evidence['monotonic'] < .8)
        return dict(revision=self.input_revision, source='simulated_sensor', contact=self.contact,
                    camera_evidence=dict(fresh=person_fresh, count=self.person_evidence['count'] if person_fresh else 0,
                                         fresh_remaining_seconds=max(0, .8-(now-self.person_evidence['monotonic'])) if person_fresh else 0),
                    progress=progress, replies=list(self.replies),
                    occupancy=dict(elapsed_seconds=elapsed, required_seconds=self.config['occupancy_seconds'],
                                   remaining_seconds=max(0, self.config['occupancy_seconds']-elapsed), fresh=bool(fresh),
                                   fresh_remaining_seconds=max(0, .8-(now-self.occupancy_last)) if fresh else 0))

    def reply(self, kind, result):
        self.replies.append(dict(kind=kind, accepted=result['accepted'], reason=result.get('reason'),
                                 observed_at=result.get('input', {}).get('observed_at') or stamp(),
                                 armed=self.armed, severity=(result.get('event') or {}).get('severity')))
        self.input_revision += 1
        return result

    def combined_impact_alert(self):
        now = self.clock()
        person = self.person_evidence
        if not self.armed or not self.contact or self.contact['kind'] != 'contact_closed' or not person or not 0 <= now-person['monotonic'] < .8:
            return None
        impacts = [entry for entry in self.inputs if entry['kind'] == 'impact' and entry.get('door_closed')
                   and 0 <= now-entry['monotonic'] <= self.config['impact_window']]
        if len(impacts) < self.config['impact_count']:
            return None
        return self.emit('person_closed_door_impacts', 'urgent',
                         'Fresh camera person detection and repeated simulated impacts on a closed door while Child safety mode is on.', [
            dict(id='person', text=f"The webcam detector reported {person['count']} {'person' if person['count'] == 1 else 'people'} in a fresh assessed frame.", source='laptop_webcam', observed_at=person['observed_at']),
            dict(id='impact', text=f"{len(impacts)} simulated impacts occurred within {self.config['impact_window']} seconds.", source='simulated_sensor', observed_at=impacts[-1]['observed_at']),
            dict(id='contact', text='The simulated door contact indicated closed throughout the qualifying impacts.', source='simulated_sensor', observed_at=self.contact['observed_at'])])

    def current(self):
        now = self.clock()
        expired = [key for key, (_, deadline) in self.active.items() if now >= deadline]
        for key in expired:
            del self.active[key]
            self.revision += 1
        candidates = [self.record(event['id']) for event, _ in self.active.values()]
        candidates = [event for event in candidates if event]
        return max(candidates, key=lambda event: (event['severity'] == 'urgent', event['created_at']), default=None)

    def record(self, event_id):
        try:
            saved = self.store.event(event_id)
            if saved:
                return saved
        except (sqlite3.Error, OSError):
            self.storage_error = 'Local event storage unavailable. Active alerts remain in this session; restart after checking storage.'
        return next((event for event, _ in self.active.values() if event['id'] == event_id), None)

    def emit(self, rule, severity, reason, facts):
        self.current()
        if rule in self.active:
            return None
        created = stamp()
        duration = self.config['urgent_seconds' if severity == 'urgent' else 'review_seconds']
        event = dict(id=uuid.uuid4().hex, revision=1, rule_id=rule, severity=severity,
                     rule_reason=reason, created_at=created,
                     expires_at=datetime.fromtimestamp(datetime.fromisoformat(created).timestamp() + duration, timezone.utc).isoformat(),
                     facts=facts, acknowledged_at=None, feedback=None,
                     uncertainties=['Identity, intent and safety are not established.',
                                    'Prototype thresholds are unvalidated; sensor inputs are simulated.'])
        event.update(media=[], persisted=True)
        try:
            self.store.save_event(event)
        except (sqlite3.Error, OSError):
            event['persisted'] = False
            self.storage_error = 'Event could not be persisted locally. Active alert remains in this session only.'
        self.active[rule] = (event, self.clock() + duration)
        self.revision += 1
        return event

    def sensor(self, kind):
        if kind not in ('bell', 'impact', 'contact_open', 'contact_closed'):
            raise ValueError('Unknown simulated sensor')
        now = self.clock()
        # Repeated identical contact states are not fresh corroboration.
        if now - self.last.get(kind, -float('inf')) < self.config['debounce_seconds']:
            return self.reply(kind, {'accepted': False, 'reason': 'debounced', 'source': 'simulated_sensor'})
        contact = self.contact
        if kind.startswith('contact_') and contact and contact['kind'] == kind:
            return self.reply(kind, {'accepted': False, 'reason': 'unchanged_contact', 'source': 'simulated_sensor'})
        self.last[kind] = now
        record = dict(id=uuid.uuid4().hex, kind=kind, observed_at=stamp(), value=kind,
                      source='simulated_sensor', armed=self.armed)
        try:
            self.store.save_input(record)
        except (sqlite3.Error, OSError):
            self.storage_error = 'Simulated input could not be persisted locally. Check event storage.'
        self.inputs.append({**record, 'monotonic': now,
                            'door_closed': bool(self.contact and self.contact['kind'] == 'contact_closed')})
        if kind.startswith('contact_'):
            self.contact = record
            # Opening/closing ends the previous closed-door impact sequence.
            self.inputs = deque((entry for entry in self.inputs if entry['kind'] != 'impact'), maxlen=128)
        raised = None
        if self.armed:
            bells = [entry for entry in self.inputs if entry['kind'] == 'bell' and now-entry['monotonic'] <= self.config['bell_window']]
            if kind == 'bell' and len(bells) >= self.config['bell_count']:
                raised = self.emit('repeated_bell', 'review', 'Repeated simulated doorbell presses while armed.', [
                    dict(id='bell', text=f"{len(bells)} simulated doorbell presses occurred within {self.config['bell_window']} seconds.", source='simulated_sensor', observed_at=record['observed_at'])])
            if kind == 'impact':
                raised = self.combined_impact_alert() or raised
        return self.reply(kind, {'accepted': True, 'input': record, 'event': raised})

    def observe(self, count, captured_monotonic, captured_at):
        if not self.armed or count <= 0 or not 0 <= self.clock()-captured_monotonic < .8:
            self.person_evidence = None
            self.occupancy_start = self.occupancy_last = None
            self.occupancy_fired = False
            return None
        self.person_evidence = dict(count=count, monotonic=captured_monotonic, observed_at=captured_at)
        combined = self.combined_impact_alert()
        if self.occupancy_last is None or captured_monotonic-self.occupancy_last >= .8:
            self.occupancy_start = captured_monotonic
            self.occupancy_fired = False
        self.occupancy_last = captured_monotonic
        if not self.occupancy_fired and captured_monotonic-self.occupancy_start >= self.config['occupancy_seconds']:
            self.occupancy_fired = True
            return self.emit('sustained_occupancy', 'review', 'Continuous person detections exceeded the configured duration while armed.', [
                dict(id='occupancy', text=f"Fresh person detections continued for at least {self.config['occupancy_seconds']} seconds.", source='laptop_webcam', observed_at=captured_at)])
        return combined
