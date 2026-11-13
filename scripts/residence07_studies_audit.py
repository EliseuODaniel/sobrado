"""Confere os três modelos reabertos, sem alterar os arquivos Blender."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
import residence07_studies_data as data

REPORT=geo.ROOT/data.CFG['report_directory']


def audit(kind,require_renders=False):
    receipt=json.loads((REPORT/(kind+'-modelo.json')).read_text());checks=[]
    def check(name,value,details=None):
        row={'name':name,'passed':bool(value)}
        if details is not None:row['details']=details
        checks.append(row)
    check('arquivo nativo salvo',geo.sha(bpy.data.filepath)==receipt['blend_sha256'])
    check('base 07 preservada',geo.sha(geo.ROOT/receipt['source_blend'])==receipt['source_blend_sha256'])
    check('configuração do estudo',geo.sha(data.CONFIG)==receipt['config_sha256'])
    check('geradores registrados',len(receipt['generators'])==3 and all(geo.sha(geo.ROOT/p)==h for p,h in receipt['generators'].items()))
    check('conjunto de cenas',set(bpy.data.scenes.keys())=={j['scene'] for j in receipt['jobs']})
    check('nenhuma biblioteca externa vinculada',not bpy.data.libraries)
    for j in receipt['jobs']:
        scene=bpy.data.scenes[j['scene']]
        check('câmera '+j['id'],scene.camera is not None and (scene.camera.location-Vector(j['pos'])).length<1e-4)
        check('origem métrica '+j['id'],scene.get('geometry_source_sha256')==geo.sha(geo.CONFIG))
        check('configuração '+j['id'],scene.get('study_config_sha256')==geo.sha(data.CONFIG))
        check('destino '+j['id'],scene.render.filepath==str(geo.ROOT/j['file']))
        check('resolução '+j['id'],[scene.render.resolution_x,scene.render.resolution_y]==data.CFG['resolution'])
        check('sem override '+j['id'],scene.view_layers[0].material_override is None)
        check('unidade '+j['id'],scene.unit_settings.system=='METRIC')
    # Conferir cópias contra malhas do arquivo aprovado, em uma nova leitura da biblioteca.
    copies=[o for o in bpy.data.objects if o.get('study_geometry_unchanged')]
    if copies:
        wanted={o['study_source_object'] for o in copies}
        local_originals={n:bpy.data.objects.get(n) for n in wanted}
        with bpy.data.libraries.load(str(geo.ROOT/receipt['source_blend']),link=False) as (src,dst):
            # O carregador modifica a lista fornecida; as chaves do recibo precisam permanecer strings.
            names=[n for n in src.objects if n in wanted];dst.objects=list(names)
        originals=dict(zip(names,dst.objects));bad=[];compared=0;local_compared=0;external_compared=0
        for obj in copies:
            key=obj['study_source_object'];original=originals.get(key)
            # Paredes da sala técnica e oitões são propostas novas; suas cópias transparentes
            # têm a origem no próprio modelo. Elementos da base são sempre lidos da biblioteca.
            local=key not in originals
            if local:original=local_originals.get(key)
            if original is None:bad.append(obj.name);continue
            if obj.type!='MESH':continue
            compared+=1
            if local:local_compared+=1
            else:external_compared+=1
            if len(obj.data.vertices)!=len(original.data.vertices) or any((a.co-b.co).length>1e-6 for a,b in zip(obj.data.vertices,original.data.vertices)):
                bad.append(obj.name)
        check('vértices das cópias preservados',not bad,bad)
        check('cópias efetivamente comparadas',compared>0,compared)
        check('cópias da base comparadas independentemente',external_compared>0,{'external':external_compared,'local_proposal_copies':local_compared})
    if kind=='instalacoes':
        check('20 vistas de estrutura e redes',len(receipt['jobs'])==20)
        for key,alpha in [('EST Parede transparente',.12),('EST Laje transparente',.055)]:
            mat=bpy.data.materials[key]
            check('transparência '+key,abs(mat['study_opacity']-alpha)<1e-6 and any(n.type=='BSDF_TRANSPARENT' for n in mat.node_tree.nodes))
        check('seis disciplinas de rede',{n['system'] for n in receipt['network_graph']['nodes']}=={'cold','hot','sewer','vent','electric','telecom'})
        check('grafo corresponde à configuração',receipt['network_graph']==data.pipe_points())
        for key in ['electric','cold','hot','sewer','vent','telecom']:
            col=bpy.data.collections['INST_'+key];tubes=[o for o in col.objects if o.type=='CURVE']
            check('tubos tridimensionais '+key,bool(tubes) and all(o.data.dimensions=='3D' and o.data.bevel_depth>0 for o in tubes))
            check('diâmetro nominal preservado '+key,all(o.get('nominal_diameter_m',0)>0 and o['display_diameter_m']>=o['nominal_diameter_m'] for o in tubes))
            for level in [0,1]:
                col=bpy.data.collections[f'INST_{key}_Piso_{level}']
                zs=[p.co.z for o in col.objects if o.type=='CURVE' for p in o.data.splines[0].points]
                check(f'rede {key} isolada no piso {level}',bool(zs) and min(zs)>=level*2.7-.35001 and max(zs)<=(level+1)*2.7-.04999)
        for level in [0,1]:
            col=bpy.data.collections['INST_Arquitetura_Piso_'+str(level)]
            zs=[(o.matrix_basis@v.co).z for o in col.objects if o.type=='MESH' for v in o.data.vertices]
            check('arquitetura isolada piso '+str(level),bool(zs) and min(zs)>=level*2.7-.15001 and max(zs)<=(level+1)*2.7+.00001)
        for j in receipt['jobs'][:4]:
            scene=bpy.data.scenes[j['scene']];walls=[o for o in scene.objects if o.type=='MESH' and ('Parede' in o.name or 'Corte' in o.name)]
            check('estrutura sem móveis '+j['id'],not any('Mobiliario' in c.name for c in scene.collection.children))
            check('parede em sálvia '+j['id'],bool(walls) and any(m and m.name=='EST Parede sálvia suave' for o in walls for m in o.data.materials))
        check('reservatório documentado',any(o.get('capacity_liters')==1000 for o in bpy.data.objects))
    else:
        check('20 vistas do estado atual',len(receipt['jobs'])==20)
        visible={o for sc in bpy.data.scenes for o in sc.objects}
        check('parede dos fundos retirada',not any(o.get('wall_id')=='T-fundos-sala' for o in visible))
        check('esquadria retirada da abertura',not any('PJ1-jardim' in o.name for o in visible))
        check('cobertura posterior em dois panos',sum(o.name.startswith('ATUAL Cobertura vidro') for o in visible)==2)
        check('divisão com porta de vidro',any(o.name.startswith('ATUAL Vidro divisao') for o in visible))
        check('oito conjuntos de móveis das fotos',len(receipt['photo_rooms'])==8)
        check('origem dos móveis preservada',geo.sha(geo.ROOT/receipt['furniture_source'])==receipt['furniture_source_sha256'])
        furniture=[o for o in visible if o.get('photo_room')]
        check('móveis importados editáveis',len(furniture)>=100 and all(o.get('furniture_scale_preserved') for o in furniture))
        check('sem coleção industrial',not any('INDUSTRIAL' in c.name.upper() for sc in bpy.data.scenes for c in sc.collection.children))
        check('sem teto coincidente com laje superior',all('R07_Teto_Terreo' not in sc.collection.children for sc in bpy.data.scenes))
        for scene_name in ['ATUAL_planta-terreo','ATUAL_terreo-3d']:
            check('escada visível em '+scene_name,'ATUAL_Escada' in bpy.data.scenes[scene_name].collection.children)
        sink=bpy.data.objects['ATUAL Bancada lavabo'];bpy.context.window.scene=bpy.data.scenes['ATUAL_lavabo'];bpy.context.view_layer.update()
        check('louças dentro do lavabo',3.8<sink.matrix_world.translation.x<6.25 and 2.15<sink.matrix_world.translation.y<3.1)
    if require_renders:
        records=json.loads((REPORT/(kind+'-renders.json')).read_text())
        check('conjunto exato de imagens',{r['id'] for r in records}=={j['id'] for j in receipt['jobs']})
        for row in records:
            p=geo.ROOT/row['file']
            check('imagem salva '+row['id'],p.is_file() and geo.sha(p)==row['sha256'] and row['blend_sha256']==receipt['blend_sha256'] and not row['preview'])
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'kind':kind,'blend_sha256':receipt['blend_sha256'],
            'scope':'Geometria visual de estudo; não constitui levantamento presencial ou cálculo de engenharia.','checks':checks,'all_passed':all(c['passed'] for c in checks),'renders_required':require_renders}
    (REPORT/(kind+'-validacao.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('STUDY_AUDIT',kind,len(checks),'PASSED' if result['all_passed'] else 'FAILED')
    for c in checks:
        if not c['passed']:print('FAIL',c)
    if not result['all_passed']:raise RuntimeError('Conferência reprovada: '+kind)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',required=True,choices=['instalacoes','atual']);p.add_argument('--require-renders',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);audit(args.kind,args.require_renders)
