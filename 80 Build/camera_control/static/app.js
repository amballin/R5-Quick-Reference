const token = document.querySelector('meta[name="camera-lab-token"]').content;
const requestedProfileName = new URLSearchParams(window.location.search).get("profile");

const elements = {
  backendBadge: document.querySelector("#backend-badge"),
  projectContextBadge: document.querySelector("#project-context-badge"),
  cameraLabVersion: document.querySelector("#camera-lab-version"),
  cameraLabSourceHash: document.querySelector("#camera-lab-source-hash"),
  backendSwitchButton: document.querySelector("#backend-switch-button"),
  physicalWriteModeButton: document.querySelector("#physical-write-mode-button"),
  headerSafetyBadge: document.querySelector("#header-safety-badge"),
  stopCameraLabButton: document.querySelector("#stop-camera-lab-button"),
  statusDot: document.querySelector("#status-dot"),
  connectionTitle: document.querySelector("#connection-title"),
  connectionMessage: document.querySelector("#connection-message"),
  discoverButton: document.querySelector("#discover-button"),
  connectButton: document.querySelector("#connect-button"),
  scanButton: document.querySelector("#scan-button"),
  disconnectButton: document.querySelector("#disconnect-button"),
  refreshButton: document.querySelector("#refresh-button"),
  message: document.querySelector("#message"),
  cameraChoiceCard: document.querySelector("#camera-choice-card"),
  cameraChoices: document.querySelector("#camera-choices"),
  cameraModel: document.querySelector("#camera-model"),
  cameraBody: document.querySelector("#camera-body"),
  cameraFirmware: document.querySelector("#camera-firmware"),
  cameraBattery: document.querySelector("#camera-battery"),
  cameraLens: document.querySelector("#camera-lens"),
  sdkMode: document.querySelector("#sdk-mode"),
  sdkVersion: document.querySelector("#sdk-version"),
  sdkPath: document.querySelector("#sdk-path"),
  sdkAccess: document.querySelector("#sdk-access"),
  simulationPanel: document.querySelector("#simulation-panel"),
  scenarioSelect: document.querySelector("#scenario-select"),
  applyScenarioButton: document.querySelector("#apply-scenario-button"),
  simulateDisconnectButton: document.querySelector("#simulate-disconnect-button"),
  eventLog: document.querySelector("#event-log"),
  connectStep: document.querySelector("#connect-step"),
  discoverStep: document.querySelector("#discover-step"),
  compareStep: document.querySelector("#compare-step"),
  configureStep: document.querySelector("#configure-step"),
  capabilityPanel: document.querySelector("#capability-panel"),
  capabilitySummary: document.querySelector("#capability-summary"),
  capabilityRows: document.querySelector("#capability-rows"),
  coverageReadableSummary: document.querySelector("#coverage-readable-summary"),
  coverageReadable: document.querySelector("#coverage-readable"),
  coverageConditionalSummary: document.querySelector("#coverage-conditional-summary"),
  coverageConditional: document.querySelector("#coverage-conditional"),
  coverageUnmappedSummary: document.querySelector("#coverage-unmapped-summary"),
  coverageUnmapped: document.querySelector("#coverage-unmapped"),
  cxSlotCards: document.querySelector("#cx-slot-cards"),
  comparisonPanel: document.querySelector("#comparison-panel"),
  profileSelect: document.querySelector("#profile-select"),
  compareButton: document.querySelector("#compare-button"),
  equipmentContext: document.querySelector("#equipment-context"),
  equipmentContextSource: document.querySelector("#equipment-context-source"),
  lensChoiceSelect: document.querySelector("#lens-choice-select"),
  lensChoiceGuidance: document.querySelector("#lens-choice-guidance"),
  isModeControl: document.querySelector("#is-mode-control"),
  isModeSelect: document.querySelector("#is-mode-select"),
  isModeGuidance: document.querySelector("#is-mode-guidance"),
  equipmentInteractionList: document.querySelector("#equipment-interaction-list"),
  comparisonResults: document.querySelector("#comparison-results"),
  comparisonSummary: document.querySelector("#comparison-summary"),
  comparisonOrder: document.querySelector("#comparison-order"),
  comparisonSafetyBadge: document.querySelector("#comparison-safety-badge"),
  prepareGuardedButton: document.querySelector("#prepare-guarded-button"),
  checklistRescanButton: document.querySelector("#checklist-rescan-button"),
  checklistClearButton: document.querySelector("#checklist-clear-button"),
  checklistSdkCount: document.querySelector("#checklist-sdk-count"),
  checklistManualCount: document.querySelector("#checklist-manual-count"),
  checklistUnresolvedCount: document.querySelector("#checklist-unresolved-count"),
  checklistBlockedCount: document.querySelector("#checklist-blocked-count"),
  checklistResult: document.querySelector("#checklist-result"),
  checklistLastScan: document.querySelector("#checklist-last-scan"),
  cardFindingSection: document.querySelector("#card-finding-section"),
  cardFindingHeading: document.querySelector("#card-finding-heading"),
  cardFindingDescription: document.querySelector("#card-finding-description"),
  additionalFindingSection: document.querySelector("#additional-finding-section"),
  cardFindings: document.querySelector("#card-findings"),
  additionalFindings: document.querySelector("#additional-findings"),
  returnToTop: document.querySelector("#return-to-top"),
  recoveryDialog: document.querySelector("#recovery-dialog"),
  recoveryDetail: document.querySelector("#recovery-detail"),
  recoveryRetryButton: document.querySelector("#recovery-retry-button"),
  backendSwitchDialog: document.querySelector("#backend-switch-dialog"),
  backendSwitchTitle: document.querySelector("#backend-switch-title"),
  backendSwitchMessage: document.querySelector("#backend-switch-message"),
  backendSwitchConfirm: document.querySelector("#backend-switch-confirm"),
  physicalWriteModeDialog: document.querySelector("#physical-write-mode-dialog"),
  physicalWriteModeTitle: document.querySelector("#physical-write-mode-title"),
  physicalWriteModeMessage: document.querySelector("#physical-write-mode-message"),
  physicalWriteModeSafety: document.querySelector("#physical-write-mode-safety"),
  physicalWriteModeConfirm: document.querySelector("#physical-write-mode-confirm"),
  guardedRunPanel: document.querySelector("#guarded-run-panel"),
  applyProfileTitle: document.querySelector("#apply-profile-title"),
  applyProfileIntro: document.querySelector("#apply-profile-intro"),
  applyReviewMessage: document.querySelector("#apply-review-message"),
  applyResult: document.querySelector("#apply-result"),
  applyResultTitle: document.querySelector("#apply-result-title"),
  applyResultSummary: document.querySelector("#apply-result-summary"),
  applyResultDetails: document.querySelector("#apply-result-details"),
  guardedPreflightForm: document.querySelector("#guarded-preflight-form"),
  guardedCameraIdentity: document.querySelector("#guarded-camera-identity"),
  guardedCameraFirmware: document.querySelector("#guarded-camera-firmware"),
  guardedCameraPower: document.querySelector("#guarded-camera-power"),
  guardedStillMovie: document.querySelector("#guarded-still-movie"),
  guardedCurrentMode: document.querySelector("#guarded-current-mode"),
  guardedLens: document.querySelector("#guarded-lens"),
  guardedLensSource: document.querySelector("#guarded-lens-source"),
  guardedFlash: document.querySelector("#guarded-flash"),
  guardedCards: document.querySelector("#guarded-cards"),
  guardedBackupFilename: document.querySelector("#guarded-backup-filename"),
  guardedSetupEssentialsConfirmed: document.querySelector("#guarded-setup-essentials-confirmed"),
  guardedAppsClosed: document.querySelector("#guarded-apps-closed"),
  guardedBackupConfirmed: document.querySelector("#guarded-backup-confirmed"),
  guardedPlanButton: document.querySelector("#guarded-plan-button"),
  guardedResumeButton: document.querySelector("#guarded-resume-button"),
  guardedPreview: document.querySelector("#guarded-preview"),
  guardedStatus: document.querySelector("#guarded-status"),
  guardedProgressCount: document.querySelector("#guarded-progress-count"),
  guardedProgressBar: document.querySelector("#guarded-progress-bar"),
  guardedClassificationCounts: document.querySelector("#guarded-classification-counts"),
  guardedFailure: document.querySelector("#guarded-failure"),
  guardedActiveWorkspace: document.querySelector("#guarded-active-workspace"),
  guardedCurrentStep: document.querySelector("#guarded-current-step"),
  guardedStepTitle: document.querySelector("#guarded-step-title"),
  guardedStepSettings: document.querySelector("#guarded-step-settings"),
  guardedStepDetail: document.querySelector("#guarded-step-detail"),
  guardedStepRoute: document.querySelector("#guarded-step-route"),
  guardedConfirmButton: document.querySelector("#guarded-confirm-button"),
  guardedNextButton: document.querySelector("#guarded-next-button"),
  guardedAbortButton: document.querySelector("#guarded-abort-button"),
  guardedPlanDetails: document.querySelector("#guarded-plan-details"),
  guardedPlanSteps: document.querySelector("#guarded-plan-steps"),
  guardedConfirmDialog: document.querySelector("#guarded-confirm-dialog"),
  guardedConfirmExecute: document.querySelector("#guarded-confirm-execute"),
  guardedConfirmMessage: document.querySelector("#guarded-confirm-message"),
  guardedConfirmSafety: document.querySelector("#guarded-confirm-safety"),
  writeQualificationControls: document.querySelector("#write-qualification-controls"),
  writeQualificationNeeded: document.querySelector("#write-qualification-needed"),
  writeQualificationProperty: document.querySelector("#write-qualification-property"),
  writeQualificationTarget: document.querySelector("#write-qualification-target"),
  writeQualificationPrepare: document.querySelector("#write-qualification-prepare"),
  writeQualificationPreview: document.querySelector("#write-qualification-preview"),
  writeQualificationSummary: document.querySelector("#write-qualification-summary"),
  writeQualificationResult: document.querySelector("#write-qualification-result"),
  writeQualificationConfirm: document.querySelector("#write-qualification-confirm"),
  writeQualificationExecute: document.querySelector("#write-qualification-execute"),
  writeQualificationDialog: document.querySelector("#write-qualification-dialog"),
  writeQualificationDialogSummary: document.querySelector("#write-qualification-dialog-summary"),
  writeQualificationDialogConfirm: document.querySelector("#write-qualification-dialog-confirm"),
};

let statusState = null;
let comparisonState = null;
let selectedCameraIndex = null;
let requestPending = false;
let cameraLabStopped = false;
let statusPollId = null;
let contextSelections = {};
let equipmentSelection = { choiceKey: "", isMode: "" };
let requestedBackendMode = null;
let requestedPhysicalWriteMode = null;
let guardedRunState = null;
let writeQualificationState = null;
let writeQualificationCandidates = [];
const checklistStorageKey = "camera-lab-phase1-checklist-v1";
let checklistState = loadChecklistState();

function loadChecklistState() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(checklistStorageKey) || "{}");
    return parsed && parsed.version === 1 && parsed.profiles ? parsed : { version: 1, profiles: {} };
  } catch (_error) {
    return { version: 1, profiles: {} };
  }
}

function saveChecklistState() {
  try {
    window.localStorage.setItem(checklistStorageKey, JSON.stringify(checklistState));
  } catch (_error) {
    setMessage("Checklist progress could not be saved in this browser.", "info");
  }
}

function cameraContextKey() {
  const camera = statusState?.camera || {};
  return [camera.product_name || "EOS R5", camera.body_id || "unknown-body", camera.firmware_version || "unknown-firmware"].join("|");
}

