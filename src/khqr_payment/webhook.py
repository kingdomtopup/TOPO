import hashlib
import hmac
import json
from typing import Any

from khqr_payment.errors import WebhookSignatureError


class WebhookHandler:
    """Handle Bakong webhook events."""

    def __init__(self, secret_key: str):
        """
        Initialize webhook handler.
        
        Args:
            secret_key: Webhook secret key
        """
        self.secret_key = secret_key

    def verify_signature(
        self,
        payload: str | dict,
        signature: str,
    ) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Raw payload string or dict
            signature: Signature from webhook header
            
        Returns:
            True if signature is valid
            
        Raises:
            WebhookSignatureError: If signature is invalid
        """
        if isinstance(payload, dict):
            payload = json.dumps(payload, separators=(",", ":"))

        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            raise WebhookSignatureError("Invalid webhook signature")

        return True

    def parse_payload(self, payload: str | dict) -> dict[str, Any]:
        """
        Parse webhook payload.
        
        Args:
            payload: Raw payload string or dict
            
        Returns:
            Parsed webhook data
        """
        if isinstance(payload, str):
            return json.loads(payload)
        return payload

    def handle_payment_webhook(self, payload: str | dict) -> dict[str, Any]:
        """
        Handle payment webhook.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Payment data
        """
        data = self.parse_payload(payload)

        return {
            "event_type": data.get("eventType"),
            "hash": data.get("hash"),
            "from_account": data.get("fromAccountId"),
            "to_account": data.get("toAccountId"),
            "amount": data.get("amount"),
            "currency": data.get("currency"),
            "description": data.get("description"),
            "created_at": data.get("createdDateMs"),
        }


def verify_webhook_signature(
    payload: str | dict,
    signature: str,
    secret_key: str,
) -> bool:
    """
    Verify webhook signature.
    
    Args:
        payload: Raw payload string or dict
        signature: Signature from webhook header
        secret_key: Webhook secret key
        
    Returns:
        True if signature is valid
    """
    handler = WebhookHandler(secret_key)
    return handler.verify_signature(payload, signature)
