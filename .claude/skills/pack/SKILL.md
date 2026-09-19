---
name: pack
description: Monta o reconstruye el PACK-YOUTUBE.html de un proyecto a partir de sus archivos Markdown. Úsalo al terminar el flujo o cada vez que se modifique alguna sección del pack.
allowed-tools: Bash(python3 scripts/build_pack.py *), Read, Glob
---

# Montar el pack HTML

```bash
python3 scripts/build_pack.py output/NOMBRE-DEL-VIDEO
# o, para el proyecto más reciente:
python3 scripts/build_pack.py --last
```

## Qué hace

Lee `01-RESEARCH.md` … `08-SOURCES.md` y `thumbnails/*.png` y genera un
único `PACK-YOUTUBE.html`:

- se abre con doble clic, sin servidor ni internet;
- modo claro/oscuro automático, legible en móvil;
- las etiquetas `[FUENTE DEL VÍDEO]`, `[FUENTE EXTERNA]` e `[INFERENCIA]`
  se resaltan con color, para ver de un golpe qué está verificado;
- las miniaturas se enlazan por ruta relativa, así que la carpeta se puede
  mover o comprimir entera;
- se imprime a PDF correctamente.

## Antes de montarlo

Comprueba que no queda ninguna sección con el texto `> Pendiente.`:
esas se marcan como pendientes en el HTML. Si falta alguna a propósito
(por ejemplo, sin imágenes generadas), dilo al usuario al entregar.

## Al entregar

Da la ruta completa del archivo y una frase por sección clave: ángulo
recomendado, título recomendado y qué queda sin verificar.
