const editorToken = document.querySelector('meta[name="profile-editor-token"]').content;

const elements = {
  editorVersion: document.querySelector("#editor-version"),
  editorSourceHash: document.querySelector("#editor-source-hash"),
  projectContextBadge: document.querySelector("#project-context-badge"),
  openCameraLab: document.querySelector("#open-camera-lab"),
  sidebarCameraLab: document.querySelector("#sidebar-camera-lab"),
  stopProfileEditor: document.querySelector("#stop-profile-editor"),
  profileActionMenu: document.querySelector(".profile-action-menu"),
  viewTabs: [...document.querySelectorAll(".view-tab")],
  views: [...document.querySelectorAll(".app-view")],
  profileDraftBadge: document.querySelector("#profile-draft-badge"),
  cxFoundationDraftBadge: document.querySelector("#cx-foundation-draft-badge"),
  myMenuDraftBadge: document.querySelector("#my-menu-draft-badge"),
  baselineDraftBadge: document.querySelector("#baseline-draft-badge"),
  pendingDraftBadge: document.querySelector("#pending-draft-badge"),
  daySteps: [...document.querySelectorAll(".day-step")],
  dayPanels: [...document.querySelectorAll("[data-day-panel]")],
  refreshWorkflowPreflight: document.querySelector("#refresh-workflow-preflight"),
  workflowPreflightBadge: document.querySelector("#workflow-preflight-badge"),
  workflowPreflightSummary: document.querySelector("#workflow-preflight-summary"),
  workflowPreflightDetails: document.querySelector("#workflow-preflight-details"),
  workflowPreflightOutput: document.querySelector("#workflow-preflight-output"),
  beginWork: document.querySelector("#begin-work"),
  todayMessage: document.querySelector("#today-message"),
  todayDraftCount: document.querySelector("#today-draft-count"),
  todayOpenProfiles: document.querySelector("#today-open-profiles"),
  todayOpenCameraLab: document.querySelector("#today-open-camera-lab"),
  todayCameraLabNote: document.querySelector("#today-camera-lab-note"),
  todayOpenReviewBuild: document.querySelector("#today-open-review-build"),
  goToFinish: document.querySelector("#go-to-finish"),
  finishReadinessBadge: document.querySelector("#finish-readiness-badge"),
  finishDraftNote: document.querySelector("#finish-draft-note"),
  finishOpenReviewBuild: document.querySelector("#finish-open-review-build"),
  openFinishDay: document.querySelector("#open-finish-day"),
  switchingMacs: document.querySelector("#switching-macs"),
  handoffGuidance: document.querySelector("#handoff-guidance"),
  continueToPublish: document.querySelector("#continue-to-publish"),
  refreshFinishDay: document.querySelector("#refresh-finish-day"),
  finishDayBranch: document.querySelector("#finish-day-branch"),
  finishDayMessage: document.querySelector("#finish-day-message"),
  finishDaySteps: [...document.querySelectorAll(".finish-day-steps li")],
  finishDayStatusBadge: document.querySelector("#finish-day-status-badge"),
  finishDaySummary: document.querySelector("#finish-day-summary"),
  finishDayDetails: document.querySelector("#finish-day-details"),
  finishDayOutput: document.querySelector("#finish-day-output"),
  finishDayPreparePanel: document.querySelector("#finish-day-prepare-panel"),
  finishDayConfirmPrepare: document.querySelector("#finish-day-confirm-prepare"),
  prepareFinishDay: document.querySelector("#prepare-finish-day"),
  finishDayProgress: document.querySelector("#finish-day-progress"),
  finishDayProgressStage: document.querySelector("#finish-day-progress-stage"),
  finishDayProgressElapsed: document.querySelector("#finish-day-progress-elapsed"),
  finishDayProgressCommand: document.querySelector("#finish-day-progress-command"),
  finishDayProgressLog: document.querySelector("#finish-day-progress-log"),
  finishDayCommitPanel: document.querySelector("#finish-day-commit-panel"),
  finishDayFileCount: document.querySelector("#finish-day-file-count"),
  finishDayFileList: document.querySelector("#finish-day-file-list"),
  finishDayCommitMessage: document.querySelector("#finish-day-commit-message"),
  finishDayConfirmCommit: document.querySelector("#finish-day-confirm-commit"),
  commitFinishDay: document.querySelector("#commit-finish-day"),
  finishDayPushPanel: document.querySelector("#finish-day-push-panel"),
  finishDayPushTarget: document.querySelector("#finish-day-push-target"),
  finishDayConfirmPush: document.querySelector("#finish-day-confirm-push"),
  pushFinishDay: document.querySelector("#push-finish-day"),
  finishDayCompletePanel: document.querySelector("#finish-day-complete-panel"),
  openBranchIntegration: document.querySelector("#open-branch-integration"),
  refreshBranchIntegration: document.querySelector("#refresh-branch-integration"),
  branchIntegrationBranch: document.querySelector("#branch-integration-branch"),
  branchIntegrationMessage: document.querySelector("#branch-integration-message"),
  branchIntegrationSteps: [...document.querySelectorAll(".integration-steps li")],
  branchIntegrationStatusBadge: document.querySelector("#branch-integration-status-badge"),
  branchIntegrationSummary: document.querySelector("#branch-integration-summary"),
  branchIntegrationDetails: document.querySelector("#branch-integration-details"),
  branchIntegrationOutput: document.querySelector("#branch-integration-output"),
  branchIntegrationReviewPanel: document.querySelector("#branch-integration-review-panel"),
  branchIntegrationConfirmPrepare: document.querySelector("#branch-integration-confirm-prepare"),
  prepareBranchIntegration: document.querySelector("#prepare-branch-integration"),
  branchIntegrationProgress: document.querySelector("#branch-integration-progress"),
  branchIntegrationProgressStage: document.querySelector("#branch-integration-progress-stage"),
  branchIntegrationProgressElapsed: document.querySelector("#branch-integration-progress-elapsed"),
  branchIntegrationProgressCommand: document.querySelector("#branch-integration-progress-command"),
  branchIntegrationProgressLog: document.querySelector("#branch-integration-progress-log"),
  branchIntegrationMergePanel: document.querySelector("#branch-integration-merge-panel"),
  branchIntegrationCommitList: document.querySelector("#branch-integration-commit-list"),
  branchIntegrationFileCount: document.querySelector("#branch-integration-file-count"),
  branchIntegrationFileList: document.querySelector("#branch-integration-file-list"),
  branchIntegrationConfirmMerge: document.querySelector("#branch-integration-confirm-merge"),
  mergeBranchToMain: document.querySelector("#merge-branch-to-main"),
  branchIntegrationPushPanel: document.querySelector("#branch-integration-push-panel"),
  branchIntegrationConfirmPush: document.querySelector("#branch-integration-confirm-push"),
  pushIntegratedMain: document.querySelector("#push-integrated-main"),
  branchIntegrationResyncPanel: document.querySelector("#branch-integration-resync-panel"),
  branchIntegrationConfirmResync: document.querySelector("#branch-integration-confirm-resync"),
  resyncIntegratedBranch: document.querySelector("#resync-integrated-branch"),
  branchIntegrationCompletePanel: document.querySelector("#branch-integration-complete-panel"),
  branchIntegrationCompleteMessage: document.querySelector("#branch-integration-complete-message"),
  branchIntegrationAppStatus: document.querySelector("#branch-integration-app-status"),
  finishOpenCleanup: document.querySelector("#finish-open-cleanup"),
  integrationOpenCleanup: document.querySelector("#integration-open-cleanup"),
  refreshCleanupReview: document.querySelector("#refresh-cleanup-review"),
  cleanupReviewMessage: document.querySelector("#cleanup-review-message"),
  cleanupReviewCount: document.querySelector("#cleanup-review-count"),
  cleanupReviewSummary: document.querySelector("#cleanup-review-summary"),
  cleanupCandidateList: document.querySelector("#cleanup-candidate-list"),
  cleanupProtectedDetails: document.querySelector("#cleanup-protected-details"),
  cleanupProtectedSummary: document.querySelector("#cleanup-protected-summary"),
  cleanupProtectedList: document.querySelector("#cleanup-protected-list"),
  cleanupConfirmDelete: document.querySelector("#cleanup-confirm-delete"),
  cleanupSelectedSummary: document.querySelector("#cleanup-selected-summary"),
  deleteCleanupCandidates: document.querySelector("#delete-cleanup-candidates"),
  refreshPublication: document.querySelector("#refresh-publication"),
  publicationContext: document.querySelector("#publication-context"),
  publicationMessage: document.querySelector("#publication-message"),
  publicationStatusBadge: document.querySelector("#publication-status-badge"),
  publicationSummary: document.querySelector("#publication-summary"),
  publicationDetails: document.querySelector("#publication-details"),
  publicationOutput: document.querySelector("#publication-output"),
  publicationMainHandoff: document.querySelector("#publication-main-handoff"),
  openMainEditor: document.querySelector("#open-main-editor"),
  publicationNotesPanel: document.querySelector("#publication-notes-panel"),
  publicationNotesVersion: document.querySelector("#publication-notes-version"),
  publicationVersionKind: document.querySelector("#publication-version-kind"),
  publicationMajorField: document.querySelector("#publication-major-field"),
  publicationMajorVersion: document.querySelector("#publication-major-version"),
  publicationHighlights: document.querySelector("#publication-highlights"),
  reviewPublicationNotes: document.querySelector("#review-publication-notes"),
  publicationOptionsPanel: document.querySelector("#publication-options-panel"),
  publicationVersionLabel: document.querySelector("#publication-version-label"),
  publicationSpreadsheetStatus: document.querySelector("#publication-spreadsheet-status"),
  publicationSpreadsheetChoices: [...document.querySelectorAll('input[name="publication-spreadsheets"]')],
  reviewPublication: document.querySelector("#review-publication"),
  publicationProgress: document.querySelector("#publication-progress"),
  publicationProgressStage: document.querySelector("#publication-progress-stage"),
  publicationProgressElapsed: document.querySelector("#publication-progress-elapsed"),
  publicationProgressCommand: document.querySelector("#publication-progress-command"),
  publicationProgressLog: document.querySelector("#publication-progress-log"),
  publicationComplete: document.querySelector("#publication-complete"),
  publicationCompleteMessage: document.querySelector("#publication-complete-message"),
  publicationNotesDialog: document.querySelector("#publication-notes-dialog"),
  publicationNotesDiff: document.querySelector("#publication-notes-diff"),
  publicationNotesClose: document.querySelector("#publication-notes-close"),
  publicationNotesCancel: document.querySelector("#publication-notes-cancel"),
  publicationNotesConfirm: document.querySelector("#publication-notes-confirm"),
  savePublicationNotes: document.querySelector("#save-publication-notes"),
  publicationConfirmDialog: document.querySelector("#publication-confirm-dialog"),
  publicationConfirmClose: document.querySelector("#publication-confirm-close"),
  publicationConfirmCancel: document.querySelector("#publication-confirm-cancel"),
  publicationReviewSummary: document.querySelector("#publication-review-summary"),
  publicationReviewHighlights: document.querySelector("#publication-review-highlights"),
  publicationConfirmLive: document.querySelector("#publication-confirm-live"),
  startPublication: document.querySelector("#start-publication"),
  dictionarySource: document.querySelector("#dictionary-source"),
  dictionarySearch: document.querySelector("#dictionary-search"),
  dictionaryClassification: document.querySelector("#dictionary-classification"),
  dictionaryCount: document.querySelector("#dictionary-count"),
  dictionarySections: document.querySelector("#dictionary-sections"),
  loadSavedMenus: document.querySelector("#load-saved-menus"),
  loadRecommendedMenus: document.querySelector("#load-recommended-menus"),
  analyzeMyMenu: document.querySelector("#analyze-my-menu"),
  reviewMyMenuColors: document.querySelector("#review-my-menu-colors"),
  myMenuColorMessage: document.querySelector("#my-menu-color-message"),
  myMenuTabs: document.querySelector("#my-menu-tabs"),
  reloadCxFoundation: document.querySelector("#reload-cx-foundation"),
  cxFoundationMessage: document.querySelector("#cx-foundation-message"),
  cxAssignmentGrid: document.querySelector("#cx-assignment-grid"),
  reviewCxAssignments: document.querySelector("#review-cx-assignments"),
  cxProfileSelect: document.querySelector("#cx-profile-select"),
  cxFitSummary: document.querySelector("#cx-fit-summary"),
  cxFitResults: document.querySelector("#cx-fit-results"),
  cxSelectionStatus: document.querySelector("#cx-selection-status"),
  reviewCxSelection: document.querySelector("#review-cx-selection"),
  cxFoundationReviewDialog: document.querySelector("#cx-foundation-review-dialog"),
  cxFoundationReviewSummary: document.querySelector("#cx-foundation-review-summary"),
  cxFoundationReviewDiff: document.querySelector("#cx-foundation-review-diff"),
  cxFoundationReviewClose: document.querySelector("#cx-foundation-review-close"),
  cxFoundationReviewCancel: document.querySelector("#cx-foundation-review-cancel"),
  saveCxFoundation: document.querySelector("#save-cx-foundation"),
  myMenuColorReviewDialog: document.querySelector("#my-menu-color-review-dialog"),
  myMenuColorReviewSummary: document.querySelector("#my-menu-color-review-summary"),
  myMenuColorReviewDiff: document.querySelector("#my-menu-color-review-diff"),
  myMenuColorReviewClose: document.querySelector("#my-menu-color-review-close"),
  myMenuColorReviewCancel: document.querySelector("#my-menu-color-review-cancel"),
  saveMyMenuColors: document.querySelector("#save-my-menu-colors"),
  profileSelect: document.querySelector("#profile-select"),
  newButton: document.querySelector("#new-button"),
  duplicateButton: document.querySelector("#duplicate-button"),
  reloadButton: document.querySelector("#reload-button"),
  discardProfileButton: document.querySelector("#discard-profile-button"),
  profileRemovalReason: document.querySelector("#profile-removal-reason"),
  previewButton: document.querySelector("#preview-button"),
  reviewButton: document.querySelector("#review-button"),
  profileMetadata: document.querySelector("#profile-metadata"),
  operationTitle: document.querySelector("#operation-title"),
  operationNote: document.querySelector("#operation-note"),
  titleInput: document.querySelector("#title-input"),
  subtitleInput: document.querySelector("#subtitle-input"),
  filenameInput: document.querySelector("#filename-input"),
  statusInput: document.querySelector("#status-input"),
  displayCategoryInput: document.querySelector("#display-category-input"),
  releaseInput: document.querySelector("#release-input"),
  profileTitle: document.querySelector("#profile-title"),
  sourceFile: document.querySelector("#source-file"),
  customCount: document.querySelector("#custom-count"),
  inheritedCount: document.querySelector("#inherited-count"),
  cardSettingsGroup: document.querySelector("#card-settings-group"),
  cardSettings: document.querySelector("#card-settings"),
  cardSettingsCount: document.querySelector("#card-settings-count"),
  additionalSettingsGroup: document.querySelector("#additional-settings-group"),
  additionalSettingsCount: document.querySelector("#additional-settings-count"),
  settings: document.querySelector("#settings"),
  message: document.querySelector("#message"),
  referenceCard: document.querySelector("#reference-card"),
  lensGuidanceGroup: document.querySelector("#lens-guidance-group"),
  lensChoiceList: document.querySelector("#lens-choice-list"),
  lensChoiceCount: document.querySelector("#lens-choice-count"),
  addLensChoice: document.querySelector("#add-lens-choice"),
  profileWorkspace: document.querySelector("#profile-workspace"),
  profileSaveBar: document.querySelector("#profile-save-bar"),
  workflowSteps: [...document.querySelectorAll(".workflow-step")],
  mobilePaneTabs: [...document.querySelectorAll(".mobile-pane-tab")],
  previewPanel: document.querySelector("#preview-panel"),
  previewFrame: document.querySelector("#preview-frame"),
  previewPath: document.querySelector("#preview-path"),
  previewStatus: document.querySelector("#preview-status"),
  previewEmpty: document.querySelector("#preview-empty"),
  previewChangeNote: document.querySelector("#preview-change-note"),
  returnToTop: document.querySelector("#return-to-top"),
  reviewDialog: document.querySelector("#review-dialog"),
  reviewSummary: document.querySelector("#review-summary"),
  reviewEffective: document.querySelector("#review-effective"),
  reviewEffectiveList: document.querySelector("#review-effective-list"),
  reviewDiff: document.querySelector("#review-diff"),
  reviewClose: document.querySelector("#review-close"),
  reviewCancel: document.querySelector("#review-cancel"),
  saveButton: document.querySelector("#save-button"),
  discardProfileDialog: document.querySelector("#discard-profile-dialog"),
  discardProfileSummary: document.querySelector("#discard-profile-summary"),
  discardProfileDiff: document.querySelector("#discard-profile-diff"),
  discardProfileMentions: document.querySelector("#discard-profile-mentions"),
  discardProfileClose: document.querySelector("#discard-profile-close"),
  discardProfileCancel: document.querySelector("#discard-profile-cancel"),
  discardProfileConfirm: document.querySelector("#discard-profile-confirm"),
  refreshDeletedCards: document.querySelector("#refresh-deleted-cards"),
  deletedCardsMessage: document.querySelector("#deleted-cards-message"),
  deletedCardsList: document.querySelector("#deleted-cards-list"),
  restoreProfileDialog: document.querySelector("#restore-profile-dialog"),
  restoreProfileSummary: document.querySelector("#restore-profile-summary"),
  restoreProfileDiff: document.querySelector("#restore-profile-diff"),
  restoreProfileClose: document.querySelector("#restore-profile-close"),
  restoreProfileCancel: document.querySelector("#restore-profile-cancel"),
  restoreProfileConfirm: document.querySelector("#restore-profile-confirm"),
  migrationReviewDialog: document.querySelector("#migration-review-dialog"),
  migrationReviewSummary: document.querySelector("#migration-review-summary"),
  migrationReviewDiff: document.querySelector("#migration-review-diff"),
  migrationReviewClose: document.querySelector("#migration-review-close"),
  migrationReviewCancel: document.querySelector("#migration-review-cancel"),
  migrationSaveButton: document.querySelector("#migration-save-button"),
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
  refreshReviewBuild: document.querySelector("#refresh-review-build"),
  sessionSummary: document.querySelector("#session-summary"),
  reviewBuildMessage: document.querySelector("#review-build-message"),
  pendingChangeCount: document.querySelector("#pending-change-count"),
  pendingChangeList: document.querySelector("#pending-change-list"),
  importVerificationTracker: document.querySelector("#import-verification-tracker"),
  validateReadiness: document.querySelector("#validate-readiness"),
  runLocalBuild: document.querySelector("#run-local-build"),
  localBuildOutput: document.querySelector("#local-build-output"),
  buildConfirmDialog: document.querySelector("#build-confirm-dialog"),
  buildConfirmClose: document.querySelector("#build-confirm-close"),
  buildConfirmCancel: document.querySelector("#build-confirm-cancel"),
  buildConfirmRun: document.querySelector("#build-confirm-run"),
};

