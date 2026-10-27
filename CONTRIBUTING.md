# Contributing to DrowsyAlert

Thank you for helping improve DrowsyAlert. This repository is a research prototype, not a
certified road-safety or medical system. Contributions must preserve that distinction and
must not overstate experimental results.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Before starting

1. Search existing issues and the canonical task list in
   [`specs/001-drowsyalert/tasks.md`](specs/001-drowsyalert/tasks.md).
2. Open an issue for a bug, feature, dataset concern, or change that affects behavior,
   research protocol, dependencies, or multiple modules.
3. Keep each branch and pull request focused on one small task.

Documentation-only typo fixes may be submitted directly as a focused pull request.

## Development setup

Install Python 3.12 and [uv](https://docs.astral.sh/uv/), then run:

```powershell
git clone https://github.com/khanv02/driver-drowsiness-detection.git
cd driver-drowsiness-detection
uv sync --locked --extra train
```

Create a branch from the current target branch. Use a descriptive name such as
`task/T-123-short-description`, `fix/short-description`, or `docs/short-description`.

## Making changes

- Keep reusable code under `src/drowsyalert/`; keep command wrappers under `scripts/`.
- Add or update focused tests for changed behavior, including boundary and invalid input.
- Preserve `UNKNOWN` for missing or invalid evidence; do not silently convert it to a
  normal/open observation.
- Keep display, audio, and logging side effects separate from algorithmic decisions.
- Update specifications, documentation, and configuration examples when their contracts
  change.
- Do not change a frozen evaluation split or held-out result without an explicit protocol
  revision and review.

See [`docs/project/development-conventions.md`](docs/project/development-conventions.md)
for the complete repository conventions.

## Data, models, privacy, and security

Never commit:

- downloaded or derived datasets;
- participant recordings or identifying metadata;
- model checkpoints or third-party model assets;
- generated experiment outputs;
- credentials, tokens, machine-specific paths, or private logs.

Use the ignored `data/`, `models/`, and `outputs/` locations described by their README
files. Confirm dataset provenance, terms, consent, labels, and leakage controls before use.
Redact paths, faces, identifiers, and secrets from issue and pull-request evidence.

Report security vulnerabilities using [SECURITY.md](SECURITY.md), not a public issue.

## Verification

Run the checks that match CI before requesting review:

```powershell
uv run ruff check src scripts demo tests
uv run python -m pytest -p no:cacheprovider
uv build
```

Hardware-dependent webcam and audio checks must be reported separately. Do not describe a
skipped manual check as passed.

## Pull requests

- Link the relevant issue or task.
- Explain what changed, why it changed, and what remains out of scope.
- Include reproducible verification commands and results.
- Call out dataset, model, protocol, privacy, or user-facing changes.
- Keep the worktree free of generated artifacts and private data.
- Wait for CI and review before merging.
