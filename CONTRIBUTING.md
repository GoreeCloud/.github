# Contributing to GoreeCloud

Thank you for helping improve GoreeCloud. This file provides default contribution guidance for repositories that do not define a more specific local process.

## Before you start

1. Read the target repository's `README.md`, contribution guidance, specifications, and development documentation when present.
2. Check existing issues and pull requests before starting duplicate work.
3. Keep the change focused on one coherent purpose.
4. Do not include credentials, secrets, private user data, internal-only infrastructure details, or other sensitive material.

Repository-local instructions take precedence when they are more specific.

## Branches

Use short-lived, purpose-specific branches where practical. Clear examples include:

- `feature/<name>`
- `fix/<name>`
- `docs/<name>`
- `security/<name>`
- `refactor/<name>`
- `test/<name>`
- `build/<name>`
- `ci/<name>`

Branch names should be lowercase, descriptive, automation-safe, and free of sensitive information.

## Changes and commits

Make changes that are understandable, reviewable, and recoverable.

- Preserve unrelated behavior and files.
- Follow the repository's established architecture and formatting conventions.
- Add or update tests when behavior changes.
- Update repository documentation when the change affects documented behavior, interfaces, configuration, or lifecycle state.
- Preserve third-party provenance, notices, and license obligations.
- Do not describe planned, partial, or unverified work as implemented, released, deployed, production-ready, or accepted.

## Pull requests

Material changes should normally be submitted through a pull request.

A useful pull request explains:

- what changed;
- why the change is needed;
- the scope and affected components;
- validation performed on the exact proposed revision;
- security, privacy, compatibility, migration, or recovery considerations when applicable;
- remaining limitations or follow-up work.

Use the repository's pull-request template when one is provided.

## Validation

Run the checks applicable to the repository before requesting merge. Depending on the project, this may include formatting, linting, unit tests, integration tests, builds, security checks, accessibility validation, or platform-specific acceptance.

A passing build alone does not establish release, deployment, production, or lifecycle acceptance.

## User interface changes

For repositories using Glaze UI or another governed GoreeCloud interface layer, preserve the repository's current design-system contract and applicable accessibility behavior. Validate relevant responsive states, keyboard or assistive-technology behavior, reduced motion, contrast, and interaction states where the change affects them.

## Security and privacy

Do not report vulnerabilities in public issues. Follow [SECURITY.md](./SECURITY.md).

Do not commit:

- passwords or authentication secrets;
- API or session tokens;
- private keys;
- production credentials;
- private user information;
- reusable recovery codes;
- secret-bearing environment files.

Use sanitized examples and templates instead.

## Licensing

Follow the license and third-party notices of the repository you are contributing to. Do not assume that a license in one GoreeCloud repository applies to another repository.

If the repository does not clearly state the rights that apply to a contribution or third-party component, resolve that question before introducing material that depends on those rights.
