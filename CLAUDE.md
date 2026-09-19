# Kit de Vídeo para YouTube — instrucciones para el agente

## Qué es este proyecto

Un kit para **preparar vídeos de YouTube**. Convierte material de referencia
(vídeos de YouTube, vídeos locales, PDFs, imágenes, notas) en un pack de
preparación completo: investigación, ángulo, ganchos, estructura, títulos,
miniaturas y SEO.

No es una aplicación web. No tiene interfaz. Son carpetas, Markdown, skills
y scripts de Python que tú ejecutas.

## Las tres reglas que definen el producto

1. **No escribes el guion.** Nunca redactes el vídeo palabra por palabra.
   Entregas puntos a contar, datos, estructura y decisiones. El creador
   pone sus palabras.
2. **No copias la referencia.** El material se analiza para **investigar**
   un tema y hacer algo **original y mejor**. Si tu resultado se parece al
   vídeo de referencia, has fallado.
3. **Etiquetas el origen de todo.** Sin excepciones:

   | Etiqueta | Significado | Obligatorio |
   |---|---|---|
   | `[FUENTE DEL VÍDEO]` | lo dice el material analizado | timestamp mm:ss |
   | `[FUENTE EXTERNA]` | verificado fuera del material | URL |
   | `[INFERENCIA]` | tu deducción | nada, pero dilo claro |
   | `[NO VERIFICADO]` | no se ha podido comprobar | mantenerlo visible |

   **No inventes fuentes, cifras, estudios, URLs ni timestamps.** Si no lo
   tienes, escribe "No verificado en el material". Esto no es negociable:
   el creador va a decir esto en cámara delante de su audiencia.

## Flujo de ejecución

El usuario escribe `/nuevo-video` y tú sigues la skill `nuevo-video`.
Orden estricto (cada paso necesita el anterior):

```
0. doctor.py --offline      ->  ¿hay clave de Gemini?
1. preguntar material       ->  UNA sola ronda de preguntas
2. new_project.py "tema"    ->  crea output/NOMBRE-DEL-VIDEO/
3. skill research           ->  01-RESEARCH.md + 08-SOURCES.md
4. skill youtube-structure  ->  02-ANGLE.md, 03-HOOKS.md, 04-STRUCTURE.md
5. skill packaging          ->  05-TITLES.md
6. skill thumbnail          ->  06-THUMBNAILS.md  (conceptos)
7. skill seo                ->  07-SEO.md
8. [opcional, con coste]    ->  thumbnails/*.png
9. build_pack.py            ->  PACK-YOUTUBE.html
```

Si el usuario pide solo una parte ("más títulos", "otra miniatura",
"rehaz el SEO"), invoca únicamente esa skill sobre el proyecto existente.
**No repitas la investigación si `01-RESEARCH.md` ya está relleno**: es la
parte más lenta y más cara del flujo.

## Skills disponibles

`.claude/skills/<nombre>/SKILL.md`

| Skill | Cuándo |
|---|---|
| `nuevo-video` | vídeo nuevo de cero (`/nuevo-video`) |
| `research` | analizar y comparar material de referencia |
| `video-analysis` | dudas técnicas o fallos al analizar vídeo |
| `youtube-structure` | ángulo, ganchos, estructura |
| `packaging` | títulos |
| `thumbnail` | conceptos de miniatura y generación de imágenes |
| `seo` | descripción, keywords, tags, capítulos |
| `pack` | montar el HTML (`/pack`) |
| `configurar` | claves de API y diagnóstico (`/configurar`) |

## Subagentes

`.claude/agents/`

- **`analista-video`** — un vídeo por agente, contexto aislado. Úsalo en
  paralelo cuando haya **3 o más vídeos** de referencia. Con 1 o 2, hazlo
  directamente: lanzar subagentes cuesta más de lo que ahorra.
- **`verificador`** — comprueba cifras y afirmaciones contra fuentes
  externas. Úsalo antes de cerrar un pack con muchos datos.

## Dónde leer las entradas

| Ruta | Qué hay | Lee siempre |
|---|---|---|
| `input/REFERENCIAS.md` | URLs de YouTube y notas del usuario | **sí, primero** |
| `input/channel-context/*.md` | canal, audiencia, estilo, posición | **sí** |
| `input/videos/` | vídeos locales | listar |
| `input/images/` | foto del creador y material visual | listar |
| `input/documents/` | PDFs, notas, datos | listar |

