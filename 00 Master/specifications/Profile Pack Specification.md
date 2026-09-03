# Profile Pack Specification

## Scope

This specification defines the accepted target contract for composing an independently owned private profile pack with the Canon EOS R5 application repository. It governs pack identity, source ownership, compatibility, selection, privacy, publication, Git independence, migration, and activation. General system boundaries remain governed by [`Architecture.md`](Architecture.md); profile YAML semantics remain governed by [`Profile Specification.md`](Profile%20Specification.md).

The contract is not activated for source migration, Camera Lab direct pack-source writes, Git, or publication. Steps 3A and 3B permit one explicit external pack for isolated development builds and combined source/generated-output validation. Step 4B permits guarded Profile Editor reads, previews, reviews, saves, and Deleted Cards recovery for an explicit pack. Step 4C adds a machine-local saved editor selection and guarded switching among remembered packs and embedded compatibility sources. Steps 5A and 5B permit Camera Lab comparison, guarded simulation, and explicitly enabled physical-camera operation against the editor-selected pack. Step 5C permits deliberate Profile Editor promotion of exact completed physical-camera evidence into the active pack's verification status. Spreadsheet generation, local build from the editor, cleanup, Git, handoff, main-editor launch, and publication remain unavailable in an external-pack session.

## Architecture and Trust Boundaries

- The target system has three distinct ownership roles:
  - the **shared upstream** supplies reusable application logic, schemas, validators, templates, Canon knowledge, and educational material;
  - the **owner application fork** accepts selected reusable updates, owns its release and publication workflow, and uses its own repository as `origin`;
  - the **private profile pack** owns personal camera configuration, workflow choices, equipment selection, and mutable verification state.
- The private profile pack must be a separate private Git repository. It must not be a Git submodule, subtree, vendored directory, or tracked application-repository dependency.
- The application and pack are independent authorities. Neither repository may commit, push, rewrite, clean, back up, restore, or otherwise mutate the other except through an exact action explicitly approved for that repository.
- A shared-upstream remote is optional and inbound-only in ordinary operation. Its exact remote and branch must be configured and reviewed explicitly. The application must never infer an upstream repository from hosting relationships, repository names, or URLs and must never redirect an `origin` operation to it.
- Pack privacy applies to canonical source. Generated output is governed separately by the publication rules below.

## Source Ownership

### Shared application source

The shared application owns reusable behavior and camera-independent or Canon-grounded definitions, including:

- schemas, setting catalogs, card layout, setting access, feature interactions, and Canon capability definitions;
- Profile Editor, Camera Lab, validation, rendering, spreadsheet, build, application-wrapper, and workflow logic;
- templates, reusable visual assets, Canon guides, and educational field-guide content;
- the profile-pack contract and its executable validator once implemented;
- generic sample or test fixtures that contain no owner data and are clearly identified as non-authoritative examples.

An owner's application fork may retain owner-specific release notes, project branding, and publication metadata. Those sources belong to the fork and are not supplied by the private pack merely because the fork can receive shared application updates.

### Private profile-pack source

The private pack owns:

- the operational baseline and every profile or reference-card declaration under its profile collection;
- My Menu tab names, ordered items, named-tab colors, and assignments;
- profile-specific lens guidance and the owner's equipment selection;
- owner-specific button and dial assignments, C1-C3 assignments and registration targets;
- mutable verification results, observations, sessions, evidence references, and history;
- private release selection for profiles and other pack-controlled content;
- pack-specific supporting configuration explicitly listed by the manifest contract.

The operational baseline and inheriting profiles must remain in the same pack. External-pack support must preserve the existing baseline-plus-overrides semantics and must not add a second override layer between an application baseline and a pack baseline.

### Sources requiring separation before activation

Current source families that combine reusable definitions with owner-specific state must be separated before external-pack activation:

- Canon equipment capability definitions must remain application-owned, while owned-equipment inventory and preferences become pack-owned.
- Verification checklist definitions, valid statuses, setting identities, and Canon access information must remain application-owned, while C1-C3 targets, results, notes, sessions, and history become pack-owned.
- Reusable control identities and Canon option definitions must remain application-owned, while current assignments, operations, INFO details, notes, and evidence state become pack-owned.

