"""Lances com XY idênticos aos existentes; caixa deslocada para a esquerda."""
import json
import math
from pathlib import Path

import residence07_geometry as geo
import residence07_attic_roof as roof
from residence07_attic_roof import walking_samples,ceiling_z
from stairs_geometry import slab_cells

ROOT=geo.ROOT;CONFIG=ROOT/'config/residencia-07-atico-v05.json';CFG=json.loads(CONFIG.read_text())


def steps():
    return [dict(index=i+1,polygon=p,top=2.7+(i+1)*CFG['stair']['rise']) for i,p in enumerate(geo.stair_polygons(geo.load()))]


def on_floor(x,y):
    return 0<=x<=6.35 and -1.2<=y<=(6.5 if x<3.3 else 7.2) and not any(a<x<b and c<y<d for a,b,c,d in CFG['stair']['floor_holes'])


def floor_cells():
    return [p for rect in [[0,3.3,-1.2,6.5],[3.3,6.35,-1.2,7.2]] for p in slab_cells(rect,CFG['stair']['floor_holes'])]


def stair_clearance(step,x,y):
    return min(ceiling_z(x,y),5.25 if on_floor(x,y) else 100)-step['top']


def main_jobs():
    jobs=[dict(j) for j in roof.jobs() if j['mode'] not in ['access','heights']]
    for j in jobs:
        j['group']='main'
        if j['id']=='atico-reservatorio':j.update(title='Caixa reposicionada e nova área técnica à esquerda',pos=[-7,-4,11],target=[1.8,3.175,6.0],ortho=7)
        if j['id']=='atico-planta-3d':j['title']='Ático atualizado · escadas sobrepostas e caixa lateral'
        if j['id']=='atico-interior-frente':j.update(title='Estar frontal atualizado sob o forro',pos=[3.55,1.85,6.9],target=[1.9,.5,6.1],lens=21)
        if j['id']=='atico-interior-fundos':j.update(title='Escritório posterior após mover a área técnica',pos=[3.45,4.45,6.9],target=[1.7,5.45,6.25],lens=21)
    jobs.extend([
        dict(id='escada-u-conjunto',title='Escadas alinhadas desde o térreo · nova caixa lateral',pos=[12,-8,11],target=[3.2,3.175,3.8],ortho=10,mode='access',group='main'),
        dict(id='escada-u-chegada-existente',title='Hall de chegada · primeiro lance novo ao lado',pos=[2.7,1.7,4.4],target=[4.8,3.7,3.8],lens=24,mode='entry',group='main'),
        dict(id='escada-u-detalhe',title='Lances novos exatamente sobre os inferiores',pos=[-5,-6,10],target=[4.8,3.2,3.5],ortho=8.4,mode='stair',group='main'),
        dict(id='escada-u-planta-superior',title='Superior preservado · subida pelo hall',pos=[3.175,2.7,20],target=[3.175,2.7,2.7],ortho=12,top=True,mode='lower-plan',group='main'),
        dict(id='atico-forro-corte',title='Ático atualizado · forro e reservatório à esquerda',pos=[11,-9,13],target=[3.4,2.7,6.8],ortho=12,mode='ceiling-cut',group='main'),
        dict(id='atico-alturas-forro',title='Alturas sob o forro · novo vão em L',pos=[3.175,3,20],target=[3.175,3,5.4],ortho=13,top=True,mode='heights',group='main')])
    return jobs


def jobs():
    out=main_jobs();target=[3.2,3.175,3.25];radius=18;azimuth=math.radians(-58)
    for i in range(4):
        a=azimuth+i*math.pi/2
        out.append(dict(id=['01-referencia','02-giro-90','03-giro-180','04-giro-270'][i],title=f'Escadas sobrepostas · giro {i*90}°',pos=[target[0]+radius*math.cos(a),target[1]+radius*math.sin(a),10.6],target=target,ortho=10.4,mode='isolated',group='detail'))
    out.extend([
        dict(id='05-lateral-patamares',title='Lateral atualizada · lances exatamente sobrepostos',pos=[-15,3.175,3.25],target=target,ortho=10.4,mode='isolated',group='detail'),
        dict(id='06-vista-superior',title='Vista superior · caixa fora da projeção das escadas',pos=[3.2,3.175,25],target=target,ortho=10.4,top=True,mode='isolated',group='detail')])
    for i in range(24):
        a=azimuth+i*math.tau/24
        out.append(dict(id=f'giro-{i:02}',title=f'Giro 360° · {i*15}°',pos=[target[0]+radius*math.cos(a),target[1]+radius*math.sin(a),10.6],target=target,ortho=10.4,mode='isolated',group='orbit',angle_degrees=i*15))
    return out


def validate():
    old=geo.stair_polygons(geo.load());new=steps();assert [s['polygon'] for s in new]==old
    assert new[-1]['top']==5.4
    minimum=min(stair_clearance(s,x,y) for s in new for x,y in walking_samples(s))
    assert minimum>=2.10
    assert not on_floor(5.2,3.5) and on_floor(4.3,3.7) and on_floor(5.8,.5)
    box=CFG['tank'];assert box['center_xy'][0]+.9<4.1
    assert len(jobs())==48
    return {'risers':16,'exact_xy_alignment':True,'minimum_stair_clearance_m':minimum,'tank_center':box['center_xy'],'tank_translation':[-3.55,0,0],'views':48}


if __name__=='__main__':print(validate())
