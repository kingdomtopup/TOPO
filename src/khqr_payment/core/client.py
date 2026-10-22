from typing import Literal

import httpx

from khqr_payment.core.constants import APIConstants
from khqr_payment.errors import (
    APIError,
    InvalidTokenError,
    NetworkError,
    RateLimitError,
    ValidationError,
)
from khqr_payment.models.payment import BulkPaymentStatus, PaymentInfo, PaymentStatus
from khqr_payment.models.qr import Merchant, ParsedQRCode, QRCode, QRCodeRequest
from khqr_payment.utils.deeplink import generate_deeplink, generate_native_deeplink
from khqr_payment.utils.qr_generator import generate_qr_string
from khqr_payment.utils.qr_image import generate_qr_image, save_qr_image
from khqr_payment.utils.qr_parser import parse_qr_string
from khqr_payment.utils.validators import validate_request, validate_token


class KHQRClient:
    """Main client for Bakong KHQR API."""

    def __init__(
        self,
        token: str,
        use_sit: bool = False,
        use_relay: bool = False,
        timeout: float = 30.0,
    ):
        """
        Initialize KHQR client.

        Args:
            token: Bakong API token
            use_sit: Use SIT environment (default: False for production)
            use_relay: Use Bakong Relay API (default: False)
            timeout: Request timeout in seconds (default: 30)
        """
        validate_token(token)

        self.token = token
        self.use_sit = use_sit
        self.use_relay = use_relay
        self.timeout = timeout

        base_url = (
            APIConstants.SIT_BASE_URL
            if use_sit
            else APIConstants.RELAY_BASE_URL
            if use_relay
            else APIConstants.BASE_URL
        )

        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    def __enter__(self) -> "KHQRClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def create_qr_string(
        self,
        merchant: Merchant | str,
        amount: float | None = None,
        currency: Literal["USD", "KHR"] = "USD",
        store_label: str | None = None,
        phone_number: str | None = None,
        bill_number: str | None = None,
        terminal_label: str | None = None,
        purpose: str | None = None,
        static: bool = False,
        merchant_name: str | None = None,
        merchant_city: str | None = None,
        acquiring_bank: str | None = None,
        account_information: str | None = None,
        language_preference: str | None = None,
        merchant_name_alternate: str | None = None,
        merchant_city_alternate: str | None = None,
    ) -> QRCode:
        """
        Create QR string for payment.

        Args:
            merchant: Merchant object or bank account string
            amount: Transaction amount
            currency: Currency code (USD/KHR)
            store_label: Store label
            phone_number: Phone number
            bill_number: Bill number
            terminal_label: Terminal label
            purpose: Payment purpose
            static: Static or Dynamic QR (default: False)
            merchant_name: Merchant name (required if merchant is string)
            merchant_city: Merchant city (required if merchant is string)
            acquiring_bank: Acquiring bank name
            account_information: Customer account info for remittance
            language_preference: Language preference (en, kh)
            merchant_name_alternate: Merchant name in alternate language
            merchant_city_alternate: Merchant city in alternate language

        Returns:
            QRCode object with string and md5 hash
        """
        if isinstance(merchant, str):
            if not merchant_name or not merchant_city:
                raise ValidationError(
                    "merchant_name and merchant_city are required when merchant is a string"
                )
            merchant = Merchant(bank_account=merchant, name=merchant_name, city=merchant_city)

        validate_request(amount, currency, merchant.bank_account, static)

        request = QRCodeRequest(
            bank_account=merchant.bank_account,
            merchant_name=merchant.name,
            merchant_city=merchant.city,
            postal_code=merchant.postal_code,
            amount=amount,
            currency=currency,
            acquiring_bank=acquiring_bank or merchant.acquiring_bank,
            account_information=account_information or merchant.account_information,
            store_label=store_label or merchant.store_label,
            phone_number=phone_number or merchant.phone_number,
            bill_number=bill_number or merchant.bill_number,
            terminal_label=terminal_label or merchant.terminal_label,
            purpose=purpose or merchant.purpose,
            language_preference=language_preference or merchant.language_preference,
            merchant_name_alternate=merchant_name_alternate or merchant.merchant_name_alternate,
            merchant_city_alternate=merchant_city_alternate or merchant.merchant_city_alternate,
            static=static,
        )

        qr_string, md5_hash = generate_qr_string(request)

        return QRCode(
            string=qr_string,
            md5=md5_hash,
            is_static=static,
            amount=amount,
            currency=currency,
            merchant=merchant,
        )

    def generate_qr_image(
        self,
        data: QRCode | str,
        output_path: str | None = None,
        format: Literal["png", "jpeg", "webp"] = "png",
    ) -> bytes | str:
        """
        Generate QR code image from QRCode object or QR string.

        Args:
            data: QRCode object from create_qr_string() or QR string directly
            output_path: Path to save the image (if None, returns bytes)
            format: Image format (png, jpeg, webp)

        Returns:
            Image bytes if output_path is None, otherwise the saved file path

        Examples:
            # Using QRCode object (recommended)
            qr = client.create_qr_string(merchant="shop@bank", ...)
            client.generate_qr_image(qr)

            # Using QR string directly
            client.generate_qr_image(qr.string)

            # Save to file
            client.generate_qr_image(qr, output_path="qr.png")
        """
        qr_string: str
        if isinstance(data, QRCode):
            qr_string = data.string
        else:
            qr_string = data

        if output_path:
            return save_qr_image(qr_string, output_path, format=format)

        return generate_qr_image(qr_string, format=format)

    def generate_deeplink(
        self,
        qr_string: str,
        callback: str,
        app_icon_url: str | None = None,
        app_name: str | None = None,
    ) -> str:
        """
        Generate deeplink from QR string.

        Args:
            qr_string: QR string from create_qr
            callback: Callback URL after payment
            app_icon_url: App icon URL
            app_name: App name

        Returns:
            Generated deeplink URL
        """
        return generate_deeplink(
            qr_string=qr_string,
            callback=callback,
            app_icon_url=app_icon_url,
            app_name=app_name,
            use_relay=self.use_relay,
        )

    def generate_native_deeplink(
        self,
        qr_string: str,
        callback: str,
        app_scheme: str | None = None,
    ) -> str:
        """
        Generate native app deeplink (bakong://payment?data=...).

        Args:
            qr_string: QR string from create_qr
            callback: Callback URL after payment
            app_scheme: Custom app scheme (e.g., myapp://)

        Returns:
            Native deeplink URL (bakong://payment?data=...)
        """
        return generate_native_deeplink(
            qr_string=qr_string,
            callback=callback,
            app_scheme=app_scheme,
        )

    def check_payment(self, md5_hash: str) -> PaymentStatus:
        """
        Check payment status.

        Args:
            md5_hash: MD5 hash from QR code

        Returns:
            PaymentStatus object
        """
        endpoint = (
            APIConstants.RELAY_ENDPOINTS["check_payment"]
            if self.use_relay
            else APIConstants.ENDPOINTS["check_payment"]
        )

        try:
            response = self._client.post(endpoint, json={"md5": md5_hash})

            if response.status_code == 401:
                raise InvalidTokenError("Invalid or expired token")
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            if response.status_code >= 400:
                raise APIError(f"API error: {response.text}", code=str(response.status_code))

            data = response.json()
            return PaymentStatus.from_response(md5_hash, data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}")

    def get_payment(self, md5_hash: str) -> PaymentInfo:
        """
        Get payment information.

        Args:
            md5_hash: MD5 hash from QR code

        Returns:
            PaymentInfo object
        """
        endpoint = (
            APIConstants.RELAY_ENDPOINTS["get_payment"]
            if self.use_relay
            else APIConstants.ENDPOINTS["get_payment"]
        )

        try:
            response = self._client.post(endpoint, json={"md5": md5_hash})

            if response.status_code == 401:
                raise InvalidTokenError("Invalid or expired token")
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            if response.status_code >= 400:
                raise APIError(f"API error: {response.text}", code=str(response.status_code))

            data = response.json()
            return PaymentInfo(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}")

    def check_bulk_payments(self, md5_list: list[str]) -> BulkPaymentStatus:
        """
        Check multiple payment statuses.

        Args:
            md5_list: List of MD5 hashes (max 50)

        Returns:
            BulkPaymentStatus object
        """
        if len(md5_list) > 50:
            raise ValidationError("Maximum 50 MD5 hashes allowed per request")

        endpoint = (
            APIConstants.RELAY_ENDPOINTS["bulk_payment"]
            if self.use_relay
            else APIConstants.ENDPOINTS["bulk_payment"]
        )

        try:
            response = self._client.post(endpoint, json={"hashes": md5_list})

            if response.status_code == 401:
                raise InvalidTokenError("Invalid or expired token")
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            if response.status_code >= 400:
                raise APIError(f"API error: {response.text}", code=str(response.status_code))

            data = response.json()
            return BulkPaymentStatus.from_response(md5_list, data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}")

    def parse_qr(self, qr_string: str) -> ParsedQRCode:
        """
        Parse QR string.

        Args:
            qr_string: QR string to parse

        Returns:
            ParsedQRCode object
        """
        data = parse_qr_string(qr_string)

        additional_data = data.get("additional_data", {})

        return ParsedQRCode(
            raw_string=qr_string,
            merchant_id=data.get("merchant_id"),
            merchant_name=data.get("merchant_name"),
            merchant_city=data.get("merchant_city"),
            amount=data.get("amount"),
            currency=data.get("currency"),
            bill_number=additional_data.get("01"),
            store_label=additional_data.get("03"),
            terminal_label=additional_data.get("04"),
            phone_number=additional_data.get("02"),
            purpose=additional_data.get("05"),
        )

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to API."""
        try:
            response = self._client.get("/api/v1/health")
            return response.status_code == 200
        except Exception:
            return False

    def get_account_info(self, bank_account: str) -> dict:
        """
        Get account information for a Bakong account.

        Args:
            bank_account: Bakong account ID (e.g., "user@bank")

        Returns:
            dict: Account information

        Raises:
            InvalidTokenError: If token is invalid or expired
            NetworkError: If network error occurs
            APIError: If API returns an error
        """
        endpoint = (
            APIConstants.RELAY_ENDPOINTS["account_info"]
            if self.use_relay
            else APIConstants.ENDPOINTS["account_info"]
        )

        try:
            response = self._client.post(endpoint, json={"accountId": bank_account})

            if response.status_code == 401:
                raise InvalidTokenError("Invalid or expired token")
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            if response.status_code >= 400:
                raise APIError(f"API error: {response.text}", code=str(response.status_code))

            return response.json()

        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}")

    def get_merchant_info(self, bank_account: str) -> dict:
        """
        Get merchant information (alias for get_account_info).

        Args:
            bank_account: Bakong account ID (e.g., "user@bank")

        Returns:
            dict: Account/merchant information
        """
        return self.get_account_info(bank_account)

    def validate_token(self) -> bool:
        """
        Validate if the token is valid and working.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            import hashlib

            fake_md5 = hashlib.md5(b"test").hexdigest()
            endpoint = (
                APIConstants.RELAY_ENDPOINTS["check_payment"]
                if self.use_relay
                else APIConstants.ENDPOINTS["check_payment"]
            )
            response = self._client.post(endpoint, json={"md5": fake_md5})
            if response.status_code == 401:
                return False
            return True
        except Exception:
            return False
            if response.status_code >= 400:
                return False
            return True
        except Exception:
            return False
