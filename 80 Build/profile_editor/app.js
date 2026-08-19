const elements = {
  viewTabs: [...document.querySelectorAll(".view-tab")],
  views: [...document.querySelectorAll(".app-view")],
  dictionarySource: document.querySelector("#dictionary-source"),
  dictionarySearch: document.querySelector("#dictionary-search"),
  dictionaryClassification: document.querySelector("#dictionary-classification"),
  dictionaryCount: document.querySelector("#dictionary-count"),
  dictionarySections: document.querySelector("#dictionary-sections"),
  loadRecommendedMenus: document.querySelector("#load-recommended-menus"),
  myMenuTabs: document.querySelector("#my-menu-tabs"),
  profileSelect: document.querySelector("#profile-select"),
  newButton: document.querySelector("#new-button"),
  duplicateButton: document.querySelector("#duplicate-button"),
  reloadButton: document.querySelector("#reload-button"),
  previewButton: document.querySelector("#preview-button"),
  reviewButton: document.querySelector("#review-button"),
  profileMetadata: document.querySelector("#profile-metadata"),
  operationTitle: document.querySelector("#operation-title"),
  operationNote: document.querySelector("#operation-note"),
  titleInput: document.querySelector("#title-input"),
  subtitleInput: document.querySelector("#subtitle-input"),
  filenameInput: document.querySelector("#filename-input"),
  statusInput: document.querySelector("#status-input"),
  releaseInput: document.querySelector("#release-input"),
  profileTitle: document.querySelector("#profile-title"),
  sourceFile: document.querySelector("#source-file"),
  customCount: document.querySelector("#custom-count"),
  inheritedCount: document.querySelector("#inherited-count"),
  settings: document.querySelector("#settings"),
  message: document.querySelector("#message"),
  referenceCard: document.querySelector("#reference-card"),
  previewPanel: document.querySelector("#preview-panel"),
  previewFrame: document.querySelector("#preview-frame"),
  previewPath: document.querySelector("#preview-path"),
  reviewDialog: document.querySelector("#review-dialog"),
  reviewSummary: document.querySelector("#review-summary"),
  reviewDiff: document.querySelector("#review-diff"),
  reviewClose: document.querySelector("#review-close"),
  reviewCancel: document.querySelector("#review-cancel"),
  saveButton: document.querySelector("#save-button"),
  baselineReset: document.querySelector("#baseline-reset"),
  baselineAnalyze: document.querySelector("#baseline-analyze"),
  baselineMessage: document.querySelector("#baseline-message"),
  baselineSummary: document.querySelector("#baseline-summary"),
  baselineDecisionTools: document.querySelector("#baseline-decision-tools"),
  baselineDecisionStatus: document.querySelector("#baseline-decision-status"),
  baselineFollowAll: document.querySelector("#baseline-follow-all"),
  baselinePreserveAll: document.querySelector("#baseline-preserve-all"),
  baselineBuildPlan: document.querySelector("#baseline-build-plan"),
  baselineBuildPlanBottomRow: document.querySelector("#baseline-build-plan-bottom-row"),
  baselineBuildPlanBottom: document.querySelector("#baseline-build-plan-bottom"),
  baselineResults: document.querySelector("#baseline-results"),
  baselinePlan: document.querySelector("#baseline-plan"),
  baselineSettings: document.querySelector("#baseline-settings"),
};

