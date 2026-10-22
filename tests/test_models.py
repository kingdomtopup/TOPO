import pytest
from khqr_payment.models.qr import Merchant, QRCode, QRCodeRequest, ParsedQRCode


class TestMerchant:
    def test_merchant_creation(self):
        merchant = Merchant(
            bank_account="user@bank",
            name="Test Store",
            city="Phnom Penh"
        )
        assert merchant.bank_account == "user@bank"
        assert merchant.name == "Test Store"
        assert merchant.city == "Phnom Penh"
    
    def test_merchant_with_postal_code(self):
        merchant = Merchant(
            bank_account="user@bank",
            name="Test Store",
            city="Phnom Penh",
            postal_code="12000"
        )
        assert merchant.postal_code == "12000"


class TestQRCodeRequest:
    def test_qr_request_creation(self):
        request = QRCodeRequest(
            bank_account="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh",
            amount=100.00,
            currency="USD",
            static=False
        )
        assert request.bank_account == "user@bank"
        assert request.amount == 100.00
        assert request.currency == "USD"
    
    def test_qr_request_to_merchant(self):
        request = QRCodeRequest(
            bank_account="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh"
        )
        merchant = request.to_merchant()
        assert isinstance(merchant, Merchant)
        assert merchant.bank_account == "user@bank"
        assert merchant.name == "Test Store"


class TestQRCode:
    def test_qr_code_creation(self):
        merchant = Merchant(
            bank_account="user@bank",
            name="Test Store",
            city="Phnom Penh"
        )
        qr = QRCode(
            string="00020101021229...",
            md5="abc123",
            is_static=False,
            amount=100.00,
            currency="USD",
            merchant=merchant
        )
        assert qr.string == "00020101021229..."
        assert qr.md5 == "abc123"
        assert qr.is_static is False
        assert qr.is_paid() is True
    
    def test_static_qr_requires_amount(self):
        merchant = Merchant(
            bank_account="user@bank",
            name="Test Store",
            city="Phnom Penh"
        )
        qr = QRCode(
            string="00020101021229...",
            md5="abc123",
            is_static=True,
            amount=None,
            currency="USD",
            merchant=merchant
        )
        assert qr.requires_amount() is True


class TestParsedQRCode:
    def test_parsed_qr_creation(self):
        parsed = ParsedQRCode(
            raw_string="00020101021229...",
            merchant_id="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh",
            amount=100.00,
            currency="USD"
        )
        assert parsed.is_static is False
    
    def test_parsed_static_qr(self):
        parsed = ParsedQRCode(
            raw_string="00020101021229...",
            merchant_id="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh"
        )
        assert parsed.is_static is True
