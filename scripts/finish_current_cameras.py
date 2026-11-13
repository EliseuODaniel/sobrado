"""Calibração final dos enquadramentos após inspecionar as prévias; sem mudar geometria."""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data
m=json.loads((data.REPORT/'modelo.json').read_text());input_sha=data.sha(bpy.data.filepath);assert input_sha==m['blend_sha256']
previous=dict(m['generators']);fresh={j['id']:j for j in data.jobs()};changed=[]
for job in m['jobs']:
    if job['id'] not in {'banheiro-social','banheiro-suite'}:continue
    new=fresh[job['id']];s=bpy.data.scenes[job['scene']];s.camera.location=new['pos'];s.camera.rotation_euler=(Vector(new['target'])-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=new['lens']
    job.update({k:new[k] for k in ['pos','target','lens']});changed.append(job['id'])
assert len(changed)==2
bpy.context.window.scene=bpy.data.scenes['FIEL2_sala-foto']
for s in bpy.data.scenes:s.use_fake_user=True
bpy.ops.file.pack_all();dest=data.ROOT/data.CFG['output_blend'];temporary=dest.with_name(dest.stem+'.cameras.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
m['temporary_blend']=temporary.relative_to(data.ROOT).as_posix();m['temporary_sha256']=data.sha(temporary);m['status']='built_pending_reopen'
m.setdefault('finish_stages',[]).append({'stage':'Câmeras dos dois banheiros após revisão das prévias','input_sha256':input_sha,'output_sha256':m['temporary_sha256'],'changed_views':changed,'geometry_changed':False,'input_generator_snapshot':previous,'script':'scripts/finish_current_cameras.py','script_sha256':data.sha(Path(__file__))})
for p in ['scripts/finish_current_cameras.py','scripts/current_photoreal_data.py','scripts/current_photoreal_audit.py']:m['generators'][p]=data.sha(data.ROOT/p)
(data.REPORT/'modelo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_CAMERAS_OK',','.join(changed),flush=True)