const state = {
  dictionary: null,
  myMenus: Array.from({ length: 5 }, () => ({ name: "", items: Array(6).fill("") })),
  detail: null,
  originalOverrides: {},
  draftOverrides: {},
  reviewToken: null,
  loadSequence: 0,
  baselineDetail: null,
  baselineCurrent: {},
  baselineDraft: {},
  baselineAnalysis: null,
  baselineDecisions: {},
  baselinePlan: null,
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function equal(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function displayValue(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "True" : "False";
  return String(value);
}

async function request(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "The prototype could not complete the request.");
  return payload;
}

function showMessage(text, error = false) {
  elements.message.textContent = text;
  elements.message.classList.toggle("error", error);
  elements.message.hidden = !text;
}

function showBaselineMessage(text, error = false) {
  elements.baselineMessage.textContent = text;
  elements.baselineMessage.classList.toggle("error", error);
  elements.baselineMessage.hidden = !text;
}

async function loadProfiles(selectedName = null, loadSelection = true) {
  try {
    const payload = await request("/api/profiles");
    elements.profileSelect.replaceChildren();
    for (const profile of payload.profiles) {
      const option = document.createElement("option");
      option.value = profile.name;
      option.textContent = profile.cardType === "reference" ? `${profile.title} (reference)` : profile.title;
      elements.profileSelect.append(option);
    }
    elements.profileSelect.disabled = false;
    const selected = payload.profiles.find((profile) => profile.name === selectedName) || payload.profiles[0];
    if (selected) {
      elements.profileSelect.value = selected.name;
      if (loadSelection) await loadProfile(selected.name);
    }
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function loadDictionary() {
  try {
    state.dictionary = await request("/api/dictionary");
    elements.dictionarySource.href = state.dictionary.metadata.authority_url || "https://cam.start.canon/en/C003/manual/html/index.html";
    loadRecommendedMenus(false);
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function loadBaseline() {
  showBaselineMessage("Loading the current baseline…");
  try {
    const detail = await request("/api/baseline");
    state.baselineDetail = detail;
    state.baselineCurrent = clone(detail.values || {});
    state.baselineDraft = clone(state.baselineCurrent);
    state.baselineAnalysis = null;
    state.baselineDecisions = {};
    state.baselinePlan = null;
    renderBaseline();
    showBaselineMessage("No proposed baseline changes. This workspace is read-only.");
  } catch (error) {
    showBaselineMessage(error.message, true);
  }
}

function switchView(viewName) {
  for (const tab of elements.viewTabs) tab.classList.toggle("is-active", tab.dataset.view === viewName);
  for (const view of elements.views) view.hidden = view.id !== `${viewName}-view`;
}

function configuredShortcuts() {
  const paths = new Map();
  state.myMenus.forEach((tab, tabIndex) => {
    const tabName = tab.name.trim() || `MY MENU${tabIndex + 1}`;
    tab.items.forEach((itemId) => {
      if (itemId) paths.set(itemId, `${tabName} → ${dictionaryItem(itemId)?.label || itemId}`);
    });
  });
  return paths;
}

function dictionaryItem(itemId) {
  for (const section of state.dictionary?.sections || []) {
    const item = section.items.find((candidate) => candidate.id === itemId);
    if (item) return item;
  }
  return null;
}

function renderDictionary() {
  if (!state.dictionary) return;
  const query = elements.dictionarySearch.value.trim().toLocaleLowerCase();
  const classification = elements.dictionaryClassification.value;
  const shortcuts = configuredShortcuts();
  let visibleCount = 0;
  let totalCount = 0;
  elements.dictionarySections.replaceChildren();
  for (const section of state.dictionary.sections) {
    totalCount += section.items.length;
    const matching = section.items.filter((item) => {
      const searchable = [item.label, item.menu_location, item.recommended, item.note].join(" ").toLocaleLowerCase();
      return (!query || searchable.includes(query)) && (!classification || item.classification === classification);
    });
    if (!matching.length) continue;
    visibleCount += matching.length;
    const fragment = document.querySelector("#dictionary-section-template").content.cloneNode(true);
    fragment.querySelector("h2").textContent = section.label;
    fragment.querySelector(".section-source").href = section.source;
    const list = fragment.querySelector(".dictionary-list");
    for (const item of matching) list.append(renderDictionaryItem(item, shortcuts.get(item.id)));
    elements.dictionarySections.append(fragment);
  }
  elements.dictionaryCount.textContent = `${visibleCount} of ${totalCount} settings shown`;
}

function renderDictionaryItem(item, shortcut) {
  const fragment = document.querySelector("#dictionary-item-template").content.cloneNode(true);
  fragment.querySelector("h3").textContent = item.label;
  fragment.querySelector(".menu-location").textContent = item.menu_location;
  const badge = fragment.querySelector(".classification-badge");
  badge.textContent = item.classification;
  badge.dataset.classification = item.classification;
  fragment.querySelector(".canon-default").textContent = item.canon_default;
  fragment.querySelector(".recommended").textContent = item.recommended;
  fragment.querySelector(".visit-again").textContent = item.visit_again;
  const shortcutDetail = fragment.querySelector(".shortcut-detail");
  if (shortcut) {
    fragment.querySelector(".shortcut-path").textContent = shortcut;
    shortcutDetail.hidden = false;
  }
  const note = fragment.querySelector(".dictionary-note");
  note.textContent = item.note || "";
  note.hidden = !item.note;
  fragment.querySelector(".item-source").href = item.source;
  return fragment;
}

function renderMyMenus() {
  if (!state.dictionary) return;
  elements.myMenuTabs.replaceChildren();
  const selected = new Set(state.myMenus.flatMap((tab) => tab.items).filter(Boolean));
  state.myMenus.forEach((tab, tabIndex) => {
    const fragment = document.querySelector("#my-menu-tab-template").content.cloneNode(true);
    fragment.querySelector(".my-menu-number").textContent = `MY MENU${tabIndex + 1}`;
    const name = fragment.querySelector(".my-menu-name");
    name.value = tab.name;
    name.placeholder = `Tab ${tabIndex + 1}`;
    name.addEventListener("input", () => {
      tab.name = name.value;
      myMenuDraftChanged();
      renderDictionary();
    });
    const items = fragment.querySelector(".my-menu-items");
    tab.items.forEach((itemId, itemIndex) => {
      const label = document.createElement("label");
      label.textContent = `Item ${itemIndex + 1}`;
      const select = document.createElement("select");
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "— Empty —";
      select.append(empty);
      for (const item of state.dictionary.myMenuEligible) {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = `${item.label} · ${item.menuLocation}`;
        option.selected = item.id === itemId;
        option.disabled = selected.has(item.id) && item.id !== itemId;
        select.append(option);
      }
      select.addEventListener("change", () => {
        tab.items[itemIndex] = select.value;
        myMenuDraftChanged();
        renderMyMenus();
        renderDictionary();
      });
      label.append(select);
      items.append(label);
    });
    elements.myMenuTabs.append(fragment);
  });
}

function loadRecommendedMenus(invalidateAnalysis = true) {
  state.myMenus = Array.from({ length: 5 }, () => ({ name: "", items: Array(6).fill("") }));
  (state.dictionary?.myMenu?.recommended_tabs || []).slice(0, 5).forEach((tab, index) => {
    state.myMenus[index].name = tab.name;
    tab.items.slice(0, 6).forEach((itemId, itemIndex) => { state.myMenus[index].items[itemIndex] = itemId; });
  });
  if (invalidateAnalysis) myMenuDraftChanged();
  renderMyMenus();
  renderDictionary();
}

function myMenuDraftChanged() {
  if (!state.baselineAnalysis) return;
  baselineDraftChanged();
  updateBaselineDraftState();
}

async function loadProfile(name) {
  const loadSequence = ++state.loadSequence;
  showMessage("");
  elements.profileSelect.disabled = true;
  elements.reloadButton.disabled = true;
  elements.previewButton.disabled = true;
  try {
    const detail = await request(`/api/profiles/${encodeURIComponent(name)}`);
    if (loadSequence !== state.loadSequence) return;
    elements.profileSelect.value = name;
    applyProfileDetail(detail);
  } catch (error) {
    if (loadSequence !== state.loadSequence) return;
    showMessage(error.message, true);
  } finally {
    if (loadSequence === state.loadSequence) elements.profileSelect.disabled = false;
  }
}

async function loadProfileDraft(operation) {
  const sourceProfile = operation === "duplicate" ? state.detail?.sourceProfile || state.detail?.name : null;
  if (operation === "duplicate" && !state.detail?.editableDraft) return;
  disableProfileActions(true);
  showMessage(operation === "duplicate" ? "Preparing a duplicate draft…" : "Preparing a baseline-derived draft…");
  try {
    const detail = await request("/api/profile-drafts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ operation, sourceProfile }),
    });
    applyProfileDetail(detail);
    elements.profileSelect.value = "";
    elements.titleInput.focus();
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    disableProfileActions(false);
  }
}

function applyProfileDetail(detail) {
  state.detail = detail;
  state.originalOverrides = clone(detail.originalOverrides || {});
  state.draftOverrides = clone(state.originalOverrides);
  state.reviewToken = null;
  elements.profileTitle.textContent = detail.title;
  elements.sourceFile.textContent = detail.sourceFile;
  elements.titleInput.value = detail.title || "";
  elements.subtitleInput.value = detail.subtitle || "";
  elements.filenameInput.value = detail.targetName || detail.name || "";
  elements.statusInput.value = detail.metadata?.status || "Draft";
  elements.releaseInput.checked = Boolean(detail.metadata?.release);
  elements.previewPanel.hidden = true;
  if (elements.reviewDialog.open) elements.reviewDialog.close();
  render();
}

function disableProfileActions(disabled) {
  elements.newButton.disabled = disabled;
  elements.duplicateButton.disabled = disabled || !state.detail?.editableDraft;
  elements.reloadButton.disabled = disabled || !state.detail?.editableDraft;
  elements.previewButton.disabled = disabled || !state.detail?.editableDraft;
  elements.reviewButton.disabled = disabled || !state.detail?.editableDraft;
}

function render() {
  elements.settings.replaceChildren();
  elements.referenceCard.hidden = true;
  const editable = state.detail?.editableDraft;
  elements.profileMetadata.hidden = !editable;
  elements.duplicateButton.disabled = !editable;
  elements.reloadButton.disabled = !editable;
  elements.previewButton.disabled = !editable;
  elements.reviewButton.disabled = !editable;
  if (!editable) {
    renderReference();
    elements.customCount.textContent = "0";
    elements.inheritedCount.textContent = "0";
    showMessage("This reference card remains read-only. Stage 2 saves apply only to shooting profiles.");
    return;
  }
  renderMetadataState();
  showMessage("");
  for (const section of state.detail.sections) renderSection(section);
  updateCounts();
}

function renderMetadataState() {
  const operation = state.detail.operation || "update";
  const creating = operation !== "update";
  elements.operationTitle.textContent = operation === "update"
    ? "Update existing profile"
    : operation === "duplicate" ? "Duplicate shooting profile" : "Create from baseline";
  elements.operationNote.textContent = operation === "update"
    ? "The existing filename is preserved."
    : "New profiles are saved as Draft and excluded from release.";
  elements.filenameInput.disabled = !creating;
  elements.statusInput.disabled = creating;
  elements.releaseInput.disabled = creating;
  elements.profileTitle.textContent = elements.titleInput.value.trim() || "Untitled profile";
  elements.sourceFile.textContent = operation === "update"
    ? `10 Profiles/${state.detail.name}.yaml`
    : `Proposed: 10 Profiles/${elements.filenameInput.value.trim() || "Untitled"}.yaml`;
}

function renderReference() {
  const intro = document.createElement("p");
  intro.textContent = "Reference-card assignments";
  const table = document.createElement("table");
  const body = document.createElement("tbody");
  for (const item of state.detail.referenceSettings || []) {
    const row = document.createElement("tr");
    const control = document.createElement("th");
    const assignment = document.createElement("td");
    control.textContent = item.control;
    assignment.textContent = item.assignment;
    row.append(control, assignment);
    body.append(row);
  }
  table.append(body);
  elements.referenceCard.replaceChildren(intro, table);
  elements.referenceCard.hidden = false;
}

function renderSection(section) {
  const fragment = document.querySelector("#section-template").content.cloneNode(true);
  const container = fragment.querySelector(".setting-section");
  fragment.querySelector("h2").textContent = section.label;
  fragment.querySelector(".reset-section").addEventListener("click", () => {
    for (const setting of section.settings) delete state.draftOverrides[setting.path];
    draftChanged();
    render();
  });
  const list = fragment.querySelector(".setting-list");
  for (const setting of section.settings) list.append(renderSetting(setting));
  elements.settings.append(container);
}

function renderSetting(setting) {
  const fragment = document.querySelector("#setting-template").content.cloneNode(true);
  const row = fragment.querySelector(".setting-row");
  const label = fragment.querySelector("label");
  const path = fragment.querySelector("code");
  const controlHost = fragment.querySelector(".setting-control");
  const icon = fragment.querySelector(".field-icon");
  const reset = fragment.querySelector(".reset-setting");
  label.textContent = setting.label;
  path.textContent = setting.path;
  const hasOverride = Object.hasOwn(state.draftOverrides, setting.path);
  const value = hasOverride ? state.draftOverrides[setting.path] : setting.baseline;
  const { control, datalist } = buildControl(setting, value);
  const controlId = `setting-${setting.path.replaceAll(".", "-")}`;
  control.id = controlId;
  label.htmlFor = controlId;
  control.addEventListener("change", () => updateSetting(setting, readControl(control, setting)));
  if (control.tagName === "INPUT") control.addEventListener("input", () => updateSetting(setting, readControl(control, setting), false));
  controlHost.append(control);
  if (datalist) controlHost.append(datalist);
  if (setting.catalogNote) {
    const note = document.createElement("small");
    note.className = "catalog-note";
    note.textContent = setting.catalogNote;
    controlHost.append(note);
  }
  const iconUrl = iconForValue(setting, value);
  if (iconUrl) {
    icon.src = iconUrl;
    icon.hidden = false;
  }
  row.classList.toggle("is-custom", hasOverride);
  const badge = fragment.querySelector(".state-badge");
  badge.textContent = hasOverride ? "Customized" : "Inherited";
  fragment.querySelector(".baseline-value").textContent = `Baseline: ${displayValue(setting.baseline)}`;
  const canonSource = fragment.querySelector(".canon-source");
  if (setting.catalogSource) {
    canonSource.href = setting.catalogSource;
    canonSource.hidden = false;
  }
  reset.disabled = !hasOverride;
  reset.addEventListener("click", () => {
    delete state.draftOverrides[setting.path];
    draftChanged();
    render();
  });
  return row;
}

function baselineChangedPaths() {
  return Object.keys(state.baselineCurrent).filter(
    (path) => !equal(state.baselineCurrent[path], state.baselineDraft[path]),
  );
}

function renderBaseline() {
  if (!state.baselineDetail) return;
  elements.baselineSettings.replaceChildren();
  for (const section of state.baselineDetail.sections) renderBaselineSection(section);
  updateBaselineDraftState();
  renderBaselineAnalysis();
}

function renderBaselineSection(section) {
  const fragment = document.querySelector("#section-template").content.cloneNode(true);
  const container = fragment.querySelector(".setting-section");
  fragment.querySelector("h2").textContent = section.label;
  const reset = fragment.querySelector(".reset-section");
  reset.textContent = "Restore current section";
  reset.disabled = !section.settings.some(
    (setting) => !equal(state.baselineCurrent[setting.path], state.baselineDraft[setting.path]),
  );
  reset.addEventListener("click", () => {
    for (const setting of section.settings) {
      state.baselineDraft[setting.path] = clone(state.baselineCurrent[setting.path]);
    }
    baselineDraftChanged();
    renderBaseline();
  });
  const list = fragment.querySelector(".setting-list");
  for (const setting of section.settings) list.append(renderBaselineSetting(setting));
  elements.baselineSettings.append(container);
}

function renderBaselineSetting(setting) {
  const fragment = document.querySelector("#setting-template").content.cloneNode(true);
  const row = fragment.querySelector(".setting-row");
  const label = fragment.querySelector("label");
  const path = fragment.querySelector("code");
  const controlHost = fragment.querySelector(".setting-control");
  const icon = fragment.querySelector(".field-icon");
  const reset = fragment.querySelector(".reset-setting");
  const current = state.baselineCurrent[setting.path];
  const value = state.baselineDraft[setting.path];
  const changed = !equal(current, value);
  label.textContent = setting.label;
  path.textContent = setting.path;
  const { control, datalist } = buildControl(setting, value);
  const controlId = `baseline-setting-${setting.path.replaceAll(".", "-")}`;
  control.id = controlId;
  label.htmlFor = controlId;
  control.addEventListener("change", () => updateBaselineSetting(setting, readControl(control, setting)));
  if (control.tagName === "INPUT") {
    control.addEventListener("input", () => updateBaselineSetting(setting, readControl(control, setting), false));
  }
  controlHost.append(control);
  if (datalist) controlHost.append(datalist);
  if (setting.catalogNote) {
    const note = document.createElement("small");
    note.className = "catalog-note";
    note.textContent = setting.catalogNote;
    controlHost.append(note);
  }
  const iconUrl = iconForValue(setting, value);
  if (iconUrl) {
    icon.src = iconUrl;
    icon.hidden = false;
  }
  row.classList.toggle("is-custom", changed);
  fragment.querySelector(".state-badge").textContent = changed ? "Proposed" : "Current";
  fragment.querySelector(".baseline-value").textContent = `Current: ${displayValue(current)}`;
  const canonSource = fragment.querySelector(".canon-source");
  if (setting.catalogSource) {
    canonSource.href = setting.catalogSource;
    canonSource.hidden = false;
  }
  reset.textContent = "Restore current";
  reset.disabled = !changed;
  reset.addEventListener("click", () => {
    state.baselineDraft[setting.path] = clone(current);
    baselineDraftChanged();
    renderBaseline();
  });
  return row;
}

function updateBaselineSetting(setting, value, rerender = true) {
  state.baselineDraft[setting.path] = value;
  baselineDraftChanged();
  if (rerender) renderBaseline();
  else updateBaselineDraftState();
}

function baselineDraftChanged() {
  state.baselineAnalysis = null;
  state.baselineDecisions = {};
  state.baselinePlan = null;
  elements.baselineSummary.hidden = true;
  elements.baselineSummary.replaceChildren();
  elements.baselineDecisionTools.hidden = true;
  elements.baselineBuildPlanBottomRow.hidden = true;
  elements.baselineResults.replaceChildren();
  elements.baselinePlan.hidden = true;
  elements.baselinePlan.replaceChildren();
}

function updateBaselineDraftState() {
  const changed = baselineChangedPaths().length;
  elements.baselineAnalyze.disabled = changed === 0;
  elements.baselineReset.disabled = changed === 0;
  if (changed === 0) {
    showBaselineMessage("No proposed baseline changes. This workspace is read-only.");
  } else {
    showBaselineMessage(`${changed} proposed baseline ${changed === 1 ? "change" : "changes"}. Analyze the draft to review profile impact.`);
  }
}

async function analyzeBaselineDraft() {
  elements.baselineAnalyze.disabled = true;
  showBaselineMessage("Calculating effective values for every inheriting profile…");
  try {
    state.baselineAnalysis = await request("/api/baseline-impact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ values: state.baselineDraft, myMenuTabs: state.myMenus }),
    });
    state.baselineDecisions = {};
    state.baselinePlan = null;
    renderBaselineAnalysis();
    showBaselineMessage("Impact analysis complete. Nothing was saved.");
    elements.baselineSummary.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    state.baselineAnalysis = null;
    state.baselineDecisions = {};
    state.baselinePlan = null;
    renderBaselineAnalysis();
    showBaselineMessage(error.message, true);
  } finally {
    elements.baselineAnalyze.disabled = baselineChangedPaths().length === 0;
  }
}

function renderBaselineAnalysis() {
  elements.baselineSummary.replaceChildren();
  elements.baselineResults.replaceChildren();
  elements.baselinePlan.hidden = true;
  elements.baselinePlan.replaceChildren();
  const analysis = state.baselineAnalysis;
  if (!analysis) {
    elements.baselineSummary.hidden = true;
    elements.baselineDecisionTools.hidden = true;
    elements.baselineBuildPlanBottomRow.hidden = true;
    return;
  }
  const summaryItems = [
    ["Changed settings", analysis.summary.changed_settings],
    ["Affected profiles", analysis.summary.affected_profiles],
    ["Need decisions", analysis.summary.profiles_requiring_decision],
    ["Redundant overrides", analysis.summary.classifications.override_redundant || 0],
  ];
  for (const [label, value] of summaryItems) {
    const item = document.createElement("div");
    const count = document.createElement("strong");
    const caption = document.createElement("span");
    count.textContent = String(value);
    caption.textContent = label;
    item.append(count, caption);
    elements.baselineSummary.append(item);
  }
  elements.baselineSummary.hidden = false;
  if (analysis.cx_impact) elements.baselineResults.append(renderCxImpact(analysis.cx_impact));
  if (analysis.my_menu_impact) elements.baselineResults.append(renderMyMenuImpact(analysis.my_menu_impact));
  for (const change of analysis.changes) elements.baselineResults.append(renderImpactChange(change));
  elements.baselineDecisionTools.hidden = false;
  elements.baselineBuildPlanBottomRow.hidden = false;
  updateBaselineDecisionState();
}

const impactLabels = {
  inherited_change: "Would follow the proposed baseline",
  override_protected: "Protected by an existing override",
  override_redundant: "Override would become redundant",
  override_invalid_path: "Override path would be invalid",
  override_invalid_type: "Override type would be invalid",
};

function baselineSettingLabel(path) {
  for (const section of state.baselineDetail?.sections || []) {
    const setting = section.settings.find((candidate) => candidate.path === path);
    if (setting) return setting.label;
  }
  return path.split(".").at(-1).replaceAll("_", " ");
}

function renderCxImpact(cxImpact) {
  const article = document.createElement("article");
  article.className = "cx-impact";
  const heading = document.createElement("div");
  heading.className = "cx-impact-heading";
  const headingCopy = document.createElement("div");
  const eyebrow = document.createElement("p");
  const title = document.createElement("h3");
  const summary = document.createElement("strong");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Registration warning report";
  title.textContent = "C1–C3 effective impact";
  summary.textContent = `${cxImpact.summary.affected_registered_modes} modes · ${cxImpact.summary.profiles_with_affected_starting_mode} routed profiles affected`;
  headingCopy.append(eyebrow, title);
  heading.append(headingCopy, summary);
  article.append(heading);

  const modes = document.createElement("div");
  modes.className = "cx-mode-grid";
  for (const mode of cxImpact.registered_modes) {
    const section = document.createElement("section");
    const modeHeading = document.createElement("div");
    const modeTitle = document.createElement("h4");
    const modeStatus = document.createElement("span");
    const list = document.createElement("ul");
    section.className = "cx-mode";
    section.dataset.affected = String(mode.affected);
    modeTitle.textContent = mode.heading;
    modeStatus.textContent = mode.affected ? "Effective value changes" : "Registration protects value";
    modeHeading.append(modeTitle, modeStatus);
    for (const setting of mode.settings) {
      const item = document.createElement("li");
      const settingCopy = document.createElement("div");
      const label = document.createElement("strong");
      const path = document.createElement("code");
      const result = document.createElement("div");
      const transition = document.createElement("span");
      const badge = document.createElement("em");
      label.textContent = baselineSettingLabel(setting.path);
      path.textContent = setting.path;
      transition.textContent = `${displayValue(setting.current_effective_value)} → ${displayValue(setting.proposed_effective_value)}`;
      badge.textContent = setting.changed
        ? "Changes with baseline"
        : setting.registration_override
          ? `Protected by ${mode.start} registration`
          : "No effective change";
      settingCopy.append(label, path);
      result.append(transition, badge);
      item.append(settingCopy, result);
      list.append(item);
    }
    modeHeading.className = "cx-mode-heading";
    section.append(modeHeading, list);
    modes.append(section);
  }
  article.append(modes);

  const warnings = document.createElement("section");
  const warningTitle = document.createElement("h4");
  const warningCopy = document.createElement("p");
  const warningList = document.createElement("ul");
  warnings.className = "cx-route-warnings";
  warningTitle.textContent = `Declared starting-mode warnings · ${cxImpact.route_warnings.length}`;
  warningCopy.textContent = cxImpact.route_warnings.length
    ? "These profile routes start from a C-mode whose effective registered value would change. Routing is not rewritten."
    : "No declared profile starting mode is affected by this baseline proposal.";
  for (const warning of cxImpact.route_warnings) {
    const item = document.createElement("li");
    const profile = document.createElement("strong");
    const route = document.createElement("span");
    const paths = document.createElement("small");
    profile.textContent = warning.title;
    route.textContent = `${warning.start} ${warning.source_profile || "declared source"}`;
    paths.textContent = warning.affected_paths.map(baselineSettingLabel).join(", ");
    item.append(profile, route, paths);
    warningList.append(item);
  }
  warnings.append(warningTitle, warningCopy, warningList);
  article.append(warnings);
  return article;
}

function renderMyMenuImpact(menuImpact) {
  const article = document.createElement("article");
  article.className = "my-menu-impact";
  const heading = document.createElement("div");
  heading.className = "my-menu-impact-heading";
  const headingCopy = document.createElement("div");
  const eyebrow = document.createElement("p");
  const title = document.createElement("h3");
  const summary = document.createElement("strong");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Card access report";
  title.textContent = "My Menu card coverage";
  summary.textContent = `${menuImpact.summary.profiles_with_warnings} profiles with warnings · ${menuImpact.summary.missing_card_cues} missing cues`;
  headingCopy.append(eyebrow, title);
  heading.append(headingCopy, summary);
  article.append(heading);

  const overview = document.createElement("div");
  overview.className = "my-menu-impact-overview";
  const overviewItems = [
    ["Displayed menu assignments", menuImpact.summary.displayed_assignments],
    ["Assignments hidden on cards", menuImpact.summary.hidden_assignments],
    ["Unavailable in named tab", menuImpact.summary.unavailable_settings],
    ["Configured shortcuts unused by cards", menuImpact.summary.unreferenced_configured_items],
  ];
  for (const [label, value] of overviewItems) {
    const item = document.createElement("div");
    const count = document.createElement("strong");
    const copy = document.createElement("span");
    count.textContent = String(value);
    copy.textContent = label;
    item.append(count, copy);
    overview.append(item);
  }
  article.append(overview);

  if (menuImpact.configuration_warnings.length) {
    const warnings = document.createElement("ul");
    warnings.className = "my-menu-configuration-warnings";
    for (const warning of menuImpact.configuration_warnings) {
      const item = document.createElement("li");
      item.textContent = warning;
      warnings.append(item);
    }
    article.append(warnings);
  }

  if (menuImpact.unreferenced_configured_items.length) {
    const unused = document.createElement("div");
    const unusedTitle = document.createElement("h4");
    const unusedCopy = document.createElement("p");
    const unusedList = document.createElement("ul");
    unused.className = "my-menu-unused";
    unusedTitle.textContent = "Configured shortcuts not referenced by any card";
    unusedCopy.textContent = "These are the only shortcuts this report identifies as possible removal candidates. My Menu itself is never changed automatically.";
    unusedList.className = "my-menu-setting-findings";
    for (const setting of menuImpact.unreferenced_configured_items) {
      const item = document.createElement("li");
      const label = document.createElement("strong");
      const location = document.createElement("small");
      label.textContent = setting.path ? baselineSettingLabel(setting.path) : myMenuItemLabel(setting.item_id);
      location.textContent = `${setting.tabs.join(", ")} · ${setting.item_id}`;
      item.append(label, location);
      unusedList.append(item);
    }
    unused.append(unusedTitle, unusedCopy, unusedList);
    article.append(unused);
  }

  const profiles = document.createElement("div");
  profiles.className = "my-menu-route-profiles";
  for (const profile of menuImpact.profiles) profiles.append(renderMyMenuRouteProfile(profile));
  article.append(profiles);
  return article;
}

function renderMyMenuRouteProfile(profile) {
  const details = document.createElement("details");
  details.className = "my-menu-route-profile";
  details.open = profile.warning_count > 0;
  const summary = document.createElement("summary");
  const identity = document.createElement("span");
  const title = document.createElement("strong");
  const route = document.createElement("small");
  const status = document.createElement("em");
  title.textContent = profile.title;
  route.textContent = profile.access_only
    ? "Access-only card"
    : profile.start
      ? `${profile.start} ${profile.source_profile || "declared source"}`
      : "No starting mode declared";
  status.textContent = profile.warning_count
    ? `${profile.warning_count} ${profile.warning_count === 1 ? "warning" : "warnings"}`
    : "Card cues covered";
  status.dataset.warning = String(profile.warning_count > 0);
  identity.append(title, route);
  summary.append(identity, status);
  details.append(summary);

  const body = document.createElement("div");
  body.className = "my-menu-route-body";
  if (profile.tabs.length) {
    const tabs = document.createElement("ul");
    tabs.className = "my-menu-tab-findings";
    for (const tab of profile.tabs) {
      const item = document.createElement("li");
      const name = document.createElement("strong");
      const finding = document.createElement("span");
      name.textContent = tab.name;
      finding.textContent = tab.shown_on_card
        ? tab.configured
          ? `${tab.displayed_paths.length} displayed ${tab.displayed_paths.length === 1 ? "setting" : "settings"}`
          : "Named tab is not configured"
        : "Not shown — no listed settings on card";
      item.dataset.warning = String(tab.shown_on_card && !tab.configured);
      item.append(name, finding);
      tabs.append(item);
    }
    body.append(tabs);
  }

  if (profile.declared_settings.length) {
    body.append(myMenuFindingHeading("Declared route settings"));
    const declared = document.createElement("ul");
    declared.className = "my-menu-setting-findings";
    for (const setting of profile.declared_settings) {
      const item = document.createElement("li");
      const copy = document.createElement("div");
      const label = document.createElement("strong");
      const route = document.createElement("small");
      const badges = document.createElement("div");
      label.textContent = baselineSettingLabel(setting.path);
      route.textContent = `${setting.tab} · ${setting.path}`;
      copy.append(label, route);
      badges.className = "my-menu-finding-badges";
      badges.append(myMenuFindingBadge(
        setting.displayed_after ? "Shown on card" : "Not listed on this card",
        setting.displayed_after ? "required" : "hidden",
      ));
      if (setting.displayed_after) {
        badges.append(myMenuFindingBadge(
          setting.item_available ? "Available in named tab" : setting.identity_missing ? "No menu identity" : "Missing from named tab",
          setting.item_available ? "covered" : "missing",
        ));
      }
      item.append(copy, badges);
      declared.append(item);
    }
    body.append(declared);
  }

  if (profile.missing_card_cues.length) {
    body.append(myMenuFindingHeading("Displayed settings without a My Menu cue"));
    const missing = document.createElement("ul");
    missing.className = "my-menu-setting-findings missing";
    for (const setting of profile.missing_card_cues) {
      const item = document.createElement("li");
      const copy = document.createElement("div");
      const label = document.createElement("strong");
      const route = document.createElement("small");
      const badge = myMenuFindingBadge(setting.newly_visible ? "Newly visible" : "Menu cue missing", "missing");
      label.textContent = baselineSettingLabel(setting.path);
      route.textContent = setting.available_in_tabs.length
        ? `Configured in ${setting.available_in_tabs.join(", ")}`
        : `Canon item ${setting.item_id} is not in the current My Menu draft`;
      copy.append(label, route);
      item.append(copy, badge);
      missing.append(item);
    }
    body.append(missing);
  }

  details.append(body);
  return details;
}

function myMenuItemLabel(itemId) {
  return state.dictionary?.myMenuEligible?.find((item) => item.id === itemId)?.label || itemId;
}

function myMenuFindingHeading(text) {
  const heading = document.createElement("h4");
  heading.textContent = text;
  return heading;
}

function myMenuFindingBadge(text, status) {
  const badge = document.createElement("span");
  badge.className = "my-menu-finding-badge";
  badge.dataset.status = status;
  badge.textContent = text;
  return badge;
}

function baselineDecisionKey(profile, path) {
  return JSON.stringify([profile, path]);
}

function inheritedDecisionItems() {
  const items = [];
  for (const change of state.baselineAnalysis?.changes || []) {
    for (const profile of change.profiles) {
      if (profile.classification === "inherited_change") {
        items.push({ profile: profile.name, path: change.path });
      }
    }
  }
  return items;
}

function migrationDecisions() {
  return inheritedDecisionItems()
    .map(({ profile, path }) => ({
      profile,
      path,
      decision: state.baselineDecisions[baselineDecisionKey(profile, path)],
    }))
    .filter((item) => item.decision);
}

function updateBaselineDecisionState() {
  const required = inheritedDecisionItems();
  const resolved = required.filter(({ profile, path }) => state.baselineDecisions[baselineDecisionKey(profile, path)]).length;
  const unresolved = required.length - resolved;
  elements.baselineDecisionStatus.textContent = `${resolved} of ${required.length} inherited ${required.length === 1 ? "change" : "changes"} decided.`;
  elements.baselineFollowAll.disabled = unresolved === 0;
  elements.baselinePreserveAll.disabled = unresolved === 0;
  for (const button of [elements.baselineBuildPlan, elements.baselineBuildPlanBottom]) {
    button.disabled = false;
    button.textContent = unresolved ? `Build plan · ${unresolved} unresolved` : "Build complete plan";
  }
}

function setUnresolvedBaselineDecisions(decision, settingPath = null) {
  for (const { profile, path } of inheritedDecisionItems()) {
    if (settingPath && path !== settingPath) continue;
    const key = baselineDecisionKey(profile, path);
    if (!state.baselineDecisions[key]) state.baselineDecisions[key] = decision;
  }
  state.baselinePlan = null;
  renderBaselineAnalysis();
}

function renderImpactChange(change) {
  const article = document.createElement("article");
  article.className = "impact-change";
  const heading = document.createElement("div");
  heading.className = "impact-heading";
  const title = document.createElement("div");
  const name = document.createElement("h3");
  const path = document.createElement("code");
  const transition = document.createElement("span");
  name.textContent = baselineSettingLabel(change.path);
  path.textContent = change.path;
  transition.textContent = `${displayValue(change.current_baseline_value)} → ${displayValue(change.proposed_baseline_value)}`;
  title.append(name, path);
  heading.append(title, transition);
  article.append(heading);

  const groups = new Map();
  for (const profile of change.profiles) {
    if (!groups.has(profile.classification)) groups.set(profile.classification, []);
    groups.get(profile.classification).push(profile);
  }
  for (const [classification, profiles] of groups) {
    const group = document.createElement("section");
    group.className = "impact-group";
    group.dataset.classification = classification;
    const groupTitle = document.createElement("h4");
    const list = document.createElement("ul");
    groupTitle.textContent = `${impactLabels[classification] || classification} · ${profiles.length}`;
    group.append(groupTitle);
    if (classification === "inherited_change") {
      const unresolved = profiles.filter(
        (profile) => !state.baselineDecisions[baselineDecisionKey(profile.name, change.path)],
      ).length;
      const actions = document.createElement("div");
      const actionLabel = document.createElement("span");
      actions.className = "setting-decision-actions";
      actionLabel.textContent = unresolved
        ? `${unresolved} unresolved for this setting`
        : "All profiles decided for this setting";
      actions.append(actionLabel);
      for (const [decision, label] of [
        ["follow_baseline", "Follow baseline for this setting"],
        ["preserve_previous", "Preserve previous for this setting"],
      ]) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "secondary";
        button.textContent = label;
        button.disabled = unresolved === 0;
        button.addEventListener("click", () => setUnresolvedBaselineDecisions(decision, change.path));
        actions.append(button);
      }
      group.append(actions);
    }
    for (const profile of profiles) {
      const item = document.createElement("li");
      item.className = "impact-profile";
      const profileName = document.createElement("strong");
      const values = document.createElement("span");
      profileName.textContent = profile.title;
      values.textContent = `${displayValue(profile.old_effective_value)} → ${displayValue(profile.new_effective_value)}`;
      item.append(profileName, values);
      if (classification === "inherited_change") {
        const choices = document.createElement("fieldset");
        const legend = document.createElement("legend");
        const key = baselineDecisionKey(profile.name, change.path);
        legend.textContent = "Migration decision";
        choices.className = "impact-decisions";
        choices.append(legend);
        for (const [decision, label] of [
          ["follow_baseline", "Follow proposed baseline"],
          ["preserve_previous", "Preserve previous value as override"],
        ]) {
          const choice = document.createElement("label");
          const input = document.createElement("input");
          input.type = "radio";
          input.name = `decision-${encodeURIComponent(key)}`;
          input.value = decision;
          input.checked = state.baselineDecisions[key] === decision;
          input.addEventListener("change", () => {
            state.baselineDecisions[key] = decision;
            state.baselinePlan = null;
            elements.baselinePlan.hidden = true;
            elements.baselinePlan.replaceChildren();
            updateBaselineDecisionState();
          });
          choice.append(input, document.createTextNode(label));
          choices.append(choice);
        }
        item.append(choices);
      } else if (classification === "override_redundant") {
        const action = document.createElement("em");
        action.textContent = "Plan action: remove redundant override";
        item.append(action);
      }
      list.append(item);
    }
    group.append(list);
    article.append(group);
  }
  return article;
}

async function buildBaselinePlan() {
  elements.baselineBuildPlan.disabled = true;
  elements.baselineBuildPlanBottom.disabled = true;
  showBaselineMessage("Validating migration decisions against the current sources…");
  try {
    state.baselinePlan = await request("/api/baseline-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        values: state.baselineDraft,
        decisions: migrationDecisions(),
        myMenuTabs: state.myMenus,
      }),
    });
    renderBaselinePlan();
    const unresolved = state.baselinePlan.summary.unresolved_decisions;
    showBaselineMessage(
      unresolved
        ? `Migration plan built with ${unresolved} unresolved ${unresolved === 1 ? "item" : "items"}. Nothing was saved.`
        : "Complete migration plan validated. Nothing was saved.",
    );
    elements.baselinePlan.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    state.baselinePlan = null;
    renderBaselinePlan();
    showBaselineMessage(error.message, true);
  } finally {
    updateBaselineDecisionState();
  }
}

