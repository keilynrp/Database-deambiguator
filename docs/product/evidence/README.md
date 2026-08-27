# Release Evidence Index

This directory is the governed location for versioned release-evidence
indexes produced by operating `docs/product/ENTERPRISE_CONTROL_REGISTER.md`
on a real release candidate (control `ER-CTRL-001`).

It does not replace or duplicate the register. The register remains the
sole authority on control status, priority, and ownership. Each file here
is a point-in-time reconciliation of that register against the evidence
actually available for one release candidate (RC).

## Authority

1. Control status: `docs/product/ENTERPRISE_CONTROL_REGISTER.md`
2. Maturity model and claim policy: `docs/product/ENTERPRISE_READINESS_PROGRAM.md`
3. Machine-readable control manifest: `backend/enterprise_controls.py`
4. This directory: evidence only. It records what was observed for a given
   RC; it never sets or overrides a control's current maturity.

## File naming

`RC-<YYYY>-<MM>-<DD>-<NN>.md`, where the date is the date the evidence
cycle was run (not necessarily the commit date) and `NN` is a two-digit
sequence for same-day cycles (`01`, `02`, ...). IDs are never reused or
rewritten after publication; a correction is a new file plus a dated
addendum note in the superseded file, not an edit to a settled evidence
snapshot.

## Reproducible procedure for the next release candidate

1. **Select the candidate.** Pick the exact `main` commit SHA being
   evaluated. Do not change the SHA once evidence collection starts; if the
   SHA proves invalid mid-cycle, stop and escalate rather than silently
   switching candidates.
2. **Collect CI evidence for that exact SHA**, not for a branch name:
   - `gh api repos/<org>/<repo>/actions/runs?head_sha=<sha>` for the
     push-triggered workflow runs on `main`.
   - `gh api repos/<org>/<repo>/actions/runs/<run_id>/jobs` for per-job
     conclusions (a workflow-level conclusion can hide a single flaky job,
     or mask a real failure among otherwise-green jobs — check jobs, not
     just the workflow summary).
   - `gh api repos/<org>/<repo>/actions/runs/<run_id>/artifacts` to confirm
     SBOM/coverage/report artifacts actually exist and are not expired.
   - `gh api repos/<org>/<repo>/branches/main/protection` to check whether
     push protection / required checks are actually enabled (do not assume
     — this has historically been unset; see `ER-SDLC-001`).
3. **Read `docs/product/ENTERPRISE_CONTROL_REGISTER.md` as it stands at that
   SHA.** If it has changed since the last cycle, reconcile against the new
   text and call out the drift explicitly in the new evidence file.
4. **Persist the contemporaneous P0/P1 control-set snapshot**, then fill
   every row it lists. Copy the exact list of P0/P1 control IDs from
   `ENTERPRISE_CONTROLS` (`backend/enterprise_controls.py`) as of this
   cycle into a ```` ```control-set-snapshot ```` fenced block under §1 (see
   any existing RC file for the format). One row per control in that
   snapshot, exactly once. Use only one of the five evidence dispositions:
   `EVIDENCED`, `PARTIALLY EVIDENCED`, `NOT EVIDENCED`,
   `OPERATOR ACTION REQUIRED`, `EXTERNAL ASSURANCE REQUIRED`.
   Cite exact run/job/artifact IDs. A branch name, a chat message, or an
   unlinked claim is not evidence.

   `scripts/lint_release_evidence.py` validates every RC file against its
   *own* persisted snapshot, not the current manifest — that is what keeps
   older, settled RC files valid after later control additions/removals
   (see "File naming" above). It additionally requires the *newest* RC's
   snapshot to equal the current manifest's P0/P1 set, so a newly authored
   RC cannot silently omit or invent a control.
5. **Do not promote maturity from the evidence file alone.** A control's
   `current_maturity` only changes in
   `docs/product/ENTERPRISE_CONTROL_REGISTER.md` and
   `backend/enterprise_controls.py` together, in a change that an
   accountable owner reviews on its own terms — never as a side effect of
   publishing an evidence index.
6. **Validate before opening a PR:**
   `python scripts/lint_release_evidence.py`
   This fails closed if a P0/P1 control is missing, duplicated, has no
   disposition, or if the register/manifest pair drifts.
7. **Record residual risks and an invalidation trigger list** — what would
   make this specific evidence snapshot stale (new commits to security
   workflows, branch-protection changes, artifact expiry, a superseding
   register edit).
8. **Leave the owner-attestation field for the accountable owner to sign.**
   The agent or engineer producing the evidence file does not self-attest.
