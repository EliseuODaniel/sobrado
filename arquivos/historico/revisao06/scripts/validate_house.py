"""Validação da revisão: integridade e testes de contradições, com escopos separados."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_photo_geometry
import render_revision


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--device',choices=['auto','cpu'],default='cpu');p.add_argument('--preview',action='store_true');p.add_argument('--no-render',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=args.project_root.resolve();file=Path(bpy.data.filepath);before=hashlib.sha256(file.read_bytes()).hexdigest();cfg=json.loads((root/'config/planta-casa.json').read_text())
    revision=cfg.get('revision_number',2);folder=root/'relatorios/atual';folder.mkdir(exist_ok=True)
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'revision':revision,'file':str(file.relative_to(root)),'sha256':before,'version':bpy.app.version_string,'checks':{},'unknowns':['Implantação dos quartos e banheiros superiores','Forma e dimensões completas do retorno da escada','Dimensões reais; croqui do usuário não é levantamento métrico','Conciliação com a matrícula original, que não foi fornecida']}
    def check(name,ok,detail=None):
        report['checks'][name]={'passed':bool(ok),'detail':detail}
        if not ok:raise AssertionError(name+': '+str(detail))
    expected={'PLANTA_Terreo','PLANTA_Superior','PLANTA_Terreo_Cotas','PLANTA_Superior_Cotas','CASA_Completa','ESTUDOS_Superior'}|{key.replace('CAM_Foto_','FOTO_') for key in cfg['cameras']}
    if revision>=4:expected.add('CORTE_Lavabo_Escada')
    expected.add('PLANTA_Terreo_Portas')
    check('todas_as_cenas_salvas',expected<=set(s.name for s in bpy.data.scenes),sorted(expected))
    check('cena_inicial_terreo',bpy.context.scene.name=='PLANTA_Terreo')
    check('config_hash_todas_cenas',all(s.get('config_sha256')==hashlib.sha256((root/'config/planta-casa.json').read_bytes()).hexdigest() for s in bpy.data.scenes))
    check('dois_niveis',abs(bpy.data.objects['NIVEL_1 — superior'].location.z-cfg['estimated_dimensions_m']['floor_height'])<1e-5)
    steps=[o for o in bpy.data.objects if re.match(r'^Degrau \d{2} granito',o.name)]
    check('numero_degraus_da_hipotese',len(steps)==cfg['layout']['stairs']['risers'],len(steps))
    inv=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
    check('originais_preservados',all(hashlib.sha256((root/'referencias-originais'/name).read_bytes()).hexdigest()==meta['sha256'] for name,meta in inv['inputs'].items()))
    check('referencias_empacotadas',len([i for i in bpy.data.images if i.packed_file and i.name.endswith('.webp')])==26)
    check('analise_chatgpt_nao_promovida',cfg['secondary_analysis']['verification']=='unverified_secondary_analysis' and cfg['confirmed_dimensions_m']=={})
    check('superior_sem_bounds_inventados',all(r['bounds'] is None for r in cfg['rooms'] if r['level']==1))
    studies=[o for o in bpy.data.objects if o.name.startswith('ESTUDO_')]
    check('cinco_modulos_superiores_separados',len(studies)==5 and all(o.get('not_house_coordinates') for o in studies),[o.name for o in studies])
    def layer(scene,name):
        def find(node):
            if node.name==name:return node
            for child in node.children:
                found=find(child)
                if found:return found
        return find(scene.view_layers[0].layer_collection)
    check('estudos_fora_da_planta_e_fotos',all(layer(bpy.data.scenes[name],'Estudos_Superior') is None or layer(bpy.data.scenes[name],'Estudos_Superior').exclude for name in expected if name!='ESTUDOS_Superior'))
    hole=cfg['layout']['stair_hole'];overlaps=[]
    for obj in bpy.data.objects:
        if not obj.name.startswith('Laje superior'):continue
        x0,x1=obj.location.x-obj.dimensions.x/2,obj.location.x+obj.dimensions.x/2;y0,y1=obj.location.y-obj.dimensions.y/2,obj.location.y+obj.dimensions.y/2
        area=max(0,min(x1,hole[1])-max(x0,hole[0]))*max(0,min(y1,hole[3])-max(y0,hole[2]))
        if area>1e-5:overlaps.append([obj.name,area])
    check('laje_nao_fecha_vao_escada',not overlaps,overlaps)
    collisions=[]
    for name in expected:
        if not name.startswith('FOTO_'):continue
        scene=bpy.data.scenes[name];point=scene.camera.matrix_world.translation
        for obj in scene.objects:
            if obj.type!='MESH' or not obj.visible_get(view_layer=scene.view_layers[0]):continue
            bounds=[obj.matrix_world@Vector(v) for v in obj.bound_box]
            if all(min(v[i] for v in bounds)+.008<point[i]<max(v[i] for v in bounds)-.008 for i in range(3)):collisions.append({'scene':name,'object':obj.name})
    check('cameras_fora_dos_solidos',not collisions,collisions)
    saved_argv=sys.argv[:]
    try:
        sys.argv=['audit_photo_geometry.py','--','--project-root',str(root)];audit_photo_geometry.main()
        report['photo_geometry_audit']=json.loads((folder/'auditoria-depois.json').read_text())
        check('contradicoes_fotograficas_testadas',report['photo_geometry_audit']['all_passed'])
        if not args.no_render:
            sys.argv=['render_revision.py','--','--project-root',str(root),'--device',args.device]+(['--preview'] if args.preview else [])
            render_revision.main()
            report['renders']=json.loads((folder/('renders-previa.json' if args.preview else 'renders-finais.json')).read_text())
    finally:sys.argv=saved_argv
    check('arquivo_preservado_durante_validacao',hashlib.sha256(file.read_bytes()).hexdigest()==before)
    report['scope']='Integridade do arquivo e remoção de contradições fotográficas específicas. Não aprova a planta completa, escala real ou implantação do superior.'
    (folder/'validacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('REVISION_VALIDATED',len(report['checks']),'integrity checks;',len(report['photo_geometry_audit']['checks']),'photo geometry checks',flush=True)


if __name__=='__main__':main()