function renderBaselinePlan() {
  elements.baselinePlan.replaceChildren();
  const plan = state.baselinePlan;
  if (!plan) {
    elements.baselinePlan.hidden = true;
    return;
  }
  const heading = document.createElement("div");
  heading.className = "baseline-plan-heading";
  const title = document.createElement("h3");
  const status = document.createElement("strong");
  title.textContent = "Read-only migration plan";
  status.textContent = plan.complete ? "Complete" : "Needs decisions";
  status.className = plan.complete ? "plan-complete" : "plan-incomplete";
  heading.append(title, status);
  elements.baselinePlan.append(heading);

  if (plan.profile_card_cues_to_add.length) {
    const explanation = document.createElement("section");
    const explanationCopy = document.createElement("p");
    explanation.className = "baseline-plan-explanation";
    explanationCopy.textContent = "What these My Menu suggestions mean: Each suggestion applies to a setting that is already shown on the card. The setting will use the color of the My Menu tab where you can find it, and that tab’s name will appear at the top of the card. Nothing new will be added to the card or to the camera’s My Menu.";
    explanation.append(explanationCopy);
    elements.baselinePlan.append(explanation);
  }

  const groups = [
    ["Profiles following baseline", plan.profiles_following_baseline, (item) => `${item.title}: ${displayValue(item.previous_effective_value)} → ${displayValue(item.proposed_effective_value)}`],
    ["Overrides to add", plan.overrides_to_add, (item) => `${item.title}: preserve ${displayValue(item.override_value)} for ${item.path}`],
    ["Redundant overrides to remove", plan.overrides_to_remove, (item) => `${item.title}: remove ${item.path}`],
    ["Existing overrides retained", plan.overrides_to_keep, (item) => `${item.title}: keep ${item.path}`],
    ["Existing card rows to mark with My Menu access", plan.profile_card_cues_to_add, (item) => `${item.title}: color-code existing ${baselineSettingLabel(item.path)} row for ${item.tab} access`],
    ["Unresolved decisions", plan.unresolved_decisions, (item) => `${item.title}: ${item.path} · ${item.reason.replaceAll("_", " ")}`],
  ];
  for (const [label, items, describe] of groups) {
    const section = document.createElement("section");
    const groupTitle = document.createElement("h4");
    const list = document.createElement("ul");
    groupTitle.textContent = `${label} · ${items.length}`;
    if (!items.length) {
      const empty = document.createElement("li");
      empty.textContent = "None";
      list.append(empty);
    } else {
      for (const item of items) {
        const row = document.createElement("li");
        row.textContent = describe(item);
        list.append(row);
      }
    }
    section.append(groupTitle, list);
    elements.baselinePlan.append(section);
  }
  elements.baselinePlan.hidden = false;
}

