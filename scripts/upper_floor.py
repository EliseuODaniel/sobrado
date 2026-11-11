"""Superior: quartos localizados pelo usuário; banheiros e dimensões provisórios."""
import math
import house_geometry as h
import blender_primitives as g


def build(cfg):
    rooms={r['id']:r for r in cfg['rooms']}
    doors={spec['id']:spec for spec in cfg['upper_layout']['doors']}
    suite=rooms['suite']['bounds'];front=rooms['quarto_branco']['bounds'];rear=rooms['quarto_azul']['bounds'];wc=rooms['banho_social']['bounds']
    split=suite[1];north=suite[3];back=cfg['estimated_dimensions_m']['upper_back_y'];width=cfg['estimated_dimensions_m']['width']
    def portal(wall_start,wall_end,key,label,angle):
        length=math.dist(wall_start,wall_end);ux=(wall_end[0]-wall_start[0])/length;uy=(wall_end[1]-wall_start[1])/length
        distances=sorted((point[0]-wall_start[0])*ux+(point[1]-wall_start[1])*uy for point in [doors[key]['a'],doors[key]['b']])
        spec=h.opening(*distances,'Porta superior '+label,'door',top=2.05);spec['open_angle_deg']=angle;return spec
    def partition(name,a,b,key=None,label=None,angle=75):
        h.wall(name,a,b,1,'Superior',[portal(a,b,key,label,angle)] if key else [])
    partition('Divisória quartos frente',(split,suite[2]),(split,front[3]))
    partition('Suíte porta lateral para hall',(split,north),(split,front[3]),'suite','suíte',-75)
    partition('WC suíte acesso privativo — proposta',(wc[0],north),(0,north),'banho_suite','banho suíte')
    partition('WC social limite com suíte — proposta',(wc[0],north),(split,north))
    partition('Divisão entre WCs — proposta',(wc[0],north),(wc[0],back))
    partition('WC social porta para hall — proposta',(split,north),(split,back),'banho_social','banho social')
    partition('Quarto frente limite hall',(split,front[3]),(width,front[3]),'quarto_branco','quarto frente',-75)
    partition('Quarto fundos frente',(split,rear[2]),(width,rear[2]),'quarto_azul','quarto fundos')
    for key in ['banho_suite','banho_social']:
        p,c=h.room_parent(key);x0,x1,y0,y1=rooms[key]['bounds']
        h.box('Piso WC hipótese '+key,((x0+x1)/2,(y0+y1)/2,.008),(x1-x0-.15,y1-y0-.15,.012),'Area desconhecida',c,.002,p)
        h.box('Gabinete '+key,(x0+.35,y0+.55,.42),(.48,.65,.84),'Armario branco',c,.006,p)
        h.box('Bancada '+key,(x0+.35,y0+.55,.86),(.52,.68,.04),'Granito preto',c,.006,p)
        g.sphere('Cuba '+key,(x0+.35,y0+.55,.91),(.16,.22,.05),'Louca branca',c,p)
        g.sphere('Vaso '+key,((x0+x1)/2,y1-.95,.38),(.22,.30,.13),'Louca branca',c,p)
        h.box('Caixa vaso '+key,((x0+x1)/2,y1-.69,.55),(.33,.16,.42),'Louca branca',c,.02,p)
        h.box('Box '+key,((x0+x1)/2,y1-.62,1.02),(x1-x0-.15,.016,2.04),'Vidro transparente',c,.002,p)
    p,c=h.room_parent('suite')
    bed=h.bed('Cama suíte',(1.15,0,0),1.40,1.95,c,p);bed.rotation_euler.z=math.pi/2
    h.box('Armário suíte',(.35,1.8,1.25),(.5,1.9,2.5),'Madeira bar',c,.008,p)
    h.box('Cabeceira suíte',(.13,0,.85),(.08,1.55,.75),'Lencol',c,.025,p)
    h.box('Painel TV suíte',(2.70,0,1.5),(.025,.85,.7),'Madeira bar',c,.003,p)
    h.box('TV suíte',(2.67,0,1.5),(.03,.65,.4),'TV desligada',c,.005,p)
    p,c=h.room_parent('quarto_branco')
    h.bed('Cama quarto frente',(4.75,.15,0),.88,1.9,c,p)
    h.box('Armário quarto frente',(3.22,-.15,1.25),(.6,2.25,2.5),'Armario branco',c,.008,p)
    p,c=h.room_parent('quarto_azul')
    h.bed('Beliche quarto fundos',(4.85,back-1.25,0),.88,1.9,c,p,True)
    h.box('Escrivaninha quarto fundos',(3.13,back-1.25,.74),(.48,1.6,.04),'Armario branco',c,.005,p)
    h.box('Parede azul acabamento',(2.881,back-1.25,1.35),(.012,1.8,2.7),'Parede azul',c,.001,p)
    h.box('TV quarto fundos',(2.90,back-1.25,1.3),(.025,.65,.4),'TV desligada',c,.004,p)
    h.collection('Teto_Superior',g.C['Superior'])
    h.box('Teto superior — oculto nas plantas',(width/2,(cfg['estimated_dimensions_m']['upper_front_y']+back)/2,2.77),(width,back-cfg['estimated_dimensions_m']['upper_front_y'],.14),'Parede branca','Teto_Superior',.002,h.FLOORS[1])


def annotations(cfg):
    for r in cfg['rooms']:
        if r['level']!=1:continue
        x0,x1,y0,y1=r['bounds'];bath=r['id'].startswith('banho')
        name={'suite':'SUÍTE','quarto_branco':'QUARTO FRENTE','quarto_azul':'QUARTO FUNDOS','banho_suite':'WC SUÍTE?','banho_social':'WC SOCIAL?'}[r['id']]
        width=x1-x0-.15;depth=y1-y0-.15
        label=name+f'\n≈ {width:.2f} × {depth:.2f} m'
        if bath:label+='\nHIPÓTESE'
        h.text('Rótulo superior '+r['id'],label,((x0+x1)/2,(y0+y1)/2,6.0),.13 if bath else .15,'Cotas_Superior','Hipotese tinta' if bath else 'Cotas tinta')
    h.text('Superior aviso','PROPORÇÕES DO CROQUI • MEDIDAS APROXIMADAS',(2.8,cfg['estimated_dimensions_m']['upper_back_y']+.55,3.0),.14,'Cotas_Superior','Hipotese tinta')
    h.text('Circulação superior','CIRCULAÇÃO',(3.45,cfg['layout']['stairs']['first_y']-.25,6.0),.13,'Cotas_Superior')
    h.text('Varanda superior','VARANDA',(1.4,-1.26,6.0),.13,'Cotas_Superior')
    s=cfg['layout']['stairs']
    for body,loc in [('7 DEGRAUS',(4.48,s['first_y'],6.0)),('4 DEGRAUS',(4.70,s['return_y'],6.0)),(f"CURVA\n{s['turn_steps']} ESTIMADOS",(5.25,(s['first_y']+s['return_y'])/2,6.0))]:
        h.text('Contagem '+body,body+'\nTRECHO SOB O HALL' if body=='7 DEGRAUS' else body,loc,.10,'Cotas_Superior','Hipotese tinta' if 'CURVA' in body else 'Cotas tinta')
    g.rod('Subida primeiro lance',(4.02,s['first_y']+.22,5.95),(4.89,s['first_y']+.22,5.95),.012,'Cotas tinta','Cotas_Superior')
    g.rod('Subida lance final',(4.94,s['return_y']-.29,5.95),(4.45,s['return_y']-.29,5.95),.012,'Cotas tinta','Cotas_Superior')