function activeChecklistRecord(create = false) {
  if (!comparisonState) return null;
  const profileName = comparisonState.profile.name || elements.profileSelect.value;
  const equipment = comparisonState.equipment || {};
  const equipmentKey = [
    equipment.selected_lens_id || "unresolved-lens",
    equipment.selected_accessory_id || "no-accessory",
    equipment.stabilization?.selected_mode || equipment.stabilization?.control || "unresolved-is",
  ].join("|");
  const recordKey = `${cameraContextKey()}|${profileName}|${equipmentKey}`;
  if (!checklistState.profiles[recordKey] && create) {
    checklistState.profiles[recordKey] = { profile: profileName, camera_context: cameraContextKey(), equipment_context: equipmentKey, confirmations: {}, last_scan_at: null };
  }
  return checklistState.profiles[recordKey] || null;
}

function checklistFindingKey(finding) {
  const identity = finding.path || finding.key || (finding.items || []).map((item) => item.path).join("+") || finding.label;
  const selectedContext = contextPromptForFinding(finding)?.selected_target || "no-context-selected";
  return `${identity}|${finding.expected}|${selectedContext}`;
}

function isManualChecklistFinding(finding) {
  const prompt = contextPromptForFinding(finding);
  if (finding.status === "conditional" && prompt && !prompt.selected) return false;
  return ["manual_confirmation_needed", "conditional", "unreadable"].includes(finding.status);
}

function contextPromptForFinding(finding) {
  if (finding.context_prompt) return finding.context_prompt;
  return (finding.context_prompts || [])[0] || null;
}

function manualConfirmation(finding) {
  return activeChecklistRecord()?.confirmations?.[checklistFindingKey(finding)]
    || finding.shared_manual_confirmation
    || null;
}

function setManualConfirmation(finding, confirmed) {
  const record = activeChecklistRecord(true);
  const key = checklistFindingKey(finding);
  if (confirmed) {
    record.confirmations[key] = {
      evidence_method: "manual_user_confirmed",
      confirmed_at: new Date().toISOString(),
      expected: finding.expected,
      source: "this_card",
    };
  } else {
    delete record.confirmations[key];
  }
  saveChecklistState();
}

function sharedManualContext() {
  const key = guardedPreflightStorageKey();
  if (!key) return null;
  try {
    const saved = JSON.parse(window.sessionStorage.getItem(key) || "null");
    if (!saved
      || saved.still_movie_context !== "still"
      || !saved.flash
      || !saved.cards
      || saved.applications_closed !== true
      || saved.camera_backup_confirmed !== true) return null;
    return {
      still_movie_context: saved.still_movie_context,
      flash: saved.flash,
      cards: saved.cards,
      selected_lens_id: comparisonState?.equipment?.selected_lens_id || "",
      selected_accessory_id: comparisonState?.equipment?.selected_accessory_id || "",
      selected_is_mode: comparisonState?.equipment?.stabilization?.selected_mode || "",
    };
  } catch (_error) {
    return null;
  }
}

function sharedConfirmationItems(finding) {
  return (finding.items?.length ? finding.items : [finding])
    .filter((item) => item.path && item.expected)
    .map((item) => ({path: item.path, target: item.expected}));
}

async function revokeSharedManualConfirmation(finding) {
  const manualContext = sharedManualContext();
  if (!finding.shared_manual_confirmation || !manualContext) return;
  await request("/api/camera-control/manual-confirmations/revoke", {
    method: "POST",
    body: JSON.stringify({
      confirmations: sharedConfirmationItems(finding),
      manual_context: manualContext,
    }),
  });
}

function allComparisonFindings() {
  if (!comparisonState) return [];
  return [...comparisonState.card_findings, ...comparisonState.additional_findings];
}

function checklistCounts() {
  const counts = { sdk: 0, manual: 0, unresolved: 0, blocked: 0 };
  for (const finding of allComparisonFindings()) {
    if (["match", "equivalent"].includes(finding.status)) {
      counts.sdk += 1;
    } else if (finding.status === "blocked") {
      counts.blocked += 1;
    } else if (isManualChecklistFinding(finding) && manualConfirmation(finding)) {
      counts.manual += 1;
    } else if (finding.status !== "not_applicable") {
      counts.unresolved += 1;
    }
  }
  return counts;
}

function renderChecklistSummary() {
  const counts = checklistCounts();
  elements.checklistSdkCount.textContent = counts.sdk;
  elements.checklistManualCount.textContent = counts.manual;
  elements.checklistUnresolvedCount.textContent = counts.unresolved;
  elements.checklistBlockedCount.textContent = counts.blocked;
  const complete = counts.unresolved === 0 && counts.blocked === 0;
  elements.checklistResult.className = `checklist-result ${complete ? "complete" : "incomplete"}`;
  elements.checklistResult.textContent = complete
    ? `Review complete: ${counts.sdk} camera-verified and ${counts.manual} manually confirmed findings.`
    : `Review incomplete: ${counts.unresolved} unresolved and ${counts.blocked} blocked findings remain.`;
  const record = activeChecklistRecord();
  elements.checklistLastScan.textContent = record?.last_scan_at
    ? `Last full camera scan: ${new Date(record.last_scan_at).toLocaleString()}`
    : "No full camera scan has been recorded for this checklist.";
}

async function request(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.method === "POST") {
    headers["Content-Type"] = "application/json";
    headers["X-Camera-Lab-Token"] = token;
  }
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json();
  if (!response.ok || payload.ok === false) {
    const error = new Error(payload.error?.message || `Request failed (${response.status})`);
    error.payload = payload;
    throw error;
  }
  return payload;
}

function valueOrUnavailable(value) {
  return value === null || value === undefined || value === "" ? "Unavailable" : String(value);
}

function powerStatus(value) {
  if (value === -1 || value === 0xffffffff) return "External power";
  if (value === 0xfffffffe) return "Unknown";
  return valueOrUnavailable(value);
}

function setMessage(text, kind = "error") {
  elements.message.textContent = text || "";
  elements.message.className = `message ${kind}`;
  elements.message.hidden = !text;
}

function showRecoveryInstructions(detail) {
  elements.recoveryDetail.textContent = detail || "Camera Lab could not restore the camera session.";
  if (typeof elements.recoveryDialog.showModal === "function") {
    elements.recoveryDialog.showModal();
  } else {
    elements.recoveryDialog.setAttribute("open", "");
  }
}

function setBusy(busy) {
  requestPending = busy;
  elements.discoverButton.disabled = busy || Boolean(statusState?.connected);
  elements.connectButton.disabled = busy || Boolean(statusState?.connected);
  elements.scanButton.disabled = busy || (!Boolean(statusState?.connected) && !Boolean(statusState?.reconnect_available));
  elements.compareButton.disabled = busy || (!Boolean(statusState?.connected) && !Boolean(statusState?.reconnect_available)) || !elements.profileSelect.value;
  elements.checklistRescanButton.disabled = busy || (!Boolean(statusState?.connected) && !Boolean(statusState?.reconnect_available));
  elements.checklistClearButton.disabled = busy;
  elements.disconnectButton.disabled = busy;
  elements.refreshButton.disabled = busy;
  elements.applyScenarioButton.disabled = busy;
  elements.simulateDisconnectButton.disabled = busy || !statusState?.connected;
  elements.backendSwitchButton.disabled = busy;
  elements.stopCameraLabButton.disabled = busy;
  elements.prepareGuardedButton.disabled = busy;
  elements.guardedPlanButton.disabled = busy;
  elements.guardedResumeButton.disabled = busy;
  elements.guardedConfirmButton.disabled = busy;
  elements.guardedNextButton.disabled = busy;
  elements.guardedAbortButton.disabled = busy;
  elements.guardedConfirmExecute.disabled = busy;
  elements.writeQualificationPrepare.disabled = busy || !elements.writeQualificationTarget.value;
  elements.writeQualificationConfirm.disabled = busy;
  elements.writeQualificationExecute.disabled = busy;
  elements.writeQualificationDialogConfirm.disabled = busy;
  for (const button of document.querySelectorAll("[data-cx-profile]")) button.disabled = busy;
}

function renderStoppedState() {
  cameraLabStopped = true;
  if (statusPollId !== null) {
    window.clearInterval(statusPollId);
    statusPollId = null;
  }
  requestPending = true;
  statusState = null;
  elements.statusDot.className = "status-dot";
  elements.connectionTitle.textContent = "Camera Lab stopped";
  elements.connectionMessage.textContent = "The camera session and local server closed cleanly. You may close this tab.";
  elements.stopCameraLabButton.disabled = true;
  for (const button of document.querySelectorAll("button")) button.disabled = true;
  setMessage("Camera Lab stopped cleanly. If this tab remains open, close it when ready.", "info");
}

async function stopCameraLab() {
  if (requestPending) return;
  if (!window.confirm("Stop Camera Lab and close the current EOS R5 session?")) return;
  setBusy(true);
  setMessage("Stopping Camera Lab and closing the camera session…", "info");
  try {
    const result = await request("/api/camera-control/shutdown", { method: "POST", body: "{}" });
    if (!result.camera_session_closed) throw new Error("Camera Lab did not confirm that the camera session closed.");
    renderStoppedState();
    window.setTimeout(() => window.close(), 300);
  } catch (error) {
    requestPending = false;
    setBusy(false);
    setMessage(`Camera Lab could not stop cleanly: ${error.message}`);
  }
}

function showBackendSwitchConfirmation() {
  if (requestPending || !statusState) return;
  requestedBackendMode = statusState.backend_mode === "simulated" ? "edsdk" : "simulated";
  const usingSimulator = requestedBackendMode === "simulated";
  elements.backendSwitchTitle.textContent = usingSimulator ? "Use the simulator?" : "Use the physical camera?";
  elements.backendSwitchMessage.textContent = usingSimulator
    ? "Camera Lab will disconnect any physical EOS R5 session and restart in simulated mode. Current camera scans and comparisons will be cleared."
    : "Camera Lab will end the simulated session and restart with Canon EDSDK for a physical EOS R5. Current simulated scans and comparisons will be cleared.";
  elements.backendSwitchConfirm.textContent = usingSimulator ? "Use Simulator" : "Use Camera";
  if (typeof elements.backendSwitchDialog.showModal === "function") {
    elements.backendSwitchDialog.showModal();
  } else {
    elements.backendSwitchDialog.setAttribute("open", "");
  }
}

async function waitForBackendRestart(backend, physicalWriteEnabled = false) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 150));
    try {
      const response = await fetch("/api/camera-control/status", { cache: "no-store" });
      if (!response.ok) continue;
      const payload = await response.json();
      if (payload.backend_mode === backend && payload.physical_write_enabled === physicalWriteEnabled) {
        window.location.reload();
        return;
      }
    } catch (_error) {
      // The loopback server is expected to be briefly unavailable during restart.
    }
  }
  throw new Error("Camera Lab did not return after changing its connection mode. Refresh this page or reopen the app.");
}

async function restartWithSelectedBackend() {
  const backend = requestedBackendMode;
  if (!backend || requestPending) return;
  elements.backendSwitchDialog.close();
  setBusy(true);
  if (statusPollId !== null) {
    window.clearInterval(statusPollId);
    statusPollId = null;
  }
  const label = backend === "simulated" ? "simulator" : "physical-camera mode";
  setMessage(`Closing the current session and restarting Camera Lab in ${label}…`, "info");
  try {
    const result = await request("/api/camera-control/restart-backend", {
      method: "POST",
      body: JSON.stringify({ backend, physical_write_enabled: false }),
    });
    if (!result.restarting || !result.camera_session_closed) {
      throw new Error("Camera Lab did not confirm a safe backend restart.");
    }
    await waitForBackendRestart(backend, false);
  } catch (error) {
    requestedBackendMode = null;
    setBusy(false);
    if (statusPollId === null) statusPollId = window.setInterval(() => refreshStatus({ quiet: true }), 2500);
    setMessage(error.message);
  }
}

