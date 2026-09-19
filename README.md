# Kit de Vídeo para YouTube

Convierte vídeos y material de referencia en un **pack completo para
preparar tu próximo vídeo**: investigación, ángulo, ganchos, estructura,
títulos, miniaturas y SEO.

No es una app. No hay que instalar nada raro ni abrir un navegador.
Es una carpeta que abres en VS Code y usas con Claude Code.

---

## Empezar

**1.** Descarga esta carpeta y ábrela en VS Code.

**2.** Abre una terminal dentro de VS Code y lanza Claude Code:

```bash
claude
```

**3.** Escribe esto y pega tus URLs:

```
/nuevo-video cómo automatizar la atención al cliente con IA
https://youtu.be/AAAAAAA  https://youtu.be/BBBBBBB
```

Ya está. **A partir de aquí no escribes comandos**: Claude instala lo que
falte, analiza los vídeos y te deja el pack en `output/`.

### Lo único que harás tú: la clave de Gemini

La primera vez Claude te la pedirá. Es gratis y se tarda un minuto:

1. Entra en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   y pulsa **"Create API key"**.
2. Abre el archivo **`.env`** de esta carpeta en VS Code.
3. Pega la clave después de `GEMINI_API_KEY=` y guarda.

**No la pegues en el chat.** Ahí quedaría guardada en el historial de la
conversación. Por eso, y solo por eso, esa parte la haces tú.

Guía detallada: **[SETUP.md](SETUP.md)**

---

## Qué necesitas

| | |
|---|---|
| **Python 3.9 o superior** | ya lo tienes en Mac y Linux; en Windows, desde python.org |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Una clave de Gemini** | gratis en [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

Y nada más. OpenRouter y Higgsfield son opcionales.

---

## Cómo se usa

### 1. Dile qué quieres, por el chat

```
/nuevo-video
```

Claude te hace **una sola ronda de preguntas** y tú contestas por el chat:

| Te pregunta | Tú le dices |
|---|---|
| El tema | «agentes de IA en atención al cliente» |
| Las referencias | pegas las URLs de YouTube, una detrás de otra |
| Si tienes foto para la miniatura | «está en mi Escritorio, se llama foto.jpg» |
| Si hay algo que quieras contar sí o sí | lo que sea |

Los archivos los copia él a `input/` por ti. Tú no mueves nada.

### 2. Si prefieres dejarlo preparado antes (opcional)

| Qué tienes | Dónde puedes dejarlo |
|---|---|
| URLs de YouTube y tus notas | `input/REFERENCIAS.md` |
| Vídeo tuyo o privado | `input/videos/` |
| Tu foto para la miniatura | `input/images/` |
| PDFs, informes, notas | `input/documents/` |
| Datos de tu canal (una vez) | copia `input/channel-context/canal.example.md` a `canal.md` |

Si ya lo has dejado ahí, Claude lo encuentra solo y **no te lo vuelve a
preguntar**.

Los vídeos públicos de YouTube **no se descargan**: se analizan
directamente desde la URL. Es más rápido, más barato y más limpio.

### 3. Recoge el pack

```
output/COMO-AUTOMATIZAR-LA-ATENCION-AL-CLIENTE-CON-IA/
├── 01-RESEARCH.md      investigación completa, con timestamps y fuentes
├── 02-ANGLE.md         3 ángulos posibles + el recomendado
├── 03-HOOKS.md         5 ganchos de máximo 20 segundos
├── 04-STRUCTURE.md     estructura bloque a bloque
├── 05-TITLES.md        10 títulos analizados + los 3 mejores
├── 06-THUMBNAILS.md    conceptos de miniatura
├── 07-SEO.md           descripción, keywords, tags, capítulos
├── 08-SOURCES.md       fuentes y enlaces a citar
├── PACK-YOUTUBE.html   ← todo junto, se abre con doble clic
└── thumbnails/         imágenes 16:9 generadas
```

**`PACK-YOUTUBE.html`** es el archivo que vas a usar de verdad: reúne todo
con un índice lateral, funciona sin internet y se imprime a PDF.

---

## Qué NO hace

- **No escribe el guion.** A propósito. Te da qué contar, no las palabras
  exactas: el vídeo tiene que sonar a ti.
- **No copia el vídeo de referencia.** Lo investiga para que hagas algo
  distinto y mejor.
- **No se inventa datos.** Todo lleva su origen etiquetado, y lo que no se
  ha podido verificar aparece marcado como tal.

---

## Comandos útiles

| Comando | Para qué |
|---|---|
| `/nuevo-video` | flujo completo |
| `/pack` | reconstruir el HTML tras editar algo |
| `/configurar` | claves de API y diagnóstico |

También puedes pedir partes sueltas en lenguaje normal: *"dame 10 títulos
más para este vídeo"*, *"genera otra miniatura del concepto 2"*,
*"verifica las cifras del research"*.

---

## Tus claves están a salvo

- Se guardan **solo** en `.env`, con permisos `600` y fuera de Git.
- Al teclearlas no se ven en pantalla, y después nunca se muestran
  completas (solo `AIza******a3`).
- El agente tiene **prohibido por configuración** leer `.env`.
- Las operaciones que cuestan dinero piden confirmación antes de ejecutarse.

Detalle completo en [SETUP.md](SETUP.md) y en la sección de seguridad de
[CLAUDE.md](CLAUDE.md).

---

## Estructura del proyecto

```
├── CLAUDE.md            instrucciones para el agente
├── SETUP.md             instalación paso a paso
├── LIMITACIONES.md      qué se puede y qué no, con las razones
├── .env.example          plantilla de configuración (sin claves)
├── .claude/
│   ├── skills/          las 9 skills del kit
│   ├── agents/          subagentes (analista-video, verificador)
│   └── settings.json    permisos: bloquea el acceso a .env
├── input/               tu material
├── output/              los packs generados
├── scripts/             el motor (Python)
└── config/              modelos detectados (sin secretos)
```

---

## Si algo falla

Escríbelo en el chat: *"algo va mal"*. Claude ejecuta el diagnóstico y te
dice qué falta y cómo arreglarlo.

Si quieres verlo tú:

```bash
python3 scripts/doctor.py
```

Nunca muestra tus claves. Los problemas típicos y sus soluciones están en
[LIMITACIONES.md](LIMITACIONES.md).
