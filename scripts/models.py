#!/usr/bin/env python3
"""Descubre qué modelos de Gemini tiene disponible tu clave.

  python3 scripts/models.py              -> muestra la selección actual
  python3 scripts/models.py --refresh    -> vuelve a consultar la API
  python3 scripts/models.py --all        -> lista todos los modelos

Por qué existe: los IDs de modelo de Gemini cambian cada pocos meses. El kit
no los lleva escritos a fuego; los detecta y guarda en config/models.json
(ese archivo NO contiene secretos y se puede versionar si quieres).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import envfile  # noqa: E402
from lib.paths import MODELS_FILE, rel  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Modelos de Gemini disponibles.")
    parser.add_argument("--refresh", action="store_true", help="consulta la API de nuevo")
    parser.add_argument("--all", action="store_true", help="lista todos los modelos")
    args = parser.parse_args()

    envfile.load()
    from lib import gemini  # noqa: PLC0415

    chosen = gemini.resolve_models(refresh=args.refresh or not MODELS_FILE.exists())

    print("\nModelos que usará el kit")
    print("------------------------")
    for kind, label in (("text", "Texto  "), ("video", "Vídeo  "), ("image", "Imagen ")):
        print(f"  {label}: {chosen.get(kind) or '(ninguno disponible)'}")
    print(f"\n  Guardado en: {rel(MODELS_FILE)}")
    print("  Para fijar uno a mano, pon GEMINI_TEXT_MODEL / GEMINI_VIDEO_MODEL /")
    print("  GEMINI_IMAGE_MODEL en .env (por ejemplo, un 'flash' para gastar menos).")

    if args.all:
        print("\nTodos los modelos de tu cuenta")
        print("------------------------------")
        for model in gemini.list_models():
            tags = []
            if model.is_image_generator:
                tags.append("imagen")
            if model.is_preview:
                tags.append("preview")
            suffix = f"  [{', '.join(tags)}]" if tags else ""
            print(f"  {model.id}{suffix}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