Mira estas rutas **antes** de preguntar nada. Si el usuario ya apuntó las
URLs en `REFERENCIAS.md`, no le hagas repetirlas.

## Dónde guardar las salidas

Todo en `output/NOMBRE-DEL-VIDEO/`, creado por `scripts/new_project.py`.
Nunca escribas resultados en la raíz del proyecto ni en `input/`.

```
output/NOMBRE-DEL-VIDEO/
├── 01-RESEARCH.md      05-TITLES.md
├── 02-ANGLE.md         06-THUMBNAILS.md
├── 03-HOOKS.md         07-SEO.md
├── 04-STRUCTURE.md     08-SOURCES.md
├── PACK-YOUTUBE.html   (lo genera build_pack.py)
├── proyecto.json       (metadatos del proyecto)
├── fuentes/            (análisis crudo de cada referencia)
└── thumbnails/         (prompts e imágenes generadas)
```

## Scripts

Todos se ejecutan con `python3 scripts/<nombre>.py`. Llevan `--help`.

| Script | Para qué |
|---|---|
| `setup.py` | asistente de claves (**interactivo: lo ejecuta el usuario**) |
| `doctor.py` | diagnóstico completo; `--offline` sin red |
| `models.py` | qué modelos de Gemini hay disponibles |
| `new_project.py` | crea la carpeta del proyecto |
| `analyze.py` | analiza vídeos/documentos con Gemini |
| `web_research.py` | verificación con búsqueda web |
| `thumbnail.py` | genera imágenes (**con coste**) |
| `build_pack.py` | monta el `PACK-YOUTUBE.html` |

## Seguridad — obligatorio

- **Nunca pidas una clave de API por el chat.** El usuario la introduce en
  su terminal con `python3 scripts/setup.py`, que la oculta al teclearla.
  Si el usuario pega una clave en la conversación, dile que la revoque y
  genere otra: ya ha quedado en el historial.
- **Nunca leas ni imprimas `.env`.** Ni con `cat`, ni con `Read`, ni con
  `env`, ni con `printenv`. Está bloqueado en `.claude/settings.json`.
  Para saber qué hay configurado: `python3 scripts/doctor.py` (enmascara).
- **Nunca escribas una clave** en Markdown, HTML, logs, commits ni en este
  archivo. Los scripts ya leen los secretos por variable de entorno.
- **Las claves solo van en `.env`** (permisos 600, ignorado por Git).
  `.env.example` nunca lleva valores reales.
- **Mínimo privilegio**: pasa a cada proveedor solo lo que necesita. No
  mandes la clave de un proveedor a otro ni metas secretos en un prompt.
- **Antes de cualquier operación con coste alto** (generar imágenes,
  analizar varios vídeos largos) di qué vas a hacer, cuántas unidades y
  espera confirmación. `scripts/thumbnail.py` está deliberadamente fuera
  de la lista de permisos automáticos: debe aprobarse cada vez.
- **Dependencias**: solo `google-genai` (SDK oficial de Google). No
  instales paquetes nuevos sin explicar para qué y pedir permiso.

## Límites reales del sistema

Está todo detallado en `LIMITACIONES.md`. Lo esencial:

- Las URLs de YouTube deben ser de vídeos **públicos**. Privados o no
  listados: hay que descargarlos a `input/videos/`.
- Máximo **10 vídeos por petición**; nivel gratuito, **8 h de YouTube/día**.
- **OpenRouter no analiza vídeo** ni URLs de YouTube. Solo texto.
- Las miniaturas salen 16:9 desde la API, pero el parecido facial no es
  perfecto: para la versión definitiva suele hacer falta un editor.
- Si la cuenta no tiene modelo de imagen en Gemini y no hay Higgsfield,
  entrega los conceptos de miniatura y dilo. **No finjas una imagen.**

## Cómo hablar al usuario

Es el creador del canal, no un programador. Directo y sin rodeos:

- Comandos completos, listos para copiar y pegar.
- Rutas exactas de los archivos generados.
- Cuando algo falla: qué ha fallado, por qué y el comando que lo arregla.
- Al entregar el pack: ángulo recomendado, título + miniatura recomendados
  y **qué queda sin verificar antes de grabar**. Esas tres cosas siempre.
- No adornes los resultados. Si la investigación ha salido pobre, dilo.
