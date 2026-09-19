# Qué se puede hacer y qué no

Documento honesto de capacidades reales, con la fuente de cada afirmación.
Última verificación: **septiembre de 2026**.

---

## Resumen: quién hace qué

| Tarea | Proveedor | Estado |
|---|---|---|
| Analizar URL de YouTube sin descargarla | Gemini | **funciona** |
| Analizar vídeo local | Gemini (Files API) | **funciona** |
| Analizar PDFs, imágenes, notas | Gemini | **funciona** |
| Verificar datos con búsqueda web | Gemini (grounding) | **funciona** |
| Generar miniatura 16:9 | Gemini (modelo de imagen) | **funciona** |
| Miniatura usando tu foto como referencia | Gemini | **funciona** |
| Generar imágenes | Higgsfield | **funciona** (opcional) |
| Texto alternativo (ángulos, títulos, SEO) | OpenRouter | funciona (opcional) |
| Analizar vídeo con OpenRouter | — | **no se puede** |

---

## Gemini / Google AI

### Lo que se ha verificado

Comprobado directamente sobre el SDK oficial `google-genai` (v2.24.0):

- `types.FileData(file_uri=...)` acepta **URLs de YouTube**, así que no hay
  que descargar el vídeo.
- `types.VideoMetadata(fps, start_offset, end_offset)` permite muestrear
  fotogramas y **recortar tramos** del vídeo.
- `types.ImageConfig(aspect_ratio=...)` admite **`"16:9"`**, que es
  exactamente el formato de miniatura de YouTube.
- `response_modalities=["IMAGE"]` devuelve la imagen generada.
- `client.models.list()` permite **descubrir los modelos** de tu cuenta.
- `types.Tool(google_search=...)` da búsqueda web con fuentes citadas.

### Límites

| Límite | Valor | Consecuencia |
|---|---|---|
| Vídeos de YouTube | solo **públicos** | privados o no listados: descargar a `input/videos/` |
| Vídeos por petición | **10** (modelos 2.5+) | más de 10 referencias: analizar en tandas |
| Nivel gratuito | **8 h de vídeo de YouTube al día** | vídeos muy largos agotan la cuota rápido |
| Duración por vídeo | ~1 h a resolución normal, ~3 h en baja | usar `--media-resolution low` o recortar |
| Vídeos locales | se suben a la Files API | Google los borra a las pocas horas |

### Decisión de diseño: los modelos no están escritos a fuego

Los IDs de modelo de Gemini cambian cada pocos meses. Si el kit llevara
`gemini-X.Y-pro` escrito en el código, se rompería solo con el tiempo.

En su lugar, `scripts/models.py` consulta qué modelos tiene tu cuenta,
elige el mejor para cada tarea (texto, vídeo, imagen) y lo guarda en
`config/models.json`. Para forzar uno concreto:

```bash
# en .env — por ejemplo, un 'flash' para gastar menos en vídeo
GEMINI_VIDEO_MODEL=gemini-3.8-flash
```

### Miniaturas: expectativa realista

Sale en 16:9 y lista para subir, pero:

- **el parecido facial no es exacto**. Para la miniatura definitiva, lo
  habitual es usar la imagen generada como fondo y componer encima tu foto
  real en cualquier editor;
- **el texto dentro de la imagen sale con faltas a menudo**. Si el texto es
  importante, genera sin texto y añádelo tú;
- si tu cuenta no tiene modelo de imagen, el kit lo dice y entrega solo los
  conceptos. **No finge haber generado una imagen.**

---

## OpenRouter

**Qué sí**: texto, imágenes de entrada y PDFs a través de
`/api/v1/chat/completions`. Sirve como alternativa para ángulos, ganchos,
títulos y SEO si prefieres otro modelo.

**Qué no**: **no acepta URLs de YouTube ni análisis de vídeo largo**. Su
API es compatible con el formato de chat, que no tiene una forma de pasar
una referencia de vídeo de YouTube como sí la tiene la API de Gemini.

Por eso el kit **no** ofrece OpenRouter como motor de investigación de
vídeo: sería prometer algo que no puede cumplir. Es un proveedor de texto
opcional, y así está documentado.

