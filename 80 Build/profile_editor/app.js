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
  reloadButton: document.querySelector("#reload-button"),
  previewButton: document.querySelector("#preview-button"),
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
};

const state = {
  dictionary: null,
  myMenus: Array.from({ length: 5 }, () => ({ name: "", items: Array(6).fill("") })),
  detail: null,
  originalOverrides: {},
  draftOverrides: {},
  loadSequence: 0,
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

async function loadProfiles() {
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
    if (payload.profiles.length) await loadProfile(payload.profiles[0].name);
  } catch (error) {
    showMessage(error.message, true);
  }
}

async function loadDictionary() {
  try {
    state.dictionary = await request("/api/dictionary");
    elements.dictionarySource.href = state.dictionary.metadata.authority_url || "https://cam.start.canon/en/C003/manual/html/index.html";
    renderDictionary();
    renderMyMenus();
  } catch (error) {
    showMessage(error.message, true);
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
        renderMyMenus();
        renderDictionary();
      });
      label.append(select);
      items.append(label);
    });
    elements.myMenuTabs.append(fragment);
  });
}

function loadRecommendedMenus() {
  state.myMenus = Array.from({ length: 5 }, () => ({ name: "", items: Array(6).fill("") }));
  (state.dictionary?.myMenu?.recommended_tabs || []).slice(0, 5).forEach((tab, index) => {
    state.myMenus[index].name = tab.name;
    tab.items.slice(0, 6).forEach((itemId, itemIndex) => { state.myMenus[index].items[itemIndex] = itemId; });
  });
  renderMyMenus();
  renderDictionary();
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
    state.detail = detail;
    state.originalOverrides = clone(detail.originalOverrides || {});
    state.draftOverrides = clone(state.originalOverrides);
    elements.profileSelect.value = name;
    elements.profileTitle.textContent = detail.title;
    elements.sourceFile.textContent = detail.sourceFile;
    elements.previewPanel.hidden = true;
    render();
  } catch (error) {
    if (loadSequence !== state.loadSequence) return;
    showMessage(error.message, true);
  } finally {
    if (loadSequence === state.loadSequence) elements.profileSelect.disabled = false;
  }
}

function render() {
  elements.settings.replaceChildren();
  elements.referenceCard.hidden = true;
  const editable = state.detail?.editableDraft;
  elements.reloadButton.disabled = !editable;
  elements.previewButton.disabled = !editable;
  if (!editable) {
    renderReference();
    elements.customCount.textContent = "0";
    elements.inheritedCount.textContent = "0";
    showMessage("This reference card has no baseline overrides. It is shown for completeness and cannot be drafted in Stage 1.");
    return;
  }
  showMessage("");
  for (const section of state.detail.sections) renderSection(section);
  updateCounts();
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
    render();
  });
  return row;
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
  elements.previewPanel.hidden = true;
  if (rerender) render();
  else updateCounts();
}

function updateCounts() {
  const custom = Object.keys(state.draftOverrides).length;
  const total = state.detail.sections.reduce((sum, section) => sum + section.settings.length, 0);
  elements.customCount.textContent = String(custom);
  elements.inheritedCount.textContent = String(total - custom);
}

async function preview() {
  elements.previewButton.disabled = true;
  showMessage("Rendering a temporary preview…");
  try {
    const payload = await request("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile: state.detail.name, overrides: state.draftOverrides }),
    });
    elements.previewPath.textContent = payload.outputFile;
    elements.previewFrame.src = `${payload.previewUrl}?t=${Date.now()}`;
    elements.previewPanel.hidden = false;
    showMessage("Preview updated. The profile YAML remains unchanged.");
    elements.previewPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    elements.previewButton.disabled = false;
  }
}

elements.profileSelect.addEventListener("change", () => loadProfile(elements.profileSelect.value));
elements.reloadButton.addEventListener("click", () => {
  state.draftOverrides = clone(state.originalOverrides);
  elements.previewPanel.hidden = true;
  render();
  showMessage("Draft discarded. The selected profile's original saved overrides were reloaded; no source file was changed.");
});
elements.previewButton.addEventListener("click", preview);
for (const tab of elements.viewTabs) tab.addEventListener("click", () => switchView(tab.dataset.view));
elements.dictionarySearch.addEventListener("input", renderDictionary);
elements.dictionaryClassification.addEventListener("change", renderDictionary);
elements.loadRecommendedMenus.addEventListener("click", loadRecommendedMenus);

Promise.all([loadDictionary(), loadProfiles()]);