function showPhysicalWriteModeConfirmation() {
  if (requestPending || !statusState || statusState.backend_mode !== "edsdk") return;
  requestedPhysicalWriteMode = !statusState.physical_write_enabled;
  elements.physicalWriteModeTitle.textContent = requestedPhysicalWriteMode
    ? "Enable camera changes?"
    : "Return Camera Lab to read-only mode?";
  elements.physicalWriteModeMessage.textContent = requestedPhysicalWriteMode
    ? "Camera Lab will close the current camera session and restart with the explicit physical-write gate. Enabling the gate does not change any camera setting."
    : "Camera Lab will close the current camera session and restart in its ordinary read-only mode.";
  elements.physicalWriteModeSafety.textContent = requestedPhysicalWriteMode
    ? "Camera Lab still shows every proposed change first and requires another confirmation before applying anything."
    : "Any unfinished attempt remains incomplete; no setting is changed while returning to read-only mode.";
  elements.physicalWriteModeConfirm.textContent = requestedPhysicalWriteMode
    ? "Enable camera changes"
    : "Return to read-only";
  elements.physicalWriteModeConfirm.className = requestedPhysicalWriteMode ? "danger" : "primary";
  if (typeof elements.physicalWriteModeDialog.showModal === "function") {
    elements.physicalWriteModeDialog.showModal();
  } else {
    elements.physicalWriteModeDialog.setAttribute("open", "");
  }
}

async function restartWithPhysicalWriteMode() {
  const physicalWriteEnabled = requestedPhysicalWriteMode;
  if (typeof physicalWriteEnabled !== "boolean" || requestPending) return;
  elements.physicalWriteModeDialog.close();
  setBusy(true);
  if (statusPollId !== null) {
    window.clearInterval(statusPollId);
    statusPollId = null;
  }
  setMessage(
    physicalWriteEnabled
      ? "Closing the current session and enabling guarded physical writes…"
      : "Closing the current session and returning Camera Lab to read-only mode…",
    "info"
  );
  try {
    const result = await request("/api/camera-control/restart-backend", {
      method: "POST",
      body: JSON.stringify({backend: "edsdk", physical_write_enabled: physicalWriteEnabled}),
    });
    if (!result.restarting || !result.camera_session_closed
        || result.physical_write_enabled !== physicalWriteEnabled) {
      throw new Error("Camera Lab did not confirm the requested guarded-write restart.");
    }
    await waitForBackendRestart("edsdk", physicalWriteEnabled);
  } catch (error) {
    requestedPhysicalWriteMode = null;
    setBusy(false);
    if (statusPollId === null) statusPollId = window.setInterval(() => refreshStatus({ quiet: true }), 2500);
    setMessage(error.message);
  }
}

function renderStatus(status) {
  statusState = status;
  const connected = Boolean(status.connected);
  const reconnectAvailable = Boolean(status.reconnect_available);
  const app = status.app || {};
  const projectContext = app.project_context || {};
  elements.projectContextBadge.textContent = projectContext.label || "Project context unavailable";
  elements.projectContextBadge.className = `project-context-badge ${projectContext.kind || "unknown"}`;
  elements.projectContextBadge.title = projectContext.branch ? `Git branch: ${projectContext.branch}` : "Git branch unavailable";
  const contextName = app.context_name || (projectContext.kind === "main" ? "Main" : projectContext.kind === "prototype" ? "Prototype" : "Unknown");
  elements.cameraLabVersion.textContent = app.version
    ? `Camera Lab ${app.version} · ${contextName}`
    : "Camera Lab version unavailable";
  elements.cameraLabSourceHash.textContent = app.build ? `Source hash ${app.build}` : "Source hash unavailable";
  elements.backendBadge.textContent = status.backend_mode === "simulated" ? "Simulated camera" : "Canon EDSDK";
  elements.backendBadge.classList.toggle("live", status.backend_mode === "edsdk");
  elements.headerSafetyBadge.textContent = status.backend_mode === "simulated"
    ? "Simulator changes only"
    : status.physical_write_enabled
      ? "Camera changes enabled"
      : "No setting writes";
  elements.backendSwitchButton.textContent = status.backend_mode === "simulated" ? "Use Camera" : "Use Simulator";
  elements.physicalWriteModeButton.hidden = status.backend_mode !== "edsdk";
  elements.physicalWriteModeButton.textContent = status.physical_write_enabled
    ? "Return to read-only"
    : "Enable camera changes";
  elements.statusDot.classList.toggle("connected", connected);
  elements.statusDot.classList.toggle("error", !connected && Boolean(status.last_error));
  elements.connectionTitle.textContent = connected ? "EOS R5 connected" : "Camera not connected";
  elements.connectionMessage.textContent = connected
    ? status.backend_mode === "simulated"
      ? "The simulator is connected. Camera Lab will show every proposed change before applying it."
      : status.physical_write_enabled
        ? "The USB session is open. Camera Lab will show and confirm every change before applying it."
        : "The USB session is open and responding. Camera settings remain unchanged."
    : status.last_error?.message || "Discover a camera, then connect when you are ready.";
  elements.connectButton.hidden = connected || reconnectAvailable;
  elements.scanButton.hidden = !connected && !reconnectAvailable;
  elements.scanButton.textContent = connected ? "Scan capabilities" : "Reconnect and scan";
  elements.disconnectButton.hidden = !connected;
  elements.cameraChoiceCard.hidden = connected || elements.cameraChoices.childElementCount === 0;

  const camera = status.camera || {};
  elements.cameraModel.textContent = valueOrUnavailable(camera.product_name);
  elements.cameraBody.textContent = valueOrUnavailable(camera.body_id);
  elements.cameraFirmware.textContent = valueOrUnavailable(camera.firmware_version);
  elements.cameraBattery.textContent = powerStatus(camera.battery_raw);
  elements.cameraLens.textContent = valueOrUnavailable(camera.lens_name);

  const sdk = status.sdk || {};
  elements.sdkMode.textContent = status.backend_mode === "simulated" ? "Simulation" : "Physical camera";
  elements.sdkVersion.textContent = valueOrUnavailable(sdk.framework_version);
  elements.sdkPath.textContent = valueOrUnavailable(sdk.path);
  elements.sdkAccess.textContent = status.backend_mode === "simulated"
    ? "Simulator profile application"
    : status.physical_write_enabled ? "Camera changes enabled" : "Read-only";
  elements.comparisonSafetyBadge.textContent = status.backend_mode === "simulated"
    ? "Comparison stays read-only"
    : status.physical_write_enabled ? "Changes require review" : "No setting writes";

  elements.simulationPanel.hidden = status.backend_mode !== "simulated";
  const guardedAvailable = status.backend_mode === "simulated" || status.physical_guarded_runs;
  elements.prepareGuardedButton.hidden = !guardedAvailable || !comparisonState;
  elements.writeQualificationControls.hidden = !status.physical_write_qualification;
  if (!guardedAvailable) {
    elements.guardedRunPanel.hidden = true;
  } else if (status.guarded_run && !guardedRunState) {
    elements.guardedRunPanel.hidden = false;
    elements.guardedResumeButton.hidden = false;
    elements.guardedResumeButton.dataset.sessionId = status.guarded_run.session_id;
    elements.guardedResumeButton.textContent = `Resume ${status.guarded_run.status} run`;
  }
  elements.connectStep.classList.toggle("active", !connected);
  elements.discoverStep.classList.toggle("active", connected);
  elements.discoverStep.classList.toggle("locked", !connected);
  elements.compareStep.classList.toggle("locked", !Boolean(status.capabilities));
  elements.configureStep.classList.toggle("locked", !guardedAvailable || (!comparisonState && !status.guarded_run));
  elements.configureStep.classList.toggle("active", Boolean(guardedRunState) || Boolean(status.guarded_run));
  if (status.capabilities) renderCapabilities(status.capabilities);
  if (status.backend_mode === "simulated") {
    const scenarios = status.available_scenarios || {};
    const currentOptions = [...elements.scenarioSelect.options].map((option) => option.value).join("|");
    if (currentOptions !== Object.keys(scenarios).join("|")) {
      elements.scenarioSelect.replaceChildren(
        ...Object.entries(scenarios).map(([value, label]) => {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = label;
          return option;
        })
      );
    }
    elements.scenarioSelect.value = status.simulated_scenario;
  }
  setBusy(requestPending);
}

function capabilityValue(property) {
  if (property.read_status !== "sdk_verified") {
    return `Unavailable${property.read_error === null ? "" : ` (error ${property.read_error})`}`;
  }
  if (property.value_raw === null || property.value_raw === undefined) {
    return property.value_hex ? `0x${property.value_hex}` : "Readable";
  }
  if (property.key === "battery_level") return powerStatus(property.value_raw);
  return String(property.value_raw);
}

function renderCapabilities(capabilities) {
  const properties = capabilities.properties || [];
  const summary = capabilities.summary || {};
  elements.capabilityPanel.hidden = false;
  elements.capabilitySummary.textContent = `${summary.readable || 0} of ${summary.total || properties.length} properties readable; ${summary.descriptors_available || 0} Canon descriptors returned.`;
  elements.capabilityRows.replaceChildren(
    ...properties.map((property) => {
      const row = document.createElement("tr");
      if (property.read_status !== "sdk_verified") row.className = "capability-unavailable";
      const name = document.createElement("th");
      name.scope = "row";
      const label = document.createElement("strong");
      label.textContent = property.label;
      const id = document.createElement("small");
      id.textContent = property.property_id_hex;
      name.append(label, id);
      const readback = document.createElement("td");
      const decoded = document.createElement("strong");
      decoded.textContent = property.value_display || capabilityValue(property);
      const raw = document.createElement("small");
      raw.textContent = property.read_status === "sdk_verified" ? `Raw: ${valueOrUnavailable(property.value_raw)}` : capabilityValue(property);
      readback.append(decoded, raw);
      const mapping = document.createElement("td");
      mapping.textContent = property.profile_paths?.length
        ? property.profile_paths.join(", ")
        : property.capability_classification === "context_only" ? "Camera context" : "Unmapped";
      const descriptor = document.createElement("td");
      descriptor.textContent = property.descriptor_status === "sdk_verified"
        ? valueOrUnavailable(property.descriptor_access)
        : "Unavailable";
      const values = document.createElement("td");
      const allowed = property.allowed_values_raw || [];
      const allowedDisplay = property.allowed_values_display || [];
      values.textContent = allowed.length
        ? `${allowed.slice(0, 6).map((value, index) => `${allowedDisplay[index] || `Raw ${value}`} [${value}]`).join(", ")}${allowed.length > 6 ? ` +${allowed.length - 6} more` : ""}`
        : "None reported";
      const write = document.createElement("td");
      write.textContent = property.write_classification === "machine_local_sdk_written_and_verified"
        ? `Body-scoped verified: ${(property.verified_write_values_raw || []).join(", ")}`
        : "Unverified";
      row.append(name, readback, mapping, descriptor, values, write);
      return row;
    })
  );
  renderCoverage(capabilities.coverage || {});
}

function renderPathList(element, paths, limit = paths.length) {
  element.replaceChildren(
    ...paths.slice(0, limit).map((path) => {
      const item = document.createElement("li");
      item.textContent = path;
      return item;
    })
  );
}

function renderCoverage(coverage) {
  const readable = coverage.sdk_readable_paths || [];
  const conditional = coverage.conditional_paths || [];
  const unmapped = coverage.manual_or_unmapped_paths || [];
  elements.coverageReadableSummary.textContent = `${readable.length} baseline paths`;
  elements.coverageConditionalSummary.textContent = `${conditional.length} baseline paths`;
  elements.coverageUnmappedSummary.textContent = `${unmapped.length} baseline paths require later SDK mapping or manual guidance`;
  renderPathList(elements.coverageReadable, readable);
  renderPathList(elements.coverageConditional, conditional);
  renderPathList(elements.coverageUnmapped, unmapped, 12);
  if (unmapped.length > 12) {
    const remaining = document.createElement("li");
    remaining.textContent = `+${unmapped.length - 12} more in the API report`;
    elements.coverageUnmapped.append(remaining);
  }
}

const statusLabels = {
  match: "Match",
  difference: "Different",
  equivalent: "Equivalent",
  unreadable: "Unreadable",
  conditional: "Conditional",
  manual_confirmation_needed: "Manual",
  not_applicable: "Not applicable",
};

const statusPriority = {
  difference: 0,
  unreadable: 1,
  conditional: 2,
  manual_confirmation_needed: 3,
  equivalent: 4,
  match: 5,
  not_applicable: 6,
};

