import pytest
from unittest.mock import Mock, patch, AsyncMock
from khqr_payment.core.client import KHQRClient
from khqr_payment.core.async_client import AsyncKHQRClient
from khqr_payment.models.qr import Merchant, QRCodeRequest
from khqr_payment.models.payment import PaymentStatus, PaymentInfo
from khqr_payment.errors import (
    InvalidTokenError,
    ValidationError,
    RateLimitError,
)


class TestKHQRClient:
    def test_client_initialization(self):
        client = KHQRClient(token="test_token_12345678901234567890")
        assert client.token == "test_token_12345678901234567890"
        assert client.use_sit is False
        assert client.use_relay is False
        client.close()

    def test_client_with_sit(self):
        client = KHQRClient(token="test_token_12345678901234567890", use_sit=True)
        assert "sit-api-bakong" in str(client._client.base_url)
        client.close()

    def test_client_with_relay(self):
        client = KHQRClient(token="test_token_12345678901234567890", use_relay=True)
        assert "bakongrelay" in str(client._client.base_url)
        client.close()

    def test_invalid_token(self):
        with pytest.raises(ValidationError):
            KHQRClient(token="")

    def test_create_qr_string(self):
        with patch("khqr_payment.core.client.httpx.Client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            client = KHQRClient(token="test_token_12345678901234567890")
            client._client = mock_instance

            merchant = Merchant(bank_account="user@bank", name="Test Store", city="Phnom Penh")

            qr = client.create_qr_string(merchant=merchant, amount=100.00, currency="USD")

            assert qr.string is not None
            assert qr.md5 is not None
            assert qr.amount == 100.00
            assert qr.currency == "USD"
            assert qr.merchant.bank_account == "user@bank"

    def test_create_qr_string_with_string_merchant(self):
        with patch("khqr_payment.core.client.httpx.Client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            client = KHQRClient(token="test_token_12345678901234567890")
            client._client = mock_instance

            qr = client.create_qr_string(
                merchant="user@bank",
                merchant_name="Test Store",
                merchant_city="Phnom Penh",
                amount=100.00,
                currency="USD",
            )

            assert qr.merchant.bank_account == "user@bank"

    def test_create_static_qr_string(self):
        with patch("khqr_payment.core.client.httpx.Client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            client = KHQRClient(token="test_token_12345678901234567890")
            client._client = mock_instance

            qr = client.create_qr_string(
                merchant="user@bank",
                merchant_name="Test Store",
                merchant_city="Phnom Penh",
                amount=None,
                static=True,
            )

            assert qr.is_static is True

    def test_parse_qr(self):
        with patch("khqr_payment.core.client.httpx.Client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            client = KHQRClient(token="test_token_12345678901234567890")
            client._client = mock_instance

            request = QRCodeRequest(
                bank_account="user@bank",
                merchant_name="Test Store",
                merchant_city="Phnom Penh",
                amount=100.00,
                currency="USD",
                static=False,
            )

            from khqr_payment.utils.qr_generator import generate_qr_string

            qr_string, _ = generate_qr_string(request)

            parsed = client.parse_qr(qr_string)

            assert parsed.merchant_name == "Test Store"


class TestAsyncKHQRClient:
    @pytest.mark.asyncio
    async def test_async_client_initialization(self):
        client = AsyncKHQRClient(token="test_token_12345678901234567890")
        assert client.token == "test_token_12345678901234567890"
        await client.close()

    @pytest.mark.asyncio
    async def test_async_create_qr_string(self):
        with patch("khqr_payment.core.async_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance

            client = AsyncKHQRClient(token="test_token_12345678901234567890")
            client._client = mock_instance

            qr = await client.create_qr_string(
                merchant="user@bank",
                merchant_name="Test Store",
                merchant_city="Phnom Penh",
                amount=100.00,
                currency="USD",
            )

            assert qr.md5 is not None
            await client.close()
