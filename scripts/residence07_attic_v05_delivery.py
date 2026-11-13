"""Plantas, caderno e índice da revisão alinhada das escadas e do ático."""
import datetime as dt
import json
import re
from urllib.parse import unquote

import fitz
from PIL import Image

import residence07_geometry as geo
import residence07_attic_v05_data as data
import residence07_attic_v05_views as views
from residence07_plans import Sheet

ROOT=data.ROOT;CFG=data.CFG;OUT=ROOT/CFG['render_directory'];REPORT=ROOT/CFG['report_directory']


def rect(s,r,fill,stroke='#607165',width=1):
    a,b,c,d=r;s.poly([s.xy(p) for p in [(a,c),(b,c),(b,d),(a,d)]],fill,stroke,width)


def label(s,x,y,text,size=15,color='#354a40'):s.text(*s.xy((x,y)),text,size,color,anchor='middle')


def footer(s,lines):
    s.line([(75,1450),(1325,1450)],'#b9c1b5')
    for i,line in enumerate(['PROPOSTA V05 · RESIDÊNCIA 07 · COTAS EM METROS',*lines]):s.text(75,1490+i*35,line,17,'#526157')


def save(s,name):
    s.items.append('</svg>');p=OUT/'04-plantas'/(name+'.svg');p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(s.items))
    with fitz.open(p) as src:pdf=src.convert_to_pdf()
    with fitz.open('pdf',pdf) as doc:doc.save(p.with_suffix('.pdf'),deflate=True);doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p.with_suffix('.png'))
    return p.with_suffix('.pdf')


def draw_stair(s,fill='#e5d3b8',color='#9d652f'):
    for step in data.steps():
        p=step['polygon'];s.poly([s.xy(v) for v in p],fill,color,1.5)
        label(s,sum(x for x,y in p)/len(p),sum(y for x,y in p)/len(p),str(step['index']),10)


def alignment():
    s=Sheet('Escadas · mesmo alinhamento','Pavimento superior +2,70 m · a nova U repete exatamente o XY da existente');s.scale=105;s.ox=360;s.oy=1090
    cfg=geo.load();s.poly([s.xy(p) for p in cfg['levels'][1]['outline']],'#ebe6d9','#9ba69a',1)
    for w in cfg['walls']:
        if w['level']!=1:continue
        for a,b,z0,z1 in geo.wall_cells(w,2.55):
            if z0<1.2<z1:s.poly([s.xy(p) for p in geo.wall_polygon(w,a,b)],'#59675e')
    # Contornos de duas cores coincidentes comprovam a sobreposição na planta.
    for p in geo.stair_polygons(cfg):s.poly([s.xy(v) for v in p],'#bed0c3','#52786c',5)
    draw_stair(s)
    s.line([s.xy(p) for p in CFG['stair']['arrival_path']],'#cf7628',4)
    label(s,2.75,2.65,'HALL · 0,65 m NOMINAL',13)
    label(s,1.75,.6,'SUÍTE PRESERVADA',13);label(s,4.8,.6,'QUARTO FRONTAL PRESERVADO',12)
    s.dimension([4.1,2.15],[6.25,2.15],'2,15 · mesma projeção',55)
    s.dimension([6.25,2.15],[6.25,4.15],'2,00',55)
    s.dimension([0,-1.2],[6.35,-1.2],'6,35 · base documental',55)
    s.text(75,1310,'Verde: escada existente. Ocre: nova escada. Os 16 contornos XY coincidem.',18)
    s.text(75,1350,'O percurso no hall liga os eixos Y=2,60 e Y=3,70 m. Vidro/guarda antigo retirado.',18)
    s.text(75,1390,'A divisória e a porta frontais voltam à base atual; os dois quartos ficam preservados.',18)
    footer(s,['16 espelhos de 16,875 cm; piso reto de 25 cm; largura dos lances de 90 cm.',
              'Deslocamento da nova escada: somente Z=+2,70 m, sem espelhamento ou translação em XY.',
              'Hall nominal de 65 cm e dimensionamento resistente precisam de compatibilização.'])
    return save(s,'escadas-alinhadas')


def tank_circle(s,xy,fill,stroke,dash=None):
    x,y=s.xy(xy);r=.9*s.scale;extra=f' stroke-dasharray="{dash}"' if dash else ''
    s.items.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"{extra}/>')