function manualGroup(finding) {
  const routes = finding.access_paths || [];
  if (routes.some((route) => route.kind === "direct" || route.kind === "quick")) {
    return { key: "direct", label: "Buttons and direct controls", order: 0 };
  }
  const myMenu = routes.find((route) => route.kind === "my_menu");
  if (myMenu) {
    const tab = myMenu.tab || myMenu.label.split("→").pop().trim();
    return {
      key: `my-menu-${tab}`,
      label: `My Menu → ${tab}`,
      order: 100 + (Number.isInteger(myMenu.tab_order) ? myMenu.tab_order : 999),
    };
  }
  if (routes.some((route) => route.kind === "menu")) {
    return { key: "menu", label: "Standard menu", order: 1000 };
  }
  if (routes.some((route) => route.kind === "reference")) {
    return { key: "reference", label: "Reference guidance", order: 1500 };
  }
  return { key: "unmapped", label: "No reviewed route", order: 2000 };
}

function actionBucket(finding) {
  return ["equivalent", "match", "not_applicable"].includes(finding.status) ? 1 : 0;
}

function menuPageOrder(label) {
  const page = label.split(">")[0].trim();
  const match = page.match(/^(Shooting|AF|Playback|Set-up)(?: menu)?\s*(\d+)?/i);
  if (!match) return 4900;
  const family = { shooting: 0, af: 1, playback: 2, "set-up": 3 }[match[1].toLowerCase()] ?? 4;
  return family * 100 + (match[2] ? Number(match[2]) : 90);
}

function setupGroup(finding) {
  const route = (finding.access_paths || [])[0];
  if (!route) return { key: "unmapped", label: "No reviewed route", order: 5000, itemOrder: 999 };
  if (route.kind === "direct") {
    return { key: "direct", label: "Buttons, dials, and physical controls", order: 0, itemOrder: 0 };
  }
  if (route.kind === "quick") {
    return { key: "quick", label: "Q screen", order: 1000, itemOrder: 0 };
  }
  if (route.kind === "my_menu") {
    return {
      key: `my-menu-${route.tab || route.label}`,
      label: route.label,
      order: 2000 + (route.tab_order ?? 99),
      itemOrder: route.item_order ?? 999,
    };
  }
  if (route.kind === "menu") {
    const page = route.label.split(">")[0].trim();
    return { key: `menu-${page}`, label: page, order: 3000 + menuPageOrder(route.label), itemOrder: 0 };
  }
  if (route.kind === "reference") {
    return { key: "reference", label: "Reference guidance", order: 4000, itemOrder: 0 };
  }
  return { key: route.kind, label: route.label, order: 4900, itemOrder: 0 };
}

function orderedFindings(findings) {
  if (elements.comparisonOrder.value === "card") return [...findings];
  return findings
    .map((finding, index) => ({ finding, index }))
    .sort((left, right) => {
      if (elements.comparisonOrder.value === "setup") {
        const actionDifference = actionBucket(left.finding) - actionBucket(right.finding);
        if (actionDifference) return actionDifference;
        const leftGroup = setupGroup(left.finding);
        const rightGroup = setupGroup(right.finding);
        const routeDifference = leftGroup.order - rightGroup.order;
        if (routeDifference) return routeDifference;
        const setupStatusDifference = (statusPriority[left.finding.status] ?? 99) - (statusPriority[right.finding.status] ?? 99);
        if (setupStatusDifference) return setupStatusDifference;
        const itemDifference = leftGroup.itemOrder - rightGroup.itemOrder;
        if (itemDifference) return itemDifference;
        return left.index - right.index;
      }
      const statusDifference = (statusPriority[left.finding.status] ?? 99) - (statusPriority[right.finding.status] ?? 99);
      if (statusDifference) return statusDifference;
      if (left.finding.status === "manual_confirmation_needed") {
        const groupDifference = manualGroup(left.finding).order - manualGroup(right.finding).order;
        if (groupDifference) return groupDifference;
      }
      return left.index - right.index;
    })
    .map(({ finding }) => finding);
}

function groupHeadingRow(label) {
  const row = document.createElement("tr");
  row.className = "group-heading-row";
  const heading = document.createElement("th");
  heading.colSpan = 5;
  heading.scope = "rowgroup";
  heading.textContent = label;
  row.append(heading);
  return row;
}

function findingRow(finding, cardRow = false) {
  const row = document.createElement("tr");
  row.className = `finding-row finding-${finding.status}`;

  const expected = document.createElement("th");
  expected.scope = "row";
  expected.dataset.label = "Card Expected";
  expected.className = "expected-cell";
  const title = document.createElement("span");
  title.className = "expected-setting";
  title.textContent = finding.label;
  const expectedValue = document.createElement("strong");
  expectedValue.className = "expected-value";
  expectedValue.textContent = finding.expected;
  if (finding.expected_color) expectedValue.style.color = finding.expected_color;
  expected.append(title, expectedValue);
  const interactions = finding.interactions || [];
  if (interactions.length) {
    const interactionList = document.createElement("ul");
    interactionList.className = "finding-interactions";
    for (const interaction of interactions) {
      const item = document.createElement("li");
      item.textContent = `${interaction.behavior}: ${interaction.message}`;
      interactionList.append(item);
    }
    expected.append(interactionList);
  }
  const contextPrompt = contextPromptForFinding(finding);
  if (contextPrompt) {
    const contextControl = document.createElement("label");
    contextControl.className = "context-choice";
    const question = document.createElement("span");
    question.textContent = contextPrompt.question;
    const select = document.createElement("select");
    select.dataset.contextPath = contextPrompt.path;
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Choose context…";
    select.append(placeholder);
    for (const option of contextPrompt.options || []) {
      const choice = document.createElement("option");
      choice.value = option.id;
      choice.textContent = `${option.label} — ${option.target}`;
      choice.selected = option.id === contextPrompt.selected;
      select.append(choice);
    }
    select.addEventListener("change", () => {
      if (select.value) contextSelections[contextPrompt.path] = select.value;
      else delete contextSelections[contextPrompt.path];
      runAction(compareSelectedProfile);
    });
    contextControl.append(question, select);
    if (contextPrompt.selected_target) {
      const selectedTarget = document.createElement("small");
      selectedTarget.textContent = `Applicable authored target: ${contextPrompt.selected_target}`;
      contextControl.append(selectedTarget);
    }
    expected.append(contextControl);
  }

  const camera = document.createElement("td");
  camera.dataset.label = "Camera";
  const cameraValue = document.createElement("strong");
  cameraValue.textContent = finding.actual || "Manual confirmation needed";
  camera.append(cameraValue);
  if (finding.actual_raw !== null && finding.actual_raw !== undefined) {
    const raw = document.createElement("small");
    raw.textContent = `Raw: ${finding.actual_raw}`;
    camera.append(raw);
  }

  const statusCell = document.createElement("td");
  statusCell.dataset.label = "Status";
  const status = document.createElement("span");
  status.className = "finding-status";
  status.textContent = statusLabels[finding.status] || finding.status;
  statusCell.append(status);

  const access = document.createElement("td");
  access.dataset.label = "Optimal Access Path";
  access.className = "access-cell";
  if ((finding.access_paths || []).length) {
    const list = document.createElement("ol");
    list.className = "access-paths";
    for (const route of finding.access_paths) {
      const item = document.createElement("li");
      item.className = `access-${route.kind}`;
      item.textContent = route.label;
      if (route.color) item.style.setProperty("--access-color", route.color);
      list.append(item);
    }
    access.append(list);
  } else {
    access.textContent = "No reviewed shortcut or menu path";
    access.classList.add("access-unavailable");
  }

  const checklist = document.createElement("td");
  checklist.dataset.label = "Checklist";
  checklist.className = "checklist-cell";
  if (["match", "equivalent"].includes(finding.status)) {
    checklist.textContent = finding.status === "match" ? "Verified by camera" : "Accepted equivalent";
  } else if (finding.status === "difference") {
    checklist.textContent = "Change, then rescan";
  } else if (finding.status === "blocked") {
    checklist.textContent = "Resolve blocker";
  } else if (finding.status === "not_applicable") {
    checklist.textContent = "No action";
  } else if (finding.status === "conditional" && contextPrompt && !contextPrompt.selected) {
    checklist.textContent = "Choose context before evaluating";
    const reason = document.createElement("small");
    reason.className = "checklist-reason";
    reason.textContent = [...new Set(
      (finding.items?.length ? finding.items : [finding])
        .map((item) => item.reason)
        .filter(Boolean)
    )].join(" ");
    checklist.append(reason);
  } else if (isManualChecklistFinding(finding)) {
    const label = document.createElement("label");
    label.className = "manual-confirmation";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    const confirmation = manualConfirmation(finding);
    checkbox.checked = Boolean(confirmation);
    checkbox.addEventListener("change", () => {
      setManualConfirmation(finding, checkbox.checked);
      if (!checkbox.checked && finding.shared_manual_confirmation) {
        runAction(async () => {
          await revokeSharedManualConfirmation(finding);
          await compareSelectedProfile();
        });
      } else {
        renderComparisonTables();
        renderChecklistSummary();
      }
    });
    const text = document.createElement("span");
    text.textContent = "Reviewed/set manually";
    const evidence = document.createElement("small");
    evidence.textContent = checkbox.checked
      ? (finding.shared_manual_confirmation
        ? "Previously manually confirmed in this connected-camera session"
        : "Saved as manual_user_confirmed")
      : "Not camera-verified";
    label.append(checkbox, text, evidence);
    checklist.append(label);
    const reasons = [...new Set(
      (finding.items?.length ? finding.items : [finding])
        .map((item) => item.reason)
        .filter(Boolean)
    )];
    if (reasons.length) {
      const reason = document.createElement("small");
      reason.className = "checklist-reason";
      reason.textContent = reasons.join(" ");
      checklist.append(reason);
    }
    row.classList.toggle("finding-manually-confirmed", checkbox.checked);
  } else {
    checklist.textContent = "Review required";
  }

  if (cardRow && (finding.items || []).length > 1) {
    const details = document.createElement("ul");
    details.className = "finding-details";
    for (const item of finding.items) {
      const row = document.createElement("li");
      row.textContent = `${item.label}: expected ${item.expected}; actual ${item.actual || "manual confirmation needed"} — ${statusLabels[item.status] || item.status}`;
      details.append(row);
    }
    camera.append(details);
  } else if (!cardRow && finding.reason) {
    const reason = document.createElement("p");
    reason.className = "finding-reason";
    reason.textContent = finding.reason;
    camera.append(reason);
  }
  row.append(expected, camera, statusCell, access, checklist);
  return row;
}

function findingTable(findings, cardRows = false) {
  const wrapper = document.createElement("div");
  wrapper.className = "comparison-table-scroll";
  const table = document.createElement("table");
  table.className = "comparison-table";
  const head = document.createElement("thead");
  const headingRow = document.createElement("tr");
  for (const label of ["Card Expected", "Camera", "Status", "Optimal Access Path", "Checklist"]) {
    const heading = document.createElement("th");
    heading.scope = "col";
    heading.textContent = label;
    headingRow.append(heading);
  }
  head.append(headingRow);
  const body = document.createElement("tbody");
  let previousManualGroup = null;
  let previousSetupGroup = null;
  for (const finding of orderedFindings(findings)) {
    if (elements.comparisonOrder.value === "setup") {
      const group = setupGroup(finding);
      const noChange = actionBucket(finding) === 1;
      const groupKey = `${noChange ? "no-change" : "action"}-${group.key}`;
      if (groupKey !== previousSetupGroup) {
        body.append(groupHeadingRow(`${noChange ? "No change needed — " : ""}${group.label}`));
      }
      previousSetupGroup = groupKey;
    }
    if (elements.comparisonOrder.value === "status" && finding.status === "manual_confirmation_needed") {
      const group = manualGroup(finding);
      if (group.key !== previousManualGroup) body.append(groupHeadingRow(group.label));
      previousManualGroup = group.key;
    }
    body.append(findingRow(finding, finding.card_row ?? cardRows));
  }
  table.append(head, body);
  wrapper.append(table);
  return wrapper;
}

