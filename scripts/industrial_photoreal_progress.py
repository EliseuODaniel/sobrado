"""Galeria provisória: somente arquivos concluídos, até a entrega final assumir."""
from html import escape
import json
import os
from pathlib import Path
import time

from PIL import Image, ImageOps

import industrial_photoreal_data as data

ROOT, CFG = data.ROOT, data.CFG
REPORT, OUT = ROOT / CFG['report_directory'], ROOT / CFG['render_directory']


def read(path):
    try: return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError): return None


def main():
    thumbnails = OUT / '06-galerias'; thumbnails.mkdir(parents=True, exist_ok=True)
    seen = set()
    while True:
        model = read(REPORT / 'modelo.json')
        if not model: time.sleep(2); continue
        rows = read(REPORT / 'renders.json') or []
        rows = [r for r in rows if r['blend_sha256'] == model['blend_sha256'] and (ROOT / r['file']).is_file()]
        if len(rows) == len(model['jobs']):
            print('PROGRESS_GALLERY_COMPLETE_HANDOFF', len(rows), flush=True); return
        titles = {j['id']: j['title'] for j in model['jobs']}
        for row in rows:
            key = (row['id'], row['sha256'])
            if key in seen: continue
            path = ROOT / row['file']
            assert data.sha(path) == row['sha256']
            with Image.open(path) as image:
                ImageOps.contain(image.convert('RGB'), (960, 720)).save(thumbnails / (row['id'] + '.jpg'), quality=91)
            seen.add(key)
        cards = []
        for row in rows:
            source = Path(os.path.relpath(ROOT / row['file'], OUT)).as_posix()
            cards.append(f'<figure><a href="{escape(source)}"><img src="06-galerias/{row["id"]}.jpg" alt="{escape(titles[row["id"]])}"></a><figcaption>{escape(titles[row["id"]])} · final 4K</figcaption></figure>')
        previews = read(REPORT / 'previas.json') or []
        preview_cards = []
        for row in previews:
            if row['blend_sha256'] != model['blend_sha256']: continue
            source = Path(os.path.relpath(ROOT / row['file'], OUT)).as_posix()
            preview_cards.append(f'<figure><a href="{escape(source)}"><img src="{escape(source)}" alt="Prévia: {escape(titles[row["id"]])}"></a><figcaption>{escape(titles[row["id"]])} · prévia 960 × 720</figcaption></figure>')
        native = Path(os.path.relpath(ROOT / model['blend'], OUT)).as_posix()
        html = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="30"><title>Industrial v06 / imagens em processamento</title><style>body{margin:0;padding:30px;background:#15191a;color:#eee5d8;font:17px system-ui;line-height:1.6}main,header{max-width:1450px;margin:auto}a{color:#d7b68d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}figure{margin:0;background:#252b2c;border-radius:8px;overflow:hidden}img{width:100%;height:auto;display:block}figcaption{padding:12px}h1{font-size:clamp(28px,4vw,48px)}p{max-width:85ch}</style></head><body><header><p>RESIDÊNCIA 07 · INDUSTRIAL V06</p><h1>Imagens finais em processamento</h1>'''+f'<p><strong>{len(rows)} de {len(model["jobs"])} imagens 4K concluídas.</strong> Esta página atualiza a cada 30 segundos. As prévias abaixo já mostram o bar sem geladeira e os acabamentos novos.</p><p><a href="{escape(native)}">Modelo Blender editável</a></p></header><main><h2>Finais 4K disponíveis</h2><div class="grid">'+(''.join(cards) or '<p>Calculando a primeira imagem final.</p>')+'</div><h2>Prévias de materiais e iluminação</h2><div class="grid">'+''.join(preview_cards)+'</div><p>Medidas documentais da base 07; anexos e móveis com dimensões de estudo. A geladeira da cozinha permanece. O entorno é ilustrativo.</p></main></body></html>'
        # A entrega definitiva assume a página quando a última imagem termina.
        latest = read(REPORT / 'renders.json') or []
        if len([r for r in latest if r['blend_sha256'] == model['blend_sha256']]) == len(model['jobs']): continue
        temporary = OUT / 'galeria.progress.tmp'; temporary.write_text(html); temporary.replace(OUT / 'galeria.html')
        print('PROGRESS_GALLERY_UPDATED', len(rows), flush=True)
        time.sleep(30)


if __name__ == '__main__': main()
