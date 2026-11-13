"""Dados de redes, cenários e percursos 3D; sem dependência do Blender."""
import json
import math
from pathlib import Path

import residence07_geometry as geo

ROOT=geo.ROOT
CONFIG=ROOT/'config/residencia-07-estudos.json'
CFG=json.loads(CONFIG.read_text())


def roof_z(y):
    a=CFG['attic'];edge=a['roof_front_y'] if y<=a['ridge_y'] else a['roof_back_y']
    return a['eave_z']+(a['ridge_z']-a['eave_z'])*(y-edge)/(a['ridge_y']-edge)


def contains_rect(point,rect):
    return rect[0]<=point[0]<=rect[1] and rect[2]<=point[1]<=rect[3]


def pipe_points():
    """Rede conectada com alturas documentadas e percursos de estudo explícitos."""
    nodes={};edges=[]
    def node(key,xyz,system,kind='junction',source='Percurso 3D de estudo, posição em planta aproximada'):
        if key in nodes:raise ValueError(key)
        nodes[key]={'id':key,'xyz':list(xyz),'system':system,'kind':kind,'source':source}
        return key
    def edge(a,b,diameter,source='Traçado 3D de estudo'):
        assert nodes[a]['system']==nodes[b]['system']
        kind='junction' if math.dist(nodes[a]['xyz'],nodes[b]['xyz'])<.001 else 'segment'
        edges.append({'a':a,'b':b,'system':nodes[a]['system'],'nominal_diameter_m':diameter,'source':source,'geometry':kind})
    # Alimentação e distribuição, mantendo a caixa d'água sobre a escada.
    tx,ty=CFG['tank']['center_xy'];base=CFG['tank']['base_z']
    node('AF-REDE',(.20,-1.0,-.20),'cold','supply','HID04/HID05: entrada de água; posição de percurso aproximada')
    node('AF-SUBIDA',(.20,3.175,-.20),'cold');node('AF-MONTANTE',(.20,3.175,base+.90),'cold')
    node('AF-ENTRADA',(tx+.84,ty,base+.90),'cold','tank_inlet','HID04: entrada 25 mm')
    node('AF-SAIDA',(tx-.84,ty,base+.12),'cold','tank_outlet','HID04: alimentação 32 mm')
    node('AF-DISTRIB',(3.45,ty,base+.12),'cold')
    edge('AF-REDE','AF-SUBIDA',.025);edge('AF-SUBIDA','AF-MONTANTE',.025);edge('AF-MONTANTE','AF-ENTRADA',.025)
    edge('AF-SAIDA','AF-DISTRIB',.032)
    cold_by_level={}
    for level,z in [(1,2.7),(0,0)]:
        key=f'AF-PISO-{level}';node(key,(3.45,ty,z+2.35),'cold');edge('AF-DISTRIB' if level==1 else 'AF-PISO-1',key,.025);cold_by_level[level]=key
    water=[('cozinha',0,4.90,7.02,.60),('lavabo-lavatorio',0,4.35,3.08,.60),('lavabo-vaso',0,5.00,3.08,.20),
           ('banho-suite-lavatorio',1,.18,3.95,.60),('banho-suite-vaso',1,.18,4.82,.20),('banho-suite-chuveiro',1,.18,6.10,2.10),
           ('banho-social-lavatorio',1,1.83,3.95,.60),('banho-social-vaso',1,1.83,4.82,.20),('banho-social-chuveiro',1,1.83,6.10,2.10),
           ('lavanderia-tanque',0,4.40,10.20,1.0),('lavanderia-lavadora',0,5.60,10.20,1.0)]
    for name,level,x,y,height in water:
        z=level*2.7;top=f'AF-{name}-alto';elbow=f'AF-{name}-desvio';end=f'AF-{name}'
        node(top,(x,ty,z+2.35),'cold');node(elbow,(x,y,z+2.35),'cold')
        node(end,(x,y,z+height),'cold','outlet','HID05: altura do ponto transcrita; XY registrado pela arquitetura e pelas fotos para a lavanderia')
        edge(cold_by_level[level],top,.025);edge(top,elbow,.025);edge(elbow,end,.025)
    node('AQ-AQUECEDOR',(3.47,6.10,1.20),'hot','heater','HID05: aquecedor; posicionamento XY de estudo')
    for name,level,x,y,height in water:
        if 'vaso' in name or 'lavabo' in name or 'lavanderia' in name:continue
        z=level*2.7;key='AQ-'+name;mid=key+'-coluna';run=key+'-piso';turn=key+'-desvio'
        node(mid,(3.50,6.10,z+.48),'hot');node(run,(x,6.10,z+.48),'hot');node(turn,(x,y,z+.48),'hot')
        node(key,(x,y,z+height),'hot','outlet','HID05: pontos de água quente CPVC 22 mm')
        edge('AQ-AQUECEDOR',mid,.022);edge(mid,run,.022);edge(run,turn,.022);edge(turn,key,.022)
    # Esgoto: ramais sob o piso e coluna de queda; ventilação continua até a cobertura.
    for level,z in [(0,0),(1,2.7)]:
        node(f'ESG-COL-{level}',(3.05,6.70,z-.12),'sewer','stack','HID08: esgoto; coluna e percursos de estudo')
    edge('ESG-COL-1','ESG-COL-0',.10)
    node('ESG-CP',(1.10,8.05,-.32),'sewer','inspection','HID08: caixa de passagem; posição de estudo')
    node('ESG-SAIDA',(1.10,-1.0,-.50),'sewer','outfall');edge('ESG-COL-0','ESG-CP',.10);edge('ESG-CP','ESG-SAIDA',.10)
    for name,level,x,y,height in water:
        if 'chuveiro' in name:height=.02
        z=level*2.7;key='ESG-'+name;branch=key+'-ramal';turn=key+'-desvio'
        node(key,(x,y,z+(.18 if 'vaso' in name else min(height,.45))),'sewer','fixture','HID08/HID05: ponto sanitário; conexão 3D de estudo')
        node(branch,(x,y,z-.12),'sewer');node(turn,(3.05,y,z-.12),'sewer')
        d=.10 if 'vaso' in name else .05
        edge(key,branch,d);edge(branch,turn,d);edge(turn,f'ESG-COL-{level}',.10 if 'vaso' in name else .05)
    node('VENT-BASE',(3.05,6.70,2.58),'vent','stack','HID08: ventilação PVC 50 mm')
    node('VENT-TOPO',(3.05,6.70,6.35),'vent','vent_terminal','Terminal acima da cobertura: elevação de estudo')
    edge('VENT-BASE','VENT-TOPO',.05)
    # Circuitos de iluminação e tomadas: planos de conexão, sem simular caminhos existentes desconhecidos.
    for level,z in [(0,0),(1,2.7)]:
        qd=f'ELE-QD-{level}';node(qd,(3.48,3.90,z+1.50),'electric','panel','ELE04/05: quadro 1,50 m')
        trunk=f'ELE-TETO-{level}';node(trunk,(3.48,3.90,z+2.42),'electric');edge(qd,trunk,.025)
        lights=[(1.6,1.5),(1.6,4.3),(4.85,5.7),(4.8,2.7)] if level==0 else [(1.65,1.4),(4.85,.45),(4.85,5.7),(.9,4.8),(2.55,4.8),(3.85,3.3)]
        for i,(x,y) in enumerate(lights):
            a=f'ELE-L{level}-{i}-tr';b=f'ELE-L{level}-{i}'
            node(a,(x,3.90,z+2.42),'electric');node(b,(x,y,z+2.42),'electric','light','ELE04/05: iluminação de teto; centros registrados aproximadamente')
            edge(trunk,a,.025);edge(a,b,.025)
        sockets=[(.17,.9,.30),(.17,3.7,.30),(3.20,1.35,.30),(6.23,4.73,1.10),(6.23,5.7,1.10),(4.90,7.02,1.10),(6.23,6.4,2.20),(4.10,3.2,1.10)] if level==0 else [(.17,1.1,.30),(3.27,.3,.30),(6.23,.1,.30),(6.23,1.5,.30),(6.23,5.2,.30),(3.48,6.1,1.10),(.17,4.0,1.10),(1.83,4.0,1.10)]
        for i,(x,y,h) in enumerate(sockets):
            a=f'ELE-T{level}-{i}-alto';b=f'ELE-T{level}-{i}'
            node(a,(x,y,z+2.42),'electric');node(b,(x,y,z+h),'electric','socket','ELE04: tomadas a 0,30 / 1,10 / 2,20 m; XY interpretado na base')
            edge(trunk,a,.025);edge(a,b,.025)
        switches=[(2.64,.25),(3.50,4.45)] if level==0 else [(3.27,2.5),(3.75,1.95),(3.65,4.35)]
        for i,(x,y) in enumerate(switches):
            a=f'ELE-S{level}-{i}-alto';b=f'ELE-S{level}-{i}'
            node(a,(x,y,z+2.42),'electric');node(b,(x,y,z+1.10),'electric','switch','ELE04: interruptor a 1,10 m')
            edge(trunk,a,.025);edge(a,b,.025)
    edge('ELE-QD-0','ELE-QD-1',.032)
    # TV/telefone: rede independente de elétrica, em tom ciano.
    node('TV-ENTRADA',(.20,-.8,.10),'telecom','supply','TV-TEL04/05: entrada e rede; elevações do estudo')
    for level,z in [(0,0),(1,2.7)]:
        distro=f'TV-DS-{level}';node(distro,(3.54,3.90,z+1.45),'telecom','distribution','TV-TEL04/05: distribuidor; altura de estudo')
        edge('TV-ENTRADA' if level==0 else 'TV-DS-0',distro,.025)
        for i,(x,y) in enumerate([(.17,1.4),(3.2,1.4)] if level==0 else [(.17,1.5),(6.23,.5),(3.48,6.0)]):
            a=f'TV-{level}-{i}-alto';b=f'TV-{level}-{i}'
            node(a,(x,y,z+2.30),'telecom');node(b,(x,y,z+.30),'telecom','tv_phone','TV-TEL04/05: ponto TV/RJ11; altura 3D de estudo')
            edge(distro,a,.025);edge(a,b,.025)
    return {'nodes':list(nodes.values()),'edges':edges}