def attic(height_map=False):
    s=Sheet('Ático · alturas após o forro' if height_map else 'Ático · planta atualizada','Nova área técnica à esquerda · escadas alinhadas · cota do piso +5,40 m');s.scale=105;s.ox=360;s.oy=1100
    for r in [[0,3.3,-1.2,6.5],[3.3,6.35,-1.2,7.2]]:rect(s,r,'#e8dfca')
    if height_map:
        for ix in range(61):
            x=.2+ix*.1
            for iy in range(84):
                y=-1.15+iy*.1
                if data.on_floor(x,y):rect(s,[x-.05,x+.05,y-.05,y+.05],'#8ab799' if data.ceiling_z(x,y)-5.4>=2.1 else '#dcb88b','none')
    for h in CFG['stair']['floor_holes']:rect(s,h,'#faf9f4','#607165',2)
    draw_stair(s)
    rect(s,CFG['tank']['technical_room'],'#dce7df','#71867b',2);tank_circle(s,CFG['tank']['center_xy'],'#8db6c9','#456c80')
    label(s,1.8,3.175,'1.000 L',16);label(s,1.7,4.6,'ÁREA TÉCNICA TRANSFERIDA',12)
    s.line([s.xy((3.25,2.62)),s.xy((3.25,3.52))],'#faf9f4',7)
    label(s,3.65,2.6,'SAÍDA',11);label(s,1.6,1.0,'ESTAR',15);label(s,1.7,5.7,'ESCRITÓRIO',15)
    s.dimension([4.1,2.15],[6.25,2.15],'2,15 · vão em L',55)
    s.dimension([6.25,2.15],[6.25,4.15],'2,00',55)
    s.dimension([3.3,2.0],[4.1,2.0],'0,80 · faixa livre',100)
    s.dimension([0,-1.2],[6.35,-1.2],'6,35 · base documental',55)
    s.text(75,1310,'Verde: altura ≥ 2,10 m; areia: menor. Desconto de 8 cm de cobertura + 15 cm de forro.' if height_map else 'O vão frontal da v04 foi fechado. O novo vão reproduz o L da escada existente.',18)
    s.text(75,1350,'Altura livre máxima acabada: 3,77 m. Mapa em células de 10 cm.' if height_map else 'Caixa em X=1,80 / Y=3,175 m; base +5,45 m e volume externo ilustrativo.',18)
    s.text(75,1390,'A faixa de 2,10 m é referência geométrica, sem certificação legal de ocupação.' if height_map else 'Estar na frente, escritório atrás e armários baixos ajustados à cobertura.',18)
    footer(s,['Mansardas centralizadas e prolongadas até a cumeeira principal preservadas da v03.',
              'Posição nova da caixa e redes de conexão são propostas; apoios e cargas não dimensionados.',
              'A escala da base vem das pranchas; o estado físico e as medidas executadas não foram medidos.'])
    return save(s,'mapa-alturas-forro' if height_map else 'planta-atico-cotada')


def tank_relocation():
    s=Sheet('Caixa · mudança de posição','Planta ampliada · manter a cota da base e retirar o reservatório da região da escada');s.scale=150;s.ox=230;s.oy=1170
    rect(s,[0,6.35,1.8,4.6],'#eee9dc','#9ba69a');draw_stair(s)
    rect(s,CFG['tank']['technical_room'],'#dce7df','#71867b',2)
    tank_circle(s,CFG['tank']['old_center_xy'],'none','#a77f68','9 5');tank_circle(s,CFG['tank']['center_xy'],'#8db6c9','#456c80')
    label(s,1.8,3.175,'NOVA · 1.000 L',16);label(s,5.35,3.175,'POSIÇÃO ANTERIOR',12)
    s.dimension([1.8,3.175],[5.35,3.175],'3,55 · deslocamento em X',-180)
    s.dimension([0,1.8],[1.8,1.8],'1,80 · novo centro X',60)
    s.text(75,365,'Centro anterior: X=5,35 m. Novo centro: X=1,80 m. Y=3,175 m preservado.',19)
    s.text(75,405,'A base permanece em +5,45 m; a caixa não foi elevada.',21,weight='bold')
    s.text(75,1310,'O centro novo fica fora da projeção dos dois lances; capacidade mantida em 1.000 L.',18)
    s.text(75,1350,'A forma externa de Ø1,80 m × 1,15 m é ilustrativa, sem fabricante confirmado.',18)
    s.text(75,1390,'A transferência da carga e os novos percursos hidráulicos exigem projeto específico.',18)
    footer(s,['Linha tracejada: posição original usada nas revisões anteriores. Azul: nova posição proposta.',
              'A laje de apoio e a estrutura sob a caixa não foram dimensionadas.',
              'Na vista lateral, a caixa pode aparecer alinhada em profundidade; conferir esta planta.'])
    return save(s,'reposicionamento-caixa')


