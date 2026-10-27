# Security Policy

DrowsyAlert is a research prototype. It is not a certified road-safety device, a medical
device, or a substitute for safe driving practices.

## Supported versions

Security fixes are applied to the latest code on `main`. Older commits, experiment
branches, local checkpoints, and unpublished builds are not separately supported.

| Version | Supported |
|---|---|
| Latest `main` / latest release | Yes |
| Older versions and branches | No |

## Reporting a vulnerability

Do not disclose a suspected vulnerability, credential, private path, participant record,
or restricted dataset in a public issue.

Use the repository's **Security** tab and select **Report a vulnerability** to submit a
private report. If private reporting is unavailable, contact the project owner,
[@khanv02](https://github.com/khanv02), and request a private channel before sharing
details.

Include, when safe:

- the affected version or commit;
- the affected component and configuration;
- reproducible steps or a minimal proof of concept;
- expected impact and known mitigations;
- whether private data, model files, or credentials may be exposed.

Remove real secrets, personal data, face images, and restricted dataset content. Use
synthetic or redacted examples whenever possible.

The maintainer will acknowledge a complete report as soon as practical, normally within
seven days, then coordinate validation, remediation, and disclosure. Please allow time for
a fix before public discussion.

## Security boundaries

- Webcam and video processing is local by default.
- Raw frames are not stored by the standard runtime flow.
- Dataset, model, output, and credential paths are excluded from Git.
- Experimental accuracy is not a safety guarantee.
