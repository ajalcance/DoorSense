// Evidence interpretation with frame-bound local appearance matching; no intent probability.
// Qwen responses retain their independent, validated source labels.
export function visitAnalysis(m) {
  if (m.status?.demo_mode === 'face_enrollment' && !m.selectedEvent) return faceDemoAnalysis(m);
  const event = m.selected || m.status?.event;
  const simulation = m.simulation;
  const confirmation = m.status?.confirmation || m.confirmation;
  const currentSnapshot = !!m.frame && confirmation?.sequence === m.frame.sequence &&
    confirmation?.captured_at === m.frame.captured_at;
  const recognition = m.frame?.recognition;
  const familyMatch = recognition?.state === 'matched' && recognition.category === 'Family member' &&
    recognition.sequence === m.frame?.sequence && recognition.captured_at === m.frame?.captured_at;
  const visitor = m.selectedEvent ? 'Not established by this saved event' : recognition ? `${familyMatch ? 'Family member' : 'Unknown'} · local appearance match` : confirmation ? `${confirmation.label} · parent-confirmed snapshot` : 'Unknown · identity unverified';
  const evidence = event ? event.facts.map(fact => ({text:fact.text, source:fact.source, time:fact.observed_at})) : [
    ...(m.frame ? [{text:`${m.frame.people.length} ${m.frame.people.length === 1 ? 'person' : 'people'} detected in the current assessed frame.`, source:'laptop_webcam', time:m.frame.captured_at}] : []),
    ...(recognition ? [{text:recognition.message,source:'local_face_match',time:recognition.captured_at}] : []),
    ...(simulation?.contact ? [{text:`Simulated door contact is ${simulation.contact.kind === 'contact_closed' ? 'closed' : 'open'}.`, source:'simulated_sensor', time:simulation.contact.observed_at}] : []),
    ...['bell','impact'].flatMap(kind => {
      const progress = simulation?.progress?.[kind];
      return progress?.count > 0 ? [{text:`${progress.count}/${progress.required} accepted ${kind === 'bell' ? 'bells' : 'closed-door impacts'} in the current rule window.`, source:'simulated_sensor'}] : [];
    }),
  ];
  const missing = [];
  if (event) missing.push('Intent and safety are not established by the recorded evidence.');
  if (!event && !m.frame) missing.push('No fresh camera frame is available.');
  if (!event && !simulation) missing.push('Current sensor state is unavailable.');
  if (!event && !simulation?.contact) missing.push('Door contact has not been established.');
  if (!event && !simulation?.camera_evidence?.fresh) missing.push('Combined urgent review needs fresh person evidence.');
  if (recognition) missing.push('One-example appearance matching can miss or falsely match a face; identity and safety are not guaranteed.');
  if (confirmation && !currentSnapshot) missing.push('The confirmed snapshot does not identify the person in later frames.');
  if (event?.rule_id === 'person_closed_door_impacts') missing.push('Person presence does not establish who caused the impacts or their intent.');
  let level='limited', headline='Insufficient current evidence', interpretation='Wait for fresh camera and sensor evidence before interpreting this visit.';
  if (event) {
    level=event.severity; headline=event.severity === 'urgent' ? 'Urgent rule met' : 'Parent review advised';
    interpretation=event.rule_reason;
  } else if (!m.status) {
    interpretation='The local service is unavailable; the current door and camera states are unknown.';
  } else if (!m.status.armed) {
    level='off'; headline='Child safety mode is off'; interpretation='Camera observations remain available. New child activity warnings are disabled.';
  } else if (m.frame && simulation) {
    const activity=simulation.progress?.bell?.count > 0 || simulation.progress?.impact?.count > 0;
    if (activity && !(familyMatch || (!recognition && currentSnapshot && confirmation?.label === 'Family member'))) {
      level='advisory'; headline='Parent review advised';
      interpretation='Door activity is present, but the current visitor is unidentified. Ask a parent to check. This advisory is separate from a triggered activity alert.';
    } else {
      level='monitoring'; headline=familyMatch ? 'Family member · expected visit' : 'No urgent condition established';
      interpretation=familyMatch ? 'Local appearance matching recognizes the enrolled family example. No concerning activity alert is active.' : currentSnapshot && confirmation?.label === 'Family member' ? 'A parent marked this snapshot as a family member. No configured activity alert is active; this does not establish safety.' : 'The supplied evidence has not met an activity alert condition. Unknown identity alone is not evidence of suspicious intent.';
    }
    if (simulation.progress?.impact?.count >= simulation.progress?.impact?.required && !simulation.camera_evidence?.fresh) {
      level='limited'; headline='Sensor activity · camera corroboration missing';
      interpretation='Repeated impacts are recorded, but fresh person evidence is missing. A combined urgent condition has not been established.';
    }
  }
  const door=simulation?.contact?.kind;
  const nextStep=m.selectedEvent ? 'Review the saved facts and timestamps; they describe a past event.' :
    door === 'contact_open' ? 'Step back from the doorway and get a parent.' :
    level === 'off' ? 'A parent can enable Child safety mode when needed.' :
    door === 'contact_closed' ? 'Keep the door closed. Ask a parent before opening.' : 'Ask a parent to check the door before approaching.';
  return {level,headline,interpretation,visitor,evidence,missing,nextStep,
    match:recognition && !m.selectedEvent ? recognition.distance == null ? recognition.message : `Distance ${recognition.distance.toFixed(2)} · threshold ${recognition.threshold} · lower is closer` : null,
    probability:'Not estimated · no calibrated intent or safety probability',
    historical:!!m.selectedEvent};
}

