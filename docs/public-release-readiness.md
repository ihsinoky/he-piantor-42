# Public-release readiness report

**Audit date:** 2026-10-02

**Decision owner:** Product Owner / PMO Human Gate

**Result:** **PUBLIC RELEASE COMPLETED**

This report records both the pre-release audit and the completed publication
decision. The Product Owner explicitly approved public release before the
repository visibility was changed. Publication did not migrate the
authoritative EDA source to JITX.

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
  `hardware/lib/THIRD_PARTY.md`; and
- GitHub-hosted metadata accessible through the repository connection: all
  Pull Request discussions and Issue bodies existing at the time of review,
  all remote branch names present during the hosted-metadata audit, current
  workflow definitions, representative successful and failed Actions logs
  across workflow types, relevant artifact names and purposes, Codex Task URLs
  in historical PR bodies, and Vercel bot comments, project/deployment
  identifiers, and Preview URLs.

The hosted review was risk-based. It did **not** manually inspect every
historical binary artifact or every individual Actions log line. Repository
secrets (including encrypted secrets), webhooks, deploy keys, and similar
GitHub configuration are not public repository content and are neither
required to be disclosed nor enumerated by this report.

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
- QMK-derived layout assets remain under their GPL-2.0-only exception; and
- RP2040-minimal-derived assets retain their BSD-3-Clause notice.

Full project license texts are present at `LICENSES/CERN-OHL-P-2.0.txt` and
`LICENSES/MIT.txt`; the QMK exception text is at
`LICENSES/GPL-2.0-only.txt`.

## Third-party inventory result

The marbastlib Hall footprint (CERN-OHL-P-2.0), Keebio W25Q16 footprint (MIT),
and RP2040-minimal reference (BSD-3-Clause) have source URLs and license texts
in the repository. Their notices were preserved.

PMO external evidence resolved both targeted provenance rows. The QMK-derived
42-tuple sequence is pinned to `qmk/qmk_firmware` revision
`d9f6dd215f2c4d295c6ad85b1f602125c2d81db1`, including the Cantor source and
equivalent Beekeeb Piantor layout, and is conservatively covered by the QMK
GPL-2.0-only exception. The RP2040 cache, rescue library, legacy symbol library,
and three footprints are exact Git-blob matches to RP2040-minimal-design
revision `7a3e5234447a9e01624c6a8de12d510f9e0161a7` and retain its BSD-3-Clause
notice. Working schematic derivatives retain that notice, while project
modifications are additionally CERN-OHL-P-2.0.

The QMK exception does not affect the current four-key M1 JITX electrical
evaluation, which does not consume the 42-key coordinate asset. The source and
license strategy for final 42-key JITX Rev.A geometry remains a future Human
Gate, not a conclusion of this audit.

## Secret and privacy audit result

No credential or secret was found by the local audit. Checks included the
current tree and every reachable historical blob for common private-key
headers, AWS access-key IDs, GitHub and Slack token forms, credential assignment
patterns, private/local URLs, and sensitive filenames. Manual URL review found
public source, package-registry, manufacturer, and datasheet links; it found no
private task/session URL. Git config contains no remote or stored credential.

Commit metadata exposes the public GitHub identity `ihsinoky` and a
GitHub-generated noreply commit identity; no private email address was
observed. The Product Owner's explicit approval at the final Human Gate
confirmed that this expected attribution could become public, and it is now
public following the visibility change.

A negative pattern scan is not proof that no secret exists. GitHub-hosted
metadata review likewise cannot prove that no secret exists. Before the
Product Owner decision, identification of any credential or sensitive
information would have stopped the visibility change; none was identified.

## Git-history concerns

The local history contains 65 reachable commits. Subjects are engineering
summaries and Issue/PR references; no secret, private URL, password, or private
email was found in the reachable blobs or displayed commit metadata. No
history rewrite was attempted or proposed by this change.

