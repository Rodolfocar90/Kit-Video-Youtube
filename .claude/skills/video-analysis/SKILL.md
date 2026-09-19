---
name: video-analysis
description: Detalles técnicos para analizar vídeo con Gemini (URLs de YouTube, vídeos locales, recortes, fps, control de coste y errores frecuentes). Úsalo cuando falle un análisis de vídeo, cuando el vídeo sea muy largo o cuando haya que decidir cómo procesar material audiovisual.
allowed-tools: Bash(python3 scripts/*), Read, Glob
---

# Análisis de vídeo con Gemini

## Qué se puede y qué no (verificado)

| Puedo | Cómo |
|---|---|
| Analizar una URL de YouTube sin descargarla | `--youtube URL` |
| Analizar hasta 10 vídeos en una petición | varios `--youtube` |
| Analizar vídeo local (mp4, mov, mkv, webm…) | `--file ruta` |
| Recortar un tramo | `--start 120s --end 600s` |
| Muestrear más o menos fotogramas | `--fps 0.5` (menos) / `--fps 2` (más) |
| Abaratar un vídeo largo | `--media-resolution low` |
| PDFs, imágenes y notas | `--file ruta` |

| No puedo | Motivo |
|---|---|
| Vídeos de YouTube privados o no listados | la API solo acepta públicos |
| Analizar vídeo con OpenRouter | su API no admite URL de YouTube ni vídeo largo |
| Saltarme el límite diario del nivel gratuito | 8 h de vídeo de YouTube al día |

## Uso normal

```bash
python3 scripts/analyze.py \
  --youtube "https://www.youtube.com/watch?v=XXXX" \
  --prompt-file .claude/skills/research/prompt-video.md \
  --out output/NOMBRE/fuentes/video-01.md --yes
```

## Decisiones según duración

| Duración | Qué hacer |
|---|---|
| < 20 min | por defecto, sin más opciones |
| 20–60 min | `--media-resolution low`; avisa de que tardará varios minutos |
| > 60 min | trocea con `--start/--end` en tramos de ~30 min y analiza por partes |
| Solo interesa un tramo | `--start/--end` desde el principio: más barato y más preciso |

## Coste

El vídeo es lo más caro del kit: los tokens de entrada crecen con la
duración. Antes de lanzar más de 2 vídeos largos, dile al usuario cuántos
vas a analizar y con qué resolución, y espera su confirmación.
El script ya pide confirmación; `--yes` solo cuando el usuario ya ha dicho sí.

## Errores frecuentes y qué significan

| Mensaje | Causa real | Solución |
|---|---|---|
| `No parece una URL de YouTube válida` | otra plataforma | descárgalo a `input/videos/` y usa `--file` |
| `403` / `no accesible` | vídeo privado, no listado o con restricción | pide el archivo local |
| `RESOURCE_EXHAUSTED` / `429` | cuota agotada | espera, o usa un modelo `flash` con `GEMINI_VIDEO_MODEL` |
| `TIMEOUT ... procesando` | vídeo local muy grande | recorta con `--start/--end` o reduce resolución |
| respuesta vacía | el modelo elegido no admite vídeo | `python3 scripts/models.py --refresh` |
| `SIN MODELO` | la cuenta no expone modelos de ese tipo | `python3 scripts/models.py --all` y fija uno en `.env` |

## Si un análisis sale pobre

1. ¿Usaste el prompt largo (`prompt-video.md`) o uno improvisado?
2. ¿El modelo es `pro`? Comprueba con `python3 scripts/models.py`.
3. ¿Bajaste la resolución? Recupérala para los tramos clave.
4. Analiza por bloques con `--start/--end`: más señal, menos ruido.
