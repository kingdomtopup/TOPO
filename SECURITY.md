# Security Policy

## Supported Versions

The following versions of khqr-payment are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

We recommend always using the latest version of the library.

---

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Email**: Send an email to [earhengly@gmail.com](mailto:earhengly@gmail.com) with the subject line: "SECURITY: khqr-payment vulnerability"

2. **GitHub Security Advisories**: Use [GitHub's private vulnerability reporting](https://github.com/henglyrepo/khqr-payment/security/advisories/new) feature

### What to Include

When reporting a vulnerability, please include:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact assessment of the vulnerability

---

## Response Timeline

We aim to acknowledge security reports within **48 hours** and provide a more detailed response within **7 days**.

| Timeline | Action |
|----------|--------|
| 48 hours | Acknowledge report |
| 7 days | Initial response with findings and planned fix |
| 30 days | Publish security update (if applicable) |

---

## Security Best Practices

When using khqr-payment in your application, please follow these security practices:

### 1. Token Security

- **Never** hardcode your API token in source code
- Use environment variables or secure secret management:
  ```python
  import os
  token = os.environ.get("BAKONG_TOKEN")
  ```
- **Never** commit tokens to version control
- Rotate tokens periodically

### 2. Webhook Verification

Always verify webhook signatures before processing payment notifications:

```python
from khqr_payment import verify_webhook_signature

def handle_webhook(payload: bytes, signature: str):
    verify_webhook_signature(
        payload=payload,
        signature=signature,
        secret_key="your_webhook_secret"
    )
    # Process payment...
```

### 3. HTTPS Only

Always use HTTPS for:
- Production environments
- Callback URLs
- Webhook endpoints

### 4. Input Validation

The library performs input validation, but always validate:
- User-provided amounts
- Currency codes
- Bank account formats

### 5. Error Handling

Don't expose sensitive information in error messages:

```python
try:
    client = KHQRClient(token)
except Exception as e:
    # Log the error internally
    logger.error(f"Failed to initialize client: {e}")
    # Show generic message to user
    raise ValueError("Failed to initialize payment client")
```

---

## Security Updates

Security updates will be released as patch versions and announced through:

- GitHub Releases
- PyPI release notifications
- GitHub Security Advisories

---

## Attribution

Thank you to all security researchers and contributors who help keep khqr-payment secure!

---

*Last updated: February 2026*
