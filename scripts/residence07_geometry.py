"""Contrato métrico compartilhado pelas plantas e pelo Blender da residência 07."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/residencia-07.json'
OUTPUT_ROOT = ROOT / json.loads(CONFIG.read_text())['delivery']['renders']


def artifact_path(name, extension='png'):
    """Local único para a organização dos entregáveis, usado por todos os geradores."""
    if name in ['caderno-residencia-07','plantas-tecnicas-residencia-07']:
        folder='00-cadernos'
    elif name.startswith('painel-'):
        folder='06-galerias'
    elif name.startswith('estrutura-'):
        folder='02-estrutura/3d' if name.endswith('-3d') else '02-estrutura/2d'
    elif name.startswith('eletrica-'):folder='03-instalacoes/eletrica'
    elif name.startswith('hidraulica-'):folder='03-instalacoes/hidraulica'
    elif name.startswith('esgoto-'):folder='03-instalacoes/esgoto'
    elif name.startswith('tv-telefone-'):folder='03-instalacoes/tv-telefone'
    elif name.startswith('instalacoes-coordenadas-'):folder='03-instalacoes/coordenadas'
    elif name in ['planta-terreo-humanizada','planta-superior-humanizada','terreo-3d','superior-3d','lavabo-planta']:
        folder='04-plantas-3d'
    elif name.startswith('cotas-originais-') or name in ['planta-terreo','planta-superior','pavimentos-sobrepostos','corte-longitudinal']:
        folder='01-plantas-arquitetonicas'
    elif name in ['volumetria','fachada','fundos','cobertura','sacada']:
        folder='05-imagens/exteriores'
    elif name in ['suite','quarto-frente','quarto-fundos','banheiro-suite','banheiro-social']:
        folder='05-imagens/superior'
    elif name in ['lazer-fundos','lavanderia']:
        folder='05-imagens/fundos-proposta'
    elif name in ['sala-integrada','sala','sala-tv','jantar','cozinha','cozinha-reversa','escada-acesso','lavabo']:
        folder='05-imagens/terreo'
    else:raise ValueError('Artefato sem destino definido: '+name)
    return OUTPUT_ROOT/folder/(name+'.'+extension)


def preview_path(name):
    return OUTPUT_ROOT/'_trabalho/previas'/(name+'.png')


def valid_render_record(record):
    """Valida imagem e origem; a revisão de materiais só substitui as quatro estruturas."""
    try:
        cfg=load();base=cfg['delivery']['blend'];source=record.get('source_blend',base)
        if source!=base:
            study=json.loads((ROOT/'config/residencia-07-estudos.json').read_text())
            if source!=study['services_blend'] or not record['id'].startswith('estrutura-'):return False
            receipt=json.loads((ROOT/study['report_directory']/'instalacoes-modelo.json').read_text())
            if receipt['blend_sha256']!=record['blend_sha256'] or receipt['config_sha256']!=sha(ROOT/'config/residencia-07-estudos.json'):return False
            if not any(j['id']==record['id'] and j['file']==record['file'] for j in receipt['jobs']):return False
        return sha(ROOT/source)==record['blend_sha256'] and sha(ROOT/record['file'])==record['sha256']
    except (OSError,KeyError,ValueError):return False


def load():
    cfg = json.loads(CONFIG.read_text())
    validate(cfg)
    return cfg


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def area(poly):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))) / 2


def point(wall, distance, offset=0):
    a,b = wall['a'],wall['b']
    length = math.dist(a,b)
    ux,uy = (b[0]-a[0])/length,(b[1]-a[1])/length
    return [a[0]+ux*distance-uy*offset,a[1]+uy*distance+ux*offset]


def wall_polygon(wall, start=0, end=None):
    end = math.dist(wall['a'],wall['b']) if end is None else end
    t = wall['t']/2
    return [point(wall,start,t),point(wall,end,t),point(wall,end,-t),point(wall,start,-t)]


def wall_cells(wall, clear_height):
    """Faixas sólidas, com vãos reais; retorna distância inicial/final e Z local."""
    length = math.dist(wall['a'],wall['b'])
    height = wall.get('height',clear_height)
    cursor = 0
    for op in sorted(wall.get('openings',[]),key=lambda o:o['start']):
        start,end = op['start'],op['start']+op['width']
        if start > cursor+1e-8:
            yield cursor,start,0,height
        sill,top = op.get('sill',0),op.get('sill',0)+op['height']
        if sill>0:
            yield start,end,0,min(sill,height)
        if top<height:
            yield start,end,top,height
        cursor=end
    if cursor<length-1e-8:
        yield cursor,length,0,height


def stair_polygons(cfg):
    """Cinco pisos retos, seis compensados e cinco pisos de retorno."""
    s=cfg['stair'];x=s['start_x'];turn=s['turn_x'];going=s['going']
    result=[]
    for i in range(s['straight_treads']):
        result.append([[x+i*going,s['top_center_y']],[x+(i+1)*going,s['top_center_y']],
                       [x+(i+1)*going,s['top_y']],[x+i*going,s['top_y']]])
    # Centro comum: a faixa entre os lances fecha no leque, sem degraus soltos.
    def ray(center, angle, upper):
        dx,dy=math.cos(angle),math.sin(angle)
        distances=[]
        if dx>1e-8:distances.append((s['right_x']-center[0])/dx)
        boundary=s['top_y'] if upper else s['bottom_y']
        if abs(dy)>1e-8:distances.append((boundary-center[1])/dy)
        distance=min(t for t in distances if t>0)
        return [center[0]+dx*distance,center[1]+dy*distance]
    for upper in [True,False]:
        center=[turn,(s['top_center_y']+s['bottom_center_y'])/2]
        angles=[math.pi/2,math.pi/3,math.pi/6,0] if upper else [0,-math.pi/6,-math.pi/3,-math.pi/2]
        for a,b in zip(angles,angles[1:]):
            pa,pb=ray(center,a,upper),ray(center,b,upper)
            poly=[center,pa]
            if min(abs(a),abs(b))<math.pi/4<max(abs(a),abs(b)):
                poly.append([s['right_x'],s['top_y'] if upper else s['bottom_y']])
            poly.append(pb)
            result.append(poly)
    for i in range(s['straight_treads']):
        result.append([[turn-(i+1)*going,s['bottom_y']],[turn-i*going,s['bottom_y']],
                       [turn-i*going,s['bottom_center_y']],[turn-(i+1)*going,s['bottom_center_y']]])
    return result


def validate(cfg):
    assert cfg['unit']=='07' and cfg['units']=='METERS'
    d=cfg['dimensions']
    assert d['width']==6.35 and d['floor_height']==2.70
    assert abs(d['clear_height']+d['slab']-d['floor_height'])<1e-8
    ids=[w['id'] for w in cfg['walls']]
    assert len(ids)==len(set(ids))
    openings=[]
    for w in cfg['walls']:
        assert w['level'] in [0,1] and w['t']>0
        length=math.dist(w['a'],w['b']);assert length>0
        previous=0
        for op in sorted(w.get('openings',[]),key=lambda o:o['start']):
            assert op['kind'] in ['door','window','sliding']
            assert op['width']>0 and op['height']>0
            assert op['start']>=previous and op['start']+op['width']<=length+1e-6,w['id']
            assert op.get('sill',0)+op['height']<=w.get('height',d['clear_height'])+1e-6
            previous=op['start']+op['width'];openings.append(op['id'])
    assert len(openings)==len(set(openings))
    s=cfg['stair']
    assert s['rise_count']==2*s['straight_treads']+s['winders']
    assert abs(s['rise_count']*s['rise']-d['floor_height'])<1e-8
    assert len(stair_polygons(cfg))==s['rise_count']
    assert len([r for r in cfg['rooms'] if r['level']==1 and r['id'].startswith('banheiro')])==2
    return {'walls':len(ids),'openings':len(openings),'stairs':s['rise_count']}


if __name__=='__main__':
    print(json.dumps(validate(load()),ensure_ascii=False))
