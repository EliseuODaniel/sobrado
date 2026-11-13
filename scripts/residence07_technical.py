"""Pranchas sem mobiliário e instalações vetoriais registradas da unidade 07.

Conserva os símbolos e textos originais, evitando inventar circuitos, bitolas ou
rotas. O caderno inclui as pranchas-fonte completas com seus detalhes e legendas.
"""
import copy
import datetime as dt
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import fitz

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
from residence07_plans import Sheet

ROOT=geo.ROOT;CFG=geo.load();SPEC=json.loads((ROOT/'config/residencia-07-instalacoes.json').read_text())
OUT=ROOT/CFG['delivery']['renders'];REPORT=ROOT/CFG['delivery']['reports'];SOURCES=ROOT/SPEC['source_directory']
NS='{http://www.w3.org/2000/svg}'
ET.register_namespace('',NS[1:-1]);ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
RECEIPTS=[]


def sheet(title,subtitle):
    s=Sheet(title,subtitle);s.scale=85;s.ox=350;s.oy=1160
    return s


def base(s,level,rooms=False):
    for wall in CFG['walls']:
        if wall['level']!=level:continue
        for a,b,z0,z1 in geo.wall_cells(wall,CFG['dimensions']['clear_height']):
            if z0<=1.2<=z1:s.poly([s.xy(p) for p in geo.wall_polygon(wall,a,b)],'#48554b')
    for poly in geo.stair_polygons(CFG):s.poly([s.xy(p) for p in poly],'none','#92998d',.8)
    # Linha do contorno da laje: evita confundir cobertura de garagem com paredes.
    outline=CFG['levels'][level]['outline'];s.line([s.xy(p) for p in outline+outline[:1]],'#9a7150',1.2,'7 4')
    if rooms:
        for room in CFG['rooms']:
            if room['level']==level:
                px,py=s.xy(room['label_at']);s.text(px,py,room['label'],12,'#737c71',anchor='middle')


def dimensions(s,level):
    front=-1.2 if level else 0
    s.dimension([0,front],[6.35,front],'6,35 m · eixo da geminação',65)
    s.dimension([0,front],[0,6.50 if level else 5.70],'7,70 m' if level else '5,70 m',-190)
    s.dimension([6.35,front],[6.35,7.20],'8,40 m' if level else '7,20 m',70)
    if level:
        s.dimension([0,6.50],[0,7.20],'0,70 m',-250)
    else:
        s.dimension([3.45,7.20],[6.25,7.20],'2,80 m',-35)
        s.dimension([0,5.70],[0,7.20],'1,50 m',-250)


def footer(s,number,lines):
    y=1350
    for line in lines:s.text(75,y,line,15,'#626963');y+=27
    s.line([(75,1480),(1325,1480)],'#c7c9bf')
    s.text(75,1520,'RESIDÊNCIA 07 · PRANCHAS TÉCNICAS SEM MOBILIÁRIO',18,weight='bold')
    s.text(75,1556,'Cotas em metros. Símbolos e especificações: consultar os originais anexos.',16,'#626963')
    s.text(75,1590,'Projeto fornecido de 2011 · situação construída não levantada.',16,'#626963')
    s.text(1315,1625,number,30,anchor='end')


def structural(level):
    suffix='superior' if level else 'terreo';title='Base estrutural · '+('superior' if level else 'térreo')
    s=sheet(title,'Paredes, laje, vãos e escada da arquitetura · sem mobiliário')
    base(s,level,True);dimensions(s,level)
    # Cotas verticais confirmadas nos cortes; não atribuir seções resistentes às paredes.
    s.text(75,285,'NÍVEIS',17,weight='bold')
    s.text(75,320,'Piso: '+('+2,70 m' if level else '0,00 m'),17)
    s.text(75,353,'Pé-direito: 2,55 m',16)
    s.text(75,386,'Laje: 0,15 m',16)
    s.text(75,419,'Paredes: 0,15 m*',16)
    s.text(75,452,'Geminada: 0,20 m',16)
    s.text(75,490,'* espessura arquitetônica',12,'#626963')
    s.text(75,518,'Função resistente não informada.',12,'#626963')
    footer(s,'E01' if level==0 else 'E02',[
        'Elementos indicados no projeto arquitetônico; não classifica paredes como portantes.',
        'Fundações, armaduras e seções de vigas/pilares: não fornecidas.',
        'A planta sem mobiliário está cotada; o cálculo estrutural permanece não informado.'
    ])
    name='estrutura-'+suffix;s.save(name);return name


