import {questions} from './contracts.js';

export function simulationState(status, requestStarted, now) {
  if (!status?.simulation || now < requestStarted || now-requestStarted > 1500) return null;
  const elapsed = (now-requestStarted)/1000;
  const simulation = status.simulation;
  const progress = Object.fromEntries(Object.entries(simulation.progress).map(([kind, value]) => {
    const remaining = Math.max(0, value.remaining_seconds-elapsed);
    return [kind, {...value, remaining_seconds: remaining,
      // The backend supplies counts; once a deadline passes, wait for a fresh
      // packet rather than guessing which other inputs remain in the window.
      count: value.count > 0 && remaining === 0 ? null : value.count,
      open_transition_remaining_seconds: Math.max(0, (value.open_transition_remaining_seconds || 0)-elapsed)}];
  }));
  const occupancyFresh = simulation.occupancy.fresh && simulation.occupancy.fresh_remaining_seconds > elapsed;
  const cameraFresh = !!simulation.camera_evidence?.fresh && simulation.camera_evidence.fresh_remaining_seconds > elapsed;
  return {...simulation, progress, camera_evidence: {...simulation.camera_evidence, fresh:cameraFresh}, occupancy: {...simulation.occupancy, fresh: occupancyFresh,
    elapsed_seconds: occupancyFresh ? simulation.occupancy.elapsed_seconds : 0,
    remaining_seconds: occupancyFresh ? simulation.occupancy.remaining_seconds : simulation.occupancy.required_seconds}};
}

export function freshFrame(status, requestStarted, now) {
  const frame = status?.frame;
  return status?.camera === 'monitoring' && frame &&
    Array.isArray(frame.people) && frame.people.every(person => Array.isArray(person.box) && person.box.length === 4 && person.box.every(Number.isFinite)) &&
    (!frame.objects || (Array.isArray(frame.objects) && frame.objects.every(item => ['backpack', 'handbag', 'suitcase'].includes(item.label) && Array.isArray(item.box) && item.box.length === 4 && item.box.every(Number.isFinite)))) &&
    (!frame.features || Object.values(frame.features).every(item => item && item.sequence === frame.sequence && item.captured_at === frame.captured_at && Array.isArray(item.descriptions) && item.descriptions.every(text => typeof text === 'string'))) &&
    (!frame.facts || (Array.isArray(frame.facts) && frame.facts.length <= 8 && frame.facts.every(item => typeof item.text === 'string' && item.observed_at === frame.captured_at))) &&
    Number.isFinite(frame.width) && frame.width > 0 && Number.isFinite(frame.height) && frame.height > 0 &&
    Number.isFinite(frame.inference_ms) && typeof frame.image === 'string' && Number.isFinite(Date.parse(frame.captured_at)) &&
    Number.isFinite(frame.age_seconds) && frame.age_seconds >= 0 &&
    now >= requestStarted && frame.age_seconds + (now - requestStarted) / 1000 < 0.8 ? frame : null;
}

