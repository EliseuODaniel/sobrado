"""Reabrir a variante industrial e validar a entrega sem alterar o .blend."""
import datetime as dt
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from style_industrial import geometry, sha
import audit_envelope

root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/'config/estilo-industrial-v01.json').read_text())
folder=root/cfg['report_directory'];model=json.loads((folder/'modelo.json').read_text())
file=Path(bpy.data.filepath);before=sha(file);checks={}
def check(name,ok,detail):
    checks[name]={'passed':bool(ok),'detail':detail}
    assert ok,(name,detail)
check('arquivo_e_base',before==model['blend_sha256'] and sha(root/cfg['base_blend'])==model['base_sha256'],{'blend_sha256':before,'base_sha256':model['base_sha256']})
now=geometry();differences=[n for n,v in model['original_geometry_sha256'].items() if now.get(n)!=v]
check('geometria_herdada_preservada',not differences,{'objects':len(model['original_geometry_sha256']),'differences':differences})
check('cena_inicial_industrial',bpy.context.scene.name=='IND_Sala_Integrada',bpy.context.scene.name)
check('sete_cenas_editaveis',all(bpy.data.scenes.get(j['scene']) is not None for j in cfg['jobs']),[j['scene'] for j in cfg['jobs']])
expected={'AMB_sala':'IND Couro caramelo','AMB_jantar':'IND Nogueira','AMB_cozinha':'IND Grafite','AMB_bar':'IND Nogueira','AMB_quarto_azul':'IND Azul petróleo'}
actual={c:sorted({slot.material.name for obj in bpy.data.collections[c].objects if hasattr(obj,'material_slots') for slot in obj.material_slots if slot.material}) for c in expected}
check('materiais_nos_quatro_ambientes',all(mat in actual[c] for c,mat in expected.items()),actual)
external=[]
for mat in bpy.data.materials:
    if not mat.name.startswith('IND ') or not mat.use_nodes:continue
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE' and (node.image is None or not node.image.packed_file):external.append([mat.name,node.name])
check('revestimentos_industriais_sem_dependencias_externas',not external,external)
photos=[i for i in bpy.data.images if i.name.endswith('.webp') and i.packed_file]
check('fotos_originais_empacotadas',len(photos)==26,{'count':len(photos),'style_references_location':cfg['references'],'style_references_embedded':False})
envelope=audit_envelope.audit(json.loads((root/'config/planta-casa.json').read_text()))
check('encaixe_dos_pavimentos',envelope['all_passed'],envelope)
check('arquivo_preservado',sha(file)==before,before)
(folder/'validacao.json').write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':before,'checks':checks,'all_passed':True},ensure_ascii=False,indent=2)+'\n')
print('INDUSTRIAL_AUDIT_PASSED',len(checks),flush=True)
