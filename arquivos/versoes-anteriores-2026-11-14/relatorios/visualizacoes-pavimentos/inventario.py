import bpy,json,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
rows=[]
for s in bpy.data.scenes:
 rows.append({'scene':s.name,'collections':[c.name for c in s.collection.children]})
cols=[]
for c in bpy.data.collections:
 if not c.objects: continue
 pts=[o.matrix_world@Vector(p) for o in c.all_objects if o.type=='MESH' for p in o.bound_box]
 cols.append({'name':c.name,'count':len(c.all_objects),'z':[round(min(p.z for p in pts),2),round(max(p.z for p in pts),2)] if pts else None})
key=sys.argv[-1]
(root/'relatorios/visualizacoes-pavimentos'/('inventario-'+key+'.json')).write_text(json.dumps({'scenes':rows,'collections':cols},ensure_ascii=False,indent=2),encoding='utf-8')
