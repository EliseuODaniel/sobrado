from pathlib import Path
import sys,json
import bpy
sys.path.insert(0,str(Path.cwd()/'scripts'))
import current_photoreal_data as data
from current_photoreal_refinement import orchids
before=data.sha(bpy.data.filepath);details=orchids();s=bpy.data.scenes['FIEL2_sala-foto'];bpy.context.window.scene=s;bpy.context.view_layer.update()
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.cycles.samples=64;s.cycles.adaptive_threshold=.035;s.render.resolution_percentage=33;s.render.filepath=str(data.REPORT/'orquideas-previa.png');bpy.ops.render.render(write_still=True,scene=s.name)
assert data.sha(bpy.data.filepath)==before
print('ORCHIDS_REVIEW_OK',details['flower_count'])
