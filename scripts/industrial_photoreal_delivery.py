"""Galeria, caderno, comparações e conferência das imagens 4K industriais."""
import datetime as dt
from html import escape
import json
import math
import os
from pathlib import Path
import re
import shutil

import fitz
from PIL import Image, ImageDraw, ImageOps

import industrial_photoreal_data as data
from residence07_industrial_delivery import board, font

ROOT, CFG = data.ROOT, data.CFG
OUT, REPORT = ROOT / CFG['render_directory'], ROOT / CFG['report_directory']


def relative(path, parent=OUT):
    return Path(os.path.relpath(path, parent)).as_posix()


def prepare_images(model):
    folder = OUT / '06-galerias'; folder.mkdir(parents=True, exist_ok=True)
    for job in model['jobs']:
        with Image.open(ROOT / job['file']) as source:
            pic = source.convert('RGB')
            ImageOps.contain(pic, (960, 720)).save(folder / (job['id'] + '.jpg'), quality=91)
            ImageOps.contain(pic, (1800, 1350)).save(folder / (job['id'] + '-caderno.jpg'), quality=94)
    w, h, columns = 480, 405, 3
    canvas = Image.new('RGB', (w * columns, math.ceil(len(model['jobs']) / columns) * h + 100), '#15191a')
    draw = ImageDraw.Draw(canvas); draw.text((25, 25), 'Residência 07 / Industrial v06', font=font(30), fill='#eee5d8')
    for i, job in enumerate(model['jobs']):
        x, y = i % columns * w + 10, i // columns * h + 100
        with Image.open(folder / (job['id'] + '.jpg')) as image:
            tile = ImageOps.contain(image, (460, 345)); canvas.paste(tile, (x, y))
        draw.text((x, y + 351), job['title'][:43], font=font(16), fill='#d7b68d')
    canvas.save(folder / 'painel-geral.jpg', quality=91)


def plans():
    folder = OUT / '01-plantas'; folder.mkdir(parents=True, exist_ok=True)
    outputs = []
    for suffix in ['terreo', 'superior']:
        for ext in ['svg', 'pdf', 'png']:
            source = ROOT / 'renders/industrial-v05/01-plantas' / ('planta-industrial-' + suffix + '.' + ext)
            shutil.copy2(source, folder / source.name)
        for name in ['planta-industrial-', 'cotas-oficiais-']:
            source = ROOT / 'renders/industrial-v05/01-plantas' / (name + suffix + '.pdf')
            dest = folder / source.name
            if not dest.exists(): shutil.copy2(source, dest)
            outputs.append(dest)
    return outputs


def comparisons(model):
    jobs = {j['id']: ROOT / j['file'] for j in model['jobs']}
    old = {j['id']: ROOT / j['file'] for j in json.loads((ROOT / 'relatorios/industrial-v05/modelo.json').read_text())['jobs']}
    outputs = []
    for key in ['sala-fundos', 'cozinha', 'bar', 'escritorio-alternativa']:
        dest = OUT / '04-comparacoes' / ('v05-e-v06-' + key + '.jpg')
        board([(old[key], jobs[key], 'Industrial v05', 'Industrial v06 · acabamento e luz novos')], dest,
              'Evolução industrial / ' + key, 'Mesma câmera e arquitetura; materiais, acabamento e iluminação revistos.'); outputs.append(dest)
    refs = ROOT / CFG['references']
    pairs = [(refs / filename, jobs[key], 'Referência fornecida', label) for filename, key, label in [
        ('01-cena-final-menos-warn.png', 'sala-integrada-dia', 'Sala na planta atual'),
        ('02-bar-fundo.png', 'bar-dia', 'Bar, pedra e marcenaria'),
        ('03-mesa-jantar.png', 'mesa-jantar', 'Mesa com pés quadrados torneados'),
        ('escritorio2.png', 'escritorio-dia', 'Escritório alternativo na planta atual')]]
    dest = OUT / '05-referencias/referencias-e-proposta.jpg'
    board(pairs, dest, 'Referências e proposta industrial', 'As referências orientam o estilo; os vãos e dimensões seguem a residência 07 atual.'); outputs.append(dest)
    return outputs


