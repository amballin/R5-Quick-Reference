const token = document.querySelector('meta[name="camera-lab-token"]').content;
const requestedProfileName = new URLSearchParams(window.location.search).get("profile");

const elements = {
  backendBadge: document.querySelector("#backend-badge"),
  projectContextBadge: document.querySelector("#project-context-badge"),
  cameraLabVersion: document.querySelector("#camera-lab-version"),
  cameraLabSourceHash: document.querySelector("#camera-lab-source-hash"),
  backendSwitchButton: document.querySelector("#backend-switch-button"),
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
  sdkMode: document.querySelector("#sdk-mode"),
  sdkVersion: document.querySelector("#sdk-version"),
  sdkPath: document.querySelector("#sdk-path"),
  simulationPanel: document.querySelector("#simulation-panel"),
  scenarioSelect: document.querySelector("#scenario-select"),
  applyScenarioButton: document.querySelector("#apply-scenario-button"),
  simulateDisconnectButton: document.querySelector("#simulate-disconnect-button"),
  eventLog: document.querySelector("#event-log"),
  connectStep: document.querySelector("#connect-step"),
  discoverStep: document.querySelector("#discover-step"),
  compareStep: document.querySelector("#compare-step"),
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
  comparisonResults: document.querySelector("#comparison-results"),
  comparisonSummary: document.querySelector("#comparison-summary"),
  comparisonOrder: document.querySelector("#comparison-order"),
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
};

let statusState = null;
let comparisonState = null;
let selectedCameraIndex = null;
let requestPending = false;
let cameraLabStopped = false;
let statusPollId = null;
let contextSelections = {};
let requestedBackendMode = null;
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
  const recordKey = `${cameraContextKey()}|${profileName}`;
  if (!checklistState.profiles[recordKey] && create) {
    checklistState.profiles[recordKey] = { profile: profileName, camera_context: cameraContextKey(), confirmations: {}, last_scan_at: null };
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
  return activeChecklistRecord()?.confirmations?.[checklistFindingKey(finding)] || null;
}

function setManualConfirmation(finding, confirmed) {
  const record = activeChecklistRecord(true);
  const key = checklistFindingKey(finding);
  if (confirmed) {
    record.confirmations[key] = {
      evidence_method: "manual_user_confirmed",
      confirmed_at: new Date().toISOString(),
      expected: finding.expected,
    };
  } else {
    delete record.confirmations[key];
  }
  saveChecklistState();
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

async function waitForBackendRestart(backend) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 150));
    try {
      const response = await fetch("/api/camera-control/status", { cache: "no-store" });
      if (!response.ok) continue;
      const payload = await response.json();
      if (payload.backend_mode === backend) {
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
      body: JSON.stringify({ backend }),
    });
    if (!result.restarting || !result.camera_session_closed) {
      throw new Error("Camera Lab did not confirm a safe backend restart.");
    }
    await waitForBackendRestart(backend);
  } catch (error) {
    requestedBackendMode = null;
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
  elements.backendSwitchButton.textContent = status.backend_mode === "simulated" ? "Use Camera" : "Use Simulator";
  elements.statusDot.classList.toggle("connected", connected);
  elements.statusDot.classList.toggle("error", !connected && Boolean(status.last_error));
  elements.connectionTitle.textContent = connected ? "EOS R5 connected" : "Camera not connected";
  elements.connectionMessage.textContent = connected
    ? "The USB session is open and responding. Camera settings remain unchanged."
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

  const sdk = status.sdk || {};
  elements.sdkMode.textContent = status.backend_mode === "simulated" ? "Simulation" : "Physical camera";
  elements.sdkVersion.textContent = valueOrUnavailable(sdk.framework_version);
  elements.sdkPath.textContent = valueOrUnavailable(sdk.path);

  elements.simulationPanel.hidden = status.backend_mode !== "simulated";
  elements.connectStep.classList.toggle("active", !connected);
  elements.discoverStep.classList.toggle("active", connected);
  elements.discoverStep.classList.toggle("locked", !connected);
  elements.compareStep.classList.toggle("locked", !Boolean(status.capabilities));
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
      write.textContent = "Unverified";
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
    checkbox.checked = Boolean(manualConfirmation(finding));
    checkbox.addEventListener("change", () => {
      setManualConfirmation(finding, checkbox.checked);
      renderComparisonTables();
      renderChecklistSummary();
    });
    const text = document.createElement("span");
    text.textContent = "Reviewed/set manually";
    const evidence = document.createElement("small");
    evidence.textContent = checkbox.checked
      ? "Saved as manual_user_confirmed"
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
  const record = activeChecklistRecord(true);
  if (recordScan) record.last_scan_at = new Date().toISOString();
  saveChecklistState();
  elements.comparisonResults.hidden = false;
  elements.comparisonSummary.textContent = `${comparison.profile.display_title || comparison.profile.title}: ${comparison.summary.card_rows} card rows followed by ${comparison.summary.additional_settings} additional settings. Camera settings were not changed.`;
  renderComparisonTables();
  renderChecklistSummary();
  elements.compareStep.classList.remove("locked");
  elements.compareStep.classList.add("active");
}

function openCxChecklist(profileName) {
  const option = [...elements.profileSelect.options].find((item) => item.value === profileName);
  if (!option) return;
  elements.profileSelect.value = profileName;
  contextSelections = {};
  comparisonState = null;
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

elements.scanButton.addEventListener("click", () => runAction(scanAndCompare));

elements.profileSelect.addEventListener("change", () => {
  contextSelections = {};
  comparisonState = null;
  elements.comparisonResults.hidden = true;
  setBusy(requestPending);
});

elements.cxSlotCards.addEventListener("click", (event) => {
  const button = event.target.closest("[data-cx-profile]");
  if (button) openCxChecklist(button.dataset.cxProfile);
});

elements.compareButton.addEventListener("click", () => runAction(scanAndCompare));

elements.checklistRescanButton.addEventListener("click", () => runAction(scanAndCompare));

elements.checklistClearButton.addEventListener("click", () => {
  const record = activeChecklistRecord();
  if (!record || !Object.keys(record.confirmations || {}).length) return;
  if (!window.confirm("Clear every saved manual confirmation for this profile and camera context?")) return;
  record.confirmations = {};
  saveChecklistState();
  renderComparisonTables();
  renderChecklistSummary();
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
}));

elements.simulateDisconnectButton.addEventListener("click", () => runAction(async () => {
  await request("/api/camera-control/simulate-disconnect", { method: "POST", body: "{}" });
}));

loadProfiles();
refreshStatus();
updateFloatingReturn();
statusPollId = window.setInterval(() => refreshStatus({ quiet: true }), 2500);
