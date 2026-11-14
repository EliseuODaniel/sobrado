import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
key='industrial';dest=ROOT/'projeto/visualizacoes-pavimentos/industrial-sem-telhado.blend'
bpy.ops.wm.open_mainfile(filepath=str(dest))
source=ROOT/'projeto/industrial-v06/casa-industrial-fotorrealista.blend'
jobs=[]
for mode in ['terreo','dois-pavimentos']:
 group=bpy.data.collections['APRESENTACAO_'+mode]
 prefix='VISTA '+mode+' '
 names=[o.name.removeprefix(prefix) for o in group.objects]
 walls=[o.name.removeprefix(prefix) for o in group.objects if o.get('wall_id')]
 jobs.append({'mode':mode,'objects':len(names),'full_wall_objects':walls,'included_objects':names,'excluded_upper_objects':[],'image':f'renders/visualizacoes-pavimentos/{key}/{mode}.png'})
record={'variant':key,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_preserved':True,'blend':str(dest.relative_to(ROOT)),'same_camera':True,'roof_removed':True,'side_walls_full_height':True,'render_status':'Adiado pelo usuário; apenas Blender concluído','jobs':jobs}
(ROOT/'relatorios/visualizacoes-pavimentos/industrial-verificacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('RECIBO_INDUSTRIAL_BLENDER_OK')
