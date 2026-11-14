"""Valida a entrega reaberta e renderiza presets sem modificar o .blend salvo."""
import argparse
import datetime as dt
from decimal import Decimal
import hashlib
import json
import re
from pathlib import Path
import sys

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_scene import configure_device


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--preview',action='store_true');p.add_argument('--only',choices=['plans','photos','exterior']);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=args.project_root.resolve();file=Path(bpy.data.filepath);before=hashlib.sha256(file.read_bytes()).hexdigest();cfg=json.loads((root/'config/planta-casa.json').read_text(encoding='utf-8'))
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'file':str(file.relative_to(root)),'sha256':before,'version':bpy.app.version_string,'object_count':len(bpy.data.objects),'checks':{},'renders':[]}
    def check(name,ok,detail=None):
        report['checks'][name]={'passed':bool(ok),'detail':detail}
        if not ok:raise AssertionError(name+': '+str(detail))
    for name in ['CASA_Completa','PLANTA_Terreo','PLANTA_Superior','PLANTA_Terreo_Cotas','PLANTA_Superior_Cotas','FOTO_Sala_Fundos','FOTO_Sala_Frente','FOTO_Cozinha']:check('scene_'+name,name in bpy.data.scenes)
    check('abertura_inicial_planta',bpy.context.scene.name=='PLANTA_Terreo',bpy.context.scene.name)
    check('config_hash',all(s.get('config_sha256')==hashlib.sha256((root/'config/planta-casa.json').read_bytes()).hexdigest() for s in bpy.data.scenes))
    check('dois_niveis',abs(bpy.data.objects['NIVEL_1 — superior'].location.z-cfg['estimated_dimensions_m']['floor_height'])<1e-5)
    check('18_degraus',len([o for o in bpy.data.objects if re.match(r'^Degrau \d{2} granito',o.name)])==18)
    check('tres_quartos',all('AMBIENTE_'+key in bpy.data.objects for key in ['suite','quarto_azul','quarto_branco']))
    check('dois_banheiros_e_lavabo',all('AMBIENTE_'+key in bpy.data.objects for key in ['lavabo','banho_suite','banho_social']))
    check('cozinha_bar_lavanderia',all('AMBIENTE_'+key in bpy.data.objects for key in ['cozinha','bar','lavanderia']))
    check('originais_empacotados',len([i for i in bpy.data.images if i.packed_file and i.name.endswith('.webp')])==26)
    inv=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
    check('originais_preservados',all(hashlib.sha256((root/'referencias-originais'/name).read_bytes()).hexdigest()==meta['sha256'] for name,meta in inv['inputs'].items()))
    check('sem_medidas_confirmadas_inventadas',cfg['confirmed_dimensions_m']=={})
    check('analise_chatgpt_identificada',cfg['secondary_analysis']['verification']=='unverified_secondary_analysis')
    check('implantacao_superior_hipotetica',all(r['position_confidence']=='hypothesis' for r in cfg['rooms'] if r['level']==1))
    dims=cfg['estimated_dimensions_m'];a0=Decimal(str(dims['width']))*Decimal(str(dims['main_depth']));a1=Decimal(str(dims['width']))*(Decimal(str(dims['upper_back_y']))-Decimal(str(dims['upper_front_y'])))
    report['area_comparison']={'modeled_base_envelope_ground_m2':str(a0),'modeled_base_envelope_upper_m2':str(a1),'secondary_analysis':cfg['secondary_analysis'],'not_legal_area_validation':True,'note':'Retângulos equivalentes antes de recortes; varanda, paredes, anexos e abertura da escada não conciliados com critério da matrícula. Não identifica espacialmente os 1,74 m² mencionados como comuns.'}
    check('superior_nao_duplicado',a1>a0)
    check('cobertura_bar_fora_da_laje_superior',dims['upper_back_y']<=8.5)
    camera_collisions=[]
    for name in ['FOTO_Sala_Fundos','FOTO_Sala_Frente','FOTO_Cozinha']:
        scene=bpy.data.scenes[name];point=scene.camera.matrix_world.translation
        for obj in scene.objects:
            if obj.type!='MESH' or not obj.visible_get(view_layer=scene.view_layers[0]):continue
            corners=[obj.matrix_world@Vector(v) for v in obj.bound_box]
            if all(min(v[i] for v in corners)+.008<point[i]<max(v[i] for v in corners)-.008 for i in range(3)):
                camera_collisions.append({'scene':name,'mesh':obj.name})
    check('cameras_fora_dos_volumes_solidos',not camera_collisions,camera_collisions)
    # Somente a coerência geométrica dos volumes-base; não mede área registral.
    hole=(dims['living_dining_width'],dims['width'],dims['stair_front_y'],dims['stair_back_y'])
    slabs=[o for o in bpy.data.objects if o.name.startswith('Laje superior')]
    overlaps=[]
    for o in slabs:
        x0,x1=o.location.x-o.dimensions.x/2,o.location.x+o.dimensions.x/2;y0,y1=o.location.y-o.dimensions.y/2,o.location.y+o.dimensions.y/2
        area=max(0,min(x1,hole[1])-max(x0,hole[0]))*max(0,min(y1,hole[3])-max(y0,hole[2]))
        if area>1e-5:overlaps.append([o.name,area])
    check('laje_recortada_na_escada',not overlaps,overlaps)
    report['stair_opening_estimated_m2']=(hole[1]-hole[0])*(hole[3]-hole[2])
    report['device']=configure_device(args.device)
    jobs=[('PLANTA_Terreo','terreo-3d.png','plans'),('PLANTA_Superior','superior-3d.png','plans'),('PLANTA_Terreo_Cotas','terreo-superior.png','plans'),('PLANTA_Superior_Cotas','pavimento-superior.png','plans'),('FOTO_Sala_Fundos','sala-fundos.png','photos'),('FOTO_Sala_Frente','sala-frente.png','photos'),('FOTO_Cozinha','cozinha.png','photos'),('CASA_Completa','volumetria.png','exterior')]
    for name,out,group in jobs:
        if args.only and group!=args.only:continue
        s=bpy.data.scenes[name];s.cycles.device='GPU' if report['device']['backend']=='OPTIX' else 'CPU';s.render.resolution_percentage=50 if args.preview else 100;s.cycles.samples=20 if args.preview else cfg['render']['samples']
        if group=='photos':s.render.resolution_x=1200;s.render.resolution_y=630
        s.render.filepath=str(root/'renders/planta-casa'/out)
        bpy.ops.render.render(write_still=True,scene=s.name)
        report['renders'].append(str(Path(s.render.filepath).relative_to(root)))
        print('HOUSE_RENDERED',name,s.render.filepath,flush=True)
    check('blend_nao_modificado_pelos_testes',hashlib.sha256(file.read_bytes()).hexdigest()==before)
    report['scope']='Modelo preliminar proporcional baseado em fotos; implantação superior e medidas não verificadas; não atesta a matrícula ou a planta real.'
    (root/'relatorios/planta-casa/validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('HOUSE_VALIDATED',len(report['checks']),'checks; renders',len(report['renders']),flush=True)


if __name__=='__main__':main()
