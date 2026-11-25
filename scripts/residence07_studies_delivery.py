"""Cadernos, plantas atuais, comparações e índices das versões independentes."""
import datetime as dt
from html import escape
import json
import math
import os
from pathlib import Path

import fitz
from PIL import Image,ImageDraw,ImageFont,ImageOps

import residence07_geometry as geo
import residence07_studies_data as data
from residence07_plans import Sheet

ROOT=geo.ROOT;REPORT=ROOT/data.CFG['report_directory'];FONT=str(ROOT/'assets/fonts/DejaVuSans.ttf')
TITLES={'atual':'Residência 07 · estado atual pelas fotos','atico':'Residência 07 · proposta de ático','instalacoes':'Residência 07 · instalações em 3D'}
NOTES={
    'atual':'Base ARQ03/04, abertura informada e móveis das fotos. Anexos e móveis têm medidas aproximadas; não houve levantamento presencial.',
    'atico':'Proposta independente: acesso pelo quarto frontal, caixa de 1.000 L mantida. Novo vão, laje, cargas e escada dependem de projeto específico.',
    'instalacoes':'Percursos 3D de estudo, com alturas documentadas quando disponíveis. Não constituem levantamento de tubulações e fiação existentes.'}


def rel(path,parent):return Path(os.path.relpath(path,parent)).as_posix()


def font(size):return ImageFont.truetype(FONT,size)


def write_svg(sheet,dest):
    sheet.items.append('</svg>');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('\n'.join(sheet.items))
    with fitz.open(dest) as svg:pdf=svg.convert_to_pdf()
    with fitz.open('pdf',pdf) as doc:
        doc.save(dest.with_suffix('.pdf'));doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(dest.with_suffix('.png'))


def current_plan(level):
    cfg=geo.load();s=Sheet('Estado atual · '+('térreo' if level==0 else 'superior'),'Base documental 07 + alterações informadas e referências fotográficas')
    s.scale=90;s.ox=360;s.oy=1275
    s.poly([s.xy(p) for p in cfg['levels'][level]['outline']],'#e7e4d9')
    if level==0:
        for x0,x1,y0,y1 in [[0,3.3,5.7,10.4],[3.3,6.35,7.2,10.4]]:
            s.poly([s.xy(p) for p in [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]],'#e2ece5')
    for poly in geo.stair_polygons(cfg):s.poly([s.xy(p) for p in poly],'#d1c5ad','#6b766e',1)
    for wall in cfg['walls']:
        if wall['level']!=level or (level==0 and wall['id']=='T-fundos-sala'):continue
        for a,b,z0,z1 in geo.wall_cells(wall,cfg['dimensions']['clear_height']):
            if z0<=1.2<=z1:s.poly([s.xy(p) for p in geo.wall_polygon(wall,a,b)],'#34443b')
        for op in wall.get('openings',[]):
            a=geo.point(wall,op['start']);b=geo.point(wall,op['start']+op['width'])
            if op['kind'] in ['window','sliding']:s.line([s.xy(a),s.xy(b)],'#4a8c96',3)
            else:s.line([s.xy(a),s.xy(geo.point(wall,op['start'],op['width']))],'#a16e43',2)
    for room in cfg['rooms']:
        if room['level']!=level:continue
        x,y=s.xy(room['label_at']);s.text(x,y,room['label'],13,anchor='middle',weight='bold')
    if level==0:
        # Novos fechamentos do modelo atual, sem apresentar as medidas como aferidas.
        for poly in [
            [[0,5.7],[.15,5.7],[.15,10.4],[0,10.4]],[[6.25,7.2],[6.35,7.2],[6.35,10.4],[6.25,10.4]],
            [[0,10.25],[3.825,10.25],[3.825,10.4],[0,10.4]],[[5.95,10.25],[6.35,10.25],[6.35,10.4],[5.95,10.4]],
            [[3.3,7.2],[3.45,7.2],[3.45,7.65],[3.3,7.65]],[[3.3,8.45],[3.45,8.45],[3.45,10.4],[3.3,10.4]]]:s.poly([s.xy(p) for p in poly],'#a17846')
        s.line([s.xy([3.375,7.65]),s.xy([3.375,8.45])],'#4a8c96',3)
        s.line([s.xy([3.825,10.25]),s.xy([5.95,10.25])],'#4a8c96',3)
        s.line([s.xy([.15,5.7]),s.xy([3.3,5.7])],'#a6603f',2,'5 5')
        for x in [.7,1.7,2.7]:s.line([s.xy([x,6.5]),s.xy([x,10.25])],'#9db2a1',1,'6 5')
        for x in [3.8,4.8,5.8]:s.line([s.xy([x,7.2]),s.xy([x,10.25])],'#9db2a1',1,'6 5')
        for pos,label in [([1.65,8.2],'LAZER / BAR'),([4.8,8.8],'LAVANDERIA'),([1.65,6.05],'FUNDO ABERTO')]:
            x,y=s.xy(pos);s.text(x,y,label,14,'#82613d',anchor='middle',weight='bold')
        s.dimension([0,0],[0,10.4],'≈ 10,40 · limite modelado',-110)
        s.dimension([.15,5.7],[3.3,5.7],'3,15 · abertura modelada',35)
        s.dimension([3.375,7.65],[3.375,8.45],'≈ 0,80',40)
        s.text(75,1375,'Verde: área posterior coberta · ocre: novos fechamentos · tracejado: cobertura/abertura.',17)
    else:
        s.dimension([6.35,-1.2],[6.35,7.2],'8,40 · geometria da base',75)
        s.text(75,1375,'Distribuição dos quartos e banheiros preservada na base documental 07.',18)
    s.dimension([0,-1.2 if level else 0],[6.35,-1.2 if level else 0],'6,35 · até eixo da geminação',60)
    s.line([(75,1450),(1325,1450)],'#b7beb1')
    for y,text in [(1492,'COTAS EM METROS · base original ARQ03/04; medidas executadas não aferidas.'),
                   (1530,'≈ identifica dimensão aproximada do modelo, dependente de medição no local.'),
                   (1568,'Fundos e móveis: fotos em referencias-originais + instruções do proprietário.'),
                   (1606,'Planta para visualização. Redes 3D originais não são levantamento após a reforma.')]:s.text(75,y,text,17,'#59695c')
    dest=ROOT/data.CFG['current_renders']/'01-plantas'/('planta-atual-'+('terreo' if level==0 else 'superior')+'.svg')
    write_svg(s,dest);return dest.with_suffix('.pdf')