The hosted review covered all remote branch names present during the
hosted-metadata audit and found no security blocker. The review does not claim
that deleted refs or every
historical binary artifact were exhaustively inspected. If content requiring
removal from Git history had been found before release, publication would have
stopped and any rewrite would have required a separate, owner-approved
incident procedure.

## Repository-metadata concerns

Workflow files request read-only contents permission and do not contain literal
credentials. They use third-party Actions by mutable major tags (`@v4`, `@v2`)
rather than immutable commit SHAs; this is a supply-chain hardening follow-up,
not evidence of a leaked secret.

**Hosted metadata result: PASS — no public-release security blocker
identified.** PMO reviewed all Pull Request discussions and Issue bodies
existing at the time of review, together with all remote branch names present
during the hosted-metadata audit and the current workflow definitions.
Representative successful and failed Actions logs across workflow types were
inspected for secret/private-data patterns, and relevant artifact names and
purposes were reviewed. This was not a claim that every log line or every
historical binary artifact was manually inspected.

Codex Task URLs in historical PR bodies and Vercel bot comments,
project/deployment identifiers, and Preview URLs were reviewed and
intentionally accepted; they are not credentials or public-release blockers.
No credential, private key, GitHub/AWS/Slack token, Cloudflare Access
credential, or other security blocker was identified. Issue and PR templates
also contain no sensitive values.

## Product Owner Human Gate outcome

Engineering, security, and license readiness work is complete. Repository
visibility was changed to public only after the Product Owner explicitly
approved public release. That approval completed the Public Human Gate and
confirmed publication of the expected GitHub identity and GitHub-generated
noreply commit attribution. No known public-release blocker remains.

## Pre-publication visibility-change procedure

The audit recorded the following procedure to be followed after Product Owner
approval:

1. Freeze merges and record the exact candidate commit and all remote ref tips.
2. Re-run current-tree and all-ref secret scanning with a maintained scanner,
   then manually review high-entropy findings and all URLs.
3. Reconfirm that no material change since the completed hosted-metadata review
   introduces a new public-content security blocker.
4. Reconfirm the pinned third-party inventory and preserve every upstream
   notice without altering upstream content.
5. Confirm the license map and copyright authority with the Product Owner and,
   if needed, qualified legal review.
6. Confirm that no fork, mirror, package, site, JITX upload, or other external
   publication is triggered unintentionally.
7. Obtain an explicit, recorded Product Owner approval at the Human Gate.
8. Change visibility in GitHub settings manually, without changing EDA
   authority, and perform post-publication access verification.
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

# PUBLIC RELEASE COMPLETED

The local code and history scan found no credential or directly unsafe personal
information, and the two targeted third-party provenance rows are resolved by
exact revision, path, Git-blob, license, and retained-notice evidence. No
third-party provenance **REVIEW REQUIRED** row remains for those assets.

The hosted GitHub metadata review passed with no public-release security
blocker identified. Engineering/security/license readiness is complete. The
Product Owner explicitly approved public release before repository visibility
was changed to public, completing the Public Human Gate. No known
public-release blocker remains.

## Final Product Owner Human Gate checklist

- ☑ local tree/history audit complete
- ☑ third-party provenance resolved
- ☑ required license texts/notices present
- ☑ hosted GitHub metadata review complete
- ☑ no known credential/security blocker
- ☑ M1 tscircuit golden reference preserved
- ☑ Product Owner explicitly approves public release

Product Owner approval was explicitly given and recorded before repository
visibility was changed. The Human Gate is complete.

## Post-publication verification

- GitHub repository metadata reports `visibility = public`.
- The default branch is `main`.
- Branch cleanup resulted in `main` being the only remote branch at the time of
  post-publication verification.
- The publication operation modified no engineering design.
- The frozen M1 tscircuit golden reference remains unchanged.
- JITX implementation has not started.

This documentation synchronization changes no geometry, electrical design,
Git history, JITX implementation, upstream notice, license decision, or
repository visibility.
