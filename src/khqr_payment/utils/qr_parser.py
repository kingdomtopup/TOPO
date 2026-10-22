from typing import Any

from khqr_payment.core.constants import QRConstants
from khqr_payment.errors import QRValidationError


class QRParser:
    """Parse Bakong KHQR string."""

    @staticmethod
    def parse(qr_string: str) -> dict[str, Any]:
        """
        Parse QR string into components.

        Args:
            qr_string: QR string to parse

        Returns:
            Dictionary of parsed components

        Raises:
            QRValidationError: If QR string is invalid
        """
        if not qr_string or len(qr_string) < 20:
            raise QRValidationError("Invalid QR string: too short")

        result = {}
        pos = 0
        length = len(qr_string)

        while pos < length:
            if pos + 4 > length:
                break

            tag = qr_string[pos : pos + 2]
            if not tag.isdigit():
                break

            length_str = qr_string[pos + 2 : pos + 4]
            if not length_str.isdigit():
                break

            value_length = int(length_str)
            pos += 4

            if pos + value_length > length:
                break

            value = qr_string[pos : pos + value_length]
            pos += value_length

            QRParser._process_tag(tag, value, result)

        return result

    @staticmethod
    def _process_tag(tag: str, value: str, result: dict[str, Any]) -> None:
        """Process individual tag and extract value."""
        if tag == QRConstants.TAG_PAYLOAD_FORMAT:
            result["payload_format"] = value
        elif tag == QRConstants.TAG_POINT_OF_INITIATION:
            result["point_of_initiation"] = value
            result["is_static"] = value == "12"
        elif tag == QRConstants.TAG_MERCHANT_ID:
            result["merchant_id_data"] = QRParser._parse_merchant_account(value)
        elif tag == QRConstants.TAG_MERCHANT_NAME:
            result["merchant_name"] = value
        elif tag == QRConstants.TAG_MERCHANT_NAME_ALTERNATE:
            result["merchant_name_alternate"] = value
        elif tag == QRConstants.TAG_MERCHANT_CITY:
            result["merchant_city"] = value
        elif tag == QRConstants.TAG_MERCHANT_CITY_ALTERNATE:
            result["merchant_city_alternate"] = value
        elif tag == QRConstants.TAG_POSTAL_CODE:
            result["postal_code"] = value
        elif tag == QRConstants.TAG_TIMESTAMP:
            result["timestamp"] = value
        elif tag == QRConstants.TAG_ADDITIONAL_DATA:
            result["additional_data"] = QRParser._parse_additional_data(value)
        elif tag == QRConstants.TAG_NATIONAL_INFO:
            result["national_info"] = value
        elif tag == "54":
            result["amount"] = QRParser._parse_amount(value)
        elif tag == "53":
            result["currency"] = "KHR" if value == "116" else "USD"
        elif tag == QRConstants.TAG_CRC:
            result["crc"] = value

    @staticmethod
    def _parse_merchant_account(value: str) -> dict[str, str]:
        """Parse merchant account tag (29) to extract all sub-tags."""
        result = {}
        pos = 0
        length = len(value)

        while pos < length:
            if pos + 4 > length:
                break

            tag = value[pos : pos + 2]
            length_str = value[pos + 2 : pos + 4]
            if not length_str.isdigit():
                break

            value_length = int(length_str)
            pos += 4

            if pos + value_length > length:
                break

            sub_value = value[pos : pos + value_length]
            pos += value_length

            if tag == QRConstants.TAG_GLOBAL_UNIQUE_ID:
                result["bank_account"] = sub_value
            elif tag == QRConstants.TAG_ACCOUNT_INFORMATION:
                result["account_information"] = sub_value
            elif tag == QRConstants.TAG_ACQUIRING_BANK:
                result["acquiring_bank"] = sub_value

        if not result:
            result["bank_account"] = value

        return result

    @staticmethod
    def _parse_additional_data(data: str) -> dict[str, str]:
        """Parse additional data field."""
        result = {}
        pos = 0
        length = len(data)

        while pos < length:
            if pos + 4 > length:
                break

            tag = data[pos : pos + 2]
            length_str = data[pos + 2 : pos + 4]
            if not length_str.isdigit():
                break

            value_length = int(length_str)
            pos += 4

            if pos + value_length > length:
                break

            value = data[pos : pos + value_length]
            pos += value_length

            result[tag] = value

        return result

    @staticmethod
    def _parse_amount(value: str) -> float:
        """Parse amount value (supports decimal string and integer format)."""
        try:
            if "." in value:
                return float(value)
            return float(value)
        except ValueError:
            return 0.0


def parse_qr_string(qr_string: str) -> dict[str, Any]:
    """
    Parse QR string into components.

    Args:
        qr_string: QR string to parse

    Returns:
        Dictionary of parsed components
    """
    return QRParser.parse(qr_string)
