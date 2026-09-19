#!/usr/bin/env python3
"""Monta PACK-YOUTUBE.html a partir de los archivos Markdown del proyecto.

  python3 scripts/build_pack.py output/MI-VIDEO
  python3 scripts/build_pack.py --last          # el proyecto más reciente

El HTML resultante:
  * es un único archivo, sin servidor ni internet (se abre con doble clic);
  * enlaza las miniaturas por ruta relativa (thumbnails/...), así que si
    mueves la carpeta se mueve todo junto;
  * tiene modo claro/oscuro automático y se imprime bien en PDF.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.markdown import to_html  # noqa: E402
from lib.paths import IMAGE_EXT, OUTPUT_DIR, rel  # noqa: E402

SECTIONS = [
    ("01-RESEARCH.md", "Investigación", "01"),
    ("02-ANGLE.md", "Ángulo", "02"),
    ("03-HOOKS.md", "Ganchos", "03"),
    ("04-STRUCTURE.md", "Estructura", "04"),
    ("05-TITLES.md", "Títulos", "05"),
    ("06-THUMBNAILS.md", "Miniaturas", "06"),
    ("07-SEO.md", "SEO y publicación", "07"),
    ("08-SOURCES.md", "Fuentes", "08"),
]

CSS = """
:root{
  --bg:#f7f7f8; --panel:#ffffff; --ink:#16181d; --muted:#61656e;
  --line:#e3e4e8; --accent:#c0392b; --accent-soft:#fdecea;
  --ok:#1f7a45; --ok-soft:#e6f4ec; --warn:#a4531c; --warn-soft:#fdf0e4;
  --info:#1d4f91; --info-soft:#e8f0fb; --code:#f1f1f4;
  --radius:12px; --shadow:0 1px 3px rgba(0,0,0,.06),0 8px 24px rgba(0,0,0,.05);
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#101114; --panel:#181a1f; --ink:#e8e9ec; --muted:#9a9ea8;
    --line:#2a2d34; --accent:#ff6b5a; --accent-soft:#2c1a18;
    --ok:#5fd18f; --ok-soft:#14251b; --warn:#f0b86e; --warn-soft:#2a2016;
    --info:#7cb0f5; --info-soft:#151f2e; --code:#20232a;
    --shadow:0 1px 3px rgba(0,0,0,.5);
  }
}
*{box-sizing:border-box}
code,pre,a,td,th,li,p,h1,h2,h3{overflow-wrap:anywhere}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.layout{display:grid; grid-template-columns:260px minmax(0,1fr); gap:32px;
  max-width:1280px; margin:0 auto; padding:32px 24px 96px}
.layout > *{min-width:0}
/* ---------- navegación ---------- */
nav{position:sticky; top:32px; align-self:start; max-height:calc(100vh - 64px); overflow:auto}
nav .marca{font-weight:700; font-size:.78rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin-bottom:6px}
nav h2{font-size:1.05rem; margin:0 0 18px; line-height:1.3}
nav a{display:flex; gap:10px; align-items:baseline; padding:8px 12px; margin-bottom:2px;
  border-radius:8px; color:var(--muted); text-decoration:none; font-size:.92rem;
  border:1px solid transparent}
nav a:hover{background:var(--panel); color:var(--ink); border-color:var(--line)}
nav a .num{font-variant-numeric:tabular-nums; font-size:.75rem; color:var(--accent);
  font-weight:700; min-width:18px}
nav .meta{margin-top:20px; padding-top:16px; border-top:1px solid var(--line);
  font-size:.8rem; color:var(--muted)}
/* ---------- contenido ---------- */
header.pack{background:var(--panel); border:1px solid var(--line);
  border-radius:var(--radius); padding:28px 32px; margin-bottom:28px; box-shadow:var(--shadow)}
header.pack .kicker{font-size:.75rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--accent); font-weight:700}
header.pack h1{margin:8px 0 12px; font-size:clamp(1.5rem,3.4vw,2.1rem); line-height:1.2}
header.pack p{margin:0; color:var(--muted)}
.chips{display:flex; flex-wrap:wrap; gap:8px; margin-top:18px}
.chip{font-size:.78rem; padding:5px 11px; border-radius:99px; background:var(--bg);
  border:1px solid var(--line); color:var(--muted)}
section.card{background:var(--panel); border:1px solid var(--line);
  border-radius:var(--radius); padding:28px 32px; margin-bottom:24px; box-shadow:var(--shadow);
  scroll-margin-top:24px}
section.card > .cabecera{display:flex; align-items:center; gap:12px;
  padding-bottom:14px; margin-bottom:18px; border-bottom:1px solid var(--line)}
section.card > .cabecera .num{font-size:.78rem; font-weight:700; color:#fff;
  background:var(--accent); border-radius:6px; padding:3px 8px}
