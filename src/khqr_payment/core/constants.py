class APIConstants:
    BASE_URL = "https://api-bakong.nbc.gov.kh/v1"
    SIT_BASE_URL = "https://sit-api-bakong.nbc.gov.kh/v1"

    ENDPOINTS = {
        "create_qr": "/khqr/create",
        "check_payment": "/check_transaction_by_md5",
        "bulk_payment": "/check_transaction_by_md5_list",
        "get_payment": "/check_transaction_by_md5",
        "account_info": "/check_bakong_account",
    }

    RELAY_BASE_URL = "https://bakongrelay.com/api/v1"
    RELAY_ENDPOINTS = {
        "create_qr": "/khqr/create",
        "check_payment": "/check_transaction_by_md5",
        "bulk_payment": "/check_transaction_by_md5_list",
        "get_payment": "/check_transaction_by_md5",
        "account_info": "/check_bakong_account",
    }


class QRConstants:
    CURRENCY_USD = "USD"
    CURRENCY_KHR = "KHR"
    CURRENCIES = [CURRENCY_USD, CURRENCY_KHR]

    # Payload Format
    TAG_PAYLOAD_FORMAT = "00"
    DEFAULT_PAYLOAD_FORMAT = "01"

    # Point of Initiation
    TAG_POINT_OF_INITIATION = "01"
    STATIC_QR = "11"
    DYNAMIC_QR = "12"

    # Merchant Account Information
    TAG_MERCHANT_ID = "29"
    TAG_GLOBAL_UNIQUE_ID = "00"

    # Merchant Details
    TAG_MERCHANT_NAME = "59"
    TAG_MERCHANT_CITY = "60"

    # Transaction Details
    TAG_MCC = "52"
    DEFAULT_MCC = "5999"
    TAG_COUNTRY_CODE = "58"
    DEFAULT_COUNTRY_CODE = "KH"
    TAG_CURRENCY = "53"
    TAG_AMOUNT = "54"

    # Additional Data Field
    TAG_ADDITIONAL_DATA = "62"
    TAG_BILL_NUMBER = "01"
    TAG_MOBILE_NUMBER = "02"
    TAG_STORE_LABEL = "03"
    TAG_TERMINAL_LABEL = "07"

    # Timestamp
    TAG_TIMESTAMP = "99"
    TAG_LANGUAGE_PREFERENCE = "00"

    # Language Preference
    TAG_LANGUAGE_PREF = "64"
    TAG_MERCHANT_NAME_ALTERNATE = "01"
    TAG_MERCHANT_CITY_ALTERNATE = "02"

    # CRC
    TAG_CRC = "63"
    TAG_CRC_LENGTH = "04"

    # Postal Code & National Info (for parser)
    TAG_POSTAL_CODE = "61"
    TAG_NATIONAL_INFO = "64"
    TAG_ACCOUNT_INFORMATION = "00"
    TAG_ACQUIRING_BANK = "00"

    # Max lengths
    MAX_AMOUNT_KHR = 999999999
    MAX_AMOUNT_USD = 999999.99

    DEFAULT_ENCODING = "UTF-8"