function buildControl(setting, value) {
  if (setting.control === "select") {
    const select = document.createElement("select");
    const choices = normalizedChoiceDetails(setting, value);
    for (const choice of choices) {
      const option = document.createElement("option");
      option.value = JSON.stringify(choice.value);
      option.textContent = choiceDisplayLabel(choice);
      option.selected = equal(choice.value, value);
      select.append(option);
    }
    return { control: select, datalist: null };
  }
  if (setting.control === "combo") {
    const input = document.createElement("input");
    const datalist = document.createElement("datalist");
    const listId = `choices-${setting.path.replaceAll(".", "-")}`;
    input.type = "text";
    input.value = value ?? "";
    input.setAttribute("list", listId);
    input.dataset.valueType = setting.valueType;
    datalist.id = listId;
    for (const choice of normalizedChoiceDetails(setting, value)) {
      if (choice.value === null || choice.value === undefined) continue;
      const option = document.createElement("option");
      option.value = String(choice.value);
      option.label = choiceDisplayLabel(choice);
      datalist.append(option);
    }
    return { control: input, datalist };
  }
  const input = document.createElement("input");
  input.type = setting.control === "number" ? "number" : "text";
  input.value = value ?? "";
  input.dataset.valueType = setting.valueType;
  return { control: input, datalist: null };
}