No mixed source may be copied into both repositories as competing canonical data. The activation review must identify exactly one canonical owner for every persisted field.

## Repository and Pack Identity

- The pack repository root is the directory containing `profile-pack.yaml` and its own `.git` directory or Git worktree identity.
- `profile-pack.yaml` is the sole pack manifest. It must be UTF-8 YAML with no duplicate keys.
- The pack root and every resolved source must use canonical real paths. A declared source must be relative to, contained by, and resolve within the pack root. Absolute paths, `..` traversal, unresolved symlinks, and symlinks escaping the pack root are invalid.
- The pack root or any parent folder marked old, backup, archive, build output, generated output, or native wrapper is invalid under the same normalized prohibited-name policy as the application repository.
- Pack identity must remain stable across clones and computers. Machine-local locations and credentials are not pack identity.
- Pack and application camera manufacturer and model must agree exactly. Firmware context may be more specific in the pack but must not claim compatibility the application contract rejects.

## Manifest Contract

The version-1 manifest has this normative shape:

```yaml
manifest_version: 1
pack_id: 00000000-0000-0000-0000-000000000000
pack_name: Canon EOS R5 Private Profile Pack
repository_role: private-profile-pack
artifact_type: source-repository
camera:
  manufacturer: Canon
  model: EOS R5
compatibility:
  application_project_id: canon-eos-r5-camera-reference
  profile_pack_contract: 1
sources:
  baseline: 00 Master/baseline.yaml
  profiles: 10 Profiles
  my_menu: 00 Master/my_menu.yaml
  my_menu_colors: 00 Master/my_menu_colors.yaml
  profile_lens_guidance: 00 Master/profile_lens_guidance.yaml
  owned_equipment: data/owned_equipment.yaml
  controls: controls.yaml
  registration_targets: 90 Testing/eos_r5_registration_targets.yaml
  verification_status: 90 Testing/eos_r5_verification_status.yaml
publication:
  default_profile_policy: explicit-release-only
```

Requirements:

- `manifest_version` must be integer `1` for this contract.
- `pack_id` must be one immutable UUID unique to the pack. Copying a pack for a new owner requires a new pack ID; cloning the same pack across computers preserves it.
- `pack_name` must be a non-empty, user-friendly human-facing label and is not machine identity. Profile Editor must display this live manifest value for an available external pack; it must not substitute a filesystem folder name, path, pack ID, or machine-local alias.
- `repository_role` must be `private-profile-pack` and `artifact_type` must be `source-repository`.
- `compatibility.application_project_id` must equal the selected application's project ID.
- `compatibility.profile_pack_contract` must name the one contract version understood by both sources. Unsupported versions stop before data loading, editing, validation, build, camera connection, Git mutation, or publication.
- Every `sources` key shown above is required for version 1. Paths are pack-root-relative canonical locations; alternate path layouts are not supported in version 1.
- `publication.default_profile_policy` must be `explicit-release-only`.
- Unknown top-level, compatibility, source, or publication keys are invalid in version 1. Contract extension requires an explicitly versioned specification change.
- The manifest must not contain repository credentials, access tokens, remotes, absolute machine paths, publication secrets, or mutable Git status.

The all-zero UUID in the example is illustrative and invalid for a real pack.

## Pack Selection and Resolution

- One application process may select exactly one profile pack.
- Selection order is:
  1. an explicit pack-root argument supplied to the supported command;
  2. an exact machine-local saved selection owned by that application checkout;
  3. embedded compatibility mode while the migration transition remains active;
  4. otherwise a stop requiring owner selection.
