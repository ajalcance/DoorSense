import React, {useEffect, useRef, useState, useSyncExternalStore} from 'react';
import {createRoot} from 'react-dom/client';
import {ConsoleSession, freshFrame, simulationState} from './session.js';
import ConsoleView from './ConsoleView.jsx';
import './styles.css';

const supportedOrigin = location.protocol === 'http:' && ['127.0.0.1', 'localhost'].includes(location.hostname);

function App() {
  const sessionRef = useRef(null);
  if (!sessionRef.current) sessionRef.current = new ConsoleSession();
  const session = sessionRef.current;
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  const [fullscreen, setFullscreen] = useState(false);
  const [view, setView] = useState('overview');
  const [panel, setPanel] = useState(null);
  const [evidenceFocus, setEvidenceFocus] = useState(0);
  const [, setTick] = useState(0);
  const panelTrigger = useRef(null);

  useEffect(() => {
    if (!supportedOrigin) {session.patch({connectionError: 'Open the owner-started local console at http://127.0.0.1:8765. Standalone previews are unavailable.'}); return;}
    let cancelled = false;
    let timer;
    async function poll() {
      const began = performance.now();
      try {
        const response = await fetch('/api/status', {cache: 'no-store', signal: AbortSignal.timeout(1500)});
        if (!response.ok) throw Error('Service unavailable');
        const data = await response.json();
        if (!cancelled) session.acceptStatus(data, began);
      } catch { if (!cancelled) session.pollFailed(); }
      if (!cancelled) timer = setTimeout(poll, 200);
    }
    poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [session]);

  useEffect(() => {
    if (!supportedOrigin) {session.patch({connectionError: 'Open the owner-started local console at http://127.0.0.1:8765. Standalone previews are unavailable.'}); return;}
    session.loadHistory();
    const timer = setInterval(() => session.loadHistory(), 2000);
    return () => clearInterval(timer);
  }, [session, !!state.status]);

  useEffect(() => {
    const timer = setInterval(() => {session.checkFreshness(); setTick(value => value + 1);}, 100);
    return () => clearInterval(timer);
  }, [session]);
  useEffect(() => {
    const update = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', update);
    return () => document.removeEventListener('fullscreenchange', update);
  }, []);

  function closePanel() {
    setPanel(null);
    panelTrigger.current?.focus();
  }
  useEffect(() => {
    if (!panel) return;
    document.querySelector('.tool-panel button')?.focus();
    const escape = event => {if (event.key === 'Escape') closePanel();};
    const outside = event => {if (!event.target.closest('.tool-panel, .tool-trigger')) setPanel(null);};
    document.addEventListener('keydown', escape);
    document.addEventListener('pointerdown', outside);
    return () => {
      document.removeEventListener('keydown', escape);
      document.removeEventListener('pointerdown', outside);
    };
  }, [panel]);

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {session.patch({actionError: 'Fullscreen unavailable in this browser.'});}
  }

  async function downloadEvidence() {
    const evidence = await session.downloadEvidence();
    if (!evidence) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(evidence, null, 2)], {type:'application/json'}));
    const link = document.createElement('a');
    link.href = url;
    link.download = `doorsense-runtime-evidence-${Date.now()}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  const frame = freshFrame(state.status, session.requestStarted, performance.now());
  const camera = state.status?.camera || 'unknown';
  const selected = session.selectedRecord();
  const severity = selected?.severity || state.status?.severity;
  const title = selected ? selected.severity === 'urgent' ? 'Urgent review' : 'Review event' : camera === 'paused' ? 'Monitoring paused' : camera === 'monitoring' ? (state.status?.assessment === 'unavailable' ? 'Person assessment unavailable' : frame ? 'Camera monitoring' : 'Assessment waiting') : camera === 'starting' ? 'Starting camera' : camera === 'stopping' ? 'Stopping camera' : 'Monitoring unavailable';
  const confirmation = frame && !selected ? state.status?.confirmation : null;
  const factRecords = selected?.facts || confirmation?.facts || frame?.facts || [];
  const facts = selected ? selected.facts.map(fact => fact.text) : confirmation ? confirmation.facts.map(fact => fact.text) : frame ? [
    ...(frame.facts?.map(fact => fact.text) || [`The detector reported ${frame.people.length} ${frame.people.length === 1 ? 'person' : 'people'} in this frame.`]),
  ] : [];
  const stamp = frame ? new Date(frame.captured_at).toLocaleTimeString('en-PH', {timeZone: 'Asia/Manila'}) : null;
  const error = [state.connectionError, state.actionError].filter(Boolean).join(' ');
  const simulation = simulationState(state.status, session.requestStarted, performance.now());
  const model = {...state, simulation, error, selected, confirmation, factRecords, ack: !!selected?.acknowledged_at, fullscreen, view, panel, frame, camera, severity, title, facts, stamp, evidenceFocus};
  useEffect(() => {session.refreshAutomaticAnalysis();});
  const actions = {
    resetSession: async () => {if (await session.resetSession()) {setPanel(null); setView('overview'); setEvidenceFocus(0);}},
    control: action => session.control(action),
    ask: () => session.ask(),
    acknowledge: () => session.acknowledge(),
    setQuestion: value => session.setQuestion(value),
    toggleFullscreen, closePanel, downloadEvidence,
    setView: value => {setPanel(null); session.selectRecord(null); setView(value);},
    selectRecord: id => session.selectRecord(id),
    openActiveEvent: () => {setPanel(null); session.selectRecord(null); setView('events'); setEvidenceFocus(value => value+1); session.loadHistory(0);},
    openEvent: async () => {setPanel(null); await session.loadHistory(0); session.selectRecord(selected.id); setView('events'); setEvidenceFocus(value => value+1);},
    loadHistory: offset => session.loadHistory(offset),
    arm: armed => session.mutate('/api/armed', {armed}),
    sensor: kind => session.mutate('/api/sensors', {kind}),
    confirmVisitor: label => session.mutate('/api/visitor-confirmation', {label}),
    saveFamilyReference: () => session.mutate('/api/family-reference/save'),
    deleteFamilyReference: () => session.deleteFamilyReference(),
    previewFamilyReference: () => session.previewFamilyReference(),
    feedback: feedback => session.mutate(`/api/events/${selected.id}/feedback`, {feedback}),
    captureMedia: action => session.mutate(`/api/events/${selected.id}/media/${action}`),
    stopRecording: () => session.mutate(`/api/events/${state.status.recording.event_id}/media/stop`),
    replay: id => session.replay(id),
    deleteMedia: id => session.deleteMedia(id),
    closeMedia: () => session.closeMedia(),
    togglePanel: (value, trigger) => {panelTrigger.current = trigger; setPanel(current => current === value ? null : value);},
  };
  return <ConsoleView model={model} actions={actions}/>;
}

createRoot(document.getElementById('root')).render(<App/>);
