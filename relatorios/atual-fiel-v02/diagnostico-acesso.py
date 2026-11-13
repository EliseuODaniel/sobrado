import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.data.scenes['FIEL2_sala-foto'];bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();cam=s.camera;f=cam.data.view_frame(scene=s);rows=[]
for u in [.26,.28,.30,.32,.34]:
 for v in [.45,.55,.65]:
  p=f[2].lerp(f[1],u).lerp(f[3].lerp(f[0],u),v);d=cam.matrix_world.to_3x3()@p.normalized();hit,loc,n,idx,obj,mat=s.ray_cast(deps,cam.matrix_world.translation,d)
  rows.append({'u':u,'v':v,'hit':obj.name if hit else None,'point':list(loc)})
closed=[{'name':o.name,'location':list(o.matrix_world.translation),'hide_render':o.hide_render,'in_scene':o.name in s.objects,'bounds':[[min((o.matrix_world@Vector(v))[i] for v in o.bound_box),max((o.matrix_world@Vector(v))[i] for v in o.bound_box)] for i in range(3)]} for o in bpy.data.objects if o.type=='MESH' and 'posicao fechada' in o.name and 'Porta P3-entrada' in o.name]
Path('relatorios/atual-fiel-v02/diagnostico-acesso.json').write_text(json.dumps({'rays':rows,'closed':closed},ensure_ascii=False,indent=2));print(json.dumps({'rays':rows,'closed':closed},ensure_ascii=False))
