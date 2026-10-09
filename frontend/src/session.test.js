import test from 'node:test';
import assert from 'node:assert/strict';
import {ConsoleSession, freshFrame, simulationState} from './session.js';
import {questions} from './contracts.js';
import {visitAnalysis} from './analysis.js';

const packet = (changes = {}) => ({
  camera: 'monitoring', revision: 1, release_completed: true, token: 'fixture-token', diagnostics: {},
  frame: {image: 'fixture', width: 640, height: 480, inference_ms: 1, age_seconds: 0.1,
    captured_at: '2026-10-09T14:00:00Z', people: [{box: [0, 0, 10, 10]}]}, ...changes,
});
const response = (body, ok = true) => ({ok, json: async () => body});
const deferred = () => {let resolve; const promise = new Promise(done => {resolve = done;}); return {promise, resolve};};

const simulation = () => ({contact: {kind:'contact_closed'}, replies: [],
  progress: {impact: {count:1, required:3, remaining_seconds:1}, bell: {count:0, required:3, remaining_seconds:0}},
  occupancy: {elapsed_seconds:0, required_seconds:30, remaining_seconds:30, fresh:false}});
test('local face match changes visit; deletion restores unknown and urgent still wins', () => {
  const recognition={category:'Family member',state:'matched',sequence:7,captured_at:'now',distance:12.5,threshold:65,message:'Matched.'};
  const frame={sequence:7,captured_at:'now',people:[{}],recognition};
  const state=simulation(); state.camera_evidence={fresh:true};
  const model={frame,status:{armed:true},simulation:state};
  const family=visitAnalysis(model);
  assert.equal(family.headline,'Family member · expected visit');
  assert.equal(family.level,'monitoring');
  assert.match(family.match,/12.50/);
  const unknown=visitAnalysis({...model,frame:{...frame,recognition:{...recognition,category:'Unknown',state:'no_reference',distance:null,message:'No family example enrolled.'}}});
  assert.equal(unknown.level,'advisory');
  assert.match(unknown.visitor,/Unknown/);
  assert.equal(visitAnalysis({...model,status:{armed:true,event:{severity:'urgent',facts:[],rule_reason:'Repeated impacts.',rule_id:'person_closed_door_impacts'}}}).level,'urgent');
  assert.equal(visitAnalysis({...model,frame:{...frame,sequence:8}}).level,'advisory');
});
test('visit interpretation distinguishes confirmed family snapshot from current unknown visitor', () => {
  const frame={sequence:1,captured_at:'2026-10-10T00:00:00Z',people:[{}]};
  const status={armed:true,confirmation:{sequence:1,captured_at:frame.captured_at,label:'Family member'}};
  const confirmed=visitAnalysis({frame,status,simulation:simulation()});
  assert.equal(confirmed.level,'monitoring');
  assert.match(confirmed.interpretation,/parent marked this snapshot/);
  const later=visitAnalysis({frame:{...frame,sequence:2},status,simulation:simulation()});
  assert.equal(later.level,'advisory');
  assert(later.missing.some(text=>text.includes('later frames')));
  const unknown=visitAnalysis({frame,status:{...status,confirmation:{...status.confirmation,label:'Unknown'}},simulation:simulation()});
  assert.equal(unknown.level,'advisory');
  assert.match(unknown.probability,/Not estimated/);
});
test('face-only demo works without arming, switches on deletion and waits on face loss', () => {
  const recognition={category:'Family member',state:'matched',sequence:1,captured_at:'now',distance:14,threshold:65,message:'Matches example.'};
  const frame={sequence:1,captured_at:'now',people:[{}],facts:[],features:{face:{state:'available'}},recognition};
  const status={demo_mode:'face_enrollment',armed:true};
  const family=visitAnalysis({frame,status});
  assert.equal(family.level,'monitoring');
  assert.match(family.headline,/familiar visitor/);
  assert.match(family.nextStep,/Ask your parent/);
  const unknown=visitAnalysis({frame:{...frame,recognition:{...recognition,state:'no_reference',category:'Unknown',distance:null,message:'No example.'}},status});
  assert.equal(unknown.level,'advisory');
  assert.match(unknown.nextStep,/Keep the door closed/);
  assert.match(unknown.interpretation,/does not mean dangerous/);
  assert.equal(visitAnalysis({status}).level,'limited');
  assert.equal(visitAnalysis({frame:{...frame,people:[],features:{face:{state:'limited'}},recognition:{...recognition,state:'limited',category:'Unknown'}},status}).level,'limited');
  const off=visitAnalysis({frame,status:{...status,armed:false}});
  assert.equal(off.visitor,'Family member');
  assert.equal(off.guidanceEnabled,false);
  assert.match(off.nextStep,/mode is off/);
  const lost=visitAnalysis({frame:{...frame,sequence:2},status});
  assert.equal(lost.level,'limited');
  assert.equal(lost.visitor,'Unknown');
});
test('automatic findings are throttled and update when the visitor changes', async () => {
  let now=0;
  let calls=0;
  const session=new ConsoleSession({now:()=>now,fetchImpl:async path=>{assert.equal(path,'/api/explain');calls++;return response({source:'qwen_evidence_selection',text:'Observed person.'});}});
  session.acceptStatus(packet({demo_mode:'face_enrollment',armed:false}),now);
  await session.refreshAutomaticAnalysis();
  await session.refreshAutomaticAnalysis();
  assert.equal(calls,1);
  assert.equal(session.state.question,'What was observed?');
  now=6000;
  session.acceptStatus(packet({revision:2,demo_mode:'face_enrollment',frame:{...packet().frame,recognition:{state:'matched',category:'Family member'}}}),now);
  await session.refreshAutomaticAnalysis();
  assert.equal(calls,2);
  session.acceptStatus(packet({demo_mode:'face_enrollment',frame:null,camera:'paused'}),now);
  await session.refreshAutomaticAnalysis();
  assert.equal(calls,2);
});
test('family confirmation cannot lower an urgent event; historical identity stays unspecified', () => {
  const event={severity:'urgent',rule_id:'person_closed_door_impacts',rule_reason:'Combined evidence.',facts:[{text:'Recorded person.',source:'laptop_webcam'}]};
  const status={armed:false,event,confirmation:{label:'Family member'}};
  assert.equal(visitAnalysis({status,simulation:simulation()}).level,'urgent');
  const historical=visitAnalysis({status,selected:event,selectedEvent:'old',simulation:simulation()});
  assert.equal(historical.visitor,'Not established by this saved event');
  assert.match(historical.nextStep,/past event/);
});
test('missing camera corroboration never becomes a probability or urgent conclusion', () => {
  const state=simulation(); state.progress.impact.count=3;
  const assessment=visitAnalysis({status:{armed:true},frame:{people:[{}]},simulation:state});
  assert.equal(assessment.level,'limited');
  assert.match(assessment.headline,/corroboration missing/);
  assert(!/\d+%/.test(assessment.probability));
  assert.equal(visitAnalysis({status:{armed:false},simulation:state}).level,'off');
  assert.equal(visitAnalysis({}).level,'limited');
});
test('deleting a family reference closes its preview without deleting history', async () => {
  const history={events:[savedEvent()],total:1,offset:0};
  const session=new ConsoleSession({fetchImpl:async path=>response(path.startsWith('/api/events?') ? history : packet({revision:2,family_reference:null}))});
  session.acceptStatus(packet({family_reference:{category:'Family member'}}));
  session.patch({media:{id:'family-reference',kind:'reference',frames:[]},history});
  await session.deleteFamilyReference();
  assert.equal(session.state.media,null);
  assert.equal(session.state.history.total,1);
  assert.equal(session.state.status.family_reference,null);
});
test('simulation countdown uses server state and transit age, without inventing expired counts', () => {
  const status = packet({simulation: simulation()});
  assert.equal(simulationState(status, 0, 400).progress.impact.remaining_seconds, .6);
  assert.equal(simulationState(status, 0, 1100).progress.impact.count, null);
  assert.equal(simulationState(status, 0, 1600), null);
  assert.equal(simulationState(packet(), 0, 0), null);
  const session = new ConsoleSession({now:()=>0});
  session.acceptStatus(status);
  assert.equal(session.state.sensorLog.length, 0);
  assert.equal(simulationState(session.state.status, 0, 0).contact.kind, 'contact_closed');
});
test('sensor reply updates authoritative progress immediately; no optimistic accepted input', async () => {
  const pending = deferred();
  const session = new ConsoleSession({now:()=>0, fetchImpl:()=>pending.promise});
  session.acceptStatus(packet({event_revision:0, simulation:simulation()}));
  const request = session.mutate('/api/sensors', {kind:'impact'});
  assert.equal(session.state.sensorResult, null);
  const updated = simulation(); updated.progress.impact.count = 2;
  pending.resolve(response({accepted:true,input:{kind:'impact'},status:packet({event_revision:1,simulation:updated})}));
  await request;
  assert.equal(session.state.status.simulation.progress.impact.count, 2);
  session.acceptStatus(packet({event_revision:0,simulation:simulation()}));
  assert.equal(session.state.status.simulation.progress.impact.count, 2);
});
test('late sensor replies from a restarted service are discarded', async () => {
  const pending = deferred();
  const session = new ConsoleSession({now:()=>0,fetchImpl:()=>pending.promise});
  session.acceptStatus(packet());
  const request = session.mutate('/api/sensors',{kind:'impact'});
  session.acceptStatus(packet({token:'new-service'}));
  pending.resolve(response({accepted:true,input:{kind:'impact'},status:packet({simulation:simulation()})}));
  await request;
  assert.equal(session.state.sensorResult,null);
  assert.equal(session.state.status.token,'new-service');
});
test('newer input reply wins over an intervening poll and clears changed Qwen evidence', async () => {
  let now=10;
  const pending=deferred();
  const initial=simulation(); initial.revision=0;
  const session=new ConsoleSession({now:()=>now,fetchImpl:()=>pending.promise});
  session.acceptStatus(packet({simulation:initial,event_revision:0}));
  session.patch({answer:{source:'template_fallback',text:'Current evidence'}});
  const request=session.mutate('/api/sensors',{kind:'impact'});
  now=20;
  session.acceptStatus(packet({simulation:initial,event_revision:0}));
  const changed=simulation(); changed.revision=1; changed.progress.impact.count=2;
  pending.resolve(response({accepted:true,input:{kind:'impact'},status:packet({simulation:changed,event_revision:0})}));
  await request;
  assert.equal(session.state.status.simulation.progress.impact.count,2);
  assert.equal(session.state.answer,null);
  now=30;
  session.acceptStatus(packet({simulation:initial,event_revision:0}));
  assert.equal(session.state.status.simulation.revision,1);
});
test('reset clears temporary UI and stale Qwen while keeping saved history', async () => {
  const pending = deferred();
  const history = {events:[savedEvent()], total:1, offset:0};
  const session = new ConsoleSession({now:()=>0,fetchImpl:async path => {
    if(path === '/api/explain') return pending.promise;
    if(path === '/api/session/reset') return response(packet({revision:2,armed:false,camera:'paused',frame:null,simulation:simulation()}));
    return response(history);
  }});
  session.acceptStatus(packet()); session.patch({history});
  const asking = session.ask();
  assert.equal(await session.resetSession(),true);
  pending.resolve(response({source:'qwen_evidence_selection',text:'old answer'}));
  await asking;
  assert.equal(session.state.answer,null);
  assert.equal(session.state.status.camera,'paused');
  assert.equal(session.state.history.total,1);
  assert.equal(session.state.sensorResult,null);
});