function renderComparisonTables() {
  if (!comparisonState) return;
  const setupOrder = elements.comparisonOrder.value === "setup";
  elements.additionalFindingSection.hidden = setupOrder;
  elements.cardFindingHeading.textContent = setupOrder ? "Rapid camera setup route" : "Settings shown on the card";
  elements.cardFindingDescription.textContent = setupOrder
    ? "One pass through physical controls, Q, each My Menu tab, and each Canon menu page. Settings that need no change are listed afterward."
    : "Shown in the exact order used by the selected card.";
  if (setupOrder) {
    const combined = [
      ...comparisonState.card_findings.map((finding) => ({ ...finding, card_row: true })),
      ...comparisonState.additional_findings.map((finding) => ({ ...finding, card_row: false })),
    ];
    elements.cardFindings.replaceChildren(findingTable(combined));
    elements.additionalFindings.replaceChildren();
    return;
  }
  elements.cardFindings.replaceChildren(findingTable(comparisonState.card_findings, true));
  elements.additionalFindings.replaceChildren(findingTable(comparisonState.additional_findings, false));
}

function renderComparison(comparison, { recordScan = false } = {}) {
  comparisonState = comparison;
  renderEquipmentContext(comparison.equipment);
  const record = activeChecklistRecord(true);
  if (recordScan) record.last_scan_at = new Date().toISOString();
  saveChecklistState();
  elements.comparisonResults.hidden = false;
  const equipmentName = comparison.equipment?.selected_lens_name || "unresolved lens";
  elements.comparisonSummary.textContent = `${comparison.profile.display_title || comparison.profile.title} with ${equipmentName}: ${comparison.summary.card_rows} card rows followed by ${comparison.summary.additional_settings} additional settings. Camera settings were not changed.`;
  renderComparisonTables();
  renderChecklistSummary();
  elements.compareStep.classList.remove("locked");
  elements.compareStep.classList.add("active");
  const guardedAvailable = statusState?.backend_mode === "simulated" || statusState?.physical_guarded_runs;
  elements.prepareGuardedButton.hidden = !guardedAvailable;
  elements.configureStep.classList.toggle("locked", !guardedAvailable);
}

function renderEquipmentContext(equipment) {
  if (!equipment) {
    elements.equipmentContext.hidden = true;
    return;
  }
  elements.equipmentContext.hidden = false;
  const detected = equipment.detected_lens_name;
  if (equipment.planning_override) {
    elements.equipmentContextSource.textContent = `Planning override: ${equipment.selected_lens_name}. The connected camera reports ${detected}; a physical guarded run will require the planned lens to be attached.`;
    elements.equipmentContext.classList.add("equipment-warning");
  } else if (equipment.selection_source === "camera_readback") {
    elements.equipmentContextSource.textContent = `Using the camera-reported attached lens: ${detected}.`;
    elements.equipmentContext.classList.remove("equipment-warning");
  } else if (equipment.selection_source === "profile_primary") {
    elements.equipmentContextSource.textContent = `No authored camera lens match is available, so planning defaults to the card's Primary lens: ${equipment.selected_lens_name}.`;
    elements.equipmentContext.classList.remove("equipment-warning");
  } else {
    elements.equipmentContextSource.textContent = equipment.selected_lens_name
      ? `Using ${equipment.selected_lens_name} for this comparison.`
      : "Choose or connect a recognized lens to resolve equipment-dependent settings.";
    elements.equipmentContext.classList.remove("equipment-warning");
  }

  const automatic = document.createElement("option");
  automatic.value = "";
  const primaryChoice = (equipment.options || []).find((item) => item.role === "primary");
  automatic.textContent = equipment.detected_lens_recognized
    ? `Automatic — camera reports ${detected}`
    : `Automatic — card Primary (${primaryChoice?.display_name || "unresolved"})`;
  elements.lensChoiceSelect.replaceChildren(
    automatic,
    ...(equipment.options || []).map((item) => {
      const option = document.createElement("option");
      option.value = item.key;
      option.textContent = `${item.display_name} — ${item.role_label}`;
      return option;
    })
  );
  elements.lensChoiceSelect.value = equipmentSelection.choiceKey || "";
  const guidance = equipment.selected_guidance;
  elements.lensChoiceGuidance.textContent = guidance
    ? `${guidance.use_when}. Field check: ${guidance.field_check}.`
    : "The attached lens is not an authored choice for this card.";

  const stabilization = equipment.stabilization || {};
  const modes = stabilization.supported_modes || [];
  elements.isModeControl.hidden = !modes.length;
  if (modes.length) {
    const profileDefault = document.createElement("option");
    profileDefault.value = "";
    profileDefault.textContent = stabilization.profile_mode
      ? `Profile default — Mode ${stabilization.profile_mode}`
      : "Choose a supported mode";
    elements.isModeSelect.replaceChildren(
      profileDefault,
      ...modes.map((mode) => {
        const option = document.createElement("option");
        option.value = String(mode.value);
        option.textContent = `Mode ${mode.value} — ${mode.purpose}`;
        return option;
      })
    );
    elements.isModeSelect.value = equipmentSelection.isMode || "";
  }
  elements.isModeGuidance.textContent = stabilization.mode_override
    ? `${stabilization.summary} Override active: Mode ${stabilization.selected_mode} replaces the profile default Mode ${stabilization.profile_mode} for this comparison.`
    : stabilization.summary || "";

  const interactions = equipment.interactions || [];
  elements.equipmentInteractionList.replaceChildren(
    ...(interactions.length ? interactions : [{message: "No additional conditional rules are active."}]).map((interaction) => {
      const item = document.createElement("li");
      item.textContent = interaction.message;
      return item;
    })
  );
}

const guardedClassificationLabels = {
  already_matching_skipped: "Already correct",
  simulator_automatic: "Camera Lab will change",
  physical_automatic: "Camera Lab will change",
  manual: "You will change",
  blocked_or_unsupported: "Needs attention first",
};

const guardedStatusLabels = {
  planned: "Ready for your review",
  confirmed: "Ready to begin",
  in_progress: "Applying profile",
  failed: "Stopped — not fully applied",
  blocked: "Cannot continue yet",
  aborted: "Stopped by you — not fully applied",
  complete: "Profile applied successfully",
};

function friendlyStepReason(step) {
  const reason = String(step.reason || "");
  if (step.classification === "already_matching_skipped") {
    return "The camera already matches this profile. Nothing will be changed.";
  }
  if (["simulator_automatic", "physical_automatic"].includes(step.classification)) {
    return "Camera Lab can make this change and immediately verify the camera reports the requested value.";
  }
  if (step.classification === "manual") {
    return "Change this on the camera using the route shown, then confirm it here.";
  }
  if (reason.includes("has not passed reversible qualification")) {
    return "Automatic changing is not enabled for this value yet. Open Advanced setup above to test and enable it safely.";
  }
  if (reason.includes("outside the reviewed write-qualification allowlist")) {
    return "Camera Lab cannot change this setting automatically. Change it on the camera, rescan, and review the profile again.";
  }
  if (reason.includes("descriptor")) {
    return "The camera does not currently offer this value for automatic changing. Check the camera mode, change it manually if needed, then rescan.";
  }
  if (reason.includes("context remains unresolved")) {
    return "Choose the missing subject or shooting condition in the comparison, then review again.";
  }
  return reason || "Resolve this item before starting.";
}

function guardedStepInstruction(step, position, total) {
  return `${position} of ${total}: ${step.label} → ${step.target}:`;
}

function renderApplyResult(run, counts, completed, total) {
  const steps = run.steps || [];
  const actions = run.summary?.actions || { completed: completed, total: total, remaining: total - completed };
  const operatorActions = run.summary?.operator_actions || actions;
  const automaticActions = run.summary?.automatic_actions || {completed: 0, total: 0};
  const verifiedSteps = steps.filter((step) => ["camera_verified", "simulator_verified"].includes(step.status));
  const unchangedSteps = steps.filter((step) => step.status === "skipped");
  const manualSteps = steps.filter((step) => step.status === "manual_user_confirmed");
  const verified = verifiedSteps.length;
  const unchanged = unchangedSteps.length;
  const manual = manualSteps.length;
  const blocked = steps.filter((step) => step.classification === "blocked_or_unsupported");
  elements.applyResult.className = "apply-result";
  elements.applyResultDetails.replaceChildren();

  let title = "";
  let summary = "";
  let details = [];
  if (run.status === "planned" && blocked.length) {
    title = "Not ready to apply";
    summary = `${blocked.length} ${blocked.length === 1 ? "item needs" : "items need"} attention. Nothing has changed.`;
    details = blocked.map((step) => `${step.label}: ${friendlyStepReason(step)}`);
    elements.applyResult.classList.add("needs-attention");
  } else if (run.status === "planned") {
    title = "Ready to apply";
    summary = `Review complete: ${operatorActions.total} actions for you, ${automaticActions.total} handled automatically, and ${counts.already_matching_skipped || 0} plan items requiring no action.`;
    details = ["Nothing has changed yet. Camera Lab will automatically clear already-correct items and simulator-safe changes after confirmation."];
    elements.applyResult.classList.add("ready");
  } else if (run.status === "complete") {
    title = "Profile applied successfully";
    summary = `All ${operatorActions.total} operator ${operatorActions.total === 1 ? "action" : "actions"} finished. Camera Lab handled ${automaticActions.completed} simulator-safe ${automaticActions.completed === 1 ? "change" : "changes"} automatically, verified ${verified}, and accounted for ${unchanged} items without a change.`;
    details = [
      `Verified automatically: ${verifiedSteps.length ? verifiedSteps.map((step) => `${step.label} = ${step.target}`).join("; ") : "None"}.`,
      `Confirmed by you: ${manualSteps.length ? manualSteps.map((step) => `${step.label} = ${step.target}`).join("; ") : "None"}.`,
      `Already correct: ${unchangedSteps.length ? unchangedSteps.map((step) => step.label).join("; ") : "None"}.`,
      "No failed or unfinished steps remain.",
    ];
    elements.applyResult.classList.add("success");
  } else if (["failed", "blocked", "aborted"].includes(run.status)) {
    title = run.status === "aborted" ? "Stopped by you — profile not fully applied" : "Stopped — profile not fully applied";
    summary = `${operatorActions.completed} of ${operatorActions.total} operator actions finished. Do not treat this profile as complete.`;
    const failedStep = steps.find((step) => step.status === "failed" || step.status === "blocked");
    details = [
      run.failure || "Review the unfinished step before continuing or starting again.",
      failedStep ? `Stopped at: ${failedStep.label} → ${failedStep.target}.` : "Review the next unfinished step before continuing.",
      `Finished before stopping: ${steps.filter((step) => ["camera_verified", "simulator_verified", "manual_user_confirmed", "skipped"].includes(step.status)).map((step) => step.label).join("; ") || "None"}.`,
    ];
    elements.applyResult.classList.add("stopped");
  }
  elements.applyResult.hidden = !title;
  elements.applyResultTitle.textContent = title;
  elements.applyResultSummary.textContent = summary;
  elements.applyResultDetails.replaceChildren(...details.map((detail) => {
    const item = document.createElement("li");
    item.textContent = detail;
    return item;
  }));
}

function comparisonCurrentMode() {
  for (const finding of allComparisonFindings()) {
    const items = finding.items || [finding];
    const mode = items.find((item) => item.path === "exposure.mode");
    if (mode?.actual) return mode.actual;
  }
  return "";
}

