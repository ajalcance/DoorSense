import React, {useEffect, useRef, useState} from 'react';
import {questions} from './contracts.js';
import {visitAnalysis} from './analysis.js';

export const responseLabels = {
  qwen_evidence_selection: 'Qwen-selected evidence',
  template_fallback: 'Template fallback',
  application_unavailable: 'Application unavailable',
  discarded: 'Superseded response discarded',
};

function Icon({ type, className = '' }) {
  return <svg className={className} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
    {type === 'brand' ? <><path d="M12 2 22 12 12 22 2 12Z"/><path d="m12 6 6 6-6 6-6-6Z"/></>
      : type === 'overview' ? <><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M15 4v16M3 15h12"/></>
      : type === 'camera' ? <><rect x="3" y="6" width="14" height="12" rx="3"/><path d="m17 10 4-3v10l-4-3"/></>
      : <><path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h1M3 12h1M3 18h1"/></>}
  </svg>;
}

function Assessment({ model: m, actions: a }) {
  const [tab, setTab] = useState('scene');
  useEffect(() => {if (m.evidenceFocus) {setTab('evidence'); document.getElementById('analysis-tab-evidence')?.focus();}}, [m.evidenceFocus]);
  const hasAlert = ['urgent', 'review'].includes(m.severity) && m.selected;
  const analysis = visitAnalysis(m);
  const faceDemo = m.status?.demo_mode === 'face_enrollment' && !m.selectedEvent;
  if (!m.selectedEvent && m.status?.demo_mode !== 'legacy_activity') return <FaceAssessment model={m} actions={a}/>;
  const scores = (m.frame?.people || []).map(item => item.score).filter(value => Number.isFinite(value) && value >= 0 && value <= 1);
  const score = scores.length ? `${Math.round(Math.min(...scores)*100)}${scores.length > 1 ? `–${Math.round(Math.max(...scores)*100)}` : ''}%` : '—';
  return <aside className="panel assessment" aria-label="Current assessment">
    <section className={`assessment-section event ${faceDemo ? analysis.level : m.severity || 'neutral'}`}>
      <div className="assessment-status-row"><h2 className="status-title"><span className="status-mark" aria-hidden="true">{m.severity === 'urgent' ? '!' : m.severity === 'review' ? '△' : '○'}</span>{faceDemo ? analysis.headline : m.title}</h2>
        {hasAlert && <button className="small-button" onClick={a.acknowledge} disabled={!m.status || m.ack || m.busy || m.selected?.persisted === false}>{m.ack ? 'Acknowledged' : 'Acknowledge'}</button>}
      </div>
      <div className="assessment-context-row">{m.selectedEvent && <span className="historical-tag">Saved event · historical severity</span>}<p>{faceDemo ? 'Live camera → local face comparison → child guidance' : m.selected?.rule_reason || m.status?.rule_reason || 'Event rule state unavailable.'}</p><span className="source-label">{m.selected ? `Source: ${[...new Set(m.selected.facts.map(f => f.source))].join(' / ')}` : 'Source: webcam / system'}</span></div>
    </section>
    <div className="ai-metrics" aria-label="Live vision measurements">
      <div><small>People detected</small><strong>{m.frame ? m.frame.people.length : '—'}</strong></div>
      <div><small>Detector score</small><strong>{score}</strong></div>
      <div><small>Vision latency</small><strong>{m.frame ? `${Math.round(m.frame.inference_ms)}` : '—'}<span>{m.frame ? ' ms' : ''}</span></strong></div>
    </div>
    {faceDemo && <LearningSummary model={m}/>}
    <div className="analysis-heading"><h3>Local AI workspace</h3><span className="local-indicator">On-device</span></div>
    <div className="analysis-tabs" role="tablist" aria-label="Local AI views">{[['scene','Analysis'],['qwen','Qwen'],['evidence',faceDemo ? 'Learning' : 'Evidence']].map(([key,label]) => <button key={key} id={`analysis-tab-${key}`} role="tab" aria-selected={tab === key} aria-controls={`analysis-${key}`} tabIndex={tab === key ? 0 : -1} onClick={() => setTab(key)} onKeyDown={event => {
      const keys = ['scene','qwen','evidence'];
      let index = keys.indexOf(key);
      if (event.key === 'ArrowRight') index = (index+1)%3;
      else if (event.key === 'ArrowLeft') index = (index+2)%3;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = 2;
      else return;
      event.preventDefault(); setTab(keys[index]); document.getElementById(`analysis-tab-${keys[index]}`)?.focus();
    }}>{label}{key === 'qwen' && m.answer && <span className="tab-dot" aria-label="Response available"/>}</button>)}</div>
    <div className="analysis-content">
    <section className="assessment-section observations" id="analysis-scene" role="tabpanel" aria-labelledby="analysis-tab-scene" hidden={tab !== 'scene'}>
      <section className={`visit-analysis ${analysis.level}`} aria-label="Visit evidence assessment">
        <small>{analysis.historical ? 'Saved event interpretation' : 'Visit interpretation · application assessment'}</small>
        <h3>{analysis.headline}</h3><p>{analysis.interpretation}</p>
        <dl><dt>Visitor context</dt><dd>{analysis.visitor}{analysis.historical && ' · current snapshot is separate from this saved event'}</dd>
          {analysis.match && <><dt>Local face comparison</dt><dd>{analysis.match}</dd></>}
          {!faceDemo && <><dt>Likelihood of suspicious intent</dt><dd>{analysis.probability}</dd></>}</dl>
        <details open><summary>Supporting evidence</summary>{analysis.evidence.length ? <ul>{analysis.evidence.map((fact,index) => <li key={index}>{fact.text}<small>{fact.source}{fact.time ? ` · ${new Date(fact.time).toLocaleTimeString()}` : ''}</small></li>)}</ul> : <p>No supported evidence available.</p>}</details>
        {analysis.missing.length > 0 && <details><summary>Missing evidence and uncertainty</summary><ul>{analysis.missing.map(text => <li key={text}>{text}</li>)}</ul></details>}
        <p className="analysis-guidance"><strong>For children: </strong>{analysis.nextStep}</p>
      </section>
      <h3>Observations</h3>
      {m.confirmation && <div className="owner-annotation"><strong>Visitor snapshot · parent-confirmed category</strong><small>{m.confirmation.label} · Frame {m.confirmation.sequence} · {new Date(m.confirmation.captured_at).toLocaleTimeString()}<br/>Applies only to that snapshot; not recognition of later live frames.</small><button className="small-button" disabled={m.busy || !m.status} onClick={() => a.confirmVisitor(null)}>Clear visitor confirmation</button></div>}
      {!m.selected && <FaceAvailability feature={m.frame?.features?.face || m.status?.features?.face}/>}
      {m.facts.length ? <ul className="fact-list">{m.facts.map((fact, index) => <li key={index}>{fact}<small>{m.factRecords?.[index] ? `${m.factRecords[index].source} · ${new Date(m.factRecords[index].observed_at).toLocaleTimeString()}` : m.selected ? `${m.selected.facts[index].source} · ${new Date(m.selected.facts[index].observed_at).toLocaleTimeString()}` : `Laptop webcam · ${m.stamp}`}</small></li>)}</ul>
        : <p className="muted">No current evidence available.</p>}
      {!m.selected && <div className="feature-status" aria-label="Scene feature availability">{Object.entries(m.frame?.features || m.status?.features || {}).map(([name, feature]) => <div key={name}><span>{name === 'face' ? 'Facial movement' : 'Body posture'} · {feature.state}</span><small>{feature.message}</small></div>)}</div>}
    </section>
    <section className="assessment-section explanation" id="analysis-qwen" role="tabpanel" aria-labelledby="analysis-tab-qwen" hidden={tab !== 'qwen'}>
      <div className="model-heading"><div><h3>Qwen</h3><span className="model-purpose">Evidence selection · text model</span></div><span className="model-tag">0.6B · local</span></div>
      <div className="qwen-question">
      <label htmlFor="question">Question about the evidence</label>
      <div className="qwen-controls">
      <select id="question" value={m.question} onChange={event => a.setQuestion(event.target.value)}>{questions.map(question => <option key={question}>{question}</option>)}</select>
      <button className="ask" disabled={!m.status || m.asking || (!m.frame && !m.selected)} onClick={a.ask}>{m.asking ? 'Selecting…' : 'Select evidence'}</button>
      </div><p className="helper qwen-input-note">Uses supplied facts, not camera images.</p></div>
      <div className={`answer qwen-result ${m.answer ? 'has-response' : 'awaiting-response'}`} aria-live="polite" aria-busy={!!m.asking}>
        <div className="qwen-result-heading"><span>Result</span>{m.asking ? <small>Selecting evidence…</small> : !m.answer && <small>No response yet</small>}</div>
        {m.answer ? <>
          <span className="answer-source">{responseLabels[m.answer.source] || 'Response unavailable'}</span>
          <p>{m.answer.text || 'The observation changed before this response completed. Ask again about the current observation.'}</p>
          {m.answer.observation_captured_at && <small>{m.answer.observation_source === 'saved_event' ? 'Evidence observed' : 'Frame captured'} at {new Date(m.answer.observation_captured_at).toLocaleTimeString('en-PH', { timeZone: 'Asia/Manila' })} Philippine time.</small>}
          {m.answer.fallback_reason && <small>Fallback reason: {m.answer.fallback_reason}</small>}
        </> : <>{m.explanationNotice && <span className="answer-source">Request or result cleared</span>}<p className="helper">{m.explanationNotice || (!m.status ? 'Connect to the console service to request a response.' : m.asking ? 'Local Qwen is selecting supplied evidence. Keep this view open.' : !m.frame && !m.selected ? 'Start monitoring or select a saved event to supply evidence.' : 'Choose a supported question, then select evidence.')}</p></>}
        {m.answer && <div className="response-metrics"><small>{m.answer.source === 'qwen_evidence_selection' && m.answer.model ? `Accepted model: ${m.answer.model}` : 'No accepted Qwen selection claimed'}</small>{Number.isFinite(m.answer.elapsed_ms) && <small>Response · {Math.round(m.answer.elapsed_ms)} ms</small>}</div>}
      </div>
      <p className="helper qwen-provenance">Qwen selects supplied evidence; original wording is preserved.</p>
    </section>
    <section id="analysis-evidence" role="tabpanel" aria-labelledby="analysis-tab-evidence" hidden={tab !== 'evidence'}>
      {faceDemo ? <LearningDetails model={m} actions={a}/> : m.selected && m.view === 'events' ? <Evidence model={m} actions={a}/> : <EvidenceOverview model={m} actions={a}/>}
    </section>
    </div>
    <div className="analysis-footer"><span>{m.selectedEvent ? 'Saved event facts · live metrics above' : m.confirmation ? 'Owner-confirmed snapshot facts · live metrics above' : 'Timestamped facts · sampled camera frames'}</span></div>
  </aside>;
}

function FaceAssessment({model:m,actions:a}) {
  const analysis=visitAnalysis({...m,status:m.status || {demo_mode:'face_enrollment',armed:false}});
  const rawRecognition=m.frame?.recognition;
  const recognition=rawRecognition?.sequence === m.frame?.sequence && rawRecognition?.captured_at === m.frame?.captured_at ? rawRecognition : null;
  const distance=recognition?.distance;
  const threshold=recognition?.threshold ?? m.status?.learning?.threshold;
  const hasDistance=Number.isFinite(distance) && Number.isFinite(threshold);
  const nearCutoff=hasDistance && Math.abs(distance-threshold) <= 5;
  const score=m.frame?.people?.[0]?.score;
  const family=analysis.visitor === 'Family member';
  return <aside className="panel assessment face-assessment" aria-label="AI Analysis">
    <div className="analysis-heading"><h2>AI Analysis</h2><span className="local-indicator">On-device · automatic</span></div>
    <div className="analysis-content">
      <section className={`visitor-verdict ${analysis.level}`} aria-label="Visitor assessment">
        <span className="verdict-icon" aria-hidden="true">{family ? '✓' : m.frame ? '?' : '○'}</span>
        <div><small>Live camera assessment</small><h2>{analysis.headline}</h2><p>{analysis.interpretation}</p></div>
      </section>
      <section className={`child-recommendation ${analysis.guidanceEnabled ? analysis.level : 'off'}`} aria-label="Child guidance">
        <small>{analysis.guidanceEnabled ? 'For children' : 'Parent control'}</small>
        <h3>{analysis.guidanceEnabled ? family ? 'Ask a parent before opening' : 'Keep the door closed. Get a parent.' : 'Child safety mode is off'}</h3>
        <p>{analysis.guidanceEnabled ? family ? 'A familiar face is a reason to check with your parent, not permission to open.' : 'Let your parent check who is at the door. Unknown does not mean dangerous.' : 'Face learning and recognition continue. Enable the mode to show child alerts.'}</p>
      </section>
      <section className="face-comparison" aria-label="Face comparison result">
        <div className="learning-heading"><h3>Why this result?</h3><span className={`decision-chip ${family ? 'accepted' : ''}`}>{hasDistance ? family ? 'Match accepted' : 'Match rejected' : 'Awaiting comparison'}</span></div>
        <p>{analysis.reason}</p>
        {hasDistance && <><div className="comparison-values"><strong>{distance.toFixed(2)}<small>Face distance · lower is closer</small></strong><span>Match at ≤ {threshold}</span></div><meter aria-label="Face match distance" min="0" max={Math.max(threshold*2,distance)} low={threshold} high={threshold} optimum="0" value={distance}/>{nearCutoff && <small className="near-cutoff">Close to the cutoff · parent confirmation is especially important.</small>}</>}
      </section>
      <section className="learning-proof" aria-label="Supervised face learning">
        <span className="learning-proof-icon" aria-hidden="true">✦</span><div><h3>Supervised face learning</h3><p>{m.status?.learning?.example_count ? '1 parent-labeled face saved · compared locally with each clear frame.' : '0 family examples · save your face to teach the system.'}</p><small>{m.status?.family_reference ? 'Delete the example to repeat as Unknown.' : 'Your confirmation supplies the family label.'}</small></div>
      </section>
      <div className="automatic-findings" aria-live="polite">{m.answer?.source === 'qwen_evidence_selection' ? <><small>Local model findings</small><p>{m.answer.text}</p></> : m.asking ? <small>Updating local model findings…</small> : <small>Camera findings update automatically. {m.answer && 'The text explanation is unavailable; the face assessment above remains visible.'}</small>}</div>
      <details className="analysis-details"><summary>Measurements and learning details</summary>
        <dl><dt>Person detection score</dt><dd>{Number.isFinite(score) ? `${Math.round(score*100)}% · person detector, not identity confidence` : 'No current person score'}</dd><dt>Vision latency</dt><dd>{m.frame ? `${Math.round(m.frame.inference_ms)} ms` : 'Waiting for camera'}</dd><dt>Learning method</dt><dd>One labeled example · OpenCV LBPH</dd><dt>Training time</dt><dd>{Number.isFinite(recognition?.training_ms) ? `${recognition.training_ms.toFixed(2)} ms` : 'No current training measurement'}</dd><dt>Face comparison time</dt><dd>{Number.isFinite(recognition?.inference_ms) ? `${recognition.inference_ms.toFixed(2)} ms` : 'No current comparison'}</dd></dl>
        <p className="helper">Distance is not a probability. Pose and lighting can change a comparison. A match does not establish friendly intent or safety.</p>
        {m.status?.family_reference && <button className="small-button" disabled={m.busy} onClick={a.previewFamilyReference}>View learned face example</button>}
        {m.answer && <small>{responseLabels[m.answer.source] || 'Text explanation unavailable'}</small>}
      </details>
    </div>
    <div className="analysis-footer"><span>{m.stamp ? `Live assessment · ${m.stamp} · frame ${m.frame.sequence}` : 'Waiting for a fresh camera frame'}</span></div>
  </aside>;
}

function LearningSummary({model:m}) {
  const recognition=m.frame?.recognition;
  const enrolled=!!m.status?.family_reference?.automatic_matching;
  return <section className="learning-summary" aria-label="Supervised face learning">
    <div className="learning-heading"><h3>Supervised face learning</h3><span className="local-indicator">Local</span></div>
    <div className="learning-metrics"><div><small>Labeled examples</small><strong>{m.status?.learning?.example_count ?? (enrolled ? 1 : 0)}</strong></div><div><small>Face match distance</small><strong>{Number.isFinite(recognition?.distance) ? recognition.distance.toFixed(2) : '—'}</strong></div><div><small>Match threshold</small><strong>{recognition?.threshold ?? m.status?.learning?.threshold ?? '—'}</strong></div></div>
    <p className="helper">{!enrolled ? 'No family example learned. Enroll your face to change the next comparison.' : recognition?.trained_examples === 1 ? 'The recognizer learned your labeled example and is comparing camera frames.' : 'Example enrolled. Start the camera with a clear face to train and compare.'}</p>
    <small>Lower distance means a closer appearance match · not a probability.</small>
  </section>;
}

function LearningDetails({model:m,actions:a}) {
  const reference=m.status?.family_reference;
  const recognition=m.frame?.recognition;
  return <section className="assessment-section" aria-label="Local learning evidence">
    <h3>What the system learned</h3>
    <p className="helper">Your confirmation labels one captured face as Family member. LBPH learns its texture pattern and compares later camera faces with it.</p>
    <dl><dt>Learning method</dt><dd>Supervised enrollment · OpenCV LBPH</dd>
      <dt>Training data</dt><dd>{reference?.automatic_matching ? '1 captured face · Family member' : '0 labeled face examples'}</dd>
      <dt>Local training time</dt><dd>{Number.isFinite(recognition?.training_ms) ? `${recognition.training_ms.toFixed(2)} ms` : 'Awaiting training on a clear camera frame'}</dd>
      <dt>Local comparison time</dt><dd>{Number.isFinite(recognition?.inference_ms) ? `${recognition.inference_ms.toFixed(2)} ms` : 'No current comparison'}</dd>
      <dt>Current decision</dt><dd>{recognition?.category || 'Waiting for camera analysis'} · {recognition?.message || 'No fresh face assessment'}</dd>
      {reference && <><dt>Example captured</dt><dd>{new Date(reference.captured_at).toLocaleTimeString()} · Frame {reference.sequence}</dd></>}
    </dl>
    {reference && <button className="small-button" disabled={m.busy} onClick={a.previewFamilyReference}>View captured training example</button>}
    <p className="helper">Deleting the example removes the basis for a family match. The next face is Unknown. Stop and Reset keep the example.</p>
    <p className="helper">Single-example demo; recognition accuracy is unmeasured. Familiarity does not establish friendly intent. Child recommendations are application guidance; Qwen separately selects supplied facts.</p>
  </section>;
}

function FaceAvailability({feature}) {
  const available = feature?.state === 'available';
  const off = !feature || feature.state === 'disabled';
  return <div className={`face-availability ${available ? 'available' : 'limited'}`}><span className="face-status-dot"/><div><strong>{available ? 'Face analysis available · identity unverified' : off ? 'Face analysis off · identity unverified' : 'Face analysis limited · ask a parent before opening'}</strong><small>{available ? 'Face landmarks available; the separate local matcher assesses the enrolled example.' : off ? 'Requires the local Face Landmarker model and owner startup configuration.' : 'Availability is separate from event severity; this is not a suspicious-person classification.'}</small></div></div>;
}

function EvidenceOverview({model: m, actions: a}) {
  const event = m.selected;
  return <section className="assessment-section evidence-overview">
    <div className="evidence-heading"><div><h3>Evidence library</h3><p className="helper">Event records, snapshot facts and saved media</p></div><span className="model-tag">Local</span></div>
    <div className="evidence-summary"><div><small>Local event records</small><strong>{Number.isInteger(m.history?.total) ? m.history.total : '—'}</strong></div><div><small>Media in selected event</small><strong>{event ? event.media?.length || 0 : '—'}</strong></div></div>
    <div className="evidence-context-card">
      <div className="evidence-card-title"><Icon type="events"/><h3>{event ? 'Local event record' : m.confirmation ? 'Owner-confirmed snapshot facts' : 'No selected event'}</h3></div>
      {event ? <><small>{event.persisted === false ? 'Session only · not persisted' : 'Local record'} · {m.ack ? 'acknowledged' : 'unacknowledged'}</small><p className="helper">{event.rule_reason}</p><button className="small-button" onClick={a.openEvent}>Event details · media & feedback</button></> : m.confirmation ? <><small>{m.confirmation.label} · Frame {m.confirmation.sequence} · {new Date(m.confirmation.captured_at).toLocaleTimeString()}</small><ul className="fact-list">{m.confirmation.facts?.map(fact => <li key={fact.id}>{fact.text}<small>{fact.source}</small></li>)}</ul><p className="helper">Temporary annotation · no image saved. Media and feedback require an event.</p></> : <p className="helper">Select a local record to view its evidence, or use labelled inputs to create a test event.</p>}
    </div>
    <div className="evidence-navigation"><button className="small-button" onClick={() => a.setView('events')}>Browse local events</button><button className="small-button" onClick={() => a.setView('overview')}>Visit simulation controls</button></div>
    <p className="helper evidence-storage-note">Media is saved only when you request it for an active event.</p>
  </section>;
}

function Evidence({model: m, actions: a}) {
  const event = m.selected;
  const recording = m.status?.recording;
  const canCapture = m.frame && m.status?.event?.id === event.id && event.persisted !== false;
  return <section className="assessment-section evidence">
    <h3>Evidence & feedback</h3>
    <small>{m.selectedEvent ? 'Saved event · historical severity' : 'Active event'} · {new Date(event.created_at).toLocaleString()}<br/>Expires {new Date(event.expires_at).toLocaleTimeString()}; acknowledgement does not resolve it.</small>
    <div className="compact-actions">
      <button className="small-button" disabled={m.busy || !canCapture || !!recording} onClick={() => a.captureMedia('snapshot')}>Save current snapshot</button>
      <button className="small-button" disabled={m.busy || (recording ? recording.event_id !== event.id : !canCapture)} onClick={() => a.captureMedia(recording ? 'stop' : 'record')}>{recording?.event_id === event.id ? 'Stop & save clip' : 'Record up to 10s'}</button>
    </div>
    <small>Current active event only. Saves a fresh assessed frame; clips continue after your action. No pre-event buffer.</small>
    {event.media?.length ? <ul className="media-list">{event.media.map(media => <li key={media.id}><span>{media.kind} · {new Date(media.created_at).toLocaleTimeString()}</span><div className="compact-actions"><button className="small-button" disabled={!m.status || m.busy} onClick={() => a.replay(media.id)}>View {media.kind}</button><button className="small-button" disabled={!m.status || m.busy} onClick={() => a.deleteMedia(media.id)}>Delete media</button></div></li>)}</ul> : <small>No saved media for this event.</small>}
    <label htmlFor="feedback">Resident feedback</label><select id="feedback" value={event.feedback || ''} disabled={!m.status || m.busy || event.persisted === false} onChange={e => a.feedback(e.target.value)}><option value="" disabled>Unknown · no feedback</option>{['Useful alert', 'Unnecessary alert', 'Incorrect detection'].map(label => <option key={label}>{label}</option>)}</select>
    <small>Stored with this event. Does not retrain a model.</small>
  </section>;
}

function MediaViewer({media, close}) {
  const closeButton = useRef(null);
  useEffect(() => {
    const previous = document.activeElement;
    closeButton.current?.focus();
    return () => {if (previous?.isConnected) previous.focus();};
  }, []);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  useEffect(() => {setIndex(0); setPlaying(false);}, [media.id]);
  useEffect(() => {
    if (!playing) return;
    if (index >= media.frames.length-1) {setPlaying(false); return;}
    const gap = Math.max(40, Math.min(1000, Date.parse(media.frames[index+1].captured_at)-Date.parse(media.frames[index].captured_at)));
    const timer = setTimeout(() => setIndex(i => i+1), gap);
    return () => clearTimeout(timer);
  }, [playing, index, media]);
  useEffect(() => {const escape = e => {if (e.key === 'Escape') close();}; document.addEventListener('keydown', escape); return () => document.removeEventListener('keydown', escape);}, [close]);
  const frame = media.frames[Math.min(index, media.frames.length-1)];
  return <section className="panel media-viewer" role="dialog" aria-modal="false" aria-label="Recorded webcam evidence">
    <div className="tool-heading"><h2>{media.kind === 'reference' ? 'Saved Family member reference' : `Recorded webcam · ${media.kind}`}</h2><button ref={closeButton} aria-label="Close recorded media" className="close-button" onClick={close}>×</button></div>
    <p className="helper">Saved local evidence · no inference on replay · not the live view</p>
    <img src={`data:image/jpeg;base64,${frame.image}`} alt="Saved webcam evidence"/>
    <div className="compact-actions">{media.kind === 'clip' && <button className="small-button" onClick={() => {if (index === media.frames.length-1) setIndex(0); setPlaying(!playing);}}>{playing ? 'Pause' : 'Play clip'}</button>}<small>Frame {index+1} / {media.frames.length} · {new Date(frame.captured_at).toLocaleString()}</small></div>
  </section>;
}

function LiveView({ model: m }) {
  const analysis=visitAnalysis({...m,status:m.status || {demo_mode:'face_enrollment',armed:false}});
  const faceDemo=m.status?.demo_mode !== 'legacy_activity';
  return <section className="panel camera-panel" aria-label="Live view">
    <div className="camera-heading"><div><h1>Live view</h1><div className="availability"><span>{'Webcam'} · {m.camera}</span><span>Assessment · {m.frame ? 'available' : m.status?.assessment === 'unavailable' ? 'unavailable' : m.status ? 'waiting' : 'unknown'}</span></div></div></div>
    <div className="viewport">
      {faceDemo && <div className={`camera-alert-banner ${analysis.guidanceEnabled ? analysis.level : 'off'}`} role="status" aria-live="polite"><span aria-hidden="true">{analysis.guidanceEnabled ? m.frame?.recognition?.state === 'matched' ? '✓' : '!' : '○'}</span><div><small>{analysis.guidanceEnabled ? 'Child safety mode · On' : 'Child safety mode · Off'}</small><strong>{analysis.banner}</strong>{!analysis.guidanceEnabled && <small>{analysis.headline}</small>}</div></div>}
      {m.frame ? <div className="image-wrap">
        <img alt="Current laptop webcam frame" src={`data:image/jpeg;base64,${m.frame.image}`}/>
        <svg viewBox={`0 0 ${m.frame.width} ${m.frame.height}`} preserveAspectRatio="xMidYMid meet" aria-label="Person and supported object detection boxes">
          {m.frame.people.map((person, index) => {
            const [x,y,w,h] = person.box, corner = Math.min(24, w/4, h/4);
            const path = `M${x+corner} ${y}H${x}V${y+corner} M${x+w-corner} ${y}H${x+w}V${y+corner} M${x} ${y+h-corner}V${y+h}H${x+corner} M${x+w-corner} ${y+h}H${x+w}V${y+h-corner}`;
            return <g key={index}><path d={path}/><text x={Math.max(0, x)} y={Math.max(18, y-6)}>Person {index+1}{Number.isFinite(person.score) ? ` · ${Math.round(person.score*100)}% model score` : ''}</text></g>;
          })}
          {(m.frame.objects || []).map((item, index) => <g className="object-box" key={`object-${index}`}><rect x={item.box[0]} y={item.box[1]} width={item.box[2]} height={item.box[3]}/><text x={Math.max(0, item.box[0])} y={Math.max(18, item.box[1]-6)}>{item.label}</text></g>)}
        </svg>
      </div> : <div className="placeholder"><Icon type="camera"/><h2>{m.camera === 'paused' ? 'Camera is off' : 'Fresh assessed image unavailable'}</h2>
        <p>{m.status?.assessment_message || (m.camera === 'paused' ? 'Start monitoring from the toolbar.' : m.status?.message) || 'Start the local service, then use the toolbar.'}</p>
      </div>}
      {m.frame && <details className={`camera-hud ${m.status?.event?.severity || (m.status?.armed ? 'monitoring' : 'neutral')}`}><summary><span className="hud-mark"/>{m.status?.event ? `${m.status.event.severity === 'urgent' ? 'Urgent review' : 'Review event'}` : m.status?.armed ? 'Monitoring' : 'Camera active'}<span className="hud-detail">{m.frame.people.length} detected · findings</span></summary><div><strong>Current frame · identity unverified</strong><ul>{(m.frame.facts || []).map(fact => <li key={fact.id}>{fact.text}</li>)}</ul><small>Frame-local detections; no persistent identity tracking. No emotion, relationship or safety conclusion.</small></div></details>}
    </div>
    <div className="camera-meta"><span>{m.stamp ? `Captured ${m.stamp} · Philippine time · Frame ${m.frame.sequence}` : 'No automatic media storage'}</span><span>{m.status?.recording ? `Recording · ${m.status.recording.seconds}s / 10s` : 'Not recording'}</span></div>
  </section>;
}

function Events({ model: m, actions: a }) {
  return <section className="events-view" aria-labelledby="events-title">
    <div className="view-heading"><h1 id="events-title">Recent events</h1><p className="muted">{'Local event history · simulation provenance preserved · media saved only on request'}</p></div>
    {<div className="events-layout">
      <div className="panel event-list" aria-label="Local event records">
        {m.historyError && <p role="status" className="helper">{m.historyError}</p>}
        {(m.history?.events || []).map(event => <button key={event.id} className={`event-record ${m.selectedEvent === event.id ? 'selected' : ''}`} aria-pressed={m.selectedEvent === event.id} onClick={() => a.selectRecord(event.id)}>
          <span className={`record-indicator ${event.severity}`} aria-hidden="true"/>
          <span><strong>{event.severity === 'urgent' ? 'Urgent review' : 'Review'} · {event.rule_id.replaceAll('_', ' ')}</strong>
            <small>{new Date(event.created_at).toLocaleString()} · {event.facts.some(f => f.source === 'simulated_sensor') ? 'Simulated sensor' : 'Laptop webcam'}</small>
            <small>{event.acknowledged_at ? 'Acknowledged' : 'Unacknowledged'} · {event.media.length} saved media</small></span>
        </button>)}
        <p className="list-note">{m.history?.total || 0} local records. Active alerts expire; history remains.</p>
        <div className="compact-actions"><button className="small-button" disabled={!m.history?.offset} onClick={() => a.loadHistory(Math.max(0, m.history.offset-25))}>Newer</button><button className="small-button" disabled={m.history?.next_offset == null} onClick={() => a.loadHistory(m.history.next_offset)}>Older</button></div>
      </div>
      {m.selected ? <Assessment model={m} actions={a}/> : <div className="panel empty-state"><Icon type="events"/><h2>{m.history?.total ? 'Select an event' : 'No events yet'}</h2><p>Enable Child safety mode and use labelled sensor inputs, or monitor sustained person detections. No footage is stored automatically.</p></div>}
    </div>}

  </section>;
}

function SimulationControls({ model: m, actions: a }) {
  const reference = m.status?.family_reference;
  const blocked = !m.status ? 'Console service unavailable.' : m.busy ? 'Waiting for the current action.' : m.camera !== 'monitoring' ? 'Start the camera above.' : !m.frame ? 'Waiting for a fresh assessed frame.' : m.frame.people.length !== 1 ? 'Show one person at a time.' : m.frame.features?.face?.state !== 'available' ? 'Face the camera and wait for face analysis.' : '';
  const recognition = m.frame?.recognition;
  return <aside className="simulation-column panel" aria-label="Face learning demo controls">
    <h2>Face learning demo</h2>
    <p className="helper">One camera. Two visitor scenarios.</p>
    <section className="sensor-controls parent-face-controls" aria-label="Parent controls">
      <div className="learning-heading"><h3>Child safety mode</h3><span className={`decision-chip ${m.status?.armed ? 'accepted' : ''}`}>{m.status?.armed ? 'On' : 'Off'}</span></div>
      <p className="helper">Parents choose when to show child guidance. Recognition works in either mode.</p>
      <button className="small-button" disabled={m.busy || !m.status} aria-pressed={!!m.status?.armed} onClick={() => a.arm(!m.status?.armed)}>{m.status?.armed ? 'Turn off Child safety mode' : 'Enable Child safety mode'}</button>
    </section>
    <section className="sensor-controls visit-scenario" aria-labelledby="visit-scenario-title">
      <h3 id="visit-scenario-title">1. Learn a family member</h3>
      <p className="helper">Start the camera, face it, then save your face. The next frames are compared with your saved example.</p>
      {reference ? <><p className="confirmation-readiness ready">Family example saved locally</p><button className="small-button" disabled={m.busy} onClick={a.previewFamilyReference}>View captured face</button>{!reference.automatic_matching && <p className="helper">This older photo needs reenrollment. Delete it below, then save your face again.</p>}</> : <><button className="small-button primary" aria-describedby="reference-readiness" disabled={!!blocked} onClick={a.saveFamilyReference}>Save my face as Family member</button><p id="reference-readiness" className="confirmation-readiness" role="status">{blocked || 'Ready to capture and learn your face.'}</p></>}
    </section>
    <section className="sensor-controls">
      <h3>2. Try an unknown visitor</h3>
      <p className="helper">Delete your saved example and stay in view. The same face becomes Unknown because it is no longer enrolled.</p>
      <button className="small-button" disabled={!reference || m.busy || !m.status} onClick={a.deleteFamilyReference}>Delete face · try Unknown</button>
    </section>
    <section className="sensor-controls" aria-label="Live visitor result">
      <h3>Camera result</h3>
      <p className="confirmation-readiness" role="status">{recognition ? recognition.category : 'Waiting for camera analysis'}</p>
      <p className="helper">See the analysis and guidance for children on the right.</p>
    </section>
    <details className="scope-details"><summary>How the demo learns</summary><p className="helper">One parent-labeled face example is stored and compared locally using LBPH. Matching is provisional and does not establish friendly intent. Stop and Reset keep the example; Delete removes it. The saved photo includes the camera background.</p></details>
    <div className="simulation-session"><strong>{m.status?.diagnostics.assessed_frames ?? '—'}</strong><small>Frames assessed on this Mac<br/>Webcam · {m.camera}</small></div>
  </aside>;
}

function ToolPanel({model: m, actions: a}) {
  return <section className="tool-panel panel" id="tool-panel" role="dialog" aria-modal="false" aria-labelledby="tool-title">
    <div className="tool-heading"><h2 id="tool-title">Diagnostics</h2><button className="close-button" aria-label="Close panel" onClick={a.closePanel}>×</button></div>
      <dl><dt>Source mode</dt><dd>{'Laptop webcam'}</dd>
        <dt>Camera release confirmed</dt><dd>{String(m.status?.release_completed ?? 'Unavailable')}</dd>
        <dt>Vision asset SHA-256</dt><dd>{m.status?.diagnostics.vision_hash || 'Unavailable'}</dd>
        <dt>Configured Qwen / digest</dt><dd>{m.status?.diagnostics.configured_qwen || 'Unavailable'} / {m.status?.diagnostics.configured_digest || 'Unavailable'}</dd>
        <dt>Current frame inference</dt><dd>{m.frame ? `${m.frame.inference_ms.toFixed(2)} ms` : 'Unavailable'}</dd>
        <dt>Assessed frames this session</dt><dd>{m.status?.diagnostics.assessed_frames ?? 'Unavailable'}</dd>
        <dt>Scene feature models / state</dt><dd><pre>{JSON.stringify(m.status?.diagnostics.scene_features || {}, null, 2)}</pre></dd>
        <dt>Last live response</dt><dd><pre>{JSON.stringify(m.status?.diagnostics.last_response || 'Unavailable', null, 2)}</pre></dd>
      </dl><button className="small-button" disabled={!m.status} onClick={a.downloadEvidence}>Download runtime evidence</button><p className="helper">Current service observations only; no camera images. Configured identity does not prove runtime availability. Offline acceptance is pending.</p>
  </section>;
}


export default function ConsoleView({ model: m, actions: a }) {
  return <main className="console-shell">
    <header className="app-header">
      <div className="brand"><Icon type="brand" className="brand-symbol"/><div><strong>DoorSense</strong><span>Entrance · indoor console</span></div></div>
      <nav className="header-navigation" aria-label="Console navigation">{(m.status?.demo_mode === 'face_enrollment' ? ['overview'] : ['overview', 'events']).map(view => <button key={view} className={`nav-item ${m.view === view ? 'active' : ''}`} aria-current={m.view === view ? 'page' : undefined} onClick={() => a.setView(view)}><Icon type={view}/>{view === 'overview' ? 'Overview' : 'Events'}</button>)}</nav>
      <div className="toolbar" role="group" aria-label="Console controls">
        <div className="capture-controls"><button className="primary" aria-label="Start monitoring" title="Start monitoring" disabled={m.busy || !m.status || !['paused', 'unavailable'].includes(m.camera) || !m.status.release_completed} onClick={() => a.control('start')}>Start</button>
          <button aria-label="Stop monitoring" title="Stop monitoring" disabled={m.busy || !m.status || m.camera === 'paused'} onClick={() => a.control('stop')}>Stop</button></div>
        {m.status?.recording && <button disabled={m.busy} onClick={a.stopRecording}>Stop & save clip</button>}
        <button onClick={a.toggleFullscreen}>{m.fullscreen ? 'Exit fullscreen' : 'Fullscreen'}</button>
        <button className="tool-trigger" aria-controls="tool-panel" aria-expanded={m.panel === 'diagnostics'} onClick={event => a.togglePanel('diagnostics', event.currentTarget)}>Diagnostics</button>
        <button className="reset-session" disabled={m.busy || !m.status} title="Stops capture and clears the active session; keeps saved history and media" onClick={a.resetSession}>Reset session</button>
      </div>
    </header>

    {m.status?.event && <div className={`active-alert ${m.status.event.severity}`} role="status"><span className="alert-symbol" aria-hidden="true">{m.status.event.severity === 'urgent' ? '!' : '△'}</span><div className="alert-message"><div className="alert-heading"><span className="alert-level">{m.status.event.severity === 'urgent' ? 'Active urgent review' : 'Door activity needs review'}</span><span className="alert-provenance">{m.status.event.facts.some(fact => fact.source === 'simulated_sensor') ? m.status.event.facts.some(fact => fact.source === 'laptop_webcam') ? 'Webcam + simulated sensors' : 'Simulated sensor inputs' : 'Webcam evidence'}</span></div><strong>{m.simulation?.contact?.kind === 'contact_open' ? 'Step back from the doorway and get a parent.' : m.simulation?.contact?.kind === 'contact_closed' ? 'Keep the door closed. Ask a parent before opening.' : 'Ask a parent. Check the door before approaching.'}</strong><span className="alert-reason">{m.status.event.rule_reason}</span><small>{m.status.event.acknowledged_at ? 'Acknowledged' : 'Awaiting acknowledgement'} · Webcam {m.camera} · {Math.max(0, Math.ceil((Date.parse(m.status.event.expires_at)-Date.now())/1000))}s until alert expiry</small></div><button className="small-button" onClick={a.openActiveEvent}>View active event</button></div>}
    {m.status?.media_error && <div className="error" role="status">{m.status.media_error}</div>}
    {m.status?.storage_error && <div className="error" role="status">{m.status.storage_error}</div>}
    {m.error && <div className="error" role="status">{m.error}</div>}
    <div className={`workspace ${m.view === 'events' ? 'history-workspace' : ''}`}>
      {m.view === 'overview' ? <><SimulationControls model={m} actions={a}/><div className="overview"><LiveView model={m}/><Assessment model={m} actions={a}/></div></> : <Events model={m} actions={a}/>}
    </div>
    {m.media && <MediaViewer media={m.media} close={a.closeMedia}/>}
    {m.panel === 'diagnostics' && <ToolPanel model={m} actions={a}/>}
  </main>;
}