test('unsupported questions cannot enter the live session', () => {
  const session = new ConsoleSession();
  session.setQuestion('Who is this?');
  assert.equal(session.state.question, questions[0]);
});
test('overlapping capture actions do not queue duplicate controls', async () => {
  const pending = deferred(); let calls = 0;
  const session = new ConsoleSession({fetchImpl: () => {calls++; return pending.promise;}});
  session.acceptStatus(packet());
  const stopping = session.control('stop');
  await session.control('stop'); await session.control('start');
  assert.equal(calls, 1);
  pending.resolve(response(packet({camera: 'paused', frame: null})));
  await stopping;
});
test('network transit time is included in frame expiry', () => {
  assert(freshFrame(packet(), 0, 500));
  assert.equal(freshFrame(packet(), 0, 900), null);
  assert.equal(freshFrame(packet({camera: 'paused'}), 0, 100), null);
});
test('malformed/stale frame does not become displayable', () => {
  assert.equal(freshFrame(packet({frame: {...packet().frame, people: null}}), 0, 100), null);
  assert.equal(freshFrame(packet({frame: {...packet().frame, age_seconds: -1}}), 0, 100), null);
  assert.equal(freshFrame(packet({frame: {...packet().frame, inference_ms: 'invented'}}), 0, 100), null);
});
test('camera action error persists across normal polling', async () => {
  const session = new ConsoleSession({fetchImpl: async () => response({detail: 'Camera operation already in progress'}, false)});
  session.acceptStatus(packet({camera: 'paused', frame: null}));
  await session.control('start');
  session.acceptStatus(packet({camera: 'paused', frame: null}));
  assert.match(session.state.actionError, /already in progress/);
  assert.equal(session.state.connectionError, '');
});
test('timed-out control releases UI busy state and keeps truthful error', async () => {
  const session = new ConsoleSession({controlDeadlineMs: 5, fetchImpl: (_, options) => new Promise((resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(options.signal.reason), {once: true});
  })});
  session.acceptStatus(packet({camera: 'paused', frame: null}));
  const control = session.control('start');
  await new Promise(resolve => setTimeout(resolve, 20));
  await control;
  assert.equal(session.state.busy, false);
  assert.match(session.state.actionError, /timed out/);
  assert.match(session.state.actionError, /server work may still be running/);
});
test('no live explanation is sent when fresh assessment is missing', async () => {
  let calls = 0;
  const session = new ConsoleSession({now: () => 1000, fetchImpl: () => {calls++;}});
  session.acceptStatus(packet(), 0);
  await session.ask();
  assert.equal(calls, 0);
});
test('superseded request cannot attach to a changed camera revision', async () => {
  const pending = deferred();
  const session = new ConsoleSession({now: () => 0, fetchImpl: () => pending.promise});
  session.acceptStatus(packet(), 0);
  const asking = session.ask();
  session.acceptStatus(packet({revision: 2}), 0);
  pending.resolve(response({source: 'qwen_evidence_selection', text: 'Old snapshot'}));
  await asking;
  assert.equal(session.state.answer, null);
});
test('frame expiring during generation discards the late result', async () => {
  let now = 0; const pending = deferred();
  const session = new ConsoleSession({now: () => now, fetchImpl: () => pending.promise});
  session.acceptStatus(packet(), 0);
  const asking = session.ask();
  now = 1000;
  pending.resolve(response({source: 'qwen_evidence_selection', text: 'Old snapshot'}));
  await asking;
  assert.equal(session.state.answer, null);
  assert.match(session.state.explanationNotice, /evidence changed or expired/);
  session.acceptStatus(packet({revision: 3}), now);
  assert.match(session.state.explanationNotice, /evidence changed or expired/);
});
test('service loss clears imagery and supersedes pending explanation', async () => {
  const pending = deferred();
  const session = new ConsoleSession({now: () => 0, fetchImpl: () => pending.promise});
  session.acceptStatus(packet(), 0);
  const asking = session.ask();
  session.pollFailed();
  pending.resolve(response({source: 'template_fallback', text: 'Old snapshot'}));
  await asking;
  assert.equal(session.state.status, null);
  assert.equal(session.state.answer, null);
  assert.match(session.state.connectionError, /unknown/);
});
test('duplicate Ask while pending sends one request only', async () => {
  const pending = deferred(); let calls = 0;
  const session = new ConsoleSession({now: () => 0, fetchImpl: () => {calls++; return pending.promise;}});
  session.acceptStatus(packet(), 0);
  const first = session.ask();
  await session.ask();
  assert.equal(calls, 1);
  pending.resolve(response({source: 'template_fallback', text: 'Fixture transport response'}));
  await first;
  assert.equal(session.state.answer.source, 'template_fallback');
});
test('displayed snapshot answer expires at 60 seconds', () => {
  let wall = Date.parse(packet().frame.captured_at);
  const session = new ConsoleSession({now: () => 0, wallNow: () => wall});
  session.acceptStatus(packet(), 0);
  session.patch({answer: {source: 'qwen_evidence_selection', observation_captured_at: packet().frame.captured_at}});
  wall += 60001;
  session.checkFreshness();
  assert.equal(session.state.answer, null);
});
test('poll started before Stop cannot restore a stopped camera image', () => {
  const session = new ConsoleSession({now: () => 200});
  session.acceptStatus(packet({camera: 'paused', frame: null, revision: 2}), 200);
  session.acceptStatus(packet({revision: 1}), 100);
  assert.equal(session.state.status.camera, 'paused');
  assert.equal(session.state.status.frame, null);
  session.acceptStatus(packet({revision: 1}), 300);
  assert.equal(session.state.status.camera, 'paused');
});
test('a restarted service token allows its new revision without stale packet regression', () => {
  const session = new ConsoleSession({now: () => 200});
  session.acceptStatus(packet({revision: 12}), 100);
  session.acceptStatus(packet({token: 'restarted-service', revision: 0, camera: 'paused', frame: null}), 200);
  session.acceptStatus(packet({revision: 12}), 100);
  assert.equal(session.state.status.token, 'restarted-service');
  assert.equal(session.state.status.revision, 0);
});

