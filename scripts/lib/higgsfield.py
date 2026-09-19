"""Cliente mínimo de la API oficial de Higgsfield.

ORIGEN DE ESTE CONTRATO — importante:
El contrato de más abajo NO está inventado. Está extraído del código fuente
del SDK oficial `higgsfield-client` 0.2.0 (PyPI / github.com/higgsfield-ai):

    BASE_URL            https://api.higgsfield.ai
    Autenticación       Authorization: Key <API_KEY>:<API_SECRET>
    Enviar trabajo      POST  {BASE_URL}/{application}        body = arguments JSON
                        query opcional  ?hf_webhook=<url>
                        respuesta       {request_id, status_url, cancel_url}
    Consultar estado    GET   {BASE_URL}/requests/{id}/status
    Cancelar            POST  {BASE_URL}/requests/{id}/cancel
    Subir archivo       POST  {BASE_URL}/files/generate-upload-url
                        body  {"content_type": "image/png"}
                        -> {public_url, upload_url, upload_headers}
                        luego PUT upload_url con los bytes
    Estados             queued | in_progress | completed | failed | nsfw | canceled

Se usa la librería estándar (urllib) a propósito: el kit no necesita
dependencias extra para hablar con esta API. Si prefieres el SDK oficial:
    pip3 install higgsfield-client

La RUTA DE LA APPLICATION (p. ej. `bytedance/seedream/v4/text-to-image`) se
lee de .env porque el catálogo de modelos cambia. Cópiala exactamente de la
página del modelo en https://cloud.higgsfield.ai/ — este kit no adivina rutas.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import envfile
from .paths import mime_for

BASE_URL = "https://api.higgsfield.ai"
CREDENTIALS_URL = "https://cloud.higgsfield.ai/"
USER_AGENT = "kit-video-youtube/1.0"

DONE = {"completed", "failed", "nsfw", "canceled"}


class HiggsfieldError(RuntimeError):
    pass


def configured() -> bool:
    return bool(
        envfile.get("HF_KEY")
        or (envfile.get("HF_API_KEY") and envfile.get("HF_API_SECRET"))
    )


def _credential() -> str:
    """Mismo orden de resolución que el SDK oficial (auth.py)."""
    key = envfile.get("HF_KEY")
    if key:
        return key
    api_key, api_secret = envfile.get("HF_API_KEY"), envfile.get("HF_API_SECRET")
    if api_key and api_secret:
        return f"{api_key}:{api_secret}"
    raise SystemExit(
        "\n[FALTA CONFIGURACIÓN] Higgsfield necesita HF_API_KEY y HF_API_SECRET.\n"
        f"  Consíguelas en: {CREDENTIALS_URL}\n"
        "  Después ejecuta:  python3 scripts/setup.py\n"
    )


def _request(method: str, url: str, *, payload: Any = None,
             headers: dict[str, str] | None = None, raw: bytes | None = None,
             timeout: float = 120.0, authenticate: bool = True) -> Any:
    body = raw if raw is not None else (
        json.dumps(payload).encode("utf-8") if payload is not None else None
    )
    final_headers = {"User-Agent": USER_AGENT}
    if authenticate:
        # La credencial viaja SOLO en esta cabecera y nunca se registra.
        final_headers["Authorization"] = f"Key {_credential()}"
    if raw is None and payload is not None:
        final_headers["Content-Type"] = "application/json"
    final_headers.update(headers or {})

    req = urllib.request.Request(url, data=body, method=method, headers=final_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        if exc.code in (401, 403):
            raise HiggsfieldError(
                f"Higgsfield rechazó las credenciales (HTTP {exc.code}). "
                f"Revísalas en {CREDENTIALS_URL} y vuelve a ejecutar "
                f"scripts/setup.py. Respuesta: {detail}"
            ) from exc
        if exc.code == 404:
            raise HiggsfieldError(
                f"Ruta no encontrada (HTTP 404): {urllib.parse.urlparse(url).path}\n"
                "  La 'application' configurada no existe. Copia la ruta exacta "
                "de la página del modelo en cloud.higgsfield.ai y ponla en\n"
                "  HIGGSFIELD_TEXT_TO_IMAGE_APP / HIGGSFIELD_IMAGE_EDIT_APP (.env)."
            ) from exc
        raise HiggsfieldError(f"HTTP {exc.code} en {method} {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise HiggsfieldError(f"No se pudo conectar con Higgsfield: {exc.reason}") from exc

    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return data


def upload_file(path: Path) -> str:
    """Sube una imagen y devuelve su URL pública (para usarla como referencia)."""
    path = Path(path)
    content_type = mime_for(path)
    slot = _request("POST", f"{BASE_URL}/files/generate-upload-url",
                    payload={"content_type": content_type})
    upload_url = slot.get("upload_url")
    public_url = slot.get("public_url")
    if not upload_url or not public_url:
        raise HiggsfieldError(f"Respuesta inesperada al pedir URL de subida: {slot}")
    _request("PUT", upload_url, raw=path.read_bytes(), authenticate=False,
             headers=slot.get("upload_headers") or {"Content-Type": content_type})
    return public_url


def submit(application: str, arguments: dict[str, Any],
           webhook_url: str | None = None) -> dict[str, Any]:
    url = f"{BASE_URL}/{application.strip('/')}"
    if webhook_url:
        url += "?" + urllib.parse.urlencode({"hf_webhook": webhook_url})
    data = _request("POST", url, payload=arguments)
    if "request_id" not in data:
        raise HiggsfieldError(f"Respuesta sin request_id: {data}")
    return data


def wait(status_url: str, *, poll: float = 3.0, timeout: float = 900.0,
         verbose: bool = True) -> dict[str, Any]:
    deadline = time.time() + timeout
    last = None
    while True:
        data = _request("GET", status_url)
        status = str(data.get("status", "")).lower()
        if verbose and status != last:
            print(f"  [higgsfield] {status or 'desconocido'}")
            last = status
        if status in DONE:
            if status != "completed":
                raise HiggsfieldError(
                    f"El trabajo terminó con estado '{status}'. "
                    f"Detalle: {json.dumps(data)[:300]}"
                )
            return data
        if time.time() > deadline:
            raise HiggsfieldError(f"Tiempo de espera agotado ({timeout:.0f}s).")
        time.sleep(poll)


def image_urls(result: dict[str, Any]) -> list[str]:
    """Extrae URLs de imagen del resultado sin asumir una única forma."""
    urls: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "url" and isinstance(value, str) and value.startswith("http"):
                    urls.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(result)
    seen, unique = set(), []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def download(url: str, destination: Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=180) as response:
        destination.write_bytes(response.read())
    return destination


def generate_image(prompt: str, *, aspect_ratio: str = "16:9",
                   reference: Path | None = None,
                   application: str | None = None,
                   extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Lanza una generación de imagen y espera el resultado."""
    if reference:
        application = application or envfile.get("HIGGSFIELD_IMAGE_EDIT_APP")
        if not application:
            raise SystemExit(
                "\n[CONFIGURACIÓN INCOMPLETA] Para usar tu foto como referencia en\n"
                "Higgsfield hace falta la ruta de un modelo que acepte imagen de\n"
                "entrada (image-to-image / edit).\n"
                f"  1. Entra en {CREDENTIALS_URL} y abre el modelo que quieras usar.\n"
                "  2. Copia su ruta de 'application' exacta.\n"
                "  3. Ponla en .env como HIGGSFIELD_IMAGE_EDIT_APP\n"
                "  Alternativa inmediata: usa Gemini, que sí admite foto de\n"
                "  referencia de serie:  python3 scripts/thumbnail.py --provider gemini ...\n"
            )
    else:
        application = application or envfile.get(
            "HIGGSFIELD_TEXT_TO_IMAGE_APP", "bytedance/seedream/v4/text-to-image"
        )

    arguments: dict[str, Any] = {"prompt": prompt, "aspect_ratio": aspect_ratio}
    if reference:
        public_url = upload_file(Path(reference))
        # El nombre del parámetro de imagen de entrada depende del modelo.
        # No lo adivinamos: se lee de .env y por defecto usamos "image_url".
        # Si el modelo devuelve error de validación, cópialo de su página.
        param = envfile.get("HIGGSFIELD_IMAGE_PARAM", "image_url")
        arguments[param] = public_url
    if extra:
        arguments.update(extra)

    job = submit(application, arguments)
    status_url = job.get("status_url") or f"{BASE_URL}/requests/{job['request_id']}/status"
    return wait(status_url)