- Environment variables may support controlled automation only if a later implementation documents them; they must not silently outrank an explicit command selection or machine-local confirmed selection.
- The machine-local selection and remembered-pack registry store only canonical pack roots and pack IDs under `<application local workspace>/Profile Packs/editor-selection.json`. They must not store display-name aliases, be committed, be copied into generated output, or be treated as portable configuration. Available display names are read live from each pack manifest.
- Profile Editor must not scan the filesystem or sibling folders for packs. A new pack enters the registry only when the owner provides its exact root. Switching requires zero pending browser drafts, a separate confirmation, complete pack resolution, and successful editor-model loading before the saved selection changes.
- The ordinary Profile Editor launcher uses the valid saved selection. `--profile-pack PATH` remains the highest-priority one-launch override and does not silently replace the saved selection. `--embedded` is the fail-closed recovery override when a saved pack is missing, moved, identity-changed, or invalid; selecting embedded sources in the running editor clears the active saved pack while retaining valid remembered packs. After a recovery launch, a separately confirmed valid selection may replace an invalid registry, while ordinary startup continues to fail closed.
- Startup and every mutating boundary must revalidate application identity, pack identity, path containment, compatibility, and source fingerprints. A missing, moved, changed-identity, incompatible, or ambiguous pack stops safely.
- The resolved-source implementation must be centralized. Build, validators, Profile Editor, Camera Lab, spreadsheet tools, and publication must not independently reconstruct private source paths.
- Diagnostics and user interfaces must identify both the application checkout and selected pack without exposing credentials or unnecessarily displaying private filesystem paths.

## Cross-Boundary Integrity

- The combined resolved source set is the validation unit for profile UUIDs, baseline inheritance, C1-C3 mappings, My Menu cues, lens and equipment references, appendices, controls, and verification-definition fingerprints.
- Shared definitions are read-only to pack editing transactions. Pack sources are read-only to shared-application update transactions.
- A pack must not replace executable code, templates, schemas, validators, Canon capability definitions, or shared educational content through path shadowing.
- Duplicate identities, missing references, conflicting canonical owners, unsupported contract versions, or a pack source that resolves outside its root are blockers rather than merge opportunities.
- Validation errors must identify whether the defective source belongs to the application or pack.
- The deterministic pack fingerprint covers the manifest and every canonical pack source byte in normalized manifest-key and relative-path order. It excludes `.git`, machine-local state, backups, deleted-card holding areas, generated output, logs, credentials, and working spreadsheet files.

## Editing, Backups, and Recovery

- Profile Editor and Camera Lab must display the selected application context and pack context before any pack-backed work. Steps 5A–5B supersede the Step 4B Camera Lab prohibition for comparison and guarded camera operation. Step 5C additionally permits only the reviewed Profile Editor evidence-promotion transaction defined here; Camera Lab itself cannot write pack source.
- Step 4B permits Profile, lens-guidance, baseline, Cx Foundation, My Menu, owner-control, and Deleted Cards transactions only. Every canonical write targets the selected pack path declared by the manifest, or a direct profile YAML child of its declared profile directory. C1-C3 assignment changes also reconcile affected pack-owned verification-status fingerprints in the same reviewed transaction. Equipment editing and independent verification-result editing remain unavailable.
- Existing exact review, source fingerprint, one-use token, concurrent-change, validation, atomic replacement, rollback, and evidence-class safeguards remain required across the pack boundary.
- Pack backups belong in a machine-local workspace associated with the pack, never in either Git repository. A backup records the pack ID, pack commit when available, affected relative paths, and exact prior bytes.
- Deleted Cards is machine-local pack recovery state. It must remain associated with one pack ID and must never be offered to another pack with a coincidentally matching filename or card ID.
- Application backups and pack backups remain distinct. A recovery action names one authority and must not restore files into the other.

## Git, Upstream Updates, and Handoff

- The application and pack each require their own clean-status, exact-branch, matching-`origin`-upstream, ahead/behind, commit, push, and final-synchronization checks.
- Ordinary application Finish Day may commit and push only the owner application fork. Pack Finish Day may commit and push only the private pack.
- One review may describe coordinated changes, but two repository commits are not atomic and must not be represented as one transaction. Each mutation requires authority for its exact repository.
- Shared application updates are a separate, explicit inbound workflow. They must identify the configured shared remote and reviewed commits, stop on conflicts or incompatibility, and never push to that remote.
- A computer handoff that depends on combined application and pack work is complete only when both repositories are clean, synchronized with their respective matching `origin` branches, and recorded as a compatible pair.
- No workflow may create or switch branches in either repository without the project owner's explicit approval under the governing branch rule.

## Build and Publication

