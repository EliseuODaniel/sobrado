"""Comparações atuais: nova planta confirmada, modelo e referências originais."""
from pathlib import Path
import datetime as dt
import hashlib
import json
from PIL import Image,ImageDraw,ImageFont,ImageStat

root=Path(__file__).resolve().parents[1];cfg=json.loads((root/'config/planta-casa.json').read_text())
folder=root/'renders/atual';report_dir=root/'relatorios/atual'
receipt=json.loads((report_dir/'renders-finais.json').read_text())
assert receipt['sha256']==hashlib.sha256((root/'projeto/casa-reconstruida.blend').read_bytes()).hexdigest()
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';title=ImageFont.truetype(font,30);small=ImageFont.truetype(font,22)
def read(path):
    with Image.open(path) as image:im=image.convert('RGB')
    assert ImageStat.Stat(im.convert('L')).stddev[0]>8,path
    return im

def pair(a,b,name,titles,subtitle):
    left,right=read(a),read(b);w=max(left.width,right.width);h=max(left.height,right.height)
    canvas=Image.new('RGB',(w*2,h+125),(27,32,35));draw=ImageDraw.Draw(canvas)
    draw.text((20,14),titles[0],font=title,fill='white');draw.text((w+20,14),titles[1],font=title,fill='white');draw.text((20,72),subtitle,font=small,fill=(240,191,111))
    canvas.paste(left,((w-left.width)//2,125+(h-left.height)//2));canvas.paste(right,(w+(w-right.width)//2,125+(h-right.height)//2));canvas.save(folder/name)

pair(root/cfg['user_layout_source']['path'],folder/'porta-lavabo.png','comparacao-planta.png',
     ('PLANTA MARCADA PELO USUÁRIO','ATUAL · vista da porta sem a escada'),
     'Porta no traço preto horizontal; a escada está oculta apenas nesta vista para mostrar os vãos.')
pair(root/cfg['previous_delivery']['root']/'renders/atual/planta-terreo.png',folder/'planta-terreo.png','antes-depois.png',
     ('ANTERIOR · revisão 06 arquivada','ATUAL · revisão 07'),
     'Parede da cozinha encurtada, acesso contínuo e laje compatível com a faixa sem degraus.')
rows=[('sala7.webp','sala-fundos.png','SALA PARA OS FUNDOS'),('sala4.webp','sala-frente.png','SALA PARA A FRENTE'),('sala1.webp','escada-acesso.png','ACESSO À ESCADA'),('cozinha1.webp','cozinha.png','COZINHA'),('cozinha2.webp','cozinha-reversa.png','COZINHA REVERSA'),('area3.webp','bar.png','CHURRASQUEIRA'),('lavanderia1.webp','lavanderia.png','LAVANDERIA'),('lavabo1.webp','lavabo.png','LAVABO')]
facades=[('exterior2.webp','fachada-frontal.png','FACHADA FRONTAL'),('exterior1.webp','fachada-obliqua.png','FACHADA OBLÍQUA')]
outputs=['comparacao-planta.png','antes-depois.png']
for name,jobs,heading in [('comparacao-fotos.png',rows,'TÉRREO × FOTOS · a nova planta prevalece para a porta e a passagem'),('comparacao-fachada.png',facades,'FACHADA × FOTOS · vizinhas como contexto aproximado')]:
    canvas=Image.new('RGB',(2400,len(jobs)*700+100),(27,32,35));draw=ImageDraw.Draw(canvas);draw.text((20,14),heading,font=title,fill='white')
    for i,(source,render,label) in enumerate(jobs):
        a,b=read(root/'referencias-originais'/source),read(folder/render);assert a.size==b.size==(1200,630)
        y=100+i*700;draw.text((20,y),source+' · '+label,font=small,fill='white');draw.text((1220,y),'ATUAL · modelo editável, medidas aproximadas',font=small,fill='white')
        canvas.paste(a,(0,y+50));canvas.paste(b,(1200,y+50))
    canvas.save(folder/name);outputs.append(name)
for filename,title_text in [('sala-frente.png','SALA PARA A FRENTE'),('acesso-lavabo.png','ACESSO AO LAVABO')]:
    photo=read(folder/filename);plan=read(folder/'porta-lavabo.png');view=receipt['viewpoints'][filename]
    draw=ImageDraw.Draw(plan)
    def pixel(key):return tuple(round(v*s) for v,s in zip(view[key],plan.size))
    point,end=pixel('plan_point'),pixel('plan_direction_end');draw.line([point,end],fill=(210,45,40),width=12)
    draw.ellipse((point[0]-18,point[1]-18,point[0]+18,point[1]+18),fill=(210,45,40),outline='white',width=4)
    dx,dy=end[0]-point[0],end[1]-point[1];length=max(1,(dx*dx+dy*dy)**.5);ux,uy=dx/length,dy/length
    draw.polygon([end,(round(end[0]-30*ux+16*uy),round(end[1]-30*uy-16*ux)),(round(end[0]-30*ux-16*uy),round(end[1]-30*uy+16*ux))],fill=(210,45,40))
    draw.line([pixel('door_start'),pixel('door_end')],fill=(235,135,20),width=18)
    plan=plan.resize((420,630),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(1620,740),(27,32,35));draw=ImageDraw.Draw(canvas)
    draw.text((20,12),title_text+' · mesma geometria da planta',font=title,fill='white')
    draw.text((20,65),'Vermelho: câmera e direção da vista. Laranja: porta do lavabo. Escada oculta só na planta ao lado.',font=small,fill=(240,191,111))
    canvas.paste(photo,(0,110));canvas.paste(plan,(1200,110));target=filename.replace('.png','-planta.png');canvas.save(folder/target);outputs.append(target)
report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'revision':cfg['revision_number'],'blend_sha256':receipt['sha256'],'source':cfg['user_layout_source'],'scope':'Nova planta confirmada e porta horizontal; comparação visual sem validação métrica.','outputs':[str((folder/name).relative_to(root)) for name in outputs],'comparison_rows':[{'source':'referencias-originais/'+s,'render':'renders/atual/'+r} for s,r,_ in rows+facades]}
(report_dir/'comparacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('CURRENT_ATLAS_COMPLETE',len(outputs))
