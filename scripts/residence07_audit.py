"""Auditoria em processo limpo: geometria salva, referências e entrega completa.

Blender: --background casa-07.blend --python este.py [-- --require-renders]
Não modifica o modelo.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
import residence07_build as build


def bounds(obj):
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    return [min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)]


def main(require_renders=False):
    cfg=geo.load();root=geo.ROOT;report=root/cfg['delivery']['reports'];out=root/cfg['delivery']['renders']
    checks=[]
    def check(name,passed,details=None):
        record={'name':name,'passed':bool(passed)}
        if details is not None:record['details']=details
        checks.append(record)
    model=report/'modelo.json';receipt=json.loads(model.read_text())
    check('hash do modelo salvo',receipt['blend_sha256']==geo.sha(bpy.data.filepath))
    check('configuração usada na geração',receipt['config_sha256']==geo.sha(geo.CONFIG))
    for scene in bpy.data.scenes:
        check('configuração da cena '+scene.name,scene.get('R07_geometry_sha256')==geo.sha(geo.CONFIG))
    check('conjunto exato de cenas',set(bpy.data.scenes.keys())=={'R07_'+v['id'] for v in cfg['views']})
    check('sem bibliotecas vinculadas',not bpy.data.libraries)
    images=[im for im in bpy.data.images if im.source=='FILE' and im.users>0]
    check('texturas usadas empacotadas',all(im.packed_file for im in images),len(images))
    inverted=[];seen=set()
    for obj in bpy.data.objects:
        if obj.type!='MESH' or obj.data in seen:continue
        if not obj.name.startswith(('R07 Parede ','R07 Corte ','R07 Laje ','R07 Teto ','R07 Degrau ')):continue
        seen.add(obj.data);bm=bmesh.new();bm.from_mesh(obj.data)
        if bm.calc_volume(signed=True)<-1e-9:inverted.append(obj.name)
        bm.free()
    check('normais externas de prismas fechados',not inverted,inverted)
    count=0
    for wall in cfg['walls']:
        level=wall['level'];base=cfg['levels'][level]['z']
        cells=list(geo.wall_cells(wall,cfg['dimensions']['clear_height']))
        actual=[o for o in bpy.data.objects if o.get('wall_id')==wall['id'] and o.name.startswith('R07 Parede ')]
        check('número de sólidos '+wall['id'],len(actual)==len(cells))
        for i,(a,b,z0,z1) in enumerate(cells):
            obj=bpy.data.objects.get('R07 Parede '+wall['id']+f' {i:02}')
            if obj is None:check('sólido ausente '+wall['id'],False);continue
            poly=geo.wall_polygon(wall,a,b)
            expected=[min(p[0] for p in poly),min(p[1] for p in poly),base+z0,
                      max(p[0] for p in poly),max(p[1] for p in poly),base+z1]
            check('vértices '+obj.name,max(abs(x-y) for x,y in zip(bounds(obj),expected))<2e-5)
            count+=1
        for op in wall.get('openings',[]):
            obj=bpy.data.objects.get('R07 Vao '+op['id']);center=geo.point(wall,op['start']+op['width']/2)
            expected=Vector((center[0],center[1],base+op.get('sill',0)))
            check('vão real '+op['id'],obj is not None and (obj.location-expected).length<2e-5 and abs(obj['width_m']-op['width'])<1e-6)
    # Limites das lajes e abertura real da escada, pelos vértices do arquivo salvo.
    ground_outline=cfg['levels'][0]['slabs'][0]
    check('área bruta térrea coincide com ARQ03',abs(geo.area(ground_outline)-40.77)<1e-6,geo.area(ground_outline))
    check('contorno superior coincide com área total de ARQ03',abs(geo.area(cfg['levels'][1]['outline'])-51.03)<1e-6,geo.area(cfg['levels'][1]['outline']))
    for level in cfg['levels']:
        suffix='Terreo' if level['z']==0 else 'Superior'
        for i,poly in enumerate(level['slabs']):
            obj=bpy.data.objects.get('R07 Laje '+suffix+f' {i:02}')
            check('laje '+suffix+str(i),obj is not None and abs(bounds(obj)[5]-level['z'])<1e-5)
    upper=[o for o in bpy.data.objects if o.get('slab') and o.get('level')==1]
    # Ponto central do vão: nenhum polígono horizontal de laje deve cobri-lo.
    testpoint=Vector((5.8,3.5,2.7))
    def contains(poly,point):
        x,y=point[:2];inside=False
        for a,b in zip(poly,poly[1:]+poly[:1]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
        return inside
    check('vão da escada sem laje',not any(contains([[v.co.x,v.co.y] for v in o.data.vertices[:len(o.data.vertices)//2]],testpoint) for o in upper))
    stair=sorted([o for o in bpy.data.objects if o.get('stair_index')],key=lambda o:o['stair_index'])
    check('16 degraus presentes',[o['stair_index'] for o in stair]==list(range(1,17)))
    check('escada vence 2,70 m',abs(bounds(stair[-1])[5]-2.70)<1e-5)
    check('primeiro espelho 16,875 cm',abs(bounds(stair[0])[5]-.16875)<1e-5)
    check('cobertura correta',len([o for o in bpy.data.objects if o.name.startswith('R07 Telhado ')])==2)
    # Conferência independente com os traços do PDF, extraídos antes da geração.
    sources=json.loads((report/'fontes.json').read_text())
    for item in sources['files']:check('fonte preservada '+item['file'],geo.sha(root/item['file'])==item['sha256'])
    anchors=[(0,'fundos sala',1,5.70),(0,'fundos cozinha',1,7.20),(1,'frente superior',1,-1.20),
             (1,'fundos banheiros',1,6.50),(1,'fundos quarto',1,7.20),(0,'face oeste',0,0),
             (0,'face interna geminada',0,6.25),(1,'divisão principal',0,3.30)]
    anchor_receipts=[]
    for level,label,axis,value in anchors:
        candidates=[]
        for segment in sources['wall_lines_m'][str(level)]:
            a,b=segment
            if abs(a[axis]-b[axis])<.002 and math.dist(a,b)>.25:candidates.append(a[axis])
        nearest=min(candidates,key=lambda v:abs(v-value));error=abs(nearest-value)
        check('PDF independente '+label,error<=.012,{'expected_m':value,'pdf_m':nearest,'error_m':round(error,4)})
        anchor_receipts.append({'anchor':label,'level':level,'expected_m':value,'pdf_m':nearest,'error_m':round(error,4)})
    # Câmeras, visibilidade e camadas: os anexos propostos não contaminam o original.
    for view in cfg['views']:
        scene=bpy.data.scenes.get('R07_'+view['id'])
        if scene is None:continue
        check('câmera '+view['id'],scene.camera is not None and (scene.camera.location-Vector(view['pos'])).length<1e-5)
        check('destino organizado '+view['id'],scene.render.filepath==str(geo.artifact_path(view['id'])))
        check('coleções '+view['id'],set(scene.collection.children.keys())==set(build.scene_collections(view['mode'])))
        if view['mode'].startswith('structure'):
            check('sem mobiliário '+view['id'],not any('Mobiliario' in c.name or 'Proposta' in c.name for c in scene.collection.children))
            check('material neutro '+view['id'],scene.view_layers[0].material_override is not None)
            check('escopo estrutural explícito '+view['id'],bool(scene.get('R07_structural_scope')))
    exploded=bpy.data.collections.get('R07_Superior_Explodido')
    check('vista explodida separada',exploded is not None and len(exploded.objects)>0 and all(o.get('R07_diagram_only') for o in exploded.objects))
    expected_ids={v['id'] for v in cfg['views']};render_status='NOT_REQUESTED'
    if require_renders:
        records=json.loads((report/'renders.json').read_text())
        check('conjunto exato de renders',{r['id'] for r in records}==expected_ids)
        for r in records:
            path=root/r['file']
            check('imagem nativa '+r['id'],geo.valid_render_record(r))
        for name in ['planta-terreo','planta-superior','pavimentos-sobrepostos','corte-longitudinal']:
            for ext in ['svg','pdf','png']:check('planta '+name+'.'+ext,geo.artifact_path(name,ext).is_file())
        check('caderno completo',geo.artifact_path('caderno-residencia-07','pdf').is_file())
        check('galeria completa',geo.artifact_path('painel-geral','jpg').is_file())
        technical=json.loads((report/'instalacoes.json').read_text())
        check('registro das instalações',technical['all_passed'])
        check('caderno técnico íntegro',geo.sha(geo.artifact_path('plantas-tecnicas-residencia-07','pdf'))==technical['pdf_sha256'])
        check('todas as pranchas técnicas',all(geo.artifact_path(name,'pdf').is_file() and geo.artifact_path(name,'svg').is_file() and geo.artifact_path(name).is_file() for name in technical['sheets']))
        render_status='VERIFIED' if all(c['passed'] for c in checks) else 'FAILED'
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'modelo Blender salvo e referências PDF; imagens se --require-renders',
            'unit':'07','blender_version':bpy.app.version_string,'blend_sha256':geo.sha(bpy.data.filepath),
            'checked_wall_solids':count,'source_anchors':anchor_receipts,'checks':checks,
            'all_passed':all(c['passed'] for c in checks),'renders':render_status,
            'area_comparison':[{'room':r['id'],'declared_m2':r['declared_area'],'model_polygon_m2':round(geo.area(r['polygon']),4),'delta_m2':round(geo.area(r['polygon'])-r['declared_area'],4)} for r in cfg['rooms']],
            'unknowns':cfg['source']['notes']}
    (report/('validacao-completa.json' if require_renders else 'validacao-modelo.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('R07_AUDIT',len(checks),'checks','PASSED' if result['all_passed'] else 'FAILED')
    for c in checks:
        if not c['passed']:print('FAIL',c)
    if not result['all_passed']:raise RuntimeError('Falhas na validação da residência 07.')


if __name__=='__main__':main('--require-renders' in sys.argv)
