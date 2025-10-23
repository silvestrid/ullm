# Installation

## Requirements

- Python 3.8 or higher
- pip or uv

## Basic Installation

Install ullm using pip:

```bash
pip install ullm
```

Or using uv (faster):

```bash
uv pip install ullm
```

## Optional Dependencies

### AWS Bedrock Support

If you need AWS Bedrock support, install with the `aws` extra:

```bash
pip install ullm[aws]
```

This installs `boto3` which is required for AWS Bedrock integration.

### Development Installation

For development, install with dev dependencies:

```bash
pip install ullm[dev]
```

This includes:
- pytest (testing)
- ruff (linting and formatting)
- mypy (type checking)
- pytest-asyncio (async testing)
- pytest-cov (coverage)

### Documentation

To build the documentation locally:

```bash
pip install ullm[docs]
```

### All Optional Dependencies

To install everything:

```bash
pip install ullm[aws,dev,docs]
```

## From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/silvestrid/ullm.git
cd ullm
pip install -e ".[dev]"
```

## Verify Installation

Verify your installation:

```python
import ullm

print(f"ullm version: {ullm.__version__}")
print(f"Available functions: {dir(ullm)}")
```

## API Keys

ullm reads API keys from environment variables:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Groq
export GROQ_API_KEY=gsk_...

# AWS Bedrock (uses standard AWS credentials)
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION_NAME=us-east-1
```

Or pass them directly:

```python
import ullm

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hi"}],
    api_key="sk-..."
)
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started in 5 minutes
- [Basic Usage](basic-usage.md) - Learn the fundamentals
- [User Guide](../guide/overview.md) - Explore all features
