"""Imagens de conferência e giro da v05, sem modificar versões anteriores."""
import base64
from html import escape
import json
from pathlib import Path

import fitz
from PIL import Image,ImageDraw,ImageOps,ImageFont

import residence07_attic_v05_data as data

ROOT=data.ROOT;OUT=ROOT/data.CFG['render_directory'];DETAIL=OUT/'07-escadas'


def font(size):return ImageFont.truetype(str(ROOT/'assets/fonts/DejaVuSans.ttf'),size)


def matte(path):
    with Image.open(path) as original:
        original.load();result=Image.new('RGB',original.size,'#faf9f4')
        result.paste(original,mask=original.getchannel('A') if original.mode=='RGBA' else None)
    return result


def stills(model):
    lookup={j['id']:j for j in model['jobs'] if j['group']=='detail'}
    return [lookup[k] for k in ['01-referencia','04-giro-270','02-giro-90','03-giro-180','05-lateral-patamares','06-vista-superior']]


def panels(model):
    views=stills(model);canvas=Image.new('RGB',(2400,2360),'#faf9f4');draw=ImageDraw.Draw(canvas)
    draw.text((60,30),'V05 / LANCES EXATAMENTE SOBREPOSTOS',font=font(45),fill='#304039')
    draw.text((60,95),'Caixa deslocada para a esquerda · linha laranja = percurso completo',font=font(28),fill='#66756b')
    for i,j in enumerate(views):
        x=(i%3)*800+20;y=(i//3)*1060+160;tile=ImageOps.contain(matte(ROOT/j['file']),(760,925));canvas.paste(tile,(x+(760-tile.width)//2,y+(925-tile.height)//2))
        draw.text((x+12,y+950),j['title'],font=font(22),fill='#304039')
    draw.text((65,2300),'Mesmos polígonos XY nos 16 degraus; deslocamento vertical de +2,70 m. Hall nominal: 65 cm.',font=font(25),fill='#66756b')
    DETAIL.mkdir(parents=True,exist_ok=True);overview=DETAIL/'painel-seis-angulos.jpg';canvas.save(overview,quality=94)
    return (overview,)


def animation(model):
    frames=sorted([j for j in model['jobs'] if j['group']=='orbit'],key=lambda j:j['angle_degrees']);ordered=frames[18:]+frames[:18];images=[]
    for j in ordered:
        canvas=Image.new('RGB',(900,1100),'#faf9f4');canvas.paste(matte(ROOT/j['file']),(0,65));draw=ImageDraw.Draw(canvas)
        draw.text((25,20),'V05 / ESCADAS SOBREPOSTAS + CAIXA LATERAL',font=font(25),fill='#304039')
        draw.text((25,1060),f"Giro {j['angle_degrees']}° · subida em laranja · hall nominal 65 cm",font=font(21),fill='#66756b');images.append(canvas)
    palette=images[0].quantize(colors=128);indexed=[p.quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG) for p in images]
    indexed[0].save(DETAIL/'giro-360.gif',save_all=True,append_images=indexed[1:],duration=[650 if j['angle_degrees']%90==0 else 180 for j in ordered],loop=0,disposal=2,optimize=False)
    template=ROOT/'scripts/templates/atico-escadas.html';html=template.read_text()
    assert '60 cm' not in html and 'v04' not in html
    (DETAIL/'galeria.html').write_text(html)
    doc=fitz.open();page=doc.new_page(width=842,height=842);page.insert_image(fitz.Rect(15,15,827,827),filename=str(DETAIL/'painel-seis-angulos.jpg'),keep_proportion=True)
    for j in stills(model):
        page=doc.new_page(width=680,height=842);page.insert_text((30,35),j['title'],fontsize=16);page.insert_image(fitz.Rect(25,55,655,777),filename=str(ROOT/j['file']),keep_proportion=True)
        page.insert_textbox(fitz.Rect(30,795,650,832),'Escadas com XY idênticos e desnível de 2,70 m. Caixa à esquerda; cota de base mantida em +5,45 m. Paredes/cobertura omitidas.',fontsize=9)
    doc.save(DETAIL/'escadas-seis-angulos.pdf',deflate=True,garbage=4);doc.close()
    return template


