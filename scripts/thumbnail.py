#!/usr/bin/env python3
"""Genera miniaturas 16:9 listas para YouTube.

  # Con Gemini (recomendado: admite tu foto como referencia de serie)
  python3 scripts/thumbnail.py \
      --prompt-file output/MI-VIDEO/thumbnails/prompt-01.txt \
      --reference input/images/creador.jpg \
      --out output/MI-VIDEO/thumbnails/thumbnail-01.png

  # Con Higgsfield (si lo has configurado)
  python3 scripts/thumbnail.py --provider higgsfield --prompt "..." --out ...

Proveedores
-----------
gemini      (por defecto) Modelo Gemini de imagen. Soporta aspect_ratio 16:9
            nativo y acepta imágenes de referencia, así que puede usar la
            foto real del creador.
higgsfield  API oficial (api.higgsfield.ai). Requiere HF_API_KEY + HF_API_SECRET
            y la ruta de la "application" del modelo en .env.

Seguridad y coste
-----------------
Generar imágenes es la operación más cara del kit: siempre pide confirmación
y respeta MAX_IMAGES_PER_RUN.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import envfile, guard, higgsfield  # noqa: E402
from lib.paths import IMAGE_EXT, rel  # noqa: E402

CALIDAD = (
    "Formato: miniatura de YouTube, 16:9, pensada para leerse a tamaño muy "
    "pequeño en un móvil. Sujeto principal grande y recortado con claridad, "
    "alto contraste entre sujeto y fondo, iluminación limpia, colores "
    "saturados pero no chillones. Si el diseño incluye texto, máximo 4 "
    "palabras, tipografía gruesa y perfectamente legible, sin faltas de "
    "ortografía. Nada de marcas de agua, logotipos de terceros, bordes ni "
    "texto decorativo ilegible."
)


def resolve_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        text = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    elif args.prompt:
        text = args.prompt.strip()
    else:
        raise SystemExit("[ERROR] Indica --prompt o --prompt-file.")
    if args.reference:
        text += ("\n\nLa persona que aparece en la imagen de referencia es el "
                 "creador del vídeo: mantén su parecido real, su edad y sus "
                 "rasgos. No lo sustituyas por otra persona ni lo idealices.")
    return f"{text}\n\n{CALIDAD}"


def save(images: list[bytes], out: Path, expected: int) -> list[Path]:
    out.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, data in enumerate(images):
        if expected == 1 and index == 0:
            target = out
        else:
            target = out.with_name(f"{out.stem}-{index + 1}{out.suffix}")
        target.write_bytes(data)
        written.append(target)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera miniaturas 16:9.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--prompt", help="descripción de la miniatura")
    parser.add_argument("--prompt-file", help="archivo con la descripción")
    parser.add_argument("--reference", action="append", default=[], metavar="RUTA",
                        help="foto del creador u otra referencia visual (repetible)")
    parser.add_argument("--out", required=True, help="archivo .png de salida")
    parser.add_argument("--provider", choices=["gemini", "higgsfield"], default="gemini")
    parser.add_argument("--count", type=int, default=1, help="nº de variantes")
    parser.add_argument("--aspect-ratio", default="16:9")
    parser.add_argument("--application", help="ruta de application (solo Higgsfield)")
    parser.add_argument("--model", help="forzar modelo (solo Gemini)")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    envfile.load()

    references = [Path(p) for p in args.reference]
    for path in references:
        if not path.exists():
            raise SystemExit(f"[ERROR] No existe la imagen de referencia: {path}")
        if path.suffix.lower() not in IMAGE_EXT:
            raise SystemExit(f"[ERROR] {path.name} no parece una imagen "
                             f"({', '.join(sorted(IMAGE_EXT))}).")

    count = guard.enforce_image_limit(max(1, args.count))
    prompt = resolve_prompt(args)
    out = Path(args.out)

    detalle = (f"{count} imagen(es) {args.aspect_ratio} con {args.provider}"
               + (f", referencia: {', '.join(p.name for p in references)}"
                  if references else ", sin referencia"))
    if not guard.confirm_cost("Generar miniatura", detalle, units=count,
                              assume_yes=args.yes, kind="image"):
        return 1

    started = time.time()

    if args.provider == "gemini":
        from lib import gemini  # noqa: PLC0415
        print(f"\n  Proveedor: Gemini\n  Modelo: {args.model or gemini.model_for('image')}")
        images = gemini.generate_images(
            prompt, reference_images=references, aspect_ratio=args.aspect_ratio,
            count=count, model=args.model,
        )
        written = save(images, out, count)
    else:
        if not higgsfield.configured():
            raise SystemExit(
                "\n[NO CONFIGURADO] Higgsfield necesita HF_API_KEY y HF_API_SECRET.\n"
                "  Consíguelas en: https://cloud.higgsfield.ai/\n"
                "  Configúralas:   python3 scripts/setup.py --provider higgsfield\n"
                "  O usa Gemini:   --provider gemini\n"
            )
        print("\n  Proveedor: Higgsfield (api.higgsfield.ai)")
        written = []
        for index in range(count):
            result = higgsfield.generate_image(
                prompt, aspect_ratio=args.aspect_ratio,
                reference=references[0] if references else None,
                application=args.application,
            )
            urls = higgsfield.image_urls(result)
            if not urls:
                raise SystemExit(f"[ERROR] Higgsfield no devolvió imagen: {result}")
            target = out if count == 1 else out.with_name(f"{out.stem}-{index + 1}{out.suffix}")
            written.append(higgsfield.download(urls[0], target))

    print(f"\n  Listo en {time.time() - started:.0f}s:")
    for path in written:
        size_kb = path.stat().st_size / 1024
        print(f"    {rel(path)}  ({size_kb:.0f} KB)")
    print("\n  Comprueba que el texto es legible a tamaño pequeño antes de usarla.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
