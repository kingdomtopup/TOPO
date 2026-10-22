from typing import Any


class KHQRPaymentError(Exception):
    """Base exception for all KHQR payment errors."""

    def __init__(self, message: str, code: str | None = None, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class APIError(KHQRPaymentError):
    """Exception raised when API request fails."""
    pass


class AuthenticationError(APIError):
    """Exception raised when authentication fails."""
    pass


class InvalidTokenError(AuthenticationError):
    """Exception raised when token is invalid or expired."""
    pass


class ValidationError(KHQRPaymentError):
    """Exception raised when input validation fails."""
    pass


class QRValidationError(ValidationError):
    """Exception raised when QR string validation fails."""
    pass


class CurrencyError(ValidationError):
    """Exception raised when currency is invalid."""
    pass


class AmountError(ValidationError):
    """Exception raised when amount is invalid."""
    pass


class NetworkError(KHQRPaymentError):
    """Exception raised when network request fails."""
    pass


class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded."""
    pass


class WebhookError(KHQRPaymentError):
    """Exception raised when webhook verification fails."""
    pass


class WebhookSignatureError(WebhookError):
    """Exception raised when webhook signature is invalid."""
    pass
