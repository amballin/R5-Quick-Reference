# Protect the Application Owner Boundary on GitHub

This is a one-time repository-owner setup for `amballin/R5-Quick-Reference`. Repeat the verification after changing collaborators, GitHub plans, repository visibility, or repository rules.

The tracked `.github/CODEOWNERS` file assigns the protected application profile catalog to `@amballin`. It covers the ownership file itself, `00 Master/profile_catalog_policy.yaml`, `00 Master/profile_lens_guidance.yaml`, and everything under `10 Profiles/`.

CODEOWNERS provides review routing. It does not block a direct push by itself. The active GitHub ruleset is the remote enforcement boundary.

## When to activate this

Complete the current Step 7D source commit and integrate it into `main` first. GitHub uses the CODEOWNERS file from the pull request's base branch, so the ownership rules must exist on `main` before they can govern later contributions.

## Create the main-owner ruleset

1. Open the GitHub repository, choose **Settings**, then under **Code and automation** choose **Rules** → **Rulesets**.
2. Create a new **Branch ruleset** named `Application owner main protection` and set it to **Active**.
3. Target the default branch, `main`.
4. In **Bypass list**, add only **Repository admins** with **Always allow**. For this personal-account repository, `@amballin` is the single repository owner and therefore the sole administrator. Do not add Write, Maintain, collaborators, apps, or any other role.
5. Enable **Restrict updates**, **Restrict deletions**, and **Block force pushes**.
6. Enable **Require a pull request before merging** for contributors who are not the bypass owner.
7. Require one approval, enable **Dismiss stale pull request approvals when new commits are pushed**, and enable **Require review from Code Owners**.
8. Do not require a status check until this repository has a dedicated source-validation check that reports to GitHub. The existing Pages workflow validates published `docs/`; it is not a substitute for source validation.
9. Save the ruleset, then reopen it and verify its status is **Active**, its target is `main`, and **Repository admins** is the only bypass actor.

This arrangement preserves the existing Profile Editor **Integrate Branch** workflow for the owner: its direct `main` push is allowed through the **Repository admins** bypass. In a personal-account repository there is one owner with full control; ordinary collaborators have write access but are not repository administrators. Other contributors must use a pull request, and protected catalog changes require the CODEOWNERS review.

## Verify the protection

- On `main`, open `.github/CODEOWNERS` and confirm GitHub shows no syntax errors and identifies `@amballin` as owner.
- In **Settings** → **Rules** → **Rulesets**, confirm `Application owner main protection` is Active and targets `main`.
- In the repository access list, confirm `@amballin` remains the personal repository owner. If the repository is ever transferred to an organization, stop and redesign the bypass boundary before relying on this setup.
- Use GitHub's rules view for `main` to confirm the ruleset applies.
- When the first contributor pull request changes a protected catalog file, confirm GitHub requests `@amballin` and blocks merging until that review is approved.
- Do not treat the local Profile Editor checkbox, Git author name, commit email, or a clean validation result as proof of GitHub identity.

## Recovery

If the ruleset unexpectedly blocks the owner's reviewed Profile Editor push, do not weaken or delete the rules. Confirm the signed-in GitHub account is `@amballin`, confirm `@amballin` is still the personal repository owner, confirm **Repository admins** is the sole Always-allow bypass actor, and confirm the Git remote still points to `amballin/R5-Quick-Reference`. Correct the exact mismatch, then retry the existing reviewed integration.

GitHub references: [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), [Creating rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository), [Available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), and [Permission levels for a personal-account repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository).
