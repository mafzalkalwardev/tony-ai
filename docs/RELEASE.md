# Release Process

Tony AI uses simple semantic versioning.

Current version is stored in:

```text
VERSION
```

## Release Checklist

1. Run tests.
2. Run health check.
3. Run command and voice transcript simulations.
4. Generate assets/screenshots if needed.
5. Update README and docs.
6. Update CHANGELOG.
7. Prepare release notes.
8. Ask Muhammad Afzal before committing, tagging, pushing, or publishing.

## Commands

```powershell
python -m pytest tests
python scripts/health_check.py
python scripts/test_tony_commands.py
python scripts/test_voice_transcripts.py
python scripts/prepare_release.py
python scripts/prepare_pr_summary.py
```

## GitHub Release

Do not run these without approval:

```powershell
git commit -m "release: prepare Tony AI v1.0.0"
git tag v1.0.0
git push
git push origin v1.0.0
gh release create v1.0.0
```

## Packaging Notes

Packaging is not automated yet. Future work can add PyInstaller or MSIX packaging after the test suite and safety system remain stable.
