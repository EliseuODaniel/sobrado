"""Comparações atuais: nova planta confirmada, modelo e referências originais."""
from pathlib import Path
import datetime as dt
import hashlib
import json
from PIL import Image,ImageDraw,ImageFont,ImageStat

root=Path(__file__).resolve().parents[1];cfg=json.loads((root/'config/planta-casa.json').read_text())
folder=root/'renders/atual';report_dir=root/'arquivos/versoes-anteriores-2026-11-14/relatorios/atual-anterior'
receipt=json.loads((report_dir/'renders-finais.json').read_text())
assert receipt['sha256']==hashlib.sha256((root/'arquivos/versoes-anteriores-2026-11-14/projeto/casa-reconstruida.blend').read_bytes()).hexdigest()
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
     'Porta horizontal e acesso lateral preservados; o conjunto acompanha a nova posição da escada.')
pair(root/cfg['previous_delivery']['root']/'renders/atual/planta-terreo.png',folder/'planta-terreo.png','antes-depois.png',
     ('ANTERIOR · revisão 09 arquivada','ATUAL · revisão 10'),
     'Contorno principal comum; fundos superiores alinhados à cozinha e ambientes redistribuídos.')
pair(root/cfg['upper_layout_source']['path'],folder/'planta-superior.png','comparacao-superior.png',
     ('CROQUI DO USUÁRIO · POSIÇÃO DOS QUARTOS','PROPOSTA · MEDIDAS E BANHEIROS PROVISÓRIOS'),
     'Distribuição do croqui ajustada ao contorno comum: fundos dos WCs e do quarto sobre a parede da cozinha.')
pair(root/'referencias-originais/escada1.webp',folder/'escada-superior.png','comparacao-escada.png',
     ('CHEGADA DA ESCADA · FOTO ORIGINAL','CHEGADA DA ESCADA · PROPOSTA'),
     'Lances colados: sete degraus iniciais, curva estimada e quatro finais; escala linear pendente de medição.')
rows=[('sala7.webp','sala-fundos.png','SALA PARA OS FUNDOS'),('sala4.webp','sala-frente.png','SALA PARA A FRENTE'),('sala1.webp','escada-acesso.png','ACESSO À ESCADA'),('cozinha1.webp','cozinha.png','COZINHA'),('cozinha2.webp','cozinha-reversa.png','COZINHA REVERSA'),('area3.webp','bar.png','CHURRASQUEIRA'),('lavanderia1.webp','lavanderia.png','LAVANDERIA'),('lavabo1.webp','lavabo.png','LAVABO')]
facades=[('exterior2.webp','fachada-frontal.png','FACHADA FRONTAL'),('exterior1.webp','fachada-obliqua.png','FACHADA OBLÍQUA')]
outputs=['comparacao-planta.png','antes-depois.png','comparacao-superior.png','comparacao-escada.png']
upper_rows=[('quartosuite1.webp','suite.png','SUÍTE · FRENTE ESQUERDA'),('quartobranco1.webp','quarto-frente.png','QUARTO FRENTE · ASSOCIAÇÃO DA FOTO INFERIDA'),('quartoazul2.webp','quarto-fundos.png','QUARTO FUNDOS · ASSOCIAÇÃO DA FOTO INFERIDA')]
for name,jobs,heading in [('comparacao-fotos.png',rows,'TÉRREO × FOTOS · a nova planta prevalece para a porta e a passagem'),('comparacao-quartos.png',upper_rows,'QUARTOS × FOTOS · posições do croqui; associação das fotos e dimensões estimadas'),('comparacao-fachada.png',facades,'FACHADA × FOTOS · vizinhas como contexto aproximado')]:
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
ground=read(folder/'planta-terreo.png');upper=read(folder/'planta-superior.png')
a=receipt['plan_views']['planta-terreo.png'];b=receipt['plan_views']['planta-superior.png']
assert all(abs(x-y)<1e-5 for x,y in zip(a['rotation_world'],b['rotation_world']))
scale=b['ortho_scale']/a['ortho_scale'];registered=Image.new('RGB',ground.size,ground.getpixel((10,10)))
upper=upper.resize((round(upper.width*scale),round(upper.height*scale)),Image.Resampling.LANCZOS)
pixels_per_m=ground.height/a['ortho_scale'];center=(ground.width/2+(b['position_world'][0]-a['position_world'][0])*pixels_per_m,ground.height/2+(a['position_world'][1]-b['position_world'][1])*pixels_per_m)
registered.paste(upper,(round(center[0]-upper.width/2),round(center[1]-upper.height/2)))
canvas=Image.new('RGB',(ground.width*2,ground.height+125),(27,32,35));draw=ImageDraw.Draw(canvas)
draw.text((20,14),'TÉRREO · MESMA ESCALA E ORIGEM',font=title,fill='white');draw.text((ground.width+20,14),'SUPERIOR · MESMA ESCALA E ORIGEM',font=title,fill='white')
draw.text((20,72),'Compare a projeção da escada, as paredes externas e a frente da casa nos dois pavimentos.',font=small,fill=(240,191,111))
canvas.paste(ground,(0,125));canvas.paste(registered,(ground.width,125));canvas.save(folder/'pavimentos-alinhados.png');outputs.append('pavimentos-alinhados.png')
alignment=json.loads((report_dir/'encaixe-pavimentos.json').read_text());assert alignment['all_passed']
contour=alignment['checks']['mesmo_contorno_do_corpo_principal']['detail']['superior']
blend=Image.blend(ground.convert('RGBA'),registered.convert('RGBA'),.45).convert('RGB')
overlay=Image.new('RGB',(ground.width,ground.height+155),(27,32,35));overlay.paste(blend,(0,155));draw=ImageDraw.Draw(overlay)
draw.text((20,12),'SOBREPOSIÇÃO DOS PAVIMENTOS',font=title,fill='white')
draw.text((20,58),'Linha branca: contorno comum das lajes do corpo principal.',font=small,fill=(240,191,111))
draw.text((20,100),'Pátio frontal e serviço/churrasqueira posteriores são anexos térreos.',font=small,fill='white')
def common_pixel(x,y):return (round(ground.width/2+(x-a['position_world'][0])*pixels_per_m),round(155+ground.height/2+(a['position_world'][1]-y)*pixels_per_m))
left,top=common_pixel(contour[0],contour[3]);right,bottom=common_pixel(contour[1],contour[2]);draw.rectangle((left,top,right,bottom),outline='white',width=5)
draw.text((left,max(160,top-34)),'FUNDOS: COZINHA = WCs + QUARTO',font=small,fill='white')
draw.text((left,bottom+12),'FRENTE COMUM NA FACHADA',font=small,fill='white')
overlay.save(folder/'pavimentos-sobrepostos.png');outputs.append('pavimentos-sobrepostos.png')
report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'revision':cfg['revision_number'],'blend_sha256':receipt['sha256'],'source':cfg['user_layout_source'],'scope':'Contorno comum e fundos coplanares com a cozinha; medidas e curva hipotéticas.','outputs':[str((folder/name).relative_to(root)) for name in outputs],'comparison_rows':[{'source':'referencias-originais/'+s,'render':'renders/atual/'+r} for s,r,_ in rows+facades+upper_rows]}
(report_dir/'comparacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('CURRENT_ATLAS_COMPLETE',len(outputs))
