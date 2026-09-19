---
name: research
description: Investiga a fondo uno o varios materiales de referencia (vídeos de YouTube, vídeos locales, PDFs, imágenes, notas) y produce 01-RESEARCH.md y 08-SOURCES.md. Úsalo cuando haya que analizar, comparar o extraer información de material de referencia.
allowed-tools: Bash(python3 scripts/*), Read, Write, Edit, Glob, WebSearch, WebFetch, Task
---

# Investigación del material

Objetivo: entender el tema **mejor que las referencias**, no resumirlas.

## 1. Inventario del material

```bash
ls -la input/videos input/images input/documents input/channel-context
cat input/REFERENCIAS.md 2>/dev/null
```

Clasifica lo que tienes:

| Tipo | Cómo se procesa |
|---|---|
| URL de YouTube (pública) | `scripts/analyze.py --youtube URL` — **no se descarga** |
| Vídeo local | `scripts/analyze.py --file ruta` (se sube a la Files API) |
| PDF / imagen / notas | `scripts/analyze.py --file ruta` |
| Notas del usuario | también `--file`, o pégalas como contexto |

Vídeo de YouTube privado o no listado: la API lo rechaza. Dilo y pide que
lo descargue a `input/videos/`.

## 2. Análisis vídeo por vídeo

Un comando por vídeo, para que cada análisis sea profundo:

```bash
python3 scripts/analyze.py \
  --youtube "URL" \
  --prompt-file .claude/skills/research/prompt-video.md \
  --out output/NOMBRE/fuentes/video-01.md --yes
```

Si hay **3 o más vídeos**, lánzalos en paralelo con el subagente
`analista-video` (uno por vídeo, contexto aislado). Con 1 o 2, hazlo directo.

Para vídeos de más de ~40 minutos, añade `--media-resolution low` y dilo:
baja el coste a cambio de menos detalle visual.

## 3. Comparativa (solo si hay 2+ fuentes)

```bash
python3 scripts/analyze.py \
  --file output/NOMBRE/fuentes/video-01.md \
  --file output/NOMBRE/fuentes/video-02.md \
  --prompt-file .claude/skills/research/prompt-comparativa.md \
  --out output/NOMBRE/fuentes/comparativa.md --yes
```

## 4. Verificación de datos

Toda cifra, fecha, nombre propio o afirmación fuerte que vayas a poner en
el pack necesita comprobación:

- Si tienes **WebSearch**, úsala directamente y cita la URL.
- Si no, usa el script (deja además rastro documental):

```bash
python3 scripts/web_research.py "dato concreto a verificar" \
  --context-file output/NOMBRE/fuentes/video-01.md \
  --out output/NOMBRE/fuentes/verificacion.md --yes
```

Lo que no puedas verificar se queda marcado `[NO VERIFICADO]`. No se
elimina: el creador tiene que saber qué es terreno firme y qué no.

## 5. Escribir `01-RESEARCH.md`

Estructura obligatoria:

```markdown
# Investigación — <TEMA>

## Resumen ejecutivo
5 puntos. Lo que de verdad importa del tema.

## Ideas principales
Por cada idea: qué es, por qué importa, de dónde sale (etiqueta + timestamp).

## Datos y cifras
| Dato | Valor | Origen | Verificado |
|---|---|---|---|

## Ejemplos, casos e historias
Los que funcionan en cámara. Con timestamp de la referencia.

## Argumentos y contraargumentos
Incluye las objeciones que hará la audiencia.

## Momentos destacados de las referencias
| Fuente | Timestamp | Qué pasa | Por qué es útil |
|---|---|---|---|

## Elementos visuales aprovechables
Gráficos, demos, pantallas, comparativas vistas en el material.

## Qué falta verificar
Lista explícita de `[NO VERIFICADO]`.

## Si hay varias fuentes
### Coincidencias  ### Exclusivo de cada fuente
### Contradicciones  ### Huecos de información
### Oportunidades para un vídeo distinto
```

## 6. Escribir `08-SOURCES.md`

- Cada referencia: título, autor/canal, URL o ruta, fecha, qué aporta.
- Fuentes externas usadas para verificar, con URL.
- **Enlaces que el creador debería citar en la descripción.**
- Qué NO se ha podido verificar.

## Errores que arruinan esta fase

- Resumir el vídeo ajeno en vez de investigar el tema.
- Dar por buena una cifra porque la dice el vídeo de referencia.
- Poner timestamps aproximados o inventados.
- Omitir las contradicciones entre fuentes: ahí está el ángulo bueno.
