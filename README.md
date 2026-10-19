# GoreeCloud GitHub defaults

This repository contains the public, account-wide GitHub community-health defaults for GoreeCloud.

GitHub repositories that do not provide a more specific local equivalent may use the files here for contribution guidance, security reporting, support routing, issue intake, and pull-request structure. Repository-local requirements remain authoritative for repository-specific behavior.

## What belongs here

- `CONTRIBUTING.md` — default contribution workflow and quality expectations.
- `SECURITY.md` — default vulnerability-reporting guidance.
- `SUPPORT.md` — default support and help routing.
- `CODE_OF_CONDUCT.md` — baseline conduct expectations for public collaboration.
- `.github/PULL_REQUEST_TEMPLATE.md` — default pull-request structure.
- `.github/ISSUE_TEMPLATE/` — default structured issue forms.

## GoreeCloud-wide design-system requirement

**Effective October 19, 2026:** Every GoreeCloud application, website, icon, operating system and other designed user-facing product must use [GoreeCloud UI (GC UI)](https://github.com/GoreeCloud/gc-ui) as its authoritative design foundation. **Glaze and Glaze UI are permanently banned as active design and development systems.** Legacy implementations require verified migration; policy effect does not prove rollout completion. See [GC UI succession and conformance](https://github.com/GoreeCloud/gc-ui/blob/main/docs/DESIGN_SYSTEM_SUCCESSION.md).

**Platform classification:** GC UI is **Integral Platform System #5 of GoreeCloud's nine systems**, replacing the former Glaze UI system; this is not a tenth system. GC UI governs the shared experience domain while each other system retains authority over its own capabilities. See the [versioned GC UI classification](https://github.com/GoreeCloud/gc-ui/blob/main/docs/DESIGN_SYSTEM_SUCCESSION.md#goreecloud-ui-as-an-integral-platform-system).

## Scope and authority

This repository is a public GitHub configuration and community-health repository. It is not the canonical home for private GoreeCloud governance, credentials, operational records, production secrets, or project-specific implementation state.

A repository may provide its own local files when its product, security boundary, development model, upstream obligations, support model, or contribution process requires more specific guidance.

## Security

Do not publish vulnerabilities, credentials, private data, tokens, internal-only infrastructure details, or other sensitive information in public issues or pull requests. Follow [SECURITY.md](./SECURITY.md) for private security-reporting guidance.

## GoreeCloud

- [GoreeCloud on GitHub](https://github.com/GoreeCloud)
- [Official website](https://www.goreecloud.com)
