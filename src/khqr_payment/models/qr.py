from typing import Literal

from pydantic import BaseModel, Field


class Merchant(BaseModel):
    """Merchant information for QR code generation."""

    bank_account: str = Field(..., description="Bank account ID (e.g., user@bank)")
    name: str = Field(..., min_length=1, max_length=25, description="Merchant name")
    city: str = Field(..., min_length=1, max_length=40, description="Merchant city")
    postal_code: str | None = Field(None, max_length=10, description="Postal code")
    acquiring_bank: str | None = Field(None, max_length=32, description="Acquiring bank name")
    account_information: str | None = Field(
        None, max_length=32, description="Customer account info for remittance"
    )
    bill_number: str | None = Field(None, max_length=25, description="Bill number")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    store_label: str | None = Field(None, max_length=25, description="Store label")
    terminal_label: str | None = Field(None, max_length=25, description="Terminal label")
    purpose: str | None = Field(None, max_length=25, description="Purpose of transaction")
    language_preference: str | None = Field(
        None, max_length=2, description="Language preference (en, kh)"
    )
    merchant_name_alternate: str | None = Field(
        None, max_length=25, description="Merchant name in alternate language"
    )
    merchant_city_alternate: str | None = Field(
        None, max_length=15, description="Merchant city in alternate language"
    )

    model_config = {"str_strip_whitespace": True}


class QRCode(BaseModel):
    """QR code data model."""

    string: str = Field(..., description="Raw QR string")
    md5: str = Field(..., description="MD5 hash of the QR string")
    is_static: bool = Field(..., description="Whether this is a static QR code")
    amount: float | None = Field(None, description="Transaction amount")
    currency: Literal["USD", "KHR"] = Field(..., description="Currency code")
    merchant: Merchant = Field(..., description="Merchant information")

    def is_paid(self) -> bool:
        """Check if payment is required for this QR."""
        return not self.is_static and self.amount is not None

    def requires_amount(self) -> bool:
        """Check if amount is required (static QR requires user input)."""
        return self.is_static


class QRCodeRequest(BaseModel):
    """Request model for creating QR code."""

    bank_account: str = Field(..., description="Bank account ID")
    merchant_name: str = Field(..., min_length=1, max_length=25)
    merchant_city: str = Field(..., min_length=1, max_length=40)
    amount: float | None = Field(None, ge=0, description="Transaction amount")
    currency: Literal["USD", "KHR"] = Field(default="USD")
    acquiring_bank: str | None = Field(None, max_length=32, description="Acquiring bank name")
    account_information: str | None = Field(
        None, max_length=32, description="Customer account info for remittance"
    )
    store_label: str | None = Field(None, max_length=25)
    phone_number: str | None = Field(None, max_length=20)
    bill_number: str | None = Field(None, max_length=25)
    terminal_label: str | None = Field(None, max_length=25)
    purpose: str | None = Field(None, max_length=25)
    language_preference: str | None = Field(None, max_length=2)
    merchant_name_alternate: str | None = Field(None, max_length=25)
    merchant_city_alternate: str | None = Field(None, max_length=15)
    static: bool = Field(default=False, description="Static or Dynamic QR")
    postal_code: str | None = Field(None, max_length=10)

    def to_merchant(self) -> Merchant:
        """Convert to Merchant model."""
        return Merchant(
            bank_account=self.bank_account,
            name=self.merchant_name,
            city=self.merchant_city,
            postal_code=self.postal_code,
        )


class ParsedQRCode(BaseModel):
    """Parsed QR code information."""

    raw_string: str = Field(..., description="Raw QR string")
    merchant_id: str | None = Field(None, description="Merchant ID")
    merchant_name: str | None = Field(None, description="Merchant name")
    merchant_city: str | None = Field(None, description="Merchant city")
    amount: float | None = Field(None, description="Transaction amount")
    currency: str | None = Field(None, description="Currency")
    bill_number: str | None = Field(None, description="Bill number")
    store_label: str | None = Field(None, description="Store label")
    terminal_label: str | None = Field(None, description="Terminal label")
    phone_number: str | None = Field(None, description="Phone number")
    purpose: str | None = Field(None, description="Payment purpose")

    @property
    def is_static(self) -> bool:
        """Check if this is a static QR code."""
        return self.amount is None