function normalizedChoiceDetails(setting, value) {
  const choices = [...(setting.choiceDetails || [])];
  if (!choices.some((choice) => equal(choice.value, value))) {
    choices.push({ value, label: displayValue(value), origin: "existing_profile", iconUrl: setting.iconUrl });
  }
  return choices;
}

function choiceDisplayLabel(choice) {
  let label = choice.label || displayValue(choice.value);
  if (["project_alias", "project_extension", "project_model"].includes(choice.origin)) label += " — project compatibility";
  if (choice.conditional) label += ` (${choice.conditional})`;
  return label;
}

function iconForValue(setting, value) {
  const choice = (setting.choiceDetails || []).find((item) => equal(item.value, value));
  return choice?.iconUrl || setting.iconUrl || "";
}

function readControl(control, setting) {
  if (control.tagName === "SELECT") return JSON.parse(control.value);
  if (setting.valueType === "integer") return control.value === "" ? null : Number.parseInt(control.value, 10);
  if (setting.valueType === "number") return control.value === "" ? null : Number(control.value);
  return control.value;
}

function updateSetting(setting, value, rerender = true) {
  if (equal(value, setting.baseline)) delete state.draftOverrides[setting.path];
  else state.draftOverrides[setting.path] = value;
  draftChanged();
  if (rerender) render();
  else updateCounts();
}