- `python3 "80 Build/build.py" --profile-pack PATH` is the Step 3A external development-build command. `PATH` must be the exact root of a separate compatible profile-pack Git repository; no environment variable or saved selection chooses a pack in this phase.
- The external development build resolves the pack baseline, profiles, My Menu configuration and colors, lens guidance, owned equipment, controls, registration targets, and verification status through the central `ProjectPaths` context. Application-owned templates, schemas, setting access, Canon definitions, assets, and field-guide content remain rooted in the application checkout.
- External output must be written under `<local workspace>/Profile Packs/<pack_id>/Build Output/`. Its Pages review belongs at `Build Output/pages`; it must not write application `docs/`, tracked workflow HTML, either repository, or another pack's machine-local output.
- Step 3A external builds reject publish mode, spreadsheet generation, and spreadsheet-download options. They do not by themselves activate Profile Editor, Camera Lab, Finish Day, Git, handoff, recovery, or publication support for external packs; later Steps 4B–5C activate only their expressly documented editor, Camera Lab, and evidence-promotion boundaries.
- `python3 "80 Build/validator.py" --profile-pack PATH --source-only` validates the combined application and selected-pack source set. The same command without `--source-only` validates that source set plus its pack-ID-namespaced generated output and isolated Pages mirror.
- Combined validation resolves pack-owned YAML, baseline, profiles, My Menu, controls, lens/equipment, registration, and verification sources through the same context used by the build. Application identity, structure, schemas, setting catalogs, Canon definitions, guides, assets, and governance remain application-root checks.
- External validation includes Profile Editor guarded-write readiness. It must instantiate the editor through the same selected `ProjectPaths` context, verify path-free application and pack identity, load the pack-backed editor surfaces, and verify the guarded boundary without mutating source.
- `python3 -B "80 Build/profile_editor.py" --profile-pack PATH` remains the explicit external editor command. In Step 4C, the normal launcher uses the machine-local saved selection when no explicit override is supplied, and `--embedded` bypasses it for one recovery launch.
- An external editor process must show application and pack identity, mark the workspace **guarded editing**, and load pack-owned baseline, profiles, My Menu, lens/equipment, controls, registration targets, and verification state through the centralized resolver.
- The server may accept only pack-namespaced preview endpoints, the reviewed Profile, lens-guidance, baseline, Cx Foundation, My Menu, Camera Buttons, removal, restore, and Camera Lab evidence-promotion endpoints, profile-pack selection, and the Camera Lab launcher. It must reject spreadsheet import/generation, build, cleanup, Git, Finish Day, branch integration, main-editor launch, and publication endpoints. Browser disabling is a secondary safeguard; server-side rejection and canonical path containment are authoritative.
- Steps 5A–5B Camera Lab accept an explicit compatible pack context from Profile Editor, display its live manifest name, and resolve pack-owned inputs through the same `ProjectPaths` instance. The Lab may connect, scan, compare, show C1–C3 foundations and setup routes, run guarded simulation, and use the explicitly enabled physical-write and reversible-qualification path. Existing preflight, review, confirmation, camera-identity, allowlist, readback, restore, and stop-on-failure safeguards remain mandatory. API operations revalidate the exact pack identity and fingerprint; an independently changed pack requires Camera Lab to stop and reopen. Machine-local Camera Lab state is namespaced under `<application local workspace>/Profile Packs/<pack_id>/Camera Lab/`, and new guarded/qualification journals record path-free pack identity. A legacy journal without pack identity cannot resume externally. Camera Lab cannot write pack source or promote evidence into canonical verification state. A running Lab may be reused only for the same pack ID, whether it is read-only or explicitly write-enabled.
- Camera Lab's version summary remains its sole visible Main/Prototype application-context signal. The expandable version detail contains the full branch and source hash; the redundant project-context badge is absent. The friendly path-free `Profile Pack:` badge remains visible independently.
- Step 5C evidence inventory resolves only `<application local workspace>/Profile Packs/<pack_id>/Camera Lab/Guarded Runs/`, requires a matching recorded pack ID in every external journal, and returns a path-free storage label. Missing-identity legacy journals and journals for another pack are ineligible. Promotion preserves the existing completed-physical-session, exact C1-C3 mapping, provenance, deduplication, draft-resolution, review, confirmation, concurrent-change, validation, backup, atomic-write, and rollback safeguards. It writes only the selected pack's manifest-owned verification-status YAML and does not create or refresh a spreadsheet working copy. External UI presents this surface as **Evidence Review** and hides unrelated build controls.
- Before API work, the server revalidates application identity, exact pack identity, compatibility, source containment, and the complete deterministic pack fingerprint. After its own successful guarded transaction it adopts the new verified fingerprint. A moved, missing, replaced, incompatible, identity-changed, or independently source-changed pack stops API work and requires an editor restart. Diagnostics expose pack name, ID, mode, and a shortened deterministic fingerprint without exposing its absolute path.
- External previews and Deleted Cards/backups use the selected pack's ID-namespaced machine-local workspace. They never write application source, application `docs/`, tracked workflow HTML, or another pack's recovery state.
- The header profile-pack chooser lists embedded sources plus remembered packs, displays each available external pack's live manifest `pack_name`, and never returns or renders stored roots. Switching replaces the complete bound editor context and reloads the browser. The editor version indicator remains the application Main/Prototype signal; a second yellow project-context badge is not shown. Its expandable details retain branch and source-hash diagnostics without displaying an application path.
- A combined build must validate the exact application commit or dirty-source fingerprint, pack commit or dirty-source fingerprint, pack ID, manifest version, contract version, and deterministic pack fingerprint before generation.
- Generated provenance must record the application revision, pack revision, pack ID, and pack fingerprint without recording an absolute pack path or repository credential.
- Local review output may include unreleased profiles only in existing explicitly non-publishable candidate locations.
- Published output may contain only profiles explicitly selected by the existing release flag and content expressly permitted by the applicable publication specification.
- Verification status, evidence references, session history, machine-local configuration, credentials, Git remotes, absolute paths, unreleased profile identities, and private backup metadata must never be published.
- Pack source privacy does not make released cards or other deliberately published derived content private. Publication review must state which pack and released profile IDs will be exposed.
- Publication requires both repositories to be clean, synchronized with their exact matching `origin` branches, contract-compatible, and bound to the reviewed revisions. Its completion receipt records both commit IDs and the pack fingerprint.
- The owner application fork remains the publication authority. The pack repository is an input and is never a website deployment target unless a future separately accepted architecture replaces this rule.

