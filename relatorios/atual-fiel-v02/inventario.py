import bpy,json,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path.cwd()/'scripts'))
from residence07_current import world_matrix
items=[]
for o in bpy.data.objects:
 if not o.name.startswith('ATUAL '):continue
 mat=world_matrix(o)
 pts=[mat@Vector(v) for v in o.bound_box] if o.type in {'MESH','CURVE'} else [mat.translation]
 items.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,collections=[c.name for c in o.users_collection],materials=[s.material.name if s.material else None for s in o.material_slots],center=[round(sum(p[i] for p in pts)/len(pts),4) for i in range(3)],bounds=[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)],vertices=len(o.data.vertices) if o.type=='MESH' else 0))
Path('relatorios/atual-fiel-v02/inventario.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print('INVENTORY',len(items),'scenes',len(bpy.data.scenes))