const savedEvent = (changes = {}) => ({id: 'a'.repeat(32), revision: 1, severity: 'urgent',
  created_at: '2026-10-09T14:00:00Z', facts: [{text: 'Simulated impact.', source: 'simulated_sensor'}], media: [], ...changes});
test('sensor event can be explained without a camera; camera loss does not supersede it', async () => {
  const done = deferred();
  const session = new ConsoleSession({fetchImpl: () => done.promise});
  session.acceptStatus(packet({event: savedEvent(), event_revision: 1}));
  const request = session.ask();
  session.acceptStatus(packet({camera: 'unavailable', frame: null, event: savedEvent(), event_revision: 1}));
  done.resolve(response({source: 'template_fallback', text: 'Simulated impact.'}));
  await request;
  assert.equal(session.state.answer.source, 'template_fallback');
});
test('new event supersedes a live-event answer', async () => {
  const done = deferred();
  const session = new ConsoleSession({fetchImpl: () => done.promise});
  session.acceptStatus(packet({event: savedEvent(), event_revision: 1}));
  const request = session.ask();
  session.acceptStatus(packet({event: savedEvent({id: 'b'.repeat(32)}), event_revision: 2}));
  done.resolve(response({source: 'template_fallback'}));
  await request;
  assert.equal(session.state.answer, null);
});
test('history selection sends the exact stored event reference; old live polls cannot regress an alert', async () => {
  let payload;
  const session = new ConsoleSession({fetchImpl: async (path, options) => {
    payload = JSON.parse(options.body); return response({source: 'application_unavailable'});
  }});
  const event = savedEvent();
  session.acceptStatus(packet({event_revision: 2, event}));
  session.patch({history: {events: [event], total: 1, offset: 0}});
  session.selectRecord(event.id);
  await session.ask();
  assert.equal(payload.event_id, event.id);
  session.acceptStatus(packet({event_revision: 1, event: null}));
  assert.equal(session.state.status.event.id, event.id);
});
test('acknowledgement posts the exact stored event action', async () => {
  const paths = [];
  const event = savedEvent();
  const session = new ConsoleSession({fetchImpl: async path => {
    paths.push(path); return response(path.startsWith('/api/events?') ? {events: [event], total: 1, offset: 0} : event);
  }});
  session.acceptStatus(packet({event, event_revision: 1}));
  await session.acknowledge();
  assert.equal(paths[0], `/api/events/${event.id}/acknowledge`);
});
test('replay and deletion use actual media references and clear deleted media', async () => {
  const paths = [];
  const session = new ConsoleSession({fetchImpl: async path => {
    paths.push(path);
    if (path.endsWith('/delete')) return response({deleted: true});
    if (path.startsWith('/api/events?')) return response({events: [], total: 0, offset: 0});
    return response({id: 'media', frames: [{image: 'synthetic'}]});
  }});
  session.acceptStatus(packet());
  await session.replay('media');
  assert.equal(session.state.media.id, 'media');
  await session.deleteMedia('media');
  assert.equal(session.state.media, null);
  assert.deepEqual(paths, ['/api/media/media', '/api/media/media/delete', '/api/events?offset=0']);
});
test('history fetch started for an old service cannot replace the new service history', async () => {
  const done = deferred();
  const session = new ConsoleSession({fetchImpl: () => done.promise});
  session.acceptStatus(packet());
  const request = session.loadHistory();
  session.acceptStatus(packet({token: 'new-service'}));
  done.resolve(response({events: [savedEvent()], total: 1, offset: 0}));
  await request;
  assert.equal(session.state.history.total, 0);
});
test('changing history page clears an event reference absent from that page', async () => {
  const event = savedEvent();
  const session = new ConsoleSession({fetchImpl: async () => response({events: [], offset: 25, total: 26})});
  session.acceptStatus(packet()); session.patch({history: {events: [event], offset: 0}});
  session.selectRecord(event.id); await session.loadHistory(25);
  assert.equal(session.state.selectedEvent, null);
});

