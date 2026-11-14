import bpy,json
from mathutils import Vector
for name in ['ATC_Reservatorio','ATC_Mobiliario','ATC5_Tecnica','ATC5_Tecnica_Transparente']:
 print('COL',name)
 for o in bpy.data.collections[name].objects:
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]; print(o.name,[round(v,3) for v in o.location], [[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)])