def gallery(model,out):
    jobs=model['jobs'];width,height=640,530;canvas=Image.new('RGB',(width*3,height*math.ceil(len(jobs)/3)+150),'#f4f1e9');draw=ImageDraw.Draw(canvas)
    draw.text((30,25),TITLES[model['kind']],font=font(35),fill='#263c30')
    draw.text((30,85),'Modelo Blender editável · imagens finais · consulte os limites no LEIA-ME',font=font(22),fill='#59695c')
    cards=[]
    for i,j in enumerate(jobs):
        path=ROOT/j['file'];assert path.exists(),path
        with Image.open(path) as im:
            im=im.convert('RGB');im.thumbnail((610,455));x=(i%3)*width+15;y=(i//3)*height+150;canvas.paste(im,(x+(610-im.width)//2,y))
        title=j['title'].split(' · ',1)[-1]
        draw.text((x+6,y+466),title[:53],font=font(18),fill='#263c30')
        src=rel(path,out);category=Path(j['file']).parent.name
        cards.append(f'<a class="card" data-category="{escape(category)}" href="{escape(src)}"><img loading="lazy" src="{escape(src)}" alt="{escape(title)}"><span>{escape(title)}</span></a>')
    dest=out/'06-galerias'/'painel-geral.jpg';dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest,quality=93)
    categories=sorted({Path(j['file']).parent.name for j in jobs})
    options=''.join(f'<option>{escape(c)}</option>' for c in categories)
    page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+escape(TITLES[model['kind']])+'''</title>
<style>body{font:17px system-ui;background:#f5f2e9;color:#263c30;margin:0;padding:3vw}h1{font-size:2rem}p{max-width:85ch;line-height:1.6}select{font:inherit;padding:.6rem;margin:1rem 0}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:20px}.card{color:inherit;text-decoration:none;background:white;border:1px solid #d4dbcd;border-radius:12px;overflow:hidden}.card img{width:100%;display:block}.card span{display:block;padding:14px}.card[hidden]{display:none}</style>
<h1>'''+escape(TITLES[model['kind']])+'''</h1><p>'''+escape(NOTES[model['kind']])+'''</p><p><a href="LEIA-ME.md">Índice e fontes</a> · <a href="06-galerias/painel-geral.jpg">Painel completo</a></p><label>Filtrar: <select id="filter"><option value="">Todas as vistas</option>'''+options+'''</select></label><main>'''+''.join(cards)+'''</main><script>document.querySelector('#filter').addEventListener('change',e=>document.querySelectorAll('.card').forEach(c=>c.hidden=!!e.target.value&&c.dataset.category!==e.target.value))</script></html>'''
    (out/'galeria.html').write_text(page)


