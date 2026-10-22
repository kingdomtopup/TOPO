# Contributing to khqr-payment

Thank you for your interest in contributing to khqr-payment!

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and inclusive.

---

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/khqr-payment.git`
3. **Create** a feature branch: `git checkout -b feature/your-feature-name`

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Step 1: Create Virtual Environment

```bash
# Create a new folder (optional)
mkdir khqr-payment-dev
cd khqr-payment-dev

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install the package with dev dependencies
pip install -e ".[dev]"

# Or install individually
pip install -e .
pip install pytest pytest-asyncio pytest-cov ruff mypy
```

### Step 3: Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```

---

## Code Style

This project follows strict code style guidelines:

### Formatting Rules

- **Line length**: 100 characters (configured in pyproject.toml)
- **Indentation**: 4 spaces
- **Trailing commas**: Use for multi-line calls

### Type Hints

- **ALL** function parameters and return types MUST have type hints
- Use Python 3.10+ union syntax (`X | None`) NOT `Optional[X]`
- Use `Literal` for enum-like string constants

```python
# Good
def create_qr(merchant: str, amount: float | None, currency: str) -> QRCode:
    ...

# Bad
def create_qr(merchant, amount, currency):
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `KHQRClient` |
| Functions/methods | snake_case | `create_qr` |
| Variables | snake_case | `qr_string` |
| Constants | UPPER_SNAKE_CASE | `BASE_URL` |
| Private methods | Prefix with underscore | `_validate_request` |

### Imports

- Use absolute imports from package root
- Group: standard library, third-party, local
- Sort alphabetically within groups

```python
# Standard library
import time
from typing import Literal

# Third-party
from pydantic import BaseModel

# Local
from khqr_payment.errors import KHQRPaymentError
```

### Docstrings

Add docstrings to all public methods using Google-style:

```python
def create_qr_string(
    self,
    merchant: str,
    merchant_name: str,
    merchant_city: str,
    amount: float | None = None,
    currency: str = "USD",
    static: bool = False,
) -> QRCode:
    """Create a KHQR string for payment.

    Args:
        merchant: Bank account ID (e.g., "shop@bank")
        merchant_name: Name displayed to customer (max 25 chars)
        merchant_city: City name (max 40 chars)
        amount: Payment amount (None for static QR)
        currency: Currency code (USD or KHR)
        static: Whether to create a static QR (default: False)

    Returns:
        QRCode object containing the QR string and metadata

    Raises:
        ValidationError: If input parameters are invalid
        NetworkError: If unable to connect to Bakong API
    """
    ...
```

### Pydantic Models

```python
class Merchant(BaseModel):
    bank_account: str = Field(..., description="Bank account ID")
    name: str = Field(..., min_length=1, max_length=25)
    city: str = Field(..., min_length=1, max_length=40)
    model_config = {"str_strip_whitespace": True}
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestKHQRClient::test_create_qr

# Run tests matching pattern
pytest -k "test_create"

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Writing Tests

- Use `pytest` with `pytest-asyncio` for async tests
- Use `unittest.mock` for mocking
- Group tests in classes by functionality
- Use descriptive names: `test_<method>_<expected_behavior>`

```python
class TestKHQRClient:
    def test_create_qr_with_valid_merchant(self):
        ...

    def test_create_qr_with_invalid_amount_raises_error(self):
        ...

@pytest.mark.asyncio
class TestAsyncKHQRClient:
    async def test_async_create_qr(self):
        ...
```

---

## Pull Request Guidelines

1. **Before submitting:**
   - Run `ruff check src/` to lint your code
   - Run `ruff format src/` to format code
   - Run `mypy src/` to type check
   - Run `pytest` to ensure all tests pass

2. **PR Description should include:**
   - Clear description of the changes
   - Related issue number (if applicable)
   - Testing done

3. **PR Checklist:**
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated for new features
   - [ ] Documentation updated (if needed)
   - [ ] All tests pass
   - [ ] No linting/type errors

---

## Commit Message Guidelines

Follow [Conventional Commits](https://www.commitizen.com/conventional-commits) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, no logic) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, dependencies |

### Examples

```
feat: add AsyncKHQRClient for async operations
fix: correct QR generation to match Bakong specification
docs: add quick start guide to README
chore: update pyproject.toml with new author info
```

---

## Questions?

If you have any questions, feel free to open an issue or reach out to the maintainers.

Thank you for contributing!
