# Shared SlopMonster editorial advisory

GoreeCloud uses [SlopMonster](https://github.com/ItsssssJack/SlopMonster) to identify English-language prose that could benefit from editorial review. The source is licensed MIT; the scorer is checked out from the specific upstream revision `3fc9787d9337b57c599a80afbefbbb3be5a8eb0b`.

## Coverage and intent

The shared workflow in `GoreeCloud/.github` is called by lightweight workflows in individual repositories. The published callers must pin their reusable workflow reference and `advisory_sha` input to the same reviewed 40-character central commit; a manually triggered shared workflow may use the current `main` scanner. Central upgrades require deliberate caller repinning after validation. On pull requests and pushes it examines `README.md` plus eligible changed Markdown and selected HTML. On `workflow_dispatch` it checks up to 50 eligible tracked files. If the Git comparison base is missing, it falls back to a bounded tracked-file audit. If Git cannot enumerate files, the advisory explicitly reports an incomplete scan rather than certifying clean prose. Generated, vendored and dependency directories are excluded; files over 128 KiB are skipped. Individual scan commands time out after eight seconds to bound execution. The scanner rejects misleading scorer exit codes without the expected score output, reports no-visible-prose separately, and marks reviews with skipped files as partial coverage. Summaries appear in GitHub Actions.

Findings never gate a merge. The workflow has `contents: read`, uses pinned checkouts, does not send repository text to an AI API, never changes the content it scans and does not comment on pull requests. Scorer errors are also advisory: the scanner returns a diagnostic exit code, while the job uses `continue-on-error: true` and reports unavailable setup checks separately. This is not a substitute for checking whether the action itself executed.

No SlopMonster score establishes authenticity, correctness, writing quality, or security. A reviewer must check facts and intent. The scanner is English-only and scans source HTML rather than rendering a browser page.

## Rollout and rollback

Install this shared workflow and `scripts/slopmonster_advisory.py` in `GoreeCloud/.github` first. Merge that change to `main` before enabling caller workflows. Add the caller workflow at `.github/workflows/slopmonster-advisory.yml` to each active repository with documented, human-facing text. Empty and archived repositories are excluded. Confirm successful workflow runs in each repository. The broad rollout script requires a validated `gc-ui` pilot on the exact currently published central revision before publishing any other wrapper.

To roll back in an application, remove its small caller workflow. Shared files in `.github` can remain until every caller is retired. Do not adjust required checks, branch protections or repository permissions.

To upgrade SlopMonster, review the upstream diff and tests, change the pinned SHA in the shared workflow, run validation, and separately verify runner execution before considering wider adoption.

## Release acceptance note

The advisory workflow intentionally marks scoring exceptions non-blocking. Therefore a successful overall GitHub Actions job **does not prove** that every eligible document was scored. Inspect the summary and any explicit incomplete-coverage or prerequisite warnings during pilot acceptance. Ecosystem expansion must additionally verify that the most recent completed hosted pilot run corresponds to the exact current `gc-ui/main` commit and the same pinned central workflow revision.
