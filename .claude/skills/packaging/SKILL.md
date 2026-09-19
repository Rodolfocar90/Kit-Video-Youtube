---
name: packaging
description: Genera 10 títulos para el vídeo con su análisis (caracteres, mecanismo de curiosidad, promesa y concepto de miniatura que lo complementa) y selecciona los 3 mejores pares título+miniatura. Produce 05-TITLES.md.
allowed-tools: Read, Write, Edit, Glob
---

# Packaging: títulos

Lee `01-RESEARCH.md` y `02-ANGLE.md` antes de escribir nada. Los títulos
salen del ángulo elegido, no de la nada.

## Archivo `05-TITLES.md`

Primero, la tabla resumen de los 10:

```markdown
| # | Título | Car. | Mecanismo | Promesa |
|---|---|---|---|---|
```

Después, cada título desarrollado:

```markdown
### Título N

- **Título**: <texto exacto>
- **Caracteres**: N   (cuenta los caracteres REALES, espacios incluidos)
- **Mecanismo de curiosidad**: hueco de información / contradicción /
  cifra concreta / consecuencia / comparación / urgencia real / rareza
- **Promesa**: qué se lleva el espectador si hace clic
- **Concepto de miniatura que lo complementa**: qué debe MOSTRAR la imagen
  para completar el título sin repetirlo
- **A quién le hace clic**:
- **Riesgo**: ¿promete más de lo que el vídeo da? Si sí, corrígelo o descártalo.
```

## Reglas

1. **Prioriza 60 caracteres o menos.** Al menos 7 de los 10 deben cumplirlo.
   Cuenta los caracteres de verdad, uno a uno; no estimes.
2. **Variedad de mecanismos.** Si tres títulos usan el mismo truco, sobran dos.
3. **Nada de clickbait falso.** Todo lo que promete el título tiene que estar
   en la estructura del vídeo. Si no está, cambia el título o el vídeo.
4. **La miniatura no repite el título.** El título dice una cosa, la imagen
   muestra otra, y juntos generan la pregunta. Si la miniatura solo pone el
   título en texto, el concepto está mal.
5. **Lenguaje natural**, el del espectador. Sin jerga corporativa, sin
   MAYÚSCULAS gritadas, sin emojis salvo que el canal ya los use.
6. **Sin números inventados.** Un "3x más rápido" solo entra si está
   verificado en la investigación.

## Selección final

```markdown
## Los 3 mejores pares título + miniatura

### Recomendado
- Título:
- Miniatura:
- Por qué este par gana: qué pregunta abre la combinación
- A quién ataca:

### Alternativa A / ### Alternativa B
(igual formato)

## Descartados y por qué
Una línea por título descartado. Es información útil, no relleno.
```

Los 3 elegidos deben apuntar a **públicos o entradas distintas**, para que
el creador tenga opciones reales de test, no tres versiones de lo mismo.