def gallery(model):
    cards = []
    for job in model['jobs']:
        kind = 'dia-noite' if job.get('pilot') else ('plantas' if job['mode'].startswith(('plan', 'iso')) else 'exteriores' if job['mode'] == 'exterior' else 'ambientes')
        cards.append(f'<figure data-kind="{kind}"><a href="{escape(relative(ROOT / job["file"]))}"><img loading="lazy" width="960" height="720" src="06-galerias/{job["id"]}.jpg" alt="{escape(job["title"])}"></a><figcaption>{escape(job["title"])}</figcaption></figure>')
    sliders = []
    for key, title in [('sala-integrada', 'Sala integrada'), ('bar', 'Bar'), ('escritorio', 'Escritório')]:
        sliders.append(f'<section class="pair"><h3>{title}</h3><div class="compare"><img src="06-galerias/{key}-noite.jpg" alt="{title} à noite"><div class="day"><img src="06-galerias/{key}-dia.jpg" alt="{title} de dia"></div></div><label>Comparar noite e dia <input type="range" min="0" max="100" value="50" aria-label="Comparação dia e noite: {title}"></label></section>')
    text = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Residência 07 / Industrial v06</title><style>
*{box-sizing:border-box}body{margin:0;background:#15191a;color:#eee5d8;font:16px system-ui;line-height:1.6}header,main,footer{max-width:1500px;margin:auto;padding:30px}h1{font-size:clamp(30px,5vw,58px);line-height:1.1;max-width:900px}h2{margin-top:50px}a{color:#d7b68d}p{max-width:85ch}nav{display:flex;gap:10px;flex-wrap:wrap}button{background:#242b2d;color:#eee5d8;border:1px solid #64706e;border-radius:30px;padding:10px 18px;cursor:pointer}button[aria-pressed=true]{background:#d7b68d;color:#15191a}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}figure{margin:0;background:#202628;border-radius:8px;overflow:hidden}figure img{width:100%;height:auto;display:block}figcaption{padding:12px 15px}.pairs{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px}.compare{position:relative;aspect-ratio:4/3;overflow:hidden}.compare>img,.day img{position:absolute;width:100%;height:100%;object-fit:cover;inset:0}.day{position:absolute;inset:0;clip-path:inset(0 50% 0 0)}input{width:100%;accent-color:#d7b68d}.pair h3{margin-bottom:12px}figure[hidden]{display:none}footer{color:#a9b1ac;border-top:1px solid #46504c}</style></head><body><header><p>RESIDÊNCIA 07 · PLANTA ATUAL</p><h1>Madeira quente, couro caramelo e luz âmbar.</h1><p>Proposta industrial com acabamentos e mobiliário refinados, preservando a arquitetura atual. Abra as imagens para ver os arquivos 4K. O escritório é uma alternativa ao dormitório dos fundos.</p><nav><a href="00-cadernos/caderno-industrial-v06.pdf">Caderno PDF</a><a href="01-plantas/planta-industrial-terreo.pdf">Térreo cotado</a><a href="01-plantas/planta-industrial-superior.pdf">Superior cotado</a><a href="LEIA-ME.md">Modelo, fontes e detalhes</a></nav></header><main><h2>Dia e noite, no mesmo enquadramento</h2><div class="pairs">'''+''.join(sliders)+'''</div><h2>Ambientes e vistas</h2><nav id="filters" aria-label="Filtrar imagens">'''+''.join(f'<button data-filter="{key}" aria-pressed="{"true" if key=="todos" else "false"}">{title}</button>' for key,title in [('todos','Todas'),('ambientes','Ambientes'),('dia-noite','Dia e noite'),('plantas','Plantas'),('exteriores','Exteriores')])+'''</nav><p>Clique em uma imagem para ampliar.</p><div class="grid">'''+''.join(cards)+'''</div></main><footer>Medidas documentais da residência 07; anexos e móveis com dimensões de estudo. Entorno ilustrativo. <a href="05-referencias/referencias-e-proposta.jpg">Referências e proposta</a>.</footer><script>
document.querySelectorAll('.pair input').forEach(input=>input.addEventListener('input',()=>{input.closest('.pair').querySelector('.day').style.clipPath=`inset(0 ${100-input.value}% 0 0)`}));document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelectorAll('figure').forEach(f=>f.hidden=button.dataset.filter!=='todos'&&f.dataset.kind!==button.dataset.filter)}));
</script></body></html>'''
    (OUT / 'galeria.html').write_text(text)


def book(model, plan_files, comparison_files):
    doc = fitz.open(); page = doc.new_page(width=842, height=680)
    page.insert_textbox(fitz.Rect(40, 50, 800, 150), 'RESIDÊNCIA 07\nIndustrial v06 / Acabamento fotográfico', fontsize=26)
    cover_notes = [
        'Proposta industrial sobre a planta atual da residência 07, preservando paredes, vãos e dimensões documentais.',
        'Madeira quente, couro caramelo, cimento suave, aço preto e luz âmbar seguem as quatro referências fornecidas.',
        '31 imagens 4K, incluindo três pares de dia e noite. O escritório é uma alternativa ao dormitório dos fundos.',
        'O bar não possui geladeira; a geladeira da cozinha permanece.',
        'Anexos e móveis conservam medidas de estudo. O entorno é ilustrativo.',
        'Renderização em Blender/Cycles com GPU. A comparação no Unreal permanece pendente.',
    ]
    assert page.insert_textbox(fitz.Rect(40, 185, 800, 600), '\n\n'.join(cover_notes), fontsize=13) >= 0
    for path in plan_files:
        with fitz.open(path) as part: doc.insert_pdf(part)
    for job in model['jobs']:
        page = doc.new_page(width=842, height=680); page.insert_text((30, 32), job['title'], fontsize=15)
        page.insert_image(fitz.Rect(25, 55, 817, 640), filename=str(OUT / '06-galerias' / (job['id'] + '-caderno.jpg')), keep_proportion=True)
        page.insert_text((30, 662), 'Arquitetura atual preservada. Imagens originais em 3840 x 2880 na pasta da entrega.', fontsize=9)
    for path in comparison_files:
        page = doc.new_page(width=842, height=680); page.insert_text((30, 32), path.stem, fontsize=15)
        page.insert_image(fitz.Rect(25, 55, 817, 650), filename=str(path), keep_proportion=True)
    dest = OUT / '00-cadernos/caderno-industrial-v06.pdf'; dest.parent.mkdir(parents=True, exist_ok=True)
    doc.set_metadata({'title': 'Residência 07 — Industrial v06', 'creator': 'industrial_photoreal_delivery.py'})
    doc.save(dest, garbage=4, deflate=True); pages = len(doc); doc.close()
    return pages


def index(model):
    lines = '\n'.join(f'- [{j["title"]}]({relative(ROOT / j["file"])})' for j in model['jobs'])
    text = f'''# Residência 07 — industrial v06

