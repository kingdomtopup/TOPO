from simple_config import api_token
from khqr_payment import KHQRClient, Merchant
import time

BANK_ACCOUNT = "abaakhppxxx@abaa"  # Your Bakong account

# 1. Initialize client with your token
client = KHQRClient(api_token)

# Validate token before proceeding
if client.validate_token():
    print("Token is valid and working!")
else:
    print("Token is invalid or expired!")
    client.close()
    exit(1)

# Get account/merchant info (requires bank account)
try:
    merchant_info = client.get_merchant_info(BANK_ACCOUNT)
    print(f"Merchant Info: {merchant_info}")
except Exception as e:
    print(f"Could not get merchant info: {e}")

# Create merchant information with all available fields
merchant = Merchant(
    bank_account="abaakhppxxx@abaa",  # Your Bakong account
    name="FnDevX",  # Max 25 characters
    city="Phnom Penh",  # Your city
    store_label="Coffee Shop",
    phone_number="85566669999",
    bill_number="TRX987654321",
    terminal_label="Cashier-01",
    acquiring_bank="ACLB",  # Acquiring bank name
    account_information=None,  # For remittance (customer's account)
    purpose="Payment for coffee",
    language_preference="en",
    merchant_name_alternate=None,
    merchant_city_alternate=None,
    static=False,  # Static or Dynamic QR code (default: False)
)

# Create QR code for payment with new parameters
qr = client.create_qr_string(
    merchant="abaakhppxxx@abaa",  # Bank account (first param)
    merchant_name="Coffee Shop",  # Name of the receiver
    merchant_city="Phnom Penh",
    amount=0.01,  # 9800 Riel
    currency="USD",  # USD or KHR
    store_label="Coffee Shop",
    phone_number="85517272781",
    bill_number="TRX987654321",
    terminal_label="Cashier-01",
    static=False,  # Static or Dynamic QR code (default: False)
)

# Show qr.string to customer (they scan it to pay)
print(f"QR String: {qr.string}")
print(f"MD5 Hash: {qr.md5}")  # Use this to verify payment later

# Generate and save QR image from QRCode object (simplified!)
# This generates QR from raw KHQR string - which is what banking apps scan!
saved_path = client.generate_qr_image(
    qr,  # Pass the QRCode object directly!
    output_path="payment_qr.png",
)
print(f"QR image saved to: {saved_path}")

# ============================================
# Check Payment by MD5 Hash (Standalone Example)

# Option 1: Use qr.md5 from current session
MD5_HASH = qr.md5

# Option 2: Use a saved MD5 hash string
# MD5_HASH = "af0fdac4a8e1e55c095f93e95eb5d0c5"

# Check payment with retry (every 5 seconds, timeout 2 minutes)
MAX_ATTEMPTS = 24  # 24 * 5 seconds = 2 minutes
CHECK_INTERVAL = 5  # seconds

print(f"\n=== Waiting for payment (timeout: 2 minutes) ===")

for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
        status = client.check_payment(MD5_HASH)

        print(f"Attempt {attempt}/{MAX_ATTEMPTS} - Status: {status.status}")
        print(f"MD5: {status.md5}")  # Print MD5 to verify it matches the original QR code

        if status.is_paid:
            print(f"\n=== Payment Received! ===")
            print(f"Amount: {status.amount} {status.currency}")
            print(f"Status: {status.status}")
            print(f"From: {status.from_account_id}")
            print(f"To: {status.to_account_id}")
            break
        else:
            print(f"Payment not yet received, retrying in {CHECK_INTERVAL}s...")

    except Exception as e:
        print(f"Error checking payment: {e}")

    if attempt < MAX_ATTEMPTS:
        time.sleep(CHECK_INTERVAL)
else:
    print("\n=== Payment timeout (2 minutes) ===")
    print("Payment was not received within the timeout period.")

# Close connection when done
client.close()
print("Client closed.")
