#!/usr/bin/env python3
"""Analiza material de referencia con Gemini y guarda el resultado en Markdown.

Ejemplos
--------
  # Un vídeo de YouTube (NO se descarga: se pasa la URL a Gemini)
  python3 scripts/analyze.py --youtube "https://youtu.be/XXXX" \
      --prompt-file .claude/skills/video-analysis/prompt-video.md \
      --out output/MI-VIDEO/fuentes/video-01.md

  # Varias fuentes a la vez (comparativa)
  python3 scripts/analyze.py --youtube URL1 --youtube URL2 \
      --prompt-file .claude/skills/research/prompt-comparativa.md \
      --out output/MI-VIDEO/01-RESEARCH.md

  # Todo lo que haya en input/ (vídeos locales, PDFs, imágenes, notas)
  python3 scripts/analyze.py --auto-input --prompt "Resume el material" \
      --out output/MI-VIDEO/fuentes/material-propio.md

Notas
-----
* Las URLs de YouTube deben ser de vídeos PÚBLICOS (límite de la API).
* Con modelos 2.5+ se admiten hasta 10 vídeos por petición.
* Los vídeos locales se suben con la Files API de Gemini y se borran solos
  del servidor a las pocas horas.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import envfile, guard  # noqa: E402
from lib.paths import (DOC_EXT, IMAGE_EXT, INPUT_CHANNEL, INPUT_DOCS,  # noqa: E402
                       INPUT_IMAGES, INPUT_VIDEOS, VIDEO_EXT, rel)

MAX_VIDEOS_PER_REQUEST = 10

REGLAS = """
REGLAS INQUEBRANTABLES DE ESTE ANÁLISIS:

1. Etiqueta CADA afirmación con su origen, usando exactamente estas marcas:
   [FUENTE DEL VÍDEO]  -> lo dice el material analizado (añade timestamp mm:ss)
   [FUENTE EXTERNA]    -> viene de una búsqueda web (añade la URL)
   [INFERENCIA]        -> es tu deducción, no lo dice nadie
2. No inventes fuentes, cifras, estudios, nombres ni enlaces. Si no lo sabes,
   escribe: "No verificado en el material".
3. No copies el guion del material de referencia. Estás INVESTIGANDO para
   crear una pieza original, no reescribiendo la ajena.