test('service-backed session contains no presentation mode or canned response source', () => {
  const session = new ConsoleSession();
  assert.equal('mode' in session.state, false);
  assert.equal('scenario' in session.state, false);
  assert.equal('source' in session.state, false);
});
test('late replay cannot reopen media after navigation or service restart', async () => {
  for (const change of ['navigate', 'restart']) {
    const pending = deferred();
    const session = new ConsoleSession({fetchImpl: () => pending.promise});
    session.acceptStatus(packet());
    const replay = session.replay('media');
    if (change === 'navigate') session.selectRecord(null);
    else session.acceptStatus(packet({token:'new-service'}));
    pending.resolve(response({id:'media',frames:[]}));
    await replay;
    assert.equal(session.state.media,null);
  }
});
test('service unavailable session never posts camera controls or explanations', async () => {
  let calls=0;
  const session=new ConsoleSession({fetchImpl:()=>{calls++;}});
  await session.control('start'); await session.ask();
  assert.equal(calls,0);
});
test('service restart invalidates a camera answer even when revisions and counts match', () => {
  const session = new ConsoleSession();
  session.acceptStatus(packet());
  session.patch({answer:{source:'template_fallback',text:'old service'}});
  session.acceptStatus(packet({token:'restarted-service'}));
  assert.equal(session.state.answer,null);
});
test('scene description changes supersede a pending answer without count change', async () => {
  const pending = deferred();
  const session = new ConsoleSession({fetchImpl:()=>pending.promise});
  const first = packet();
  first.frame.sequence = 1;
  first.frame.features = {face:{state:'available',sequence:1,captured_at:first.frame.captured_at,descriptions:['mouth open']}};
  session.acceptStatus(first);
  const asking = session.ask();
  const second = structuredClone(first);
  second.frame.features.face.descriptions = [];
  session.acceptStatus(second);
  pending.resolve(response({source:'qwen_evidence_selection',text:'old movement'}));
  await asking;
  assert.equal(session.state.answer,null);
});
test('scene outputs from a different frame cannot be displayed', () => {
  const data = packet();
  data.frame.sequence = 2;
  data.frame.features = {face:{sequence:1,captured_at:data.frame.captured_at,descriptions:[]}};
  assert.equal(freshFrame(data,0,0),null);
});
