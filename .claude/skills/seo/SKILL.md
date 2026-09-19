---
name: seo
description: Genera la descripción de YouTube, keywords, tags, capítulos, entidades mencionadas y enlaces a citar. Produce 07-SEO.md. Úsalo cuando ya existan la estructura y los títulos del vídeo.
allowed-tools: Read, Write, Edit, Glob, WebSearch
---

# SEO y publicación

Lee `01-RESEARCH.md`, `04-STRUCTURE.md`, `05-TITLES.md` y `08-SOURCES.md`.

## Archivo `07-SEO.md`

### 1. Descripción de YouTube

Tres partes, claramente separadas:

- **Primeras 2-3 líneas** (lo que se ve sin desplegar): refuerzan la promesa
  del título e incluyen la keyword principal de forma natural.
- **Cuerpo**: 100-200 palabras. Qué resuelve el vídeo y para quién.
  En prosa legible, no una lista de palabras clave.
- **Bloque fijo**: capítulos, enlaces citados, recursos.

### 2. Keywords

```markdown
- **Keyword principal**: una sola. Con intención de búsqueda real.
- **Secundarias** (4-6): tabla | keyword | intención | dónde se usa |
- **Términos relacionados / semánticos** (8-12): vocabulario del tema
  que el espectador usaría. No son para meter a presión: son para escribir
  la descripción con naturalidad.
```

### 3. Tags

10-15 tags. Del más específico al más general (long tail primero).
Todos relacionados de verdad con el contenido.

### 4. Capítulos

Derivados de `04-STRUCTURE.md`, formato de YouTube:

```
00:00 <nombre del capítulo>
01:30 …
```

Reglas de YouTube: el primero es siempre `00:00`, mínimo 3 capítulos,
mínimo 10 segundos cada uno. Los minutos son **estimaciones** — dilo
claramente, el creador los ajusta tras editar.

### 5. Entidades importantes

Personas, empresas, productos, herramientas, estudios y lugares citados.
Tabla: | Entidad | Qué es | Dónde aparece | ¿Merece enlace? |

### 6. Enlaces y fuentes a citar

Los de `08-SOURCES.md` que aportan credibilidad. Con URL y una línea de
por qué citarlo. Distingue lo obligatorio (fuente de un dato usado) de lo
recomendable.

### 7. Publicación

- Miniatura elegida y su archivo.
- Texto de la miniatura (si lleva).
- Comentario fijado propuesto.
- Idea de Short/clip a partir de un momento concreto del vídeo.

## Prohibido

- **Keyword stuffing.** Si al leer la descripción en voz alta suena a
  máquina, está mal. La keyword principal aparece 2-3 veces como mucho,
  y solo donde encaja.
- Tags que no tienen que ver con el vídeo.
- Prometer en la descripción algo que no está en la estructura.
- Inventar URLs. Si no tienes la URL exacta, no la pongas.
