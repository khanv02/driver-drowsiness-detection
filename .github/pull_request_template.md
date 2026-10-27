## Summary

<!-- Explain what changed and why. Keep the pull request focused. -->

## Related work

<!-- Link the issue or task, for example: Closes #123 or T-123. -->

## Change type

- [ ] Bug fix
- [ ] Feature
- [ ] Data, annotation, or evaluation tooling
- [ ] Documentation
- [ ] Refactor or maintenance

## Validation

<!-- List exact commands and results. Separate automated checks from manual hardware checks. -->

```text
uv run ruff check src scripts demo tests
uv run python -m pytest -p no:cacheprovider
uv build
```

## Research and privacy impact

<!-- Describe effects on datasets, models, splits, metrics, protocols, webcam/audio, or privacy. Write "None" when not applicable. -->

## Checklist

- [ ] The change is scoped to one issue or task.
- [ ] Tests and documentation were added or updated where needed.
- [ ] CI-relevant checks pass, or failures are explained above.
- [ ] No credentials, private media, participant data, restricted datasets, checkpoints, or generated outputs are included.
- [ ] Reported results are traceable and are not presented as certified safety or medical claims.
- [ ] Skipped webcam/audio checks are not reported as passed.

