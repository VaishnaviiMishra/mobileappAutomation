"""Decode barcode PNG assets on the automation host."""

from __future__ import annotations

from pathlib import Path

import zxingcpp
from PIL import Image


def decode_barcode_from_image(image_path: Path | str) -> str:
    """Return decoded text (e.g. CODE128 item EZ ID) from a local barcode image."""
    path = Path(image_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Barcode image not found: {path}")

    results = list(zxingcpp.read_barcodes(Image.open(path)))
    texts = [r.text.strip() for r in results if r.text and r.text.strip()]
    if not texts:
        raise ValueError(f"No barcode found in image: {path}")
    return texts[0]
