# ullm Documentation

This directory contains the source for ullm's documentation, built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## 📚 Live Documentation

**https://silvestrid.github.io/ullm/**

The documentation is automatically deployed to GitHub Pages on every push to main.

## Local Development

### Install Dependencies

```bash
pip install ullm[docs]
# or
uv pip install -e ".[docs]"
```

### Serve Locally

```bash
# Using just
just docs-serve

# Or directly
mkdocs serve
```

Visit http://localhost:8000 to view.

### Build

```bash
# Using just
just docs-build

# Or directly
mkdocs build
```

Output goes to `site/` directory.

## Documentation Structure

```
docs/
├── index.md                    # Home page
├── getting-started/            # Getting started guides
│   ├── installation.md
│   ├── quickstart.md
│   └── basic-usage.md
├── guide/                      # User guides
│   ├── overview.md
│   ├── providers.md
│   ├── streaming.md
│   ├── tool-calling.md
│   ├── structured-output.md
│   ├── error-handling.md
│   └── dspy-integration.md
├── api/                        # API reference
│   ├── completion.md
│   ├── responses.md
│   ├── types.md
│   └── exceptions.md
├── architecture/               # Architecture docs
│   ├── decisions.md            # ADRs
│   ├── registry.md
│   └── providers.md
├── development/                # Development guides
│   ├── contributing.md
│   ├── setup.md
│   ├── releases.md
│   └── testing.md
└── changelog.md                # Changelog
```

## Configuration

Documentation configuration is in `mkdocs.yml` at the project root.

Key features enabled:
- Material theme with dark/light mode
- Search functionality
- Code highlighting
- Tabbed content
- Admonitions (notes, warnings, etc.)
- Auto-generated API docs via mkdocstrings
- Mobile-responsive design

## Writing Documentation

### Markdown Features

We use [Python-Markdown](https://python-markdown.github.io/) with these extensions:

#### Code Blocks

\`\`\`python
import ullm

response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...]
)
\`\`\`

#### Admonitions

```markdown
!!! note
    This is a note.

!!! warning
    This is a warning.

!!! tip
    This is a tip.
```

#### Tabbed Content

```markdown
=== "Python"
    \`\`\`python
    import ullm
    \`\`\`

=== "Async"
    \`\`\`python
    import asyncio
    \`\`\`
```

#### API Documentation

Auto-generate from docstrings:

```markdown
::: ullm.completion
```

### Adding a New Page

1. Create markdown file in appropriate directory
2. Add to navigation in `mkdocs.yml`:

```yaml
nav:
  - New Section:
    - Title: path/to/file.md
```

3. Test locally with `just docs-serve`
4. Commit and push - auto-deploys to GitHub Pages

## Deployment

### Automatic (Recommended)

Push to main branch triggers `.github/workflows/docs.yml`:
- Builds documentation
- Deploys to `gh-pages` branch
- Live at https://silvestrid.github.io/ullm/

### Manual

```bash
# Using just
just docs-deploy

# Or directly
mkdocs gh-deploy
```

## Troubleshooting

### Build Fails

```bash
# Check for errors
mkdocs build

# Common issues:
# - Missing pages in nav
# - Invalid markdown syntax
# - Broken internal links
```

### Deployment Fails

Check GitHub Actions logs:
https://github.com/silvestrid/ullm/actions

Common issues:
- GitHub Pages not enabled in repository settings
- Permissions issue (workflow needs `contents: write`)

### Navigation Not Updating

The navigation structure is defined in `mkdocs.yml` under the `nav:` section. Changes require updating this file.

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Python-Markdown](https://python-markdown.github.io/)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.

For documentation-specific contributions:

1. **Fix typos/errors**: Edit the markdown file directly
2. **Add examples**: Add to relevant guide pages
3. **New features**: Document in appropriate section + update API reference
4. **Breaking changes**: Update migration guide and changelog

All documentation changes should be submitted via pull request.
