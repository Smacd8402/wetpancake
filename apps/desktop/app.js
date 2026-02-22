const API_BASE = "http://127.0.0.1:8000";

const idleView = document.getElementById("idle-view");
const inCallView = document.getElementById("in-call-view");
const scorecardView = document.getElementById("scorecard-view");

const startCallBtn = document.getElementById("start-call-btn");
const holdReleaseBtn = document.getElementById("hold-release-btn");
const endCallBtn = document.getElementById("end-call-btn");
const restartBtn = document.getElementById("restart-btn");

const idleError = document.getElementById("idle-error");
const callError = document.getElementById("call-error");
const inCallStatus = document.getElementById("in-call-status");
const transcriptList = document.getElementById("transcript-list");

const closeAttempt = document.getElementById("close-attempt");
const valueStatement = document.getElementById("value-statement");
const objectionResolved = document.getElementById("objection-resolved");

const scoreTotal = document.getElementById("score-total");
const scoreDimensions = document.getElementById("score-dimensions");
const scoreMisses = document.getElementById("score-misses");
const scoreActual = document.getElementById("score-actual");
const scoreStronger = document.getElementById("score-stronger");

const state = {
  sessionId: "",
  trust: 0.4,
  resistance: 0.6,
  isRecording: false,
  isProcessing: false,
  transcript: [],
  mediaRecorder: null,
  mediaStream: null,
  chunks: [],
};

function showError(node, message) {
  node.textContent = message;
  node.classList.remove("hidden");
}

function clearError(node) {
  node.textContent = "";
  node.classList.add("hidden");
}

function setView(name) {
  idleView.classList.toggle("hidden", name !== "idle");
  inCallView.classList.toggle("hidden", name !== "in_call");
  scorecardView.classList.toggle("hidden", name !== "post_call");
}

function pushTranscript(speaker, text) {
  const turn = { speaker, text, ts: new Date().toISOString() };
  state.transcript.push(turn);
  const li = document.createElement("li");
  li.innerHTML = `<strong>${speaker}:</strong> ${text}`;
  transcriptList.appendChild(li);
}

async function createSession() {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration_minutes: 8 }),
  });
  if (!response.ok) {
    throw new Error(`Failed creating session (${response.status})`);
  }
  return response.json();
}

async function transcribeAudio(audioBlob) {
  const form = new FormData();
  form.append("audio", audioBlob, "turn.wav");
  const response = await fetch(`${API_BASE}/stt/transcribe`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error(`Failed transcribing audio (${response.status})`);
  }
  const body = await response.json();
  return body.text || "";
}

async function generateDialogueTurn(traineeText) {
  const response = await fetch(`${API_BASE}/dialogue/turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trust: state.trust,
      resistance: state.resistance,
      trainee_text: traineeText,
      primary_objection: "busy",
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed dialogue turn (${response.status})`);
  }
  return response.json();
}

