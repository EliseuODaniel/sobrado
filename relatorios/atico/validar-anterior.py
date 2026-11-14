import bpy
from mathutils import Vector
bpy.context.window.scene=bpy.data.scenes['CAIXA_LATERAL_Planta'];bpy.context.view_layer.update()
t=[o for o in bpy.data.collections['ATC_Reservatorio'].objects if o.get('capacity_liters')][0]
p=[t.matrix_world@Vector(v) for v in t.bound_box]
lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
assert lo[0]>4 and lo[1]>4.15
assert abs(hi[0]-lo[0]-1.52)<1e-4 and abs(hi[2]-lo[2]-.97)<1e-4
assert len(bpy.data.collections['PROPOSTA_Reserva_Manutencao'].objects)==0
assert len([o for o in bpy.data.collections['ATC5_Escada'].objects if o.get('stair_index')])==16
print('CAIXA_CANTO_REABERTO_OK: fora da faixa da janela, fora do vão, envelope 1,52 x 0,97 m, escada preservada')
