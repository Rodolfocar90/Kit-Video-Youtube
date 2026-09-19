#!/usr/bin/env python3
"""Asistente de configuración del Kit de Vídeo para YouTube.

  python3 scripts/setup.py              -> configura lo que falte
  python3 scripts/setup.py --reconfigure -> vuelve a preguntar todo
  python3 scripts/setup.py --provider gemini|openrouter|higgsfield

Reglas de seguridad que cumple este script:
  * Las claves se escriben SOLO en .env (permisos 600) y en ninguna otra parte.
  * Al teclearlas no se muestran en pantalla (getpass).
  * Después de guardarlas nunca se imprimen completas: solo enmascaradas.
  * Si falta una clave, se dice exactamente dónde conseguirla.
"""
from __future__ import annotations

import argparse
import getpass
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import envfile  # noqa: E402
from lib.paths import ENV_EXAMPLE, ENV_FILE, INPUT_DIR, OUTPUT_DIR, rel  # noqa: E402

PROVIDERS = {
    "gemini": {
        "titulo": "Gemini / Google AI  (OBLIGATORIO)",
        "porque": "Es el único proveedor que analiza vídeo completo y acepta\n"
                  "            URLs de YouTube de forma nativa. Sin él no hay investigación.",
        "donde": "https://aistudio.google.com/apikey  (hay nivel gratuito)",
        "claves": [("GEMINI_API_KEY", True)],
    },
    "openrouter": {
        "titulo": "OpenRouter  (opcional)",
        "porque": "Solo para tareas de TEXTO si quieres otro modelo como respaldo.\n"
                  "            NO sirve para analizar vídeo ni URLs de YouTube.",
        "donde": "https://openrouter.ai/keys",
        "claves": [("OPENROUTER_API_KEY", True), ("OPENROUTER_MODEL", False)],
    },
    "higgsfield": {
        "titulo": "Higgsfield  (opcional, miniaturas)",
        "porque": "Segundo proveedor de imagen. Gemini ya genera miniaturas 16:9\n"
                  "            con tu foto de referencia, así que esto es opcional.",
        "donde": "https://cloud.higgsfield.ai/  (la clave solo se ve al crearla)",
        "claves": [("HF_API_KEY", True), ("HF_API_SECRET", True),
                   ("HIGGSFIELD_TEXT_TO_IMAGE_APP", False),
                   ("HIGGSFIELD_IMAGE_EDIT_APP", False)],
    },
}

BANNER = """
============================================================
  KIT DE VÍDEO PARA YOUTUBE — configuración inicial
============================================================
"""


def check_dependencies() -> bool:
    print("1) Comprobando dependencias\n")
    ok = True

    version = sys.version_info
    good_python = version >= (3, 9)
    print(f"   [{'OK' if good_python else 'X '}] Python {version.major}.{version.minor}"
          f"{'' if good_python else '  -> se necesita 3.9 o superior'}")
    ok &= good_python

    try:
        import google.genai  # noqa: F401
        print("   [OK] SDK oficial de Google (google-genai)")
    except ImportError:
        ok = False
        print("   [X ] Falta el SDK google-genai")
        print("        Instálalo con:  pip3 install -r requirements.txt")

    for tool, why in (("git", "control de versiones (opcional)"),
                      ("ffmpeg", "recortar vídeos locales (opcional)")):
        present = shutil.which(tool) is not None
        print(f"   [{'OK' if present else '--'}] {tool} — {why}")

    print()
    return ok


def offer_install() -> None:
    if not sys.stdin.isatty():
        return
    answer = input("   ¿Instalo ahora las dependencias con pip? [s/N]: ").strip().lower()
    if answer in ("s", "si", "sí", "y", "yes"):
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        print(f"   Ejecutando: {' '.join(cmd)}\n")
        subprocess.run(cmd, check=False)
        print()


