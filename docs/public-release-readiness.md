# Public-release readiness report

**Audit date:** 2026-10-02

**Decision owner:** Product Owner / PMO Human Gate

**Result:** **NOT READY**

This report prepares a decision; it does not authorize or perform a repository
visibility change and does not migrate the authoritative EDA source to JITX.

## Audit scope

The audit covered:

- every file tracked at commit `795479e` (the PR #27 M1 baseline);
- all 65 commits and 134 unique Git blobs reachable from local refs;
- commit subjects, author names, and author email addresses;
- GitHub Actions workflows and repository Issue/PR templates;
- URLs, credential-like strings, sensitive filenames, generated outputs, and
  vendored/reference design assets in the current tree;
- the local repository configuration and available repository metadata; and
- the third-party hardware/reference assets enumerated in
  `hardware/lib/THIRD_PARTY.md`.

The audit did **not** inspect GitHub Issue or Pull Request bodies/comments,
reviews, Actions logs/artifacts, releases, repository secrets/variables,
branch-protection settings, deleted remote refs, forks, or other GitHub-only
metadata. The checkout has no configured remote and GitHub CLI has no
credentials, so that material was unavailable. It must be reviewed at the Human
Gate.

## Frozen engineering state

PR #27 completed EVT-001. The M1 four-key model at
`hardware/tscircuit/src/evaluation/m1-four-key.tsx`, together with existing
Checkpoint A/B/C verification, is the frozen electrical golden reference.
D-014 remains an accepted historical decision. EVT-002 and final placement,
routing, and DRC have not started and must remain on hold until the Product
Owner resolves the JITX EDA evaluation gate.

## License mapping

`LICENSE.md` is the repository-level authoritative path map:

- project-authored hardware, mechanical, and manufacturing design material is
  CERN-OHL-P-2.0;
- project-authored firmware, software, scripts, dashboard, and documentation is
  MIT;
- third-party material retains its upstream license and notices; and
- unresolved mixed/provenance files are explicitly marked **REVIEW REQUIRED**
  rather than being relicensed by assumption.

Full project license texts are present at `LICENSES/CERN-OHL-P-2.0.txt` and
`LICENSES/MIT.txt`.

## Third-party inventory result

The marbastlib Hall footprint (CERN-OHL-P-2.0), Keebio W25Q16 footprint (MIT),
and RP2040-minimal reference (BSD-3-Clause) have source URLs and license texts
in the repository. Their notices were preserved.

The detailed inventory found unresolved redistribution provenance for:

1. the QMK Cantor coordinate source identified by
   `hardware/layout/layout_source.json` and its generated outputs; and
2. individual cached/rescued KiCad symbols and copied footprints in
   `hardware/sensor-test/kicad/`, whose exact upstream revisions and per-file
   license boundaries are not recorded.

The RP2040-derived working schematics carry the BSD text, but their exact copied
and modified boundaries should also be pinned. See
`hardware/lib/THIRD_PARTY.md` for paths and required follow-up evidence.

## Secret and privacy audit result

No credential or secret was found by the local audit. Checks included the
current tree and every reachable historical blob for common private-key
headers, AWS access-key IDs, GitHub and Slack token forms, credential assignment
patterns, private/local URLs, and sensitive filenames. Manual URL review found
public source, package-registry, manufacturer, and datasheet links; it found no
private task/session URL. Git config contains no remote or stored credential.

Commit metadata exposes one GitHub noreply address and the public account name
`ihsinoky`; no private email address was observed. This is appropriate only if
the account owner confirms that the attribution is intended to become public.

A negative pattern scan is not proof that no secret exists. GitHub-hosted
metadata and logs remain unaudited, and the visibility change must stop if the
owner review finds any committed credential or sensitive information.

## Git-history concerns

The local history contains 65 reachable commits. Subjects are engineering
summaries and Issue/PR references; no secret, private URL, password, or private
email was found in the reachable blobs or displayed commit metadata. No
history rewrite was attempted or proposed by this change.

**Unresolved:** local refs cannot prove that the remote has no additional or
deleted refs, releases, attachments, Actions artifacts, or sensitive Issue/PR
content. Fetch all remote refs and complete the hosted-metadata review before a
public decision. If that review finds content requiring removal from Git
history, stop; do not make the repository public and handle any rewrite as a
separate, owner-approved incident procedure.

## Repository-metadata concerns

Workflow files request read-only contents permission and do not contain literal
credentials. They use third-party Actions by mutable major tags (`@v4`, `@v2`)
rather than immutable commit SHAs; this is a supply-chain hardening follow-up,
not evidence of a leaked secret. Workflow artifacts and logs were unavailable.

Issue and PR templates contain no sensitive values. Actual Issue/PR bodies,
comments, reviews, attachments, labels, branch names on the remote, Actions
settings, secrets/variables, webhooks, deploy keys, collaborators, and release
assets were not accessible. In particular, PR #27 was established from local
Git history, not from a hosted-content audit.

## Unresolved concerns and STOP conditions

The following blockers require PMO / Product Owner review:

1. **Third-party redistribution is not fully established.** Resolve the QMK
   coordinate and KiCad cache/rescue provenance rows in the canonical inventory.
2. **Hosted repository metadata is unaudited.** Authenticate with read access
   and review Issues, PRs, comments, reviews, attachments, Actions logs and
   artifacts, releases, all refs, and repository/security settings.
3. **Attribution confirmation is required.** The owner must confirm that the
   GitHub account name and noreply commit identity may be published.

These are STOP conditions. Do not change visibility until all are resolved and
this report is updated to `READY FOR PUBLIC HUMAN GATE`.

## Proposed visibility-change procedure

After resolving the blockers:

1. Freeze merges and record the exact candidate commit and all remote ref tips.
2. Re-run current-tree and all-ref secret scanning with a maintained scanner,
   then manually review high-entropy findings and all URLs.
3. Review every Issue, PR, comment, review, attachment, release, Actions
   log/artifact, branch/tag name, wiki, project board, webhook, deploy key,
   environment, variable, and collaborator for public suitability.
4. Resolve every **REVIEW REQUIRED** inventory row; preserve or add the exact
   upstream notices without altering upstream content.
5. Confirm the license map and copyright authority with the Product Owner and,
   if needed, qualified legal review.
6. Confirm that no fork, mirror, package, site, JITX upload, or other external
   publication is triggered unintentionally.
7. Obtain an explicit, recorded Product Owner approval at the Human Gate.
8. Change visibility in GitHub settings manually, without changing EDA
   authority, and immediately verify anonymous access to expected files only.
9. Open a post-publication verification Issue and monitor security reports.

## Rollback and mitigation considerations

Changing a repository back to private does not retract clones, caches, forks,
notifications, search indexes, downloaded artifacts, or package copies. Treat
public release as irreversible disclosure. Before the change, revoke and rotate
any credential if there is doubt—even if it appears deleted—and preserve a
private evidence bundle of audit outputs and ref tips.

If sensitive content is found after publication, make the repository private,
revoke affected credentials first, notify the Product Owner/security contacts,
assess downstream copies, and only then plan any separately approved history
rewrite. Licensing/provenance failures require taking affected distribution
links down where possible and contacting the relevant rightsholder; silently
removing notices is not a mitigation.

## Final readiness result

# PENDING HOSTED-METADATA REVIEW — AND THIRD-PARTY PROVENANCE REMAINS BLOCKED

The local code and history scan found no credential or directly unsafe personal
information, and the mixed-license structure is now explicit. However,
third-party redistribution provenance and GitHub-hosted metadata remain
unresolved. The repository must remain private pending the PMO / Product Owner
Human Gate and resolution of the STOP conditions above.

The targeted 2026-10-02 follow-up audit did not clear the third-party blocker:
the local history records neither the QMK/Cantor revision used for the layout
tuples nor the RP2040-minimal/KiCad revisions used for each working asset.
Because exact provenance cannot be established without upstream evidence, the
requested STOP condition applies. No geometry, electrical design, upstream
notice, or repository visibility was changed. Hosted GitHub metadata remains
explicitly outside this audit and pending PMO review.
