# Release Process

This guide explains how to release new versions of ullm.

## Overview

ullm uses GitHub Releases and GitHub Actions for automated publishing to PyPI. The process is designed to be simple and safe.

## Prerequisites

### One-Time Setup

1. **PyPI Account**
   - Create account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
   - Verify your email

2. **PyPI API Token**
   - Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - Click "Add API token"
   - Name: `github-actions-ullm`
   - Scope: "Entire account" (or specific to ullm after first upload)
   - Copy the token (starts with `pypi-`)

3. **Add Secret to GitHub**
   - Go to [https://github.com/silvestrid/ullm/settings/secrets/actions](https://github.com/silvestrid/ullm/settings/secrets/actions)
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your PyPI token
   - Click "Add secret"

## Release Checklist

### 1. Pre-Release Checks

- [ ] All tests passing on main branch
- [ ] Documentation is up to date
- [ ] CHANGELOG.md updated with new version
- [ ] No uncommitted changes

```bash
# Verify tests pass
just test

# Verify linting passes
just lint

# Verify you're on main and up to date
git checkout main
git pull origin main
git status
```

### 2. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
name = "ullm"
version = "0.2.0"  # ← Update this
```

### 3. Update Changelog

Add release notes to `CHANGELOG.md`:

```markdown
## [0.2.0] - 2025-01-15

### Added
- New feature X
- Support for Y

### Changed
- Improved Z performance

### Fixed
- Bug in A
- Issue with B
```

### 4. Commit and Tag

```bash
# Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"

# Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0"

# Push commit and tags
git push origin main
git push origin v0.2.0
```

### 5. Create GitHub Release

1. Go to [https://github.com/silvestrid/ullm/releases/new](https://github.com/silvestrid/ullm/releases/new)
2. Select tag: `v0.2.0`
3. Release title: `v0.2.0`
4. Description: Copy from CHANGELOG.md
5. Check "Set as latest release"
6. Click "Publish release"

**That's it!** GitHub Actions will automatically:
- Build the package
- Publish to PyPI
- Update documentation (if configured)

### 6. Verify Release

Wait a few minutes, then verify:

1. **Check GitHub Actions**
   - Go to [https://github.com/silvestrid/ullm/actions](https://github.com/silvestrid/ullm/actions)
   - Verify "Publish to PyPI" workflow succeeded

2. **Check PyPI**
   - Go to [https://pypi.org/project/ullm/](https://pypi.org/project/ullm/)
   - Verify new version is live

3. **Test Installation**
   ```bash
   pip install ullm==0.2.0
   python -c "import ullm; print(ullm.__version__)"
   ```

## Version Numbering

ullm follows [Semantic Versioning](https://semver.org/):

### Format: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes, backwards compatible

### Examples

```
0.1.0 → 0.1.1   # Bug fix
0.1.1 → 0.2.0   # New feature
0.2.0 → 1.0.0   # Breaking change
```

### When to Bump

**Patch (0.0.X)**: Bug fixes only
- Fixing a bug
- Documentation updates
- Performance improvements (no API changes)

**Minor (0.X.0)**: New features, backwards compatible
- Adding new provider
- Adding new optional parameters
- Adding new exception types
- Deprecating features (with warnings)

**Major (X.0.0)**: Breaking changes
- Removing public API
- Changing function signatures
- Removing providers
- Changing exception hierarchy

## Hotfix Releases

For urgent bug fixes:

```bash
# Create hotfix branch from latest release tag
git checkout -b hotfix/0.1.1 v0.1.0

# Make fixes
git add .
git commit -m "fix: critical bug"

# Update version to 0.1.1
# Update CHANGELOG.md

# Commit, tag, and push
git commit -am "chore: bump version to 0.1.1"
git tag -a v0.1.1 -m "Hotfix v0.1.1"
git push origin hotfix/0.1.1
git push origin v0.1.1

# Create GitHub Release
# Merge back to main
git checkout main
git merge hotfix/0.1.1
git push origin main
```

## Rolling Back a Release

If a release has critical issues:

### Option 1: Yank from PyPI

```bash
# Install twine
pip install twine

# Yank the version (makes it unavailable but keeps record)
twine yank ullm==0.2.0 -r pypi
```

### Option 2: Release a Fixed Version

```bash
# Fix the issue
# Bump to 0.2.1
# Follow normal release process
```

!!! warning "Don't Delete Releases"
    Don't delete releases from PyPI or GitHub. Use yank or release a fix instead.

## Pre-releases

For beta/RC releases:

```toml
# pyproject.toml
version = "0.2.0b1"  # or 0.2.0rc1
```

```bash
git tag -a v0.2.0b1 -m "Beta release v0.2.0b1"
git push origin v0.2.0b1
```

Mark as "pre-release" when creating GitHub Release.

## Release Automation

The `.github/workflows/publish.yml` workflow:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install uv
      uses: astral-sh/setup-uv@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Build package
      run: uv build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Troubleshooting

### Build Fails

**Issue**: Package build fails

**Solution**:
```bash
# Build locally first
uv build

# Check for issues
ls dist/
```

### PyPI Upload Fails

**Issue**: Authentication error

**Solution**:
- Verify `PYPI_API_TOKEN` secret is set correctly
- Check token hasn't expired
- Ensure token has correct permissions

**Issue**: Version already exists

**Solution**:
- PyPI doesn't allow re-uploading same version
- Bump version and release again
- If testing, use TestPyPI first

### Wrong Version Number

**Issue**: Released wrong version number

**Solution**:
- Can't change PyPI version after upload
- Release a new version with correct number
- Update documentation to skip wrong version

## Best Practices

1. ✅ **Test Before Release**
   - Run full test suite
   - Test installation in clean environment
   - Try examples

2. ✅ **Update Documentation**
   - Update CHANGELOG.md
   - Update version in docs
   - Add migration notes if breaking

3. ✅ **Use Annotated Tags**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"  # Good
   git tag v0.2.0                          # Bad
   ```

4. ✅ **Write Good Release Notes**
   - Explain what changed and why
   - Include migration instructions
   - Credit contributors

5. ✅ **Test the Release**
   - Install from PyPI
   - Run smoke tests
   - Check documentation links

## Release Schedule

ullm doesn't have a fixed release schedule. Releases happen when:

- **Patch**: As needed for bug fixes
- **Minor**: When new features are ready
- **Major**: Only when breaking changes are necessary

Typical cadence: 1-2 months between minor releases.

## Communication

After releasing:

1. **Announce on GitHub**
   - Release notes automatically notify watchers

2. **Update Documentation**
   - Documentation site updates automatically

3. **Community**
   - Share on relevant channels if major release
   - Respond to feedback and issues

## Questions?

- See [Contributing Guide](contributing.md) for development workflow
- Open an issue for release process questions
- Check GitHub Actions logs for build/publish issues