// Pure, injectable application session: the same workflow used by React and tests.
// It never opens a camera, starts a service or calls Qwen directly.
export class ConsoleSession {
  constructor({fetchImpl = (...args) => fetch(...args), now = () => performance.now(), wallNow = () => Date.now(), controlDeadlineMs = 15000, explanationDeadlineMs = 60000} = {}) {
    this.fetch = fetchImpl;
    this.now = now;
    this.wallNow = wallNow;
    this.listeners = new Set();
    this.generation = 0;
    this.mediaGeneration = 0;
    this.requestStarted = 0;
    this.observationKey = null;
    this.controlDeadlineMs = controlDeadlineMs;
    this.explanationDeadlineMs = explanationDeadlineMs;
    this.state = {
      status: null,
      actionError: '', connectionError: '', busy: false, asking: false, answer: null, explanationNotice: '',
      question: questions[0],
      history: {events: [], total: 0, offset: 0, next_offset: null}, selectedEvent: null, historyError: '', media: null, sensorResult: null, sensorLog: [],
    };
  }
  subscribe = listener => { this.listeners.add(listener); return () => this.listeners.delete(listener); };
  getSnapshot = () => this.state;
  patch(changes) {
    this.state = {...this.state, ...changes};
    for (const listener of this.listeners) listener();
  }
  invalidate() {
    this.generation++;
    this.patch({answer: null, asking: false, explanationNotice: ''});
  }
  acceptStatus(status, requestStarted = this.now()) {
    if (!status || typeof status.token !== 'string' || typeof status.release_completed !== 'boolean' || !Number.isInteger(status.revision) || !status.diagnostics) {
      throw Error('Invalid local service status');
    }
    // A poll begun before Stop must never restore that earlier monitoring packet.
    const previous = this.state.status;
    const newerState = previous?.token === status.token && (status.revision > previous.revision ||
      status.event_revision > previous.event_revision || status.simulation?.revision > previous.simulation?.revision);
    if ((requestStarted < this.requestStarted && !newerState) ||
        (this.state.status?.token === status.token &&
         (status.revision < this.state.status.revision || status.event_revision < this.state.status.event_revision ||
          status.simulation?.revision < this.state.status.simulation?.revision))) return;
    const rulesChanged = this.state.status && (this.state.status.token !== status.token || this.state.status.armed !== status.armed);
    this.requestStarted = requestStarted;
    if (rulesChanged) this.patch({sensorLog: [], sensorResult: null});
    this.patch({status, connectionError: ''});
    this.checkFreshness();
  }
  pollFailed() {
    this.patch({status: null, connectionError: 'Local service unavailable. Camera state is unknown; check the owner Terminal.'});
    this.checkFreshness();
  }
  checkFreshness() {
    const {status, answer} = this.state;
    const frame = freshFrame(status, this.requestStarted, this.now());
    const event = this.selectedRecord();
    const confirmation = frame && status?.confirmation;
    const simulation = simulationState(status, this.requestStarted, this.now());
    const sensorKey = JSON.stringify([simulation?.contact?.id, simulation?.contact?.kind,
      simulation?.progress?.bell?.count, simulation?.progress?.impact?.count]);
    const key = !status ? 'service-unavailable' : event ?
      `event:${status?.token}:${event.id}:${event.revision}:${this.state.selectedEvent ? 'history' : status?.event_revision}` :
      confirmation ? `confirmation:${status.token}:${confirmation.id}:${sensorKey}` : `${status?.token}:${status?.revision}:${status?.event_revision}:${sensorKey}:${frame?.people.length ?? 'unavailable'}:${JSON.stringify(Object.entries(frame?.features || {}).map(([name, item]) => [name, item.state, item.descriptions]))}:${JSON.stringify(frame?.objects?.map(item => item.label).sort() || [])}`;
    const expired = answer?.observation_captured_at && this.wallNow() - Date.parse(answer.observation_captured_at) > 60000;
    if (key !== this.observationKey || expired) {
      const hadResponse = this.state.asking || !!answer;
      const previousNotice = this.state.explanationNotice;
      this.observationKey = key;
      this.invalidate();
      if (hadResponse) this.patch({explanationNotice: 'The evidence changed or expired. The previous request or result was cleared. Confirm a fresh snapshot or select a saved event, then try again.'});
      else if (previousNotice) this.patch({explanationNotice: previousNotice});
    }
  }
  async post(path, body = {}, timeoutMs = this.controlDeadlineMs) {
    const response = await this.fetch(path, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-DoorSense-Token': this.state.status?.token || ''},
      body: JSON.stringify(body), signal: AbortSignal.timeout(timeoutMs),
    });
    const data = await response.json();
    if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : 'Request unavailable');
    return data;
  }
  failureMessage(failure) {
    return ['TimeoutError', 'AbortError'].includes(failure.name) ?
      'The request timed out. Check camera state before retrying; server work may still be running.' : failure.message;
  }
  async control(action) {
    if (!this.state.status || this.state.busy || !['start', 'stop'].includes(action)) return;
    this.invalidate();
    this.patch({busy: true, actionError: ''});
    const began = this.now();
    try { this.acceptStatus(await this.post(`/api/camera/${action}`), began); }
    catch (failure) { this.patch({actionError: this.failureMessage(failure)}); }
    finally { this.patch({busy: false}); }
  }
  acknowledge() {
    const event = this.selectedRecord();
    if (event) return this.mutate(`/api/events/${event.id}/acknowledge`);
  }
  setQuestion(value) {
    if (!questions.includes(value) || value === this.state.question) return;
    this.invalidate();
    this.patch({question: value});
  }
  selectedRecord() {
    return this.state.selectedEvent ? this.state.history.events.find(event => event.id === this.state.selectedEvent) : this.state.status?.event;
  }
  selectRecord(id) {
    if (id !== null && !this.state.history.events.some(event => event.id === id)) return;
    this.invalidate();
    this.mediaGeneration++;
    this.patch({selectedEvent: id, media: null});
  }
  async get(path) {
    const response = await this.fetch(path, {headers: {'X-DoorSense-Token': this.state.status?.token || ''},
      cache: 'no-store', signal: AbortSignal.timeout(this.controlDeadlineMs)});
    const body = await response.json();
    if (!response.ok) throw Error(body.detail || 'Local data unavailable');
    return body;
  }
  async loadHistory(offset = this.state.history.offset) {
    if (!this.state.status || this.historyBusy) return;
    this.historyBusy = true;
    const token = this.state.status.token;
    try {
      const history = await this.get(`/api/events?offset=${offset}`);
      if (this.state.status?.token === token) {
        if (this.state.selectedEvent && !history.events.some(event => event.id === this.state.selectedEvent)) {
          this.invalidate();
          this.patch({selectedEvent: null, media: null});
        }
        this.patch({history, historyError: ''});
      }
    } catch (failure) {this.patch({historyError: this.failureMessage(failure)});}
    finally {this.historyBusy = false;}
  }
  async mutate(path, body = {}) {
    if (this.state.busy || !this.state.status) return;
    this.patch({busy: true, actionError: ''});
    const began = this.now();
    const token = this.state.status.token;
    try {
      const result = await this.post(path, body);
      if (this.state.status?.token !== token) return;
      if (path === '/api/armed' || path === '/api/visitor-confirmation' || path === '/api/session/reset' || path.startsWith('/api/family-reference/')) this.acceptStatus(result, began);
      if (path === '/api/sensors') {
        if (result.status) this.acceptStatus(result.status, began);
        this.patch({sensorResult: result, sensorLog: [...this.state.sensorLog, {accepted: result.accepted, kind: body.kind, reason: result.reason, observed_at: result.input?.observed_at, armed: result.input?.armed, severity: result.event?.severity}].slice(-6)});
        // Periodic history polling handles new records. Do not block the next
        // timed sensor press on an unrelated history request.
        return result;
      }
      await this.loadHistory();
      return result;
    } catch (failure) {this.patch({actionError: this.failureMessage(failure)});}
    finally {this.patch({busy: false});}
  }
  async resetSession() {
    this.invalidate();
    const result = await this.mutate('/api/session/reset');
    if (!result) return false;
    this.mediaGeneration++;
    this.patch({selectedEvent: null, media: null, sensorLog: [], sensorResult: null, answer: null, asking: false, explanationNotice: '', question: questions[0]});
    return true;
  }
  async replay(id) {
    if (!this.state.status || this.state.busy) return;
    const generation = ++this.mediaGeneration;
    const token = this.state.status.token;
    try {
      const media = await this.get(`/api/media/${id}`);
      if (generation === this.mediaGeneration && token === this.state.status?.token) this.patch({media, actionError: ''});
    }
    catch (failure) {this.patch({actionError: this.failureMessage(failure)});}
  }
  async previewFamilyReference() {
    if (!this.state.status || this.state.busy) return;
    const generation = ++this.mediaGeneration;
    const token = this.state.status.token;
    try {
      const reference = await this.get('/api/family-reference');
      if (generation === this.mediaGeneration && token === this.state.status?.token) {
        this.patch({media:{id:'family-reference',kind:'reference',frames:[reference.frame]}, actionError:''});
      }
    } catch (failure) {this.patch({actionError:this.failureMessage(failure)});}
  }
  async deleteFamilyReference() {
    const result = await this.mutate('/api/family-reference/delete');
    if (result && this.state.media?.id === 'family-reference') this.closeMedia();
  }
  closeMedia() {
    this.mediaGeneration++;
    this.patch({media: null});
  }
  async deleteMedia(id) {
    const result = await this.mutate(`/api/media/${id}/delete`);
    if (result?.deleted && this.state.media?.id === id) this.closeMedia();
  }
  async downloadEvidence() {
    if (!this.state.status) return null;
    try {return await this.get('/api/evidence');}
    catch (failure) {this.patch({actionError: this.failureMessage(failure)}); return null;}
  }
  async ask() {
    if (!this.state.status || this.state.asking) return;
    this.checkFreshness();
    const {question} = this.state;
    if (!this.selectedRecord() && !freshFrame(this.state.status, this.requestStarted, this.now())) {
      this.patch({explanationNotice: 'No fresh assessed frame is available. Keep one person visible, then try again.'});
      return;
    }
    const version = ++this.generation;
    this.patch({asking: true, answer: null, actionError: '', explanationNotice: ''});
    try {
      const answer = await this.post('/api/explain', {question, ...(this.state.selectedEvent ? {event_id: this.state.selectedEvent} : {})}, this.explanationDeadlineMs);
      this.checkFreshness();
      if (version === this.generation) this.patch({answer});
    } catch (failure) {
      if (version === this.generation) this.patch({answer: {source: 'application_unavailable', text: this.failureMessage(failure)}});
    } finally {
      if (version === this.generation) this.patch({asking: false});
    }
  }
  async refreshAutomaticAnalysis() {
    if (this.state.status?.demo_mode !== 'face_enrollment' || this.state.busy || this.state.asking) return;
    const frame=freshFrame(this.state.status,this.requestStarted,this.now());
    if (!frame) return;
    const key=JSON.stringify([this.state.status.token,this.state.status.family_reference?.created_at,
      frame.recognition?.category,frame.recognition?.state,frame.features?.face?.state,frame.people.length]);
    const previous=this.autoAnalysisAttempt;
    const answerCurrent=this.state.answer?.source === 'qwen_evidence_selection';
    const failedAnswer=this.state.answer && !answerCurrent;
    if (previous && ((previous.key === key && answerCurrent) ||
        this.now()-previous.at < (failedAnswer ? 30000 : 5000))) return;
    this.autoAnalysisAttempt={key,at:this.now()};
    this.setQuestion('What was observed?');
    return this.ask();
  }
}