def parse_color(value):
    if value.startswith('#') and len(value)==7:
        return [int(value[i:i+2],16)/255 for i in [1,3,5]]
    return None


def filter_colored(root):
    """Só para a sobreposição: a prancha individual conserva também texto preto."""
    def visit(node,inherited):
        if node.tag in [NS+'defs',NS+'clipPath']:return True
        style=dict(inherited)
        for key in ['fill','stroke']:
            if key in node.attrib:style[key]=node.attrib[key]
        if list(node):
            for child in list(node):
                if not visit(child,style):node.remove(child)
            return bool(list(node))
        if node.tag in [NS+'path',NS+'use',NS+'rect',NS+'circle',NS+'polyline']:
            colors=[parse_color(style.get(key,'')) for key in ['fill','stroke']]
            return any(c is not None and max(c)-min(c)>.15 for c in colors)
        return False
    visit(root,{'fill':'#000000','stroke':'none'})


def vector_layer(s,layer,colored_only=False):
    path=SOURCES/layer['file'];prefix=layer['id']+'-'+('color' if colored_only else 'full')+'-'
    with fitz.open(path) as doc:
        page=doc[0];svg=ET.fromstring(page.get_svg_image(text_as_path=True))
    if colored_only:filter_colored(svg)
    # IDs dos glifos precisam ser únicos ao combinar diferentes PDFs em um SVG.
    ids={node.attrib['id']:prefix+node.attrib['id'] for node in svg.iter() if 'id' in node.attrib}
    for node in svg.iter():
        if 'id' in node.attrib:node.attrib['id']=ids[node.attrib['id']]
        for key,value in list(node.attrib.items()):
            if value.startswith('#') and value[1:] in ids:node.attrib[key]='#'+ids[value[1:]]
            elif 'url(#' in value:node.attrib[key]=re.sub(r'url\(#([^)]+)\)',lambda m:'url(#'+ids.get(m[1],m[1])+')',value)
    source_svg=ET.tostring(svg,encoding='unicode')
    # Apenas a unidade correta; diagramas comuns completos ficam nos anexos.
    xmin,xmax=-1.80,6.36;ymin=-2.0;ymax=10.80 if layer['level']==0 else 8.80
    # HID04/HID08 têm outras plantas à direita: cortar antes da próxima unidade.
    ppm=layer['points_per_meter'];ox,oy=layer['origin_pt']
    rect=[ox+xmin*ppm,oy-ymax*ppm,(xmax-xmin)*ppm,(ymax-ymin)*ppm]
    # Transformação e recorte explícitos: o conversor SVG/PDF do MuPDF não aplica
    # viewBox de SVG aninhado como um navegador. Não depender desse comportamento.
    px,py=s.ox+xmin*s.scale,s.oy-ymax*s.scale
    pw,ph=(xmax-xmin)*s.scale,(ymax-ymin)*s.scale
    crop=prefix+'viewport';k=s.scale/ppm;tx=s.ox-ox*k;ty=s.oy-oy*k
    s.items.append('<!--R07_SOURCE_BEGIN-->')
    s.items.append(f'<defs><clipPath id="{crop}" clipPathUnits="userSpaceOnUse"><rect x="{px}" y="{py}" width="{pw}" height="{ph}"/></clipPath></defs>')
    s.items.append(f'<g clip-path="url(#{crop})"><g transform="matrix({k} 0 0 {k} {tx} {ty})">')
    for child in svg:s.items.append(ET.tostring(child,encoding='unicode'))
    s.items.append('</g></g>')
    s.items.append('<!--R07_SOURCE_END-->')
    if not hasattr(s,'layer_jobs'):s.layer_jobs=[]
    s.layer_jobs.append({'path':path,'source_svg':source_svg,'colored_only':colored_only,
                         'clip':rect,'destination':[px,py,px+pw,py+ph]})
    # Recibo da transformação; a escala gráfica não altera bitolas/circuitos.
    RECEIPTS.append({'layer':layer['id'],'source':str(path.relative_to(ROOT)),'source_sha256':geo.sha(path),
                     'colored_only':colored_only,'origin_pt':[ox,oy],'points_per_meter':ppm,
                     'clip_viewbox_pt':rect,'vector_elements':sum(1 for n in svg.iter() if n.tag in [NS+'path',NS+'use'])})


