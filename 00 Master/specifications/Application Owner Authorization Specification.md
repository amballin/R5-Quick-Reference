# Application Owner Authorization Specification

## Scope and Status

This specification defines authenticated authorization for owner-only mutations in an application fork used with independently owned profile packs. It governs owner identity, signing credentials, exact-operation binding, protected operations, failure behavior, recovery, audit evidence, and the release gate for distributing Profile Editor to other profile-pack owners.

Step 7E Task 1 accepts this architecture but does not activate it. The existing textual application-owner checkbox remains a local role assertion until the separately approved implementation is complete. GitHub repository permissions and the active `main` ruleset remain the current remote enforcement boundary.

## Security Objective

A profile-pack owner may create, edit, validate, commit, and share that owner's own pack without receiving authority over the application repository. Possessing the application files, opening Profile Editor, changing browser state, knowing the application owner's username, or checking a confirmation box must not authorize an owner-only application mutation.

The system must answer two different questions independently:

1. **What is approved?** Exact review tokens, source fingerprints, candidate commits and trees, protected diffs, and current branch heads bind authorization to reviewed bytes.
2. **Who approved it?** A cryptographic signature made with the application owner's dedicated private signing key proves possession of the configured owner credential.

Neither answer substitutes for the other. GitHub separately decides whether the authenticated remote account may update the hosted repository.

## Roles and Boundaries

- The **profile-pack owner** controls only that pack's manifest-owned sources and independent Git repository.
- An **application contributor** may prepare feature-branch commits and proposals but cannot authorize an owner-only application mutation.
- The **application owner** controls the owner fork's protected embedded catalog, local `main` integration, `origin/main`, application publication, authentication policy, and acceptance of future shared-upstream changes.
- External-pack mode must continue rejecting application Git, application build, integration, publication, cleanup, and application-owner authorization endpoints server-side. Hiding controls in the browser is secondary.
- Application-owner authorization never grants profile-pack access and must not read, copy, sign, or publish private-pack source.

## Threat Model

The implementation must block:

- a profile-pack owner or application contributor who checks the owner-confirmation box;
- a request replayed from an earlier candidate, branch head, editor process, or operation;
- a signature made by an untrusted key;
- a candidate that replaces the trusted public key or owner policy and then attempts to authenticate under the replacement key;
- approval reuse after the candidate tree, protected diff, local worktree, working-branch head, `origin/main` head, repository identity, or operation changes;
- browser-only forgery, direct endpoint calls without the editor request token, and authorization attempts from an external-pack session;
- accidental leakage of a private key, passphrase, signature request, or credential through tracked source, pack source, browser storage, generated output, command logs, or publication output.

The design cannot defend against an attacker who controls the application owner's operating-system account together with the unlocked private key or hardware authenticator, controls the owner's GitHub account or repository ownership, or replaces the executable and trusted source on the owner's machine. Those are host/account compromises requiring credential revocation and repository recovery.

## Authentication Mechanism

Use a dedicated Ed25519 SSH-format application-owner signing key. The public key and its fingerprint are non-secret and will be recorded in a machine-readable application-owner policy. The private key must remain outside both repositories and browser storage, protected by a passphrase-backed operating-system credential store or a hardware-backed authenticator. Reusing an unprotected deployment token, Git password, author email, operating-system username, or plain configuration secret is prohibited.

The editor server—not browser JavaScript—must construct, request, and verify the signature. Use the platform's maintained SSH signing and verification tools rather than implementing cryptography in project code. The signing namespace must be dedicated to this application-owner protocol so a Git commit signature or unrelated signed file cannot be replayed as an authorization.

The trusted key for a proposed change comes from the current trusted `origin/main` owner policy, never solely from the candidate being approved. A key-policy change therefore requires authorization by a key trusted before that change.

## Machine-Readable Owner Policy

A later implementation must add a versioned application-owned policy containing at least:

- the application project ID and canonical GitHub repository owner/name;
- the expected application-owner GitHub login used for display and remote-policy review;
- the SSH signing namespace, public key, and public-key fingerprint;
- the owner-only operation classes;
- the expected GitHub ruleset name and target branch;
- key-policy schema version and rotation metadata.

The policy, CODEOWNERS file, owner public key material, protected catalog policy, authorization verifier, and remote-protection validation must themselves be owner-protected paths. Source validation must reject missing, malformed, duplicate, unsupported, or silently broadened authority declarations. No private key path, token, passphrase, credential-helper output, or machine-specific account data may be tracked.

## Canonical Authorization Statement

Each authorization request must serialize a canonical, versioned statement containing at least:

- application project ID and canonical repository identity;
- exact owner-only operation;
- current `origin/main` commit;
- current working-branch name and commit when applicable;
- reviewed candidate commit and tree when applicable;
- SHA-256 digest of the complete protected diff or exact reviewed write set;
- review-token digest;
- editor-process nonce;
- issuance and expiration times;
- one-use authorization ID.