section.card > .cabecera h2{margin:0; font-size:1.25rem}
.contenido h1{font-size:1.35rem; margin:26px 0 10px}
.contenido h2{font-size:1.15rem; margin:24px 0 10px}
.contenido h3{font-size:1rem; margin:20px 0 8px; color:var(--accent)}
.contenido h4,.contenido h5,.contenido h6{font-size:.95rem; margin:16px 0 6px}
.contenido > :first-child{margin-top:0}
.contenido p{margin:0 0 12px}
.contenido ul,.contenido ol{margin:0 0 14px; padding-left:22px}
.contenido li{margin-bottom:6px}
.contenido blockquote{margin:0 0 16px; padding:12px 18px; border-left:3px solid var(--accent);
  background:var(--accent-soft); border-radius:0 8px 8px 0}
.contenido blockquote p{margin:0}
.contenido code{background:var(--code); padding:2px 6px; border-radius:5px;
  font-size:.88em; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.contenido pre{background:var(--code); padding:16px; border-radius:10px; overflow:auto;
  border:1px solid var(--line)}
.contenido pre code{background:none; padding:0}
.contenido a{color:var(--info); text-decoration:none; border-bottom:1px solid transparent}
.contenido a:hover{border-bottom-color:currentColor}
.contenido hr{border:0; border-top:1px solid var(--line); margin:24px 0}
.tabla{overflow-x:auto; margin:0 0 18px; border:1px solid var(--line); border-radius:10px}
table{border-collapse:collapse; width:100%; font-size:.92rem}
th,td{padding:10px 14px; text-align:left; border-bottom:1px solid var(--line);
  vertical-align:top}
th{background:var(--bg); font-size:.78rem; text-transform:uppercase;
  letter-spacing:.06em; color:var(--muted)}
tbody tr:last-child td{border-bottom:0}
/* ---------- etiquetas de procedencia ---------- */
.tag{font-size:.7rem; font-weight:700; letter-spacing:.04em; padding:2px 7px;
  border-radius:5px; white-space:nowrap}
.tag-video{background:var(--accent-soft); color:var(--accent)}
.tag-extern{background:var(--info-soft); color:var(--info)}
.tag-infer{background:var(--warn-soft); color:var(--warn)}
.tag-ok{background:var(--ok-soft); color:var(--ok)}
.tag-warn{background:var(--warn-soft); color:var(--warn)}
.leyenda{display:flex; flex-wrap:wrap; gap:14px; font-size:.8rem;
  color:var(--muted); margin-top:16px}
/* ---------- miniaturas ---------- */
.galeria{display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:18px}
.galeria figure{margin:0; border:1px solid var(--line); border-radius:10px;
  overflow:hidden; background:var(--bg)}
.galeria img{display:block; width:100%; aspect-ratio:16/9; object-fit:cover; background:#000}
.galeria figcaption{padding:10px 14px; font-size:.82rem; color:var(--muted);
  display:flex; justify-content:space-between; gap:8px}
.vacio{color:var(--muted); font-size:.9rem; padding:14px; border:1px dashed var(--line);
  border-radius:10px; background:var(--bg)}
footer.pack{max-width:1280px; margin:0 auto; padding:0 24px 48px;
  color:var(--muted); font-size:.82rem}
/* ---------- móvil e impresión ---------- */
@media (max-width:900px){
  .layout{grid-template-columns:minmax(0,1fr); gap:20px; padding:20px 16px 64px}
  nav{position:static; max-height:none}
  nav .lista{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:4px}
  nav a{margin:0; background:var(--panel); border-color:var(--line)}
  section.card,header.pack{padding:22px 18px}
}
@media print{
  body{background:#fff}
  nav,.no-print{display:none}
  .layout{display:block; max-width:none; padding:0}
  section.card,header.pack{box-shadow:none; border:0; border-bottom:1px solid #ccc;
    border-radius:0; page-break-inside:avoid; padding:0 0 18px; margin-bottom:22px}
}
"""

JS = """
document.querySelectorAll('nav a[href^="#"]').forEach(function(link){
  link.addEventListener('click', function(){
    document.querySelectorAll('nav a').forEach(function(a){ a.style.background=''; });
  });
});
var observer = new IntersectionObserver(function(entries){
  entries.forEach(function(entry){
    var link = document.querySelector('nav a[href="#' + entry.target.id + '"]');
    if (link) { link.style.color = entry.isIntersecting ? 'var(--ink)' : ''; }
  });
}, { rootMargin: '-10% 0px -80% 0px' });
document.querySelectorAll('section.card').forEach(function(s){ observer.observe(s); });
"""


def find_last_project() -> Path:
    candidates = [p for p in OUTPUT_DIR.glob("*") if p.is_dir()]
    if not candidates:
        raise SystemExit(f"[ERROR] No hay proyectos en {rel(OUTPUT_DIR)}.\n"
                         "  Crea uno con:  python3 scripts/new_project.py \"Tema\"")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def read_section(folder: Path, filename: str) -> str | None:
    path = folder / filename
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text or "> Pendiente." in text:
        return None
    return text


def thumbnails(folder: Path) -> list[Path]:
    thumbs_dir = folder / "thumbnails"
    if not thumbs_dir.is_dir():
        return []
    return sorted(p for p in thumbs_dir.iterdir()
                  if p.is_file() and p.suffix.lower() in IMAGE_EXT)


def build(folder: Path) -> Path:
    meta: dict = {}
    meta_file = folder / "proyecto.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}

    titulo = meta.get("titulo_final") or meta.get("titulo_provisional") or folder.name
    generado = time.strftime("%d/%m/%Y %H:%M")

    nav_items, cards, presentes = [], [], []
    for filename, label, num in SECTIONS:
        content = read_section(folder, filename)
        anchor = f"s{num}"
        estado = "" if content else " (pendiente)"
        nav_items.append(
            f'<a href="#{anchor}"><span class="num">{num}</span>'
            f'<span>{html.escape(label)}{estado}</span></a>'
        )
        if content:
            presentes.append(label)
            body = to_html(content)
        else:
            body = ('<p class="vacio">Sección todavía sin generar. Vuelve a ejecutar '
                    f'el flujo <code>/nuevo-video</code> o rellena <code>{filename}</code>'
                    ' y reconstruye el pack.</p>')
        cards.append(
            f'<section class="card" id="{anchor}">'
            f'<div class="cabecera"><span class="num">{num}</span>'
            f'<h2>{html.escape(label)}</h2></div>'
            f'<div class="contenido">{body}</div></section>'
        )

    thumbs = thumbnails(folder)
    if thumbs:
        figures = "".join(
            f'<figure><img src="thumbnails/{html.escape(p.name)}" '
            f'alt="Miniatura {i + 1}" loading="lazy">'
            f'<figcaption><span>{html.escape(p.name)}</span>'
            f'<span>{p.stat().st_size / 1024:.0f} KB</span></figcaption></figure>'
            for i, p in enumerate(thumbs)
        )
        gallery = f'<div class="galeria">{figures}</div>'
    else:
        gallery = ('<p class="vacio">Aún no hay imágenes generadas. Los conceptos de '
                   'miniatura están en la sección 06. Para generarlas:<br>'
                   '<code>python3 scripts/thumbnail.py --prompt-file … --out '
                   'thumbnails/thumbnail-01.png</code></p>')
    nav_items.append('<a href="#imagenes"><span class="num">IMG</span>'
                     '<span>Imágenes</span></a>')
    cards.append(
        '<section class="card" id="imagenes">'
        '<div class="cabecera"><span class="num">IMG</span>'
        '<h2>Miniaturas generadas</h2></div>'
        f'<div class="contenido">{gallery}</div></section>'
    )

    fuentes = meta.get("fuentes") or []
    chips = [f'<span class="chip">{len(presentes)}/8 secciones</span>',
             f'<span class="chip">{len(thumbs)} imagen(es)</span>']
    if fuentes:
        chips.append(f'<span class="chip">{len(fuentes)} fuente(s) analizada(s)</span>')
    chips.append(f'<span class="chip">Generado: {generado}</span>')

    html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)} — Pack de YouTube</title>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
  <nav>
    <div class="marca">Pack de YouTube</div>
    <h2>{html.escape(titulo)}</h2>
    <div class="lista">{''.join(nav_items)}</div>
    <div class="meta">
      Carpeta: <code>{html.escape(folder.name)}</code><br>
      Generado: {generado}
    </div>
  </nav>
  <main>
    <header class="pack">
      <div class="kicker">Preparación de vídeo</div>
      <h1>{html.escape(titulo)}</h1>
      <p>Todo lo necesario para grabar: investigación, ángulo, ganchos,
      estructura, títulos, miniaturas y SEO. Este archivo es autónomo:
      no necesita internet ni servidor.</p>
      <div class="chips">{''.join(chips)}</div>
      <div class="leyenda">
        <span><span class="tag tag-video">[FUENTE DEL VÍDEO]</span> lo dice el material analizado</span>
        <span><span class="tag tag-extern">[FUENTE EXTERNA]</span> verificado en la web</span>
        <span><span class="tag tag-infer">[INFERENCIA]</span> deducción, no verificado</span>
      </div>
    </header>
    {''.join(cards)}
  </main>
</div>
<footer class="pack">
  Generado por el Kit de Vídeo para YouTube. El guion palabra por palabra lo
  pones tú: este pack es la preparación, no el texto a leer.
</footer>
<script>{JS}</script>
</body>
</html>
"""
    out = folder / "PACK-YOUTUBE.html"
    out.write_text(html_doc, encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Monta el PACK-YOUTUBE.html.")
    parser.add_argument("proyecto", nargs="?", help="ruta a output/NOMBRE-DEL-VIDEO")
    parser.add_argument("--last", action="store_true", help="usa el proyecto más reciente")
    args = parser.parse_args()

    if args.proyecto:
        folder = Path(args.proyecto)
        if not folder.is_dir():
            candidate = OUTPUT_DIR / args.proyecto
            if candidate.is_dir():
                folder = candidate
            else:
                raise SystemExit(f"[ERROR] No existe la carpeta: {args.proyecto}")
    elif args.last:
        folder = find_last_project()
    else:
        raise SystemExit("[ERROR] Indica la carpeta del proyecto o usa --last.")

    out = build(folder)
    print(f"\n  Pack montado: {rel(out)}")
    print(f"  Ábrelo con doble clic o:  open '{out}'\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
