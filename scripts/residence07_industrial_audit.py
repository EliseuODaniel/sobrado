"""Auditoria independente do industrial reaberto e de sua arquitetura atual."""
import datetime as dt
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
import residence07_industrial_data as data
import residence07_industrial as model
import industrial_bar_policy


def main(require_renders=False):
    cfg=data.CFG;root=data.ROOT;report=root/cfg['report_directory'];receipt=json.loads((report/'modelo.json').read_text());checks=[]
    def check(name,value,details=None):
        row={'name':name,'passed':bool(value)}
        if details is not None:row['details']=details
        checks.append(row)
    check('hash do modelo salvo',geo.sha(bpy.data.filepath)==receipt['blend_sha256'])
    check('bar industrial sem geladeira',not industrial_bar_policy.bar_fridges())
    check('casa atual preservada',geo.sha(root/receipt['source_blend'])==receipt['source_sha256'])
    check('biblioteca industrial anterior preservada',geo.sha(root/receipt['furniture_library'])==receipt['furniture_library_sha256'])
    check('configuração industrial',geo.sha(data.CONFIG)==receipt['config_sha256'])
    check('configuração oficial',geo.sha(root/cfg['official_config'])==receipt['official_config_sha256'])
    check('configuração da reforma atual',geo.sha(root/cfg['current_config'])==receipt['current_config_sha256'])
    check('geradores usados',all(geo.sha(root/p)==h for p,h in receipt['generators'].items()))
    check('quatro referências preservadas',len(receipt['references'])==4 and all(geo.sha(root/r['file'])==r['sha256'] for r in receipt['references']))
    check('nenhuma biblioteca vinculada no arquivo salvo',not bpy.data.libraries)
    expected=receipt['protected_geometry'];actual=model.protected()
    check('conjunto exato de elementos arquitetônicos',set(actual)==set(expected),len(actual))
    differences=[n for n,h in expected.items() if actual.get(n)!=h]
    check('arquitetura atual inalterada',not differences,differences)
    # Uma segunda leitura do arquivo atual compara a geometria real, além do recibo.
    with bpy.data.libraries.load(str(root/cfg['base_blend']),link=False) as (src,dst):
        # Blender substitui os nomes por Objects: preservar a lista de chaves usando uma cópia.
        names=[n for n in src.objects if n in expected];dst.objects=list(names)
    source=dict(zip(names,dst.objects));delta=[n for n,h in expected.items() if n not in source or model.geometry_fingerprint(source[n])!=h]
    check('comparação independente com o arquivo atual',not delta,delta)
    check('conjunto exato de 25 cenas',len(receipt['jobs'])==25 and set(bpy.data.scenes.keys())=={j['scene'] for j in receipt['jobs']})
    for j in receipt['jobs']:
        scene=bpy.data.scenes[j['scene']];pnames={o.name for o in scene.objects if o.name in expected}
        check('arquitetura visível '+j['id'],pnames==set(j['protected_visibility']))
        check('câmera '+j['id'],scene.camera is not None and (scene.camera.location-Vector(j['pos'])).length<1e-4)
        check('dimensões '+j['id'],[scene.render.resolution_x,scene.render.resolution_y]==cfg['resolution'])
        check('origem atual '+j['id'],scene.get('current_base_sha256')==receipt['source_sha256'])
        scene_config=receipt.get('generation_provenance',{}).get('config_sha256',receipt['config_sha256'])
        check('contrato industrial '+j['id'],scene.get('industrial_config_sha256')==scene_config)
        check('destino organizado '+j['id'],scene.render.filepath==str(root/j['file']))
        office='IND07_Escritorio_Alternativo' in scene.collection.children
        check('escritório isolado '+j['id'],office==(j['mode']=='office'))
        if office:check('sem beliche no escritório '+j['id'],'ATUAL_AMB_quarto_azul' not in scene.collection.children)
    main_scene=bpy.data.scenes['IND07_sala-fundos'];visible={o.name for o in main_scene.objects}
    check('fundo da sala continua aberto',not any(main_scene.objects[n].get('wall_id')=='T-fundos-sala' for n in visible))
    check('cobertura posterior preservada',sum(n.startswith('ATUAL Cobertura vidro') for n in visible)==2)
    check('divisão lazer e lavanderia preservada',any(n.startswith('ATUAL Vidro divisao') for n in visible))
    check('quatro banquetas novas',sum(o.type=='EMPTY' and o.name.startswith('IND07 Banqueta ') for o in main_scene.objects)==4)
    check('sofá de couro importado',any(o.get('industrial_asset_source')=='DESIGN Sofá contemporâneo' for o in main_scene.objects))
    check('mesa de madeira modelada',sum(n.startswith('IND07 Tabua mesa jantar') for n in visible)==4)
    check('todas as imagens usadas empacotadas',all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.users>0))
    if require_renders:
        records=json.loads((report/'renders.json').read_text())
        check('conjunto exato de renders',{r['id'] for r in records}=={j['id'] for j in receipt['jobs']})
        for r in records:check('imagem nativa '+r['id'],not r['preview'] and r['blend_sha256']==receipt['blend_sha256'] and geo.sha(root/r['file'])==r['sha256'])
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':receipt['blend_sha256'],'checks':checks,
        'all_passed':all(c['passed'] for c in checks),'renders_required':require_renders,'scope':'Proposta visual industrial sobre a arquitetura atual documental; não equivale a levantamento ou projeto executivo.'}
    (report/('validacao-completa.json' if require_renders else 'validacao-modelo.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('IND07_AUDIT',len(checks),'PASSED' if result['all_passed'] else 'FAILED')
    for c in checks:
        if not c['passed']:print('FAIL',c)
    if not result['all_passed']:raise RuntimeError('Conferência do industrial reprovada.')


if __name__=='__main__':main('--require-renders' in sys.argv)
