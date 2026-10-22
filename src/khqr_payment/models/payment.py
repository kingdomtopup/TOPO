from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PaymentStatus(BaseModel):
    """Payment status model."""

    md5: str = Field(..., description="MD5 hash of the QR")
    is_paid: bool = Field(..., description="Whether payment has been made")
    status: Literal["PAID", "UNPAID"] = Field(..., description="Payment status")
    amount: float | None = Field(None, description="Payment amount")
    currency: str | None = Field(None, description="Currency code")
    from_account_id: str | None = Field(None, description="Sender account ID")
    to_account_id: str | None = Field(None, description="Receiver account ID")

    @classmethod
    def from_response(cls, md5: str, response: dict) -> "PaymentStatus":
        """Create from API response.

        Handles different response formats:
        - Old format: {"status": "PAID"}
        - New format: {"responseCode": 0, "data": {...}}
        """
        amount: float | None = None
        currency: str | None = None
        from_account_id: str | None = None
        to_account_id: str | None = None

        # Check responseCode (new format): 0 = success/paid, 1 = error/unpaid
        response_code = response.get("responseCode")
        if response_code is not None:
            is_paid = response_code == 0 and response.get("data") is not None
            status = "PAID" if is_paid else "UNPAID"
            # Extract amount and currency from data
            if is_paid and response.get("data"):
                data = response["data"]
                amount = data.get("amount")
                currency = data.get("currency")
                from_account_id = data.get("fromAccountId")
                to_account_id = data.get("toAccountId")
        else:
            # Fallback to old format: {"status": "PAID"}
            is_paid = response.get("status", "").upper() == "PAID"
            status = response.get("status", "UNPAID")

        return cls(
            md5=md5,
            is_paid=is_paid,
            status=status,
            amount=amount,
            currency=currency,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
        )


class PaymentInfo(BaseModel):
    """Payment information model."""

    hash: str = Field(..., description="Payment hash")
    from_account_id: str | None = Field(None, description="Sender account ID")
    to_account_id: str | None = Field(None, description="Receiver account ID")
    currency: str = Field(..., description="Currency code")
    amount: float = Field(..., description="Payment amount")
    description: str | None = Field(None, description="Payment description")
    created_date_ms: int | None = Field(None, description="Created timestamp in milliseconds")
    acknowledged_date_ms: int | None = Field(
        None, description="Acknowledged timestamp in milliseconds"
    )
    tracking_status: str | None = Field(None, description="Tracking status")
    receiver_bank: str | None = Field(None, description="Receiver bank")
    receiver_bank_account: str | None = Field(None, description="Receiver bank account")
    instruction_ref: str | None = Field(None, description="Instruction reference")
    external_ref: str | None = Field(None, description="External reference")

    @property
    def created_at(self) -> datetime | None:
        """Get created datetime."""
        if self.created_date_ms:
            return datetime.fromtimestamp(self.created_date_ms / 1000)
        return None

    @property
    def acknowledged_at(self) -> datetime | None:
        """Get acknowledged datetime."""
        if self.acknowledged_date_ms:
            return datetime.fromtimestamp(self.acknowledged_date_ms / 1000)
        return None


class BulkPaymentStatus(BaseModel):
    """Bulk payment status model."""

    md5_list: list[str] = Field(..., description="List of paid MD5 hashes")
    total_checked: int = Field(..., description="Total number of MD5 hashes checked")
    total_paid: int = Field(..., description="Total number of paid transactions")

    @classmethod
    def from_response(cls, md5_list: list[str], response: list[str]) -> "BulkPaymentStatus":
        """Create from API response."""
        return cls(md5_list=response, total_checked=len(md5_list), total_paid=len(response))