def hero(model,audit):
    job=next(j for j in model['jobs'] if j['id']=='01-referencia');canvas=Image.new('RGB',(2400,2200),'#faf9f4');draw=ImageDraw.Draw(canvas)
    draw.text((75,35),'V05 / ESCADAS DO TÉRREO AO ÁTICO',font=font(58),fill='#304039')
    draw.text((75,115),'Dois lances novos exatamente sobre os existentes · caixa reposicionada',font=font(31),fill='#66756b')
    tile=matte(ROOT/job['file']).resize((1548,1720),Image.Resampling.LANCZOS);canvas.paste(tile,(70,190))
    anchors=audit['hero_anchors'];points={n:(70+1548*p[0],190+1720*(1-p[1])) for n,p in anchors.items()}
    colors=['#52786c','#ad672b','#c6662a','#52786c','#427f9c']
    for i,(key,offset) in enumerate([('inicio',(-60,80)),('hall',(-180,20)),('nova',(200,-25)),('saida',(140,-45)),('caixa',(-160,-60))]):
        ax,ay=points[key];x,y=ax+offset[0],ay+offset[1];draw.line([(ax,ay),(x,y)],fill=colors[i],width=3);draw.ellipse((x-28,y-28,x+28,y+28),fill=colors[i],outline='white',width=4);draw.text((x,y),str(i+1),font=font(33),fill='white',anchor='mm')
    items=[('5 · CAIXA À ESQUERDA',['Centro X=1,80 / Y=3,175 m.','Deslocada 3,55 m em X.','Base +5,45 m mantida.','Capacidade: 1.000 L.']),('4 · CHEGADA AO ÁTICO',['Piso em +5,40 m.','Vão em L, igual ao existente.']),('3 · NOVA ESCADA EM U',['16 pisos com XY idênticos','aos 16 existentes.','Somente +2,70 m na vertical.']),('2 · CHEGADA EXISTENTE',['Piso em +2,70 m.','Nova subida junto ao hall.','Sem ligação pelo quarto frontal.']),('1 · INÍCIO NO TÉRREO',['Piso em +0,00 m.','Escada existente preservada.'])]
    for i,(title,lines) in enumerate(items):
        y=315+i*310;draw.text((1640,y),title,font=font(34),fill='#304039')
        for k,line in enumerate(lines):draw.text((1640,y+58+k*42),line,font=font(28),fill='#66756b')
    minimum=min(r['minimum_m'] for r in audit['stair_clearance'])
    draw.line((70,1940,2330,1940),fill='#bdc7bc',width=2)
    draw.text((75,1990),f'Altura livre mínima amostrada: {minimum:.2f} m · forro com reserva de 15 cm · altura máxima no ático: 3,77 m'.replace('2.21','2,21'),font=font(29),fill='#304039')
    draw.text((75,2050),'Paredes e cobertura omitidas; pisos recortados apenas para leitura. Nova posição da caixa é proposta.',font=font(28),fill='#66756b')
    draw.text((75,2110),'Hall nominal de 65 cm e apoios/cargas/instalações definitivas ainda dependem de compatibilização e projeto.',font=font(28),fill='#9a5c2a')
    canvas.save(DETAIL/'escada-completa-caixa.png')
    doc=fitz.open();page=doc.new_page(width=900,height=825);page.insert_image(page.rect,filename=str(DETAIL/'escada-completa-caixa.png'));doc.save(DETAIL/'escada-completa-caixa.pdf',deflate=True,garbage=4);doc.close()


def main_gallery(model):
    cards=[]
    for j in model['jobs']:
        if j['group']!='main':continue
        rel=geo_rel(ROOT/j['file'],OUT);cards.append(f'<figure><a href="{escape(rel)}"><img src="{escape(rel)}" loading="lazy" alt="{escape(j["title"])}"></a><figcaption>{escape(j["title"])}</figcaption></figure>')
    page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ático v05</title><style>body{font:17px system-ui;background:#faf9f4;color:#304039;padding:3vw;margin:0}p{max-width:85ch;line-height:1.5}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}figure{margin:0;background:white;border:1px solid #d4dccc}img{width:100%}figcaption{padding:14px}a{color:#326c81}</style><h1>Ático v05 / escadas sobrepostas e caixa lateral</h1><p>Os dois lances novos repetem os existentes, deslocados somente 2,70 m para cima. A caixa foi movida 3,55 m para a esquerda, mantendo sua cota de base. Forro, mansardas e casa atual preservados; quartos sem ocupação pela nova escada.</p><p><a href="07-escadas/galeria.html">Girar as escadas em 360°</a> · <a href="07-escadas/escada-completa-caixa.png">Desenho isolado</a> · <a href="00-cadernos/caderno-atico-v05.pdf">Caderno PDF</a> · <a href="LEIA-ME.md">Medidas e índice</a></p><main>'''+''.join(cards)+'</main></html>'
    (OUT/'galeria.html').write_text(page)


def geo_rel(path,parent):
    import os
    return Path(os.path.relpath(path,parent)).as_posix()


def generate(model,audit):
    pair=panels(model);template=animation(model);hero(model,audit);main_gallery(model)
    return pair,template