async function synthesizeSpeech(text) {
  const response = await fetch(`${API_BASE}/tts/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    throw new Error(`Failed speech synthesis (${response.status})`);
  }
  return response.arrayBuffer();
}

async function scoreSession() {
  const response = await fetch(`${API_BASE}/sessions/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      transcript: state.transcript,
      outcomes: {
        close_attempt: closeAttempt.checked,
        value_statement: valueStatement.checked,
        objection_resolved: objectionResolved.checked,
      },
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed session scoring (${response.status})`);
  }
  return response.json();
}

function beginRecording() {
  if (state.isProcessing || state.isRecording) {
    return;
  }
  state.isRecording = true;
  holdReleaseBtn.textContent = "Release To Send";
  inCallStatus.textContent = "Listening...";
}

async function startRecording() {
  beginRecording();
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      return;
    }
    state.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.mediaRecorder = new MediaRecorder(state.mediaStream, { mimeType: "audio/webm" });
    state.chunks = [];
    state.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        state.chunks.push(event.data);
      }
    };
    state.mediaRecorder.start();
  } catch (_err) {
    // Fallback to synthetic audio if mic is unavailable.
    state.mediaRecorder = null;
    state.mediaStream = null;
    state.chunks = [];
  }
}

async function stopRecording() {
  if (!state.isRecording || state.isProcessing) {
    return;
  }
  state.isRecording = false;
  state.isProcessing = true;
  holdReleaseBtn.textContent = "Hold To Talk";
  inCallStatus.textContent = "Processing turn...";
  clearError(callError);

  try {
    let audioBlob = new Blob(["fallback"], { type: "audio/webm" });
    if (state.mediaRecorder && state.mediaRecorder.state !== "inactive") {
      await new Promise((resolve) => {
        state.mediaRecorder.onstop = resolve;
        state.mediaRecorder.stop();
      });
      if (state.chunks.length > 0) {
        audioBlob = new Blob(state.chunks, { type: "audio/webm" });
      }
    }
    if (state.mediaStream) {
      state.mediaStream.getTracks().forEach((track) => track.stop());
    }
    state.mediaRecorder = null;
    state.mediaStream = null;
    state.chunks = [];

    const traineeText = await transcribeAudio(audioBlob);
    pushTranscript("trainee", traineeText || "[transcript_pending]");

    const dialogue = await generateDialogueTurn(traineeText || "[transcript_pending]");
    state.trust = dialogue.trust;
    state.resistance = dialogue.resistance;
    pushTranscript("prospect", dialogue.text);

    const wavBytes = await synthesizeSpeech(dialogue.text);
    const blob = new Blob([wavBytes], { type: "audio/wav" });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    try {
      await audio.play();
    } catch (_err) {
      // Audio output is optional for smoke validation.
    } finally {
      URL.revokeObjectURL(url);
    }
    inCallStatus.textContent = "Live prospect simulation is active.";
  } catch (err) {
    showError(callError, String(err instanceof Error ? err.message : err));
    inCallStatus.textContent = "Live prospect simulation is active.";
  } finally {
    state.isProcessing = false;
  }
}

function resetCallForm() {
  transcriptList.innerHTML = "";
  closeAttempt.checked = false;
  valueStatement.checked = false;
  objectionResolved.checked = false;
}

function fillScorecard(score) {
  scoreTotal.textContent = `Total: ${score.total_score}`;
  scoreDimensions.innerHTML = "";
  Object.entries(score.dimensions || {}).forEach(([name, value]) => {
    const li = document.createElement("li");
    li.textContent = `${name}: ${value}`;
    scoreDimensions.appendChild(li);
  });
  scoreMisses.innerHTML = "";
  (score.misses || []).forEach((miss) => {
    const li = document.createElement("li");
    li.textContent = miss;
    scoreMisses.appendChild(li);
  });
  const replacement = score.replacement_phrasing || { actual: "", stronger: "" };
  scoreActual.innerHTML = `<strong>Actual:</strong> ${replacement.actual}`;
  scoreStronger.innerHTML = `<strong>Stronger:</strong> ${replacement.stronger}`;
}

async function onStartCall() {
  clearError(idleError);
  try {
    const session = await createSession();
    state.sessionId = session.session_id;
    state.trust = 0.4;
    state.resistance = 0.6;
    state.transcript = [];
    resetCallForm();
    setView("in_call");
  } catch (err) {
    showError(idleError, String(err instanceof Error ? err.message : err));
  }
}

async function onEndCall() {
  if (!state.sessionId) {
    showError(callError, "No active session");
    return;
  }
  clearError(callError);
  try {
    const score = await scoreSession();
    fillScorecard(score);
    setView("post_call");
  } catch (err) {
    showError(callError, String(err instanceof Error ? err.message : err));
  }
}

function onRestart() {
  state.sessionId = "";
  state.transcript = [];
  setView("idle");
}

startCallBtn.addEventListener("click", () => {
  void onStartCall();
});
holdReleaseBtn.addEventListener("mousedown", () => {
  void startRecording();
});
holdReleaseBtn.addEventListener("mouseup", () => {
  void stopRecording();
});
holdReleaseBtn.addEventListener("mouseleave", () => {
  if (state.isRecording) {
    void stopRecording();
  }
});
holdReleaseBtn.addEventListener("touchstart", () => {
  void startRecording();
});
holdReleaseBtn.addEventListener("touchend", () => {
  void stopRecording();
});
endCallBtn.addEventListener("click", () => {
  void onEndCall();
});
restartBtn.addEventListener("click", onRestart);
