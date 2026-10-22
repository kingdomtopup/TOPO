import hashlib
import time

from khqr_payment.core.constants import QRConstants
from khqr_payment.models.qr import QRCodeRequest


class QRStringGenerator:
    """Generate QR string for Bakong KHQR standard."""

    @staticmethod
    def generate(request: QRCodeRequest) -> tuple[str, str]:
        """
        Generate QR string from request.

        Args:
            request: QRCodeRequest object

        Returns:
            Tuple of (qr_string, md5_hash)
        """
        tags = []

        # 00 - Payload Format Indicator
        tags.append(
            QRStringGenerator._create_tag(
                QRConstants.TAG_PAYLOAD_FORMAT, QRConstants.DEFAULT_PAYLOAD_FORMAT
            )
        )

        # 01 - Point of Initiation Method (format: 01 + length + value)
        point_of_initiation = "11" if request.static else "12"
        tags.append(
            QRStringGenerator._create_tag(QRConstants.TAG_POINT_OF_INITIATION, point_of_initiation)
        )

        # 29 - Merchant Account Information (Solo/Individual) with sub-tag 00
        tags.append(QRStringGenerator._create_global_unique_identifier(request.bank_account))

        # 52 - Merchant Category Code
        tags.append(QRStringGenerator._create_tag(QRConstants.TAG_MCC, QRConstants.DEFAULT_MCC))

        # 58 - Country Code
        tags.append(
            QRStringGenerator._create_tag(
                QRConstants.TAG_COUNTRY_CODE, QRConstants.DEFAULT_COUNTRY_CODE
            )
        )

        # 59 - Merchant Name
        tags.append(
            QRStringGenerator._create_tag(QRConstants.TAG_MERCHANT_NAME, request.merchant_name)
        )

        # 60 - Merchant City
        tags.append(
            QRStringGenerator._create_tag(QRConstants.TAG_MERCHANT_CITY, request.merchant_city)
        )

        # 99 - Timestamp (language preference + timestamp) - BEFORE amount!
        tags.append(QRStringGenerator._generate_timestamp())

        # 54 - Transaction Amount (only for dynamic QR)
        if not request.static and request.amount is not None:
            tags.append(QRStringGenerator._format_amount(request.amount))

        # 53 - Transaction Currency
        currency_code = "116" if request.currency == "KHR" else "840"
        tags.append(QRStringGenerator._create_tag(QRConstants.TAG_CURRENCY, currency_code))

        # 62 - Additional Data Field
        additional_data = QRStringGenerator._build_additional_data(
            bill_number=request.bill_number,
            phone_number=request.phone_number,
            store_label=request.store_label,
            terminal_label=request.terminal_label,
        )
        if additional_data:
            tags.append(additional_data)

        qr_data = "".join(tags)

        # 63 - CRC
        crc = QRStringGenerator._calculate_crc(qr_data)
        qr_data += crc

        md5_hash = QRStringGenerator._calculate_md5(qr_data)

        return qr_data, md5_hash

    @staticmethod
    def _create_tag(tag_id: str, value: str) -> str:
        """Create a tag with ID and length prefix."""
        length = str(len(value)).zfill(2)
        return f"{tag_id}{length}{value}"

    @staticmethod
    def _create_global_unique_identifier(bank_account: str) -> str:
        """Create global unique identifier (tag 29 with sub-tag 00)."""
        # Sub-tag 00: Globally Unique Identifier
        sub_tag = QRStringGenerator._create_tag(QRConstants.TAG_GLOBAL_UNIQUE_ID, bank_account)
        # Tag 29: Merchant Account Information
        return QRStringGenerator._create_tag(QRConstants.TAG_MERCHANT_ID, sub_tag)

    @staticmethod
    def _format_amount(amount: float) -> str:
        """Format amount - 11 digits with leading zeros (dollar amount as integer)."""
        amount_dollars = int(amount)
        amount_str = str(amount_dollars).zfill(11)
        return QRStringGenerator._create_tag(QRConstants.TAG_AMOUNT, amount_str)

    @staticmethod
    def _build_additional_data(
        bill_number: str | None = None,
        phone_number: str | None = None,
        store_label: str | None = None,
        terminal_label: str | None = None,
    ) -> str:
        """Build additional data field with correct order."""
        if not any([bill_number, phone_number, store_label, terminal_label]):
            return ""

        data_parts = []

        # Order: bill_number (01), phone_number (02), store_label (03), terminal_label (07)
        if bill_number:
            data_parts.append(
                QRStringGenerator._create_tag(QRConstants.TAG_BILL_NUMBER, bill_number)
            )

        if phone_number:
            # Keep the full phone number (with 855 prefix)
            digits = "".join(c for c in phone_number if c.isdigit())
            data_parts.append(QRStringGenerator._create_tag(QRConstants.TAG_MOBILE_NUMBER, digits))

        if store_label:
            data_parts.append(
                QRStringGenerator._create_tag(QRConstants.TAG_STORE_LABEL, store_label)
            )

        if terminal_label:
            data_parts.append(
                QRStringGenerator._create_tag(QRConstants.TAG_TERMINAL_LABEL, terminal_label)
            )

        combined = "".join(data_parts)
        return QRStringGenerator._create_tag(QRConstants.TAG_ADDITIONAL_DATA, combined)

    @staticmethod
    def _generate_timestamp() -> str:
        """Generate timestamp with language preference."""
        # Current timestamp in milliseconds
        timestamp = str(int(time.time() * 1000))

        # Language preference + timestamp
        lang_timestamp = QRStringGenerator._create_tag(
            QRConstants.TAG_LANGUAGE_PREFERENCE, timestamp
        )

        # Wrap with tag 99
        return QRStringGenerator._create_tag(QRConstants.TAG_TIMESTAMP, lang_timestamp)

    @staticmethod
    def _calculate_crc(qr_data: str) -> str:
        """Calculate CRC-16 using CRC-CCITT polynomial."""
        # Include 6304 in the calculation
        data = qr_data + QRConstants.TAG_CRC + QRConstants.TAG_CRC_LENGTH

        crc = 0xFFFF
        polynomial = 0x1021

        for byte in data.encode("utf-8"):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFF

        crc_hex = format(crc, "04X")
        return QRStringGenerator._create_tag(QRConstants.TAG_CRC, crc_hex)

    @staticmethod
    def _calculate_md5(qr_string: str) -> str:
        """Calculate MD5 hash of QR string."""
        return hashlib.md5(qr_string.encode(QRConstants.DEFAULT_ENCODING)).hexdigest()


def generate_qr_string(request: QRCodeRequest) -> tuple[str, str]:
    """
    Generate QR string from request.

    Args:
        request: QRCodeRequest object

    Returns:
        Tuple of (qr_string, md5_hash)
    """
    return QRStringGenerator.generate(request)
