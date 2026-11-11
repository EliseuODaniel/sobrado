"""Comparações da revisão 02; originais, versão rejeitada e geometria revisada."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import shutil
from PIL import Image,ImageDraw,ImageFont,ImageStat

root=Path(__file__).resolve().parents[1];final=root/'renders/revisao-02/final';out=root/'renders/planta-casa';out.mkdir(exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';title=ImageFont.truetype(font,31);small=ImageFont.truetype(font,23)
receipt=json.loads((root/'relatorios/revisao-02/renders-finais.json').read_text())
assert receipt['sha256']==hashlib.sha256((root/'projeto/casa-reconstruida.blend').read_bytes()).hexdigest()


def read(path):
    with Image.open(path) as image:im=image.convert('RGB')
    stats=ImageStat.Stat(im.convert('L'))
    assert 10<stats.mean[0]<248 and stats.stddev[0]>8,('Imagem sem conteúdo suficiente',path)
    return im


def pair(a,b,target,titles,subtitle):
    left=read(a);right=read(b);assert left.size==right.size
    w,h=left.size;canvas=Image.new('RGB',(w*2,h+125),(27,32,35));draw=ImageDraw.Draw(canvas)
    draw.text((20,14),titles[0],font=title,fill='white');draw.text((w+20,14),titles[1],font=title,fill='white');draw.text((20,72),subtitle,font=small,fill=(240,191,111))
    canvas.paste(left,(0,125));canvas.paste(right,(w,125));canvas.save(target)


pair(final/'terreo-3d.png',final/'estudos-superior.png',out/'planta-3d.png',
     ('TÉRREO · revisão das relações fotografadas','SUPERIOR · módulos SEM implantação confirmada'),
     'As medidas permanecem estimadas. Os módulos da direita não formam a planta do superior.')
pair(final/'terreo-superior.png',final/'superior-envoltoria.png',out/'plantas-superiores.png',
     ('TÉRREO · vista superior revisada','SUPERIOR · apenas envoltória e vão da escada'),
     'As divisões internas anteriores foram retiradas por falta de evidência de suas ligações.')
aliases={'sala-fundos.png':'sala-fundos.png','sala-frente.png':'sala-frente.png','cozinha.png':'cozinha.png','terreo-3d.png':'terreo-3d.png','terreo-superior.png':'terreo-superior.png','superior-pendente.png':'superior-3d.png','superior-envoltoria.png':'pavimento-superior.png','volumetria.png':'volumetria.png','estudos-superior.png':'estudos-superior.png'}
for source,target in aliases.items():shutil.copy2(final/source,out/target)
rows=[('sala7.webp','sala-fundos.png','SALA PARA OS FUNDOS'),('sala4.webp','sala-frente.png','SALA PARA A FRENTE'),('sala1.webp','escada-acesso.png','ACESSO LATERAL À ESCADA E COZINHA'),('cozinha1.webp','cozinha.png','COZINHA — BANCADAS E JANELA'),('cozinha2.webp','cozinha-reversa.png','COZINHA — SENTIDO REVERSO'),('area3.webp','bar.png','BAR E COBERTURA')]
canvas=Image.new('RGB',(2400,len(rows)*700+100),(27,32,35));draw=ImageDraw.Draw(canvas)
draw.text((20,14),'FOTOS ORIGINAIS × REVISÃO 02 · comparação de relações, não validação métrica',font=title,fill='white')
for i,(source,render,label) in enumerate(rows):
    a=read(root/'referencias-originais'/source);b=read(final/render);assert a.size==b.size==(1200,630);y=100+i*700
    draw.text((20,y),source+' · '+label,font=small,fill='white');draw.text((1220,y),'REVISÃO 02 · Cycles, arquivo reaberto',font=small,fill='white');canvas.paste(a,(0,y+50));canvas.paste(b,(1200,y+50))
canvas.save(out/'comparacao-originais.png')
canvas=Image.new('RGB',(3600,1520),(27,32,35));draw=ImageDraw.Draw(canvas)
draw.text((20,10),'REVISÃO DA IMPLANTAÇÃO · os enquadramentos foram reajustados para as fotografias',font=title,fill='white')
for i,(source,render,_) in enumerate(rows[:2]):
    y=100+i*700
    for j,(path,label) in enumerate([(root/'referencias-originais'/source,'FOTO ORIGINAL'),(root/'relatorios/revisao-02/antes-renders'/render,'VERSÃO REJEITADA'),(final/render,'REVISÃO 02')]):
        draw.text((1200*j+20,y),label,font=title,fill='white');canvas.paste(read(path),(1200*j,y+50))
canvas.save(out/'comparacao-antes-depois.png')
report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':receipt['sha256'],'comparison_rows':[{'source':'referencias-originais/'+s,'render':'renders/revisao-02/final/'+r} for s,r,_ in rows],'scope':'Comparações visuais em seis ângulos; medidas e conexões do superior não verificadas. A versão rejeitada usa seus enquadramentos anteriores.','outputs':['renders/planta-casa/planta-3d.png','renders/planta-casa/plantas-superiores.png','renders/planta-casa/comparacao-originais.png','renders/planta-casa/comparacao-antes-depois.png']}
(root/'relatorios/planta-casa/comparacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('REVISION_ATLAS_COMPLETE')
