#!/usr/bin/env python3
"""Verificación de datos con búsqueda web real (grounding de Gemini).

  python3 scripts/web_research.py "cifras de adopción de IA en pymes 2026" \
      --out output/MI-VIDEO/fuentes/verificacion.md

Cuándo usarlo: cuando Claude Code NO tenga herramienta de búsqueda web
disponible, o cuando quieras las URLs de respaldo en un archivo.
Si Claude Code SÍ tiene WebSearch, puede usarla directamente; este script
es el plan B y además deja rastro documental de las fuentes.

Todo lo que sale de aquí es [FUENTE EXTERNA] y lleva su URL.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import envfile, guard  # noqa: E402
from lib.paths import rel  # noqa: E402

SISTEMA = """Eres un verificador de datos para un creador de YouTube.

Para cada afirmación que te pidan comprobar:
1. Busca en la web antes de responder.
2. Marca el resultado como: CONFIRMADO / MATIZADO / DESMENTIDO / SIN DATOS.
3. Da la cifra o el hecho exacto y la fecha del dato.
4. Cita la URL concreta de cada dato. Si no encuentras fuente, di
   "SIN DATOS" en lugar de rellenar con suposiciones.
5. Señala si hay datos más recientes que contradigan lo anterior.

Nunca inventes una fuente, una URL ni una cifra. Todo lo que escribas
aquí se etiqueta como [FUENTE EXTERNA].
Responde en español de España, en Markdown."""


def extract_sources(response) -> list[tuple[str, str]]:
    """Saca (título, url) de los metadatos de grounding, si los hay."""
    found: list[tuple[str, str]] = []
    for cand in getattr(response, "candidates", None) or []:
        meta = getattr(cand, "grounding_metadata", None)
        for chunk in getattr(meta, "grounding_chunks", None) or []:
            web = getattr(chunk, "web", None)
            uri = getattr(web, "uri", None)
            if uri:
                found.append((getattr(web, "title", "") or uri, uri))
    seen, unique = set(), []
    for title, uri in found:
        if uri not in seen:
            seen.add(uri)
            unique.append((title, uri))
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica datos con búsqueda web.")
    parser.add_argument("consulta", help="qué hay que verificar o investigar")
    parser.add_argument("--out", required=True, help="archivo .md de salida")
    parser.add_argument("--context-file", help="archivo .md con las afirmaciones a verificar")
    parser.add_argument("--model", help="forzar modelo")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    envfile.load()
    from lib import gemini  # noqa: PLC0415
    from google.genai import types  # noqa: PLC0415

    if not guard.confirm_cost("Búsqueda web con grounding de Gemini",
                              args.consulta[:120], assume_yes=args.yes, kind="web_search"):
        return 1

    pregunta = args.consulta
    if args.context_file:
        pregunta += ("\n\nAfirmaciones a verificar (extraídas del material):\n"
                     + Path(args.context_file).read_text(encoding="utf-8")[:20000])

    cli = gemini.client()
    model = args.model or gemini.model_for("text")
    print(f"\n  Modelo: {model}\n  Buscando…\n")
    response = cli.models.generate_content(
        model=model,
        contents=[pregunta],
        config=types.GenerateContentConfig(
            system_instruction=SISTEMA,
            temperature=0.2,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    text = getattr(response, "text", "") or ""
    sources = extract_sources(response)

    body = [
        f"<!-- Generado por scripts/web_research.py el {time.strftime('%Y-%m-%d %H:%M')} -->",
        f"<!-- Modelo: {model} | Búsqueda web: sí -->",
        "",
        f"# Verificación: {args.consulta}",
        "",
        text.strip(),
        "",
        "## Fuentes devueltas por la búsqueda  [FUENTE EXTERNA]",
        "",
    ]
    if sources:
        body += [f"- [{title}]({uri})" for title, uri in sources]
    else:
        body.append("_La búsqueda no devolvió URLs de respaldo. Trata el contenido "
                    "anterior como NO verificado._")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
    print(f"  Listo -> {rel(out)}  ({len(sources)} fuentes)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
