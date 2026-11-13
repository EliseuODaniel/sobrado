"""Redesenho vetorial das pranchas, extração de evidências e caderno PDF.

Executar com .tools/planta-venv/bin/python. As plantas usam o mesmo contrato
métrico do Blender; nenhuma imagem gerada por IA altera a arquitetura.
"""
import datetime as dt
import json
import math
from pathlib import Path
import sys
from xml.sax.saxutils import escape

import fitz
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo

ROOT=geo.ROOT
CFG=geo.load()
OUT=ROOT/CFG['delivery']['renders']
REPORT=ROOT/CFG['delivery']['reports']
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def extract():
    sources=REPORT/'fontes';sources.mkdir(parents=True,exist_ok=True)
    records=[]
    for path in sorted((ROOT/'plantas').rglob('*')):
        if path.is_file():records.append({'file':str(path.relative_to(ROOT)),'sha256':geo.sha(path),'bytes':path.stat().st_size})
    crops=[('arq03',(540,160,953,658),'terreo-original'),('arq03',(525,825,953,1440),'superior-original'),
           ('arq01',(663,130,862,508),'implantacao-07'),('arq04',(130,440,530,1050),'corte-ee'),
           ('arq04',(605,440,1265,1050),'corte-ff'),('arq04',(1360,450,1755,1050),'fachada-original')]
    for stem,bounds,name in crops:
        with fitz.open(ROOT/f'plantas/{stem}.pdf') as doc:
            page=doc[0]
            page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(bounds)).save(str(sources/(name+'.png')))
    # Guardar os traços fortes, com origem transformada para o mesmo sistema do modelo.
    source_lines={}
    with fitz.open(ROOT/CFG['source']['plan']) as doc:
        page=doc[0];matrix=page.rotation_matrix
        reg=CFG['source']['registration']
        for level,key,region in [(0,'ground_origin_pt',(577,205,942,624)),(1,'upper_origin_pt',(577,882,942,1367))]:
            lines=[];origin=reg[key];scale=reg['points_per_meter']
            for drawing in page.get_drawings():
                if abs(drawing['width']-1.08)>.02:continue
                for item in drawing['items']:
                    if item[0]!='l':continue
                    a,b=[q*matrix for q in item[1:]]
                    if all(region[0]<=q.x<=region[2] and region[1]<=q.y<=region[3] for q in [a,b]):
                        lines.append([[round((q.x-origin[0])/scale,4),round((origin[1]-q.y)/scale,4)] for q in [a,b]])
            source_lines[str(level)]=lines
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'unit':'07',
             'files':records,'selection':CFG['source']['typology'],'wall_lines_m':source_lines,
             'registration':CFG['source']['registration']}
    (REPORT/'fontes.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt


class Sheet:
    def __init__(self,title,subtitle):
        self.items=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1700" viewBox="0 0 1400 1700">',
                    '<rect width="1400" height="1700" fill="#faf8f3"/>']
        self.text(75,80,'CASA / 07',25,'#9c6238',weight='bold')
        self.text(75,143,title,48,weight='bold')
        self.text(75,185,subtitle,20,'#626963')
        self.line([(75,218),(1325,218)],'#c7c9bf',1)
        self.scale=116;self.ox=295;self.oy=1220

    def xy(self,p):return self.ox+p[0]*self.scale,self.oy-p[1]*self.scale

    def poly(self,points,fill,stroke='none',width=1):
        coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
        self.items.append(f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')

    def line(self,points,color='#38403b',width=1,dash=None):
        coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
        dash=f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>')

    def text(self,x,y,text,size=17,color='#25312b',anchor='start',weight='normal',rotate=0):
        transform=f' transform="rotate({rotate} {x} {y})"' if rotate else ''
        self.items.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{transform}>{escape(text)}</text>')

    def dimension(self,a,b,label,offset):
        pa,pb=self.xy(a),self.xy(b)
        if abs(a[1]-b[1])<1e-7:
            y=pa[1]+offset;self.line([pa,(pa[0],y+8)],'#879088');self.line([pb,(pb[0],y+8)],'#879088')
            self.line([(pa[0],y),(pb[0],y)],'#879088')
            for x in [pa[0],pb[0]]:self.line([(x-4,y+6),(x+4,y-6)],'#4a574e',1.5)
            self.text((pa[0]+pb[0])/2,y-10,label,19,anchor='middle')
        else:
            x=pa[0]+offset;self.line([pa,(x-8,pa[1])],'#879088');self.line([pb,(x-8,pb[1])],'#879088')
            self.line([(x,pa[1]),(x,pb[1])],'#879088')
            for y in [pa[1],pb[1]]:self.line([(x-6,y+4),(x+6,y-4)],'#4a574e',1.5)
            self.text(x-10,(pa[1]+pb[1])/2,label,19,anchor='middle',rotate=-90)

    def footer(self,number):
        self.line([(75,1480),(1325,1480)],'#c7c9bf')
        self.text(75,1520,'BASE DOCUMENTAL · ARQ03 / ARQ04 · RESIDÊNCIA 07',19,weight='bold')
        self.text(75,1555,'Geometria reconstruída do projeto de 2011. Cotas em metros.',18,'#626963')
        self.text(75,1587,'Áreas dos ambientes: valores declarados na prancha; conferir divergências no relatório.',16,'#626963')
        self.text(75,1628,'Modelo de estudo · não representa levantamento da situação construída.',16,'#626963')
        self.text(1315,1625,number,35,anchor='end')

    def save(self,name):
        self.items.append('</svg>');path=geo.artifact_path(name,'svg');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(self.items))
        with fitz.open(path) as svg:
            pdfdata=svg.convert_to_pdf()
        with fitz.open('pdf',pdfdata) as doc:
            doc.save(str(geo.artifact_path(name,'pdf')))
            doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(geo.artifact_path(name)))


