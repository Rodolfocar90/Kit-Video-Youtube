"""Protección de costes: nada que cueste dinero se ejecuta sin avisar."""
from __future__ import annotations

import os
import sys

# Órdenes de magnitud, NO precios oficiales. Sirven para que el usuario
# entienda el tamaño de la operación antes de confirmar.
SCALE = {
    "video_youtube": "Analizar 1 vídeo de YouTube consume tokens de entrada "
                     "proporcionales a su duración (un vídeo largo = muchos tokens).",
    "video_local":   "Subir y analizar un vídeo local consume tokens por duración "
                     "y ocupa la Files API temporalmente.",
    "document":      "Analizar documentos/imágenes tiene coste bajo.",
    "text":          "Generación de texto: coste bajo.",
    "image":         "Generar imágenes tiene coste POR IMAGEN y suele ser la "
                     "operación más cara del kit.",
    "web_search":    "Búsqueda web con grounding: coste por consulta.",
}


def _interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def confirm_cost(action: str, detail: str, *, units: int = 1,
                 assume_yes: bool = False, kind: str = "text") -> bool:
    """Informa del coste y pide confirmación explícita.

    Devuelve True si se puede continuar. En modo no interactivo exige
    `assume_yes` (flag --yes) para no bloquearse nunca en silencio.
    """
    if os.environ.get("CONFIRM_PAID_ACTIONS", "1") not in ("1", "true", "yes"):
        return True

    print("\n" + "=" * 62)
    print("  OPERACIÓN CON COSTE")
    print("=" * 62)
    print(f"  Acción      : {action}")
    print(f"  Detalle     : {detail}")
    print(f"  Unidades    : {units}")
    print(f"  Escala      : {SCALE.get(kind, SCALE['text'])}")
    print("=" * 62)

    if assume_yes:
        print("  Confirmado con --yes\n")
        return True

    if not _interactive():
        print("  Entorno no interactivo y sin --yes: OPERACIÓN CANCELADA.\n")
        return False

    answer = input("  ¿Continuar? [s/N]: ").strip().lower()
    print()
    return answer in ("s", "si", "sí", "y", "yes")


def enforce_image_limit(requested: int) -> int:
    """Aplica MAX_IMAGES_PER_RUN para evitar facturas sorpresa."""
    try:
        cap = int(os.environ.get("MAX_IMAGES_PER_RUN", "3"))
    except ValueError:
        cap = 3
    cap = max(1, cap)
    if requested > cap:
        print(f"[LÍMITE] Pediste {requested} imágenes; el límite configurado "
              f"(MAX_IMAGES_PER_RUN) es {cap}. Se generarán {cap}.")
        return cap
    return requested