31 imagens nativas em **3840 × 2880**, com materiais fotográficos, marcenaria, cadeira e acabamentos refinados; seis vistas formam três pares de dia e noite. A arquitetura atual permanece preservada.

- [Galeria e comparação dia/noite](galeria.html) · [caderno PDF](00-cadernos/caderno-industrial-v06.pdf) · [painel geral](06-galerias/painel-geral.jpg).
- [Modelo Blender editável]({relative(ROOT / model['blend'])}).
- [Térreo cotado](01-plantas/planta-industrial-terreo.pdf) · [superior cotado](01-plantas/planta-industrial-superior.pdf).
- [Evolução v05/v06](04-comparacoes) · [referências e proposta](05-referencias/referencias-e-proposta.jpg).
- [Conferência e limites]({relative(REPORT / 'RELATORIO.md')}).

## Modelagem e materiais

Cimento fino, carvalho quente, couro caramelo, aço pintado, granito, tecido e pedra oxidada seguem as quatro referências do proprietário. Novos rodapés e ferragens, rack metálico vazado, mesa com pés quadrados torneados, taças com espessura, cadeira com encosto perfurado, telas próprias e esquadria no vão oficial do escritório complementam a proposta.

As texturas e o HDRI vêm do Poly Haven, licença CC0, com hashes registrados. As interfaces das telas são desenhos vetoriais próprios. O entorno é ilustrativo; não representa levantamento dos vizinhos. A v04 e seus rascunhos foram descartados, com os componentes reutilizáveis isolados em uma biblioteca sem sua arquitetura.

A proposta industrial **não possui geladeira no bar**. A geladeira da cozinha permanece. As versões industriais anteriores disponíveis e suas imagens foram atualizadas para a mesma decisão; o modelo do estado atual continua representando a situação existente.

## Medidas e representação

Permanecem as medidas documentais da base 07 e as alterações atuais: abertura posterior, cobertura e separação lazer/lavanderia. Anexos e móveis conservam dimensões de estudo, sem levantamento presencial. A alternativa de escritório não ocupa simultaneamente o dormitório correspondente. A proposta de ático e suas escadas não foram alteradas nesta revisão industrial.

As imagens foram calculadas no **Blender/Cycles com aceleração de GPU**, até 512 amostras adaptativas, limiar 0,008 e PNG de 16 bits. O projeto contém cenas e materiais editáveis; nenhuma imagem de referência substitui a geometria. Unreal não está instalado e sua comparação/Lumen não foram executados.

## Intercâmbio

[Geometria e UVs em GLB]({relative(ROOT / 'exports/fotorrealismo-industrial-v06/LEIA-ME.md')}). O teste de unidade e de três paredes por reimportação passou. Esses GLBs usam materiais de identificação; os shaders completos estão no Blender e ainda precisam de conversão para Unreal.

## Imagens