def plan(level):
    title='Planta baixa · térreo' if level==0 else 'Planta baixa · superior'
    s=Sheet(title,'Tipologia correta da unidade 07 · mesma base métrica do modelo 3D')
    lv=CFG['levels'][level]
    s.poly([s.xy(p) for p in lv['outline']],'#ede9de')
    colors={'suite':'#e3d9c5','cozinha':'#d6e0dc','lavabo':'#d6e0dc','banheiro-suite':'#d6e0dc','banheiro-social':'#d6e0dc','sacada':'#d7ddca','garagem':'#deded7'}
    for room in CFG['rooms']:
        if room['level']==level:s.poly([s.xy(p) for p in room['polygon']],colors.get(room['id'],'#eee8da'))
    stair=geo.stair_polygons(CFG)
    for i,poly in enumerate(stair):
        s.poly([s.xy(p) for p in poly],'#ddd2bd','#7f857a',1)
        # Números só nos pisos retos: leitura clara na escala da prancha.
        if i<5 or i>=11:
            x=sum(p[0] for p in poly)/len(poly);y=sum(p[1] for p in poly)/len(poly)
            px,py=s.xy([x,y]);s.text(px,py+4,f'{i+1:02}',10,anchor='middle')
    for wall in CFG['walls']:
        if wall['level']!=level:continue
        for a,b,z0,z1 in geo.wall_cells(wall,CFG['dimensions']['clear_height']):
            if z0<=1.20<=z1:s.poly([s.xy(p) for p in geo.wall_polygon(wall,a,b)],'#34443b','#34443b',.5)
        for op in wall.get('openings',[]):
            start,end=op['start'],op['start']+op['width']
            a,b=geo.point(wall,start),geo.point(wall,end)
            if op['kind']=='window':
                for offset in [-.025,.025]:s.line([s.xy(geo.point(wall,start,offset)),s.xy(geo.point(wall,end,offset))],'#4a8c96',2)
            elif op['kind']=='sliding':
                s.line([s.xy(a),s.xy(b)],'#4a8c96',3)
                mid=geo.point(wall,(start+end)/2);s.line([s.xy(mid),s.xy(geo.point(wall,end,.06))],'#4a8c96',1.5)
            else:
                # Porta aberta e arco de giro no plano métrico.
                end_open=geo.point(wall,start,op['width'])
                s.line([s.xy(a),s.xy(end_open)],'#9a6940',2)
                length=math.dist(wall['a'],wall['b']);ux=(wall['b'][0]-wall['a'][0])/length;uy=(wall['b'][1]-wall['a'][1])/length
                arc=[]
                for j in range(21):
                    angle=j*math.pi/40;distance=op['width']
                    arc.append(s.xy([a[0]+distance*(ux*math.cos(angle)-uy*math.sin(angle)),a[1]+distance*(uy*math.cos(angle)+ux*math.sin(angle))]))
                s.line(arc,'#bc9977',1)
    for room in CFG['rooms']:
        if room['level']!=level:continue
        px,py=s.xy(room['label_at']);size=15 if 'banheiro' not in room['id'] else 13
        s.text(px,py,room['label'],size,anchor='middle',weight='bold')
        s.text(px,py+24,f"{room['declared_area']:.2f} m²".replace('.',','),15,'#69746b',anchor='middle')
    # Dados e cotas externas, sem impor o antigo contorno comum retangular.
    s.dimension([0,-1.2 if level else 0],[6.35,-1.2 if level else 0],'6,35 · até eixo da geminação',70)
    s.dimension([0,0 if level==0 else -1.2],[0,5.7 if level==0 else 6.5],'5,70' if level==0 else '7,70',-65)
    s.dimension([6.35,0 if level==0 else -1.2],[6.35,7.2],'7,20' if level==0 else '8,40',80)
    if level==0:
        s.dimension([0,5.7],[3.3,5.7],'3,30',-45)
        s.dimension([3.45,7.2],[6.25,7.2],'2,80',-45)
    else:s.dimension([0,6.5],[0,7.2],'0,70',-140)
    px,py=s.xy([6.35,5.2]);s.text(px+40,py,'EIXO DA PAREDE GEMINADA',12,'#7c857c',rotate=-90)
    # Escala gráfica 0–1–2 m. A impressão pode ser redimensionada; não declarar 1:50.
    for i in range(4):
        x=75+i*58;s.poly([(x,1410),(x+58,1410),(x+58,1422),(x,1422)],'#34443b' if i%2==0 else '#e6e5dc','#34443b')
    for i in range(3):s.text(75+i*116,1446,str(i)+' m',14)
    s.text(1200,1410,'FRENTE',16,'#9c6238',anchor='end')
    s.footer('01' if level==0 else '02');s.save('planta-terreo' if level==0 else 'planta-superior')


