# Security policy

This is the default security-reporting guidance for GoreeCloud repositories that do not provide a more specific local `SECURITY.md`.

## Reporting a vulnerability

Please do **not** open a public issue, discussion, or pull request for a vulnerability that could expose users, data, credentials, systems, or infrastructure.

Use the target repository's **Security** tab and its private vulnerability-reporting flow when that option is available.

If the repository does not provide a private GitHub reporting flow, use the [official GoreeCloud contact page](https://www.goreecloud.com/contact/) and identify the affected repository. Do not include reusable credentials, private keys, access tokens, private user data, or other secrets unless an explicitly authorized secure channel has been established.

## Helpful report details

When safe to provide, include:

- affected repository and component;
- affected version, release, tag, or commit;
- concise description of the issue;
- security impact;
- reproduction steps or proof of concept;
- prerequisites or required privileges;
- known mitigations or workarounds;
- suggested remediation, if known.

Redact secrets and unrelated private information.

## Supported versions

Support and security-maintenance status is repository-specific. Check the affected repository's release, lifecycle, and support documentation. Do not infer that every historical branch, tag, package, or deployment remains supported.

## Disclosure

Please allow time for triage and remediation before public disclosure. GoreeCloud may coordinate disclosure timing based on the affected repository, severity, available mitigation, release process, and user impact.

Repository-specific security policies override this default when they provide more precise instructions.