4. Cita timestamps reales (mm:ss) siempre que sea posible.
5. Escribe en español de España, claro y sin relleno.
"""


def collect_input_files() -> list[Path]:
    files: list[Path] = []
    for folder, extensions in (
        (INPUT_VIDEOS, VIDEO_EXT),
        (INPUT_IMAGES, IMAGE_EXT),
        (INPUT_DOCS, DOC_EXT),
        (INPUT_CHANNEL, {".md", ".txt"}),
    ):
        if folder.is_dir():
            files += sorted(
                p for p in folder.rglob("*")
                if p.is_file() and p.suffix.lower() in extensions
                and not p.name.startswith(".") and p.name != "LEEME.md"
            )
    return files


def build_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        text = Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.prompt:
        text = args.prompt
    else:
        raise SystemExit("[ERROR] Indica --prompt o --prompt-file.")
    if args.context:
        extra = "\n\n".join(
            f"### Contexto adicional: {Path(p).name}\n{Path(p).read_text(encoding='utf-8')}"
            for p in args.context
        )
        text = f"{text}\n\n{extra}"
    return f"{text}\n{REGLAS}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analiza vídeos, documentos e imágenes con Gemini.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--youtube", action="append", default=[], metavar="URL",
                        help="URL de YouTube pública (repetible)")
    parser.add_argument("--file", action="append", default=[], metavar="RUTA",
                        help="archivo local: vídeo, PDF, imagen, txt (repetible)")
    parser.add_argument("--auto-input", action="store_true",
                        help="usa todo lo que haya en input/")
    parser.add_argument("--prompt", help="instrucciones en línea")
    parser.add_argument("--prompt-file", help="archivo .md con las instrucciones")
    parser.add_argument("--context", action="append", default=[],
                        help="archivo .md de contexto extra (repetible)")
    parser.add_argument("--out", required=True, help="archivo .md de salida")
    parser.add_argument("--model", help="forzar un modelo concreto")
    parser.add_argument("--fps", type=float, help="fotogramas/seg a muestrear del vídeo")
    parser.add_argument("--start", help="recorte: inicio, formato 90s")
    parser.add_argument("--end", help="recorte: fin, formato 600s")
    parser.add_argument("--media-resolution", choices=["low", "medium", "high"],
                        help="resolución de análisis (low = más barato)")
    parser.add_argument("--web-search", action="store_true",
                        help="permite a Gemini buscar en la web para verificar datos")
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--yes", action="store_true", help="no pedir confirmación de coste")
    args = parser.parse_args()

    envfile.load()
    from lib import gemini  # noqa: PLC0415

    youtube_urls = [u.strip() for u in args.youtube if u.strip()]
    for url in youtube_urls:
        if not gemini.is_youtube_url(url):
            raise SystemExit(
                f"[ERROR] No parece una URL de YouTube válida: {url}\n"
                "  Si es un vídeo de otra plataforma, descárgalo y usa --file."
            )
    if len(youtube_urls) > MAX_VIDEOS_PER_REQUEST:
        raise SystemExit(
            f"[ERROR] {len(youtube_urls)} vídeos en una sola petición. El límite de la\n"
            f"  API de Gemini es {MAX_VIDEOS_PER_REQUEST}. Analízalos en tandas y luego"
            " compáralos."
        )

    local_files = [Path(p) for p in args.file]
    if args.auto_input:
        local_files += collect_input_files()
    local_files = [p for p in dict.fromkeys(local_files)]
    for path in local_files:
        if not path.exists():
            raise SystemExit(f"[ERROR] No existe el archivo: {path}")

    if not youtube_urls and not local_files:
        raise SystemExit(
            "[ERROR] No hay material. Usa --youtube, --file o --auto-input.\n"
            f"  Sitios donde poner archivos: {rel(INPUT_VIDEOS)}, {rel(INPUT_IMAGES)},"
            f" {rel(INPUT_DOCS)}"
        )

    videos_local = [p for p in local_files if p.suffix.lower() in VIDEO_EXT]
    kind = "video_youtube" if youtube_urls else ("video_local" if videos_local else "document")
    detalle = ", ".join(
        [f"{len(youtube_urls)} URL(s) de YouTube"] * bool(youtube_urls)
        + [f"{len(local_files)} archivo(s) local(es)"] * bool(local_files)
    )
    if not guard.confirm_cost("Analizar material con Gemini", detalle,
                              units=len(youtube_urls) + len(local_files),
                              assume_yes=args.yes, kind=kind):
        return 1

    cli = gemini.client()
    parts: list[object] = []
    manifest: list[str] = []

    for url in youtube_urls:
        parts.append(gemini.youtube_part(url, fps=args.fps, start=args.start, end=args.end))
        manifest.append(f"- URL de YouTube: {url}")
        print(f"  [fuente] YouTube -> {url}")

    for path in local_files:
        suffix = path.suffix.lower()
        if suffix in {".md", ".txt"}:
            parts.append(f"### Documento de texto: {path.name}\n"
                         f"{path.read_text(encoding='utf-8', errors='replace')}")
            manifest.append(f"- Texto local: {rel(path)}")
            print(f"  [fuente] texto -> {rel(path)}")
        elif suffix in IMAGE_EXT:
            parts.append(gemini.local_image_part(path))
            manifest.append(f"- Imagen local: {rel(path)}")
            print(f"  [fuente] imagen -> {rel(path)}")
        else:
            print(f"  [fuente] subiendo a Gemini -> {rel(path)} (puede tardar)")
            parts.append(gemini.upload_part(cli, path))
            manifest.append(f"- Archivo local: {rel(path)}")

    prompt = build_prompt(args)
    parts.append(prompt)

    model = args.model or gemini.model_for("video" if (youtube_urls or videos_local) else "text")
    resolution = {"low": "MEDIA_RESOLUTION_LOW", "medium": "MEDIA_RESOLUTION_MEDIUM",
                  "high": "MEDIA_RESOLUTION_HIGH"}.get(args.media_resolution or "")

    print(f"\n  Modelo: {model}")
    print("  Analizando… (un vídeo largo puede tardar varios minutos)\n")
    started = time.time()
    text = gemini.generate_text(
        parts, model=model, temperature=args.temperature,
        web_search=args.web_search, media_resolution=resolution,
    )
    elapsed = time.time() - started

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"<!-- Generado por scripts/analyze.py el {time.strftime('%Y-%m-%d %H:%M')} -->\n"
        f"<!-- Modelo: {model} | Búsqueda web: {'sí' if args.web_search else 'no'} -->\n\n"
        "## Material analizado\n\n" + "\n".join(manifest) + "\n\n---\n\n"
    )
    out.write_text(header + text.strip() + "\n", encoding="utf-8")

    print(f"  Listo en {elapsed:.0f}s -> {rel(out)}")
    print(f"  ({len(text.split())} palabras)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