def comparisons(out):
    rows=[('sala','sala1.webp','sala-fundos'),('cozinha','cozinha1.webp','cozinha'),('lazer','area1.webp','bar'),
          ('lavanderia','lavanderia1.webp','lavanderia'),('suite','quartosuite1.webp','suite'),('quarto-fundos','quartoazul1.webp','quarto-fundos')]
    dest=out/'04-comparacoes';dest.mkdir(parents=True,exist_ok=True);receipts=[]
    for name,photo,render in rows:
        source=ROOT/'referencias-originais'/photo;image=out/'02-ambientes'/(render+'.png')
        canvas=Image.new('RGB',(1800,930),'#f4f1e9');draw=ImageDraw.Draw(canvas)
        draw.text((35,25),name.upper()+' / foto e reconstrução',font=font(38),fill='#263c30')
        for i,path in enumerate([source,image]):
            with Image.open(path) as im:
                tile=ImageOps.contain(im.convert('RGB'),(850,690));canvas.paste(tile,(35+i*890+(850-tile.width)//2,115+(690-tile.height)//2))
            draw.text((35+i*890,825),'Foto fornecida' if i==0 else 'Modelo na base 07 · enquadramento aproximado',font=font(24),fill='#263c30')
        draw.text((35,885),'Comparação visual; perspectivas e medidas dos móveis não foram calibradas por levantamento.',font=font(22),fill='#59695c')
        target=dest/('foto-modelo-'+name+'.jpg');canvas.save(target,quality=93)
        receipts.append({'photo':str(source.relative_to(ROOT)),'photo_sha256':geo.sha(source),'render':str(image.relative_to(ROOT)),'file':str(target.relative_to(ROOT))})
    (REPORT/'atual-comparacoes.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n')
    return [ROOT/r['file'] for r in receipts]


def book(model,out,extras=()):
    doc=fitz.open();page=doc.new_page(width=842,height=650)
    page.insert_textbox(fitz.Rect(40,55,800,125),TITLES[model['kind']],fontsize=27,color=(.15,.24,.18))
    page.insert_textbox(fitz.Rect(40,155,800,245),NOTES[model['kind']],fontsize=16,lineheight=1.5)
    notes=data.CFG['source_notes'] if model['kind']=='instalacoes' else data.CFG['current']['notes']
    page.insert_textbox(fitz.Rect(40,280,800,605),'\n\n'.join(notes),fontsize=12,lineheight=1.35)
    for path in extras:
        if path.suffix=='.pdf':
            with fitz.open(path) as extra:doc.insert_pdf(extra)
    items=[(ROOT/j['file'],j['title']) for j in model['jobs']]+[(p,p.stem) for p in extras if p.suffix!='.pdf']
    for path,title in items:
        p=doc.new_page(width=842,height=680)
        p.insert_text((30,32),title,fontsize=16,color=(.15,.24,.18))
        p.insert_image(fitz.Rect(25,55,817,625),filename=str(path),keep_proportion=True)
        p.insert_textbox(fitz.Rect(30,640,812,674),NOTES[model['kind']],fontsize=8.5)
    target=out/'00-cadernos'/('caderno-'+model['kind']+'.pdf');target.parent.mkdir(parents=True,exist_ok=True)
    doc.set_metadata({'title':TITLES[model['kind']],'creator':'residence07_studies_delivery.py'});doc.save(target);doc.close()
    return target


def index(model,out):
    kind=model['kind'];lines=[f'# {TITLES[kind]}','',NOTES[kind],'',
        f"- [Caderno PDF](00-cadernos/caderno-{kind}.pdf) · [galeria navegável](galeria.html) · [painel geral](06-galerias/painel-geral.jpg)",
        f"- [Modelo Blender editável]({rel(ROOT/model['blend'],out)})",'']
    if kind=='instalacoes':
        lines+=['Paredes em sálvia suave nas quatro vistas estruturais; nas redes, paredes com 12% e lajes com 5,5% de opacidade. As redes são objetos 3D editáveis, separados por disciplina e por pavimento.','','| Cor | Rede |','| --- | --- |','| Laranja | Elétrica |','| Azul | Água fria |','| Vermelho | Água quente |','| Marrom | Esgoto |','| Verde | Ventilação |','| Ciano | TV / telefone |','',
            'As espessuras gráficas mínimas de 35 mm facilitam a leitura; os diâmetros nominais estão registrados nos objetos. As alturas de ELE04 e HID05 são transcritas quando disponíveis. As derivações e trajetos embutidos em 3D são estudo. A ligação da lavanderia posterior é inferida das fotos, sem atualização executiva comprovada; sua altura de 1,00 m é de estudo. A referência genérica a HID05 nos dados não confirma essa altura. A caixa de 1.000 L vem de HID04; a forma externa é ilustrativa.','','A transparência usa o [Transparent BSDF do Blender](https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/transparent.html), misturado ao material da parede. Não há refração para distorcer o traçado.','']
    else:
        lines+=['Esta revisão substitui as 34 imagens antigas da raiz. O conteúdo anterior permanece em [histórico](../../arquivos/historico/atual-pre-residencia07/renders), com [manifesto de hashes](../../relatorios/original/estudo-instalacoes-atico/atual-arquivos-anteriores.json).','',
            '| Pasta | Conteúdo |','| --- | --- |','| `00-cadernos` | Caderno com plantas, 3D e fotos comparativas |','| `01-plantas` | Duas plantas vetoriais cotadas e quatro vistas humanizadas/3D |','| `02-ambientes` | Sala, cozinha, bar, lavanderia, fundos, escada, lavabo e quartos |','| `03-exteriores` | Fachada e volumetria com cobertura dos fundos |','| `04-comparacoes` | Seis pares de foto e modelo |','| `06-galerias` | Painel geral |','',
            'O fundo da sala foi aberto, a área posterior recebeu cobertura de vidro com vigas de madeira e lazer/lavanderia ficaram separados por parede e porta de vidro. Os móveis cinza, mesa escura de vidro, bar e dormitórios foram reaproveitados/adaptados das referências. A suíte tem cama voltada à TV e roupeiro ao fundo.','',
            'As fotos não determinam todas as medidas. As cotas da arquitetura original continuam documentais; a profundidade dos anexos, fechamentos novos e móveis é aproximada. As plantas vetoriais marcam essas cotas com ≈. Não foram transportadas redes antigas para esta versão como se fossem instalações atuais.','',
            '- [Planta vetorial do térreo](01-plantas/planta-atual-terreo.pdf) · [superior](01-plantas/planta-atual-superior.pdf)','- [Comparações com as fotos](04-comparacoes)','']
    lines+=['## Imagens','']
    for j in model['jobs']:lines.append(f"- [{j['title']}]({rel(ROOT/j['file'],out)})")
    lines+=['',f"Gerado de `{model['blend']}` · SHA-256 `{model['blend_sha256']}`.",'',
            f"[Recibo do modelo]({rel(REPORT/(kind+'-modelo.json'),out)}) · [conferência]({rel(REPORT/(kind+'-validacao.json'),out)})",'']
    (out/'LEIA-ME.md').write_text('\n'.join(lines))


def main():
    folders={'atual':data.CFG['current_renders'],'instalacoes':data.CFG['services_renders']}
    delivery=[]
    for kind,folder in folders.items():
        model=json.loads((REPORT/(kind+'-modelo.json')).read_text());records=json.loads((REPORT/(kind+'-renders.json')).read_text())
        assert {r['id'] for r in records}=={j['id'] for j in model['jobs']},kind
        assert all(r['blend_sha256']==model['blend_sha256'] and geo.sha(ROOT/r['file'])==r['sha256'] for r in records),kind
        out=ROOT/folder;out.mkdir(parents=True,exist_ok=True);extras=[]
        if kind=='atual':extras=[current_plan(0),current_plan(1),*comparisons(out)]
        gallery(model,out);book(model,out,extras);index(model,out)
        delivery += [{'file':str(p.relative_to(ROOT)),'sha256':geo.sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
        project=(ROOT/model['blend']).parent
        if kind!='instalacoes':
            (project/'LEIA-ME.md').write_text(f"# {TITLES[kind]}\n\n{NOTES[kind]}\n\n[Abrir a entrega organizada]({rel(out/'LEIA-ME.md',project)}).\n\nEscolha uma cena no Blender; Num 0 mostra a câmera e F12 renderiza. Modelo em metros.\n")
    latest=json.loads((ROOT/'arquivos/versoes-anteriores-2026-11-14/relatorios/residencia-07-atico-v05/manifesto.json').read_text())
    delivery+=latest['artifacts']
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'artifacts':delivery}
    (REPORT/'entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('STUDIES_DELIVERY',len(delivery),'artefatos')


if __name__=='__main__':main()
