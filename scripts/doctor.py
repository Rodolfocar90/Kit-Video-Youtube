#!/usr/bin/env python3
"""Diagnóstico del kit: comprueba dependencias, claves y conexiones.

  python3 scripts/doctor.py            -> comprueba todo
  python3 scripts/doctor.py --offline  -> sin llamadas de red

NUNCA imprime una clave completa. Valida cada conexión con la llamada más
barata posible (listar modelos / consultar saldo), no generando contenido.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import envfile, higgsfield  # noqa: E402
from lib.paths import (ENV_FILE, INPUT_CHANNEL, INPUT_DOCS, INPUT_IMAGES,  # noqa: E402
                       INPUT_VIDEOS, MODELS_FILE, OUTPUT_DIR, ROOT, rel)

OK, FAIL, SKIP, WARN = "[OK]  ", "[FALLO]", "[--]  ", "[AVISO]"


def head(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def check_files() -> list[str]:
    head("1. Archivos y carpetas")
    problems = []
    gitignore = ROOT / ".gitignore"

    if ENV_FILE.exists():
        print(f"{OK} {rel(ENV_FILE)} existe")
        try:
            mode = ENV_FILE.stat().st_mode & 0o777
            if mode & 0o077:
                print(f"{WARN} permisos {oct(mode)} — recomendado 600. "
                      f"Arréglalo con:  chmod 600 {rel(ENV_FILE)}")
            else:
                print(f"{OK} permisos {oct(mode)} (solo tu usuario puede leerlo)")
        except OSError:
            pass
    else:
        problems.append(".env no existe")
        print(f"{FAIL} falta {rel(ENV_FILE)} — ejecuta:  python3 scripts/setup.py")

    if gitignore.exists() and ".env" in gitignore.read_text(encoding="utf-8"):
        print(f"{OK} .env está en .gitignore (tus claves no se subirán)")
    else:
        problems.append(".env NO está protegido en .gitignore")
        print(f"{FAIL} .env NO aparece en .gitignore — RIESGO de subir claves")

    for folder in (INPUT_VIDEOS, INPUT_IMAGES, INPUT_DOCS, INPUT_CHANNEL, OUTPUT_DIR):
        exists = folder.is_dir()
        print(f"{OK if exists else FAIL} carpeta {rel(folder)}")
        if not exists:
            problems.append(f"falta la carpeta {rel(folder)}")
    return problems


def check_secrets() -> list[str]:
    head("2. Claves configuradas (enmascaradas)")
    problems = []
    for key, masked, present in envfile.status_table():
        label = OK if present else SKIP
        print(f"{label} {key:<20} {masked}")
    if not envfile.get("GEMINI_API_KEY") and not envfile.get("GOOGLE_API_KEY"):
        problems.append("GEMINI_API_KEY sin configurar")
        print(f"\n{FAIL} GEMINI_API_KEY es obligatoria.")
        print("      Consíguela gratis en: https://aistudio.google.com/apikey")
        print("      Luego ejecuta:        python3 scripts/setup.py --provider gemini")
    return problems


def check_gemini(offline: bool) -> list[str]:
    head("3. Conexión con Gemini")
    if not (envfile.get("GEMINI_API_KEY") or envfile.get("GOOGLE_API_KEY")):
        print(f"{SKIP} sin clave: no se prueba")
        return []
    if offline:
        print(f"{SKIP} modo --offline")
        return []
    try:
        from lib import gemini  # noqa: PLC0415
        models = gemini.list_models()
    except SystemExit as exc:
        print(f"{FAIL} {exc}")
        return ["Gemini no operativo"]
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "API_KEY_INVALID" in msg or "API key not valid" in msg:
            print(f"{FAIL} la clave no es válida (la API la ha rechazado).")
            print("      Genera otra en: https://aistudio.google.com/apikey")
        elif "PERMISSION_DENIED" in msg:
            print(f"{FAIL} clave sin permisos para la API de Gemini.")
        else:
            print(f"{FAIL} {type(exc).__name__}: {msg[:250]}")
        return ["Gemini no operativo"]

    print(f"{OK} autenticación correcta — {len(models)} modelos disponibles")
    chosen = gemini.resolve_models(refresh=True)
    for kind, label in (("text", "texto"), ("video", "vídeo"), ("image", "imagen")):
        model_id = chosen.get(kind)
        if model_id:
            print(f"{OK} modelo de {label:<7}: {model_id}")
        else:
            print(f"{WARN} sin modelo de {label} en tu cuenta")
            if kind == "image":
                print("      Las miniaturas necesitarán Higgsfield, o pide acceso a un\n"
                      "      modelo Gemini de imagen en https://aistudio.google.com/")
    print(f"{OK} caché de modelos: {rel(MODELS_FILE)} (sin secretos)")
    return []


def check_openrouter(offline: bool) -> list[str]:
    head("4. Conexión con OpenRouter (opcional)")
    key = envfile.get("OPENROUTER_API_KEY")
    if not key:
        print(f"{SKIP} no configurado (no hace falta)")
        return []
    if offline:
        print(f"{SKIP} modo --offline")
        return []
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "kit-video-youtube/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            json.loads(response.read())
        print(f"{OK} autenticación correcta")
    except urllib.error.HTTPError as exc:
        print(f"{FAIL} HTTP {exc.code} — revisa la clave en https://openrouter.ai/keys")
        return ["OpenRouter no operativo"]
    except urllib.error.URLError as exc:
        print(f"{WARN} sin conexión: {exc.reason}")
    print(f"{WARN} recuerda: OpenRouter NO analiza vídeo ni URLs de YouTube.")
    return []


def check_higgsfield(offline: bool) -> list[str]:
    head("5. Conexión con Higgsfield (opcional)")
    if not higgsfield.configured():
        print(f"{SKIP} no configurado (Gemini ya genera miniaturas 16:9)")
        return []
    app = envfile.get("HIGGSFIELD_TEXT_TO_IMAGE_APP", "(sin definir)")
    print(f"{OK} credenciales presentes ({envfile.mask(envfile.get('HF_API_KEY'))})")
    print(f"{OK} application de texto->imagen: {app}")
    if not envfile.get("HIGGSFIELD_IMAGE_EDIT_APP"):
        print(f"{WARN} sin HIGGSFIELD_IMAGE_EDIT_APP: no se podrá usar tu foto como\n"
              "      referencia en Higgsfield. Con Gemini sí se puede.")
    if offline:
        print(f"{SKIP} modo --offline")
        return []
    try:
        # Llamada más barata que existe: pedir una URL de subida (no genera nada).
        higgsfield._request("POST", f"{higgsfield.BASE_URL}/files/generate-upload-url",
                            payload={"content_type": "image/png"}, timeout=30)
        print(f"{OK} la API acepta las credenciales")
    except higgsfield.HiggsfieldError as exc:
        print(f"{FAIL} {exc}")
        return ["Higgsfield no operativo"]
    except SystemExit as exc:
        print(f"{FAIL} {exc}")
        return ["Higgsfield no operativo"]
    return []


def check_material() -> None:
    head("6. Material disponible en input/")
    counts = {
        "vídeos locales": len([p for p in INPUT_VIDEOS.glob("*") if p.is_file()]),
        "imágenes": len([p for p in INPUT_IMAGES.glob("*") if p.is_file()]),
        "documentos": len([p for p in INPUT_DOCS.glob("*") if p.is_file()]),
        "contexto de canal": len([p for p in INPUT_CHANNEL.glob("*.md") if p.is_file()]),
    }
    for label, n in counts.items():
        print(f"{OK if n else SKIP} {label}: {n}")
    if not any(counts.values()):
        print("\n      Aún no has puesto material. Puedes trabajar solo con URLs de\n"
              "      YouTube, o copiar archivos en input/videos, input/images, etc.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico del kit.")
    parser.add_argument("--offline", action="store_true", help="sin llamadas de red")
    args = parser.parse_args()

    envfile.load()
    print("\n=== DIAGNÓSTICO DEL KIT DE VÍDEO PARA YOUTUBE ===")
    problems: list[str] = []
    problems += check_files()
    problems += check_secrets()
    problems += check_gemini(args.offline)
    problems += check_openrouter(args.offline)
    problems += check_higgsfield(args.offline)
    check_material()

    head("RESULTADO")
    if problems:
        print("Hay que arreglar esto antes de empezar:")
        for item in problems:
            print(f"  - {item}")
        print("\nEn la mayoría de casos se resuelve con:  python3 scripts/setup.py")
        return 1
    print("Todo listo. En Claude Code escribe:  /nuevo-video")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
