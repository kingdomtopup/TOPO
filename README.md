# khqr-payment

[![PyPI](https://img.shields.io/pypi/v/khqr-payment.svg)](https://pypi.org/project/khqr-payment/)
[![Python](https://img.shields.io/pypi/pyversions/khqr-payment)](https://pypi.org/project/khqr-payment/)
[![License](https://img.shields.io/pypi/l/khqr-payment)](https://github.com/henglyrepo/khqr-payment/blob/main/LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-Buy%20Me%20a%20Coffee-orange)](https://buymeacoffee.com/hengly)

## Project Website

Open `index.html` in a browser to view the static project website and local-only KHQR configuration demo. The demo only prepares a Python example; it does not generate a scannable payment QR, call an API, or process payment information. Never put a Bakong API token in browser code.

---

> **Disclaimer**: This is an **unofficial, open-source library** and is **not affiliated with, endorsed by, or connected to Bakong, the National Bank of Cambodia, or any participating banks**.
>
> **Use at your own risk:**
> - The developer assumes **no responsibility** for any damage, loss, corruption, or financial issues arising from the use of this library
> - **Verify all payments** through official Bakong channels
> - **Review the source code** before using in production
> - **Test thoroughly** in sandbox/SIT environment before using with real money
> - Comply with your bank's terms of service

---

## What is Bakong KHQR?

Bakong is Cambodia's national QR payment system. KHQR is the technical standard that lets your app accept payments from any Cambodian bank or e-wallet app.

Think of it like this:
- Your app generates a QR code
- Customer scans it with their banking app
- Money moves from their account to yours
- You verify the payment was successful

---

## Before You Start

### What You'll Need

1. **Python 3.10 or higher** - [Download here](https://www.python.org/downloads/)
2. **Bakong API Token** - Get this from your bank (see below)
3. **A code editor** - VS Code, PyCharm, or any text editor

### How to Get Your Bakong API Token

1. Contact your bank and ask for Bakong API access
2. They will give you a **token** (a long string of characters)
3. This token authenticates your requests to Bakong
4. **Keep it secret!** Don't share it in public code

> **Note:** For testing, you can use the Sandbox/SIT environment (set `use_sit=True`) - this doesn't use real money.

---

## Installation

### Step 1: Check Your Python Version

Open terminal/command prompt and run:

```bash
python --version
```

You should see something like `Python 3.10.13` or `Python 3.11.x`. If not, [install Python](https://www.python.org/downloads/).

### Step 2: Create a Virtual Environment (Recommended)

A virtual environment keeps your project isolated from other Python projects.

```bash
# Create a new folder for your project
mkdir my-payment-app
cd my-payment-app

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` at the start of your command line.

### Step 3: Install the Library

```bash
pip install khqr-payment
```

### Step 4: Verify It Works

```bash
python -c "import khqr_payment; print('Installation successful!')"
```

If you see "Installation successful!", you're good to go!

---

## Quick Start

### Minimal Example (5 Steps)

```python
from khqr_payment import KHQRClient, Merchant

# 1. Initialize client with your token
client = KHQRClient("your_bakong_token_here")

# 2. Validate token before proceeding
if client.validate_token():
    print("Token is valid and working!")
else:
    print("Token is invalid or expired!")
    client.close()
    exit(1)

# 3. Create merchant information
merchant = Merchant(
    bank_account="yourname@bank",     # Your Bakong account ID
    name="Your Store Name",           # Max 25 characters
    city="Phnom Penh",                # Your city
    store_label="Store Category",     # Optional: e.g., "Coffee Shop"
    phone_number="85512345678",       # Optional: phone number
    acquiring_bank="BANK_NAME",       # Optional: acquiring bank name
)

# 4. Create QR code for payment
qr = client.create_qr_string(
    merchant="yourname@bank",         # Bank account
    merchant_name="Your Store Name",  # Name shown to customer
    merchant_city="Phnom Penh",
    amount=100.00,                   # Payment amount
    currency="USD",                   # USD or KHR
    store_label="Store Category",
    phone_number="85512345678",
    bill_number="TRX12345678",        # Optional: transaction reference
    terminal_label="Cashier-01",      # Optional: terminal ID
    static=False,                     # False = Dynamic QR, True = Static QR
)

# 5. Show QR to customer (they scan it to pay)
print(f"QR String: {qr.string}")
print(f"MD5 Hash: {qr.md5}")  # Use this to verify payment later

# 6. Close connection when done
client.close()
```

---

## Understanding the Code

### What is `Merchant`?

Merchant represents your business/bank account:
```python
merchant = Merchant(
    bank_account="yourname@bank",     # Your Bakong ID (like email)
    name="Store Name",                 # Max 25 chars - shown to customer
    city="Phnom Penh",                 # Max 40 chars
    store_label="Coffee Shop",         # Optional: store category
    phone_number="85512345678",       # Optional: phone number
    bill_number="TRX12345678",        # Optional: bill reference
    terminal_label="Cashier-01",      # Optional: terminal ID
    acquiring_bank="ACLB",            # Optional: acquiring bank name
    static=False,                      # False = Dynamic, True = Static
    language_preference="en",         # Optional: "en" or "kh"
)
```

### What is `QRCode`?

When you call `create_qr_string()`, you get back a QRCode object with:
- `qr.string` - The raw QR data (show this to customer)
- `qr.md5` - A unique hash to check payment status
- `qr.amount` - The payment amount
- `qr.currency` - USD or KHR
- `qr.is_static` - True if static QR, False if dynamic

### What is a Deeplink?

A deeplink is a special URL that opens the customer's banking app directly:
```python
deeplink = client.generate_deeplink(
    qr_string=qr.string,
    callback="https://yoursite.com/payment/done"
)
# Result: bakong://pay?hash=xxxxx
```

---

## Complete Payment Flow

Here's how a typical payment works:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAYMENT FLOW                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. CREATE QR         → Generate QR code for customer           │
│         │                                                       │
│         ▼                                                       │
│  2. SHOW QR           → Display to customer (screen/print)      │
│         │                                                       │
│         ▼                                                       │
│  3. CUSTOMER SCANS    → Customer uses banking app               │
│         │                                                       │
│         ▼                                                       │
│  4. PAYMENT           → Money transferred (async)               │
│         │                                                       │
│         ▼                                                       │
│  5. CHECK STATUS      → Use md5 hash to verify                 │
│         │                                                       │
│         ▼                                                       │
│  6. CONFIRM           → Show "Payment Successful"              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Full Example: Complete Payment

```python
import time
from khqr_payment import KHQRClient, Merchant

# Setup
client = KHQRClient("your_token")

# Validate token first
if not client.validate_token():
    print("Invalid token!")
    client.close()
    exit(1)

# Step 1: Create QR for $50 payment
qr = client.create_qr_string(
    merchant="shop@bank",
    merchant_name="My Shop",
    merchant_city="Phnom Penh",
    amount=50.00,
    currency="USD",
    bill_number="TRX12345678",
    static=False
)

print(f"Show this QR to customer: {qr.string}")
print(f"Payment ID (md5): {qr.md5}")

# Step 2: Wait for customer to pay...
# In real app, you might check in a loop or wait for webhook

# Step 3: Check if customer paid (with retry logic)
for _ in range(10):  # Check every 10 seconds, up to 10 times
    status = client.check_payment(qr.md5)
    
    if status.is_paid:
        print(f"Payment received! Amount: {status.amount}")
        print(f"Status: {status.status}")  # e.g., "paid", "pending"
        break
    else:
        print("Payment not yet received")
        time.sleep(10)

client.close()
```

---

## Static vs Dynamic QR

### Dynamic QR (Most Common)
- Has a fixed amount
- One-time use (recommended for security)
- Customer scans and pays exact amount

```python
qr = client.create_qr_string(
    merchant="shop@bank",
    merchant_name="My Shop",
    merchant_city="Phnom Penh",
    amount=100.00,    # Fixed amount
    currency="USD",
    static=False      # Dynamic (default)
)
```

### Static QR
- No fixed amount
- Customer enters amount themselves
- Can be reused (like displaying at store)

```python
qr = client.create_qr_string(
    merchant="shop@bank",
    merchant_name="My Shop",
    merchant_city="Phnom Penh",
    amount=None,      # No amount - customer enters
    static=True       # Static QR
)
```

---

## Async Usage (For High Performance)

If you're building a web server, use the async client for better performance:

```python
import asyncio
from khqr_payment import AsyncKHQRClient

async def process_payment():
    # Use 'async with' to automatically manage connection
    async with AsyncKHQRClient("your_token") as client:
        # Validate token first
        if not await client.validate_token():
            print("Invalid token!")
            return
        
        # Create QR
        qr = await client.create_qr_string(
            merchant="shop@bank",
            merchant_name="My Shop",
            merchant_city="Phnom Penh",
            amount=50.00,
            currency="USD"
        )
        
        # Check payment status
        status = await client.check_payment(qr.md5)
        print(f"Paid: {status.is_paid}")

# Run the async function
asyncio.run(process_payment())
```

---

## Parse QR Code (Read Incoming QR)

When a customer shows you their QR code:

```python
from khqr_payment import KHQRClient

client = KHQRClient("your_token")

# Parse the QR string they give you
parsed = client.parse_qr(qr_string_from_customer)

# Access the information
print(f"Merchant: {parsed.merchant_name}")
print(f"Amount: {parsed.amount}")
print(f"Currency: {parsed.currency}")
print(f"Is Static: {parsed.is_static}")  # True = they enter amount
```

---

## Generate QR Image

Generate QR as an image file:

```python
from khqr_payment import generate_qr_image, save_qr_image

# Generate image bytes (for sending in API response)
image_bytes = generate_qr_image(qr_string)

# Save directly to file
save_qr_image(qr_string, "payment_qr.png")

# Or generate as base64 data URI (for HTML <img> tags)
from khqr_payment import generate_qr_base64_uri
data_uri = generate_qr_base64_uri(qr_string)
# Result: "data:image/png;base64,iVBORw0KGgo..."
```

---

## Webhooks (Server-Side Notifications)

Webhooks notify your server when a payment is made, so you don't have to keep checking:

```python
from khqr_payment import verify_webhook_signature, WebhookHandler

# When you receive a webhook from Bakong:
def handle_webhook(payload: bytes, signature: str):
    # Step 1: Verify it's really from Bakong
    verify_webhook_signature(
        payload=payload,
        signature=signature,
        secret_key="your_webhook_secret"
    )
    
    # Step 2: Parse the payment data
    handler = WebhookHandler("your_webhook_secret")
    payment = handler.handle_payment_webhook(payload)
    
    print(f"Payment received: {payment.amount} {payment.currency}")
```

> **Security Tip:** Always verify webhook signatures! Without this check, anyone could fake a payment notification.

---

## Error Handling

### Common Errors and How to Fix Them

| Error | Meaning | How to Fix |
|-------|---------|------------|
| `InvalidTokenError` | Your token is wrong | Check your token or get a new one from your bank |
| `RateLimitError` | Too many requests | Wait a moment, then retry |
| `ValidationError` | Invalid input | Check amount, currency, merchant name format |
| `NetworkError` | Can't reach Bakong | Check your internet connection |

### Handling Errors in Your Code

```python
from khqr_payment import KHQRClient
from khqr_payment.errors import (
    InvalidTokenError,
    ValidationError,
    NetworkError
)

try:
    client = KHQRClient("your_token")
    qr = client.create_qr(merchant=merchant, amount=100.00)
    
except InvalidTokenError as e:
    print("Token is invalid - get a new one from your bank")
    
except ValidationError as e:
    print(f"Invalid input: {e.message}")
    # Check amount format, merchant details
    
except NetworkError as e:
    print("Network issue - try again later")
    
finally:
    # Always close the client
    try:
        client.close()
    except:
        pass
```

---

## Testing (Without Real Money)

### Option 1: Use Sandbox (SIT) Environment

```python
client = KHQRClient(
    token="your_token",
    use_sit=True  # Use sandbox - no real money
)
```

### Option 2: Mock the API

```python
from unittest.mock import patch, Mock

# Mock the API response
with patch('khqr_payment.core.client.httpx.Client') as mock:
    mock_client = Mock()
    mock_client.post.return_value.json.return_value = {
        "status": "00",
        "amount": "100.00",
        "currency": "USD"
    }
    mock.return_value = mock_client
    
    # Your code runs with mock data
    client = KHQRClient("test_token")
    status = client.check_payment("test_hash")
```

---

## Configuration Options

### KHQRClient Options

```python
client = KHQRClient(
    token="your_token",
    use_sit=False,           # True = sandbox, False = production
    use_relay=False,         # True = use relay API
    timeout=30.0            # Request timeout in seconds
)
```

---

## API Reference

### Main Classes

| Class | Description |
|-------|-------------|
| `KHQRClient` | Synchronous client for payments |
| `AsyncKHQRClient` | Async client for high-performance apps |
| `Merchant` | Your business information |
| `QRCode` | Generated QR code data |
| `PaymentStatus` | Payment verification result |

### Key Methods

| Method | Description |
|--------|-------------|
| `create_qr()` | Create a QR code for payment |
| `generate_deeplink()` | Create a deep link URL |
| `check_payment()` | Verify if payment was made |
| `get_payment()` | Get full payment details |
| `check_bulk_payments()` | Check multiple payments |
| `parse_qr()` | Read information from QR string |

---

## FAQ

### Q: Do I need to check payments manually?
**A:** Yes, after creating a QR, call `check_payment(md5)` to verify payment. You can also use webhooks for automatic notifications.

### Q: What's the difference between USD and KHR?
**A:** USD is US Dollars, KHR is Cambodian Riel. 1 USD ≈ 4100 KHR. Use whichever currency you prefer.

### Q: Can I test without real money?
**A:** Yes! Use `use_sit=True` in KHQRClient for sandbox testing.

### Q: How long is a QR code valid?
**A:** Dynamic QR codes expire based on bank policy. Static QR codes don't expire but we recommend rotating them periodically.

### Q: What if the customer's bank isn't supported?
**A:** All major Cambodian banks support KHQR. If issues persist, contact Bakong support.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

For detailed guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Security

For security vulnerabilities, please see [SECURITY.md](SECURITY.md).

---

## Sponsor

If you find this library helpful, please consider sponsoring the project!

[![Buy Me a Coffee](https://cdn.buymeacoffee.com/buttons/default-orange.png)](https://buymeacoffee.com/hengly)

Your support helps maintain and improve this library!

---

## License

MIT License - see [LICENSE](LICENSE) file for details.