def overlay():
    s=Sheet('Sobreposição dos pavimentos','Contornos reais do projeto · mesma escala, origem e alinhamento posterior')
    for level,color in [(0,'#b77945'),(1,'#397f82')]:
        poly=CFG['levels'][level]['outline']
        s.line([s.xy(p) for p in poly+poly[:1]],color,5,dash='14 7' if level==0 else None)
    for p0,p1,label in [([-.3,0],[-.3,-1.2],'Avanço frontal do superior: 1,20 m'),([-.3,5.7],[-.3,6.5],'Banheiros recuados: fundos em Y=6,50 m')]:
        s.line([s.xy(p0),s.xy(p1)],'#7a837c',2)
    s.text(75,1300,'TÉRREO',21,'#b77945',weight='bold');s.text(350,1300,'SUPERIOR',21,'#397f82',weight='bold')
    s.text(75,1345,'Cozinha e quarto dos fundos: limite posterior comum Y=7,20 m.',20)
    s.text(75,1380,'Os dois pavimentos não têm um contorno retangular comum.',20)
    s.footer('03');s.save('pavimentos-sobrepostos')


def section():
    s=Sheet('Cortes e cobertura','Níveis verticais reconstituídos da prancha ARQ04')
    # Perfil longitudinal, em escala uniforme de 105 px por metro.
    scale=105;ox=235;oy=1300
    xy=lambda yz:(ox+yz[0]*scale,oy-yz[1]*scale)
    for z in [0,2.7,5.4]:
        s.poly([xy(p) for p in [(-1.2,z-.15),(7.2,z-.15),(7.2,z),(-1.2,z)]],'#34443b')
        s.text(115,oy-z*scale+7,f'+{z:.2f} m'.replace('.',','),20)
        s.line([(205,oy-z*scale),(1100,oy-z*scale)],'#a4aba2',1,'6 5')
    for y in [-1.2,7.2]:s.poly([xy(p) for p in [(y,0),(y+.15,0),(y+.15,5.4),(y,5.4)]],'#34443b')
    s.poly([xy(p) for p in [(-1.2,5.4),(3,9.4),(7.2,5.4),(7,5.4),(3,9.18),(-1,5.4)]],'#9c6238')
    s.text(ox+3*scale,oy-9.4*scale-25,'CUMEEIRA +9,40 m',22,anchor='middle',weight='bold')
    for z in [1.2,3.9]:s.text(ox+3*scale,oy-z*scale,'PÉ-DIREITO 2,55 m',23,anchor='middle')
    s.text(ox+3*scale,oy-6.6*scale,'ÁREA SOB COBERTURA · SEM USO',21,anchor='middle')
    s.text(75,1428,'Lajes de 0,15 m · nível superior +2,70 m · cobertura +5,40 m.',20)
    s.footer('04');s.save('corte-longitudinal')