def section(audit):
    s=Sheet('Corte · alturas da escada','Perfis desenvolvidos das duas U · mesmo trajeto em XY, deslocado em Z');s.scale=145;s.ox=230;s.oy=1190
    for base,color in [(0,'#b5cbbb'),(2.7,'#dfc8a8')]:
        for i in range(16):
            x=i*.36;z=base+(i+1)*.16875;rect(s,[x,x+.36,z-.16875,z],color)
            label(s,x+.18,z-.08,str(i+1),10)
    s.dimension([0,0],[0,2.7],'2,70 · existente',-60);s.dimension([0,2.7],[0,5.4],'2,70 · nova',-60)
    for z,text in [(0,'TÉRREO +0,00'),(2.7,'SUPERIOR +2,70'),(5.4,'ÁTICO +5,40')]:
        s.line([s.xy((0,z)),s.xy((5.76,z))],'#7e8d80',1,'6 4');label(s,5.25,z+.1,text,13)
    minimum=min(r['minimum_m'] for r in audit['stair_clearance']);oldmin=min(r['minimum_m'] for r in audit['existing_stair_clearance'])
    s.text(75,1310,f'Folga mínima amostrada na nova U: {minimum:.2f} m. Na existente: {oldmin:.2f} m.'.replace('.',','),19)
    s.text(75,1350,'O menor ponto é sob o patamar retido, nos dois primeiros pisos; forro também conferido.',18)
    s.text(75,1390,'Este perfil desdobra o percurso. O espaçamento horizontal do gráfico não mede a escada.',18)
    footer(s,['Forro com reserva de 15 cm abaixo da cobertura; altura livre máxima do ático: 3,77 m.',
              'Alturas medidas na geometria salva; raios incluem lajes, paredes e a nova escada acima.',
              'As folgas não substituem a verificação das dimensões executadas ou de conformidade legal.'])
    return save(s,'corte-alturas-escadas')


def book(model,plans,panels):
    doc=fitz.open();page=doc.new_page(width=842,height=680);page.insert_textbox(fitz.Rect(40,40,802,125),'RESIDÊNCIA 07 / ÁTICO V05\nEscadas alinhadas e caixa lateral',fontsize=26)
    notes=CFG['notes'][:3]+CFG['notes'][5:8]+CFG['notes'][-1:]
    notes[-1]=notes[-1].replace('A base documental e os projetos anteriores são preservados.','A base documental e os modelos originais são preservados. As propostas de acesso descartadas foram excluídas a pedido do usuário.')
    page.insert_textbox(fitz.Rect(40,155,802,640),'\n\n'.join(notes),fontsize=11.5,lineheight=1.3)
    for p in plans:
        with fitz.open(p) as part:doc.insert_pdf(part)
    images=[(ROOT/j['file'],j['title']) for j in model['jobs'] if j['group']=='main']+[(p,p.stem) for p in panels]
    for path,title in images:
        page=doc.new_page(width=842,height=680);page.insert_text((30,32),title,fontsize=15);page.insert_image(fitz.Rect(25,52,817,628),filename=str(path),keep_proportion=True)
        page.insert_textbox(fitz.Rect(30,643,812,674),'Proposta visual. Caixa transferida à esquerda e U alinhada à existente. Hall nominal 65 cm; apoios, cargas e execução a compatibilizar.',fontsize=9)
    p=OUT/'00-cadernos/caderno-atico-v05.pdf';p.parent.mkdir(parents=True,exist_ok=True);doc.save(p,deflate=True,garbage=4);doc.close()


