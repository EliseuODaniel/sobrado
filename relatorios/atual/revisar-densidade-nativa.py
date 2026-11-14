import json,struct,time,sys
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'scripts'))
import current_photoreal_data as data
m=json.loads((data.REPORT/'modelo.json').read_text());assert data.sha(bpy.data.filepath)==m['blend_sha256']
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices();assert any(d.type=='OPTIX' for d in p.devices)
for d in p.devices:d.use=d.type=='OPTIX'
s=bpy.data.scenes['FIEL2_sala-foto'];bpy.context.window.scene=s;s.cycles.device='GPU'
out=data.REPORT/'revisao-refinamento';out.mkdir(exist_ok=True)
s.render.resolution_percentage=33;s.cycles.samples=64;s.cycles.adaptive_threshold=.035;s.render.filepath=str(out/'sala-previa.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.render.resolution_percentage=100;s.cycles.samples=data.CFG['samples'];s.cycles.adaptive_threshold=data.CFG['adaptive_threshold'];s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=.38;s.render.border_max_x=.74;s.render.border_min_y=.20;s.render.border_max_y=.59;s.render.filepath=str(out/'tecidos-densidade-nativa.png')
start=time.monotonic();bpy.ops.render.render(write_still=True,scene=s.name);file=out/'tecidos-densidade-nativa.png'
with file.open('rb') as f:header=f.read(29)
row={'blend_sha256':m['blend_sha256'],'file':file.relative_to(root).as_posix(),'sha256':data.sha(file),'crop_fraction':[.38,.74,.20,.59],'parent_resolution':[s.render.resolution_x,s.render.resolution_y],'actual_crop_resolution':list(struct.unpack('>II',header[16:24])),'samples':s.cycles.samples,'backend':'OPTIX','seconds':round(time.monotonic()-start,2),'note':'Recorte renderizado com densidade de pixels do PNG final, sem redimensionar a imagem nem salvar o modelo.'}
(out/'recorte-recibo.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');assert data.sha(bpy.data.filepath)==m['blend_sha256'];print('CURRENT2_DENSITY_REVIEW_OK',row['seconds'],flush=True)
