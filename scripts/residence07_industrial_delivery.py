"""Entrega organizada, comparações e caderno da proposta industrial v05."""
import datetime as dt
from html import escape
import json
import math
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import fitz
from PIL import Image,ImageDraw,ImageFont,ImageOps

import residence07_geometry as geo
import residence07_industrial_data as data

ROOT=data.ROOT;CFG=data.CFG;OUT=ROOT/CFG['render_directory'];REPORT=ROOT/CFG['report_directory']
FONT=str(ROOT/'assets/fonts/DejaVuSans.ttf')


def font(size):return ImageFont.truetype(FONT,size)


def rel(path,parent):return Path(os.path.relpath(path,parent)).as_posix()


def vectors():
    outputs=[]
    for suffix in ['terreo','superior']:
        source=ROOT/'renders/atual/01-plantas'/('planta-atual-'+suffix+'.svg')
        text=source.read_text().replace('Estado atual ·','Industrial ·').replace('Base documental 07 + alterações informadas e referências fotográficas','Proposta de interiores · arquitetura atual preservada na base documental 07')
        text=text.replace('Fundos e móveis: fotos em referencias-originais + instruções do proprietário.','Arquitetura atual preservada. Acabamentos e móveis: proposta industrial separada.')
        target=OUT/'01-plantas'/('planta-industrial-'+suffix+'.svg');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
        # A planta vetorial compartilha exatamente os traços da arquitetura atual.
        a,b=ET.fromstring(source.read_text()),ET.fromstring(text)
        def lines(root):return [(e.tag,dict(e.attrib)) for e in root if e.tag.endswith(('polygon','polyline'))]
        assert lines(a)==lines(b)
        with fitz.open(target) as doc:pdf=doc.convert_to_pdf()
        with fitz.open('pdf',pdf) as doc:doc.save(target.with_suffix('.pdf'));doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(target.with_suffix('.png'))
        outputs.append(target.with_suffix('.pdf'))
        original=ROOT/'renders/original/01-plantas-arquitetonicas'/('cotas-originais-'+suffix+'.pdf')
        dest=OUT/'01-plantas'/('cotas-oficiais-'+suffix+'.pdf');shutil.copy2(original,dest);outputs.append(dest)
    return outputs