function openGuardedPreflight() {
  const available = statusState?.backend_mode === "simulated" || statusState?.physical_guarded_runs;
  if (!comparisonState || !available) return;
  elements.guardedRunPanel.hidden = false;
  const profileName = comparisonState.profile.display_title || comparisonState.profile.title || comparisonState.profile.name;
  elements.applyProfileTitle.textContent = `Apply ${profileName} to camera`;
  elements.applyProfileIntro.textContent = `Camera Lab will check readiness and show every ${profileName} change before anything happens.`;
  elements.guardedCameraIdentity.textContent = `${valueOrUnavailable(statusState.camera?.product_name)} · ${valueOrUnavailable(statusState.camera?.body_id)}`;
  elements.guardedCameraFirmware.textContent = valueOrUnavailable(statusState.camera?.firmware_version);
  elements.guardedCameraPower.textContent = powerStatus(statusState.camera?.battery_raw);
  if (guardedRunState && ["planned", "confirmed", "in_progress"].includes(guardedRunState.status)) {
    syncGuardedPreflightFromRun(guardedRunState);
    if (["confirmed", "in_progress"].includes(guardedRunState.status)) {
      setMessage("The readiness choices are locked to this active Apply plan. Stop applying and create a new review to change them.", "info");
    }
    elements.guardedRunPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  setGuardedReadinessLocked(false);
  const restoredPreflight = restoreGuardedPreflight();
  populateGuardedLensOptions(restoredPreflight?.lens_choice);
  if (!elements.guardedCurrentMode.value) elements.guardedCurrentMode.value = comparisonCurrentMode();
  elements.configureStep.classList.remove("locked");
  elements.configureStep.classList.add("active");
  if (statusState?.physical_write_qualification) runAction(loadWriteQualificationCandidates);
  elements.guardedRunPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function populateGuardedLensOptions(preferredValue = null, equipmentOverride = null) {
  const equipment = equipmentOverride || comparisonState?.equipment || {};
  const cameraLens = String(statusState?.camera?.lens_name || "").trim();
  const automatic = document.createElement("option");
  automatic.value = "__automatic__";
  automatic.dataset.lensName = cameraLens || equipment.selected_lens_name || "None";
  automatic.textContent = cameraLens
    ? `Attached — ${cameraLens}`
    : `Card Primary — ${equipment.selected_lens_name || "None"}`;
  const choices = (equipment.options || []).map((item) => {
    const option = document.createElement("option");
    option.value = item.key;
    option.dataset.lensName = item.display_name;
    option.textContent = `${item.display_name} — ${item.role_label}`;
    return option;
  });
  elements.guardedLens.replaceChildren(automatic, ...choices);
  const requested = preferredValue || (cameraLens ? "__automatic__" : equipmentSelection.choiceKey || "__automatic__");
  elements.guardedLens.value = [...elements.guardedLens.options].some((option) => option.value === requested)
    ? requested
    : "__automatic__";
  elements.guardedLensSource.textContent = cameraLens
    ? "The camera-reported attached lens is selected by default. Choose another authored card lens only to plan for changing lenses; physical Apply requires that lens to be attached and rescanned."
      : "The card's Primary lens is selected by default. Choose another authored lens for this card when planning requires it.";
}

function guardedReadinessControls() {
  return [
    elements.guardedStillMovie,
    elements.guardedCurrentMode,
    elements.guardedLens,
    elements.guardedFlash,
    elements.guardedCards,
    elements.guardedBackupFilename,
    elements.guardedSetupEssentialsConfirmed,
    elements.guardedAppsClosed,
    elements.guardedBackupConfirmed,
  ];
}

function setGuardedReadinessLocked(locked) {
  for (const control of guardedReadinessControls()) control.disabled = locked;
}

function syncGuardedPreflightFromRun(run) {
  const preflight = run.preflight || {};
  const preferredLens = preflight.lens_choice || (preflight.lens_source === "camera_readback" ? "__automatic__" : null);
  populateGuardedLensOptions(preferredLens, run.equipment);
  elements.guardedStillMovie.value = preflight.still_movie_context || "still";
  elements.guardedCurrentMode.value = preflight.current_mode || "";
  elements.guardedFlash.value = preflight.flash || "None";
  elements.guardedCards.value = preflight.cards || "CFexpress & SD";
  elements.guardedBackupFilename.value = preflight.backup_filename || "C123_CFG.CSD";
  elements.guardedSetupEssentialsConfirmed.checked = preflight.camera_setup_essentials_confirmed === true;
  elements.guardedAppsClosed.checked = preflight.applications_closed === true;
  elements.guardedBackupConfirmed.checked = preflight.camera_backup_confirmed === true;
  setGuardedReadinessLocked(run.status !== "planned");
}

function renderGuardedRun(payload) {
  guardedRunState = payload.guarded_run;
  const run = guardedRunState;
  syncGuardedPreflightFromRun(run);
  syncWriteQualificationToReview();
  const summary = run.summary || {};
  const counts = summary.classifications || {};
  const completed = summary.completed_steps || 0;
  const total = summary.total_steps || 0;
  const actions = summary.actions || {completed, total, current: 0, remaining: total - completed};
  const operatorActions = summary.operator_actions || actions;
  const automaticActions = summary.automatic_actions || {completed: 0, total: 0};
  elements.guardedRunPanel.hidden = false;
  elements.guardedPreview.hidden = false;
  elements.guardedStatus.textContent = guardedStatusLabels[run.status] || run.status;
  elements.guardedProgressCount.textContent = `${operatorActions.completed} of ${operatorActions.total} your actions · ${automaticActions.completed} automatic`;
  elements.guardedProgressBar.max = Math.max(operatorActions.total, 1);
  elements.guardedProgressBar.value = operatorActions.completed;
  elements.applyReviewMessage.textContent = run.status === "planned"
    ? "Nothing has changed yet. Check the summary below before starting."
    : run.status === "complete"
      ? "Every planned step finished. The result below is your completion receipt."
      : run.backend === "simulated"
        ? "Simulator-safe changes and already-correct items were processed automatically. Only work requiring you remains below."
        : "Already-correct items were cleared automatically. Only actual work remains below.";
  elements.guardedClassificationCounts.replaceChildren(
    ...[
      ["already_matching_skipped", "Already correct", counts.already_matching_skipped || 0],
      ["automatic", "Camera Lab will change", (counts.simulator_automatic || 0) + (counts.physical_automatic || 0)],
      ["manual", "You will change", counts.manual || 0],
      ["blocked_or_unsupported", "Needs attention first", counts.blocked_or_unsupported || 0],
    ].map(([classification, label, value]) => {
      const item = document.createElement("div");
      item.className = `guarded-count guarded-${classification}`;
      const count = document.createElement("strong");
      count.textContent = value;
      const text = document.createElement("span");
      text.textContent = label;
      item.append(count, text);
      return item;
    })
  );
  elements.guardedFailure.hidden = !run.failure;
  elements.guardedFailure.textContent = run.failure || "";
  elements.guardedPlanSteps.replaceChildren(
    ...(run.steps || []).map((step) => {
      const item = document.createElement("li");
      item.className = `guarded-plan-step guarded-${step.classification} guarded-step-${step.status}`;
      const title = document.createElement("strong");
      title.textContent = `${step.index}. ${step.label} → ${step.target}`;
      const classification = document.createElement("span");
      classification.textContent = guardedClassificationLabels[step.classification] || step.classification;
      const reason = document.createElement("small");
      reason.textContent = `${friendlyStepReason(step)}${step.result ? ` Result: ${step.result}` : ""}`;
      item.append(title, classification, reason);
      return item;
    })
  );
  const processingOneStep = ["confirmed", "in_progress"].includes(run.status);
  elements.guardedActiveWorkspace.classList.toggle("is-processing", processingOneStep);
  elements.guardedPlanDetails.hidden = processingOneStep;
  if (processingOneStep) elements.guardedPlanDetails.open = false;

  const current = (run.steps || [])[run.current_step];
  const executable = ["confirmed", "in_progress"].includes(run.status) && current;
  elements.guardedCurrentStep.hidden = !current || run.status === "planned";
  elements.guardedStepSettings.hidden = true;
  elements.guardedStepSettings.replaceChildren();
  if (current) {
    const manualGroup = current.classification === "manual"
      ? (run.steps || []).filter((step) => step.classification === "manual"
        && step.manual_group_key === current.manual_group_key
        && !["skipped", "simulator_verified", "camera_verified", "manual_user_confirmed"].includes(step.status))
      : [];
    if (manualGroup.length > 1) {
      elements.guardedStepTitle.textContent = `${operatorActions.current} of ${operatorActions.total}: ${current.manual_group_label} (${manualGroup.length} settings):`;
      elements.guardedStepSettings.hidden = false;
      elements.guardedStepSettings.replaceChildren(...manualGroup.map((step) => {
        const item = document.createElement("li");
        item.textContent = `${step.label} → ${step.target}`;
        return item;
      }));
      elements.guardedStepDetail.textContent = "Set every item in this group, then continue once. Camera Lab will perform one rescan and verify every exact readable match together.";
      elements.guardedStepRoute.textContent = `Stay in: ${current.manual_group_label}`;
    } else {
      const position = current.classification === "simulator_automatic" ? actions.current : operatorActions.current;
      const actionTotal = current.classification === "simulator_automatic" ? actions.total : operatorActions.total;
      elements.guardedStepTitle.textContent = guardedStepInstruction(current, position, actionTotal);
      const before = current.read_before || current.observed;
      elements.guardedStepDetail.textContent = before
        ? `${current.label}: ${before} → ${current.target}. ${friendlyStepReason(current)}`
        : `${current.label}: set to ${current.target}. ${friendlyStepReason(current)}`;
      elements.guardedStepRoute.textContent = current.access_paths?.length
        ? `Route: ${current.access_paths.map((route) => route.label).join("; ")}`
        : "No reviewed camera route; follow the manual explanation.";
    }
  }
  elements.guardedConfirmButton.hidden = run.status !== "planned";
  elements.guardedConfirmButton.disabled = (counts.blocked_or_unsupported || 0) > 0 || requestPending;
  elements.guardedNextButton.hidden = !executable;
  if (current) {
    elements.guardedNextButton.textContent = current.classification === "simulator_automatic"
      ? `Apply and verify ${current.label}`
      : current.classification === "physical_automatic"
        ? `Apply and verify ${current.label}`
      : current.classification === "manual"
        ? ((run.steps || []).filter((step) => step.classification === "manual"
          && step.manual_group_key === current.manual_group_key
          && !["skipped", "simulator_verified", "camera_verified", "manual_user_confirmed"].includes(step.status)).length > 1
          ? "I changed these settings — rescan once"
          : "I changed this setting — rescan")
        : "Confirm and continue";
  }
  elements.guardedAbortButton.hidden = ["complete", "aborted"].includes(run.status);
  elements.guardedResumeButton.hidden = run.status !== "failed";
  elements.guardedResumeButton.dataset.sessionId = run.session_id;
  elements.guardedResumeButton.textContent = "Continue stopped attempt";
  renderApplyResult(run, counts, completed, total);
  elements.configureStep.classList.remove("locked");
  elements.configureStep.classList.toggle("active", run.status !== "complete");
}

function guardedPreflightPayload() {
  const selectedLens = elements.guardedLens.selectedOptions[0];
  return {
    still_movie_context: elements.guardedStillMovie.value,
    current_mode: elements.guardedCurrentMode.value,
    lens: selectedLens?.dataset.lensName || "None",
    lens_choice: elements.guardedLens.value,
    flash: elements.guardedFlash.value,
    cards: elements.guardedCards.value,
    camera_setup_essentials_confirmed: elements.guardedSetupEssentialsConfirmed.checked,
    applications_closed: elements.guardedAppsClosed.checked,
    camera_backup_confirmed: elements.guardedBackupConfirmed.checked,
    backup_filename: elements.guardedBackupFilename.value,
  };
}

function selectedEquipmentPayload() {
  const payload = {};
  const guardedChoice = !elements.guardedRunPanel.hidden
    ? (elements.guardedLens.value === "__automatic__" ? "" : elements.guardedLens.value)
    : equipmentSelection.choiceKey;
  if (guardedChoice) payload.choice_key = guardedChoice;
  if (equipmentSelection.isMode) payload.is_mode = equipmentSelection.isMode;
  return payload;
}

function guardedPreflightStorageKey() {
  const camera = statusState?.camera || {};
  const identity = [camera.product_name, camera.body_id, camera.firmware_version, camera.lens_name]
    .map((value) => String(value || "").trim())
    .join("|");
  return identity.replaceAll("|", "") ? `camera-lab-preflight:${identity}` : null;
}

function persistGuardedPreflight() {
  const key = guardedPreflightStorageKey();
  if (!key) return;
  try {
    window.sessionStorage.setItem(key, JSON.stringify(guardedPreflightPayload()));
  } catch (_error) {
    // Session retention is an optional convenience; preflight validation remains authoritative.
  }
}

function restoreGuardedPreflight() {
  const key = guardedPreflightStorageKey();
  if (!key) return null;
  try {
    const saved = JSON.parse(window.sessionStorage.getItem(key) || "null");
    if (!saved) return null;
    elements.guardedStillMovie.value = saved.still_movie_context || "still";
    elements.guardedCurrentMode.value = saved.current_mode || "";
    elements.guardedFlash.value = saved.flash || "None";
    elements.guardedCards.value = saved.cards || "CFexpress & SD";
    elements.guardedSetupEssentialsConfirmed.checked = saved.camera_setup_essentials_confirmed === true;
    elements.guardedAppsClosed.checked = saved.applications_closed === true;
    elements.guardedBackupConfirmed.checked = saved.camera_backup_confirmed === true;
    elements.guardedBackupFilename.value = saved.backup_filename || "C123_CFG.CSD";
    return saved;
  } catch (_error) {
    // Ignore unavailable or invalid session-only convenience state.
    return null;
  }
}

async function prepareGuardedRun() {
  const result = await request("/api/camera-control/guarded-run/prepare", {
    method: "POST",
    body: JSON.stringify({
      profile: comparisonState.profile.name,
      context_choices: contextSelections,
      equipment_choice: selectedEquipmentPayload(),
      preflight: guardedPreflightPayload(),
    }),
  });
  renderGuardedRun(result);
}

function showGuardedConfirmation() {
  if (!guardedRunState || guardedRunState.status !== "planned") return;
  const physical = guardedRunState.backend === "edsdk";
  elements.guardedConfirmDialog.querySelector(".label").textContent = physical
    ? "Final confirmation" : "Simulator confirmation";
  elements.guardedConfirmDialog.querySelector("h2").textContent = physical
    ? "Apply these changes to your EOS R5?" : "Try these changes in the simulator?";
  elements.guardedConfirmExecute.textContent = physical
    ? "Start applying profile" : "Start simulator test";
  elements.guardedConfirmMessage.textContent = physical
    ? "Camera Lab will automatically clear items that still match, keep one deliberate action for each physical write, and group manual changes by camera route."
    : "Camera Lab will automatically process every simulator-safe change, verifying each one independently and stopping at the first problem. It will then show only grouped manual work.";
  elements.guardedConfirmSafety.textContent = physical
    ? "Camera Lab stops at the first problem and will never report a partial attempt as complete. C1–C3 registration remains manual."
    : "This simulator test cannot change the physical EOS R5.";
  if (typeof elements.guardedConfirmDialog.showModal === "function") {
    elements.guardedConfirmDialog.showModal();
  } else {
    elements.guardedConfirmDialog.setAttribute("open", "");
  }
}

function requiredWriteQualification() {
  return (guardedRunState?.steps || []).find((step) => (
    step.classification === "blocked_or_unsupported"
    && step.property_key
    && Number.isInteger(step.target_raw)
    && String(step.reason || "").includes("has not passed reversible qualification")
  ));
}

function updateWriteQualificationTargets(preferredTargetRaw = null) {
  const candidate = writeQualificationCandidates.find(
    (item) => item.key === elements.writeQualificationProperty.value
  );
  elements.writeQualificationTarget.replaceChildren(
    ...(candidate?.targets || []).map((target) => {
      const option = document.createElement("option");
      option.value = String(target.value_raw);
      option.textContent = `${target.label} (camera code ${target.value_raw})`;
      return option;
    })
  );
  if (Number.isInteger(preferredTargetRaw)) {
    const preferred = [...elements.writeQualificationTarget.options].find(
      (option) => Number(option.value) === preferredTargetRaw
    );
    if (preferred) elements.writeQualificationTarget.value = preferred.value;
  }
  elements.writeQualificationPrepare.disabled = !candidate || !(candidate.targets || []).length;
}

function syncWriteQualificationToReview() {
  if (!elements.writeQualificationNeeded) return;
  elements.writeQualificationProperty.disabled = false;
  elements.writeQualificationTarget.disabled = false;
  const required = requiredWriteQualification();
  if (!required) {
    elements.writeQualificationNeeded.textContent = "Review what will change first. Camera Lab will then select the exact blocked setting and value here.";
    return;
  }
  const candidate = writeQualificationCandidates.find((item) => item.key === required.property_key);
  const target = candidate?.targets?.find((item) => item.value_raw === required.target_raw);
  if (!candidate || !target) {
    elements.writeQualificationNeeded.textContent = `This review needs ${required.label} → ${required.target}, but that exact value is not available for a safety test in the current camera descriptor.`;
    return;
  }
  elements.writeQualificationProperty.value = required.property_key;
  updateWriteQualificationTargets(required.target_raw);
  elements.writeQualificationProperty.disabled = true;
  elements.writeQualificationTarget.disabled = true;
  elements.writeQualificationNeeded.textContent = `Required by this review: ${required.label} → ${required.target} (camera code ${required.target_raw}). The safety test below is set to that exact value.`;
}

async function loadWriteQualificationCandidates() {
  const result = await request("/api/camera-control/write-qualification/candidates");
  writeQualificationCandidates = result.candidates || [];
  elements.writeQualificationProperty.replaceChildren(
    ...writeQualificationCandidates.map((candidate) => {
      const option = document.createElement("option");
      option.value = candidate.key;
      option.textContent = `${candidate.label} — currently ${candidate.current}`;
      return option;
    })
  );
  updateWriteQualificationTargets();
  syncWriteQualificationToReview();
}

function renderWriteQualification(payload) {
  writeQualificationState = payload.qualification;
  const qualification = writeQualificationState;
  elements.writeQualificationPreview.hidden = false;
  elements.writeQualificationSummary.textContent = `${qualification.label}: temporarily change ${qualification.original} to ${qualification.target}, verify it, restore ${qualification.original}, and verify restoration.`;
  elements.writeQualificationDialogSummary.textContent = `Test only ${qualification.label} → ${qualification.target} (camera code ${qualification.target_raw}), then restore ${qualification.original}. This does not enable any other ${qualification.label} value.`;
  elements.writeQualificationResult.hidden = !qualification.failure && qualification.status !== "qualification_complete";
  elements.writeQualificationResult.textContent = qualification.failure
    || (qualification.status === "qualification_complete"
      ? `Safety test passed for ${qualification.label} → ${qualification.target} (camera code ${qualification.target_raw}). Camera Lab verified that exact value and restored ${qualification.original}; no other ${qualification.label} value was enabled.`
      : "");
  elements.writeQualificationConfirm.hidden = qualification.status !== "qualification_planned";
  elements.writeQualificationExecute.hidden = qualification.status !== "qualification_confirmed";
}

async function prepareWriteQualification() {
  if (!elements.guardedPreflightForm.reportValidity()) return;
  const result = await request("/api/camera-control/write-qualification/prepare", {
    method: "POST",
    body: JSON.stringify({
      property_key: elements.writeQualificationProperty.value,
      target_raw: Number(elements.writeQualificationTarget.value),
      preflight: guardedPreflightPayload(),
    }),
  });
  renderWriteQualification(result);
}

function showWriteQualificationConfirmation() {
  if (!writeQualificationState || writeQualificationState.status !== "qualification_planned") return;
  if (typeof elements.writeQualificationDialog.showModal === "function") {
    elements.writeQualificationDialog.showModal();
  } else {
    elements.writeQualificationDialog.setAttribute("open", "");
  }
}

async function confirmWriteQualification() {
  elements.writeQualificationDialog.close();
  const result = await request("/api/camera-control/write-qualification/confirm", {
    method: "POST",
    body: JSON.stringify({session_id: writeQualificationState.session_id, confirmed: true}),
  });
  renderWriteQualification(result);
}

async function executeWriteQualification() {
  const result = await request("/api/camera-control/write-qualification/execute", {
    method: "POST",
    body: JSON.stringify({session_id: writeQualificationState.session_id}),
  });
  renderWriteQualification(result);
  await refreshStatus({quiet: true});
  if (result.qualification?.status === "qualification_complete" && guardedRunState?.status === "planned") {
    await prepareGuardedRun();
    elements.writeQualificationResult.textContent += " The profile review below has been refreshed automatically.";
  }
}

async function confirmGuardedRun() {
  elements.guardedConfirmDialog.close();
  const result = await request("/api/camera-control/guarded-run/confirm", {
    method: "POST",
    body: JSON.stringify({ session_id: guardedRunState.session_id, confirmed: true }),
  });
  renderGuardedRun(result);
  if (!elements.guardedCurrentStep.hidden) {
    elements.guardedActiveWorkspace.scrollIntoView({behavior: "smooth", block: "center"});
    window.setTimeout(() => elements.guardedNextButton.focus({preventScroll: true}), 350);
  }
}

async function executeNextGuardedStep() {
  const scrollPosition = window.scrollY;
  const current = guardedRunState.steps[guardedRunState.current_step];
  const completedManualGroup = current?.classification === "manual";
  const result = await request("/api/camera-control/guarded-run/next", {
    method: "POST",
    body: JSON.stringify({
      session_id: guardedRunState.session_id,
      manual_confirmed: current?.classification === "manual",
    }),
  });
  renderGuardedRun(result);
  if (completedManualGroup) await compareSelectedProfile({recordScan: true});
  window.scrollTo({top: scrollPosition, behavior: "auto"});
  if (!elements.guardedNextButton.hidden) elements.guardedNextButton.focus({preventScroll: true});
}

async function resumeGuardedRun() {
  const sessionId = guardedRunState?.session_id || elements.guardedResumeButton.dataset.sessionId;
  if (!sessionId) return;
  if (!guardedRunState) {
    const recorded = await request(`/api/camera-control/guarded-run?session_id=${encodeURIComponent(sessionId)}`);
    renderGuardedRun(recorded);
    if (recorded.guarded_run.status === "planned" || recorded.guarded_run.status === "blocked") return;
  }
  const result = await request("/api/camera-control/guarded-run/resume", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
  renderGuardedRun(result);
}

async function abortGuardedRun() {
  if (!guardedRunState || !window.confirm("Stop applying this profile? Completed steps will remain recorded, but the profile will not be marked complete.")) return;
  const result = await request("/api/camera-control/guarded-run/abort", {
    method: "POST",
    body: JSON.stringify({ session_id: guardedRunState.session_id }),
  });
  renderGuardedRun(result);
}

function openCxChecklist(profileName) {
  const option = [...elements.profileSelect.options].find((item) => item.value === profileName);
  if (!option) return;
  elements.profileSelect.value = profileName;
  contextSelections = {};
  equipmentSelection = { choiceKey: "", isMode: "" };
  comparisonState = null;
  elements.equipmentContext.hidden = true;
  elements.comparisonResults.hidden = true;
  setBusy(requestPending);
  elements.comparisonPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  window.setTimeout(() => elements.compareButton.focus({ preventScroll: true }), 350);
}

function renderCxSetup(profiles) {
  const foundations = new Map(
    profiles
      .filter((profile) => profile.is_foundation && ["C1", "C2", "C3"].includes(profile.foundation_slot))
      .map((profile) => [profile.foundation_slot, profile])
  );
  elements.cxSlotCards.replaceChildren(
    ...["C1", "C2", "C3"].map((slot) => {
      const profile = foundations.get(slot);
      const card = document.createElement("article");
      card.className = `cx-slot-card${profile ? "" : " cx-slot-missing"}`;
      const heading = document.createElement("h3");
      heading.textContent = profile ? `${slot} – ${profile.title}` : `${slot} – Assignment unavailable`;
      const summary = document.createElement("p");
      summary.textContent = profile
        ? `Saved foundation: ${profile.title}. The session-3 camera-body registration was verified; Camera Lab rereads the current saved assignment whenever it loads.`
        : "No saved foundation profile currently resolves to this slot. Save the assignment in Profile Editor, then reload Camera Lab.";
      const steps = document.createElement("ol");
      const instructions = profile
        ? [
            `For routine validation, recall ${slot} and open the ${profile.title} checklist without changing the registration.`,
            `If the assignment or target changed, begin in a normal shooting mode, set or confirm the checklist values, then manually choose Set-up 5 → Custom shooting mode (C1-C3) → Register settings → ${slot}.`,
            `Leave the setup state, recall ${slot}, then use Scan & compare for ${profile.title}.`,
            "Resolve readable differences with another scan and manually confirm only the findings Camera Lab identifies as manual, conditional, or unreadable.",
          ]
        : ["Return to Profile Editor and save a foundation profile for this slot before maintaining or re-registering it on the camera."];
      for (const instruction of instructions) {
        const item = document.createElement("li");
        item.textContent = instruction;
        steps.append(item);
      }
      card.append(heading, summary, steps);
      if (profile) {
        const button = document.createElement("button");
        button.className = "secondary cx-open-button";
        button.type = "button";
        button.dataset.cxProfile = profile.name;
        button.textContent = `Open ${slot} checklist`;
        card.append(button);
      }
      return card;
    })
  );
}

async function loadProfiles() {
  try {
    const result = await request("/api/camera-control/profiles");
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select a Subject/Profile Card";
    elements.profileSelect.replaceChildren(
      placeholder,
      ...result.profiles.map((profile) => {
        const option = document.createElement("option");
        option.value = profile.name;
        option.textContent = profile.selector_label || profile.display_title || profile.title;
        return option;
      })
    );
    if (requestedProfileName) {
      const requested = result.profiles.find((profile) => profile.name === requestedProfileName);
      if (requested) {
        elements.profileSelect.value = requested.name;
        setMessage(`${requested.title} was selected by Profile Editor. Connect and scan when ready.`, "info");
      } else {
        setMessage(`The requested saved profile “${requestedProfileName}” is not available in Camera Lab. Select another profile.`, "info");
      }
    }
    renderCxSetup(result.profiles);
    setBusy(requestPending);
  } catch (error) {
    setMessage(error.message);
  }
}

function renderCameraChoices(cameras) {
  selectedCameraIndex = cameras.length === 1 ? cameras[0].index : null;
  elements.cameraChoices.replaceChildren(
    ...cameras.map((camera) => {
      const label = document.createElement("label");
      label.className = "camera-choice";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "camera-index";
      input.value = camera.index;
      input.checked = cameras.length === 1;
      input.addEventListener("change", () => {
        selectedCameraIndex = camera.index;
      });
      const text = document.createElement("span");
      const name = document.createElement("strong");
      name.textContent = camera.product_name || "Unknown Canon camera";
      const detail = document.createElement("small");
      detail.textContent = `Camera index ${camera.index}`;
      text.append(name, detail);
      label.append(input, text);
      return label;
    })
  );
  elements.cameraChoiceCard.hidden = cameras.length === 0 || Boolean(statusState?.connected);
  elements.connectButton.textContent = cameras.length ? "Connect selected camera" : "Connect";
}

function renderEvents(events) {
  if (!events.length) {
    elements.eventLog.innerHTML = '<li class="empty-event">No connection events yet.</li>';
    return;
  }
  elements.eventLog.replaceChildren(
    ...events.map((event) => {
      const item = document.createElement("li");
      item.className = event.kind.includes("error") ? "event error" : "event";
      const time = document.createElement("time");
      time.dateTime = event.time;
      time.textContent = new Date(event.time).toLocaleTimeString([], { hour: "numeric", minute: "2-digit", second: "2-digit" });
      const text = document.createElement("span");
      text.textContent = event.message;
      item.append(time, text);
      return item;
    })
  );
}

async function refreshStatus({ quiet = false } = {}) {
  if (cameraLabStopped || requestPending) return;
  try {
    const [status, events] = await Promise.all([
      request("/api/camera-control/status"),
      request("/api/camera-control/events"),
    ]);
    if (cameraLabStopped || requestPending) return;
    renderStatus(status);
    renderEvents(events.events);
    if (!quiet) setMessage("");
  } catch (error) {
    if (!cameraLabStopped && !requestPending) setMessage(error.message);
  }
}

async function runAction(action) {
  if (requestPending) return;
  setBusy(true);
  setMessage("");
  try {
    await action();
  } catch (error) {
    const cameras = error.payload?.error?.cameras;
    if (Array.isArray(cameras) && cameras.length) renderCameraChoices(cameras);
    setMessage(error.message);
  } finally {
    requestPending = false;
    await refreshStatus({ quiet: true });
    setBusy(false);
  }
}

async function compareSelectedProfile({ recordScan = false } = {}) {
  const profile = elements.profileSelect.value;
  if (!profile) return;
  const query = new URLSearchParams({ profile });
  for (const [path, choice] of Object.entries(contextSelections)) {
    query.append("context", `${path}|${choice}`);
  }
  if (equipmentSelection.choiceKey) query.set("lens_choice", equipmentSelection.choiceKey);
  if (equipmentSelection.isMode) query.set("is_mode", equipmentSelection.isMode);
  const manualContext = sharedManualContext();
  if (manualContext) query.set("manual_context", JSON.stringify(manualContext));
  const result = await request(`/api/camera-control/comparison?${query.toString()}`);
  renderComparison(result, { recordScan });
}

async function scanAndCompare() {
  try {
    const result = await request("/api/camera-control/capabilities");
    renderCapabilities(result);
    await compareSelectedProfile({ recordScan: true });
    if (result.automatic_reconnect_performed) {
      setMessage("The camera session was restored automatically, then the scan and profile comparison were refreshed.", "info");
    }
  } catch (error) {
    showRecoveryInstructions(error.message);
    throw error;
  }
}

elements.discoverButton.addEventListener("click", () => runAction(async () => {
  const result = await request("/api/camera-control/cameras");
  renderCameraChoices(result.cameras);
  if (!result.cameras.length) setMessage("No Canon camera was found in this scenario.", "info");
}));

elements.connectButton.addEventListener("click", () => runAction(async () => {
  await request("/api/camera-control/connect", {
    method: "POST",
    body: JSON.stringify({ camera_index: selectedCameraIndex }),
  });
  elements.cameraChoices.replaceChildren();
}));

elements.disconnectButton.addEventListener("click", () => runAction(async () => {
  await request("/api/camera-control/disconnect", { method: "POST", body: "{}" });
}));

elements.stopCameraLabButton.addEventListener("click", stopCameraLab);
elements.backendSwitchButton.addEventListener("click", showBackendSwitchConfirmation);
elements.backendSwitchConfirm.addEventListener("click", restartWithSelectedBackend);
elements.physicalWriteModeButton.addEventListener("click", showPhysicalWriteModeConfirmation);
elements.physicalWriteModeConfirm.addEventListener("click", restartWithPhysicalWriteMode);

elements.scanButton.addEventListener("click", () => runAction(scanAndCompare));

elements.profileSelect.addEventListener("change", () => {
  contextSelections = {};
  equipmentSelection = { choiceKey: "", isMode: "" };
  comparisonState = null;
  elements.equipmentContext.hidden = true;
  elements.comparisonResults.hidden = true;
  elements.prepareGuardedButton.hidden = true;
  setBusy(requestPending);
  if (elements.profileSelect.value && (statusState?.connected || statusState?.reconnect_available)) {
    runAction(scanAndCompare);
  }
});

elements.lensChoiceSelect.addEventListener("change", () => {
  equipmentSelection.choiceKey = elements.lensChoiceSelect.value;
  equipmentSelection.isMode = "";
  runAction(compareSelectedProfile);
});

elements.isModeSelect.addEventListener("change", () => {
  equipmentSelection.isMode = elements.isModeSelect.value;
  runAction(compareSelectedProfile);
});

elements.cxSlotCards.addEventListener("click", (event) => {
  const button = event.target.closest("[data-cx-profile]");
  if (button) openCxChecklist(button.dataset.cxProfile);
});

elements.compareButton.addEventListener("click", () => runAction(scanAndCompare));
elements.prepareGuardedButton.addEventListener("click", openGuardedPreflight);
elements.guardedLens.addEventListener("change", () => {
  const selected = elements.guardedLens.value;
  equipmentSelection.choiceKey = selected === "__automatic__" ? "" : selected;
  equipmentSelection.isMode = "";
  runAction(async () => {
    await compareSelectedProfile();
    populateGuardedLensOptions(selected);
    if (guardedRunState?.status === "planned") await prepareGuardedRun();
  });
});
elements.guardedPreflightForm.addEventListener("input", persistGuardedPreflight);
elements.guardedPreflightForm.addEventListener("change", (event) => {
  persistGuardedPreflight();
  if (event.target !== elements.guardedLens && guardedRunState?.status === "planned") {
    runAction(prepareGuardedRun);
  }
});
elements.guardedPreflightForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!elements.guardedPreflightForm.reportValidity()) return;
  runAction(prepareGuardedRun);
});
elements.guardedConfirmButton.addEventListener("click", showGuardedConfirmation);
elements.guardedConfirmExecute.addEventListener("click", () => runAction(confirmGuardedRun));
elements.guardedNextButton.addEventListener("click", () => runAction(executeNextGuardedStep));
elements.guardedResumeButton.addEventListener("click", () => runAction(resumeGuardedRun));
elements.guardedAbortButton.addEventListener("click", () => runAction(abortGuardedRun));
elements.writeQualificationProperty.addEventListener("change", () => updateWriteQualificationTargets());
elements.writeQualificationPrepare.addEventListener("click", () => runAction(prepareWriteQualification));
elements.writeQualificationConfirm.addEventListener("click", showWriteQualificationConfirmation);
elements.writeQualificationDialogConfirm.addEventListener("click", () => runAction(confirmWriteQualification));
elements.writeQualificationExecute.addEventListener("click", () => runAction(executeWriteQualification));

