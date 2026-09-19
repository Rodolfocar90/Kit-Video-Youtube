# Kit de Vídeo para YouTube

Convierte vídeos y material de referencia en un **pack completo para
preparar tu próximo vídeo**: investigación, ángulo, ganchos, estructura,
títulos, miniaturas y SEO.

No es una app. No hay que instalar nada raro ni abrir un navegador.
Es una carpeta que abres en VS Code y usas con Claude Code.

---

## Empezar en 4 pasos

```bash
# 1. Instala la dependencia (solo la primera vez)
pip3 install -r requirements.txt

# 2. Configura tu clave de Gemini (se oculta al teclearla)
python3 scripts/setup.py

# 3. Comprueba que todo funciona
python3 scripts/doctor.py
```

**4.** Abre la carpeta en VS Code, lanza `claude` y escribe:

```
/nuevo-video
```

El sistema te pregunta qué referencias quieres usar, investiga, y te
entrega el pack en `output/`.

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

### 1. Pon tu material

| Qué tienes | Dónde va |
|---|---|
| URL de un vídeo público de YouTube | apúntala en `input/REFERENCIAS.md` |
| Vídeo tuyo o privado | `input/videos/` |
| Tu foto para la miniatura | `input/images/` |
| PDFs, informes, notas | `input/documents/` |
| Datos de tu canal | copia `input/channel-context/canal.example.md` a `canal.md` |

Los vídeos públicos de YouTube **no se descargan**: se analizan
directamente desde la URL. Es más rápido, más barato y más limpio.

### 2. Pide el vídeo

```
/nuevo-video cómo automatizar la atención al cliente con IA
```

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
| `/configurar` | cambiar o añadir claves de API |
| `python3 scripts/doctor.py` | diagnóstico (nunca muestra tus claves) |
| `python3 scripts/models.py` | ver qué modelos de Gemini tienes |

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

```bash
python3 scripts/doctor.py
```

Dice exactamente qué falta y cómo arreglarlo. Los problemas típicos y sus
soluciones están en [LIMITACIONES.md](LIMITACIONES.md).