def save_technical(s,name):
    """SVG válido para navegador; PDF usa recorte PDF nativo, com suporte integral.

    MuPDF não aplica clip-path de SVG ao convertê-lo. Por isso o recorte é feito
    com show_pdf_page(clip=...), preservando os vetores e eliminando outra unidade.
    """
    full='\n'.join(s.items)+ '\n</svg>'
    geo.artifact_path(name,'svg').parent.mkdir(parents=True,exist_ok=True)
    geo.artifact_path(name,'svg').write_text(full)
    clean=re.sub(r'<!--R07_SOURCE_BEGIN-->.*?<!--R07_SOURCE_END-->','',full,flags=re.S)
    with fitz.open('svg',clean.encode()) as doc:
        base_pdf=doc.convert_to_pdf()
    with fitz.open('pdf',base_pdf) as target:
        page=target[0]
        for job in getattr(s,'layer_jobs',[]):
            x,y,w,h=job['clip'];clip=fitz.Rect(x,y,x+w,y+h)
            # Normalizar a rotação do PDF pelo SVG da página inteira. Aplicar
            # clip diretamente ao PDF rotacionado usa outro referencial no MuPDF.
            with fitz.open('svg',job['source_svg'].encode()) as svg:pdf=svg.convert_to_pdf()
            source=fitz.open('pdf',pdf)
            try:page.show_pdf_page(fitz.Rect(job['destination']),source,0,clip=clip,keep_proportion=False,overlay=True)
            finally:source.close()
        target.save(geo.artifact_path(name,'pdf'),garbage=4,deflate=True)
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(geo.artifact_path(name)))


def individual(layer,index):
    s=sheet(layer['title'],'Traçado vetorial original registrado na base cotada da residência 07')
    vector_layer(s,layer)
    dimensions(s,layer['level'])
    footer(s,f'I{index:02}',[
        'Fonte: '+layer['file']+' · tipologia interna correspondente à residência 07.',
        'Símbolos, circuitos, bitolas, diâmetros e alturas preservados da fonte.',
        'Dimensões arquitetônicas de ARQ03; diagramas de instalações não são comprimentos de execução.'
    ])
    save_technical(s,layer['id']);return layer['id']


def combined(level):
    name='instalacoes-coordenadas-'+('superior' if level else 'terreo')
    s=sheet('Instalações · '+('superior' if level else 'térreo'),'Leitura conjunta: base sem mobiliário + água / esgoto + elétrica + TV / telefone')
    base(s,level)
    for layer in SPEC['layers']:
        if layer['level']==level:vector_layer(s,layer,True)
    dimensions(s,level)
    footer(s,'C02' if level else 'C01',[
        'Sobreposição dos traçados coloridos. Notas em preto e legendas completas: pranchas individuais.',
        'Água: HID04 · esgoto: HID08 · elétrica: ELE04/05 · TV/telefone: TV-TEL04/05.',
        'Leitura documental conjunta; interferências em altura e dimensionamento estrutural não avaliados.'
    ])
    save_technical(s,name);return name


def registration_checks():
    checks=[]
    for layer in SPEC['layers']:
        with fitz.open(SOURCES/layer['file']) as doc:
            page=doc[0];rot=page.rotation_matrix;lines=[]
            for drawing in page.get_drawings():
                for item in drawing['items']:
                    if item[0]=='l':lines.append([q*rot for q in item[1:]])
        ox,oy=layer['origin_pt'];ppm=layer['points_per_meter']
        # Verificar independentemente duas faces verticais e uma horizontal da arquitetura-fonte.
        for label,axis,value,extent in [('oeste',0,0,1.0),('interna geminada',0,6.25,1.0),('fundos cozinha/quarto',1,7.2,1.0)]:
            candidates=[]
            for a,b in lines:
                if not (ox-.1*ppm<=a.x<=ox+6.4*ppm and ox-.1*ppm<=b.x<=ox+6.4*ppm):continue
                if not (oy-10.5*ppm<=a.y<=oy+2*ppm and oy-10.5*ppm<=b.y<=oy+2*ppm):continue
                a=[(a.x-ox)/ppm,(oy-a.y)/ppm];b=[(b.x-ox)/ppm,(oy-b.y)/ppm]
                if abs(a[axis]-b[axis])<.002 and math.dist(a,b)>extent:candidates.append(a[axis])
            nearest=min(candidates,key=lambda n:abs(n-value));error=abs(nearest-value)
            checks.append({'layer':layer['id'],'anchor':label,'target_m':value,'source_m':round(nearest,5),'error_m':round(error,5),'passed':error<.015})
    return checks