elements.checklistRescanButton.addEventListener("click", () => runAction(scanAndCompare));

elements.checklistClearButton.addEventListener("click", () => {
  const record = activeChecklistRecord();
  const sharedFindings = allComparisonFindings().filter((finding) => finding.shared_manual_confirmation);
  if ((!record || !Object.keys(record.confirmations || {}).length) && !sharedFindings.length) return;
  if (!window.confirm("Clear every saved manual confirmation for this profile and camera context?")) return;
  if (record) record.confirmations = {};
  saveChecklistState();
  runAction(async () => {
    for (const finding of sharedFindings) await revokeSharedManualConfirmation(finding);
    await compareSelectedProfile();
  });
});

elements.comparisonOrder.addEventListener("change", renderComparisonTables);

function updateFloatingReturn() {
  elements.returnToTop.hidden = window.scrollY < 280;
}

elements.returnToTop.addEventListener("click", () => elements.comparisonPanel.scrollIntoView({ behavior: "smooth", block: "start" }));
window.addEventListener("scroll", updateFloatingReturn, { passive: true });

elements.recoveryRetryButton.addEventListener("click", () => {
  elements.recoveryDialog.close();
  runAction(scanAndCompare);
});

elements.refreshButton.addEventListener("click", () => refreshStatus());

elements.applyScenarioButton.addEventListener("click", () => runAction(async () => {
  await request("/api/camera-control/simulation-scenario", {
    method: "POST",
    body: JSON.stringify({ scenario: elements.scenarioSelect.value }),
  });
  elements.cameraChoices.replaceChildren();
  guardedRunState = null;
  elements.guardedPreview.hidden = true;
}));

elements.simulateDisconnectButton.addEventListener("click", () => runAction(async () => {
  await request("/api/camera-control/simulate-disconnect", { method: "POST", body: "{}" });
}));

loadProfiles();
refreshStatus();
updateFloatingReturn();
statusPollId = window.setInterval(() => refreshStatus({ quiet: true }), 2500);
