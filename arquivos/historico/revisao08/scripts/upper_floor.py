"""Superior: quartos localizados pelo usuário; banheiros e dimensões provisórios."""
import math
import house_geometry as h
import blender_primitives as g


def build(cfg):
    rooms={r['id']:r for r in cfg['rooms']}
    def portal(a,b,key,angle):
        spec=h.opening(a,b,'Porta superior '+key,'door',top=2.05)
        spec['open_angle_deg']=angle
        return spec
    h.wall('Divisória quartos frente',(2.8,-.8),(2.8,2.79),1,'Superior')
    h.wall('Suíte porta lateral para hall',(2.8,3.8),(2.8,2.79),1,'Superior',[portal(.075,.875,'suíte',-75)])
    h.wall('WC suíte acesso privativo — proposta',(1.4,3.8),(0,3.8),1,'Superior',[portal(.10,.85,'banho suíte',75)])
    h.wall('WC social limite com suíte — proposta',(1.4,3.8),(2.8,3.8),1,'Superior')
    h.wall('Divisão entre WCs — proposta',(1.4,3.8),(1.4,6.95),1,'Superior')
    h.wall('WC social porta para hall — proposta',(2.8,3.8),(2.8,6.95),1,'Superior',[portal(.10,.85,'banho social',75)])
    h.wall('Quarto frente limite hall',(2.8,2.79),(5.6,2.79),1,'Superior',[portal(.2,1.0,'quarto frente',-75)])
    h.wall('Quarto fundos frente',(2.8,4.65),(5.6,4.65),1,'Superior',[portal(.075,.875,'quarto fundos',75)])
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
    bed=h.bed('Cama suíte',(1.15,.30,0),1.40,1.95,c,p);bed.rotation_euler.z=math.pi/2
    h.box('Armário suíte',(.35,2.4,1.25),(.5,1.9,2.5),'Madeira bar',c,.008,p)
    h.box('Cabeceira suíte',(.13,.30,.85),(.08,1.55,.75),'Lencol',c,.025,p)
    h.box('Painel TV suíte',(2.70,.30,1.5),(.025,.85,.7),'Madeira bar',c,.003,p)
    h.box('TV suíte',(2.67,.30,1.5),(.03,.65,.4),'TV desligada',c,.005,p)
    p,c=h.room_parent('quarto_branco')
    h.bed('Cama quarto frente',(4.75,.15,0),.88,1.9,c,p)
    h.box('Armário quarto frente',(3.22,-.15,1.25),(.6,2.25,2.5),'Armario branco',c,.008,p)
    p,c=h.room_parent('quarto_azul')
    h.bed('Beliche quarto fundos',(4.85,5.8,0),.88,1.9,c,p,True)
    h.box('Escrivaninha quarto fundos',(3.13,5.8,.74),(.48,1.6,.04),'Armario branco',c,.005,p)
    h.box('Parede azul acabamento',(2.881,5.8,1.35),(.012,1.8,2.7),'Parede azul',c,.001,p)
    h.box('TV quarto fundos',(2.90,5.8,1.3),(.025,.65,.4),'TV desligada',c,.004,p)
    h.collection('Teto_Superior',g.C['Superior'])
    h.box('Teto superior — oculto nas plantas',(2.8,2.65,2.77),(5.6,8.60,.14),'Parede branca','Teto_Superior',.002,h.FLOORS[1])


def annotations(cfg):
    for r in cfg['rooms']:
        if r['level']!=1:continue
        x0,x1,y0,y1=r['bounds'];bath=r['id'].startswith('banho')
        name={'suite':'SUÍTE','quarto_branco':'QUARTO FRENTE','quarto_azul':'QUARTO FUNDOS','banho_suite':'WC SUÍTE?','banho_social':'WC SOCIAL?'}[r['id']]
        width=x1-x0-.15;depth=y1-y0-.15
        label=name+f'\n≈ {width:.2f} × {depth:.2f} m'
        if bath:label+='\nHIPÓTESE'
        h.text('Rótulo superior '+r['id'],label,((x0+x1)/2,(y0+y1)/2,6.0),.13 if bath else .15,'Cotas_Superior','Hipotese tinta' if bath else 'Cotas tinta')
    h.text('Superior aviso','QUARTOS CONFORME CROQUI • MEDIDAS E BANHEIROS PROVISÓRIOS',(2.8,7.5,3.0),.14,'Cotas_Superior','Hipotese tinta')
    h.text('Circulação superior','CIRCULAÇÃO',(3.45,3.8,6.0),.13,'Cotas_Superior')
    h.text('Varanda superior','VARANDA',(1.4,-1.26,6.0),.13,'Cotas_Superior')
    s=cfg['layout']['stairs']
    for body,loc in [('7 DEGRAUS',(4.48,4.08,6.0)),('4 DEGRAUS',(4.70,3.22,6.0)),(f"CURVA\n{s['turn_steps']} ESTIMADOS",(5.25,3.65,6.0))]:
        h.text('Contagem '+body,body+'\nTRECHO SOB O HALL' if body=='7 DEGRAUS' else body,loc,.10,'Cotas_Superior','Hipotese tinta' if 'CURVA' in body else 'Cotas tinta')
    g.rod('Subida primeiro lance',(4.02,4.30,5.95),(4.89,4.30,5.95),.012,'Cotas tinta','Cotas_Superior')
    g.rod('Subida lance final',(4.94,2.93,5.95),(4.45,2.93,5.95),.012,'Cotas tinta','Cotas_Superior')
