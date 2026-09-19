# ¿Dónde están las skills?

En **`.claude/skills/`**, no en esta carpeta.

Ésa es la ruta donde Claude Code descubre las skills de un proyecto
(`.claude/skills/<nombre>/SKILL.md`). Si estuvieran aquí, en `skills/`,
Claude Code no las encontraría y no se activarían nunca.

## Las skills del kit

| Skill | Se invoca con | Qué hace |
|---|---|---|
| `nuevo-video` | `/nuevo-video` | flujo completo de principio a fin |
| `research` | automática | analiza y compara el material de referencia |
| `video-analysis` | automática | detalles técnicos y errores del análisis de vídeo |
| `youtube-structure` | automática | ángulo, ganchos y estructura |
| `packaging` | automática | 10 títulos con su análisis |
| `thumbnail` | automática | conceptos de miniatura y generación de imágenes |
| `seo` | automática | descripción, keywords, tags, capítulos |
| `pack` | `/pack` | monta el PACK-YOUTUBE.html |
| `configurar` | `/configurar` | claves de API y diagnóstico |

"Automática" significa que Claude Code las activa solo cuando hacen falta.
También puedes llamarlas a mano: `/research`, `/packaging`, etc.

## Subagentes

En `.claude/agents/`:

- `analista-video` — analiza un vídeo en contexto aislado (para lanzar
  varios en paralelo);
- `verificador` — comprueba cifras y afirmaciones contra fuentes externas.
