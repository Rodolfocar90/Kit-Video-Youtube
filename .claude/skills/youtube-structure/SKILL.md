---
name: youtube-structure
description: Genera el ángulo, los ganchos y la estructura completa del vídeo a partir de la investigación (02-ANGLE.md, 03-HOOKS.md, 04-STRUCTURE.md). Úsalo cuando ya exista 01-RESEARCH.md y haya que decidir el enfoque y el esqueleto del vídeo.
allowed-tools: Read, Write, Edit, Glob, Bash(python3 scripts/*)
---

# Ángulo, ganchos y estructura

Lee antes `output/NOMBRE/01-RESEARCH.md` y, si existe,
`input/channel-context/*.md`.

**Nunca escribas el guion palabra por palabra.** Escribes lo que el creador
tiene que contar, no cómo lo tiene que decir.

---

## A) `02-ANGLE.md` — tres ángulos

Por cada ángulo:

```markdown
### Ángulo N: <nombre corto>

- **Enfoque**: en una frase.
- **Promesa principal**: qué se lleva el espectador. Concreta y cumplible.
- **Para quién**: público específico, no "todo el mundo".
- **Diferenciación**: en qué se separa de CADA referencia analizada
  (cita la referencia).
- **Por qué funcionaría ahora**: apóyalo en la investigación.
- **Qué exige**: datos, demo, edición, material extra.
- **Riesgo**: qué puede salir mal o resultar flojo.
```

Cierra con **ángulo recomendado** y dos líneas de por qué. Uno solo.

Los tres ángulos tienen que ser **de verdad distintos**: distinto público,
distinta promesa o distinto formato. Tres variantes del mismo enfoque no
sirven de nada.

---

## B) `03-HOOKS.md` — cinco ganchos

Cada gancho: **máximo 20 segundos** hablados (unas 50-55 palabras).

```markdown
### Gancho N — <mecanismo: pregunta abierta / dato brutal / contradicción /
                 demostración / historia>

- **Puntos que debe decir** (viñetas, NO texto literal):
  - …
- **Qué curiosidad abre**: y en qué minuto del vídeo se cierra.
- **Beneficio que adelanta**:
- **Duración estimada**: Xs
- **Apoyo visual en los 3 primeros segundos**:
- **Por qué no es genérico**:
- **Verificación**: ¿toda afirmación está respaldada? Marca la fuente.
```

Prohibido: "Hola, bienvenidos a un nuevo vídeo", "hoy os traigo",
presentarse, pedir suscripción antes del gancho, prometer lo que el vídeo
no va a dar.

Los 5 ganchos deben usar **mecanismos diferentes**.

---

## C) `04-STRUCTURE.md` — estructura completa

Empieza con una tabla de bloques (nombre, minuto estimado, objetivo).
Después, por cada bloque:

```markdown
## Bloque N — <nombre>  (~min X a Y)

**Objetivo del bloque**: para qué existe. Si no lo tienes claro, sobra.

**Puntos que debe contar el creador**
- … (viñetas; nunca frases para leer)

**Información importante**
- Dato + origen (`[FUENTE DEL VÍDEO] 12:30` / `[FUENTE EXTERNA] url` / `[INFERENCIA]`)

**Ejemplos a usar**

**Demostraciones recomendadas**
Qué mostrar en pantalla y por qué convence más que contarlo.

**Recursos visuales**
B-roll, gráficos, capturas, rótulos.

**Timestamps de referencia útiles**
`Fuente 1, 08:15` — para ver cómo lo explicaron (para superarlo, no copiarlo).

**Riesgo de pérdida de retención**
Dónde se puede caer y qué hacer: acortar, ejemplo, cambio de plano, pregunta.

**Transición al bloque siguiente**
La idea puente en una línea.
```

Cierra el archivo con:

- **Cierre y llamada a la acción**: qué pedir y por qué encaja.
- **Duración total estimada** y reparto por bloques.
- **Lo imprescindible**: si hay que recortar, qué se queda.

## Control de calidad antes de guardar

- ¿Cada bloque tiene objetivo propio y no repite otro?
- ¿Hay al menos un momento de demostración o prueba real?
- ¿Se cierra la curiosidad que abrió el gancho?
- ¿Queda algún texto redactado para leer? Si sí, conviértelo en viñetas.
