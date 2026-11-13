"""Geometria da cobertura aprovada, independente de propostas antigas de escada."""
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/residencia-07-cobertura.json'
CFG=json.loads(CONFIG.read_text())

def inside(point,polygon):
    x,y=point;hit=False
    for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
    return hit

def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2

def roof_z(y):
    edge=CFG['roof_front_y'] if y<=CFG['ridge_y'] else CFG['roof_back_y']
    return CFG['eave_z']+(CFG['ridge_z']-CFG['eave_z'])*(y-edge)/(CFG['ridge_y']-edge)

def inverse_roof(z,front=True):
    edge=CFG['roof_front_y'] if front else CFG['roof_back_y']
    return edge+(z-CFG['eave_z'])*(CFG['ridge_y']-edge)/(CFG['ridge_z']-CFG['eave_z'])

def clean_polygon(points):
    result=[]
    for p in points:
        if not result or math.dist(p,result[-1])>1e-9:result.append(list(p))
    if len(result)>1 and math.dist(result[0],result[-1])<1e-9:result.pop()
    assert len(result)>=3 and area(result)>1e-9
    return result

def opening(d):
    c=d['center_x'];half=d['width']/2;face=d['face_y'];side=inverse_roof(d['eave_z'],d['direction']==1)
    return [[c-half,face],[c+half,face],[c+half,side],[c,CFG['ridge_y']],[c-half,side]]

def dormer_z(x,d):return d['peak_z']-(d['peak_z']-d['eave_z'])*abs(x-d['center_x'])/(d['width']/2)

def in_closed_polygon(point,polygon):
    if inside(point,polygon):return True
    x,y=point
    for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
        dx,dy=bx-ax,by-ay;length2=dx*dx+dy*dy
        t=((x-ax)*dx+(y-ay)*dy)/length2
        if 0<=t<=1 and math.hypot(x-ax-t*dx,y-ay-t*dy)<1e-8:return True
    return False

def envelope_z(x,y):return max([roof_z(y)]+[dormer_z(x,d) for d in CFG['dormers'] if in_closed_polygon((x,y),opening(d))])

def roof_panels(d):
    c=d['center_x'];lo,hi=c-d['width']/2,c+d['width']/2;face=d['face_y'];front=d['direction']==1
    edge=CFG['roof_front_y'] if front else CFG['roof_back_y'];ridge=CFG['ridge_y'];side=inverse_roof(d['eave_z'],front);ya,yb=sorted([edge,ridge]);ea,eb=sorted([edge,face]);w=CFG['house_width']
    polygons=[[[0,ya],[lo,ya],[lo,yb],[0,yb]],[[hi,ya],[w,ya],[w,yb],[hi,yb]],[[lo,ea],[hi,ea],[hi,eb],[lo,eb]]]
    if front:polygons += [[[lo,side],[c,ridge],[lo,ridge]],[[c,ridge],[hi,side],[hi,ridge]]]
    else:polygons += [[[lo,ridge],[c,ridge],[lo,side]],[[c,ridge],[hi,ridge],[hi,side]]]
    return [clean_polygon(p) for p in polygons]

def dormer_panels(d):
    c=d['center_x'];lo,hi=c-d['width']/2,c+d['width']/2;y=d['face_y'];side=inverse_roof(d['eave_z'],d['direction']==1);ridge=CFG['ridge_y']
    return [[(lo,y,d['eave_z']),(c,y,d['peak_z']),(c,ridge,CFG['ridge_z']),(lo,side,d['eave_z'])],
            [(c,y,d['peak_z']),(hi,y,d['eave_z']),(hi,side,d['eave_z']),(c,ridge,CFG['ridge_z'])]]

def jobs():
    return [
        dict(id='atico-planta-3d',title='Ático com aberturas centralizadas · cobertura removida',pos=[13,-12,17],target=[3.175,2.8,6.1],ortho=13,mode='plan'),
        dict(id='atico-cobertura',title='Duas cumeeiras centralizadas chegando à principal',pos=[15,-15,17],target=[3.175,3.4,5.8],ortho=18,mode='exterior'),
        dict(id='atico-frente',title='Frente · frontão centralizado e ampliado',pos=[3.175,-22,3.2],target=[3.175,1.4,5.8],lens=36,mode='exterior'),
        dict(id='atico-fundos',title='Fundos · mesma centralização da frente',pos=[3.175,25,5.0],target=[3.175,4.5,5.8],lens=36,mode='exterior'),
        dict(id='abertura-frente-detalhe',title='Detalhe frontal · cobertura contínua até o encontro',pos=[9,-13,11],target=[3.175,.7,7.5],ortho=10,mode='exterior'),
        dict(id='abertura-fundos-detalhe',title='Detalhe posterior · cobertura contínua até o encontro',pos=[-6,17,11],target=[3.175,5.3,7.5],ortho=10,mode='exterior'),
        dict(id='atico-interior-frente',title='Interior voltado à mansarda frontal centralizada',pos=[3.0,3.60,6.90],target=[3.175,-.45,6.85],lens=24,mode='interior'),
        dict(id='atico-interior-fundos',title='Interior voltado à mansarda posterior centralizada',pos=[3.0,2.10,6.90],target=[3.175,6.10,6.85],lens=24,mode='interior'),
        dict(id='atico-reservatorio',title='Caixa de 1.000 L preservada · conferir folga em 3D',pos=[11,-1,10.5],target=[4.8,3.2,6.0],ortho=6.9,mode='tank'),
        dict(id='atico-aberturas-transparente',title='Duas coberturas alinhadas · leitura transparente',pos=[14,-11,16],target=[3.175,3.0,6.8],ortho=14,mode='ghost'),
        dict(id='encontro-cumeeiras',title='Encontro real das cumeeiras no telhado principal',pos=[9,-3,14],target=[3.175,3.0,8.8],ortho=8.8,mode='roof-detail'),
        dict(id='cobertura-vista-superior',title='Vista superior · mesmo eixo e telhados até a cumeeira',pos=[3.175,3,22],target=[3.175,3,5.4],ortho=13,top=True,mode='roof-detail')]

def walking_samples(step):
    """Malha interna ao piso, incluindo proximidade das bordas; não inclui o vértice agudo do leque."""
    p=step['polygon'];cx=sum(x for x,y in p)/len(p);cy=sum(y for x,y in p)/len(p)
    points=[(cx,cy)]
    for a,b in zip(p,p[1:]+p[:1]):
        for t in [.2,.5,.8]:
            x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
            points.append((.9*x+.1*cx,.9*y+.1*cy))
    return points

def ceiling_z(x,y):
    ceiling=json.loads((ROOT/'config/residencia-07-atico-v05.json').read_text())['ceiling']
    return envelope_z(x,y)-CFG['roof_thickness']-ceiling['vertical_reserve_below_roof_underside']
