"""Rutas del proyecto y utilidades de nombres."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
CONFIG_DIR = ROOT / "config"
MODELS_FILE = CONFIG_DIR / "models.json"

INPUT_DIR = ROOT / "input"
INPUT_VIDEOS = INPUT_DIR / "videos"
INPUT_IMAGES = INPUT_DIR / "images"
INPUT_DOCS = INPUT_DIR / "documents"
INPUT_CHANNEL = INPUT_DIR / "channel-context"
REFERENCES_FILE = INPUT_DIR / "REFERENCIAS.md"

OUTPUT_DIR = ROOT / "output"

# Extensiones reconocidas al escanear input/
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mpeg", ".mpg"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif"}
DOC_EXT = {".pdf", ".txt", ".md", ".csv", ".json", ".rtf"}

MIME_BY_EXT = {
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".mkv": "video/x-matroska",
    ".webm": "video/webm", ".avi": "video/x-msvideo", ".m4v": "video/mp4",
    ".mpeg": "video/mpeg", ".mpg": "video/mpeg",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".heic": "image/heic", ".heif": "image/heif",
    ".pdf": "application/pdf", ".txt": "text/plain", ".md": "text/markdown",
    ".csv": "text/csv", ".json": "application/json", ".rtf": "text/rtf",
}


def mime_for(path: Path) -> str:
    return MIME_BY_EXT.get(path.suffix.lower(), "application/octet-stream")


def slugify(text: str, max_len: int = 60) -> str:
    """Convierte un título en un nombre de carpeta seguro y legible."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-") or "video"
    return text[:max_len].strip("-").upper()


def project_dir(name: str) -> Path:
    """output/NOMBRE-DEL-VIDEO/"""
    return OUTPUT_DIR / slugify(name)


def rel(path: Path) -> str:
    """Ruta relativa al root del proyecto, para logs legibles."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)