Canonical serialization and hashing must be deterministic and independently testable. The private key signs the statement digest. Verification must prove the trusted key, namespace, signature, statement bytes, expiry, operation, process nonce, and every current source binding before an authorization receipt becomes usable.

## Owner-Only Operations

Authenticated owner authorization is required before:

- writing any protected embedded catalog, catalog policy, embedded lens-guidance, owner-policy, CODEOWNERS, or authorization-enforcement source through Profile Editor;
- applying any reviewed application branch candidate to local `main`, regardless of which application paths changed;
- pushing an integrated application `main` to `origin/main`;
- accepting protected content from a future shared upstream;
- running an application publication that commits or pushes owner-fork state;
- rotating or replacing the trusted application-owner key or policy.

Feature-branch authoring, validation, isolated candidate construction, and contributor pushes to non-main branches may remain available without owner authentication because they do not grant acceptance authority. They retain their existing reviews and safeguards.

Protected-catalog changes still require their separate exact protected-file and YAML-diff acknowledgment. Authentication proves the approver; the acknowledgment proves deliberate acceptance of that sensitive content. Neither control may silently satisfy the other.

## Transaction and UI Requirements

Replace owner identity language on a bare checkbox with an **Authenticate and approve** transaction. The UI must show:

- the expected owner login, repository, public-key fingerprint, operation, and expiration;
- the exact candidate and protected-diff identity being authorized;
- whether local cryptographic authentication is missing, pending, verified, expired, or invalid;
- GitHub remote protection as a separate status, never inferred from local authentication;
- a plain-language recovery action without exposing secrets or making a terminal command the only guidance.

The exact-content checkbox remains an acknowledgment and may enable the authentication action, but it is never identity evidence. A verified receipt is memory-only, short-lived, one-use, process-bound, and operation-bound. Refresh, restart, cancellation, failure, successful use, or any reviewed-state change invalidates it. Browser local storage and session storage must not preserve owner authorization.

Immediately before every owner-only mutation, the server must reverify the signature receipt and all exact bindings. Multi-stage workflows require a new authorization when the later operation has materially different authority, including the transition from local merge to remote push or from build review to publication.

## GitHub Enforcement

Local cryptographic authorization is defense in depth; it does not replace GitHub authentication or authorization. The owner repository must retain:

- the tracked CODEOWNERS boundary;
- an active `main` ruleset targeting the default branch;
- only **Repository admins** as an Always-allow bypass role while the personal repository has one owner;
- restricted updates and deletions, blocked force pushes, and required pull-request/Code Owner review for non-bypass contributors.

The application must display the expected remote and protection requirement before an owner-only push. It must never claim the GitHub ruleset is verified merely because source validation passes or a local signature is valid. If automated ruleset inspection is later added, it must be read-only, least-privilege, and must report unavailable or indeterminate state honestly.

## Key Rotation and Recovery

Normal key rotation is a protected candidate signed by the currently trusted key. The candidate may install the next public key only after the old-key authorization is verified against current `origin/main`. After the rotation reaches `main`, old outstanding receipts are invalid and the retired key is no longer accepted.

If the private key is lost, unavailable, or rejected, owner-only operations fail closed. Pack editing and read-only application use remain available. Recovery must occur through the GitHub repository owner's separately authenticated administrative control, restore a reviewed owner policy on `main`, revoke the lost key where applicable, obtain a clean trusted checkout, and rebuild the local application. The editor must not provide a checkbox, environment variable, command flag, policy edit, or fallback key that bypasses authentication.

## Audit Evidence and Privacy

Successful and rejected authorization attempts may record machine-local receipts containing the operation, authorization ID, public-key fingerprint, repository identity, candidate/diff digests, timestamps, and outcome. Receipts must never contain the private key, passphrase, raw credential-helper data, access token, complete private-pack content, or a reusable authentication secret. Audit output is evidence of a local verification result, not proof that GitHub accepted a push.

## Release Gate and Acceptance Tests

Profile Editor must not be described, packaged, or released as ready for other profile-pack owners until the implementation is complete and tests prove at least:

- a textual claim, browser manipulation, missing key, wrong key, replaced candidate key, wrong namespace, altered statement, expired receipt, replay, and changed source/ref are rejected;
- authorization under a candidate-added key is rejected unless the current trusted key approved its rotation;
- external-pack mode cannot call or expose application-owner authorization or application mutation endpoints;
- ordinary external-pack editing remains independent and does not require the application-owner key;
- all local-main merges, `origin/main` pushes, publication mutations, and protected embedded writes require the correct fresh authorization;
- protected-catalog acknowledgment remains separately required;
- credentials and machine-specific paths are absent from tracked, generated, logged, and published content;
- GitHub rejection or unavailable remote protection cannot be reported as successful authorization or synchronization;
- loss and rotation paths fail closed and preserve recoverable source state.

The implementation requires separate project-owner approval, recovery backup, machine-readable policy review, threat-focused automated tests, source validation, normal build, full validation, manual wrong-user acceptance testing, and an explicit release-readiness decision.
