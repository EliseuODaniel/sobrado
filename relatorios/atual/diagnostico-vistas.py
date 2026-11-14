import bpy,json
from mathutils import Vector
from pathlib import Path
rows=[]
for name in ['FIEL2_banheiro-social','FIEL2_banheiro-suite']:
 s=bpy.data.scenes[name];bpy.context.window.scene=s;bpy.context.view_layer.update();cam=s.camera;f=cam.data.view_frame(scene=s);deps=bpy.context.evaluated_depsgraph_get();origin=cam.matrix_world.translation
 for u in [.50,.65,.75,.85,.95]:
  p=f[2].lerp(f[1],u).lerp(f[3].lerp(f[0],u),.5);d=cam.matrix_world.to_3x3()@p.normalized();hit,loc,n,idx,obj,mat=s.ray_cast(deps,origin,d)
  rows.append({'scene':name,'u':u,'origin':list(origin),'direction':list(d),'hit':obj.name if hit else None,'point':list(loc) if hit else None})
Path('relatorios/atual-fiel-v02/diagnostico-vistas.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps(rows,ensure_ascii=False))
