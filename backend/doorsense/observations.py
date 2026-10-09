"""Conservative, frame-bound descriptions. No emotion, identity or alert rules.

Thresholds are prototype heuristics requiring held-out owner validation.
Two consecutive sampled frames support a description; absence never proves
an object/movement absent. No landmarks or face embeddings are persisted.
"""
import math


FACE_RULES = (
    ('jawOpen', None, 'The face model suggests an open mouth.'),
    ('eyeBlinkLeft', 'eyeBlinkRight', 'The face model suggests both eyelids are lowered.'),
    ('mouthSmileLeft', 'mouthSmileRight', 'The face model suggests raised mouth corners.'),
)


def face_descriptions(output):
    if len(output.face_landmarks) != 1 or len(output.face_blendshapes) != 1:
        return [], 'One clearly detected face is required; missing landmarks do not establish occlusion.'
    landmarks = output.face_landmarks[0]
    if len(landmarks) < 478 or not all(math.isfinite(p.x) and math.isfinite(p.y) and 0 <= p.x <= 1 and 0 <= p.y <= 1 for p in landmarks):
        return [], 'Face landmarks are incomplete or extend outside the frame; facial movement assessment is limited.'
    scores = {category.category_name: category.score for category in output.face_blendshapes[0]}
    def above(name):
        value = scores.get(name)
        return isinstance(value, (int, float)) and math.isfinite(value) and .65 <= value <= 1
    return [text for left, right, text in FACE_RULES if above(left) and (not right or above(right))], None


def pose_descriptions(output):
    if len(output.pose_landmarks) != 1 or len(output.pose_landmarks[0]) < 33:
        return [], 'One clearly detected body is required.'
    points = output.pose_landmarks[0]
    def visible(point):
        values = (point.x, point.y, point.visibility, point.presence)
        return all(isinstance(v, (int, float)) and math.isfinite(v) for v in values) and \
            0 <= point.x <= 1 and 0 <= point.y <= 1 and point.visibility >= .7 and point.presence >= .7
    if not all(visible(points[i]) for i in (11, 12, 15, 16)):
        return [], 'Both shoulders and wrists must be visible; posture assessment is limited.'
    raised = sum(points[w].y < points[s].y - .08 for s, w in ((11, 15), (12, 16)))
    return ([f'The pose model places {"both wrists" if raised == 2 else "one wrist"} above shoulder level.'] if raised else []), None


class Stabilizer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.previous = set()
        self.time = None
        self.sequence = None

    def update(self, descriptions, frame):
        current = set(descriptions)
        valid = self.time is not None and 0 < frame.captured_monotonic-self.time < .8 and frame.sequence != self.sequence
        stable = [text for text in descriptions if valid and text in self.previous]
        self.previous, self.time, self.sequence = current, frame.captured_monotonic, frame.sequence
        return stable


def observation_facts(observation):
    count = len(observation['people'])
    facts = [('person', f'The detector reported {count} {"person" if count == 1 else "people"} in this frame.')]
    recognition = observation.get('recognition')
    if recognition:
        facts.append(('visitor', f"Local LBPH appearance matching reports {recognition['category']}: {recognition['message']} This is not proof of identity or safety."))
    labels = sorted({item['label'] for item in observation.get('objects', [])})
    if labels:
        facts.append(('objects', f'The object model reported {", ".join(labels)} in this frame; ownership or carrying is not established.'))
    for feature in ('face', 'pose'):
        result = observation.get('features', {}).get(feature, {})
        if result.get('state') == 'available':
            facts.extend((f'{feature}{i}', text) for i, text in enumerate(result.get('descriptions', [])))
    return facts[:8]


def observation_key(observation):
    return (tuple(observation_facts(observation)), tuple(
        (name, item.get('state'), item.get('message')) for name, item in sorted(observation.get('features', {}).items())))
