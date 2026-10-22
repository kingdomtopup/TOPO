from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response model."""

    success: bool = Field(..., description="Whether the request was successful")
    data: T | None = Field(None, description="Response data")
    message: str | None = Field(None, description="Response message")
    code: int | None = Field(None, description="Response code")

    @classmethod
    def ok(cls, data: T, message: str | None = None) -> "APIResponse[T]":
        """Create a successful response."""
        return cls(success=True, data=data, message=message, code=200)

    @classmethod
    def error(cls, message: str, code: int = 400) -> "APIResponse[Any]":
        """Create an error response."""
        return cls(success=False, message=message, code=code)


class QRCodeResponse(BaseModel):
    """QR code creation response."""

    qr_string: str = Field(..., description="Generated QR string")
    md5: str = Field(..., description="MD5 hash of QR string")
    is_static: bool = Field(..., description="Whether QR is static")
    deeplink: str | None = Field(None, description="Generated deeplink")


class DeeplinkResponse(BaseModel):
    """Deeplink generation response."""

    deeplink: str = Field(..., description="Generated deeplink URL")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    code: int | None = Field(None, description="Error code")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
