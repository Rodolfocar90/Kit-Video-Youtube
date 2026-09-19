"""Capa sobre el SDK oficial `google-genai`.

Puntos importantes de diseño:

* Los IDs de modelo NO están hardcodeados. Los modelos de Gemini cambian
  cada pocos meses, así que el kit los DESCUBRE con `client.models.list()`
  y los cachea en config/models.json. Así el proyecto no caduca.
* El análisis de vídeo usa `types.FileData(file_uri=...)`, que acepta URLs
  de YouTube de forma nativa: no descargamos nada de YouTube.
* La clave nunca se imprime ni se escribe en ningún archivo de salida.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from . import envfile
from .paths import MODELS_FILE, mime_for

GEMINI_KEY_URL = "https://aistudio.google.com/apikey"

YOUTUBE_RE = re.compile(
    r"^https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?[^ ]*v=|live/|shorts/|embed/)|youtu\.be/)[\w-]{6,}",
    re.I,
)

# Preferencias por familia. Se usan para ELEGIR entre los modelos que la
# cuenta del usuario realmente expone, nunca para inventar un ID.
PREFERENCE = {
    "text":  ("pro", "flash", "lite"),
    "video": ("pro", "flash", "lite"),
    "image": ("image",),
}


def is_youtube_url(value: str) -> bool:
    return bool(YOUTUBE_RE.match(value.strip()))


def _import_sdk():
    try:
        from google import genai  # noqa: PLC0415
        from google.genai import types  # noqa: PLC0415
    except ImportError as exc:
        raise SystemExit(
            "\n[FALTA DEPENDENCIA] No está instalado el SDK oficial de Google.\n"
            "  Instálalo con:  pip3 install -r requirements.txt\n"
            f"  (detalle: {exc})\n"
        ) from exc
    return genai, types


def client():
    """Cliente autenticado. La clave se lee de GEMINI_API_KEY."""
    genai, _ = _import_sdk()
    key = envfile.get("GEMINI_API_KEY") or envfile.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit(
            "\n[FALTA CONFIGURACIÓN] GEMINI_API_KEY está vacía.\n"
            f"  Consigue una clave gratis en: {GEMINI_KEY_URL}\n"
            "  Después ejecuta:  python3 scripts/setup.py\n"
        )
    return genai.Client(api_key=key)


# ----------------------------------------------------------------------
#  Descubrimiento de modelos
# ----------------------------------------------------------------------
@dataclass
class ModelInfo:
    id: str
    display_name: str
    actions: tuple[str, ...]

    @property
    def is_image_generator(self) -> bool:
        """True solo para modelos Gemini con salida de imagen.

        Deliberadamente excluye la familia `imagen-*`: esos modelos usan otra
        llamada (`models.generate_images`) y NO aceptan una foto de referencia,
        que es justo lo que necesitamos para las miniaturas del creador.
        """
        return bool(re.search(r"-image(?:-|$)", self.id.lower()))

    @property
    def is_preview(self) -> bool:
        low = self.id.lower()
        return any(tag in low for tag in ("preview", "exp", "experimental"))


def list_models(cli=None) -> list[ModelInfo]:
    cli = cli or client()
    found: list[ModelInfo] = []
    for m in cli.models.list():
        name = (m.name or "").removeprefix("models/")
        if not name:
            continue
        actions = tuple(m.supported_actions or ())
        if actions and "generateContent" not in actions:
            continue
        found.append(ModelInfo(name, m.display_name or name, actions))
    return sorted(found, key=lambda x: x.id)


def _version_key(model_id: str) -> tuple:
    """Ordena por número de versión descendente (3.8 > 3.1 > 2.5)."""
    nums = [float(n) for n in re.findall(r"(\d+(?:\.\d+)?)", model_id)]
    return tuple(nums[:2]) if nums else (0.0,)


def _pick(models: Iterable[ModelInfo], kind: str) -> str | None:
    pool = [m for m in models if m.is_image_generator == (kind == "image")]
    # Evita previews/experimentales si hay alternativa estable
    stable = [m for m in pool if not m.is_preview]
    for candidates in (stable, pool):
        for tag in PREFERENCE[kind]:
            matches = [m for m in candidates if tag in m.id.lower()]
            if matches:
                matches.sort(key=lambda m: _version_key(m.id), reverse=True)
                return matches[0].id
        if candidates:
            return sorted(candidates, key=lambda m: _version_key(m.id), reverse=True)[0].id
    return None


def resolve_models(refresh: bool = False, cli=None) -> dict[str, str]:
    """Devuelve {'text','video','image'} con IDs reales.

    Prioridad: variable de entorno > caché config/models.json > API en vivo.
    """
    forced = {
        "text": envfile.get("GEMINI_TEXT_MODEL"),
        "video": envfile.get("GEMINI_VIDEO_MODEL"),
        "image": envfile.get("GEMINI_IMAGE_MODEL"),
    }
    if not refresh and all(forced.values()):
        return {k: v for k, v in forced.items() if v}

    cached: dict[str, Any] = {}
    if MODELS_FILE.exists() and not refresh:
        try:
            cached = json.loads(MODELS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cached = {}

    chosen = dict(cached.get("chosen", {}))
    if refresh or not all(chosen.get(k) for k in ("text", "video", "image")):
        models = list_models(cli)
        discovered = {k: _pick(models, k) for k in ("text", "video", "image")}
        chosen = {k: (forced.get(k) or discovered.get(k) or chosen.get(k)) for k in discovered}
        MODELS_FILE.parent.mkdir(parents=True, exist_ok=True)
        MODELS_FILE.write_text(json.dumps({
            "_comentario": "Generado por scripts/models.py. No contiene secretos. "
                           "Bórralo para volver a detectar modelos.",
            "actualizado": time.strftime("%Y-%m-%d %H:%M"),
            "chosen": chosen,
            "disponibles": [m.id for m in models],
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for k, v in forced.items():
        if v:
            chosen[k] = v
    return chosen


def model_for(kind: str) -> str:
    models = resolve_models()
    model_id = models.get(kind)
    if not model_id:
        raise SystemExit(
            f"\n[SIN MODELO] No se ha encontrado un modelo de tipo '{kind}' en tu cuenta.\n"
            "  Ejecuta:  python3 scripts/models.py --refresh\n"
            f"  O fija uno a mano en .env (GEMINI_{kind.upper()}_MODEL).\n"
        )
    return model_id


# ----------------------------------------------------------------------
#  Construcción de entradas (vídeo, imagen, documento)
# ----------------------------------------------------------------------
def youtube_part(url: str, *, fps: float | None = None,
                 start: str | None = None, end: str | None = None):
    """Parte de contenido para una URL de YouTube (sin descargar el vídeo).

    Verificado contra el SDK oficial: types.FileData(file_uri=...) admite
    URLs de YouTube. Solo funciona con vídeos PÚBLICOS.
    """
    _, types = _import_sdk()
    part = types.Part(file_data=types.FileData(file_uri=url.strip()))
    if fps or start or end:
        part.video_metadata = types.VideoMetadata(
            fps=fps, start_offset=start, end_offset=end
        )
    return part


def upload_part(cli, path: Path, *, wait: bool = True):
    """Sube un archivo local con la Files API y espera a que esté ACTIVE."""
    _, types = _import_sdk()
    path = Path(path)
    file = cli.files.upload(file=str(path))
    if wait:
        deadline = time.time() + 900  # 15 min máx. para vídeos largos
        while getattr(file.state, "name", str(file.state)) == "PROCESSING":
            if time.time() > deadline:
                raise SystemExit(f"[TIMEOUT] Gemini sigue procesando {path.name} tras 15 min.")
            time.sleep(5)
            file = cli.files.get(name=file.name)
        state = getattr(file.state, "name", str(file.state))
        if state == "FAILED":
            raise SystemExit(f"[ERROR] Gemini no pudo procesar {path.name}.")
    return types.Part.from_uri(file_uri=file.uri, mime_type=file.mime_type or mime_for(path))


def local_image_part(path: Path):
    """Imagen local en línea (para fotos de referencia de miniatura)."""
    _, types = _import_sdk()
    path = Path(path)
    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_for(path))


# ----------------------------------------------------------------------
#  Llamadas
# ----------------------------------------------------------------------
def generate_text(parts: list[Any], *, model: str | None = None,
                  system: str | None = None, temperature: float = 0.7,
                  web_search: bool = False, media_resolution: str | None = None) -> str:
    """Una llamada de texto/multimodal. Devuelve el texto plano."""
    _, types = _import_sdk()
    cli = client()
    config: dict[str, Any] = {"temperature": temperature}
    if system:
        config["system_instruction"] = system
    if web_search:
        config["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    if media_resolution:
        config["media_resolution"] = media_resolution

    response = cli.models.generate_content(
        model=model or model_for("text"),
        contents=parts,
        config=types.GenerateContentConfig(**config),
    )
    text = getattr(response, "text", None)
    if text:
        return text
    # Recolecta texto parte a parte si `.text` viene vacío
    chunks = []
    for cand in getattr(response, "candidates", None) or []:
        for part in getattr(cand.content, "parts", None) or []:
            if getattr(part, "text", None):
                chunks.append(part.text)
    if not chunks:
        raise SystemExit("[ERROR] Gemini devolvió una respuesta vacía. "
                         "Revisa el prompt o prueba otro modelo.")
    return "\n".join(chunks)


def generate_images(prompt: str, *, reference_images: list[Path] | None = None,
                    aspect_ratio: str = "16:9", count: int = 1,
                    model: str | None = None) -> list[bytes]:
    """Genera imágenes con Gemini. Soporta 16:9 nativo y fotos de referencia.

    Verificado: types.ImageConfig(aspect_ratio=...) acepta "16:9" y
    response_modalities=["IMAGE"] devuelve la imagen en inline_data.
    """
    _, types = _import_sdk()
    cli = client()
    parts: list[Any] = []
    for ref in reference_images or []:
        parts.append(local_image_part(Path(ref)))
    parts.append(prompt)

    images: list[bytes] = []
    for _ in range(max(1, count)):
        response = cli.models.generate_content(
            model=model or model_for("image"),
            contents=parts,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    person_generation="ALLOW_ADULT",
                ),
            ),
        )
        for cand in getattr(response, "candidates", None) or []:
            for part in getattr(cand.content, "parts", None) or []:
                blob = getattr(part, "inline_data", None)
                if blob and getattr(blob, "data", None):
                    images.append(blob.data)
    if not images:
        raise SystemExit(
            "[ERROR] El modelo no devolvió imagen.\n"
            "  Causas habituales: el modelo elegido no genera imágenes, o el\n"
            "  prompt fue bloqueado por políticas de contenido.\n"
            "  Comprueba:  python3 scripts/models.py"
        )
    return images
