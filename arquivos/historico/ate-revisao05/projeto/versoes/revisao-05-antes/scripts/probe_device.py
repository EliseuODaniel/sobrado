"""Teste real de enumeração e renderização, sem gravar preferências globais."""
import json
from pathlib import Path
import sys
import bpy

root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
scene=bpy.context.scene
scene.render.engine='CYCLES'
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX'
prefs.get_devices()
devices=[{'name':d.name,'type':d.type} for d in prefs.devices]
gpus=[d for d in prefs.devices if d.type=='OPTIX']
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU' if gpus else 'CPU'
scene.cycles.samples=8
scene.render.resolution_x=128;scene.render.resolution_y=128;scene.render.resolution_percentage=100
scene.render.filepath=str(root/'renders/teste-dispositivo.png')
bpy.ops.render.render(write_still=True)
report={'blender_version':bpy.app.version_string,'devices':devices,'actual_backend':'OPTIX' if gpus else 'CPU','test_render_completed':True}
(root/'relatorios/dispositivo.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('DEVICE_TEST',json.dumps(report),flush=True)
