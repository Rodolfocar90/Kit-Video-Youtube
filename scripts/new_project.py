#!/usr/bin/env python3
"""Crea la carpeta de un proyecto nuevo en output/.

  python3 scripts/new_project.py "Cómo usar IA en tu negocio"

Genera output/NOMBRE-DEL-VIDEO/ con los 8 archivos del pack en blanco
(con su plantilla) y la subcarpeta thumbnails/.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.paths import project_dir, rel, slugify  # noqa: E402

FILES = {
    "01-RESEARCH.md": "INVESTIGACIÓN",
    "02-ANGLE.md": "ÁNGULO",
    "03-HOOKS.md": "GANCHOS",
    "04-STRUCTURE.md": "ESTRUCTURA",
    "05-TITLES.md": "TÍTULOS",
    "06-THUMBNAILS.md": "MINIATURAS",
    "07-SEO.md": "SEO Y PUBLICACIÓN",
    "08-SOURCES.md": "FUENTES",
}

PLACEHOLDER = """# {seccion} — {titulo}

> Pendiente. Este archivo lo rellena Claude Code durante el flujo `/nuevo-video`.

"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Crea un proyecto de vídeo.")
    parser.add_argument("titulo", help="tema o título provisional del vídeo")
    parser.add_argument("--force", action="store_true", help="reutiliza la carpeta si existe")
    args = parser.parse_args()

    folder = project_dir(args.titulo)
    if folder.exists() and not args.force:
        print(f"[AVISO] Ya existe {rel(folder)}. Usa --force para reutilizarla.")
        return 1

    (folder / "thumbnails").mkdir(parents=True, exist_ok=True)
    for name, seccion in FILES.items():
        path = folder / name
        if not path.exists():
            path.write_text(PLACEHOLDER.format(seccion=seccion, titulo=args.titulo),
                            encoding="utf-8")

    (folder / "proyecto.json").write_text(json.dumps({
        "titulo_provisional": args.titulo,
        "slug": slugify(args.titulo),
        "creado": time.strftime("%Y-%m-%d %H:%M"),
        "fuentes": [],
        "estado": "iniciado",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nProyecto creado: {rel(folder)}")
    for name in sorted(FILES):
        print(f"  - {name}")
    print("  - thumbnails/")
    print("  - proyecto.json\n")
    print(f"PROJECT_DIR={folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
