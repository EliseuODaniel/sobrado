import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'scripts'))
from residence07_current import world_matrix
rows=[]
for o in bpy.data.objects:
 if any(c.name in {'R07_Esquadrias_Terreo','R07_Esquadrias_Superior'} for c in o.users_collection):rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'location':list(world_matrix(o).translation),'matrix_world':[list(r) for r in world_matrix(o)],'collections':[c.name for c in o.users_collection]})
Path('relatorios/atual-fiel-v02/esquadrias-originais.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