def index(model,audit):
    minimum=min(r['minimum_m'] for r in audit['stair_clearance'])
    text=f'''# Ático v05 — escadas sobrepostas e caixa à esquerda

Atende à última decisão: **os dois lances novos ficam exatamente sobre os existentes**, com a caixa movida para liberar o acesso. Os 16 pisos repetem o mesmo XY, com deslocamento apenas vertical de +2,70 m. A caixa mantém base +5,45 m e Y=3,175 m; muda de X=5,35 para X=1,80 m.

- [Desenho completo das escadas e caixa](07-escadas/escada-completa-caixa.png), [PDF do desenho](07-escadas/escada-completa-caixa.pdf) e [lateral atualizada](07-escadas/01-vistas/05-lateral-patamares.png).
- [Girar em 360°](07-escadas/galeria.html), [GIF animado](07-escadas/giro-360.gif), [seis ângulos](07-escadas/painel-seis-angulos.jpg) e [PDF das seis vistas](07-escadas/escadas-seis-angulos.pdf).
- [Galeria do ático](galeria.html), [caderno de 25 páginas](00-cadernos/caderno-atico-v05.pdf) e [Blender editável](../../{model['blend']}).
- [Planta das escadas alinhadas](04-plantas/escadas-alinhadas.pdf), [planta do ático](04-plantas/planta-atico-cotada.pdf), [mudança da caixa](04-plantas/reposicionamento-caixa.pdf), [alturas sob o forro](04-plantas/mapa-alturas-forro.pdf) e [corte das escadas](04-plantas/corte-alturas-escadas.pdf). Há SVG e PNG de cada desenho na mesma pasta.
- [Relatório de conferência](../../{CFG['report_directory']}/RELATORIO.md).

## Medidas e implantação

| Elemento | Situação na proposta |
| --- | --- |
| Escadas inferior e nova | 16 pisos cada, com projeção XY idêntica |
| Cotas de piso | Térreo +0,00; superior +2,70; ático +5,40 m |
| Espelho / piso reto / largura | 16,875 / 25 / 90 cm |
| Vão do ático | Em L, repetindo o existente; pequeno patamar sobre dois pisos retido |
| Folga mínima nova U | {minimum:.2f} m amostrados, sob o patamar retido |
| Caixa de 1.000 L | Nova posição proposta X=1,80 / Y=3,175 / base Z=5,45 m |
| Mudança da caixa | 3,55 m para a esquerda em X, sem elevar a base |
| Caixa até o forro | {audit['tank_ceiling_clearance_m']:.2f} m mínimos na amostragem |
| Forro / altura máxima | Reserva vertical de 15 cm; 3,77 m de altura livre máxima |
| Quarto frontal e dos fundos | Preservados; a subida fica junto ao hall |

A ligação pelo quarto frontal de 60 cm da v04 foi eliminada. O hall nominal de 65 cm já existente continua como restrição da base; esta revisão não certifica sua conformidade executiva. A divisória e a porta frontais foram restauradas a partir do modelo atual, e a escada existente foi preservada. O vidro/guarda antigo foi retirado; a nova subida e suas proteções ocupam esse trecho.

A área técnica vai para o lado esquerdo do ático. A caixa e suas conexões esquemáticas foram deslocadas em X, mantendo forma, capacidade e cota de base. A posição nova é proposta; não corresponde à posição original de HID04. O seu volume externo continua ilustrativo. Apoios, transferência de carga, novos percursos hidráulicos e manutenção precisam de dimensionamento específico.

O vão antigo frontal foi fechado e a laje foi refeita com o recorte em L. Sobre os dois primeiros pisos há uma porção de laje retida, como na base existente; a menor folga de aproximadamente 2,21 m foi medida nesse ponto. A conferência também inclui a escada inferior sob a nova, paredes e forro. Os seis ângulos e o giro usam a mesma geometria, sem deslocamento artificial dos lances.

O estar fica na frente e o escritório na faixa posterior, liberando a nova sala técnica. Armários baixos foram ajustados para permanecer abaixo do forro. Mansardas centralizadas, telhados até a cumeeira principal, forro, fundos atuais e base documental são preservados. As propostas anteriores de acesso foram excluídas a pedido do usuário; somente a v05 permanece disponível.
'''
    (OUT/'LEIA-ME.md').write_text(text)
    p=ROOT/CFG['output_blend'];(p.parent/'LEIA-ME.md').write_text('# Ático v05\n\n[Entrega organizada](../../'+CFG['render_directory']+'/LEIA-ME.md).\n\nCenas ATC5_; Num 0 mostra a câmera. Unidades em metros. As cenas giro-00..23 permitem reproduzir o giro, e as cenas 01..06 isolam escadas e caixa.\n')
    (OUT/'07-escadas/LEIA-ME.md').write_text('# Escadas alinhadas / v05\n\n[Girar em 360°](galeria.html) · [GIF](giro-360.gif) · [desenho com medidas](escada-completa-caixa.png) · [seis vistas](painel-seis-angulos.jpg) · [PDF](escadas-seis-angulos.pdf).\n\nOs dois lances repetem exatamente a posição XY dos inferiores. A caixa foi transferida à esquerda. A vista lateral comprime a profundidade; a planta e as vistas oblíquas mostram a caixa fora da escada. [Índice do ático](../LEIA-ME.md).\n')


