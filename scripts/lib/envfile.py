"""Lectura y escritura segura de `.env`.

No usa dependencias externas a propósito: menos superficie, menos riesgo.
Ninguna función de este módulo imprime el valor de un secreto.
"""
from __future__ import annotations

import os
import re
import stat
from pathlib import Path

from .paths import ENV_FILE

_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")

# Variables que se consideran secretas: nunca se muestran enteras.
SECRET_KEYS = {
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENROUTER_API_KEY",
    "HF_API_KEY",
    "HF_API_SECRET",
    "HF_KEY",
}


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    # Quita comentarios al final solo si no venía entrecomillado
    return value.split(" #", 1)[0].strip()


def parse(path: Path | None = None) -> dict[str, str]:
    """Devuelve el contenido de .env como dict (sin tocar os.environ)."""
    path = path or ENV_FILE
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = _LINE.match(raw)
        if m:
            data[m.group(1)] = _unquote(m.group(2))
    return data


def load(path: Path | None = None, override: bool = False) -> dict[str, str]:
    """Carga .env en os.environ. Las variables ya presentes ganan por defecto."""
    data = parse(path)
    for key, value in data.items():
        if value == "":
            continue
        if override or not os.environ.get(key):
            os.environ[key] = value
    return data


def write(updates: dict[str, str], path: Path | None = None) -> Path:
    """Actualiza/añade claves en .env preservando comentarios y orden.

    El archivo se crea con permisos 600 (solo el usuario puede leerlo).
    """
    path = path or ENV_FILE
    lines: list[str] = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    remaining = dict(updates)

    for i, raw in enumerate(lines):
        m = _LINE.match(raw)
        if m and m.group(1) in remaining:
            key = m.group(1)
            lines[i] = f"{key}={remaining.pop(key)}"

    if remaining:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("# --- Añadido por scripts/setup.py ---")
        for key, value in remaining.items():
            lines.append(f"{key}={value}")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
    except OSError:
        pass  # Windows / FS sin soporte de permisos POSIX
    return path


def mask(value: str | None) -> str:
    """Representación segura de un secreto. Nunca devuelve la clave completa."""
    if not value:
        return "(sin configurar)"
    value = value.strip()
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * 6}{value[-2:]} ({len(value)} car.)"


def get(key: str, default: str | None = None) -> str | None:
    value = os.environ.get(key)
    return value if value not in (None, "") else default


def require(key: str, where: str) -> str:
    """Devuelve el secreto o explica exactamente dónde conseguirlo."""
    value = get(key)
    if value:
        return value
    raise SystemExit(
        f"\n[FALTA CONFIGURACIÓN] La variable {key} está vacía.\n"
        f"  Consíguela en: {where}\n"
        f"  Después ejecuta:  python3 scripts/setup.py\n"
    )


def status_table() -> list[tuple[str, str, bool]]:
    """(clave, valor enmascarado, configurada) para todas las claves conocidas."""
    rows = []
    for key in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "HF_API_KEY", "HF_API_SECRET"):
        value = get(key)
        rows.append((key, mask(value), bool(value)))
    return rows
