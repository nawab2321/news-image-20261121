"""Publish the finished Saturday world-news edition in the runner's output directory."""

from os import environ
from pathlib import Path

PNG_HEADER = b"\x89PNG\r\n\x1a\n"
PNG_SIZE = b"\x00\x00\x04\x00" * 2
BYTE_LIMIT = 1_048_576


def main() -> None:
    artwork = Path(__file__).resolve().parent / "assets" / "edition.png"
    image = artwork.read_bytes()
    if (len(image) > BYTE_LIMIT or not image.startswith(PNG_HEADER)
            or image[12:16] != b"IHDR" or image[16:24] != PNG_SIZE):
        raise ValueError("The bundled edition must be a 1024×1024 PNG of at most 1 MiB.")
    output = Path(environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output.mkdir(parents=True, exist_ok=True)
    (output / "entry.png").write_bytes(image)


if __name__ == "__main__":
    main()