function draftChanged() {
  state.reviewToken = null;
  elements.previewPanel.hidden = true;
  if (elements.reviewDialog.open) elements.reviewDialog.close();
}

function updateCounts() {
  const custom = Object.keys(state.draftOverrides).length;
  const total = state.detail.sections.reduce((sum, section) => sum + section.settings.length, 0);
  elements.customCount.textContent = String(custom);
  elements.inheritedCount.textContent = String(total - custom);
}

function profileDraftPayload() {
  return {
    operation: state.detail.operation || "update",
    sourceProfile: state.detail.sourceProfile,
    targetName: elements.filenameInput.value.trim(),
    sourceFingerprint: state.detail.sourceFingerprint,
    title: elements.titleInput.value.trim(),
    subtitle: elements.subtitleInput.value.trim(),
    status: elements.statusInput.value,
    release: elements.releaseInput.checked,
    overrides: state.draftOverrides,
  };
}

async function reviewChanges() {
  elements.reviewButton.disabled = true;
  showMessage("Validating the candidate profile and preparing the exact YAML diff…");
  try {
    const review = await request("/api/profile-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profileDraftPayload()),
    });
    state.reviewToken = review.reviewToken;
    elements.reviewSummary.textContent = review.summary;
    elements.reviewDiff.textContent = review.diff;
    elements.reviewDialog.showModal();
    showMessage("Candidate validation passed. Review the exact YAML before saving.");
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    elements.reviewButton.disabled = false;
  }
}