const state = {
  dictionary: null,
  myMenus: Array.from({ length: 5 }, () => ({ name: "", colorChoice: "", items: Array(6).fill("") })),
  myMenuColorReviewToken: null,
  detail: null,
  originalOverrides: {},
  draftOverrides: {},
  originalLensChoices: [],
  draftLensChoices: [],
  reviewToken: null,
  discardReviewToken: null,
  restoreReviewToken: null,
  previewLoaded: false,
  profileDrafts: new Map(),
  currentDraftKey: null,
  nextDraftId: 1,
  filenameFollowsTitle: false,
  buildReadiness: null,
  workflowPreflight: null,
  finishDay: null,
  finishDayReviewToken: null,
  finishDayBusy: false,
  branchIntegration: null,
  branchIntegrationReviewToken: null,
  branchIntegrationBusy: false,
  cleanupReview: null,
  cleanupReviewToken: null,
  cleanupBusy: false,
  publication: null,
  publicationNotesReviewToken: null,
  publicationReviewToken: null,
  publicationBusy: false,
  dayPhase: "start",
  activeView: "today",
  loadSequence: 0,
  baselineDetail: null,
  baselineCurrent: {},
  baselineDraft: {},
  baselineAnalysis: null,
  baselineDecisions: {},
  baselinePlan: null,
  migrationReviewToken: null,
  cxFoundation: null,
  cxAssignments: {},
  cxSelectedProfile: null,
  cxSelectedStart: "",
  cxSavedSelectedStart: "",
  cxSelectionDrafts: new Map(),
  cxReviewToken: null,
  cxReviewKind: null,
  activeProfileName: null,
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

function profileFilenameFromTitle(title) {
  return title
    .replace(/[^A-Za-z0-9 .&+()'_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^[^A-Za-z0-9]+/, "")
    .slice(0, 80)
    .replace(/[. ]+$/, "");
}

async function request(url, options) {
  const requestOptions = { ...(options || {}) };
  if (requestOptions.method === "POST") {
    requestOptions.headers = { ...(requestOptions.headers || {}), "X-Profile-Editor-Token": editorToken };
  }
  const response = await fetch(url, requestOptions);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "The prototype could not complete the request.");
  return payload;
}

async function loadEditorInfo() {
  try {
    const info = await request("/api/editor-info");
    const projectContext = info.project_context || {};
    elements.projectContextBadge.textContent = projectContext.label || "Project context unavailable";
    elements.projectContextBadge.className = `project-context-badge ${projectContext.kind || "unknown"}`;
    elements.projectContextBadge.title = projectContext.branch ? `Git branch: ${projectContext.branch}` : "Git branch unavailable";
    const contextName = info.context_name || (projectContext.kind === "main" ? "Main" : projectContext.kind === "prototype" ? "Prototype" : "Unknown");
    elements.editorVersion.textContent = `Editor ${info.version} · ${contextName}`;
    elements.editorSourceHash.textContent = `Source hash ${info.build}`;
  } catch (error) {
    elements.editorVersion.textContent = "Editor version unavailable";
    elements.editorSourceHash.textContent = "Source hash unavailable";
    showMessage(error.message, true);
  }
}

function showMessage(text, error = false) {
  elements.message.textContent = text;
  elements.message.classList.toggle("error", error);
  elements.message.hidden = !text;
}

function showTodayMessage(text, error = false) {
  elements.todayMessage.textContent = text;
  elements.todayMessage.classList.toggle("error", error);
  elements.todayMessage.hidden = !text;
}

function setDayPhase(phase) {
  state.dayPhase = phase;
  const order = ["start", "work", "finish"];
  const activeIndex = order.indexOf(phase);
  for (const step of elements.daySteps) {
    const stepIndex = order.indexOf(step.dataset.dayPhase);
    step.classList.toggle("is-active", stepIndex === activeIndex);
    step.classList.toggle("is-complete", stepIndex < activeIndex);
    step.setAttribute("aria-current", stepIndex === activeIndex ? "step" : "false");
  }
  for (const panel of elements.dayPanels) panel.hidden = panel.dataset.dayPanel !== phase;
  showTodayMessage("");
}

function renderWorkflowPreflight() {
  const result = state.workflowPreflight;
  const status = result?.status || "checking";
  const labels = { checking: "Checking…", ready: "Ready", notice: "Review", blocked: "Blocked" };
  elements.workflowPreflightBadge.className = `workflow-status ${status}`;
  elements.workflowPreflightBadge.textContent = labels[status] || "Review";
  elements.workflowPreflightSummary.className = `workflow-preflight-summary ${status === "ready" ? "" : status}`.trim();
  elements.workflowPreflightSummary.replaceChildren();
  const title = document.createElement("strong");
  const detail = document.createElement("span");
  if (!result) {
    title.textContent = "Running preflight…";
    detail.textContent = "The editor is checking the current project.";
  } else {
    title.textContent = result.summary;
    detail.textContent = status === "blocked"
      ? "Stop and resolve the reported condition before editing."
      : status === "notice" ? "Work may continue on this Mac after reviewing the details." : "No action is required before beginning work.";
  }
  elements.workflowPreflightSummary.append(title, detail);
  elements.workflowPreflightOutput.textContent = result?.output || "";
  elements.workflowPreflightDetails.hidden = !result?.output;
  elements.beginWork.disabled = !result || status === "blocked";
}

function renderTodayWorkflow() {
  const pending = pendingSessionItems().length;
  elements.todayDraftCount.textContent = `${pending} ${pending === 1 ? "draft" : "drafts"}`;
  elements.todayDraftCount.className = `workflow-status ${pending ? "notice" : "ready"}`;
  const savedProfile = state.detail?.cardType === "profile" && (state.detail.operation || "update") === "update";
  const changed = savedProfile && profilePayloadChanged(profileDraftPayload());
  elements.todayOpenCameraLab.disabled = !savedProfile || changed;
  elements.todayCameraLabNote.textContent = changed
    ? "Save or discard the selected profile draft before launching Camera Lab."
    : savedProfile ? `Launch the separate Camera Lab app with ${state.detail.name} selected.` : "Choose a saved profile before launching the separate Camera Lab app.";
  elements.finishReadinessBadge.textContent = pending ? "Review needed" : "Ready for Finish Day";
  elements.finishReadinessBadge.className = `workflow-status ${pending ? "notice" : "ready"}`;
  elements.finishDraftNote.textContent = pending
    ? `Resolve ${pending} pending browser ${pending === 1 ? "draft" : "drafts"} before finishing.`
    : "No pending browser drafts. Finish Day will run its required validation and build checks.";
}

const GUARDED_JOB_KEYS = {
  finishDay: "profileEditor.finishDayPrepareJob",
  branchIntegration: "profileEditor.branchIntegrationPrepareJob",
  publication: "profileEditor.publicationJob",
};

function waitMilliseconds(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function renderGuardedJobProgress(progressElements, job) {
  const status = job?.status || "running";
  progressElements.panel.hidden = false;
  progressElements.panel.classList.toggle("is-stopped", status === "failed");
  progressElements.panel.classList.toggle("is-complete", status === "complete");
  progressElements.stage.textContent = status === "failed"
    ? (progressElements.failedStage || "Workflow stopped — not completed")
    : status === "complete"
      ? (progressElements.completedStage || "Workflow complete")
      : (job?.stage || "Starting…");
  progressElements.elapsed.textContent = `${job?.elapsedSeconds || 0}s elapsed`;
  progressElements.command.textContent = job?.command
    || (status === "failed"
      ? (job?.error || "The workflow stopped before completion. Review the command log.")
      : status === "complete"
        ? (progressElements.completedMessage || "All required steps completed.")
        : "Preparing the next command…");
  progressElements.log.textContent = (job?.log || []).join("\n\n");
  progressElements.log.scrollTop = progressElements.log.scrollHeight;
}

async function waitForGuardedJob(jobId, storageKey, progressElements) {
  while (true) {
    let job;
    try {
      job = await request("/api/guarded-job-status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId }),
      });
    } catch (error) {
      if (/unavailable|expired/i.test(error.message)) sessionStorage.removeItem(storageKey);
      throw error;
    }
    renderGuardedJobProgress(progressElements, job);
    if (job.status === "complete") {
      sessionStorage.removeItem(storageKey);
      return job.result;
    }
    if (job.status === "failed") {
      sessionStorage.removeItem(storageKey);
      throw new Error(job.error || "The guarded workflow stopped.");
    }
    await waitMilliseconds(650);
  }
}

const finishDayProgressElements = {
  panel: elements.finishDayProgress,
  stage: elements.finishDayProgressStage,
  elapsed: elements.finishDayProgressElapsed,
  command: elements.finishDayProgressCommand,
  log: elements.finishDayProgressLog,
  failedStage: "Finish Day stopped — not completed",
  completedStage: "Finish Day preparation complete",
  completedMessage: "All required preparation checks completed.",
};

const branchIntegrationProgressElements = {
  panel: elements.branchIntegrationProgress,
  stage: elements.branchIntegrationProgressStage,
  elapsed: elements.branchIntegrationProgressElapsed,
  command: elements.branchIntegrationProgressCommand,
  log: elements.branchIntegrationProgressLog,
  failedStage: "Integration preparation stopped — not completed",
  completedStage: "Integration candidate complete",
  completedMessage: "The isolated integration candidate passed every required check.",
};

const publicationProgressElements = {
  panel: elements.publicationProgress,
  stage: elements.publicationProgressStage,
  elapsed: elements.publicationProgressElapsed,
  command: elements.publicationProgressCommand,
  log: elements.publicationProgressLog,
  failedStage: "Publication stopped — not completed or verified",
  completedStage: "Publication complete and verified",
  completedMessage: "The live website is verified and Main is synchronized.",
};

function showFinishDayMessage(text, error = false) {
  elements.finishDayMessage.textContent = text;
  elements.finishDayMessage.classList.toggle("error", error);
  elements.finishDayMessage.hidden = !text;
}

function renderFinishDay() {
  const result = state.finishDay;
  const phase = result?.phase || "checking";
  const order = ["check", "prepare", "commit", "push"];
  const activePhase = phase === "blocked" || phase === "checking" || phase === "complete" ? "check" : phase;
  const activeIndex = order.indexOf(activePhase);
  for (const [index, step] of elements.finishDaySteps.entries()) {
    step.classList.toggle("is-active", phase !== "complete" && index === activeIndex);
    step.classList.toggle("is-complete", phase === "complete" || index < activeIndex);
  }
  const branch = result?.branch;
  elements.finishDayBranch.textContent = branch || "Checking branch…";
  elements.finishDayBranch.className = `project-context-badge ${branch === "main" ? "main" : branch ? "prototype" : "unknown"}`;
  const status = phase === "complete" ? "ready" : phase === "blocked" ? "blocked" : phase === "checking" ? "checking" : "notice";
  const labels = { ready: "Complete", blocked: "Blocked", checking: "Checking…", notice: "Action needed" };
  elements.finishDayStatusBadge.className = `workflow-status ${status}`;
  elements.finishDayStatusBadge.textContent = labels[status];
  const summaries = {
    checking: "Checking browser drafts and the current Git branch.",
    blocked: (result?.blockers || []).join(" ") || "Finish Day cannot continue until the reported condition is resolved.",
    prepare: "The project has changes. Validate, build, and safely separate generated website files before commit review.",
    commit: "Preparation passed. Review the exact source list and provide a commit message.",
    push: `The local branch has a commit ready to synchronize with ${result?.upstream || "its matching upstream"}.`,
    complete: "The current branch is clean and synchronized. No commit or push is needed.",
  };
  elements.finishDaySummary.textContent = summaries[phase] || summaries.checking;
  elements.finishDayOutput.textContent = result?.output || "";
  elements.finishDayDetails.hidden = !result?.output;
  elements.finishDayPreparePanel.hidden = phase !== "prepare";
  elements.finishDayCommitPanel.hidden = phase !== "commit";
  elements.finishDayPushPanel.hidden = phase !== "push";
  elements.finishDayCompletePanel.hidden = phase !== "complete";
  elements.openBranchIntegration.hidden = phase !== "complete" || branch === "main";
  const files = result?.sourceFiles || [];
  elements.finishDayFileCount.textContent = `${files.length} ${files.length === 1 ? "file" : "files"}`;
  elements.finishDayFileList.textContent = files.join("\n") || "No source files are waiting for commit.";
  elements.finishDayPushTarget.textContent = branch && result?.upstream
    ? `Push ${branch} only to ${result.upstream}. GitHub Pages is not published by Finish Day.`
    : "The exact branch and matching upstream must be confirmed before push.";
  elements.refreshFinishDay.disabled = state.finishDayBusy;
  elements.prepareFinishDay.disabled = state.finishDayBusy || !elements.finishDayConfirmPrepare.checked;
  elements.commitFinishDay.disabled = state.finishDayBusy
    || !elements.finishDayConfirmCommit.checked
    || !elements.finishDayCommitMessage.value.trim()
    || !state.finishDayReviewToken;
  elements.pushFinishDay.disabled = state.finishDayBusy || !elements.finishDayConfirmPush.checked;
}

async function refreshFinishDay() {
  captureCurrentProfileDraft();
  const runningJobId = sessionStorage.getItem(GUARDED_JOB_KEYS.finishDay);
  if (runningJobId) {
    state.finishDayBusy = true;
    state.finishDay = { phase: "prepare" };
    showFinishDayMessage("Reconnected to Finish Day preparation.");
    renderFinishDay();
    try {
      const result = await waitForGuardedJob(
        runningJobId,
        GUARDED_JOB_KEYS.finishDay,
        finishDayProgressElements,
      );
      state.finishDay = result;
      state.finishDayReviewToken = result.reviewToken || null;
      showFinishDayMessage(result.phase === "commit" ? "Preparation passed. Review every source file before committing." : "Preparation completed.");
    } catch (error) {
      state.finishDay = { phase: "prepare" };
      showFinishDayMessage(error.message, true);
    } finally {
      state.finishDayBusy = false;
      renderFinishDay();
    }
    return;
  }
  state.finishDayBusy = true;
  state.finishDay = null;
  state.finishDayReviewToken = null;
  elements.finishDayProgress.hidden = true;
  showFinishDayMessage("");
  renderFinishDay();
  try {
    state.finishDay = await request("/api/finish-day-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length }),
    });
  } catch (error) {
    state.finishDay = { phase: "blocked", blockers: [error.message], output: "" };
    showFinishDayMessage(error.message, true);
  } finally {
    state.finishDayBusy = false;
    renderFinishDay();
  }
}

async function prepareFinishDay() {
  state.finishDayBusy = true;
  elements.finishDayProgress.hidden = false;
  showFinishDayMessage("Running required validation and preparing the exact source handoff. Keep this page open.");
  renderFinishDay();
  try {
    const started = await request("/api/finish-day-prepare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length, confirmPrepare: true }),
    });
    sessionStorage.setItem(GUARDED_JOB_KEYS.finishDay, started.jobId);
    const result = await waitForGuardedJob(
      started.jobId,
      GUARDED_JOB_KEYS.finishDay,
      finishDayProgressElements,
    );
    state.finishDay = result;
    state.finishDayReviewToken = result.reviewToken || null;
    elements.finishDayConfirmPrepare.checked = false;
    showFinishDayMessage(result.phase === "commit" ? "Preparation passed. Review every source file before committing." : "Preparation completed. Review the current state.");
  } catch (error) {
    showFinishDayMessage(error.message, true);
  } finally {
    state.finishDayBusy = false;
    renderFinishDay();
  }
}

async function commitFinishDay() {
  state.finishDayBusy = true;
  showFinishDayMessage("Committing exactly the reviewed source files. Nothing will be pushed yet.");
  renderFinishDay();
  try {
    const result = await request("/api/finish-day-commit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reviewToken: state.finishDayReviewToken,
        message: elements.finishDayCommitMessage.value,
        confirmCommit: true,
      }),
    });
    state.finishDay = result;
    state.finishDayReviewToken = null;
    elements.finishDayConfirmCommit.checked = false;
    showFinishDayMessage("Source committed. Push remains a separate approval.");
  } catch (error) {
    state.finishDayReviewToken = null;
    showFinishDayMessage(error.message, true);
  } finally {
    state.finishDayBusy = false;
    renderFinishDay();
  }
}

