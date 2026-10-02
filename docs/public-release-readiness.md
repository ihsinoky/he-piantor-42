# Public-release readiness report

**Audit date:** 2026-10-02

**Decision owner:** Product Owner / PMO Human Gate

**Result:** **READY FOR PUBLIC HUMAN GATE**

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
observed. Confirmation that this expected attribution may become public is an
item in the final Product Owner Human Gate, rather than a technical STOP
condition. The act of approving public release constitutes that confirmation.

A negative pattern scan is not proof that no secret exists. GitHub-hosted
metadata review likewise cannot prove that no secret exists. The visibility
change must stop if any credential or sensitive information is identified
before the Product Owner decision.

## Git-history concerns

The local history contains 65 reachable commits. Subjects are engineering
summaries and Issue/PR references; no secret, private URL, password, or private
email was found in the reachable blobs or displayed commit metadata. No
history rewrite was attempted or proposed by this change.

The hosted review covered all remote branch names present during the
hosted-metadata audit and found no security blocker. The review does not claim
that deleted refs or every
historical binary artifact were exhaustively inspected. If content requiring
removal from Git history is found before release, stop; do not make the
repository public and handle any rewrite as a separate, owner-approved
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

## Remaining authorization condition

Engineering, security, and license readiness work is complete. Repository
visibility has not been changed or authorized. The sole remaining decision is
the Product Owner Human Gate: explicit approval is required before changing
visibility, and that approval also confirms that the expected public GitHub
identity and GitHub-generated noreply commit attribution may become public.

## Proposed visibility-change procedure

After Product Owner approval:

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

# READY FOR PUBLIC HUMAN GATE

The local code and history scan found no credential or directly unsafe personal
information, and the two targeted third-party provenance rows are resolved by
exact revision, path, Git-blob, license, and retained-notice evidence. No
third-party provenance **REVIEW REQUIRED** row remains for those assets.

The hosted GitHub metadata review passed with no public-release security
blocker identified. Engineering/security/license readiness is complete, but
repository visibility has not been changed or authorized. The repository must
remain private until the Product Owner makes the final visibility decision at
the Human Gate.

## Final Product Owner Human Gate checklist

- ☑ local tree/history audit complete
- ☑ third-party provenance resolved
- ☑ required license texts/notices present
- ☑ hosted GitHub metadata review complete
- ☑ no known credential/security blocker
- ☑ M1 tscircuit golden reference preserved
- ☐ Product Owner explicitly approves public release

The unchecked Product Owner approval is expected at **READY FOR PUBLIC HUMAN
GATE** and does not make the technical readiness result **NOT READY**. No
geometry, electrical design, Git history, JITX implementation, upstream notice,
or repository visibility was changed by this documentation update.
