---
name: thumbnail
description: Crea conceptos de miniatura para YouTube (06-THUMBNAILS.md) y, si el usuario lo autoriza, genera las imágenes 16:9 en output/NOMBRE/thumbnails/ usando la foto del creador como referencia. Úsalo cuando haya que diseñar o generar miniaturas.
allowed-tools: Read, Write, Edit, Glob, Bash(python3 scripts/thumbnail.py *), Bash(python3 scripts/doctor.py *), Bash(ls *)
---

# Miniaturas

Dos fases. **Primero los conceptos, siempre.** Las imágenes solo si el
usuario lo pide, porque cuestan dinero.

## Fase 1 — Conceptos: `06-THUMBNAILS.md`

Lee `05-TITLES.md` primero: cada concepto acompaña a un título concreto.

Crea **3 conceptos**, uno por cada par recomendado en packaging:

```markdown
### Concepto N — para el título: "<título>"

- **Composición**: qué va a la izquierda, al centro y a la derecha.
  Regla práctica: un solo foco. Si hay dos, no hay ninguno.
- **Protagonista**: el creador / un objeto / una pantalla / una comparación.
- **Expresión** (si sale el creador): concreta y creíble
  (sorpresa contenida, concentración, incredulidad…). Nunca "cara graciosa".
- **Fondo**: color, profundidad, desenfoque, escenario.
- **Elemento principal**: el objeto o dato que lleva el peso visual.
- **Texto**: 2-4 palabras como máximo. Si el título ya lo dice, mejor sin texto.
- **Jerarquía visual**: qué se ve primero, segundo y tercero.
- **Contraste**: cómo se separa el sujeto del fondo (luz, color complementario,
  borde limpio). Debe leerse a 120 px de ancho en un móvil.
- **Relación con el título**: qué añade la imagen que el título NO dice.
- **Por qué funciona**: en una frase.
```

Cierra con:

- **Concepto recomendado** y por qué.
- **Prueba del pulgar**: los 3 conceptos en versión "¿se entiende a tamaño
  diminuto?" — si alguno no pasa, dilo y simplifícalo.

## Fase 2 — Generar imágenes (con coste)

Pregunta primero, siempre:

> «Voy a generar N imágenes 16:9. Tiene coste por imagen. ¿Adelante?»

### Con la foto del creador

Busca la foto: `ls input/images/`. Si no hay, pregunta por ella o genera
sin protagonista humano.

```bash
python3 scripts/thumbnail.py \
  --prompt-file output/NOMBRE/thumbnails/prompt-01.txt \
  --reference input/images/creador.jpg \
  --out output/NOMBRE/thumbnails/thumbnail-01.png --yes
```

Escribe antes el prompt en `thumbnails/prompt-01.txt`: descripción visual
en prosa, sin jerga de modelos, diciendo qué se ve y dónde. El script ya
añade las reglas de calidad y formato 16:9.

### Proveedores

| Proveedor | Cuándo | Foto de referencia |
|---|---|---|
| `gemini` (por defecto) | siempre que haya modelo de imagen | sí, de serie |
| `higgsfield` | si el usuario lo ha configurado | solo con `HIGGSFIELD_IMAGE_EDIT_APP` en `.env` |

Si Gemini no tiene modelo de imagen en esa cuenta, el script lo dice.
Entonces: o se configura Higgsfield (`python3 scripts/setup.py --provider
higgsfield`), o se entregan solo los conceptos para que los monte a mano.
**Nunca finjas que has generado una imagen.**

### Después de generar

1. Comprueba que los archivos existen y pesan algo razonable.
2. Anota en `06-THUMBNAILS.md` qué archivo corresponde a qué concepto.
3. Revisa el texto de la imagen: los modelos cometen faltas. Si el texto
   sale mal, es mejor generar sin texto y ponerlo luego en un editor.
4. Reconstruye el pack: `python3 scripts/build_pack.py output/NOMBRE`

## Límites reales

- Formato 16:9 nativo, listo para YouTube.
- El límite de imágenes por orden es `MAX_IMAGES_PER_RUN` (3 por defecto).
- El parecido de la persona no será perfecto. Para una miniatura definitiva,
  lo habitual es usar la imagen generada como fondo y componer la foto real
  encima en un editor. Dilo si el resultado no convence.
- No generes imágenes de personas reales que no sean el propio creador.
