---
name: configurar
description: Configura o reconfigura las claves de API del kit (Gemini, OpenRouter, Higgsfield) y diagnostica problemas de conexión. Úsalo cuando falten claves, fallen las llamadas a la API o el usuario quiera cambiar de proveedor.
allowed-tools: Bash(python3 scripts/setup.py *), Bash(python3 scripts/doctor.py *), Bash(python3 scripts/models.py *), Bash(pip3 install -r requirements.txt), Bash(ls *), Read
---

# Configuración del kit

## Regla de oro sobre secretos

**Nunca pidas una clave por el chat y nunca la escribas tú en un archivo.**
Todo lo demás del kit lo haces tú; la clave la pone el usuario, porque si
pasa por el chat queda grabada en el historial de la conversación.

Si el usuario pega una clave en el chat: dile que la revoque en el panel
del proveedor y genere otra. Es incómodo, pero es lo correcto.

## Primera vez: hazlo tú todo menos la clave

El usuario no tiene que escribir comandos. Este es el orden:

**1. Dependencias** — si `doctor.py` dice que falta el SDK:

```bash
pip3 install -r requirements.txt
```

**2. Prepara el archivo de claves** (no toca ningún secreto, lo crea vacío):

```bash
python3 scripts/setup.py --crear-env
```

**3. Pídele solo esto**, con estos cuatro pasos y nada más:

> Necesito tu clave de Gemini. Es gratis y se tarda un minuto:
>
> 1. Entra en https://aistudio.google.com/apikey y pulsa "Create API key".
> 2. Abre el archivo `.env` de esta carpeta en VS Code.
> 3. Pega la clave después de `GEMINI_API_KEY=` (sin espacios ni comillas).
> 4. Guarda con Ctrl+S (Cmd+S en Mac) y dime "ya está".
>
> No me la pegues por el chat: ahí quedaría guardada en el historial.

**4. Valida** cuando diga que ya está:

```bash
python3 scripts/doctor.py
```

Si falla, dile en una línea qué revisar: que no haya espacios ni comillas,
que haya guardado el archivo, que la clave empiece por `AIza`.

### Alternativa con terminal

Quien prefiera el terminal tiene el modo interactivo, que oculta la clave
al teclearla. Menciónalo **solo si pregunta** o si le cuesta editar el
archivo:

```bash
python3 scripts/setup.py
```

## Diagnóstico primero

```bash
python3 scripts/doctor.py
```

Comprueba dependencias, permisos de `.env`, protección en `.gitignore`,
claves presentes (enmascaradas), conexión con cada proveedor y modelos
disponibles. No imprime ninguna clave.

## Cambiar o añadir claves después

Dos vías, según lo que prefiera el usuario:

**Sin terminal** — dile que abra `.env` en VS Code y edite la línea que
toque. Después valida tú con `python3 scripts/doctor.py`.

**Con terminal** — el asistente interactivo, que oculta lo que teclea.
Estos comandos los ejecuta él, no tú:

```bash
python3 scripts/setup.py                          # todo lo que falte
python3 scripts/setup.py --provider gemini        # solo uno
python3 scripts/setup.py --reconfigure            # volver a preguntar todo
```

## Dónde conseguir cada clave

| Proveedor | Necesario | Dónde | Para qué |
|---|---|---|---|
| Gemini / Google AI | **sí** | https://aistudio.google.com/apikey | analizar vídeo, YouTube, documentos, generar miniaturas |
| OpenRouter | no | https://openrouter.ai/keys | solo texto alternativo; **no analiza vídeo** |
| Higgsfield | no | https://cloud.higgsfield.ai/ | segundo proveedor de imagen |

Higgsfield muestra la clave **una sola vez** al crearla. Avísalo antes.

## Modelos

```bash
python3 scripts/models.py            # qué usará el kit
python3 scripts/models.py --refresh  # volver a detectar
python3 scripts/models.py --all      # ver todos los de la cuenta
```

El kit detecta los modelos disponibles en vez de llevarlos escritos a
fuego, porque los IDs de Gemini cambian cada pocos meses. Para gastar
menos, se puede fijar un modelo `flash` en `.env` con `GEMINI_VIDEO_MODEL`.

## Problemas típicos

| Síntoma | Causa | Solución |
|---|---|---|
| `FALTA DEPENDENCIA` | falta el SDK | instálalo tú: `pip3 install -r requirements.txt` |
| `.env no existe` | primera vez | `python3 scripts/setup.py --crear-env` |
| `API_KEY_INVALID` | clave mal copiada o revocada | genera otra y `setup.py --provider gemini` |
| `RESOURCE_EXHAUSTED` | cuota agotada | espera o cambia a un modelo `flash` |
| `SIN MODELO` de imagen | la cuenta no tiene modelo de imagen | usa Higgsfield o entrega solo conceptos |
| `404` en Higgsfield | ruta de application incorrecta | cópiala de la página del modelo en cloud.higgsfield.ai |
