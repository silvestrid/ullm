# CI/CD Setup Guide

## GitHub Actions CI is Already Configured! ✅

Your repository already has GitHub Actions workflows configured. Here's what you have:

### 1. Test Workflow (`.github/workflows/tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does:**
- Runs tests on Ubuntu, macOS, and Windows
- Tests against Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Runs linting, type checking, and tests
- Uploads coverage to Codecov (if configured)

**Status:** Ready to run automatically!

### 2. Publish Workflow (`.github/workflows/publish.yml`)

**Triggers:**
- When you create a GitHub release

**What it does:**
- Builds the package
- Publishes to PyPI

**Status:** Requires `PYPI_API_TOKEN` secret (see setup below)

## How to Enable CI

### Option 1: Push to GitHub (Recommended)

The CI is already enabled! Just push your changes:

```bash
git add .
git commit -m "Replace Makefile with justfile and update docs"
git push origin main
```

Then visit: https://github.com/silvestrid/ullm/actions

You should see your CI workflow running automatically!

### Option 2: Create a Pull Request

```bash
# Create a new branch
git checkout -b feature/justfile-migration

# Commit your changes
git add .
git commit -m "Replace Makefile with justfile"

# Push the branch
git push origin feature/justfile-migration

# Create a PR on GitHub
# CI will run automatically on the PR
```

## Setting Up PyPI Publishing (Optional)

To enable automatic publishing to PyPI when you create a release:

### Step 1: Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Verify your email

### Step 2: Generate API Token
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `github-actions-ullm`
4. Scope: "Entire account" (or specific to ullm once uploaded)
5. Copy the token (starts with `pypi-`)

### Step 3: Add Secret to GitHub
1. Go to https://github.com/silvestrid/ullm/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste your PyPI token
5. Click "Add secret"

### Step 4: Create a Release
```bash
# Update version in pyproject.toml
# Update CHANGELOG.md

# Commit and tag
git add .
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags

# Create release on GitHub
# Go to: https://github.com/silvestrid/ullm/releases/new
# - Select tag: v0.2.0
# - Release title: v0.2.0
# - Click "Publish release"

# The publish workflow will run automatically!
```

## Viewing CI Results

### GitHub Actions Dashboard
Visit: https://github.com/silvestrid/ullm/actions

You'll see:
- ✅ Passed workflows (green checkmark)
- ❌ Failed workflows (red X)
- 🟡 Running workflows (yellow circle)

### Branch Protection (Optional)

To require CI to pass before merging PRs:

1. Go to: https://github.com/silvestrid/ullm/settings/branches
2. Click "Add rule" for `main` branch
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select: `test` (from the Tests workflow)
4. Save changes

## Local CI Simulation

You can run the same checks locally using just:

```bash
# Run all CI checks
just ci

# Or run individual checks
just lint
just type-check
just test-cov
```

## CI Status Badge (Optional)

Add a status badge to your README.md:

```markdown
[![Tests](https://github.com/silvestrid/ullm/actions/workflows/tests.yml/badge.svg)](https://github.com/silvestrid/ullm/actions/workflows/tests.yml)
```

## Troubleshooting

### CI doesn't run after push
- Check that you pushed to `main` or `develop` branch
- Check the Actions tab: https://github.com/silvestrid/ullm/actions
- Ensure Actions are enabled in repository settings

### Tests fail in CI but pass locally
- Check Python version (CI tests 3.8-3.12)
- Check OS (CI tests Ubuntu, macOS, Windows)
- Look at the CI logs for specific errors

### Publishing to PyPI fails
- Verify `PYPI_API_TOKEN` secret is set correctly
- Ensure version number in `pyproject.toml` is unique
- Check PyPI logs in the workflow

## Current Workflow Configuration

### Tests Matrix
- **Operating Systems:** Ubuntu, macOS, Windows
- **Python Versions:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Total Combinations:** 15 test runs per push!

### Tools Used
- **uv** - Package management
- **ruff** - Linting and formatting
- **mypy** - Type checking
- **pytest** - Testing

## Next Steps

1. ✅ Push your changes to trigger CI
2. ✅ Check the Actions tab to see results
3. ⏸️ (Optional) Set up PyPI token for publishing
4. ⏸️ (Optional) Add branch protection rules
5. ⏸️ (Optional) Add CI badge to README

---

**Your CI is ready to go!** 🚀

Just push to `main` and watch the magic happen at:
https://github.com/silvestrid/ullm/actions