def verify(model,plans):
    audit=json.loads((REPORT/'validacao-completa.json').read_text());rows=json.loads((REPORT/'renders.json').read_text());checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('modelo e renders auditados',audit['all_passed'] and audit['renders_required'] and audit['blend_sha256']==geo.sha(ROOT/model['blend']))
    check('48 imagens e quadros',{r['id'] for r in rows}=={j['id'] for j in model['jobs']} and len(rows)==48)
    for j in model['jobs']:
        with Image.open(ROOT/j['file']) as im:check('PNG '+j['id'],im.size==tuple(j['resolution']) and im.format=='PNG');im.verify()
    for p in plans:
        check('SVG e PNG '+p.stem,p.with_suffix('.svg').exists() and p.with_suffix('.png').exists())
        with fitz.open(p) as doc:check('PDF '+p.stem,len(doc)==1 and bool(doc[0].get_text()))
    with fitz.open(OUT/'00-cadernos/caderno-atico-v05.pdf') as doc:check('caderno 25 páginas',len(doc)==25)
    with fitz.open(OUT/'07-escadas/escadas-seis-angulos.pdf') as doc:check('PDF de seis ângulos e painel',len(doc)==7)
    with Image.open(OUT/'07-escadas/giro-360.gif') as im:check('GIF de 24 quadros',im.n_frames==24 and im.info['loop']==0)
    for p in [OUT/'LEIA-ME.md',OUT/'galeria.html',OUT/'07-escadas/galeria.html',OUT/'07-escadas/LEIA-ME.md']:
        txt=p.read_text();links=re.findall(r'\]\(([^)]+)\)',txt) if p.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',txt)
        check('links '+str(p.relative_to(OUT)),all((p.parent/unquote(link.split('#')[0])).exists() for link in links))
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'checks':checks,'all_passed':all(c['passed'] for c in checks),'native_checks':len(audit['checks']),'browser_verification':'PENDING','scope':'Entrega geométrica e visual; hall existente e estrutura/apoios/redes definitivas não dimensionados.'}
    (REPORT/'validacao-entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if not result['all_passed']:raise RuntimeError([c for c in checks if not c['passed']])
    return result


def report(model,audit,result,template):
    minimum=min(r['minimum_m'] for r in audit['stair_clearance']);oldmin=min(r['minimum_m'] for r in audit['existing_stair_clearance'])
    text=f'''# Ático v05 / conferência da revisão

Conferência em {result['timestamp_utc']}: {result['native_checks']} verificações nativas e {len(result['checks'])} da entrega passaram. O escopo é geométrico e visual; dimensionamento estrutural e execução permanecem fora do escopo verificado.

| Obrigação | Recibo observado | Situação |
| --- | --- | --- |
| Dois lances exatamente sobre os inferiores | 16 pares de pisos, comparação nativa de XY e diferença Z=2,70 m | VERIFICADO |
| Caixa liberando a escada | Centro movido de X=5,35 para X=1,80, Y e Z preservados; comparação com a biblioteca sem acesso descartado | VERIFICADO |
| Forma e capacidade da caixa | Mesma malha e 1.000 L; conexões transladadas -3,55 m em X | VERIFICADO no modelo |
| Altura sob patamar e entre escadas | Nova U mínima {minimum:.3f} m; existente {oldmin:.3f} m | VERIFICADO por amostragem |
| Altura caixa/forro | 81 raios, mínimo {audit['tank_ceiling_clearance_m']:.3f} m | VERIFICADO para caixa ilustrativa |
| Quarto frontal e posterior preservados | Arquitetura comparada independentemente com o modelo atual; somente quatro peças do guarda removidas | VERIFICADO |
| Mansardas, forro e fundos preservados | Malhas e transformações reconciliadas com a biblioteca sem acesso descartado | VERIFICADO |
| Mobiliário compatível com nova área técnica | Reposicionamento e conferência de volumes/altura sob forro | VERIFICADO no estudo |
| Atualizar documentação e vistas | 18 imagens gerais, seis isoladas, 24 quadros de giro, cinco plantas, GIF e caderno de 25 páginas | VERIFICADO |
| Apoios, cargas, medidas executadas e redes definitivas | Sem cálculo resistente ou levantamento presencial | DESCONHECIDOS / NÃO DIMENSIONADOS |

Os dois lances novos usam os mesmos polígonos dos existentes, sem espelhamento, translação horizontal ou mudança de escala. O vão em L é refeito no ático; a pequena porção de laje sobre os dois primeiros pisos permanece. A altura livre é verificada incluindo essa laje, forro e paredes, e também entre a escada existente e os corpos da nova U. A ligação pelo quarto frontal da v04 deixa de existir e a divisória/porta original é restaurada. O hall nominal de 65 cm permanece como limitação herdada.

A caixa foi movida lateralmente com autorização expressa do usuário. Sua base não foi elevada e a nova posição não é apresentada como existente. Os percursos hidráulicos desenhados são esquemáticos da proposta; o apoio e a transferência da carga de 1.000 L não foram dimensionados. As cotas externas do reservatório continuam ilustrativas, sem identificação do fabricante. A área técnica foi refeita à esquerda, com estar na frente, escritório atrás e armários baixos ajustados.

O forro conserva a reserva vertical de 15 cm, sob os 8 cm representados da cobertura, mantendo 3,77 m de altura máxima acabada. O mapa de 2,10 m usa a face acabada; não é certificação legal de ocupação. As propostas anteriores de acesso foram excluídas a pedido do usuário. A casa atual e a biblioteca de cobertura/forro sem acesso descartado foram preservadas.
'''
    (REPORT/'RELATORIO.md').write_text(text)
    p=REPORT/'checkpoint.json';c=json.loads(p.read_text());c.update(status='VISUAL_DELIVERY_READY_BROWSER_PENDING',pending=None,remaining=['verificar visor em navegador','atualizar índices principais'],verification='validacao-entrega.json',results={'native_checks':result['native_checks'],'delivery_checks':len(result['checks']),'main_views':18,'isolated_views':6,'orbit_frames':24,'plans':5,'book_pages':25},template={'file':str(template.relative_to(ROOT)),'sha256':geo.sha(template)});p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')


def main():
    model=json.loads((REPORT/'modelo.json').read_text());audit=json.loads((REPORT/'validacao-completa.json').read_text());assert audit['all_passed']
    plans=[alignment(),attic(),attic(True),tank_relocation(),section(audit)]
    panels,template=views.generate(model,audit);book(model,plans,panels)
    (REPORT/'RELATORIO.md').write_text('# Ático v05\n\nConferência final da entrega em andamento. A geometria está registrada em validacao-completa.json.\n')
    index(model,audit);result=verify(model,plans);report(model,audit,result,template)
    artifacts=[{'file':str(p.relative_to(ROOT)),'sha256':geo.sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()]
    (REPORT/'manifesto.json').write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'artifacts':artifacts,'delivery_generators':{str(p.relative_to(ROOT)):geo.sha(p) for p in [ROOT/'scripts/residence07_attic_v05_delivery.py',ROOT/'scripts/residence07_attic_v05_views.py']}},ensure_ascii=False,indent=2)+'\n')
    print('ATC5_DELIVERY_OK',len(result['checks']),'verificações;',len(artifacts),'artefatos')


if __name__=='__main__':main()
