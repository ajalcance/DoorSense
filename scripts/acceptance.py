#!/usr/bin/env python3
"""Prepare/review owner acceptance evidence. Never starts services or certifies isolation."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_CHECKS = (
    'disconnected_restart', 'external_requests_inspected', 'fresh_entry_exit',
    'face_quality', 'pose_quality', 'object_quality', 'combined_resources',
    'review_event', 'urgent_event', 'urgent_survives_camera_loss',
    'llm_failure_fallback', 'storage_restart', 'media_replay_delete',
    'feedback_persistence', 'external_display', 'reproduction',
)
CHECKS = (
    'disconnected_restart', 'external_requests_inspected', 'fresh_entry_exit',
    'face_quality', 'family_enrollment_match', 'unknown_after_deletion',
    'child_safety_mode', 'freshness_and_unavailable', 'automatic_analysis',
    'combined_resources', 'llm_failure_fallback', 'storage_restart',
    'reference_preview_delete', 'external_display', 'reproduction',
)


def template():
    return dict(schema='doorsense-owner-acceptance-v2', evidence_kind='owner_observations',
                tested_at=None, runtime_evidence_file=None,
                checks={name: dict(outcome='not_run', evidence='') for name in CHECKS})


def review(document, runtime):
    schema = document.get('schema')
    if schema not in ('doorsense-owner-acceptance-v1', 'doorsense-owner-acceptance-v2') or document.get('evidence_kind') != 'owner_observations':
        raise ValueError('Expected explicit owner observation report; injected checks are not live acceptance')
    legacy = schema == 'doorsense-owner-acceptance-v1'
    tested = datetime.fromisoformat(document['tested_at']) if document.get('tested_at') else None
    if tested and tested.tzinfo is None:
        raise ValueError('Acceptance time requires a timezone')
    checks = document.get('checks', {})
    results = {}
    for name in LEGACY_CHECKS if legacy else CHECKS:
        row = checks.get(name, {})
        outcome = row.get('outcome', 'not_run')
        if outcome not in ('passed', 'failed', 'blocked', 'not_run') or not isinstance(row.get('evidence', ''), str):
            raise ValueError('Invalid outcome/evidence for '+name)
        if outcome == 'passed' and (not tested or len(row.get('evidence', '').strip()) < 12):
            raise ValueError('Passed checks require time and concrete owner evidence: '+name)
        results[name] = dict(outcome=outcome, evidence=row.get('evidence', ''))
    blockers = [name for name, row in results.items() if row['outcome'] != 'passed']
    if not runtime:
        blockers.append('runtime_evidence_missing')
    else:
        captured = datetime.fromisoformat(runtime['generated_at'])
        if not captured.tzinfo or (tested and abs((captured-tested).total_seconds()) > 3600):
            blockers.append('runtime_evidence_not_from_acceptance_window')
        if not runtime.get('camera', {}).get('assessed_frames', 0):
            blockers.append('fresh_model_inference_missing')
        if not runtime.get('genuine_qwen_selection_observed'):
            blockers.append('accepted_local_qwen_response_missing')
        for name in ('face', 'pose') if legacy else ('face',):
            feature = runtime.get('scene_features', {}).get(name, {})
            if not feature.get('assessed_frames') or not feature.get('model_sha256'):
                blockers.append(name+'_runtime_evidence_missing')
    return dict(schema='doorsense-acceptance-review-v2', generated_at=datetime.now(timezone.utc).isoformat(),
                demonstration_scope='historical sensor/pose workflow' if legacy else 'current face-only demo',
                scope='Owner-reported live acceptance cross-checked against runtime metadata; not an independent network/security certification.',
                checks=results, blockers=blockers, acceptance_ready=not blockers,
                publication='Not performed; demo, disclosures, organiser eligibility and submission are separate.')


def destination(path):
    path = path.resolve()
    if not path.is_relative_to(ROOT / '.runtime'):
        raise ValueError('Acceptance output must remain in ignored DoorSense .runtime')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('init', 'review'))
    parser.add_argument('--observations', type=Path, default=ROOT / '.runtime/acceptance-observations.json')
    parser.add_argument('--runtime', type=Path)
    args = parser.parse_args()
    if args.action == 'init':
        path = destination(args.observations)
        path.parent.mkdir(exist_ok=True)
        with path.open('x') as output:
            json.dump(template(), output, indent=2)
            output.write('\n')
        print('Created '+str(path)+'. All checkpoints NOT RUN; fill only actual owner outcomes.')
        return 0
    document = json.loads(args.observations.read_text())
    runtime = json.loads(args.runtime.read_text()) if args.runtime else None
    report = review(document, runtime)
    print(json.dumps(report, indent=2))
    path = destination(ROOT / '.runtime/acceptance-review.json')
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+'\n')
    return 0 if report['acceptance_ready'] else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit('Acceptance review stopped: '+str(error))
