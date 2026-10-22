import re

from khqr_payment.core.constants import QRConstants
from khqr_payment.errors import AmountError, CurrencyError, ValidationError


class QRValidator:
    """Validate QR string and request data."""

    @staticmethod
    def validate_request(
        amount: float | None,
        currency: str,
        bank_account: str,
        is_static: bool = False
    ) -> None:
        """
        Validate QR request parameters.
        
        Args:
            amount: Transaction amount
            currency: Currency code (USD/KHR)
            bank_account: Bank account ID
            is_static: Whether this is a static QR
            
        Raises:
            ValidationError: If validation fails
        """
        QRValidator._validate_currency(currency)
        QRValidator._validate_amount(amount, currency, is_static)
        QRValidator._validate_bank_account(bank_account)

    @staticmethod
    def _validate_currency(currency: str) -> None:
        """Validate currency code."""
        if currency not in QRConstants.CURRENCIES:
            raise CurrencyError(
                f"Invalid currency: {currency}. Must be one of {QRConstants.CURRENCIES}"
            )

    @staticmethod
    def _validate_amount(amount: float | None, currency: str, is_static: bool) -> None:
        """Validate transaction amount."""
        if is_static:
            return

        if amount is None:
            raise AmountError("Amount is required for dynamic QR")

        if amount < 0:
            raise AmountError("Amount cannot be negative")

        if currency == "USD" and amount > QRConstants.MAX_AMOUNT_USD:
            raise AmountError(
                f"Amount exceeds maximum: {QRConstants.MAX_AMOUNT_USD} USD"
            )
        elif currency == "KHR" and amount > QRConstants.MAX_AMOUNT_KHR:
            raise AmountError(
                f"Amount exceeds maximum: {QRConstants.MAX_AMOUNT_KHR} KHR"
            )

    @staticmethod
    def _validate_bank_account(bank_account: str) -> None:
        """Validate bank account format."""
        if not bank_account:
            raise ValidationError("Bank account is required")

        if not re.match(r"^[\w\.-]+@[\w\.-]+$", bank_account):
            raise ValidationError(
                f"Invalid bank account format: {bank_account}. Expected format: user@bank"
            )

    @staticmethod
    def validate_qr_string(qr_string: str) -> bool:
        """
        Validate QR string format.
        
        Args:
            qr_string: QR string to validate
            
        Returns:
            True if valid
            
        Raises:
            QRValidationError: If QR string is invalid
        """
        if not qr_string or len(qr_string) < 20:
            raise ValidationError("Invalid QR string: too short")

        if not qr_string.startswith("000201"):
            raise ValidationError("Invalid QR string: wrong format")

        if not qr_string.endswith("6304"):
            raise ValidationError("Invalid QR string: missing CRC")

        return True

    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate API token format.
        
        Args:
            token: API token to validate
            
        Returns:
            True if valid
        """
        if not token:
            raise ValidationError("Token is required")

        if len(token) < 20:
            raise ValidationError("Invalid token format")

        return True


class CurrencyConverter:
    """Currency conversion utilities."""

    EXCHANGE_RATE = 4100

    @staticmethod
    def usd_to_khr(amount: float) -> int:
        """Convert USD to KHR."""
        return int(amount * CurrencyConverter.EXCHANGE_RATE)

    @staticmethod
    def khr_to_usd(amount: int) -> float:
        """Convert KHR to USD."""
        return round(amount / CurrencyConverter.EXCHANGE_RATE, 2)

    @staticmethod
    def set_exchange_rate(rate: float) -> None:
        """Set custom exchange rate."""
        if rate <= 0:
            raise ValidationError("Exchange rate must be positive")
        CurrencyConverter.EXCHANGE_RATE = rate


def validate_request(
    amount: float | None,
    currency: str,
    bank_account: str,
    is_static: bool = False
) -> None:
    """Validate QR request parameters."""
    QRValidator.validate_request(amount, currency, bank_account, is_static)


def validate_qr_string(qr_string: str) -> bool:
    """Validate QR string format."""
    return QRValidator.validate_qr_string(qr_string)


def validate_token(token: str) -> bool:
    """Validate API token format."""
    return QRValidator.validate_token(token)
