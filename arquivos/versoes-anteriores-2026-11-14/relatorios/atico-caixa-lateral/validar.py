import bpy
from mathutils import Vector
s=bpy.data.scenes['CAIXA_LATERAL_Planta']; bpy.context.window.scene=s; bpy.context.view_layer.update()
t=[o for o in bpy.data.collections['ATC_Reservatorio'].objects if o.get('capacity_liters')][0]
assert (t.location-Vector((2.8,5,5.45))).length<1e-6
assert len(bpy.data.collections['ATC_Reservatorio'].objects)==4
assert len(bpy.data.collections['ATC5_Tecnica'].objects)==0
assert len(bpy.data.collections['ATC5_Tecnica_Transparente'].objects)==0
assert len([o for o in bpy.data.collections['ATC5_Escada'].objects if o.get('stair_index')])==16
assert len([x for x in bpy.data.scenes if x.name.startswith('ATICO_TRANSPARENTE_')])==2
print('VALIDACAO_ARQUIVO_REABERTO_OK: caixa, três tubos antigos removidos, divisórias antigas removidas, 16 degraus preservados, cenas de entrega presentes')
