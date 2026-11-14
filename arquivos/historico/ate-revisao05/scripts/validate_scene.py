"""Reabre uma entrega, valida geometria/recursos e renderiza a partir do .blend salvo.

Não salva o arquivo validado. O teste do espelho restaura o objeto antes do render final.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_scene import configure_device


def world_bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects if o.type=='MESH' for c in o.bound_box]
    return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]


def descendants(obj):
    return [obj,*obj.children_recursive]


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--preview-only',action='store_true');p.add_argument('--mirror-only',action='store_true');p.add_argument('--layout-only',action='store_true');p.add_argument('--skip-mirror',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=args.project_root.resolve();scene=bpy.context.scene
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':bpy.data.filepath,'blender_version':bpy.app.version_string,'blend_sha256_before':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'object_count':len(scene.objects),'checks':{}}
    def check(name,condition,detail=None):
        report['checks'][name]={'passed':bool(condition),'detail':detail}
        if not condition:raise AssertionError(name+': '+str(detail))
    check('camera_principal_ativa',scene.camera.name=='CAM_Referencia')
    check('cycles',scene.render.engine=='CYCLES')
    check('unidades_metros',scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1)
    for c in ['Arquitetura','Estar','Jantar','Bar','Cozinha','Iluminacao','Cameras','Referencias']:check('colecao_'+c,c in bpy.data.collections)
    chairs=[o for o in scene.objects if o.get('categoria')=='cadeira_jantar'];stools=[o for o in scene.objects if o.get('categoria')=='banqueta_bar']
    check('quatro_cadeiras',len(chairs)==4,len(chairs));check('cadeiras_2_mais_2',sum(o.get('lado')=='esquerdo' for o in chairs)==2 and sum(o.get('lado')=='direito' for o in chairs)==2)
    check('quatro_banquetas',len(stools)==4,len(stools))
    check('tres_tabuas_longitudinais',len([o for o in scene.objects if o.name.startswith('Tampo tabua longitudinal')])==3)
    images=[{'name':i.name,'packed':bool(i.packed_file),'source':i.source,'size':list(i.size)} for i in bpy.data.images if i.type!='RENDER_RESULT' and i.name not in ['Render Result','Viewer Node']]
    check('imagens_disponiveis',all(i['packed'] or i['source']=='GENERATED' for i in images),images)
    check('referencias_fora_do_render',bpy.data.collections['Referencias'].hide_render)
    check('arquitetura_protegida',bpy.data.collections['Arquitetura'].hide_select)
    check('espelho_fisico',bpy.data.materials['Espelho fisico'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value==1)
    bounds={o.name:world_bounds(descendants(o)) for o in chairs+stools+[o for o in scene.objects if o.name.startswith(('MESA_','SOFA_'))]}
    # Limite de 3 mm, incluindo a pequena tolerância da superfície do porcelanato.
    check('moveis_apoiados',all(-.003<=b[2][0]<=.003 for b in bounds.values()),bounds)
    config=json.loads((root/'config/cena.json').read_text(encoding='utf-8'))
    check('configuracao_corresponde_ao_blend',scene.get('config_sha256')==hashlib.sha256((root/'config/cena.json').read_bytes()).hexdigest())
    dims=config['estimated_dimensions_m']
    check('moveis_dentro_do_piso',all(b[0][0]>=-.025 and b[0][1]<=dims['room_width']+.025 and b[1][0]>=dims.get('room_front_y',0)-.025 and b[1][1]<=dims['room_depth']+.025 for b in bounds.values()))
    overlaps=[]
    keys=list(bounds)
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            overlap=[min(bounds[a][axis][1],bounds[b][axis][1])-max(bounds[a][axis][0],bounds[b][axis][0]) for axis in range(3)]
            if all(o>.035 for o in overlap):overlaps.append({'a':a,'b':b,'overlap_m':overlap})
    check('sem_intersecoes_entre_moveis_principais',not overlaps,overlaps)
    report['layout_bounds_m']=bounds
    report['device']=configure_device(args.device)
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.resolution_percentage=100
    def render(name):
        scene.render.filepath=str(root/'renders'/name);bpy.ops.render.render(write_still=True)
        print('RENDER_WRITTEN',scene.render.filepath,flush=True)
    if args.preview_only:
        scene.render.resolution_percentage=50;scene.cycles.samples=24;render('previa-reaberta.png');return
    if not args.layout_only and not args.skip_mirror:
        # Recorte do espelho real, com o mesmo seed para eliminar ruído como explicação.
        original=(scene.render.resolution_x,scene.render.resolution_y,scene.cycles.samples)
        scene.render.resolution_x=1671;scene.render.resolution_y=941;scene.cycles.samples=80
        scene.render.use_border=True;scene.render.use_crop_to_border=True
        scene.render.border_min_x=.15;scene.render.border_max_x=.198;scene.render.border_min_y=.30;scene.render.border_max_y=.67
        probe=next(o for o in scene.objects if o.get('mirror_probe'))
        old=probe.location.copy()
        render('espelho-antes.png')
        probe.location.y-=.35;probe.location.x+=.05;probe.location.z+=.03
        bpy.context.view_layer.update();render('espelho-depois.png')
        probe.location=old;bpy.context.view_layer.update()
        check('objeto_espelho_restaurado',(probe.location-old).length<1e-7)
        scene.render.use_border=False;scene.render.use_crop_to_border=False
        scene.render.resolution_x,scene.render.resolution_y,scene.cycles.samples=original
        if args.mirror_only:
            (root/'relatorios/validacao-espelho.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return
    if not args.layout_only:
        scene.camera=bpy.data.objects['CAM_Referencia'];scene.render.resolution_x=1671;scene.render.resolution_y=941
        render('principal.png')
    scene.camera=bpy.data.objects['CAM_Superior']
    hidden=[]
    for o in scene.objects:
        if o.get('hide_in_top_view') or o.name.startswith(('HIPOTESE_Cobertura','HIPOTESE_Vegetacao','Viga cobertura','Travessa cobertura','Folhagem')) and o.users_collection[0].name=='Arquitetura':
            if not o.hide_render:hidden.append(o);o.hide_render=True
    # Bar/cupulas/pendente ocultos somente nesta vista para ver assentos e circulação.
    for o in scene.objects:
        if o.type=='MESH' and o.users_collection[0].name=='Iluminacao':
            if not o.hide_render:hidden.append(o);o.hide_render=True
    scene.render.resolution_x=1200;scene.render.resolution_y=1500;scene.cycles.samples=48
    render('vista-superior.png')
    for o in hidden:o.hide_render=False
    report['saved_file_unchanged']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==report['blend_sha256_before']
    check('arquivo_salvo_preservado',report['saved_file_unchanged'])
    report['renders']=['principal.png','vista-superior.png'] if not args.layout_only else ['vista-superior.png']
    (root/'relatorios/validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('VALIDATION_COMPLETE',json.dumps(report['checks'],ensure_ascii=False),flush=True)


if __name__=='__main__':main()
