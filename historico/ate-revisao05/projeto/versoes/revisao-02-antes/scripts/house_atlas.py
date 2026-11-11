"""Montagens de comparação e plantas. Não altera as fotografias originais."""
from pathlib import Path
import datetime as dt
import json
from PIL import Image,ImageDraw,ImageFont,ImageStat

root=Path(__file__).resolve().parents[1];out=root/'renders/planta-casa'
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,27);small=ImageFont.truetype(font_path,21);title=ImageFont.truetype(font_path,36)

def rgb(name):
    with Image.open(out/name) as im:result=im.convert('RGB')
    stat=ImageStat.Stat(result.convert('L'))
    assert 12<stat.mean[0]<245 and stat.stddev[0]>10,('Render sem conteúdo visual suficiente',name,stat.mean,stat.stddev)
    return result

def pair(name,left,right,labels,subtext):
    a,b=rgb(left),rgb(right)
    assert a.size==b.size
    width,height=a.size
    im=Image.new('RGB',(width*2,height+140),(28,34,38));d=ImageDraw.Draw(im)
    d.text((25,18),labels[0],font=title,fill='white');d.text((width+25,18),labels[1],font=title,fill='white')
    d.text((25,76),subtext,font=font,fill=(238,190,104))
    im.paste(a,(0,140));im.paste(b,(width,140));im.save(out/name)

pair('planta-3d.png','terreo-3d.png','superior-3d.png',('TÉRREO · reconstrução proporcional','SUPERIOR · distribuição hipotética'),
     'Fotos originais como referência. Todas as dimensões são estimadas; análise de áreas do ChatGPT não verificada.')
pair('plantas-superiores.png','terreo-superior.png','pavimento-superior.png',('TÉRREO · vista superior','PAVIMENTO SUPERIOR · vista superior'),
     'Cotas aproximadas. Posição dos quartos, banheiros e acessos de serviço precisa de confirmação.')

jobs=[('sala7.webp','sala-fundos.png','SALA → JANTAR / BAR / COZINHA'),('sala4.webp','sala-frente.png','SALA → FACHADA / ESCADA'),('cozinha1.webp','cozinha.png','COZINHA')]
canvas=Image.new('RGB',(2400,3*700+100),(28,34,38));draw=ImageDraw.Draw(canvas)
draw.text((25,15),'FOTOS ORIGINAIS × RECONSTRUÇÃO 3D · comparação de organização, sem calibração métrica',font=font,fill='white')
for i,(source,render,label) in enumerate(jobs):
    with Image.open(root/'referencias-originais'/source) as im:a=im.convert('RGB')
    b=rgb(render)
    assert a.size==b.size==(1200,630)
    y=100+i*700
    draw.text((20,y),label+' · '+source,font=font,fill='white')
    draw.text((1220,y),'BLENDER / CYCLES · geometria editável',font=font,fill='white')
    canvas.paste(a,(0,y+50));canvas.paste(b,(1200,y+50))
canvas.save(out/'comparacao-originais.png')
report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'comparisons':[{'source':'referencias-originais/'+a,'render':'renders/planta-casa/'+b} for a,b,_ in jobs],'method':'Lado a lado em 1200×630. Análise visual de relações entre ambientes e elementos; sem alegar equivalência fotográfica ou métrica.','source_priorities':['Fotos originais para elementos e organização observáveis','Texto secundário do ChatGPT apenas como ordem de grandeza não verificada','Imagens industriais anteriores preservadas como proposta de estilo, sem controlar a arquitetura atual']}
(root/'relatorios/planta-casa/comparacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('HOUSE_ATLAS_COMPLETE',out)
