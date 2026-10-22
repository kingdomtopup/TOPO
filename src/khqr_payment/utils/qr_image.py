import base64
import io
from typing import Literal

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import (
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    SquareModuleDrawer,
)


class QRImageGenerator:
    """Generate QR code images."""

    @staticmethod
    def generate(
        data: str,
        format: Literal["png", "jpeg", "webp"] = "png",
        module_drawer: Literal["square", "gapped", "circle"] = "square",
        fill_color: tuple[int, int, int] = (0, 0, 0),
        back_color: tuple[int, int, int] = (255, 255, 255),
        border: int = 4,
        box_size: int = 10,
    ) -> bytes:
        """Generate QR code image as bytes."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        drawer_map = {
            "square": SquareModuleDrawer(),
            "gapped": GappedSquareModuleDrawer(),
            "circle": CircleModuleDrawer(),
        }

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=drawer_map.get(module_drawer, SquareModuleDrawer()),
            color_mask=SolidFillColorMask(
                front_color=fill_color,
                back_color=back_color,
            ),
        )

        buffer = io.BytesIO()
        img.save(buffer, format=format.upper())
        buffer.seek(0)

        return buffer.getvalue()

    @staticmethod
    def generate_base64_uri(
        data: str,
        format: Literal["png", "jpeg", "webp"] = "png",
        **kwargs,
    ) -> str:
        """Generate QR code as base64 data URI."""
        image_bytes = QRImageGenerator.generate(data, format, **kwargs)
        base64_str = base64.b64encode(image_bytes).decode()
        format_map = {"png": "png", "jpeg": "jpeg", "webp": "webp"}
        mime_type = format_map.get(format, "png")
        return f"data:image/{mime_type};base64,{base64_str}"

    @staticmethod
    def save(
        data: str,
        output_path: str,
        format: Literal["png", "jpeg", "webp"] | None = None,
        **kwargs,
    ) -> str:
        """Save QR code to file."""
        if format is None:
            format = output_path.split(".")[-1].lower()
            if format not in ("png", "jpeg", "webp"):
                format = "png"

        image_bytes = QRImageGenerator.generate(data, format, **kwargs)

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        return output_path


def generate_qr_image(
    data: str,
    format: Literal["png", "jpeg", "webp"] = "png",
    **kwargs,
) -> bytes:
    """Generate QR code image as bytes."""
    return QRImageGenerator.generate(data, format, **kwargs)


def generate_qr_base64_uri(
    data: str,
    format: Literal["png", "jpeg", "webp"] = "png",
    **kwargs,
) -> str:
    """Generate QR code as base64 data URI."""
    return QRImageGenerator.generate_base64_uri(data, format, **kwargs)


def save_qr_image(
    data: str,
    output_path: str,
    format: Literal["png", "jpeg", "webp"] | None = None,
    **kwargs,
) -> str:
    """Save QR code to file."""
    return QRImageGenerator.save(data, output_path, format, **kwargs)