async function pushFinishDay() {
  state.finishDayBusy = true;
  showFinishDayMessage("Pushing the current branch to its exact matching upstream and verifying synchronization.");
  renderFinishDay();
  try {
    state.finishDay = await request("/api/finish-day-push", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirmPush: true }),
    });
    elements.finishDayConfirmPush.checked = false;
    showFinishDayMessage(state.finishDay.message || "Finished for today.");
  } catch (error) {
    showFinishDayMessage(error.message, true);
  } finally {
    state.finishDayBusy = false;
    renderFinishDay();
  }
}

function showBranchIntegrationMessage(text, error = false) {
  elements.branchIntegrationMessage.textContent = text;
  elements.branchIntegrationMessage.classList.toggle("error", error);
  elements.branchIntegrationMessage.hidden = !text;
}

function renderBranchIntegration() {
  const result = state.branchIntegration;
  const phase = result?.phase || "checking";
  const order = ["check", "review", "merge-main", "push-main", "resync"];
  const activePhase = phase === "blocked" || phase === "checking" || phase === "complete" ? "check" : phase;
  const activeIndex = order.indexOf(activePhase);
  for (const [index, step] of elements.branchIntegrationSteps.entries()) {
    step.classList.toggle("is-active", phase !== "complete" && index === activeIndex);
    step.classList.toggle("is-complete", phase === "complete" || index < activeIndex);
  }
  const branch = result?.branch;
  elements.branchIntegrationBranch.textContent = branch || "Checking branch…";
  elements.branchIntegrationBranch.className = `project-context-badge ${branch === "main" ? "main" : branch ? "prototype" : "unknown"}`;
  const status = phase === "complete" ? "ready" : phase === "blocked" ? "blocked" : phase === "checking" ? "checking" : "notice";
  const labels = { ready: "Complete", blocked: "Blocked", checking: "Checking…", notice: "Approval needed" };
  elements.branchIntegrationStatusBadge.className = `workflow-status ${status}`;
  elements.branchIntegrationStatusBadge.textContent = labels[status];
  const summaries = {
    checking: "Checking the working branch and origin/main.",
    blocked: (result?.blockers || []).join(" ") || "Branch integration cannot continue until the reported condition is resolved.",
    review: "The working branch is clean and synchronized. Prepare an isolated, fully validated integration candidate.",
    "merge-main": "The isolated candidate passed. Review every commit and file before changing local main.",
    "push-main": "The exact reviewed tree is committed on local main. Nothing has been pushed or published.",
    resync: "Main contains the working branch. Resynchronize the working branch without rewriting history.",
    complete: "Main and the working branch are synchronized. No integration action is needed.",
  };
  elements.branchIntegrationSummary.textContent = summaries[phase] || summaries.checking;
  elements.branchIntegrationOutput.textContent = result?.output || "";
  elements.branchIntegrationDetails.hidden = !result?.output;
  elements.branchIntegrationReviewPanel.hidden = phase !== "review";
  elements.branchIntegrationMergePanel.hidden = phase !== "merge-main";
  elements.branchIntegrationPushPanel.hidden = phase !== "push-main";
  elements.branchIntegrationResyncPanel.hidden = phase !== "resync";
  elements.branchIntegrationCompletePanel.hidden = phase !== "complete";
  elements.branchIntegrationCompleteMessage.textContent = result?.message
    || "Main and the working branch are synchronized. The website was not published.";
  const appRefresh = result?.appRefresh;
  elements.branchIntegrationAppStatus.hidden = !appRefresh;
  elements.branchIntegrationAppStatus.textContent = appRefresh?.message || "";
  elements.branchIntegrationAppStatus.classList.toggle("error", appRefresh?.status === "failed");
  const commits = result?.commits || [];
  const files = result?.files || [];
  elements.branchIntegrationCommitList.textContent = commits.join("\n") || "No commits are waiting for integration.";
  elements.branchIntegrationFileCount.textContent = `${files.length} ${files.length === 1 ? "file" : "files"}`;
  elements.branchIntegrationFileList.textContent = files.join("\n") || "No files differ from current main.";
  elements.refreshBranchIntegration.disabled = state.branchIntegrationBusy;
  elements.prepareBranchIntegration.disabled = state.branchIntegrationBusy || !elements.branchIntegrationConfirmPrepare.checked;
  elements.mergeBranchToMain.disabled = state.branchIntegrationBusy
    || !elements.branchIntegrationConfirmMerge.checked
    || !state.branchIntegrationReviewToken;
  elements.pushIntegratedMain.disabled = state.branchIntegrationBusy || !elements.branchIntegrationConfirmPush.checked;
  elements.resyncIntegratedBranch.disabled = state.branchIntegrationBusy || !elements.branchIntegrationConfirmResync.checked;
}

async function refreshBranchIntegration() {
  captureCurrentProfileDraft();
  const runningJobId = sessionStorage.getItem(GUARDED_JOB_KEYS.branchIntegration);
  if (runningJobId) {
    state.branchIntegrationBusy = true;
    state.branchIntegration = { phase: "review" };
    showBranchIntegrationMessage("Reconnected to integration preparation.");
    renderBranchIntegration();
    try {
      const result = await waitForGuardedJob(
        runningJobId,
        GUARDED_JOB_KEYS.branchIntegration,
        branchIntegrationProgressElements,
      );
      state.branchIntegration = result;
      state.branchIntegrationReviewToken = result.reviewToken || null;
      showBranchIntegrationMessage(result.phase === "merge-main" ? "Candidate passed. Review the exact commits and files." : "Integration state refreshed.");
    } catch (error) {
      state.branchIntegration = { phase: "review" };
      showBranchIntegrationMessage(error.message, true);
    } finally {
      state.branchIntegrationBusy = false;
      renderBranchIntegration();
    }
    return;
  }
  state.branchIntegrationBusy = true;
  state.branchIntegration = null;
  state.branchIntegrationReviewToken = null;
  elements.branchIntegrationProgress.hidden = true;
  showBranchIntegrationMessage("");
  renderBranchIntegration();
  try {
    const result = await request("/api/branch-integration-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length }),
    });
    state.branchIntegration = result;
    state.branchIntegrationReviewToken = result.reviewToken || null;
  } catch (error) {
    state.branchIntegration = { phase: "blocked", blockers: [error.message], output: "" };
    showBranchIntegrationMessage(error.message, true);
  } finally {
    state.branchIntegrationBusy = false;
    renderBranchIntegration();
  }
}

async function prepareBranchIntegration() {
  state.branchIntegrationBusy = true;
  elements.branchIntegrationProgress.hidden = false;
  showBranchIntegrationMessage("Building and validating the isolated integration candidate. No real branch is being changed.");
  renderBranchIntegration();
  try {
    const started = await request("/api/branch-integration-prepare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length, confirmPrepare: true }),
    });
    sessionStorage.setItem(GUARDED_JOB_KEYS.branchIntegration, started.jobId);
    const result = await waitForGuardedJob(
      started.jobId,
      GUARDED_JOB_KEYS.branchIntegration,
      branchIntegrationProgressElements,
    );
    state.branchIntegration = result;
    state.branchIntegrationReviewToken = result.reviewToken || null;
    elements.branchIntegrationConfirmPrepare.checked = false;
    showBranchIntegrationMessage(result.phase === "merge-main" ? "Candidate passed. Review the exact commits and files." : "Integration state refreshed.");
  } catch (error) {
    showBranchIntegrationMessage(error.message, true);
  } finally {
    state.branchIntegrationBusy = false;
    renderBranchIntegration();
  }
}

async function mergeBranchToMain() {
  state.branchIntegrationBusy = true;
  showBranchIntegrationMessage("Applying the exact reviewed tree to local main. Nothing will be pushed.");
  renderBranchIntegration();
  try {
    const result = await request("/api/branch-integration-merge-main", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.branchIntegrationReviewToken, confirmMergeMain: true }),
    });
    state.branchIntegration = result;
    state.branchIntegrationReviewToken = null;
    elements.branchIntegrationConfirmMerge.checked = false;
    showBranchIntegrationMessage(result.message || "Local main updated. Push remains a separate approval.");
  } catch (error) {
    state.branchIntegrationReviewToken = null;
    showBranchIntegrationMessage(error.message, true);
  } finally {
    state.branchIntegrationBusy = false;
    renderBranchIntegration();
  }
}

async function pushIntegratedMain() {
  state.branchIntegrationBusy = true;
  showBranchIntegrationMessage("Pushing the reviewed main integration. The website publisher is not being called.");
  renderBranchIntegration();
  try {
    const result = await request("/api/branch-integration-push-main", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirmPushMain: true }),
    });
    state.branchIntegration = result;
    elements.branchIntegrationConfirmPush.checked = false;
    showBranchIntegrationMessage(result.message || "Main synchronized. Resynchronize the working branch next.");
  } catch (error) {
    showBranchIntegrationMessage(error.message, true);
  } finally {
    state.branchIntegrationBusy = false;
    renderBranchIntegration();
  }
}

async function resyncIntegratedBranch() {
  state.branchIntegrationBusy = true;
  showBranchIntegrationMessage("Fast-forwarding the working branch, then checking and refreshing the Main app wrappers when needed.");
  renderBranchIntegration();
  try {
    const result = await request("/api/branch-integration-resync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirmResync: true }),
    });
    state.branchIntegration = result;
    elements.branchIntegrationConfirmResync.checked = false;
    showBranchIntegrationMessage(result.message || "Integration complete.");
  } catch (error) {
    showBranchIntegrationMessage(error.message, true);
  } finally {
    state.branchIntegrationBusy = false;
    renderBranchIntegration();
  }
}

function selectedPublicationMajor() {
  if (elements.publicationVersionKind.value !== "major") return null;
  const value = Number.parseInt(elements.publicationMajorVersion.value, 10);
  return Number.isInteger(value) ? value : elements.publicationMajorVersion.value;
}

function selectedSpreadsheetMode() {
  return elements.publicationSpreadsheetChoices.find((choice) => choice.checked)?.value || "preserve";
}

function releaseHighlights() {
  return elements.publicationHighlights.value.split("\n").map((line) => line.trim()).filter(Boolean);
}

function showPublicationMessage(text, error = false) {
  elements.publicationMessage.textContent = text;
  elements.publicationMessage.classList.toggle("error", error);
  elements.publicationMessage.hidden = !text;
}

function renderPublication() {
  const result = state.publication;
  const phase = result?.phase || "checking";
  const branch = result?.branch;
  elements.publicationContext.textContent = branch === "main" ? "Main project" : branch ? `Prototype · ${branch}` : "Checking project…";
  elements.publicationContext.className = `project-context-badge ${branch === "main" ? "main" : branch ? "prototype" : "unknown"}`;
  const blocked = phase === "blocked" || phase === "main-handoff";
  elements.publicationStatusBadge.className = `workflow-status ${phase === "complete" || phase === "ready" ? "ready" : blocked ? "blocked" : phase === "checking" ? "checking" : "notice"}`;
  elements.publicationStatusBadge.textContent = phase === "ready" ? "Ready to review" : phase === "complete" ? "Verified" : blocked ? "Blocked" : phase === "checking" ? "Checking…" : "Preparation needed";
  const summaries = {
    checking: "Checking the current project and publication inputs.",
    "main-handoff": "Live publication must continue in the Main project editor after approved work is integrated.",
    blocked: (result?.blockers || []).join(" ") || "Publication is blocked by the current project state.",
    "release-notes": `Reader-facing highlights are required for Version ${result?.nextVersion || "the next version"}.`,
    ready: `Version ${result?.nextVersion} is ready for an exact publication review.`,
    complete: result?.message || "The live website is published and verified.",
  };
  elements.publicationSummary.textContent = summaries[phase] || summaries.checking;
  elements.publicationOutput.textContent = [result?.output, result?.spreadsheetState?.output].filter(Boolean).join("\n\n");
  elements.publicationDetails.hidden = !elements.publicationOutput.textContent;
  elements.publicationMainHandoff.hidden = phase !== "main-handoff";
  elements.publicationNotesPanel.hidden = phase !== "release-notes";
  elements.publicationOptionsPanel.hidden = phase !== "ready";
  elements.publicationComplete.hidden = phase !== "complete";
  elements.publicationNotesVersion.textContent = result?.nextVersion ? `Version ${result.nextVersion}` : "the next version";
  elements.publicationVersionLabel.textContent = result?.nextVersion ? `Version ${result.nextVersion}` : "the next version";
  if (result?.highlights?.length && !elements.publicationHighlights.value.trim()) elements.publicationHighlights.value = result.highlights.join("\n");
  const sheetStatus = result?.spreadsheetState?.status;
  elements.publicationSpreadsheetStatus.textContent = sheetStatus === "current"
    ? "Spreadsheet downloads are current."
    : sheetStatus === "refresh-needed"
      ? "Spreadsheet inputs changed. Choose rebuild and replace, or deliberately remove the downloads."
      : sheetStatus === "blocked" ? "Spreadsheet readiness is blocked; review the details above." : "";
  elements.reviewPublicationNotes.disabled = state.publicationBusy || !releaseHighlights().length;
  elements.reviewPublication.disabled = state.publicationBusy || phase !== "ready";
  elements.refreshPublication.disabled = state.publicationBusy;
  elements.openMainEditor.disabled = state.publicationBusy;
  if (phase === "complete") elements.publicationCompleteMessage.textContent = result.message;
}

async function refreshPublication() {
  captureCurrentProfileDraft();
  const runningJobId = sessionStorage.getItem(GUARDED_JOB_KEYS.publication);
  if (runningJobId) {
    state.publicationBusy = true;
    elements.publicationProgress.hidden = false;
    showPublicationMessage("Reconnected to the running publication.");
    renderPublication();
    try {
      const result = await waitForGuardedJob(runningJobId, GUARDED_JOB_KEYS.publication, publicationProgressElements);
      state.publication = result;
      showPublicationMessage(result.message || "Publication complete and verified.");
    } catch (error) {
      showPublicationMessage(error.message, true);
    } finally {
      state.publicationBusy = false;
      renderPublication();
    }
    return;
  }
  state.publicationBusy = true;
  state.publicationReviewToken = null;
  showPublicationMessage("");
  renderPublication();
  try {
    state.publication = await request("/api/publication-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length, majorVersion: selectedPublicationMajor() }),
    });
  } catch (error) {
    state.publication = { phase: "blocked", blockers: [error.message] };
    showPublicationMessage(error.message, true);
  } finally {
    state.publicationBusy = false;
    renderPublication();
  }
}

async function openMainEditor() {
  elements.openMainEditor.disabled = true;
  showPublicationMessage("Opening the Main project editor…");
  try {
    await request("/api/main-editor-launch", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    showPublicationMessage("The Main project editor is opening in Chrome.");
  } catch (error) {
    showPublicationMessage(error.message, true);
  } finally {
    elements.openMainEditor.disabled = false;
  }
}

async function reviewPublicationNotes() {
  elements.reviewPublicationNotes.disabled = true;
  showPublicationMessage("Validating the highlights and preparing the exact source addition…");
  try {
    const result = await request("/api/publication-notes-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ majorVersion: selectedPublicationMajor(), highlights: releaseHighlights() }),
    });
    state.publicationNotesReviewToken = result.reviewToken;
    elements.publicationNotesDiff.textContent = result.diff;
    elements.publicationNotesConfirm.checked = false;
    elements.savePublicationNotes.disabled = true;
    elements.publicationNotesDialog.showModal();
    showPublicationMessage("Review the exact release-note addition before saving.");
  } catch (error) {
    showPublicationMessage(error.message, true);
  } finally {
    renderPublication();
  }
}

function closePublicationNotesReview() {
  state.publicationNotesReviewToken = null;
  elements.publicationNotesDialog.close();
}

async function savePublicationNotes() {
  elements.savePublicationNotes.disabled = true;
  showPublicationMessage("Creating a recovery backup and validating the reviewed release notes…");
  try {
    const result = await request("/api/publication-notes-save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.publicationNotesReviewToken, confirmSave: true }),
    });
    state.publicationNotesReviewToken = null;
    elements.publicationNotesDialog.close();
    invalidateBuildReadiness();
    showPublicationMessage(`${result.message} Recovery backup: ${result.backup}`);
    switchView("finish-day");
  } catch (error) {
    state.publicationNotesReviewToken = null;
    elements.publicationNotesDialog.close();
    showPublicationMessage(error.message, true);
  }
}

async function reviewPublication() {
  elements.reviewPublication.disabled = true;
  showPublicationMessage("Binding the exact version, source state, and spreadsheet choice…");
  try {
    const result = await request("/api/publication-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length, majorVersion: selectedPublicationMajor(), spreadsheetMode: selectedSpreadsheetMode() }),
    });
    state.publicationReviewToken = result.reviewToken;
    elements.publicationReviewSummary.textContent = result.summary;
    elements.publicationReviewHighlights.replaceChildren();
    for (const highlight of result.highlights || []) {
      const item = document.createElement("li");
      item.textContent = highlight;
      elements.publicationReviewHighlights.append(item);
    }
    elements.publicationConfirmLive.checked = false;
    elements.startPublication.disabled = true;
    elements.publicationConfirmDialog.showModal();
    showPublicationMessage("Review the exact live publication and confirm only when ready.");
  } catch (error) {
    state.publicationReviewToken = null;
    showPublicationMessage(error.message, true);
  } finally {
    renderPublication();
  }
}

function closePublicationConfirmation() {
  state.publicationReviewToken = null;
  elements.publicationConfirmDialog.close();
}