def original_dimensions(level):
    suffix='superior' if level else 'terreo';name='cotas-originais-'+suffix
    s=Sheet('Cotas originais · '+('superior' if level else 'térreo'),'Recorte vetorial de ARQ03 · preserva todas as cotas escritas da tipologia da unidade 07')
    footer(s,'M02' if level else 'M01',[
        'As cotas desta prancha são as inscrições originais, sem substituição por medidas estimadas.',
        'Diferenças entre cota, traço e área: consultar o quadro de divergências do relatório.'
    ])
    bounds=(525,825,953,1440) if level else (540,160,953,658)
    with fitz.open(ROOT/'plantas/arq03.pdf') as source:
        svg=source[0].get_svg_image(text_as_path=True)
    # Converter a página já na orientação de leitura e só depois recortá-la.
    with fitz.open('svg',svg.encode()) as source:pdf=source.convert_to_pdf()
    clean='\n'.join(s.items)+'\n</svg>'
    with fitz.open('svg',clean.encode()) as source:basepdf=source.convert_to_pdf()
    with fitz.open('pdf',basepdf) as target,fitz.open('pdf',pdf) as source:
        target[0].show_pdf_page(fitz.Rect(150,240,1250,1300),source,0,clip=fitz.Rect(bounds),keep_proportion=True)
        target.save(geo.artifact_path(name,'pdf'),garbage=4,deflate=True)
        target[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(geo.artifact_path(name)))
    # SVG navegável equivalente, com crop explicitamente definido.
    sourcexml=ET.fromstring(svg);crop=fitz.Rect(bounds);k=min(1100/crop.width,1060/crop.height)
    px=700-crop.width*k/2;py=240
    inner=''.join(ET.tostring(n,encoding='unicode') for n in sourcexml)
    s.items.append(f'<defs><clipPath id="source-cotas"><rect x="{px}" y="{py}" width="{crop.width*k}" height="{crop.height*k}"/></clipPath></defs>')
    s.items.append(f'<g clip-path="url(#source-cotas)"><g transform="matrix({k} 0 0 {k} {px-crop.x0*k} {py-crop.y0*k})">{inner}</g></g>')
    geo.artifact_path(name,'svg').write_text('\n'.join(s.items)+'\n</svg>')
    return name


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    names=[structural(0),structural(1),original_dimensions(0),original_dimensions(1),combined(0),combined(1)]
    names += [individual(layer,i+1) for i,layer in enumerate(SPEC['layers'])]
    book=fitz.open()
    for name in names:
        with fitz.open(geo.artifact_path(name,'pdf')) as source:book.insert_pdf(source)
    for name in SPEC['appendices']:
        with fitz.open(SOURCES/name) as source:book.insert_pdf(source)
    book.set_metadata({'title':'Residência 07 — base estrutural e instalações','subject':'Pranchas sem mobiliário, hidráulica, esgoto, elétrica e TV/telefone','creator':'residence07_technical.py'})
    path=geo.artifact_path('plantas-tecnicas-residencia-07','pdf');path.parent.mkdir(parents=True,exist_ok=True);book.save(path);pages=len(book);book.close()
    checks=registration_checks()
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'unit':'07','sheets':names,'pages':pages,
             'layers':RECEIPTS,'registration_checks':checks,'all_passed':all(c['passed'] for c in checks),
             'technical_config_sha256':geo.sha(ROOT/'config/residencia-07-instalacoes.json'),
             'pdf_sha256':geo.sha(path),'notes':SPEC['notes']}
    (REPORT/'instalacoes.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('R07_TECHNICAL',len(names),'pranchas',pages,'páginas',len(checks),'verificações',receipt['all_passed'])
    if not receipt['all_passed']:
        for c in checks:
            if not c['passed']:print('FAIL',c)
        raise RuntimeError('Rever registro das instalações.')


if __name__=='__main__':main()