async function saveReviewedProfile() {
  if (!state.reviewToken) {
    showMessage("This review is no longer current. Review the draft again.", true);
    elements.reviewDialog.close();
    return;
  }
  elements.saveButton.disabled = true;
  showMessage("Creating a recovery backup and validating the reviewed save…");
  try {
    const result = await request("/api/profile-saves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.reviewToken }),
    });
    state.reviewToken = null;
    elements.reviewDialog.close();
    await loadProfiles(result.savedProfile);
    showMessage(`Saved ${result.sourceFile}. Validation passed. Recovery backup: ${result.backup}`);
  } catch (error) {
    state.reviewToken = null;
    elements.reviewDialog.close();
    showMessage(error.message, true);
  } finally {
    elements.saveButton.disabled = false;
  }
}

async function preview() {
  elements.previewButton.disabled = true;
  showMessage("Rendering a temporary preview…");
  try {
    const payload = await request("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profileDraftPayload()),
    });
    elements.previewPath.textContent = payload.outputFile;
    elements.previewFrame.src = `${payload.previewUrl}?t=${Date.now()}`;
    elements.previewPanel.hidden = false;
    showMessage("Preview updated. No profile source was saved.");
    elements.previewPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    elements.previewButton.disabled = false;
  }
}

elements.profileSelect.addEventListener("change", () => loadProfile(elements.profileSelect.value));
elements.newButton.addEventListener("click", () => loadProfileDraft("create"));
elements.duplicateButton.addEventListener("click", () => loadProfileDraft("duplicate"));
elements.reloadButton.addEventListener("click", async () => {
  if (state.detail.operation === "update") await loadProfile(state.detail.name);
  else applyProfileDetail(state.detail);
  showMessage("Draft discarded and original source values reloaded. No profile was saved.");
});
elements.previewButton.addEventListener("click", preview);
elements.reviewButton.addEventListener("click", reviewChanges);
elements.saveButton.addEventListener("click", saveReviewedProfile);
elements.reviewClose.addEventListener("click", () => elements.reviewDialog.close());
elements.reviewCancel.addEventListener("click", () => elements.reviewDialog.close());
for (const input of [elements.titleInput, elements.subtitleInput, elements.filenameInput, elements.statusInput, elements.releaseInput]) {
  input.addEventListener("input", () => {
    draftChanged();
    renderMetadataState();
  });
  input.addEventListener("change", () => {
    draftChanged();
    renderMetadataState();
  });
}
for (const tab of elements.viewTabs) tab.addEventListener("click", () => switchView(tab.dataset.view));
elements.dictionarySearch.addEventListener("input", renderDictionary);
elements.dictionaryClassification.addEventListener("change", renderDictionary);
elements.loadRecommendedMenus.addEventListener("click", () => loadRecommendedMenus(true));
elements.baselineAnalyze.addEventListener("click", analyzeBaselineDraft);
elements.baselineFollowAll.addEventListener("click", () => setUnresolvedBaselineDecisions("follow_baseline"));
elements.baselinePreserveAll.addEventListener("click", () => setUnresolvedBaselineDecisions("preserve_previous"));
elements.baselineBuildPlan.addEventListener("click", buildBaselinePlan);
elements.baselineBuildPlanBottom.addEventListener("click", buildBaselinePlan);
elements.baselineReset.addEventListener("click", () => {
  state.baselineDraft = clone(state.baselineCurrent);
  state.baselineAnalysis = null;
  state.baselineDecisions = {};
  state.baselinePlan = null;
  renderBaseline();
  showBaselineMessage("Baseline draft discarded. Nothing was saved.");
});

Promise.all([loadDictionary(), loadProfiles(), loadBaseline()]);
