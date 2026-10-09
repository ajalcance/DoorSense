"""Small local LBPH enrollment/matching demo; no reward learning or safety inference."""
import base64
import threading
import time

import cv2
import numpy as np

THRESHOLD = 65.0  # Prototype rejection distance, not a calibrated probability.
METHOD = 'OpenCV LBPH · locally enrolled appearance'


def face_crop(pixels, observation):
    feature = observation.get('features', {}).get('face', {})
    box = feature.get('box')
    if len(observation.get('people', [])) != 1 or feature.get('state') != 'available' or not box:
        raise ValueError('One clear face is required. Enable face analysis and face the camera.')
    height, width = pixels.shape[:2]
    values = np.asarray(box, dtype=float)
    if values.shape != (4,) or not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        raise ValueError('Face bounds are unavailable.')
    x0, y0, x1, y1 = values
    left, top = int(x0*width), int(y0*height)
    right, bottom = min(width, int(np.ceil(x1*width))), min(height, int(np.ceil(y1*height)))
    if right-left < 64 or bottom-top < 64:
        raise ValueError('Move closer: a face crop of at least 64 × 64 pixels is required.')
    gray = cv2.cvtColor(pixels[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)


def encode_sample(pixels, observation):
    crop = face_crop(pixels, observation)
    ok, image = cv2.imencode('.png', crop)
    if not ok:
        raise ValueError('Face example could not be encoded.')
    return base64.b64encode(image).decode('ascii')


class FamilyMatcher:
    def __init__(self):
        self.lock = threading.Lock()
        self.sample = None
        self.model = None
        self.training_ms = None
        self.generation = 0

    def clear(self):
        with self.lock:
            self.generation += 1
            self.sample = self.model = self.training_ms = None

    def assess(self, pixels, observation, reference, generation=None):
        started = time.perf_counter()
        result = dict(category='Unknown', state='limited', source='local_face_match', method=METHOD,
                      distance=None, threshold=THRESHOLD, trained_examples=0,
                      training_ms=None, inference_ms=None, sequence=observation['sequence'],
                      captured_at=observation['captured_at'], message='No family example enrolled.')
        stored = reference.get('frame', {}) if reference else {}
        sample = stored.get('face_sample')
        with self.lock:
            if generation is not None and generation != self.generation:
                result['message'] = 'Enrollment changed before this comparison completed.'
                return result
            if sample != self.sample:
                self.sample, self.model = sample, None
                self.training_ms = None
            if not sample:
                result['state'] = 'no_reference'
                return result
            try:
                crop = face_crop(pixels, observation)
                if self.model is None:
                    encoded = base64.b64decode(sample, validate=True)
                    if len(encoded) > 128*1024:
                        raise ValueError('Invalid face example size.')
                    enrolled = cv2.imdecode(np.frombuffer(encoded, np.uint8), cv2.IMREAD_GRAYSCALE)
                    if enrolled is None or enrolled.shape != (128, 128):
                        raise ValueError('Invalid enrolled face example.')
                    model = cv2.face.LBPHFaceRecognizer_create()
                    training_started = time.perf_counter()
                    model.train([enrolled], np.array([1], dtype=np.int32))
                    self.training_ms = round((time.perf_counter()-training_started)*1000, 2)
                    self.model = model
                inference_started = time.perf_counter()
                _, distance = self.model.predict(crop)
                result['inference_ms'] = round((time.perf_counter()-inference_started)*1000, 2)
                if not np.isfinite(distance):
                    raise ValueError('Face match distance unavailable.')
                distance = round(float(distance), 2)
                matched = distance <= THRESHOLD
                result.update(category='Family member' if matched else 'Unknown', state='matched' if matched else 'unmatched',
                              distance=round(float(distance), 2),
                              message='Appearance matches the enrolled example.' if matched else 'Appearance does not match the enrolled example.')
            except (ValueError, cv2.error) as error:
                result['message'] = str(error)
            result.update(trained_examples=1 if self.model is not None else 0,
                          training_ms=self.training_ms, processing_ms=round((time.perf_counter()-started)*1000, 2))
            return result