## Migration and Activation

Implementation must proceed incrementally:

1. Add a centralized resolved-source abstraction while preserving embedded compatibility mode.
2. Add manifest parsing, identity, containment, compatibility, fingerprint, and external-pack validation using temporary fixtures.
3. Route build, validators, Profile Editor, Camera Lab, spreadsheets, backups, and recovery through that abstraction.
4. Add independent application and pack Git workflows plus combined handoff and publication checks.
5. Split every mixed shared/private source so each persisted field has one canonical owner.
6. Create the real private pack from current canonical owner data without deleting the embedded source.
7. Build and validate once from the embedded layout and twice from clean external-pack checkouts; compare required structure, data, generated content, fingerprints, and behavior.
8. Review privacy scans and exact migration differences, then obtain separate project-owner approval to activate the external pack.
9. Only after activation succeeds, remove or replace embedded personal source through a separately backed-up and reviewed change.

A later separately approved pack-creation step must add a guided **New Profile Pack** capability. It collects a user-friendly `pack_name` and exact destination, generates a new immutable UUID, creates the complete contract-versioned source structure from an approved template or migration source, validates it before registration or selection, and never scans for or overwrites an existing pack. Optional Git repository initialization is a separate explicit choice. Steps 5A–5C do not create packs.

Activation is blocked unless all of the following are true:

- the application can validate independently with non-private fixtures;
- the private pack contains every canonical owner input and validates with the selected application;
- the external clean build reproduces the approved embedded result except for explicitly reviewed provenance changes;
- a second clean external build proves deterministic generation without hidden state;
- every personal-data editor writes only to the selected pack;
- shared upstream updates cannot overwrite pack source;
- Git, backup, restore, cleanup, handoff, and publication workflows correctly distinguish both repositories;
- generated output contains no private absolute path, credential, verification evidence, session history, or unreleased profile identity;
- rollback to the last verified embedded state has been demonstrated;
- operator documentation and generated guidance have been updated and fully validated;
- the project owner separately approves activation after reviewing the exact migrated sources and validation evidence.