def board(pairs,target,title,note):
    width,height=1800,760*len(pairs)+150;im=Image.new('RGB',(width,height),'#f3f0e8');draw=ImageDraw.Draw(im)
    draw.text((30,22),title,font=font(36),fill='#26382d');draw.text((30,80),note,font=font(19),fill='#647061')
    for row,(left,right,left_label,right_label) in enumerate(pairs):
        for col,(path,label) in enumerate([(left,left_label),(right,right_label)]):
            with Image.open(path) as pic:
                tile=ImageOps.contain(pic.convert('RGB'),(850,650));x=30+890*col;y=150+row*760;im.paste(tile,(x+(850-tile.width)//2,y+(650-tile.height)//2))
            draw.text((x,y+670),label,font=font(22),fill='#26382d')
    target.parent.mkdir(parents=True,exist_ok=True);im.save(target,quality=93)


def gallery(model):
    cols=3;w,h=640,525;canvas=Image.new('RGB',(w*cols,math.ceil(len(model['jobs'])/cols)*h+150),'#f3f0e8');draw=ImageDraw.Draw(canvas)
    draw.text((30,24),'Residência 07 / Industrial na planta atual',font=font(36),fill='#26382d');draw.text((30,85),'Medidas documentais da base 07 · fundos alterados preservados · modelo nativo',font=font(22),fill='#647061')
    cards=[]
    for i,j in enumerate(model['jobs']):
        path=ROOT/j['file'];x=(i%3)*w+15;y=(i//3)*h+150
        with Image.open(path) as pic:tile=ImageOps.contain(pic.convert('RGB'),(610,455));canvas.paste(tile,(x+(610-tile.width)//2,y))
        draw.text((x+5,y+465),j['title'][:55],font=font(17),fill='#26382d')
        src=rel(path,OUT);cards.append(f'<figure><a href="{escape(src)}"><img loading="lazy" src="{escape(src)}" alt="{escape(j["title"])}"></a><figcaption>{escape(j["title"])}</figcaption></figure>')
    dest=OUT/'06-galerias/painel-geral.jpg';dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest,quality=93)
    page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Industrial / Residência 07 atual</title><style>body{font:17px system-ui;background:#f3f0e8;color:#26382d;padding:3vw;margin:0}p{max-width:85ch;line-height:1.6}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}figure{margin:0;border:1px solid #cccfc3;background:white;border-radius:10px;overflow:hidden}img{width:100%;display:block}figcaption{padding:14px}</style><h1>Industrial / Residência 07 na planta atual</h1><p>Proposta de interiores sobre a arquitetura atual preservada. As dimensões dos anexos continuam aproximadas. O escritório é uma alternativa ao dormitório dos fundos.</p><p><a href="LEIA-ME.md">Índice, fontes e medidas</a> · <a href="00-cadernos/caderno-industrial-v05.pdf">Caderno PDF</a></p><main>'''+''.join(cards)+'</main></html>'
    (OUT/'galeria.html').write_text(page)


def comparisons(model):
    byid={j['id']:ROOT/j['file'] for j in model['jobs']};current=json.loads((ROOT/'relatorios/original/estudo-instalacoes-atico/atual-modelo.json').read_text());before={j['id']:ROOT/j['file'] for j in current['jobs']}
    outputs=[]
    for id in ['sala-fundos','cozinha','bar','planta-terreo']:
        path=OUT/'04-comparacoes'/('atual-e-industrial-'+id+'.jpg');board([(before[id],byid[id],'Modelo do estado atual','Proposta industrial · mesma arquitetura e câmera')],path,'Atual e industrial / '+id,'Comparação na mesma câmera; a proposta altera móveis, acabamentos e luz.');outputs.append(path)
    refs=ROOT/CFG['references'];pairs=[(refs/'01-cena-final-menos-warn.png',byid['sala-fundos'],'Referência de estilo · sala','Proposta ajustada à residência 07'),
        (refs/'02-bar-fundo.png',byid['bar'],'Referência de estilo · bar','Bar na área posterior existente'),
        (refs/'03-mesa-jantar.png',byid['mesa-jantar'],'Referência de estilo · mesa','Mesa modelada para a circulação disponível'),
        (refs/'escritorio2.png',byid['escritorio-alternativa'],'Referência de estilo · escritório','Alternativa para o quarto dos fundos')]
    target=OUT/'05-referencias/referencias-e-proposta.jpg';board(pairs,target,'Referências e proposta industrial','As imagens de referência orientam o estilo; seus enquadramentos e dimensões não controlam a planta.');outputs.append(target)
    return outputs


def book(model,plans,comparisons_):
    doc=fitz.open();p=doc.new_page(width=842,height=680)
    p.insert_textbox(fitz.Rect(40,55,800,145),'RESIDÊNCIA 07\nIndustrial sobre a planta atual',fontsize=28,color=(.15,.22,.17))
    p.insert_textbox(fitz.Rect(40,180,800,600),'\n\n'.join(CFG['notes']),fontsize=14,lineheight=1.4)
    for path in plans:
        with fitz.open(path) as part:doc.insert_pdf(part)
    for path,title in [(ROOT/j['file'],j['title']) for j in model['jobs']]+[(p,p.stem) for p in comparisons_]:
        page=doc.new_page(width=842,height=680);page.insert_text((30,32),title,fontsize=16,color=(.15,.22,.17));page.insert_image(fitz.Rect(25,52,817,628),filename=str(path),keep_proportion=True)
        page.insert_textbox(fitz.Rect(30,642,812,673),'Base oficial ARQ03/04 + alterações atuais. Anexos e móveis: dimensões de estudo, sem levantamento presencial.',fontsize=9)
    target=OUT/'00-cadernos/caderno-industrial-v05.pdf';target.parent.mkdir(parents=True,exist_ok=True)
    doc.set_metadata({'title':'Residência 07 — industrial sobre a planta atual','creator':'residence07_industrial_delivery.py'});doc.save(target);doc.close();return target


def index(model):
    rows='\n'.join(f"- [{j['title']}]({rel(ROOT/j['file'],OUT)})" for j in model['jobs'])
    text=f'''# Residência 07 — industrial na planta atual / v05

Esta versão foi refeita a partir de `referencias-estilo-industrial` e do modelo atual da unidade 07. A arquitetura estimada das versões industriais antigas não foi reutilizada.

O bar industrial não possui geladeira, conforme a decisão posterior do proprietário. A geladeira da cozinha permanece. As imagens e os documentos desta entrega foram atualizados para essa condição.

- [Caderno PDF](00-cadernos/caderno-industrial-v05.pdf), [galeria](galeria.html) e [painel geral](06-galerias/painel-geral.jpg).
- [Modelo Blender editável]({rel(ROOT/model['blend'],OUT)}).
- [Térreo cotado](01-plantas/planta-industrial-terreo.pdf), [superior cotado](01-plantas/planta-industrial-superior.pdf) e cotas originais em `01-plantas`.
- [Atual × industrial](04-comparacoes) e [referências × proposta](05-referencias/referencias-e-proposta.jpg).

## O que controla a proposta

As medidas documentais vêm da base da residência 07: largura de 6,35 m até o eixo da geminação, piso superior em +2,70 m, pé-direito de 2,55 m e lajes de 0,15 m. Permanecem as divergências internas dos PDFs registradas no relatório principal. A abertura da sala para os fundos, a cobertura posterior e a divisão lazer/lavanderia foram preservadas do modelo atual.

Os anexos posteriores e os móveis continuam com medidas aproximadas, sem levantamento no local. As cotas aproximadas são identificadas por ≈ nas plantas. A proposta não transforma as medidas estimadas dos anexos em medidas oficiais.

## Estilo e alternativas

Cimento suave, madeira quente, couro caramelo, metal preto, pedra oxidada e luz âmbar seguem as quatro referências fornecidas. O sofá e as quatro cadeiras reaproveitam componentes da biblioteca independente; a mesa de madeira e quatro banquetas foram modeladas para este espaço. As medidas e a circulação disponíveis condicionam o mobiliário.

As cenas `escritorio-alternativa` e `escritorio-reverso` propõem três telas, mesa, estante e acabamento azul-petróleo no quarto dos fundos. São uma alternativa de mobiliário; as demais cenas mantêm a opção de dormitório. A arquitetura é a mesma nas duas opções.

## Organização

| Pasta | Conteúdo |
| --- | --- |
| `00-cadernos` | Caderno completo |
| `01-plantas` | Plantas cotadas, cotas originais e quatro plantas/perspectivas humanizadas |
| `02-ambientes` | Ambientes e detalhes; escritório em cenas alternativas |
| `03-exteriores` | Fachada e volumetria na arquitetura atual |
| `04-comparacoes` | Estado atual e proposta na mesma câmera |
| `05-referencias` | Painel com as quatro referências e as soluções propostas |
| `06-galerias` | Painel de todas as imagens |

## Imagens

{rows}

[Relatório e limites]({rel(REPORT/'RELATORIO.md',OUT)}) · [conferência do arquivo nativo]({rel(REPORT/'validacao-completa.json',OUT)}).

A revisão v04 foi descartada a pedido do proprietário; os componentes reutilizáveis e a casa atual foram preservados. Não há alteração ou certificação das instalações por esta proposta de interiores.
'''
    (OUT/'LEIA-ME.md').write_text(text)
    project=(ROOT/model['blend']).parent;project.joinpath('LEIA-ME.md').write_text(f"# Industrial v05 / residência 07 atual\n\n[Entrega organizada]({rel(OUT/'LEIA-ME.md',project)}).\n\nEscolha uma cena IND07_ no Blender, Num 0 para a câmera e F12 para renderizar. O escritório é uma alternativa em duas cenas próprias. A arquitetura atual foi preservada.\n")


def verify(model):
    checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    audit=json.loads((REPORT/'validacao-completa.json').read_text());records=json.loads((REPORT/'renders.json').read_text())
    check('modelo reaberto e imagens conferidos',audit['all_passed'] and audit['renders_required'] and audit['blend_sha256']==geo.sha(ROOT/model['blend']))
    check('conjunto exato de 25 imagens',len(records)==25 and {r['id'] for r in records}=={j['id'] for j in model['jobs']})
    for r in records:
        path=ROOT/r['file'];check('hash '+r['id'],geo.sha(path)==r['sha256'])
        with Image.open(path) as im:check('PNG '+r['id'],im.size==tuple(CFG['resolution']) and im.format=='PNG');im.verify()
    with fitz.open(OUT/'00-cadernos/caderno-industrial-v05.pdf') as doc:check('35 páginas do caderno',len(doc)==35)
    for path in [OUT/'LEIA-ME.md',OUT/'galeria.html']:
        text=path.read_text();links=re.findall(r'\]\(([^)]+)\)',text) if path.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',text)
        check('links '+path.name,all((path.parent/unquote(link.split('#')[0])).exists() for link in links if not link.startswith(('http:','https:','#'))))
    check('fontes oficiais preservadas',all(geo.sha(ROOT/r['file'])==r['sha256'] for r in model['official_sources']))
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'checks':checks,'all_passed':all(c['passed'] for c in checks),'native_checks':len(audit['checks']),'scope':'Arquitetura atual preservada, proposta de interiores, imagens e documentos locais. Galeria HTML validada estaticamente.'}
    (REPORT/'validacao-entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('IND07_DELIVERY',len(checks),'PASSED' if result['all_passed'] else 'FAILED')
    if not result['all_passed']:raise RuntimeError([c for c in checks if not c['passed']])
    return result


def report(model,result):
    text=f'''# Industrial v05 — residência 07 na planta atual

Conferência: {result['timestamp_utc']}. {result['native_checks']} verificações nativas e {len(result['checks'])} verificações de entrega passaram. O escopo é documental e visual, sem levantamento presencial ou projeto executivo.

Foram comparadas duas opções: adaptar a arquitetura estimada da v04 ou usar diretamente a casa atual. Foi adotada a segunda, preservando paredes, vãos, lajes, escada, cobertura e divisão dos fundos. A v04 fornece apenas componentes de móveis e materiais. É uma solução pragmática com um contrato explícito de geometria, em vez de recalibrar uma planta estimada.

| Obrigação | Evidência | Estado |
| --- | --- | --- |
| Base oficial da unidade 07 | `config/residencia-07.json`, ARQ03/04 e seus hashes | VERIFICADO para a geometria documental |
| Considerar a planta atual alterada | Hash de `casa-07-atual.blend`, 795 elementos arquitetônicos e comparação independente com a fonte | VERIFICADO |
| Preservar a casa atual e a v04 | Hashes dos arquivos antes e depois | VERIFICADO |
| Seguir as quatro referências de estilo | Referências com hashes, prévias e painel `referencias-e-proposta.jpg` | INTERPRETAÇÃO VISUAL |
| Gerar todas as vistas | 25 cenas e PNGs com hash do modelo nativo | VERIFICADO |
| Plantas coerentes | Polígonos e linhas dos SVG iguais à arquitetura atual; quatro vistas nativas humanizadas/3D | VERIFICADO |
| Escritório como alternativa | Duas cenas exclusivas, sem a coleção do beliche | VERIFICADO |
| Medidas executadas dos anexos | Fotos e instruções; sem medição no local | APROXIMADAS |

O acabamento usa cimento suave, couro caramelo, madeira quente, aço preto, pedra oxidada e luz âmbar. A mesa e as banquetas são modelos novos; sofá e cadeiras são componentes nativos reaproveitados da biblioteca v04, sem a sua arquitetura. As imagens PBR usadas estão empacotadas no Blender.

As medidas documentais incluem largura 6,35 m até o eixo da geminação, superior em +2,70 m, pé-direito 2,55 m e laje 0,15 m. As divergências internas dos PDFs permanecem no relatório da base. A abertura dos fundos e seus anexos vêm do modelo atual; não são apresentados como partes confirmadas do desenho aprovado de 2011.

São 25 renders em 1920 × 1440, Cycles/CUDA, 128 amostras; duas plantas vetoriais em SVG/PDF/PNG, duas folhas de cotas originais, quatro comparações atual/industrial, um painel de referências e caderno de 35 páginas. A galeria HTML teve seus links conferidos estaticamente; não foi exercitada em navegador.

As cenas de escritório propõem outro uso de mobiliário no quarto dos fundos. As outras cenas e a planta superior usam a opção com dormitório; não se somam as duas opções no mesmo ambiente. A proposta não altera ou certifica instalações elétricas/hidráulicas existentes.

Referência técnica consultada: [atribuição e reutilização de materiais no Blender](https://docs.blender.org/manual/en/latest/render/materials/assignment.html). Os geradores e recibos mantêm a separação entre geometria, materiais, fontes e renderizações.
'''
    (REPORT/'RELATORIO.md').write_text(text)
    checkpoint=json.loads((REPORT/'checkpoint.json').read_text());checkpoint.update(status='COMPLETE_VISUAL_AND_DOCUMENTARY',verification=str((REPORT/'validacao-entrega.json').relative_to(ROOT)),results={'views':25,'native_checks':result['native_checks'],'delivery_checks':len(result['checks'])})
    (REPORT/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n')


def main():
    model=json.loads((REPORT/'modelo.json').read_text());records=json.loads((REPORT/'renders.json').read_text())
    assert {r['id'] for r in records}=={j['id'] for j in model['jobs']}
    assert all(r['blend_sha256']==model['blend_sha256'] and geo.sha(ROOT/r['file'])==r['sha256'] for r in records)
    OUT.mkdir(parents=True,exist_ok=True);plans=vectors();gallery(model);pairs=comparisons(model);book(model,plans,pairs)
    (REPORT/'RELATORIO.md').write_text('# Industrial v05\n\nConferência final da entrega em andamento. Consultar validacao-completa.json para o escopo nativo já conferido.\n')
    index(model)
    result=verify(model);report(model,result)
    manifest=[{'file':str(p.relative_to(ROOT)),'sha256':geo.sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()]
    (REPORT/'manifesto.json').write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'artifacts':manifest},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