async function startPublication() {
  const reviewToken = state.publicationReviewToken;
  if (!reviewToken) return;
  state.publicationReviewToken = null;
  elements.publicationConfirmDialog.close();
  state.publicationBusy = true;
  elements.publicationProgress.hidden = false;
  showPublicationMessage("Publishing the reviewed release. Keep this editor open; refreshing will reconnect.");
  renderPublication();
  try {
    const started = await request("/api/publication-start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken, confirmPublish: true }),
    });
    sessionStorage.setItem(GUARDED_JOB_KEYS.publication, started.jobId);
    const result = await waitForGuardedJob(started.jobId, GUARDED_JOB_KEYS.publication, publicationProgressElements);
    state.publication = result;
    showPublicationMessage(result.message || "Publication complete and verified.");
  } catch (error) {
    showPublicationMessage(error.message, true);
  } finally {
    state.publicationBusy = false;
    renderPublication();
  }
}

function formatFileSize(bytes) {
  const value = Number(bytes || 0);
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  if (value < 1024 * 1024 * 1024) return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  return `${(value / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function showCleanupReviewMessage(text, error = false) {
  elements.cleanupReviewMessage.textContent = text;
  elements.cleanupReviewMessage.classList.toggle("error", error);
  elements.cleanupReviewMessage.hidden = !text;
}

function cleanupCandidateCard(item, selectable) {
  const card = document.createElement(selectable ? "label" : "div");
  card.className = "cleanup-candidate";
  if (selectable) {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.dataset.cleanupId = item.id;
    checkbox.addEventListener("change", renderCleanupSelection);
    card.append(checkbox);
  }
  const main = document.createElement("span");
  main.className = "cleanup-candidate-main";
  const name = document.createElement("strong");
  name.textContent = item.name;
  const path = document.createElement("span");
  path.className = "cleanup-candidate-path";
  path.textContent = item.path;
  const reason = document.createElement("span");
  reason.className = "cleanup-candidate-reason";
  reason.textContent = `${item.reason} Modified ${item.modified}.`;
  main.append(name, path, reason);
  const size = document.createElement("span");
  size.className = "cleanup-candidate-size";
  size.textContent = formatFileSize(item.sizeBytes);
  card.append(main, size);
  return card;
}

function selectedCleanupIds() {
  return [...elements.cleanupCandidateList.querySelectorAll("input[data-cleanup-id]:checked")]
    .map((input) => input.dataset.cleanupId);
}

function renderCleanupSelection() {
  const selected = selectedCleanupIds();
  elements.cleanupSelectedSummary.textContent = selected.length
    ? `${selected.length} exact ${selected.length === 1 ? "item" : "items"} selected.`
    : "No items selected.";
  elements.deleteCleanupCandidates.disabled = state.cleanupBusy
    || !elements.cleanupConfirmDelete.checked
    || !selected.length
    || !state.cleanupReviewToken;
}

function renderCleanupReview() {
  const result = state.cleanupReview;
  const candidates = result?.candidates || [];
  const protectedItems = result?.protected || [];
  elements.cleanupReviewCount.className = `workflow-status ${candidates.length ? "notice" : result ? "ready" : "checking"}`;
  elements.cleanupReviewCount.textContent = result ? `${candidates.length} optional` : "Checking…";
  elements.cleanupReviewSummary.textContent = result?.message || "Checking workflow-owned backups and disposable metadata.";
  elements.cleanupCandidateList.replaceChildren();
  if (result && !candidates.length) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = "Nothing recognized as safe optional cleanup.";
    elements.cleanupCandidateList.append(empty);
  } else {
    for (const item of candidates) elements.cleanupCandidateList.append(cleanupCandidateCard(item, true));
  }
  elements.cleanupProtectedList.replaceChildren();
  for (const item of protectedItems) elements.cleanupProtectedList.append(cleanupCandidateCard(item, false));
  elements.cleanupProtectedDetails.hidden = !protectedItems.length;
  elements.cleanupProtectedSummary.textContent = `Show ${protectedItems.length} protected newest ${protectedItems.length === 1 ? "backup" : "backups"}`;
  elements.refreshCleanupReview.disabled = state.cleanupBusy;
  elements.cleanupConfirmDelete.checked = false;
  renderCleanupSelection();
}

async function refreshCleanupReview() {
  state.cleanupBusy = true;
  state.cleanupReview = null;
  state.cleanupReviewToken = null;
  showCleanupReviewMessage("");
  renderCleanupReview();
  try {
    const result = await request("/api/cleanup-status", { method: "POST", body: "{}" });
    state.cleanupReview = result;
    state.cleanupReviewToken = result.reviewToken || null;
  } catch (error) {
    showCleanupReviewMessage(error.message, true);
  } finally {
    state.cleanupBusy = false;
    renderCleanupReview();
  }
}

async function deleteCleanupCandidates() {
  const candidateIds = selectedCleanupIds();
  state.cleanupBusy = true;
  elements.deleteCleanupCandidates.disabled = true;
  showCleanupReviewMessage("Deleting only the exact reviewed selections.");
  try {
    const result = await request("/api/cleanup-delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reviewToken: state.cleanupReviewToken,
        candidateIds,
        confirmDelete: true,
      }),
    });
    state.cleanupReview = result;
    state.cleanupReviewToken = result.reviewToken || null;
    showCleanupReviewMessage(`${result.message} Recovered ${formatFileSize(result.deletedBytes)}.`);
  } catch (error) {
    state.cleanupReviewToken = null;
    showCleanupReviewMessage(error.message, true);
  } finally {
    state.cleanupBusy = false;
    renderCleanupReview();
  }
}

async function runWorkflowPreflight() {
  elements.refreshWorkflowPreflight.disabled = true;
  state.workflowPreflight = null;
  renderWorkflowPreflight();
  try {
    state.workflowPreflight = await request("/api/workflow-preflight", { method: "POST", body: "{}" });
  } catch (error) {
    state.workflowPreflight = { status: "blocked", summary: error.message, output: "" };
  } finally {
    elements.refreshWorkflowPreflight.disabled = false;
    renderWorkflowPreflight();
  }
}

function showBaselineMessage(text, error = false) {
  elements.baselineMessage.textContent = text;
  elements.baselineMessage.classList.toggle("error", error);
  elements.baselineMessage.hidden = !text;
}

function showMyMenuColorMessage(text, error = false) {
  elements.myMenuColorMessage.textContent = text;
  elements.myMenuColorMessage.classList.toggle("error", error);
  elements.myMenuColorMessage.hidden = !text;
}

function showCxFoundationMessage(text, error = false) {
  elements.cxFoundationMessage.textContent = text;
  elements.cxFoundationMessage.classList.toggle("error", error);
  elements.cxFoundationMessage.hidden = !text;
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
    loadSavedMenus(false);
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
    state.migrationReviewToken = null;
    renderBaseline();
    invalidateBuildReadiness();
    renderSessionStatus();
    elements.analyzeMyMenu.disabled = false;
    showBaselineMessage("No proposed baseline changes. My Menu profile coverage can still be analyzed.");
  } catch (error) {
    showBaselineMessage(error.message, true);
  }
}

function hasCxAssignmentChanges() {
  return Boolean(state.cxFoundation) && !equal(state.cxAssignments, state.cxFoundation.assignments);
}

function hasCxSelectionChanges() {
  return state.cxSelectionDrafts.size > 0;
}

function cxSelectedProfileTitle() {
  return state.cxFoundation?.profiles?.find((profile) => profile.name === state.cxSelectedProfile)?.title
    || state.cxSelectedProfile
    || "Profile";
}

async function loadCxFoundations(preserveDraft = false) {
  showCxFoundationMessage("Loading saved C1-C3 assignments…");
  try {
    const detail = await request("/api/cx-foundations");
    state.cxFoundation = detail;
    if (!preserveDraft) {
      state.cxAssignments = clone(detail.assignments);
      state.cxSelectionDrafts.clear();
    }
    state.cxSelectedProfile = detail.selectedProfile;
    state.cxSelectedStart = detail.selectedStart || "";
    state.cxSavedSelectedStart = detail.selectedStart || "";
    state.cxReviewToken = null;
    populateCxProfileSelect();
    renderCxAssignments();
    renderCxFit(detail);
    renderSessionStatus();
    showCxFoundationMessage("Saved foundations loaded. Recommendations are advisory until you explicitly review and save.");
  } catch (error) {
    showCxFoundationMessage(error.message, true);
  }
}

function populateCxProfileSelect() {
  elements.cxProfileSelect.replaceChildren();
  for (const profile of state.cxFoundation?.profiles || []) {
    const option = document.createElement("option");
    option.value = profile.name;
    option.textContent = profile.title;
    elements.cxProfileSelect.append(option);
  }
  elements.cxProfileSelect.value = state.cxSelectedProfile || "";
  elements.cxProfileSelect.disabled = !elements.cxProfileSelect.options.length;
}

function renderCxAssignments() {
  elements.cxAssignmentGrid.replaceChildren();
  const profiles = state.cxFoundation?.profiles || [];
  for (const start of ["C1", "C2", "C3"]) {
    const card = document.createElement("article");
    card.className = "cx-assignment-card";
    const title = document.createElement("strong");
    title.textContent = start;
    const label = document.createElement("label");
    label.textContent = "Assigned complete profile";
    const select = document.createElement("select");
    select.dataset.start = start;
    for (const profile of profiles) {
      const option = document.createElement("option");
      option.value = profile.title;
      option.textContent = profile.title;
      option.selected = state.cxAssignments[start] === profile.title;
      select.append(option);
    }
    select.addEventListener("change", async () => {
      const previous = state.cxAssignments[start];
      const occupiedStart = ["C1", "C2", "C3"].find(
        (candidate) => candidate !== start && state.cxAssignments[candidate] === select.value,
      );
      if (occupiedStart) state.cxAssignments[occupiedStart] = previous;
      state.cxAssignments[start] = select.value;
      state.cxReviewToken = null;
      invalidateBuildReadiness();
      renderCxAssignments();
      renderSessionStatus();
      await refreshCxFoundationFit();
    });
    const note = document.createElement("small");
    note.textContent = "Registration evidence is tracked separately; changing an assignment requires physical re-verification.";
    label.append(select);
    card.append(title, label, note);
    elements.cxAssignmentGrid.append(card);
  }
  elements.reviewCxAssignments.disabled = !hasCxAssignmentChanges();
}

async function refreshCxFoundationFit() {
  if (!state.cxSelectedProfile || !state.cxFoundation) return;
  const profileDraft = state.profileDrafts.get(`profile:${state.cxSelectedProfile}`);
  showCxFoundationMessage("Comparing the selected card with all three foundations…");
  try {
    const detail = await request("/api/cx-foundation-fit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile: state.cxSelectedProfile,
        assignments: state.cxAssignments,
        overrides: profileDraft?.payload?.overrides,
      }),
    });
    state.cxFoundation = { ...state.cxFoundation, ...detail, assignments: state.cxFoundation.assignments };
    state.cxSavedSelectedStart = detail.selectedStart || "";
    state.cxSelectedStart = state.cxSelectionDrafts.has(state.cxSelectedProfile)
      ? state.cxSelectionDrafts.get(state.cxSelectedProfile)
      : state.cxSavedSelectedStart;
    renderCxFit(detail);
    showCxFoundationMessage(
      profileDraft
        ? "Fit refreshed from the unsaved profile draft. Save or discard that profile draft before saving its Cx selection."
        : "Fit refreshed. The lowest-change result is a recommendation only."
    );
  } catch (error) {
    showCxFoundationMessage(error.message, true);
  }
}

function renderCxFit(detail = state.cxFoundation) {
  if (!detail) return;
  const fit = detail.fit || [];
  const recommended = fit.filter((item) => item.recommended);
  elements.cxFitSummary.textContent = recommended.length
    ? `Recommended: ${recommended.map((item) => `${item.foundation_label} — ${item.change_count} ${item.change_count === 1 ? "field change" : "field changes"}`).join("; ")}. You make the final selection.`
    : "No foundation recommendation is available.";
  elements.cxFitResults.replaceChildren();
  for (const item of [...fit, { start: "", foundation_label: "No Cx", source_profile: "No registered foundation", change_count: fit[0]?.total_rows || 0, total_rows: fit[0]?.total_rows || 0, recommended: false }]) {
    const label = document.createElement("label");
    label.className = "cx-fit-option";
    label.classList.toggle("is-recommended", item.recommended);
    label.classList.toggle("is-selected", state.cxSelectedStart === item.start);
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "cx-foundation-choice";
    radio.value = item.start;
    radio.checked = state.cxSelectedStart === item.start;
    radio.addEventListener("change", () => selectCxFoundation(item.start));
    const name = document.createElement("strong");
    name.textContent = item.foundation_label;
    const count = document.createElement("span");
    count.className = "cx-fit-count";
    count.textContent = String(item.change_count);
    const detailText = document.createElement("small");
    detailText.textContent = item.start
      ? `${item.change_count === 1 ? "field change" : "field changes"} across ${item.total_rows} visible card rows`
      : `verify/set all ${item.total_rows} visible card rows`;
    label.append(radio, name);
    const badges = document.createElement("span");
    badges.className = "cx-fit-badges";
    if (item.recommended) {
      const badge = document.createElement("span");
      badge.className = "cx-recommendation";
      badge.textContent = "Recommended";
      badges.append(badge);
    }
    if (state.cxSelectedStart === item.start) {
      const badge = document.createElement("span");
      badge.className = "cx-selected-badge";
      badge.textContent = "Your selection";
      badges.append(badge);
    }
    if (badges.childElementCount) label.append(badges);
    label.append(count, detailText);
    elements.cxFitResults.append(label);
  }
  updateCxSelectionState();
}

function selectCxFoundation(start) {
  state.cxSelectedStart = start;
  if (start === state.cxSavedSelectedStart) state.cxSelectionDrafts.delete(state.cxSelectedProfile);
  else state.cxSelectionDrafts.set(state.cxSelectedProfile, start);
  state.cxReviewToken = null;
  invalidateBuildReadiness();
  renderCxFit();
  renderSessionStatus();
}

function updateCxSelectionState() {
  const selectedFit = state.cxFoundation?.fit?.find((item) => item.start === state.cxSelectedStart);
  const selection = state.cxSelectedStart
    ? `${state.cxSelectedStart} · ${state.cxAssignments[state.cxSelectedStart]}`
    : "No Cx";
  elements.cxSelectionStatus.textContent = `Currently selected: ${selection}${selectedFit ? ` — ${selectedFit.change_count} field changes` : ""}.`;
  const profileDraft = state.profileDrafts.has(`profile:${state.cxSelectedProfile}`);
  elements.reviewCxSelection.disabled = !state.cxSelectionDrafts.has(state.cxSelectedProfile) || profileDraft;
}

async function reviewCxAssignments() {
  elements.reviewCxAssignments.disabled = true;
  showCxFoundationMessage("Preparing the exact synchronized assignment diff…");
  try {
    const review = await request("/api/cx-assignment-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assignments: state.cxAssignments }),
    });
    showCxReview(review);
  } catch (error) {
    showCxFoundationMessage(error.message, true);
  } finally {
    elements.reviewCxAssignments.disabled = !hasCxAssignmentChanges();
  }
}

async function reviewCxSelection() {
  elements.reviewCxSelection.disabled = true;
  showCxFoundationMessage("Preparing the exact card-route diff…");
  try {
    const review = await request("/api/cx-selection-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile: state.cxSelectedProfile, start: state.cxSelectedStart }),
    });
    showCxReview(review);
  } catch (error) {
    showCxFoundationMessage(error.message, true);
  } finally {
    updateCxSelectionState();
  }
}

function showCxReview(review) {
  state.cxReviewToken = review.reviewToken;
  state.cxReviewKind = review.reviewKind;
  elements.cxFoundationReviewSummary.textContent = review.summary;
  elements.cxFoundationReviewDiff.textContent = review.diff;
  elements.cxFoundationReviewDialog.showModal();
  showCxFoundationMessage("Candidate validation passed. Review the exact YAML before saving.");
}

async function saveCxFoundation() {
  if (!state.cxReviewToken) return;
  elements.saveCxFoundation.disabled = true;
  showCxFoundationMessage("Creating a recovery backup and saving the reviewed Cx Foundation changes…");
  try {
    const result = await request("/api/cx-foundation-saves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.cxReviewToken }),
    });
    state.cxReviewToken = null;
    const savedKind = state.cxReviewKind;
    state.cxReviewKind = null;
    elements.cxFoundationReviewDialog.close();
    await loadProfiles(state.detail?.name, false);
    if (savedKind === "selection") state.cxSelectionDrafts.delete(state.cxSelectedProfile);
    await loadCxFoundations(true);
    invalidateBuildReadiness();
    renderSessionStatus();
    showCxFoundationMessage(`Cx Foundation saved and validated. Recovery backup: ${result.backup}`);
  } catch (error) {
    state.cxReviewToken = null;
    state.cxReviewKind = null;
    elements.cxFoundationReviewDialog.close();
    showCxFoundationMessage(error.message, true);
  } finally {
    elements.saveCxFoundation.disabled = false;
  }
}

function switchView(viewName) {
  state.activeView = viewName;
  const profilesView = document.querySelector("#profiles-view");
  if (viewName !== "profiles" && profilesView && !profilesView.hidden) captureCurrentProfileDraft();
  for (const tab of elements.viewTabs) tab.classList.toggle("is-active", tab.dataset.view === viewName);
  for (const view of elements.views) view.hidden = view.id !== `${viewName}-view`;
  if (viewName === "cx-foundation" && state.cxFoundation) {
    const carried = state.cxFoundation.profiles?.some((profile) => profile.name === state.activeProfileName);
    if (carried) {
      state.cxSelectedProfile = state.activeProfileName;
      elements.cxProfileSelect.value = state.activeProfileName;
    }
    refreshCxFoundationFit();
  }
  if (viewName === "deleted-cards") loadDeletedCards();
  if (viewName === "review-build") renderReviewBuild();
  if (viewName === "today") renderTodayWorkflow();
  if (viewName === "finish-day" && !state.finishDayBusy) refreshFinishDay();
  if (viewName === "branch-integration" && !state.branchIntegrationBusy) refreshBranchIntegration();
  if (viewName === "cleanup-review" && !state.cleanupBusy) refreshCleanupReview();
  if (viewName === "release-publish" && !state.publicationBusy) refreshPublication();
  window.scrollTo({ top: 0, behavior: "auto" });
  requestAnimationFrame(updateFloatingReturn);
}

function setWorkflowStep(step) {
  for (const item of elements.workflowSteps) {
    const itemStep = Number(item.dataset.step);
    item.classList.toggle("is-active", itemStep === step);
    item.classList.toggle("is-complete", itemStep < step);
  }
}

function setProfilePane(pane) {
  const preview = pane === "preview";
  elements.profileWorkspace.classList.toggle("show-preview", preview);
  for (const tab of elements.mobilePaneTabs) {
    tab.classList.toggle("is-active", tab.dataset.pane === pane);
  }
}

function markPreviewStale() {
  if (!state.previewLoaded) {
    elements.previewStatus.textContent = "Preview not rendered";
    elements.previewPanel.classList.remove("is-stale");
    return;
  }
  elements.previewStatus.textContent = "Settings changed · refresh preview";
  elements.previewPanel.classList.add("is-stale");
}

function profileDraftKey(detail = state.detail) {
  if (!detail?.editableDraft) return null;
  if (detail.operation === "update") return `profile:${detail.name}`;
  if (!detail.sessionDraftId) detail.sessionDraftId = `draft:${state.nextDraftId++}`;
  return detail.sessionDraftId;
}

function profilePayloadChanged(payload, detail = state.detail) {
  if (!detail?.editableDraft) return false;
  if ((detail.operation || "update") !== "update") return true;
  return payload.title !== (detail.title || "")
    || payload.subtitle !== (detail.subtitle || "")
    || payload.status !== (detail.metadata?.status || "Draft")
    || payload.displayCategory !== (detail.displayCategory || "subject")
    || payload.release !== Boolean(detail.metadata?.release)
    || !equal(payload.overrides, detail.originalOverrides || {})
    || !equal(payload.lensChoices, detail.lensChoices || []);
}

function captureCurrentProfileDraft() {
  if (!state.detail?.editableDraft || !state.currentDraftKey) return;
  const payload = profileDraftPayload();
  if (!profilePayloadChanged(payload)) {
    state.profileDrafts.delete(state.currentDraftKey);
  } else {
    state.profileDrafts.set(state.currentDraftKey, {
      key: state.currentDraftKey,
      label: payload.title || payload.targetName || "Untitled profile",
      detail: clone(state.detail),
      payload: clone(payload),
    });
  }
  invalidateBuildReadiness();
  renderSessionStatus();
  updateCameraLabAction();
}

function updateCameraLabAction() {
  const savedProfile = state.detail?.cardType === "profile" && (state.detail.operation || "update") === "update";
  const changed = savedProfile && profilePayloadChanged(profileDraftPayload());
  elements.openCameraLab.disabled = !savedProfile || changed;
  elements.sidebarCameraLab.disabled = !savedProfile || changed;
  elements.openCameraLab.title = changed
    ? "Save or discard this profile draft before opening Camera Lab."
    : savedProfile ? `Open the saved ${state.detail.name} profile in Camera Lab.` : "Select a saved Subject/Profile Card first.";
  elements.sidebarCameraLab.title = elements.openCameraLab.title;
  renderTodayWorkflow();
}

async function openCurrentProfileInCameraLab() {
  captureCurrentProfileDraft();
  updateCameraLabAction();
  if (elements.openCameraLab.disabled) {
    showMessage("Save or discard the current profile draft before opening Camera Lab.", true);
    return;
  }
  elements.openCameraLab.disabled = true;
  const statusMessage = state.activeView === "today" ? showTodayMessage : showMessage;
  statusMessage(`Opening the saved ${state.detail.name} profile in Camera Lab…`);
  try {
    const result = await request("/api/camera-lab-launch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile: state.detail.name }),
    });
    statusMessage(result.reused
      ? `Camera Lab was already running and opened ${state.detail.name}.`
      : `Camera Lab started independently with ${state.detail.name} selected.`);
  } catch (error) {
    statusMessage(error.message, true);
  } finally {
    updateCameraLabAction();
  }
}

async function stopProfileEditor() {
  captureCurrentProfileDraft();
  const pending = pendingSessionItems().length;
  const warning = pending
    ? `Stop Profile Editor? ${pending} unsaved browser draft${pending === 1 ? "" : "s"} will be lost.`
    : "Stop Profile Editor and its local server?";
  if (!window.confirm(warning)) return;
  elements.stopProfileEditor.disabled = true;
  try {
    await request("/api/editor-shutdown", { method: "POST", body: "{}" });
    document.querySelectorAll("button, select, input").forEach((control) => { control.disabled = true; });
    showMessage("Profile Editor stopped cleanly. Camera Lab, if running, remains independent. You may close this tab.");
    window.setTimeout(() => window.close(), 300);
  } catch (error) {
    elements.stopProfileEditor.disabled = false;
    showMessage(`Profile Editor could not stop cleanly: ${error.message}`, true);
  }
}

function normalizedMyMenuDraft(menus = state.myMenus) {
  return menus
    .map((tab) => ({
      name: tab.name.trim(),
      colorChoice: tab.colorChoice || "",
      items: tab.items.filter(Boolean),
    }))
    .filter((tab) => tab.name || tab.items.length);
}

function savedMyMenuDraft() {
  const assignments = state.dictionary?.myMenu?.colors?.assignments || {};
  return (state.dictionary?.myMenu?.saved_tabs || []).map((tab) => ({
    name: tab.name,
    colorChoice: assignments[tab.name] || "",
    items: [...tab.items],
  }));
}

function hasMyMenuDraftChanges() {
  return Boolean(state.dictionary) && !equal(normalizedMyMenuDraft(), savedMyMenuDraft());
}

function pendingSessionItems() {
  const items = [...state.profileDrafts.values()].map((draft) => ({
    type: "profile",
    key: draft.key,
    label: draft.label,
    detail: "Unsaved profile draft",
  }));
  if (hasMyMenuDraftChanges()) items.push({ type: "my-menu", key: "my-menu", label: "My Menu", detail: "Unsaved tab, shortcut, or color changes" });
  if (hasCxAssignmentChanges()) items.push({ type: "cx-foundation", key: "cx-assignments", label: "Cx assignments", detail: "Unsaved C1-C3 profile assignments" });
  for (const [profile, start] of state.cxSelectionDrafts) {
    const item = state.cxFoundation?.profiles?.find((candidate) => candidate.name === profile);
    items.push({
      type: "cx-foundation",
      key: `cx-selection:${profile}`,
      profile,
      label: `${item?.title || profile} foundation`,
      detail: `Unsaved card foundation selection: ${start || "No Cx"}`,
    });
  }
  const baselineChanges = baselineChangedPaths();
  if (baselineChanges.length) {
    items.push({
      type: "baseline",
      key: "baseline",
      label: "Baseline Setup",
      detail: `${baselineChanges.length} proposed ${baselineChanges.length === 1 ? "setting" : "settings"}${state.baselinePlan?.complete ? " · migration plan complete" : " · analysis or plan required"}`,
    });
  }
  return items;
}

function invalidateBuildReadiness() {
  state.buildReadiness = null;
  elements.runLocalBuild.disabled = true;
}

function setBadge(element, count) {
  element.textContent = String(count);
  element.hidden = count === 0;
}

function renderSessionStatus() {
  const profileCount = state.profileDrafts.size;
  const menuCount = hasMyMenuDraftChanges() ? 1 : 0;
  const baselineCount = baselineChangedPaths().length ? 1 : 0;
  const cxCount = Number(hasCxAssignmentChanges()) + state.cxSelectionDrafts.size;
  setBadge(elements.profileDraftBadge, profileCount);
  setBadge(elements.myMenuDraftBadge, menuCount);
  setBadge(elements.baselineDraftBadge, baselineCount);
  setBadge(elements.cxFoundationDraftBadge, cxCount);
  setBadge(elements.pendingDraftBadge, profileCount + menuCount + baselineCount + cxCount);
  if (!document.querySelector("#review-build-view")?.hidden) renderReviewBuild();
  renderTodayWorkflow();
}

function showReviewBuildMessage(text, error = false) {
  elements.reviewBuildMessage.textContent = text;
  elements.reviewBuildMessage.classList.toggle("error", error);
  elements.reviewBuildMessage.hidden = !text;
}

function sessionSummaryCard(value, label) {
  const card = document.createElement("div");
  const strong = document.createElement("strong");
  const span = document.createElement("span");
  strong.textContent = String(value);
  span.textContent = label;
  card.append(strong, span);
  return card;
}

function renderReviewBuild() {
  const items = pendingSessionItems();
  const profileCount = items.filter((item) => item.type === "profile").length;
  elements.sessionSummary.replaceChildren(
    sessionSummaryCard(profileCount, profileCount === 1 ? "profile draft" : "profile drafts"),
    sessionSummaryCard(items.filter((item) => item.type === "cx-foundation").length, "Cx Foundation drafts"),
    sessionSummaryCard(items.some((item) => item.type === "my-menu") ? 1 : 0, "My Menu draft"),
    sessionSummaryCard(items.some((item) => item.type === "baseline") ? 1 : 0, "baseline draft"),
    sessionSummaryCard(state.buildReadiness?.ready ? "Ready" : "Locked", "local build"),
  );
  elements.pendingChangeCount.textContent = `${items.length} ${items.length === 1 ? "change" : "changes"}`;
  elements.pendingChangeList.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "pending-empty";
    empty.textContent = "No unsaved browser changes. Run a fresh readiness check before building.";
    elements.pendingChangeList.append(empty);
  }
  for (const item of items) {
    const row = document.createElement("article");
    row.className = "pending-change-item";
    const copy = document.createElement("div");
    const title = document.createElement("h3");
    const detail = document.createElement("p");
    title.textContent = item.label;
    detail.textContent = item.detail;
    copy.append(title, detail);
    const actions = document.createElement("div");
    actions.className = "pending-change-actions";
    const open = document.createElement("button");
    open.type = "button";
    open.className = "secondary";
    open.textContent = "Open draft";
    open.addEventListener("click", () => openPendingItem(item));
    const discard = document.createElement("button");
    discard.type = "button";
    discard.className = "secondary danger-action";
    discard.textContent = "Discard";
    discard.addEventListener("click", () => discardPendingItem(item));
    actions.append(open, discard);
    row.append(copy, actions);
    elements.pendingChangeList.append(row);
  }
  elements.runLocalBuild.disabled = !(state.buildReadiness?.ready && items.length === 0);
}

async function openPendingItem(item) {
  if (item.type === "cx-foundation") {
    switchView("cx-foundation");
    if (item.profile) {
      state.cxSelectedProfile = item.profile;
      elements.cxProfileSelect.value = item.profile;
      await refreshCxFoundationFit();
    }
    return;
  }
  if (item.type === "my-menu") {
    switchView("my-menu");
    return;
  }
  if (item.type === "baseline") {
    switchView("baseline");
    return;
  }
  const record = state.profileDrafts.get(item.key);
  if (!record) return;
  switchView("profiles");
  if (record.detail.operation === "update") {
    await loadProfile(record.detail.name);
  } else {
    applyProfileDetail(clone(record.detail), record);
    elements.profileSelect.value = "";
  }
}

async function discardPendingItem(item) {
  if (!window.confirm(`Discard ${item.label}? These unsaved browser changes cannot be recovered.`)) return;
  if (item.type === "my-menu") {
    loadSavedMenus(true);
  } else if (item.type === "cx-foundation") {
    if (item.key === "cx-assignments") state.cxAssignments = clone(state.cxFoundation.assignments);
    if (item.profile) state.cxSelectionDrafts.delete(item.profile);
    state.cxReviewToken = null;
    await refreshCxFoundationFit();
  } else if (item.type === "baseline") {
    discardBaselineDraft();
  } else {
    state.profileDrafts.delete(item.key);
    if (state.currentDraftKey === item.key) {
      const detail = state.detail;
      state.currentDraftKey = null;
      state.detail = null;
      if (detail.operation === "update") await loadProfile(detail.name);
      else await loadProfile(detail.sourceProfile || elements.profileSelect.options[0]?.value);
    }
    invalidateBuildReadiness();
    renderSessionStatus();
  }
  showReviewBuildMessage(`${item.label} discarded. No source file was changed.`);
}

async function validateBuildReadiness() {
  captureCurrentProfileDraft();
  elements.validateReadiness.disabled = true;
  showReviewBuildMessage("Checking browser drafts and validating canonical source…");
  try {
    const readiness = await request("/api/build-readiness", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length }),
    });
    state.buildReadiness = readiness;
    elements.localBuildOutput.hidden = false;
    const refreshDetails = readiness.derivedArtifacts?.refreshNeeded
      ? `\n\nSpreadsheet refresh will run automatically:\n${readiness.derivedArtifacts.details.join("\n")}`
      : "\n\nSpreadsheet-derived artifacts are current; no workbook refresh is needed.";
    elements.localBuildOutput.textContent = readiness.ready
      ? `Readiness passed. No pending browser drafts and source validation passed.${refreshDetails}`
      : readiness.blockers.join("\n");
    showReviewBuildMessage(
      readiness.ready ? "Readiness passed. Review the confirmation before running the local build." : "Build remains locked. Resolve the items below and validate again.",
      !readiness.ready,
    );
  } catch (error) {
    state.buildReadiness = null;
    showReviewBuildMessage(error.message, true);
  } finally {
    elements.validateReadiness.disabled = false;
    renderReviewBuild();
  }
}

async function importVerificationTracker() {
  captureCurrentProfileDraft();
  const pending = pendingSessionItems().length;
  if (pending) {
    showReviewBuildMessage(`Resolve ${pending} pending browser ${pending === 1 ? "change" : "changes"} before importing the verification tracker.`, true);
    return;
  }
  if (!window.confirm("Import the most recently modified local verification tracker into canonical project status? Save and close Numbers or Excel first.")) return;
  elements.importVerificationTracker.disabled = true;
  elements.localBuildOutput.hidden = false;
  elements.localBuildOutput.textContent = "Importing verification tracker…";
  showReviewBuildMessage("Importing the most recently modified local verification tracker. Keep this page open.");
  try {
    const result = await request("/api/verification-tracker-import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: 0, confirmImport: true }),
    });
    state.buildReadiness = null;
    elements.localBuildOutput.textContent = result.output || "Verification tracker import completed.";
    showReviewBuildMessage("Verification tracker imported. Run a fresh readiness check before building.");
  } catch (error) {
    state.buildReadiness = null;
    elements.localBuildOutput.textContent += `\n\nFAILED\n${error.message}`;
    showReviewBuildMessage(error.message, true);
  } finally {
    elements.importVerificationTracker.disabled = false;
    renderReviewBuild();
  }
}

async function runLocalBuild() {
  elements.buildConfirmRun.disabled = true;
  elements.runLocalBuild.disabled = true;
  elements.buildConfirmDialog.close();
  elements.localBuildOutput.hidden = false;
  elements.localBuildOutput.textContent = "Running source validation, any required spreadsheet refresh, local build, and full validation…";
  showReviewBuildMessage("Local build is running. Keep this page open.");
  try {
    const result = await request("/api/local-build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pendingChanges: pendingSessionItems().length, confirmLocalBuild: true }),
    });
    elements.localBuildOutput.textContent = result.steps
      .map((step) => `${step.label} — ${step.status}\n${step.output || "(no output)"}`)
      .join("\n\n");
    state.buildReadiness = null;
    showReviewBuildMessage("Spreadsheet readiness, local build, and full validation passed. Git and publishing were not run.");
  } catch (error) {
    state.buildReadiness = null;
    elements.localBuildOutput.textContent += `\n\nFAILED\n${error.message}`;
    showReviewBuildMessage(error.message, true);
  } finally {
    elements.buildConfirmRun.disabled = false;
    renderReviewBuild();
  }
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
  const selectedColors = new Set(
    state.myMenus.filter((tab) => tab.name.trim()).map((tab) => tab.colorChoice).filter(Boolean),
  );
  const palette = state.dictionary.myMenu.colors?.palette || {};
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
    name.addEventListener("change", () => {
      const usedByOtherNamedTabs = new Set(
        state.myMenus
          .filter((candidate) => candidate !== tab && candidate.name.trim())
          .map((candidate) => candidate.colorChoice),
      );
      if (tab.name.trim() && usedByOtherNamedTabs.has(tab.colorChoice)) {
        tab.colorChoice = Object.keys(palette).find((choice) => !usedByOtherNamedTabs.has(choice)) || tab.colorChoice;
      }
      renderMyMenus();
    });
    const color = fragment.querySelector(".my-menu-color");
    const swatch = fragment.querySelector(".my-menu-color-swatch");
    for (const [choice, hex] of Object.entries(palette)) {
      const option = document.createElement("option");
      option.value = choice;
      option.textContent = choice;
      option.selected = choice === tab.colorChoice;
      option.disabled = selectedColors.has(choice) && choice !== tab.colorChoice;
      color.append(option);
      if (choice === tab.colorChoice) swatch.style.backgroundColor = hex;
    }
    color.addEventListener("change", () => {
      tab.colorChoice = color.value;
      myMenuDraftChanged();
      renderMyMenus();
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

function loadMenus(tabs, invalidateAnalysis = true) {
  const colorConfig = state.dictionary?.myMenu?.colors || {};
  const paletteChoices = Object.keys(colorConfig.palette || {});
  const assignments = colorConfig.assignments || {};
  state.myMenus = Array.from({ length: 5 }, (_unused, index) => ({
    name: "",
    colorChoice: paletteChoices[index] || paletteChoices[0] || "",
    items: Array(6).fill(""),
  }));
  (tabs || []).slice(0, 5).forEach((tab, index) => {
    state.myMenus[index].name = tab.name;
    state.myMenus[index].colorChoice = assignments[tab.name] || state.myMenus[index].colorChoice;
    tab.items.slice(0, 6).forEach((itemId, itemIndex) => { state.myMenus[index].items[itemIndex] = itemId; });
  });
  if (invalidateAnalysis) myMenuDraftChanged();
  renderMyMenus();
  renderDictionary();
}

function loadSavedMenus(invalidateAnalysis = true) {
  loadMenus(state.dictionary?.myMenu?.saved_tabs || [], invalidateAnalysis);
  if (invalidateAnalysis) showMyMenuColorMessage("Saved My Menu layout reloaded. Nothing was written.");
}

function loadRecommendedMenus(invalidateAnalysis = true) {
  loadMenus(state.dictionary?.myMenu?.recommended_tabs || [], invalidateAnalysis);
  if (invalidateAnalysis) showMyMenuColorMessage("Recommended tabs restored as a draft. Review to save them.");
}

function myMenuDraftChanged() {
  state.myMenuColorReviewToken = null;
  invalidateBuildReadiness();
  renderSessionStatus();
  if (elements.myMenuColorReviewDialog.open) elements.myMenuColorReviewDialog.close();
  if (!state.baselineAnalysis) return;
  baselineDraftChanged();
  updateBaselineDraftState();
}

function myMenuColorAssignments() {
  const assignments = {};
  for (const tab of state.myMenus) {
    const name = tab.name.trim();
    if (name) assignments[name] = tab.colorChoice;
  }
  return assignments;
}

async function reviewMyMenuColors() {
  elements.reviewMyMenuColors.disabled = true;
  showMyMenuColorMessage("Validating the saved tab layout, item order, and colors…");
  try {
    const review = await request("/api/my-menu-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tabs: state.myMenus }),
    });
    state.myMenuColorReviewToken = review.reviewToken;
    elements.myMenuColorReviewSummary.textContent = review.summary;
    elements.myMenuColorReviewDiff.textContent = review.diff;
    elements.myMenuColorReviewDialog.showModal();
    showMyMenuColorMessage("My Menu candidate validation passed. Review the exact YAML before saving.");
  } catch (error) {
    showMyMenuColorMessage(error.message, true);
  } finally {
    elements.reviewMyMenuColors.disabled = false;
  }
}

async function saveMyMenuColors() {
  if (!state.myMenuColorReviewToken) {
    showMyMenuColorMessage("This My Menu review is no longer current. Review the layout again.", true);
    elements.myMenuColorReviewDialog.close();
    return;
  }
  elements.saveMyMenuColors.disabled = true;
  showMyMenuColorMessage("Creating a recovery backup and validating the reviewed My Menu layout…");
  try {
    const result = await request("/api/my-menu-saves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.myMenuColorReviewToken }),
    });
    state.myMenuColorReviewToken = null;
    elements.myMenuColorReviewDialog.close();
    state.dictionary.myMenu.saved_tabs = clone(result.tabs);
    state.dictionary.myMenu.colors = {
      sourceFile: "00 Master/my_menu_colors.yaml",
      palette: result.colors.palette,
      assignments: result.colors.assignments,
    };
    for (const tab of state.myMenus) {
      tab.colorChoice = result.colors.assignments[tab.name.trim()] || tab.colorChoice;
    }
    renderMyMenus();
    invalidateBuildReadiness();
    renderSessionStatus();
    showMyMenuColorMessage(`Saved the My Menu layout and refreshed its reference-card source. Validation passed. Recovery backup: ${result.backup}`);
  } catch (error) {
    state.myMenuColorReviewToken = null;
    elements.myMenuColorReviewDialog.close();
    showMyMenuColorMessage(error.message, true);
  } finally {
    elements.saveMyMenuColors.disabled = false;
  }
}

async function loadProfile(name) {
  captureCurrentProfileDraft();
  const loadSequence = ++state.loadSequence;
  showMessage("");
  elements.profileSelect.disabled = true;
  elements.reloadButton.disabled = true;
  elements.previewButton.disabled = true;
  try {
    const detail = await request(`/api/profiles/${encodeURIComponent(name)}`);
    if (loadSequence !== state.loadSequence) return;
    state.activeProfileName = name;
    elements.profileSelect.value = name;
    applyProfileDetail(detail, state.profileDrafts.get(`profile:${name}`));
  } catch (error) {
    if (loadSequence !== state.loadSequence) return;
    showMessage(error.message, true);
  } finally {
    if (loadSequence === state.loadSequence) elements.profileSelect.disabled = false;
  }
}

async function loadProfileDraft(operation) {
  captureCurrentProfileDraft();
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

function applyProfileDetail(detail, restoredDraft = null) {
  state.detail = detail;
  if ((detail.operation || "update") === "update") state.activeProfileName = detail.name;
  state.currentDraftKey = profileDraftKey(detail);
  state.originalOverrides = clone(detail.originalOverrides || {});
  state.draftOverrides = clone(restoredDraft?.payload?.overrides || state.originalOverrides);
  state.originalLensChoices = clone(detail.lensChoices || []);
  state.draftLensChoices = clone(restoredDraft?.payload?.lensChoices || state.originalLensChoices);
  state.reviewToken = null;
  state.discardReviewToken = null;
  elements.profileTitle.textContent = restoredDraft?.payload?.title || detail.title;
  elements.sourceFile.textContent = detail.sourceFile;
  elements.titleInput.value = restoredDraft?.payload?.title ?? detail.title ?? "";
  elements.subtitleInput.value = restoredDraft?.payload?.subtitle ?? detail.subtitle ?? "";
  elements.filenameInput.value = restoredDraft?.payload?.targetName ?? detail.targetName ?? detail.name ?? "";
  state.filenameFollowsTitle = detail.operation === "create"
    && (!restoredDraft || elements.filenameInput.value === profileFilenameFromTitle(elements.titleInput.value));
  elements.statusInput.value = restoredDraft?.payload?.status ?? detail.metadata?.status ?? "Draft";
  elements.displayCategoryInput.value = restoredDraft?.payload?.displayCategory ?? detail.displayCategory ?? "subject";
  elements.releaseInput.checked = restoredDraft?.payload?.release ?? Boolean(detail.metadata?.release);
  state.previewLoaded = false;
  elements.previewFrame.hidden = true;
  elements.previewFrame.removeAttribute("src");
  elements.previewEmpty.hidden = false;
  elements.previewPath.textContent = "";
  elements.previewStatus.textContent = "Preview not rendered";
  elements.previewPanel.classList.remove("is-stale");
  elements.previewChangeNote.hidden = !detail.editableDraft;
  setProfilePane("settings");
  setWorkflowStep(detail.editableDraft ? 2 : 1);
  if (elements.reviewDialog.open) elements.reviewDialog.close();
  if (elements.discardProfileDialog.open) elements.discardProfileDialog.close();
  render();
  renderSessionStatus();
}

function disableProfileActions(disabled) {
  elements.newButton.disabled = disabled;
  elements.duplicateButton.disabled = disabled || !state.detail?.editableDraft;
  elements.reloadButton.disabled = disabled || !state.detail?.editableDraft;
  elements.previewButton.disabled = disabled || !state.detail;
  elements.reviewButton.disabled = disabled || !state.detail?.editableDraft;
  updateDiscardProfileAction();
  if (disabled) elements.discardProfileButton.disabled = true;
}

function render() {
  elements.settings.replaceChildren();
  elements.cardSettings.replaceChildren();
  elements.referenceCard.hidden = true;
  elements.lensGuidanceGroup.hidden = true;
  const editable = state.detail?.editableDraft;
  elements.profileMetadata.hidden = !editable;
  elements.cardSettingsGroup.hidden = !editable;
  elements.additionalSettingsGroup.hidden = !editable;
  elements.profileSaveBar.hidden = !editable;
  elements.duplicateButton.disabled = !editable;
  elements.reloadButton.disabled = !editable;
  elements.previewButton.disabled = !state.detail;
  elements.previewButton.textContent = state.previewLoaded
    ? "Refresh preview"
    : editable ? "Render preview" : "Render reference preview";
  elements.reviewButton.disabled = !editable;
  updateDiscardProfileAction();
  updateCameraLabAction();
  if (!editable) {
    renderReference();
    elements.customCount.textContent = "0";
    elements.inheritedCount.textContent = "0";
    showMessage("This reference card remains read-only. Preview it here; edit My Menu through Configure My Menu.");
    return;
  }
  renderMetadataState();
  showMessage("");
  renderLensChoices();
  renderProfileSettings();
  updateCounts();
}

function renderProfileSettings() {
  const byPath = new Map();
  for (const section of state.detail.sections) {
    for (const setting of section.settings) byPath.set(setting.path, setting);
  }
  const orderedPaths = state.detail.settingOrder || [...byPath.keys()];
  const cardPaths = (state.detail.cardSettingPaths || []).filter((path) => byPath.has(path));
  const cardPathSet = new Set(cardPaths);
  const cardSettings = cardPaths.map((path) => byPath.get(path));
  if (cardSettings.length) {
    renderSection({ label: "Shown on this card", settings: cardSettings }, elements.cardSettings, true);
  }
  elements.cardSettingsCount.textContent = `${cardSettings.length} ${cardSettings.length === 1 ? "control" : "controls"}`;

  let additionalCount = 0;
  for (const section of state.detail.sections) {
    const settings = orderedPaths
      .filter((path) => !cardPathSet.has(path))
      .map((path) => byPath.get(path))
      .filter((setting) => setting && setting.path.split(".", 1)[0] === section.key);
    if (!settings.length) continue;
    additionalCount += settings.length;
    renderSection({ ...section, settings }, elements.settings);
  }
  elements.additionalSettingsCount.textContent = `${additionalCount} ${additionalCount === 1 ? "control" : "controls"}`;
}

function renderLensChoices() {
  const visible = Boolean(state.detail?.editableDraft)
    && elements.displayCategoryInput.value === "subject";
  elements.lensGuidanceGroup.hidden = !visible;
  elements.lensChoiceList.replaceChildren();
  if (!visible) return;
  const catalog = state.detail.lensCatalog || [];
  elements.lensChoiceCount.textContent = `${state.draftLensChoices.length} of 3`;
  elements.addLensChoice.disabled = state.draftLensChoices.length >= 3 || catalog.length === 0;
  if (!state.draftLensChoices.length) {
    const empty = document.createElement("p");
    empty.className = "lens-choice-empty";
    empty.textContent = "Add at least one lens. The first choice becomes primary.";
    elements.lensChoiceList.append(empty);
    return;
  }
  state.draftLensChoices.forEach((choice, index) => {
    const row = document.createElement("div");
    row.className = `lens-choice-editor-row${choice.role === "primary" ? " is-primary" : ""}`;

    const lensLabel = document.createElement("label");
    lensLabel.innerHTML = "<span>Lens</span>";
    const lensSelect = document.createElement("select");
    for (const lens of catalog) {
      const option = document.createElement("option");
      option.value = lens.id;
      option.textContent = lens.name;
      option.selected = lens.id === choice.lensId;
      lensSelect.append(option);
    }
    lensSelect.addEventListener("change", () => {
      choice.lensId = lensSelect.value;
      const compatible = catalog.find((lens) => lens.id === choice.lensId)?.accessories || [];
      if (!compatible.some((accessory) => accessory.id === choice.accessoryId)) choice.accessoryId = "";
      lensDraftChanged(true);
    });
    lensLabel.append(lensSelect);

    const accessoryLabel = document.createElement("label");
    accessoryLabel.innerHTML = "<span>Accessory</span>";
    const accessorySelect = document.createElement("select");
    const noAccessory = document.createElement("option");
    noAccessory.value = "";
    noAccessory.textContent = "None";
    accessorySelect.append(noAccessory);
    const accessories = catalog.find((lens) => lens.id === choice.lensId)?.accessories || [];
    for (const accessory of accessories) {
      const option = document.createElement("option");
      option.value = accessory.id;
      option.textContent = accessory.name;
      option.selected = accessory.id === choice.accessoryId;
      accessorySelect.append(option);
    }
    accessorySelect.disabled = accessories.length === 0;
    accessorySelect.value = choice.accessoryId || "";
    accessorySelect.addEventListener("change", () => {
      choice.accessoryId = accessorySelect.value;
      lensDraftChanged(true);
    });
    accessoryLabel.append(accessorySelect);

    const roleLabel = document.createElement("label");
    roleLabel.innerHTML = "<span>Role</span>";
    const roleSelect = document.createElement("select");
    for (const [value, label] of [["primary", "Primary"], ["alternative", "Alternative"], ["specialist", "Specialist"]]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      option.selected = value === choice.role;
      roleSelect.append(option);
    }
    roleSelect.addEventListener("change", () => {
      const wasPrimary = choice.role === "primary";
      choice.role = roleSelect.value;
      if (choice.role === "primary") {
        state.draftLensChoices.forEach((item, itemIndex) => {
          if (itemIndex !== index && item.role === "primary") item.role = "alternative";
        });
      } else if (wasPrimary) {
        const replacement = state.draftLensChoices.find((_item, itemIndex) => itemIndex !== index);
        if (replacement) replacement.role = "primary";
        else choice.role = "primary";
      }
      lensDraftChanged(true);
    });
    roleLabel.append(roleSelect);

    const order = document.createElement("div");
    order.className = "lens-choice-order";
    const up = document.createElement("button");
    up.type = "button";
    up.className = "secondary";
    up.textContent = "↑";
    up.title = "Move lens choice earlier";
    up.disabled = index === 0;
    up.addEventListener("click", () => moveLensChoice(index, index - 1));
    const down = document.createElement("button");
    down.type = "button";
    down.className = "secondary";
    down.textContent = "↓";
    down.title = "Move lens choice later";
    down.disabled = index === state.draftLensChoices.length - 1;
    down.addEventListener("click", () => moveLensChoice(index, index + 1));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "secondary danger-action";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => removeLensChoice(index));
    order.append(up, down, remove);

    const copy = document.createElement("div");
    copy.className = "lens-choice-copy";
    const whenLabel = document.createElement("label");
    whenLabel.innerHTML = "<span>When to use</span>";
    const whenInput = document.createElement("input");
    whenInput.type = "text";
    whenInput.maxLength = 240;
    whenInput.value = choice.useWhen || "";
    whenInput.addEventListener("input", () => {
      choice.useWhen = whenInput.value;
      lensDraftChanged(false);
    });
    whenLabel.append(whenInput);
    const checkLabel = document.createElement("label");
    checkLabel.innerHTML = "<span>Field check</span>";
    const checkInput = document.createElement("input");
    checkInput.type = "text";
    checkInput.maxLength = 240;
    checkInput.value = choice.fieldCheck || "";
    checkInput.addEventListener("input", () => {
      choice.fieldCheck = checkInput.value;
      lensDraftChanged(false);
    });
    checkLabel.append(checkInput);
    copy.append(whenLabel, checkLabel);

    row.append(lensLabel, accessoryLabel, roleLabel, order, copy);
    elements.lensChoiceList.append(row);
  });
}

function lensDraftChanged(rerender) {
  draftChanged();
  if (rerender) renderLensChoices();
}

function moveLensChoice(from, to) {
  if (to < 0 || to >= state.draftLensChoices.length) return;
  const [choice] = state.draftLensChoices.splice(from, 1);
  state.draftLensChoices.splice(to, 0, choice);
  lensDraftChanged(true);
}

function removeLensChoice(index) {
  const [removed] = state.draftLensChoices.splice(index, 1);
  if (removed?.role === "primary" && state.draftLensChoices.length) {
    state.draftLensChoices[0].role = "primary";
  }
  lensDraftChanged(true);
}

function addLensChoice() {
  if (state.draftLensChoices.length >= 3) return;
  const catalog = state.detail?.lensCatalog || [];
  const used = new Set(state.draftLensChoices.map((choice) => `${choice.lensId}:${choice.accessoryId || ""}`));
  const lens = catalog.find((item) => !used.has(`${item.id}:`)) || catalog[0];
  if (!lens) return;
  state.draftLensChoices.push({
    lensId: lens.id,
    accessoryId: "",
    role: state.draftLensChoices.length ? "alternative" : "primary",
    useWhen: "",
    fieldCheck: "",
  });
  lensDraftChanged(true);
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
  elements.displayCategoryInput.disabled = false;
  elements.releaseInput.disabled = creating;
  elements.profileTitle.textContent = elements.titleInput.value.trim() || "Untitled profile";
  elements.sourceFile.textContent = operation === "update"
    ? `10 Profiles/${state.detail.name}.yaml`
    : `Proposed: 10 Profiles/${elements.filenameInput.value.trim() || "Untitled"}.yaml`;
  updateDiscardProfileAction();
}

function updateDiscardProfileAction() {
  const saved = Boolean(state.detail && (state.detail.operation || "update") === "update");
  elements.discardProfileButton.hidden = !saved;
  elements.profileRemovalReason.hidden = true;
  elements.profileRemovalReason.textContent = "";
  if (!saved) return;
  let blocker = "";
  if (!state.detail.editableDraft || state.detail.cardType === "reference") {
    blocker = "Permanent reference cards cannot be moved to Deleted Cards.";
  } else if (state.detail.metadata?.release) {
    blocker = "Uncheck Include in released card bundle, then review and save that change first.";
  } else {
    blocker = profileDiscardBrowserBlocker() || (state.detail.discardBlockers || []).join("; ");
  }
  elements.discardProfileButton.disabled = Boolean(blocker);
  elements.discardProfileButton.title = blocker;
  elements.profileRemovalReason.textContent = blocker;
  elements.profileRemovalReason.hidden = !blocker;
}

function profileDiscardBrowserBlocker() {
  if (profilePayloadChanged(profileDraftPayload())) {
    return "Review and save the current profile edits, or restore the saved profile, before moving this card.";
  }
  if (state.cxSelectionDrafts.has(state.detail.name)) {
    return "Save or discard this card's Cx Foundation draft before removing it.";
  }
  if (hasCxAssignmentChanges() && Object.values(state.cxAssignments).includes(state.detail.title)) {
    return "Save or discard the pending C1-C3 assignment changes before removing this card.";
  }
  return "";
}

function renderReference() {
  const intro = document.createElement("p");
  intro.textContent = state.detail.name === "My Menu"
    ? "Saved My Menu field reference"
    : "Reference-card assignments";
  const table = document.createElement("table");
  const body = document.createElement("tbody");
  for (const item of state.detail.referenceSettings || []) {
    const row = document.createElement("tr");
    const control = document.createElement("th");
    const assignment = document.createElement("td");
    if (item.rowType === "section") {
      row.className = "reference-section";
      control.colSpan = 2;
      control.textContent = item.control;
      const name = document.createElement("strong");
      name.textContent = item.assignment;
      if (item.color) name.style.color = item.color;
      control.append(name);
      row.append(control);
      body.append(row);
      continue;
    }
    control.textContent = item.control;
    assignment.textContent = item.assignment;
    if (item.detail) {
      const detail = document.createElement("small");
      detail.textContent = item.detail;
      assignment.append(detail);
    }
    row.append(control, assignment);
    body.append(row);
  }
  table.append(body);
  elements.referenceCard.replaceChildren(intro, table);
  elements.referenceCard.hidden = false;
}

function renderSection(section, host = elements.settings, cardOrder = false) {
  const fragment = document.querySelector("#section-template").content.cloneNode(true);
  const container = fragment.querySelector(".setting-section");
  container.classList.toggle("card-order-section", cardOrder);
  fragment.querySelector("h2").textContent = section.label;
  fragment.querySelector(".reset-section").addEventListener("click", () => {
    for (const setting of section.settings) delete state.draftOverrides[setting.path];
    draftChanged();
    render();
  });
  const list = fragment.querySelector(".setting-list");
  for (const setting of section.settings) list.append(renderSetting(setting));
  host.append(container);
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
  if (control.tagName === "INPUT") {
    control.addEventListener("input", () => {
      const blanked = control.value === "";
      const value = readControl(control, setting);
      const recognizedSpellingChanged = typeof value === "string" && value !== control.value;
      updateSetting(setting, value, blanked || recognizedSpellingChanged);
    });
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
  state.migrationReviewToken = null;
  if (elements.migrationReviewDialog.open) elements.migrationReviewDialog.close();
  elements.baselineSummary.hidden = true;
  elements.baselineSummary.replaceChildren();
  elements.baselineDecisionTools.hidden = true;
  elements.baselineBuildPlanBottomRow.hidden = true;
  elements.baselineResults.replaceChildren();
  elements.baselinePlan.hidden = true;
  elements.baselinePlan.replaceChildren();
  invalidateBuildReadiness();
  renderSessionStatus();
}

function discardBaselineDraft() {
  state.baselineDraft = clone(state.baselineCurrent);
  state.baselineAnalysis = null;
  state.baselineDecisions = {};
  state.baselinePlan = null;
  state.migrationReviewToken = null;
  invalidateBuildReadiness();
  renderBaseline();
  renderSessionStatus();
  showBaselineMessage("Baseline draft discarded. Nothing was saved.");
}

function updateBaselineDraftState() {
  const changed = baselineChangedPaths().length;
  elements.baselineAnalyze.disabled = false;
  elements.baselineReset.disabled = changed === 0;
  if (changed === 0) {
    showBaselineMessage("No proposed baseline changes. Analyze the current My Menu layout and profile-card coverage at any time.");
  } else {
    showBaselineMessage(`${changed} proposed baseline ${changed === 1 ? "change" : "changes"}. Analyze the draft to review profile impact.`);
  }
}

async function analyzeBaselineDraft(fromMyMenu = false) {
  elements.baselineAnalyze.disabled = true;
  showBaselineMessage(fromMyMenu
    ? "Analyzing the current My Menu layout against every profile card…"
    : "Calculating effective values and My Menu coverage for every inheriting profile…");
  try {
    state.baselineAnalysis = await request("/api/baseline-impact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ values: state.baselineDraft, myMenuTabs: state.myMenus }),
    });
    state.baselineDecisions = {};
    state.baselinePlan = null;
    renderBaselineAnalysis();
    showBaselineMessage(fromMyMenu
      ? "My Menu profile-impact analysis complete. Nothing was saved."
      : "Impact analysis complete. Nothing was saved.");
    const target = fromMyMenu
      ? elements.baselineResults.querySelector(".my-menu-impact") || elements.baselineSummary
      : elements.baselineSummary;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    state.baselineAnalysis = null;
    state.baselineDecisions = {};
    state.baselinePlan = null;
    renderBaselineAnalysis();
    showBaselineMessage(error.message, true);
  } finally {
    elements.baselineAnalyze.disabled = false;
  }
}

async function analyzeMyMenuImpact() {
  if (!state.baselineDetail) {
    showMyMenuColorMessage("The baseline is still loading. Try the analysis again in a moment.", true);
    return;
  }
  elements.analyzeMyMenu.disabled = true;
  showMyMenuColorMessage("Opening the shared My Menu profile-impact report…");
  switchView("baseline");
  try {
    await analyzeBaselineDraft(true);
  } finally {
    elements.analyzeMyMenu.disabled = false;
  }
}

function updateFloatingReturn() {
  elements.returnToTop.hidden = window.scrollY < 280;
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
  summary.textContent = `${menuImpact.summary.profiles_with_warnings} profiles with warnings · ${menuImpact.summary.missing_card_cues} missing cues · ${menuImpact.summary.obsolete_card_cues} obsolete cues`;
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
      : "No Cx foundation · verify/set rows";
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
      } else if (setting.obsolete) {
        badges.append(myMenuFindingBadge(
          setting.reason === "tab_removed" ? "Tab removed from My Menu" : "Shortcut removed from tab",
          "missing",
        ));
      }
      item.append(copy, badges);
      declared.append(item);
    }
    body.append(declared);
  }

  if (profile.obsolete_card_cues.length) {
    body.append(myMenuFindingHeading("Card cues to remove"));
    const obsolete = document.createElement("ul");
    obsolete.className = "my-menu-setting-findings missing";
    for (const setting of profile.obsolete_card_cues) {
      const item = document.createElement("li");
      const copy = document.createElement("div");
      const label = document.createElement("strong");
      const route = document.createElement("small");
      const badge = myMenuFindingBadge("Planned removal", "missing");
      label.textContent = baselineSettingLabel(setting.path);
      route.textContent = setting.reason === "tab_removed"
        ? `${setting.tab} is no longer configured`
        : `${setting.tab} no longer contains this shortcut`;
      copy.append(label, route);
      item.append(copy, badge);
      obsolete.append(item);
    }
    body.append(obsolete);
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
    state.migrationReviewToken = null;
    if (elements.migrationReviewDialog.open) elements.migrationReviewDialog.close();
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
  title.textContent = "Migration plan";
  status.textContent = plan.complete ? "Complete" : "Needs decisions";
  status.className = plan.complete ? "plan-complete" : "plan-incomplete";
  heading.append(title, status);
  elements.baselinePlan.append(heading);

  if (plan.profile_card_cues_to_add.length || plan.profile_card_cues_to_remove.length) {
    const explanation = document.createElement("section");
    const explanationCopy = document.createElement("p");
    explanation.className = "baseline-plan-explanation";
    explanationCopy.textContent = "What these My Menu changes mean: New cues color-code settings already shown on cards for their configured tab. Obsolete cues are removed when their tab or shortcut is no longer in the My Menu draft. These changes do not add or remove settings from the cards or change the camera’s My Menu.";
    explanation.append(explanationCopy);
    elements.baselinePlan.append(explanation);
  }

  const groups = [
    ["Profiles following baseline", plan.profiles_following_baseline, (item) => `${item.title}: ${displayValue(item.previous_effective_value)} → ${displayValue(item.proposed_effective_value)}`],
    ["Overrides to add", plan.overrides_to_add, (item) => `${item.title}: preserve ${displayValue(item.override_value)} for ${item.path}`],
    ["Redundant overrides to remove", plan.overrides_to_remove, (item) => `${item.title}: remove ${item.path}`],
    ["Existing overrides retained", plan.overrides_to_keep, (item) => `${item.title}: keep ${item.path}`],
    ["Existing card rows to mark with My Menu access", plan.profile_card_cues_to_add, (item) => `${item.title}: color-code existing ${baselineSettingLabel(item.path)} row for ${item.tab} access`],
    ["Obsolete My Menu card cues to remove", plan.profile_card_cues_to_remove, (item) => `${item.title}: remove ${baselineSettingLabel(item.path)} cue for ${item.tab}`],
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
  const hasSourceChanges = baselineChangedPaths().length > 0
    || plan.overrides_to_add.length > 0
    || plan.overrides_to_remove.length > 0
    || plan.profile_card_cues_to_add.length > 0
    || plan.profile_card_cues_to_remove.length > 0;
  if (plan.complete && hasSourceChanges) {
    const applySection = document.createElement("section");
    applySection.className = "baseline-migration-apply";
    const applyTitle = document.createElement("h4");
    applyTitle.textContent = "Review and apply this migration";
    const warning = document.createElement("p");
    warning.textContent = baselineChangedPaths().length > 0
      ? "This writes the proposed baseline and planned profile cleanup/cues. C1–C3 registrations and unresolved My Menu identities remain unchanged as warnings."
      : "This profile-only migration adds missing My Menu card cues and removes obsolete ones without changing the baseline, C1–C3 registrations, or the saved My Menu layout.";
    const acknowledgements = document.createElement("div");
    acknowledgements.className = "migration-acknowledgements";
    const cxLabel = document.createElement("label");
    const cx = document.createElement("input");
    cx.type = "checkbox";
    cx.id = "acknowledge-cx-impact";
    cxLabel.append(cx, document.createTextNode(" I reviewed the C1–C3 effective-value and starting-mode warnings."));
    const menuLabel = document.createElement("label");
    const menu = document.createElement("input");
    menu.type = "checkbox";
    menu.id = "acknowledge-my-menu-impact";
    menuLabel.append(menu, document.createTextNode(" I reviewed the My Menu availability, missing-cue, obsolete-cue, and unused-route warnings."));
    acknowledgements.append(cxLabel, menuLabel);
    const reviewButton = document.createElement("button");
    reviewButton.type = "button";
    reviewButton.className = "save-action";
    reviewButton.textContent = "Review exact migration YAML";
    reviewButton.disabled = true;
    const update = () => { reviewButton.disabled = !(cx.checked && menu.checked); };
    cx.addEventListener("change", update);
    menu.addEventListener("change", update);
    reviewButton.addEventListener("click", () => reviewBaselineMigration(cx, menu, reviewButton));
    applySection.append(applyTitle, warning, acknowledgements, reviewButton);
    elements.baselinePlan.append(applySection);
  } else if (plan.complete) {
    const noChanges = document.createElement("p");
    noChanges.className = "baseline-plan-explanation";
    noChanges.textContent = "No baseline or profile source changes are needed for this configuration.";
    elements.baselinePlan.append(noChanges);
  }
  elements.baselinePlan.hidden = false;
}

async function reviewBaselineMigration(cxAcknowledgement, menuAcknowledgement, reviewButton) {
  reviewButton.disabled = true;
  showBaselineMessage("Validating every candidate source and preparing the exact multi-file diff…");
  try {
    const review = await request("/api/baseline-migration-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        values: state.baselineDraft,
        decisions: migrationDecisions(),
        myMenuTabs: state.myMenus,
        acknowledgeCxImpact: cxAcknowledgement.checked,
        acknowledgeMyMenuImpact: menuAcknowledgement.checked,
      }),
    });
    state.migrationReviewToken = review.reviewToken;
    elements.migrationReviewSummary.textContent = `${review.sourceFiles.length} source ${review.sourceFiles.length === 1 ? "file" : "files"}: ${review.sourceFiles.join(", ")}`;
    elements.migrationReviewDiff.textContent = review.diff;
    elements.migrationReviewDialog.showModal();
    showBaselineMessage("Candidate validation passed. Review every YAML change before applying the migration.");
  } catch (error) {
    state.migrationReviewToken = null;
    showBaselineMessage(error.message, true);
  } finally {
    reviewButton.disabled = !(cxAcknowledgement.checked && menuAcknowledgement.checked);
  }
}

function closeMigrationReview() {
  state.migrationReviewToken = null;
  elements.migrationReviewDialog.close();
  renderBaselinePlan();
}

async function saveReviewedBaselineMigration() {
  if (!state.migrationReviewToken) {
    showBaselineMessage("This migration review is no longer current. Review the complete plan again.", true);
    elements.migrationReviewDialog.close();
    return;
  }
  elements.migrationSaveButton.disabled = true;
  showBaselineMessage("Backing up and validating the reviewed multi-file migration…");
  try {
    const result = await request("/api/baseline-migration-saves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.migrationReviewToken }),
    });
    state.migrationReviewToken = null;
    elements.migrationReviewDialog.close();
    await Promise.all([loadProfiles(), loadBaseline()]);
    showBaselineMessage(`Migration applied to ${result.sourceFiles.length} source files. Validation passed. Recovery backup: ${result.backup}`);
  } catch (error) {
    state.migrationReviewToken = null;
    elements.migrationReviewDialog.close();
    showBaselineMessage(error.message, true);
  } finally {
    elements.migrationSaveButton.disabled = false;
  }
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
  if (control.value === "") return setting.baseline;
  if (setting.valueType === "integer") return Number.parseInt(control.value, 10);
  if (setting.valueType === "number") return Number(control.value);
  if (typeof control.value !== "string") return control.value;
  const canonical = (setting.choiceDetails || []).find((choice) => (
    typeof choice.value === "string"
    && choice.value.toLocaleLowerCase("en-US") === control.value.toLocaleLowerCase("en-US")
  ));
  return canonical ? canonical.value : control.value;
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
  markPreviewStale();
  setWorkflowStep(2);
  captureCurrentProfileDraft();
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
    displayCategory: elements.displayCategoryInput.value,
    release: elements.releaseInput.checked,
    overrides: state.draftOverrides,
    lensChoices: state.draftLensChoices,
    lensGuidanceFingerprint: state.detail.lensGuidanceFingerprint,
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
    elements.reviewEffectiveList.replaceChildren();
    for (const change of review.effectiveChanges || []) {
      const item = document.createElement("li");
      const label = document.createElement("strong");
      label.textContent = `${change.label}: `;
      const values = document.createElement("span");
      values.textContent = `${change.beforeDisplay} → ${change.afterDisplay} (${change.afterSource})`;
      item.append(label, values);
      elements.reviewEffectiveList.append(item);
    }
    elements.reviewEffective.hidden = elements.reviewEffectiveList.children.length === 0;
    elements.reviewDiff.textContent = review.diff;
    elements.reviewDialog.showModal();
    setWorkflowStep(4);
    showMessage("Candidate validation passed. Review the exact YAML before saving.");
  } catch (error) {
    setWorkflowStep(2);
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
    state.profileDrafts.delete(state.currentDraftKey);
    state.currentDraftKey = null;
    state.detail = null;
    invalidateBuildReadiness();
    elements.reviewDialog.close();
    await loadProfiles(result.savedProfile);
    await loadCxFoundations(true);
    const savedFiles = (result.sourceFiles || [result.sourceFile]).join(" and ");
    showMessage(`Saved ${savedFiles}. Validation passed. Recovery backup: ${result.backup}`);
  } catch (error) {
    state.reviewToken = null;
    elements.reviewDialog.close();
    showMessage(error.message, true);
  } finally {
    elements.saveButton.disabled = false;
  }
}

async function reviewProfileDiscard() {
  if (!state.detail?.editableDraft || state.detail.metadata?.release) return;
  const browserBlocker = profileDiscardBrowserBlocker();
  if (browserBlocker) {
    showMessage(browserBlocker, true);
    return;
  }
  elements.discardProfileButton.disabled = true;
  showMessage("Checking structured references and preparing the exact removal diff…");
  try {
    const review = await request("/api/profile-removal-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile: state.detail.name,
        sourceFingerprint: state.detail.sourceFingerprint,
      }),
    });
    state.discardReviewToken = review.reviewToken;
    elements.discardProfileSummary.textContent = review.summary;
    elements.discardProfileDiff.textContent = review.diff;
    elements.discardProfileMentions.replaceChildren();
    const mentions = review.narrativeMentions || [];
    elements.discardProfileMentions.hidden = mentions.length === 0;
    if (mentions.length) {
      const heading = document.createElement("h3");
      heading.textContent = `Narrative mentions to review (${mentions.length})`;
      const list = document.createElement("ul");
      for (const mention of mentions.slice(0, 40)) {
        const item = document.createElement("li");
        item.textContent = `${mention.file}:${mention.line} — ${mention.text}`;
        list.append(item);
      }
      elements.discardProfileMentions.append(heading, list);
    }
    elements.discardProfileDialog.showModal();
    showMessage("Structured dependency checks passed. Review the active-source removal and narrative warnings.");
  } catch (error) {
    state.discardReviewToken = null;
    showMessage(error.message, true);
  } finally {
    updateDiscardProfileAction();
  }
}

function closeProfileDiscardReview() {
  state.discardReviewToken = null;
  elements.discardProfileDialog.close();
}

async function saveProfileDiscard() {
  if (!state.discardReviewToken) {
    showMessage("This removal review is no longer current. Review the card again.", true);
    elements.discardProfileDialog.close();
    return;
  }
  elements.discardProfileConfirm.disabled = true;
  showMessage("Moving the card into the recoverable holding area and validating source…");
  try {
    const result = await request("/api/profile-removals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.discardReviewToken }),
    });
    state.discardReviewToken = null;
    state.profileDrafts.delete(state.currentDraftKey);
    state.cxSelectionDrafts.delete(state.detail.name);
    state.currentDraftKey = null;
    state.detail = null;
    invalidateBuildReadiness();
    elements.discardProfileDialog.close();
    await loadProfiles();
    await loadCxFoundations(true);
    showMessage(`Moved ${result.sourceFile} to Deleted Cards. Validation passed. Recovery backup: ${result.backup}`);
  } catch (error) {
    state.discardReviewToken = null;
    elements.discardProfileDialog.close();
    showMessage(error.message, true);
  } finally {
    elements.discardProfileConfirm.disabled = false;
  }
}

async function loadDeletedCards() {
  elements.deletedCardsList.replaceChildren();
  elements.deletedCardsMessage.hidden = false;
  elements.deletedCardsMessage.classList.remove("error");
  elements.deletedCardsMessage.textContent = "Loading Deleted Cards…";
  try {
    const payload = await request("/api/deleted-cards");
    const cards = payload.cards || [];
    elements.deletedCardsMessage.hidden = cards.length > 0;
    if (!cards.length) {
      elements.deletedCardsMessage.hidden = false;
      elements.deletedCardsMessage.textContent = "Deleted Cards is empty.";
      return;
    }
    for (const card of cards) {
      const row = document.createElement("article");
      row.className = "deleted-card-item";
      const copy = document.createElement("div");
      const title = document.createElement("h3");
      title.textContent = card.title || card.name;
      const detail = document.createElement("p");
      detail.textContent = `${card.sourceFile} · removed ${card.removed || "date unavailable"}`;
      const identity = document.createElement("code");
      identity.textContent = card.cardId;
      copy.append(title, detail, identity);
      const restore = document.createElement("button");
      restore.type = "button";
      restore.className = "save-action";
      restore.textContent = "Review restore";
      restore.addEventListener("click", () => reviewProfileRestore(card.cardId));
      row.append(copy, restore);
      elements.deletedCardsList.append(row);
    }
  } catch (error) {
    elements.deletedCardsMessage.hidden = false;
    elements.deletedCardsMessage.classList.add("error");
    elements.deletedCardsMessage.textContent = error.message;
  }
}

async function reviewProfileRestore(cardId) {
  try {
    const review = await request("/api/profile-restore-reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cardId }),
    });
    state.restoreReviewToken = review.reviewToken;
    elements.restoreProfileSummary.textContent = review.summary;
    elements.restoreProfileDiff.textContent = review.diff;
    elements.restoreProfileDialog.showModal();
  } catch (error) {
    elements.deletedCardsMessage.hidden = false;
    elements.deletedCardsMessage.classList.add("error");
    elements.deletedCardsMessage.textContent = error.message;
  }
}

function closeProfileRestoreReview() {
  state.restoreReviewToken = null;
  elements.restoreProfileDialog.close();
}

async function saveProfileRestore() {
  if (!state.restoreReviewToken) return;
  elements.restoreProfileConfirm.disabled = true;
  try {
    const result = await request("/api/profile-restores", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewToken: state.restoreReviewToken }),
    });
    state.restoreReviewToken = null;
    elements.restoreProfileDialog.close();
    invalidateBuildReadiness();
    await Promise.all([loadProfiles(result.restoredProfile), loadCxFoundations(true), loadDeletedCards()]);
    elements.deletedCardsMessage.hidden = false;
    elements.deletedCardsMessage.textContent = `Restored ${result.sourceFile}. Validation passed.`;
  } catch (error) {
    state.restoreReviewToken = null;
    elements.restoreProfileDialog.close();
    elements.deletedCardsMessage.hidden = false;
    elements.deletedCardsMessage.classList.add("error");
    elements.deletedCardsMessage.textContent = error.message;
  } finally {
    elements.restoreProfileConfirm.disabled = false;
  }
}

async function preview() {
  elements.previewButton.disabled = true;
  elements.previewButton.textContent = "Rendering…";
  showMessage("Rendering a temporary preview…");
  try {
    const body = state.detail?.cardType === "reference"
      ? { profile: state.detail.name, overrides: {} }
      : profileDraftPayload();
    const payload = await request("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (Array.isArray(payload.cardSettingPaths) && state.detail?.editableDraft) {
      state.detail.cardSettingPaths = payload.cardSettingPaths;
      render();
    }
    elements.previewPath.textContent = payload.outputFile;
    elements.previewFrame.src = `${payload.previewUrl}?t=${Date.now()}`;
    elements.previewFrame.hidden = false;
    elements.previewEmpty.hidden = true;
    state.previewLoaded = true;
    elements.previewPanel.classList.remove("is-stale");
    elements.previewStatus.textContent = "Current preview";
    setWorkflowStep(3);
    showMessage("Preview updated. No source was saved.");
    if (window.matchMedia("(max-width: 950px)").matches) setProfilePane("preview");
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    elements.previewButton.disabled = false;
    elements.previewButton.textContent = state.previewLoaded ? "Refresh preview" : "Render preview";
  }
}

elements.profileSelect.addEventListener("change", () => loadProfile(elements.profileSelect.value));
elements.openCameraLab.addEventListener("click", openCurrentProfileInCameraLab);
elements.sidebarCameraLab.addEventListener("click", openCurrentProfileInCameraLab);
elements.stopProfileEditor.addEventListener("click", stopProfileEditor);
for (const step of elements.daySteps) step.addEventListener("click", () => setDayPhase(step.dataset.dayPhase));
elements.refreshWorkflowPreflight.addEventListener("click", runWorkflowPreflight);
elements.beginWork.addEventListener("click", () => setDayPhase("work"));
elements.todayOpenProfiles.addEventListener("click", () => switchView("profiles"));
elements.todayOpenCameraLab.addEventListener("click", openCurrentProfileInCameraLab);
elements.todayOpenReviewBuild.addEventListener("click", () => switchView("review-build"));
elements.goToFinish.addEventListener("click", () => setDayPhase("finish"));
elements.finishOpenReviewBuild.addEventListener("click", () => switchView("review-build"));
elements.openFinishDay.addEventListener("click", () => switchView("finish-day"));
elements.switchingMacs.addEventListener("change", () => { elements.handoffGuidance.hidden = !elements.switchingMacs.checked; });
elements.continueToPublish.addEventListener("click", () => switchView("release-publish"));
elements.refreshFinishDay.addEventListener("click", refreshFinishDay);
elements.finishDayConfirmPrepare.addEventListener("change", renderFinishDay);
elements.prepareFinishDay.addEventListener("click", prepareFinishDay);
elements.finishDayConfirmCommit.addEventListener("change", renderFinishDay);
elements.finishDayCommitMessage.addEventListener("input", renderFinishDay);
elements.commitFinishDay.addEventListener("click", commitFinishDay);
elements.finishDayConfirmPush.addEventListener("change", renderFinishDay);
elements.pushFinishDay.addEventListener("click", pushFinishDay);
elements.openBranchIntegration.addEventListener("click", () => switchView("branch-integration"));
elements.refreshBranchIntegration.addEventListener("click", refreshBranchIntegration);
elements.branchIntegrationConfirmPrepare.addEventListener("change", renderBranchIntegration);
elements.prepareBranchIntegration.addEventListener("click", prepareBranchIntegration);
elements.branchIntegrationConfirmMerge.addEventListener("change", renderBranchIntegration);
elements.mergeBranchToMain.addEventListener("click", mergeBranchToMain);
elements.branchIntegrationConfirmPush.addEventListener("change", renderBranchIntegration);
elements.pushIntegratedMain.addEventListener("click", pushIntegratedMain);
elements.branchIntegrationConfirmResync.addEventListener("change", renderBranchIntegration);
elements.resyncIntegratedBranch.addEventListener("click", resyncIntegratedBranch);
elements.finishOpenCleanup.addEventListener("click", () => switchView("cleanup-review"));
elements.integrationOpenCleanup.addEventListener("click", () => switchView("cleanup-review"));
elements.refreshCleanupReview.addEventListener("click", refreshCleanupReview);
elements.cleanupConfirmDelete.addEventListener("change", renderCleanupSelection);
elements.deleteCleanupCandidates.addEventListener("click", deleteCleanupCandidates);
elements.refreshPublication.addEventListener("click", refreshPublication);
elements.openMainEditor.addEventListener("click", openMainEditor);
elements.publicationVersionKind.addEventListener("change", () => {
  elements.publicationMajorField.hidden = elements.publicationVersionKind.value !== "major";
  if (elements.publicationVersionKind.value === "major" && !elements.publicationMajorVersion.value) {
    const currentMajor = Number.parseInt(state.publication?.currentVersion?.split(".")[0], 10);
    if (Number.isInteger(currentMajor)) elements.publicationMajorVersion.value = String(currentMajor + 1);
  }
  state.publication = null;
  refreshPublication();
});
elements.publicationMajorVersion.addEventListener("change", refreshPublication);
elements.publicationHighlights.addEventListener("input", renderPublication);
elements.reviewPublicationNotes.addEventListener("click", reviewPublicationNotes);
elements.publicationNotesClose.addEventListener("click", closePublicationNotesReview);
elements.publicationNotesCancel.addEventListener("click", closePublicationNotesReview);
elements.publicationNotesConfirm.addEventListener("change", () => {
  elements.savePublicationNotes.disabled = !elements.publicationNotesConfirm.checked;
});
elements.savePublicationNotes.addEventListener("click", savePublicationNotes);
elements.reviewPublication.addEventListener("click", reviewPublication);
elements.publicationConfirmClose.addEventListener("click", closePublicationConfirmation);
elements.publicationConfirmCancel.addEventListener("click", closePublicationConfirmation);
elements.publicationConfirmLive.addEventListener("change", () => {
  elements.startPublication.disabled = !elements.publicationConfirmLive.checked;
});
elements.startPublication.addEventListener("click", startPublication);
elements.newButton.addEventListener("click", () => loadProfileDraft("create"));
elements.duplicateButton.addEventListener("click", () => {
  elements.profileActionMenu.open = false;
  loadProfileDraft("duplicate");
});
elements.discardProfileButton.addEventListener("click", () => {
  elements.profileActionMenu.open = false;
  reviewProfileDiscard();
});
elements.reloadButton.addEventListener("click", async () => {
  elements.profileActionMenu.open = false;
  if (!window.confirm("Discard this browser draft? These unsaved changes cannot be recovered.")) return;
  const detail = state.detail;
  state.profileDrafts.delete(state.currentDraftKey);
  state.currentDraftKey = null;
  state.detail = null;
  invalidateBuildReadiness();
  if (detail.operation === "update") await loadProfile(detail.name);
  else await loadProfile(detail.sourceProfile || elements.profileSelect.options[0]?.value);
  showMessage("Draft discarded and original source values reloaded. No profile was saved.");
});
elements.previewButton.addEventListener("click", preview);
elements.addLensChoice.addEventListener("click", addLensChoice);
elements.returnToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
window.addEventListener("scroll", updateFloatingReturn, { passive: true });
elements.reviewButton.addEventListener("click", reviewChanges);
elements.saveButton.addEventListener("click", saveReviewedProfile);
elements.reviewClose.addEventListener("click", () => elements.reviewDialog.close());
elements.reviewCancel.addEventListener("click", () => elements.reviewDialog.close());
elements.discardProfileClose.addEventListener("click", closeProfileDiscardReview);
elements.discardProfileCancel.addEventListener("click", closeProfileDiscardReview);
elements.discardProfileConfirm.addEventListener("click", saveProfileDiscard);
elements.refreshDeletedCards.addEventListener("click", loadDeletedCards);
elements.restoreProfileClose.addEventListener("click", closeProfileRestoreReview);
elements.restoreProfileCancel.addEventListener("click", closeProfileRestoreReview);
elements.restoreProfileConfirm.addEventListener("click", saveProfileRestore);
elements.migrationSaveButton.addEventListener("click", saveReviewedBaselineMigration);
elements.migrationReviewClose.addEventListener("click", closeMigrationReview);
elements.migrationReviewCancel.addEventListener("click", closeMigrationReview);
for (const input of [elements.titleInput, elements.subtitleInput, elements.filenameInput, elements.statusInput, elements.displayCategoryInput, elements.releaseInput]) {
  input.addEventListener("input", () => {
    if (input === elements.filenameInput && state.detail?.operation === "create") {
      state.filenameFollowsTitle = false;
    } else if (input === elements.titleInput && state.filenameFollowsTitle) {
      elements.filenameInput.value = profileFilenameFromTitle(elements.titleInput.value);
    }
    draftChanged();
    renderMetadataState();
    if (input === elements.displayCategoryInput) renderLensChoices();
  });
  input.addEventListener("change", () => {
    if (input === elements.filenameInput && state.detail?.operation === "create") {
      state.filenameFollowsTitle = false;
    } else if (input === elements.titleInput && state.filenameFollowsTitle) {
      elements.filenameInput.value = profileFilenameFromTitle(elements.titleInput.value);
    }
    draftChanged();
    renderMetadataState();
    if (input === elements.displayCategoryInput) renderLensChoices();
  });
}
for (const tab of elements.viewTabs) tab.addEventListener("click", () => switchView(tab.dataset.view));
for (const tab of elements.mobilePaneTabs) tab.addEventListener("click", () => setProfilePane(tab.dataset.pane));
elements.dictionarySearch.addEventListener("input", renderDictionary);
elements.dictionaryClassification.addEventListener("change", renderDictionary);
elements.loadSavedMenus.addEventListener("click", () => loadSavedMenus(true));
elements.loadRecommendedMenus.addEventListener("click", () => loadRecommendedMenus(true));
elements.analyzeMyMenu.addEventListener("click", analyzeMyMenuImpact);
elements.reviewMyMenuColors.addEventListener("click", reviewMyMenuColors);
elements.saveMyMenuColors.addEventListener("click", saveMyMenuColors);
elements.myMenuColorReviewClose.addEventListener("click", () => elements.myMenuColorReviewDialog.close());
elements.myMenuColorReviewCancel.addEventListener("click", () => elements.myMenuColorReviewDialog.close());
elements.reloadCxFoundation.addEventListener("click", () => {
  if ((hasCxAssignmentChanges() || hasCxSelectionChanges()) && !window.confirm("Discard all unsaved Cx Foundation changes and reload saved source?")) return;
  loadCxFoundations(false);
});
elements.reviewCxAssignments.addEventListener("click", reviewCxAssignments);
elements.cxProfileSelect.addEventListener("change", async () => {
  state.cxSelectedProfile = elements.cxProfileSelect.value;
  await refreshCxFoundationFit();
});
elements.reviewCxSelection.addEventListener("click", reviewCxSelection);
elements.cxFoundationReviewClose.addEventListener("click", () => elements.cxFoundationReviewDialog.close());
elements.cxFoundationReviewCancel.addEventListener("click", () => elements.cxFoundationReviewDialog.close());
elements.saveCxFoundation.addEventListener("click", saveCxFoundation);
elements.baselineAnalyze.addEventListener("click", () => analyzeBaselineDraft(false));
elements.baselineFollowAll.addEventListener("click", () => setUnresolvedBaselineDecisions("follow_baseline"));
elements.baselinePreserveAll.addEventListener("click", () => setUnresolvedBaselineDecisions("preserve_previous"));
elements.baselineBuildPlan.addEventListener("click", buildBaselinePlan);
elements.baselineBuildPlanBottom.addEventListener("click", buildBaselinePlan);
elements.baselineReset.addEventListener("click", () => {
  if (!window.confirm("Discard the baseline draft? These unsaved changes cannot be recovered.")) return;
  discardBaselineDraft();
});
elements.refreshReviewBuild.addEventListener("click", () => {
  captureCurrentProfileDraft();
  renderReviewBuild();
  showReviewBuildMessage("Session status refreshed.");
});
elements.validateReadiness.addEventListener("click", validateBuildReadiness);
elements.importVerificationTracker.addEventListener("click", importVerificationTracker);
elements.runLocalBuild.addEventListener("click", () => {
  if (state.buildReadiness?.ready && pendingSessionItems().length === 0) elements.buildConfirmDialog.showModal();
});
elements.buildConfirmClose.addEventListener("click", () => elements.buildConfirmDialog.close());
elements.buildConfirmCancel.addEventListener("click", () => elements.buildConfirmDialog.close());
elements.buildConfirmRun.addEventListener("click", runLocalBuild);
window.addEventListener("beforeunload", (event) => {
  captureCurrentProfileDraft();
  if (!pendingSessionItems().length) return;
  event.preventDefault();
  event.returnValue = "";
});

Promise.all([loadEditorInfo(), loadDictionary(), loadProfiles(), loadBaseline(), loadCxFoundations()]);
setDayPhase("start");
renderTodayWorkflow();
runWorkflowPreflight();
if (sessionStorage.getItem(GUARDED_JOB_KEYS.finishDay)) {
  switchView("finish-day");
} else if (sessionStorage.getItem(GUARDED_JOB_KEYS.branchIntegration)) {
  switchView("branch-integration");
} else if (sessionStorage.getItem(GUARDED_JOB_KEYS.publication)) {
  switchView("release-publish");
}
updateFloatingReturn();