def gallery_and_book():
    files=[(v['id'],v['title']) for v in CFG['views'] if geo.artifact_path(v['id']).exists()]
    if files:
        cellw,cellh=640,530;cols=3;rows=math.ceil(len(files)/cols)
        canvas=Image.new('RGB',(cols*cellw,rows*cellh+160),'#f4f1e9');draw=ImageDraw.Draw(canvas)
        draw.text((35,28),'RESIDÊNCIA 07',font=ImageFont.truetype(FONT,45),fill='#263c30')
        draw.text((35,91),'Arquitetura ARQ03 + ARQ04 · interiores industriais · nova reconstrução',font=ImageFont.truetype(FONT,23),fill='#6b756a')
        for i,(name,title) in enumerate(files):
            with Image.open(geo.artifact_path(name)) as im:
                im=im.convert('RGB');im.thumbnail((cellw-30,cellh-64))
                x=(i%cols)*cellw+15;y=(i//cols)*cellh+160
                canvas.paste(im,(x+(cellw-30-im.width)//2,y))
            draw.text((x+8,y+cellh-56),title,font=ImageFont.truetype(FONT,20),fill='#263c30')
        gallery=geo.artifact_path('painel-geral','jpg');gallery.parent.mkdir(parents=True,exist_ok=True);canvas.save(gallery,quality=93)
    book=fitz.open()
    for name in ['planta-terreo','planta-superior','pavimentos-sobrepostos','corte-longitudinal']:
        with fitz.open(geo.artifact_path(name,'pdf')) as doc:book.insert_pdf(doc)
    technical=REPORT/'instalacoes.json'
    if technical.exists():
        for name in json.loads(technical.read_text())['sheets']:
            with fitz.open(geo.artifact_path(name,'pdf')) as doc:book.insert_pdf(doc)
    for name,title in files:
        p=book.new_page(width=842,height=650)
        p.insert_text((30,34),title.encode('latin-1','replace').decode('latin-1'),fontsize=17,color=(.14,.23,.18))
        p.insert_image(fitz.Rect(25,55,817,615),filename=str(geo.artifact_path(name)),keep_proportion=True)
        p.insert_text((30,635),'Residencia 07 | Projeto 2011 + proposta de interiores | Imagem do modelo Blender',fontsize=9,color=(.4,.45,.4))
    book.set_metadata({'title':'Residência 07 — plantas e reconstrução 3D','subject':'ARQ03 e ARQ04, tipologia esquerda','creator':'residence07_plans.py'})
    dest=geo.artifact_path('caderno-residencia-07','pdf');dest.parent.mkdir(parents=True,exist_ok=True)
    book.save(str(dest));book.close()
    return len(files)


def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    if '--delivery-only' not in sys.argv:
        extract();plan(0);plan(1);overlay();section()
    count=gallery_and_book()
    print('PLANTAS_07_OK',count,'renders no caderno')


if __name__=='__main__':main()