def views():
    result=[]
    def add(id,title,kind,systems=(),level=None,transparent=False,**camera):
        result.append(dict(id=id,title=title,kind=kind,systems=list(systems),level=level,transparent=transparent,**camera))
    base=geo.load()
    for v in base['views']:
        if v['mode'].startswith('structure'):add(v['id'],v['title'],'structure',mode=v['mode'],pos=v['pos'],target=v['target'],ortho=v['ortho'])
    for slug,label,systems in [('eletrica','Elétrica',['electric']),('hidraulica','Água fria e quente',['cold','hot']),('esgoto','Esgoto e ventilação',['sewer','vent']),('tv-telefone','TV / telefone',['telecom'])]:
        for level,suffix in [(0,'terreo'),(1,'superior')]:
            add(f'{slug}-{suffix}-transparente',label+' · '+suffix+' · paredes transparentes','services',systems,level,True,
                pos=[13,-12,15+level*2.7],target=[3.1,4.4,.9+level*2.7],ortho=16)
        add(slug+'-conjunto-transparente',label+' · dois pavimentos','services',systems,None,True,
            pos=[15,-18,14],target=[3.1,4.4,2.8],ortho=18)
    for level,suffix in [(0,'terreo'),(1,'superior'),(None,'conjunto')]:
        add('coordenadas-'+suffix+'-transparente','Instalações juntas · '+suffix,'services',['electric','cold','hot','sewer','vent','telecom'],level,True,
            pos=[15,-17,15 if level is None else 15+level*2.7],target=[3.1,4.4,2.8 if level is None else .9+level*2.7],ortho=18 if level is None else 16)
    add('reservatorio-3d','Reservatório de 1.000 L · alimentação e distribuição','tank',['cold'],None,True,pos=[11,-1,11],target=[4.75,3.2,5.4],ortho=7)
    return result


def output_path(view):
    if view['kind']=='structure':return geo.artifact_path(view['id'])
    return ROOT/CFG['services_renders']/view['id'].split('-')[0]/(view['id']+'.png')


def validate():
    graph=pipe_points();nodes={n['id']:n for n in graph['nodes']}
    assert len(nodes)==len(graph['nodes'])
    assert set(n['system'] for n in nodes.values())=={'cold','hot','sewer','vent','electric','telecom'}
    for e in graph['edges']:
        assert e['a'] in nodes and e['b'] in nodes
        assert nodes[e['a']]['system']==nodes[e['b']]['system']==e['system']
        assert 0<e['nominal_diameter_m']<=.1
    assert not contains_rect(CFG['tank']['center_xy'],CFG['attic']['floor_hole'])
    assert CFG['tank']['capacity_liters']==1000
    assert roof_z(CFG['tank']['center_xy'][1])>CFG['tank']['base_z']+CFG['tank']['display_height']+.50
    assert abs(roof_z(3)-9.4)<1e-7
    return {'nodes':len(nodes),'edges':len(graph['edges']),'views':len(views())}


if __name__=='__main__':print(json.dumps(validate(),ensure_ascii=False))