## Transition State

This specification does not authorize source movement, creation of the real private repository, editor changes, Git changes, publication changes, or deletion. While transition is inactive:

- `00 Master/project_identity.yaml` and the current Git root retain their established authority;
- `00 Master/baseline.yaml`, `10 Profiles/`, My Menu sources, lens guidance, controls, equipment data, and verification sources remain in their current repository locations;
- the default embedded build and Profile Editor launch remain unchanged; the explicit Step 3A development-build command may generate from an external pack and writes solely to isolated machine-local output;
- general validation may use the explicit Step 3B pack argument, and Profile Editor may use explicit or machine-local Step 4C selection for guarded manifest-owned editing and pack-namespaced preview, backup, removal, and restore state; Steps 5A–5B Camera Lab may use that selected external pack for comparison and guarded camera operation, and Step 5C Profile Editor may promote exact eligible evidence into its verification status; equipment editing, independent verification editing, Camera Lab direct pack-source writes, spreadsheet generation, editor-initiated build, Finish Day, Integrate Branch, publication, cleanup, and handoff behavior remains embedded-only;
- Setup & Sharing must describe the currently active Step 4C editor selection and Steps 5A–5C Camera Lab/evidence boundary, while clearly marking source migration, pack creation, direct Camera Lab pack-source writes, two-repository Git/handoff, and publication activation as future work.

The transition ends only through a later Accepted activation decision after every required gate passes.

## Enforcement and Evidence

- This Markdown specification is the normative contract during the design transition.
- The Accepted **Private Profile Pack and Independent Upstream Architecture** decision records approval of the target and the inactive transition.
- `80 Build/profile_pack.py` implements embedded compatibility, strict explicit external-manifest parsing, application and pack identity checks, canonical source containment, deterministic pack fingerprinting, and path-free combined-build provenance. `80 Build/asset_manager.py` exposes the resolved context, preserves embedded paths for default callers, and namespaces external machine-local output by pack ID.
- `80 Build/test_profile_pack.py` verifies embedded-path parity, canonical external resolution, isolated path resolution, identity and contract rejection, required sources, duplicate and unknown keys, Git-root identity, path traversal, symlink escape, and fingerprint stability and sensitivity.
- `80 Build/test_profile_pack_build.py` constructs a temporary external Git pack from the current embedded sources, runs the supported external CLI, compares card/guide/PWA bytes with an embedded reference except for reviewed provenance, verifies the isolated Pages mirror, and proves that application `docs/` and tracked workflow guidance are unchanged.
- `80 Build/test_profile_pack_validator.py` verifies the external validator CLI, selected-pack identity reporting, guarded Profile Editor readiness, and detection of a defect in a pack-owned source. The end-to-end build fixture runs external source validation before generation and full external validation afterward.
- `80 Build/test_profile_pack_editor.py` verifies explicit guarded editor selection, path-free application/pack identity, resolved pack data, endpoint rejection, pack-change invalidation, CLI/browser state, pack-only Profile/lens, C1-C3, My Menu, Camera Buttons, Deleted Cards, and evidence-promotion transactions, pack-matched journal filtering, pack-namespaced backups, validation, and rollback.
- `80 Build/profile_pack_selection.py` implements the path-private machine-local registry, live manifest-name catalog, saved startup resolution, explicit-path registration, embedded recovery selection, and atomic mode-0600 persistence. `80 Build/test_profile_pack_selection.py` verifies those boundaries and normal-launch behavior.
- These Step 3A/3B/4C/5A/5B/5C development paths are not source-migration or publication activation: saved editor selection, external-pack Camera Lab comparison/guarded operation, and reviewed Profile Editor evidence promotion are available, while direct Camera Lab pack-source writes, spreadsheet generation, editor-initiated build, Git, handoff, cleanup, and publication workflows remain in embedded mode.
- Later implementation must identify the validators, workflow engines, and integration tests that enforce every remaining active requirement before activation.
- A passing current validator proves only the current embedded repository remains internally valid; it does not prove external-pack support or activation readiness.
