import hashlib
import urllib.parse

from khqr_payment.core.constants import APIConstants


class DeeplinkGenerator:
    """Generate Bakong payment deeplink."""

    @staticmethod
    def generate(
        qr_string: str,
        callback: str,
        app_icon_url: str | None = None,
        app_name: str | None = None,
        use_relay: bool = False,
    ) -> str:
        """
        Generate deeplink from QR string.

        Args:
            qr_string: QR string from create_qr
            callback: Callback URL after payment
            app_icon_url: App icon URL (optional)
            app_name: App name (optional)
            use_relay: Use Bakong Relay API (optional)

        Returns:
            Generated deeplink URL
        """
        base_url = APIConstants.RELAY_BASE_URL if use_relay else "https://bakong.page.link"

        params = {
            "data": qr_string,
            "callback": callback,
        }

        if app_icon_url:
            params["icon"] = app_icon_url
        if app_name:
            params["name"] = app_name

        query_string = urllib.parse.urlencode(params)

        if use_relay:
            return f"{base_url}/create?{query_string}"

        hash_value = hashlib.sha256(query_string.encode()).hexdigest()[:8]
        return f"{base_url}/?{query_string}&hash={hash_value}"

    @staticmethod
    def generate_native(qr_string: str, callback: str, app_scheme: str | None = None) -> str:
        """
        Generate native app deeplink (bakong://).

        Args:
            qr_string: QR string from create_qr
            callback: Callback URL or custom scheme
            app_scheme: Custom app scheme (e.g., myapp://)

        Returns:
            Native deeplink URL
        """
        if app_scheme:
            encoded_data = qr_string.replace(" ", "+")
            return (
                f"{app_scheme}payment?data={encoded_data}&callback={urllib.parse.quote(callback)}"
            )

        encoded_data = qr_string.replace(" ", "+")
        return f"bakong://payment?data={encoded_data}&callback={urllib.parse.quote(callback)}"


def generate_deeplink(
    qr_string: str,
    callback: str,
    app_icon_url: str | None = None,
    app_name: str | None = None,
    use_relay: bool = False,
    native: bool = False,
    app_scheme: str | None = None,
) -> str:
    """
    Generate deeplink from QR string.

    Args:
        qr_string: QR string from create_qr
        callback: Callback URL after payment
        app_icon_url: App icon URL (optional)
        app_name: App name (optional)
        use_relay: Use Bakong Relay API (optional)
        native: Use native bakong:// protocol (optional, for direct app opening)
        app_scheme: Custom app scheme for native deeplink (e.g., myapp://)

    Returns:
        Generated deeplink URL
    """
    if native:
        return DeeplinkGenerator.generate_native(qr_string, callback, app_scheme)
    return DeeplinkGenerator.generate(qr_string, callback, app_icon_url, app_name, use_relay)


def generate_native_deeplink(
    qr_string: str,
    callback: str,
    app_scheme: str | None = None,
) -> str:
    """
    Generate native app deeplink (bakong://).

    Args:
        qr_string: QR string from create_qr
        callback: Callback URL after payment
        app_scheme: Custom app scheme (e.g., myapp://)

    Returns:
        Native deeplink URL (bakong://payment?data=...)
    """
    return DeeplinkGenerator.generate_native(qr_string, callback, app_scheme)
