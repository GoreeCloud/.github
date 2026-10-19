# Contributing to GoreeCloud

Thank you for helping improve GoreeCloud. This file provides default contribution guidance for repositories that do not define a more specific local process.

## Before you start

1. Read the target repository's `README.md`, contribution guidance, specifications, and development documentation when present.
2. Check existing issues and pull requests before starting duplicate work.
3. Keep the change focused on one coherent purpose.
4. Do not include credentials, secrets, private user data, internal-only infrastructure details, or other sensitive material.

Repository-local instructions may add more specific requirements, but must not override the GoreeCloud-wide GC UI mandate or reinstate prohibited Glaze/Glaze UI design dependencies.

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

**Mandatory, effective October 19, 2026:** Every GoreeCloud-controlled application, website, icon, operating system, interface, and other designed asset or presentation layer **must be built and designed based on [GoreeCloud/gc-ui](https://github.com/GoreeCloud/gc-ui)**. Glaze and Glaze UI are **permanently banned as active GoreeCloud design and development systems**; do not introduce, extend, or maintain them as future design authorities or dependencies. Existing usage requires a planned, verified migration, not cosmetic renaming or copying. Maintain official brand-asset provenance in [GoreeCloud/branding-assets](https://github.com/GoreeCloud/branding-assets) where applicable.

UI changes must document the applicable GC UI design tokens, components, icons, interaction patterns, and host-platform adaptations, and validate relevant responsive states, keyboard and assistive-technology behavior, reduced motion, contrast, and interaction states. Renamed imports alone do not establish conformance. Legacy migration and retirement status require evidence; see [GC UI succession and cutover policy](https://github.com/GoreeCloud/gc-ui/blob/main/docs/DESIGN_SYSTEM_SUCCESSION.md).

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