---

## Higgsfield

**Sí tiene API oficial.** El kit la integra de verdad, no como maqueta.

El contrato está extraído del **código fuente del SDK oficial**
(`higgsfield-client` 0.2.0, PyPI / github.com/higgsfield-ai), no inventado:

| Elemento | Valor |
|---|---|
| Base | `https://api.higgsfield.ai` |
| Autenticación | cabecera `Authorization: Key <API_KEY>:<API_SECRET>` |
| Enviar trabajo | `POST /{application}` con los argumentos en JSON |
| Consultar estado | `GET /requests/{id}/status` |
| Cancelar | `POST /requests/{id}/cancel` |
| Subir archivo | `POST /files/generate-upload-url` y luego `PUT` |
| Estados | `queued`, `in_progress`, `completed`, `failed`, `nsfw`, `canceled` |
| Webhook | parámetro `?hf_webhook=<url>` (opcional) |
| Credenciales | [cloud.higgsfield.ai](https://cloud.higgsfield.ai/) |

### Lo que el kit NO adivina

La **ruta de la "application"** (por ejemplo
`bytedance/seedream/v4/text-to-image`) identifica el modelo concreto, y ese
catálogo cambia. El kit trae como valor por defecto la única ruta
documentada oficialmente en el SDK, y el resto se configura en `.env`:

```bash
HIGGSFIELD_TEXT_TO_IMAGE_APP=bytedance/seedream/v4/text-to-image
HIGGSFIELD_IMAGE_EDIT_APP=        # cópiala de la página del modelo
HIGGSFIELD_IMAGE_PARAM=image_url  # nombre del parámetro de imagen de entrada
```

**Por qué no está rellenado**: inventar rutas de endpoint daría errores 404
confusos y haría creer que la integración está rota. Es mejor que el usuario
copie la ruta exacta de la página de su modelo. Si la ruta es incorrecta,
el kit lo dice con ese mensaje concreto y te indica dónde encontrar la buena.

**Si no configuras Higgsfield no pierdes nada**: Gemini genera miniaturas
16:9 con tu foto de referencia de serie.

---

## Claude Code

Verificado en la documentación oficial (`code.claude.com/docs`):

- Las skills de proyecto viven en **`.claude/skills/<nombre>/SKILL.md`**.
  Por eso están ahí y no en una carpeta `skills/` en la raíz: en la raíz no
  se descubrirían. (`skills/README.md` es solo un índice.)
- La misma skill funciona como **comando** (`/nuevo-video`) y como skill de
  invocación automática, según el `description` del frontmatter.
- Los subagentes de proyecto viven en **`.claude/agents/*.md`**.
- Los permisos y bloqueos van en **`.claude/settings.json`**.

---

## Lo que este kit no hace a propósito

| No hace | Por qué |
|---|---|
| Escribir el guion palabra por palabra | el vídeo tiene que sonar a ti, no a una IA |
| Copiar la estructura del vídeo de referencia | el objetivo es diferenciarte, no clonar |
| Publicar en YouTube | requiere OAuth y permisos de escritura sobre tu canal: demasiado riesgo para lo que aporta |
| Descargar vídeos de YouTube | innecesario (Gemini lee la URL) y problemático con los términos de servicio |
| Interfaz web o gráfica | el producto son carpetas y archivos que puedes versionar, editar y mover |
| Inventar datos para rellenar huecos | lo que no está verificado se marca `[NO VERIFICADO]` |

---

## Integraciones pendientes / opcionales

- **Publicación automática en YouTube**: técnicamente posible con la
  YouTube Data API, pero exige OAuth y permisos de escritura en el canal.
  No implementado por decisión de seguridad.
- **Métricas reales del canal** (CTR, retención): requieren YouTube
  Analytics API con OAuth. No implementado.
- **Transcripción con marcas de tiempo palabra por palabra**: Gemini ya da
  timestamps a nivel de momento, suficiente para preparar un vídeo. Para
  precisión de subtítulos haría falta una herramienta específica.
