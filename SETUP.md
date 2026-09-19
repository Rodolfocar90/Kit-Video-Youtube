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

**No tienes que hacer nada.** Abre la carpeta en VS Code, lanza `claude` y
escribe `/nuevo-video`: Claude detecta lo que falta y lo instala él.

Instala una sola cosa: `google-genai`, el SDK oficial de Google. Es la
única dependencia obligatoria.

Si lo prefieres a mano:

```bash
pip3 install -r requirements.txt
```

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

## 4. Poner la clave en el kit

Hay dos formas. **Las dos son seguras y las dos valen.** Elige la que te
resulte más cómoda.

### Opción A — sin terminal (la más sencilla)

Es lo que Claude te propondrá por defecto. Él crea el archivo, tú pegas la
clave en el editor:

1. Claude ejecuta `python3 scripts/setup.py --crear-env` y crea un archivo
   llamado **`.env`** en la carpeta del kit.
2. Abres `.env` en VS Code (aparece en el panel de la izquierda; si no lo
   ves, es que VS Code oculta los archivos que empiezan por punto: pulsa
   Ctrl+P / Cmd+P y escribe `.env`).
3. Buscas esta línea:

   ```
   GEMINI_API_KEY=
   ```

4. Pegas tu clave justo después del `=`, **sin espacios y sin comillas**:

   ```
   GEMINI_API_KEY=AIzaSy...tu_clave
   ```

5. Guardas con **Ctrl+S** (Cmd+S en Mac) y le dices a Claude «ya está».
   Él lo valida solo.

### Opción B — con terminal

El asistente interactivo. Te pide las claves y **no muestra lo que
escribes**, como cuando pones una contraseña:

```bash
python3 scripts/setup.py
```

1. Comprueba las dependencias.
2. Te pide **solo** las claves que hagan falta.
3. Las guarda en `.env` con permisos `600`: solo tu usuario puede leerlo.
4. Después nunca vuelve a mostrar la clave completa.

Si dejas una clave vacía, te dice exactamente dónde conseguirla.

### Lo que NO debes hacer

**No pegues la clave en el chat de Claude.** Si lo haces, queda guardada en
el historial de la conversación. Si ya te ha pasado: entra en
[aistudio.google.com/apikey](https://aistudio.google.com/apikey), borra esa
clave y crea otra. Es un minuto y te ahorra un disgusto.

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

Se lo pides a Claude por el chat («comprueba que todo funciona») o lo
ejecutas tú:

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

## 6. Crear tu primer vídeo

Abre una terminal dentro de VS Code y lanza:

```bash
claude
```

Y escribe, pegando tus URLs detrás:

```
/nuevo-video agentes de IA en atención al cliente
https://youtu.be/AAAAAAA  https://youtu.be/BBBBBBB
```

A partir de aquí **todo va por el chat**. Claude te hace una sola ronda de
preguntas y tú contestas escribiendo:

| Te pregunta | Contestas algo como |
|---|---|
| El tema, si no lo has dicho | «agentes de IA en atención al cliente» |
| Las referencias | pegas las URLs, una detrás de otra |
| Si tienes foto para la miniatura | «está en mi Escritorio, se llama foto.jpg» |
| Si hay algo que quieras contar sí o sí | lo que sea |

Los archivos los copia él a `input/` por ti. **Tú no mueves ni editas nada.**

Te avisa antes de cualquier operación que cueste dinero, y al terminar
tendrás una carpeta en `output/` con un `PACK-YOUTUBE.html` que abres con
doble clic.

---

## 7. Opcional: dejarlo preparado antes

Si prefieres tenerlo todo listo antes de hablar con Claude, puedes:

### Datos de tu canal (recomendado, una sola vez)

Copia `input/channel-context/canal.example.md` a `canal.md` y rellénalo.
Mejora mucho los ángulos, los títulos y el SEO, porque el sistema sabe a
quién le hablas y cómo hablas. También puedes pedirle a Claude que lo
rellene contigo por el chat.

### Tus referencias

En `input/REFERENCIAS.md`: el tema, las URLs (**de vídeos públicos**) y tus
notas. Si está relleno, Claude lo usa y no te pregunta.

### Archivos

| Qué | Dónde |
|---|---|
| Tu foto para la miniatura | `input/images/` |
| Vídeos locales o privados | `input/videos/` |
| PDFs, informes, notas | `input/documents/` |

---

## Cambiar de configuración más adelante

Lo más cómodo: escribe `/configurar` en Claude Code y te guía.

Si prefieres hacerlo tú:

```bash
python3 scripts/setup.py                     # completa lo que falte
python3 scripts/setup.py --crear-env         # solo crea el .env vacío
python3 scripts/setup.py --reconfigure       # vuelve a preguntar todo
python3 scripts/setup.py --provider gemini   # solo un proveedor
python3 scripts/models.py --refresh          # redetectar modelos
```

O abre `.env` en VS Code y edita la línea que quieras.

---

## Problemas frecuentes

| Mensaje | Qué pasa | Solución |
|---|---|---|
| `command not found: python3` | Python no instalado o fuera del PATH | reinstala marcando "Add to PATH"; en Windows prueba `python` |
| `FALTA DEPENDENCIA ... google-genai` | falta el SDK | `pip3 install -r requirements.txt` |
| `FALTA CONFIGURACIÓN GEMINI_API_KEY` | sin clave | pega la clave en `.env` (paso 4) |
| La clave está en `.env` y aun así falla | espacios o comillas de más | deja `GEMINI_API_KEY=AIza...` limpio y guarda |
| No veo el archivo `.env` en VS Code | VS Code oculta los archivos con punto | Ctrl+P / Cmd+P y escribe `.env` |
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
