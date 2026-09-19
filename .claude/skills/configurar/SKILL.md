---
name: configurar
description: Configura o reconfigura las claves de API del kit (Gemini, OpenRouter, Higgsfield) y diagnostica problemas de conexión. Úsalo cuando falten claves, fallen las llamadas a la API o el usuario quiera cambiar de proveedor.
allowed-tools: Bash(python3 scripts/setup.py *), Bash(python3 scripts/doctor.py *), Bash(python3 scripts/models.py *), Bash(pip3 install -r requirements.txt), Read
---

# Configuración del kit

## Regla de oro sobre secretos

**Nunca pidas una clave por el chat y nunca la escribas en un archivo tú.**
El usuario la introduce en su terminal con el asistente, que la oculta al
teclear y la guarda solo en `.env` con permisos 600.

Si el usuario pega una clave en el chat: dile que la revoque y genere otra,
porque ha quedado en el historial de la conversación. Es lo correcto,
aunque sea incómodo.

## Diagnóstico primero

```bash
python3 scripts/doctor.py
```

Comprueba dependencias, permisos de `.env`, protección en `.gitignore`,
claves presentes (enmascaradas), conexión con cada proveedor y modelos
disponibles. No imprime ninguna clave.

## Configurar

```bash
python3 scripts/setup.py                          # todo lo que falte
python3 scripts/setup.py --provider gemini        # solo uno
python3 scripts/setup.py --reconfigure            # volver a preguntar todo
```

Dile al usuario que ejecute él el comando en su terminal, porque el
asistente es interactivo y oculta lo que teclea.

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
| `FALTA DEPENDENCIA` | falta el SDK | `pip3 install -r requirements.txt` |
| `API_KEY_INVALID` | clave mal copiada o revocada | genera otra y `setup.py --provider gemini` |
| `RESOURCE_EXHAUSTED` | cuota agotada | espera o cambia a un modelo `flash` |
| `SIN MODELO` de imagen | la cuenta no tiene modelo de imagen | usa Higgsfield o entrega solo conceptos |
| `404` en Higgsfield | ruta de application incorrecta | cópiala de la página del modelo en cloud.higgsfield.ai |
