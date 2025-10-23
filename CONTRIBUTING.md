# Contributing to ullm

Thank you for your interest in contributing to ullm!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/silvestrid/ullm.git
   cd ullm
   ```

2. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

## Code Style

We use modern Python tooling for code quality:

- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

### Running checks

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy ullm

# Run tests
pytest

# Run tests with coverage
pytest --cov=ullm --cov-report=html
```

## Testing

### Unit Tests

Write unit tests for all new functionality:

```python
# tests/test_feature.py
def test_new_feature():
    result = new_feature()
    assert result == expected
```

### Integration Tests

Integration tests that require API keys are automatically skipped if keys are not present:

```python
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_integration():
    # Test code
```

## Adding a New Provider

To add a new LLM provider:

1. **Create client class** in `ullm/clients/new_provider.py`
   ```python
   from ullm.clients.base import BaseClient

   class NewProviderClient(BaseClient):
       def _get_api_key_from_env(self):
           return os.getenv("NEW_PROVIDER_API_KEY")

       def _get_default_api_base(self):
           return "https://api.newprovider.com/v1"

       # Implement completion() and acompletion()
   ```

2. **Register provider** in `ullm/providers.py`
   ```python
   SUPPORTED_PROVIDERS = [..., "new_provider"]
   ```

3. **Add to client factory** in `ullm/main.py`
   ```python
   def _get_client(provider: str, **kwargs):
       # ... existing code ...
       elif provider == "new_provider":
           return NewProviderClient(**kwargs)
   ```

4. **Write tests** in `tests/test_new_provider.py`

5. **Update documentation** in `README.md`

## Pull Request Process

1. **Fork the repository** and create a new branch
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** following the code style

3. **Add tests** for new functionality

4. **Run all checks**
   ```bash
   ruff format .
   ruff check .
   mypy ullm
   pytest
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/my-feature
   ```

7. **Open a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable

## Project Goals

Remember that ullm aims to be:

- **Lightweight**: Minimal dependencies, small footprint
- **Fast**: Quick imports, efficient execution
- **Compatible**: API-compatible with litellm where possible
- **Focused**: Core providers only (OpenAI, Anthropic, Groq, Bedrock)

When adding features, consider whether they align with these goals.

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about contributing
- General discussion

Thank you for contributing!