def ensure_env_file() -> None:
    if ENV_FILE.exists():
        return
    if ENV_EXAMPLE.exists():
        ENV_FILE.write_text(ENV_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"   Creado {rel(ENV_FILE)} a partir de {rel(ENV_EXAMPLE)}")
    else:
        ENV_FILE.write_text("# Secretos locales. NO subir a Git.\n", encoding="utf-8")
    try:
        ENV_FILE.chmod(0o600)
    except OSError:
        pass


def ask_secret(key: str, *, current: str, secret: bool) -> str | None:
    """Pregunta un valor. Devuelve None si el usuario lo deja igual."""
    shown = envfile.mask(current) if secret else (current or "(vacío)")
    print(f"      {key}   actual: {shown}")
    prompt = "      nuevo valor (Enter = dejar como está): "
    value = getpass.getpass(prompt) if secret else input(prompt)
    value = value.strip()
    if not value:
        return None
    if secret and len(value) < 8:
        print("      [!] Ese valor parece demasiado corto para ser una clave válida.")
    return value


def configure(provider: str, existing: dict[str, str], reconfigure: bool) -> dict[str, str]:
    meta = PROVIDERS[provider]
    required_key = meta["claves"][0][0]
    already = bool(existing.get(required_key))

    print("-" * 60)
    print(f"   {meta['titulo']}")
    print(f"   Para qué: {meta['porque']}")
    print(f"   Dónde conseguirla: {meta['donde']}")
    if already:
        print(f"   Estado: YA CONFIGURADO ({envfile.mask(existing.get(required_key))})")
    print("-" * 60)

    if not sys.stdin.isatty():
        print("   (modo no interactivo: se omite)\n")
        return {}

    if already and not reconfigure:
        answer = input("   ¿Reconfigurar este proveedor? [s/N]: ").strip().lower()
        if answer not in ("s", "si", "sí", "y", "yes"):
            print()
            return {}
    elif provider != "gemini" and not already:
        answer = input("   ¿Configurar este proveedor ahora? [s/N]: ").strip().lower()
        if answer not in ("s", "si", "sí", "y", "yes"):
            print("   Omitido. Puedes configurarlo más tarde con:\n"
                  f"     python3 scripts/setup.py --provider {provider}\n")
            return {}

    updates: dict[str, str] = {}
    for key, is_secret in meta["claves"]:
        value = ask_secret(key, current=existing.get(key, ""), secret=is_secret)
        if value is not None:
            updates[key] = value
    print()
    return updates


def main() -> int:
    parser = argparse.ArgumentParser(description="Configura el kit paso a paso.")
    parser.add_argument("--reconfigure", action="store_true",
                        help="vuelve a preguntar incluso lo ya configurado")
    parser.add_argument("--provider", choices=sorted(PROVIDERS),
                        help="configura solo un proveedor")
    parser.add_argument("--skip-deps", action="store_true")
    args = parser.parse_args()

    print(BANNER)

    if not args.skip_deps and not check_dependencies():
        offer_install()

    print("2) Preparando carpetas\n")
    for folder in (INPUT_DIR, OUTPUT_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    ensure_env_file()
    print(f"   Secretos en: {rel(ENV_FILE)}  (permisos 600, ignorado por Git)\n")

    print("3) Claves de API\n")
    existing = envfile.parse()
    targets = [args.provider] if args.provider else list(PROVIDERS)

    updates: dict[str, str] = {}
    for provider in targets:
        updates.update(configure(provider, existing, args.reconfigure))

    if updates:
        envfile.write(updates)
        print(f"   Guardado en {rel(ENV_FILE)}:")
        for key in updates:
            is_secret = key in envfile.SECRET_KEYS
            print(f"     {key} = "
                  f"{envfile.mask(updates[key]) if is_secret else updates[key]}")
        print()
    else:
        print("   Sin cambios.\n")

    print("4) Siguiente paso\n")
    print("   Valida las conexiones (no muestra ninguna clave):")
    print("     python3 scripts/doctor.py\n")
    print("   Y después, en Claude Code:")
    print("     /nuevo-video\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