{lines}
'''
    (OUT / 'LEIA-ME.md').write_text(text)
    project = (ROOT / model['blend']).parent
    (project / 'LEIA-ME.md').write_text(f'# Industrial v06\n\n[Galeria]({relative(OUT / "galeria.html", project)}) · [entrega]({relative(OUT / "LEIA-ME.md", project)}).\n\nAbra o Blender, escolha uma cena PHOTO6_, use Num 0 para a câmera e F12 para renderizar. As cenas com sufixo dia/noite usam a mesma câmera. O escritório é uma alternativa em cenas próprias.\n')


def verify(model, pages):
    rows = json.loads((REPORT / 'renders.json').read_text()); checks = []
    def check(name, value): checks.append({'name': name, 'passed': bool(value)})
    audit = json.loads((REPORT / 'validacao-completa.json').read_text())
    check('auditoria do arquivo e renders', audit['all_passed'] and audit['renders_required'] and audit['blend_sha256'] == model['blend_sha256'])
    check('31 imagens exatas', len(rows) == 31 and {r['id'] for r in rows} == {j['id'] for j in model['jobs']})
    for row in rows:
        path = ROOT / row['file']; check('hash ' + row['id'], data.sha(path) == row['sha256'])
        with Image.open(path) as image:
            check('PNG 4K ' + row['id'], image.size == tuple(CFG['resolution']) and image.format == 'PNG'); image.verify()
        with path.open('rb') as file: header = file.read(33)
        check('16 bits ' + row['id'], header[24] == 16)
    check('41 páginas no caderno', pages == 41)
    for path in [OUT / 'LEIA-ME.md', OUT / 'galeria.html']:
        links = re.findall(r'\]\(([^)]+)\)', path.read_text()) if path.suffix == '.md' else re.findall(r'(?:href|src)="([^"]+)"', path.read_text())
        missing = [link for link in links if not link.startswith(('https:', 'http:', '#')) and not (path.parent / link).exists()]
        check('links locais ' + path.name, not missing)
    result = {'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'checks': checks,
              'all_passed': all(c['passed'] for c in checks), 'native_checks': len(audit['checks']),
              'scope': 'Arquivos nativos, 31 imagens 4K, comparações, plantas documentais e caderno. Não valida Unreal ou aparência fotográfica por métrica automática.'}
    (REPORT / 'validacao-entrega.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if not result['all_passed']: raise RuntimeError([c for c in checks if not c['passed']])
    print('PHOTO6_DELIVERY', len(checks), 'PASSED', flush=True)
    return result


def main():
    model = json.loads((REPORT / 'modelo.json').read_text())
    prepare_images(model); p = plans(); c = comparisons(model); gallery(model); pages = book(model, p, c); index(model)
    # O relatório é escrito antes de conferir os links locais.
    (REPORT / 'RELATORIO.md').write_text('# Industrial v06 — conferência\n\nEntrega calculada em Cycles/GPU, com arquitetura atual protegida. Consulte os recibos JSON e a galeria para avaliar as imagens. O relatório detalhado de revisão visual e as limitações de intercâmbio complementam esta validação.\n')
    result = verify(model, pages)
    (REPORT / 'RELATORIO.md').write_text(f'''# Industrial v06 — residência 07

Conferência em {result['timestamp_utc']}. **{result['native_checks']} verificações nativas e {len(result['checks'])} de entrega aprovadas.**

| Escopo | Evidência | Situação |
| --- | --- | --- |
| Descarte da v04 | `descarte-v04.json`, inventário e biblioteca extraída | Verificado |
| Arquitetura atual | 795 impressões geométricas e comparação independente ao reabrir a v05 | Preservada |
| Materiais e recursos | 19 recursos 4K CC0 íntegros, telas próprias, recursos empacotados | Verificado |
| Imagens | 31 saídas Cycles/GPU em 3840 × 2880, PNG de 16 bits, hashes do modelo e dos arquivos | Verificado |
| Entrega | Plantas, pares dia/noite, comparações, galeria e caderno de 41 páginas | Verificado estaticamente |
| Unreal/Lumen | Usuário informou não possuir instalação; nenhum teste no Unreal executado | Pendente |

O render é físico e usa recursos 3D editáveis. A qualidade visual deve ser avaliada nas imagens; uma contagem de amostras ou verificações não prova fotorrealismo. O entorno é ilustrativo e as dimensões aproximadas da reforma e dos móveis permanecem identificadas como estudo. Esta revisão não altera a base original, a casa atual ou o ático v05.

Recibos: `modelo.json`, `renders.json`, `gpu-render.json`, `validacao-completa.json`, `validacao-entrega.json`. O consumo em `gpu-render.json` é amostrado para a GPU inteira e inclui outros processos; não equivale ao pico exato do Blender. Os tempos são desta máquina e configuração, sem comparação com Unreal.

[Galeria](../../renders/industrial-v06/galeria.html) · [índice](../../renders/industrial-v06/LEIA-ME.md).
''')


if __name__ == '__main__': main()
