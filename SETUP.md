# Instalación paso a paso

Pensado para que funcione aunque no hayas programado nunca.
Tiempo total: unos 10 minutos, y solo se hace una vez.

---

## 1. Lo que necesitas antes de empezar

### Python 3.9 o superior

Abre una terminal y escribe:

```bash
python3 --version
```

- **Sale un número 3.9 o mayor** → listo.
- **Mac**: ya viene instalado.
- **Windows**: descárgalo de [python.org](https://www.python.org/downloads/)
  y marca la casilla **"Add Python to PATH"** durante la instalación.
  Después usa `python` en lugar de `python3`.
- **Linux**: `sudo apt install python3 python3-pip`

### Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Si no tienes `npm`, instala [Node.js](https://nodejs.org/) primero.

### VS Code

Descárgalo de [code.visualstudio.com](https://code.visualstudio.com/).
No es obligatorio, pero es la forma más cómoda de trabajar.

---

## 2. Instalar el kit

Abre la carpeta del kit en la terminal y ejecuta:

```bash
pip3 install -r requirements.txt
```

Instala una sola cosa: `google-genai`, el SDK oficial de Google. Es la
única dependencia obligatoria.

---

## 3. Conseguir tu clave de Gemini (obligatoria)

Es la única clave imprescindible: es lo que permite analizar vídeos.

1. Entra en **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
2. Inicia sesión con tu cuenta de Google.
3. Pulsa **"Create API key"**.
4. Cópiala. Empieza por `AIza...`

Tiene **nivel gratuito** con límites generosos (hasta 8 horas de vídeo de
YouTube al día). Para uso normal de un canal, sobra.

---

## 4. Configurar el kit

```bash
python3 scripts/setup.py
```

El asistente:

1. Comprueba las dependencias.
2. Te pide **solo** las claves que hagan falta.
3. **No muestra lo que escribes** (como cuando pones una contraseña).
4. Lo guarda en `.env` con permisos `600`: solo tu usuario puede leerlo.
5. Después nunca vuelve a mostrar la clave completa.

Si dejas una clave vacía, te dice exactamente dónde conseguirla.

### Opcionales

Te preguntará por dos proveedores más. Puedes decir **no** a ambos:

| Proveedor | Para qué sirve | ¿Hace falta? |
|---|---|---|
| **OpenRouter** | usar otros modelos para el texto | no. Y **no puede analizar vídeo** |
| **Higgsfield** | segundo generador de imágenes | no. Gemini ya hace miniaturas 16:9 con tu foto |

Puedes añadirlos más adelante:

```bash
python3 scripts/setup.py --provider higgsfield
```

> **Higgsfield**: su clave se muestra **una sola vez**, al crearla en
> [cloud.higgsfield.ai](https://cloud.higgsfield.ai/). Cópiala en ese momento.
> Necesita dos valores: `HF_API_KEY` y `HF_API_SECRET`.

---

## 5. Comprobar que todo está bien

```bash
python3 scripts/doctor.py
```

Verás algo así:

```
[OK]   .env existe
[OK]   permisos 0o600 (solo tu usuario puede leerlo)
[OK]   .env está en .gitignore (tus claves no se subirán)
[OK]   GEMINI_API_KEY       AIza******a3 (39 car.)
[OK]   autenticación correcta — 47 modelos disponibles
[OK]   modelo de vídeo  : gemini-3.1-pro
```

Fíjate en que la clave aparece **enmascarada**. Nunca se muestra completa,
tampoco en los mensajes de error.

Si algo falla, el propio diagnóstico te dice el comando que lo arregla.

---

## 6. Prepara tu material

### Datos de tu canal (recomendado, una sola vez)

```bash
cp input/channel-context/canal.example.md input/channel-context/canal.md
```

Rellena ese archivo. Mejora mucho los ángulos, los títulos y el SEO,
porque el sistema sabe a quién le hablas y cómo hablas.

### Tus referencias

Abre `input/REFERENCIAS.md` y apunta:

- el tema del vídeo;
- las URLs de YouTube que quieras usar como referencia (**públicas**);
- tus notas, tu opinión, lo que quieras incluir sí o sí.

### Archivos

| Qué | Dónde |
|---|---|
| Tu foto para la miniatura | `input/images/` |
| Vídeos locales o privados | `input/videos/` |
| PDFs, informes, notas | `input/documents/` |

---

## 7. Crear tu primer vídeo

Abre la carpeta en VS Code, abre una terminal integrada y lanza:

```bash
claude
```

Y escribe:

```
/nuevo-video
```

A partir de ahí el sistema te guía: te pregunta por el material, investiga
y te avisa antes de cualquier operación que cueste dinero.

Al terminar tendrás una carpeta en `output/` y un `PACK-YOUTUBE.html` que
puedes abrir con doble clic.

---

## Cambiar de configuración más adelante

```bash
python3 scripts/setup.py                     # completa lo que falte
python3 scripts/setup.py --reconfigure       # vuelve a preguntar todo
python3 scripts/setup.py --provider gemini   # solo un proveedor
python3 scripts/models.py --refresh          # redetectar modelos
```

También desde Claude Code: `/configurar`

---

## Problemas frecuentes

| Mensaje | Qué pasa | Solución |
|---|---|---|
| `command not found: python3` | Python no instalado o fuera del PATH | reinstala marcando "Add to PATH"; en Windows prueba `python` |
| `FALTA DEPENDENCIA ... google-genai` | falta el SDK | `pip3 install -r requirements.txt` |
| `FALTA CONFIGURACIÓN GEMINI_API_KEY` | sin clave | `python3 scripts/setup.py` |
| `API_KEY_INVALID` | clave mal copiada o revocada | crea otra en aistudio.google.com/apikey |
| `RESOURCE_EXHAUSTED` / `429` | cuota diaria agotada | espera, o pon un modelo `flash` en `.env` |
| `No parece una URL de YouTube válida` | otra plataforma | descarga el vídeo a `input/videos/` |
| `403` al analizar un vídeo | privado o no listado | descárgalo a `input/videos/` |
| `SIN MODELO de imagen` | tu cuenta no tiene modelo de imagen | usa Higgsfield o quédate con los conceptos |

Para cualquier otra cosa: `python3 scripts/doctor.py`

---

## Seguridad: lo que hace el kit por ti

- Las claves se guardan **solo** en `.env`, con permisos `600`.
- `.env` está en `.gitignore`: **no se puede subir a GitHub por accidente**.
- `.env.example` no contiene ninguna clave real.
- Al teclear una clave no se ve en pantalla.
- Ningún script imprime una clave completa: siempre enmascarada.
- El agente tiene **prohibido leer `.env`** por configuración
  (`.claude/settings.json`).
- Nada se escribe en `CLAUDE.md`, en los logs, en el HTML ni en los
  archivos de salida.
- Las operaciones que cuestan dinero piden confirmación, y el número de
  imágenes por orden está limitado (`MAX_IMAGES_PER_RUN`).

**Si alguna vez pegas una clave en el chat**: revócala y crea otra.
Cualquier secreto que pase por una conversación se considera comprometido.