function faceDemoAnalysis(m) {
  const recognition = m.frame?.recognition;
  const current = recognition && recognition.sequence === m.frame.sequence && recognition.captured_at === m.frame.captured_at;
  const faceVisible = m.frame?.people?.length === 1 && m.frame?.features?.face?.state === 'available';
  const family = current && faceVisible && recognition.state === 'matched' && recognition.category === 'Family member';
  const assessed = current && faceVisible && ['matched','unmatched','no_reference'].includes(recognition.state);
  const guidanceEnabled = !!m.status?.armed;
  const reason = !current ? 'Waiting for a fresh camera assessment.' : recognition.state === 'reenroll' ? recognition.message : !faceVisible || recognition.state === 'limited' ? recognition.message : recognition.state === 'no_reference' ? 'No family face is enrolled yet.' : family ? `Face distance ${recognition.distance.toFixed(2)} is within the ${recognition.threshold} match threshold.` : `Face distance ${recognition.distance.toFixed(2)} exceeds the ${recognition.threshold} match threshold. Try the same frontal pose and lighting as your saved example.`;
  return {
    level:family ? 'monitoring' : assessed && guidanceEnabled ? 'advisory' : assessed ? 'neutral' : 'limited',
    headline:family ? 'Family member · familiar visitor' : assessed ? 'Unknown visitor' : 'Waiting for a clear face',
    interpretation:family ? 'This face matches the family example learned on this Mac.' : assessed ? 'No family match established. Unknown does not mean dangerous.' : 'Look towards the camera so the system can compare a clear face.',
    reason, guidanceEnabled,
    visitor:family ? 'Family member' : 'Unknown',
    match:current ? recognition.distance == null ? recognition.message : `Distance ${recognition.distance.toFixed(2)} · threshold ${recognition.threshold} · lower is closer` : null,
    evidence:(m.frame?.facts || []).map(fact => ({text:fact.text,source:fact.source,time:fact.observed_at})),
    missing:['A familiar face does not establish friendly intent or permission to open.', 'Single-example appearance matching can produce false or missed matches.'],
    nextStep:!guidanceEnabled ? 'Child safety mode is off. Recognition and learning remain active.' : family ? 'This looks like a familiar family visitor. Ask your parent before opening the door.' : 'Keep the door closed and get your parent to check who is there.',
    banner:!guidanceEnabled ? 'Child safety mode off · recognition only' : family ? 'Familiar visitor · ask a parent before opening' : assessed ? 'Unknown visitor · keep the door closed and get a parent' : 'Face unclear · keep the door closed and ask a parent',
    probability:'Not estimated · no calibrated intent or safety probability', historical:false,
  };
}
