# Repository instructions

## Project overview

- DrowsyAlert is a Python research prototype for driver-drowsiness signals, not a certified safety device or medical diagnostic tool.
- Keep claims about accuracy scoped to the dataset and task actually evaluated. CEW metrics describe eye-image classification, not video-based drowsiness detection or road safety.
- Follow the project constitution in `.specify/memory/constitution.md` and the applicable feature specification, plan, and tasks under `specs/`.

## Working rules

- Inspect the relevant source, tests, and documentation before changing behavior. Make focused changes and preserve established project conventions.
- Do not commit datasets, participant data, downloaded models, checkpoints, generated experiment results, credentials, or other local artifacts. Keep raw video out of Git; collection of volunteer data requires consent and institutional guidance.
- Treat `repomix-output*.xml` as a read-only snapshot for repository discovery. Make all edits in the original files, never in the packed snapshot.
- Keep the English and Vietnamese root README files aligned when changing shared project information.
- Update documentation when behavior, setup, project status, or user-facing workflows change.
- Do not commit or push unless the user explicitly asks.

## Validation

- Use the narrowest relevant checks first. The standard project checks are `uv run ruff check src scripts demo tests` and `uv run pytest`.
- Run checks when requested or when needed to verify a code change; report any checks not run and why.
- Passing automated checks does not establish real-world accuracy. Webcam and audio acceptance require physical devices and must be reported separately.

## Completion report

When the requested work is complete, respond concisely with:

- What changed, including clickable file paths when applicable.
- Checks run and their results, or state that no checks were run.
- Any remaining limitation or follow-up that materially affects use.

If a commit or push was explicitly requested and completed, include the commit hash and destination branch. Never imply that work was committed, pushed, tested, or hardware-verified unless it was.
