const token = document.querySelector('meta[name="camera-lab-token"]').content;

const elements = {
  backendBadge: document.querySelector("#backend-badge"),
  cameraLabBuild: document.querySelector("#camera-lab-build"),
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
  profileSelect: document.querySelector("#profile-select"),
  compareButton: document.querySelector("#compare-button"),
  comparisonResults: document.querySelector("#comparison-results"),
  comparisonSummary: document.querySelector("#comparison-summary"),
  comparisonOrder: document.querySelector("#comparison-order"),
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
};

let statusState = null;
let comparisonState = null;
let selectedCameraIndex = null;
let requestPending = false;

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
  elements.disconnectButton.disabled = busy;
  elements.refreshButton.disabled = busy;
  elements.applyScenarioButton.disabled = busy;
  elements.simulateDisconnectButton.disabled = busy || !statusState?.connected;
}

function renderStatus(status) {
  statusState = status;
  const connected = Boolean(status.connected);
  const reconnectAvailable = Boolean(status.reconnect_available);
  const app = status.app || {};
  elements.cameraLabBuild.textContent = app.version && app.build
    ? `Camera Lab ${app.version} · Build ${app.build}`
    : "Camera Lab build unavailable";
  elements.backendBadge.textContent = status.backend_mode === "simulated" ? "Simulated camera" : "Canon EDSDK";
  elements.backendBadge.classList.toggle("live", status.backend_mode === "edsdk");
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
  heading.colSpan = 4;
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
  row.append(expected, camera, statusCell, access);
  return row;
}

function findingTable(findings, cardRows = false) {
  const wrapper = document.createElement("div");
  wrapper.className = "comparison-table-scroll";
  const table = document.createElement("table");
  table.className = "comparison-table";
  const head = document.createElement("thead");
  const headingRow = document.createElement("tr");
  for (const label of ["Card Expected", "Camera", "Status", "Optimal Access Path"]) {
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

function renderComparison(comparison) {
  comparisonState = comparison;
  elements.comparisonResults.hidden = false;
  elements.comparisonSummary.textContent = `${comparison.profile.display_title || comparison.profile.title}: ${comparison.summary.card_rows} card rows followed by ${comparison.summary.additional_settings} additional settings. Camera settings were not changed.`;
  renderComparisonTables();
  elements.compareStep.classList.remove("locked");
  elements.compareStep.classList.add("active");
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
        option.textContent = profile.display_title || profile.title;
        return option;
      })
    );
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
  try {
    const [status, events] = await Promise.all([
      request("/api/camera-control/status"),
      request("/api/camera-control/events"),
    ]);
    renderStatus(status);
    renderEvents(events.events);
    if (!quiet) setMessage("");
  } catch (error) {
    setMessage(error.message);
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

async function compareSelectedProfile() {
  const profile = elements.profileSelect.value;
  if (!profile) return;
  const result = await request(`/api/camera-control/comparison?profile=${encodeURIComponent(profile)}`);
  renderComparison(result);
}

async function scanAndCompare() {
  try {
    const result = await request("/api/camera-control/capabilities");
    renderCapabilities(result);
    await compareSelectedProfile();
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

elements.scanButton.addEventListener("click", () => runAction(scanAndCompare));

elements.profileSelect.addEventListener("change", () => setBusy(requestPending));

elements.compareButton.addEventListener("click", () => runAction(scanAndCompare));

elements.comparisonOrder.addEventListener("change", renderComparisonTables);

function updateFloatingReturn() {
  elements.returnToTop.hidden = window.scrollY < 280;
}

elements.returnToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
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
window.setInterval(() => refreshStatus({ quiet: true }), 2500);
