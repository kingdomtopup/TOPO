import pytest
from khqr_payment.models.qr import QRCodeRequest
from khqr_payment.utils.qr_generator import generate_qr_string, QRStringGenerator
from khqr_payment.utils.qr_parser import parse_qr_string, QRParser
from khqr_payment.utils.validators import (
    validate_request,
    validate_qr_string,
    QRValidator,
    CurrencyConverter,
)
from khqr_payment.errors import (
    ValidationError,
    CurrencyError,
    AmountError,
    QRValidationError,
)


class TestQRStringGenerator:
    def test_generate_qr_string(self):
        request = QRCodeRequest(
            bank_account="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh",
            amount=100.00,
            currency="USD",
            static=False,
        )
        qr_string, md5_hash = generate_qr_string(request)

        assert qr_string is not None
        assert len(qr_string) > 0
        assert md5_hash is not None
        assert len(md5_hash) == 32

    def test_generate_static_qr(self):
        request = QRCodeRequest(
            bank_account="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh",
            static=True,
        )
        qr_string, md5_hash = generate_qr_string(request)

        assert qr_string is not None
        assert "12" in qr_string

    def test_generate_khr_qr(self):
        request = QRCodeRequest(
            bank_account="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh",
            amount=10000,
            currency="KHR",
            static=False,
        )
        qr_string, md5_hash = generate_qr_string(request)

        assert qr_string is not None
        # ISO 4217 code for KHR is 116
        assert "5303116" in qr_string


class TestQRParser:
    def test_parse_valid_qr_string(self):
        request = QRCodeRequest(
            bank_account="user@bank",
            merchant_name="Test Store",
            merchant_city="Phnom Penh",
            amount=100.00,
            currency="USD",
            static=False,
        )
        qr_string, _ = generate_qr_string(request)

        parsed = parse_qr_string(qr_string)

        assert parsed["merchant_id_data"]["bank_account"] == "user@bank"
        assert parsed["merchant_name"] == "Test Store"
        assert parsed["merchant_city"] == "Phnom Penh"
        assert parsed["amount"] == 100.00

    def test_parse_invalid_qr_string(self):
        with pytest.raises(QRValidationError):
            parse_qr_string("too short")


class TestValidators:
    def test_validate_valid_request(self):
        validate_request(amount=100.00, currency="USD", bank_account="user@bank", is_static=False)

    def test_validate_invalid_currency(self):
        with pytest.raises(CurrencyError):
            validate_request(
                amount=100.00, currency="EUR", bank_account="user@bank", is_static=False
            )

    def test_validate_negative_amount(self):
        with pytest.raises(AmountError):
            validate_request(
                amount=-100.00, currency="USD", bank_account="user@bank", is_static=False
            )

    def test_validate_exceed_max_amount_usd(self):
        with pytest.raises(AmountError):
            validate_request(
                amount=1000000, currency="USD", bank_account="user@bank", is_static=False
            )

    def test_validate_invalid_bank_account(self):
        with pytest.raises(ValidationError):
            validate_request(amount=100.00, currency="USD", bank_account="invalid", is_static=False)

    def test_validate_static_qr_no_amount(self):
        validate_request(amount=None, currency="USD", bank_account="user@bank", is_static=True)

    def test_validate_qr_string_invalid(self):
        with pytest.raises(ValidationError):
            validate_qr_string("short")


class TestCurrencyConverter:
    def test_usd_to_khr(self):
        result = CurrencyConverter.usd_to_khr(100.00)
        assert result == 410000

    def test_khr_to_usd(self):
        result = CurrencyConverter.khr_to_usd(410000)
        assert result == 100.0

    def test_custom_exchange_rate(self):
        CurrencyConverter.set_exchange_rate(4000)
        result = CurrencyConverter.usd_to_khr(100.00)
        assert result == 400000
        CurrencyConverter.set_exchange_rate(4100)

    def test_invalid_exchange_rate(self):
        with pytest.raises(ValidationError):
            CurrencyConverter.set_exchange_rate(-1)
