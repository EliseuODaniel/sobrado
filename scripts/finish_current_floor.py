"""Segundo estágio: laminado claro dos dormitórios, sem alterar as lajes oficiais."""
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data
import current_photoreal_materials as mat

m=json.loads((data.REPORT/'modelo.json').read_text())
assert data.sha(bpy.data.filepath)==m['temporary_sha256']
source=m['temporary_blend'];input_sha=m['temporary_sha256']
floor=mat.basic('Laminado claro fotografado',(.55,.52,.46),.40)
mat.scanned_surface(floor,'wood_table_001',(.38,.355,.31),(.66,.63,.565),.9,.08)
n,l=floor.node_tree.nodes,floor.node_tree.links;p=n.get('Principled BSDF')
uv=n.new('ShaderNodeUVMap');uv.uv_map='FIEL2_Metros';brick=n.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=1.20;brick.inputs['Row Height'].default_value=.19;brick.inputs['Mortar Size'].default_value=.0007;brick.inputs['Mortar Smooth'].default_value=.0002;l.new(uv.outputs[0],brick.inputs[0])
bump=n.new('ShaderNodeBump');bump.invert=True;bump.inputs['Distance'].default_value=.00045;bump.inputs['Strength'].default_value=.16
if p.inputs['Normal'].links:l.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
changed=[]
for o in bpy.data.objects:
    if o.type!='MESH' or 'Laje Superior' not in o.name:continue
    o.data=o.data.copy();idx=len(o.data.materials);o.data.materials.append(floor)
    for f in o.data.polygons:
        if f.normal.z>.5:f.material_index=idx
    mat.metric_uv(o);changed.append(o.name)
assert changed
cfg=json.loads((data.ROOT/'config/residencia-07.json').read_text());col=bpy.data.collections['FIEL2_Mobiliario_Superior'];tile=bpy.data.materials['FIEL2 Porcelanato bege polido']
for room in cfg['rooms']:
    if room['id'] not in ['banheiro-suite','banheiro-social']:continue
    points=[(x,y,2.703) for x,y in room['polygon']];d=bpy.data.meshes.new('FIEL2 Piso ceramico '+room['id']);d.from_pydata(points,[],[tuple(range(len(points)))]);d.update()
    if d.polygons[0].normal.z<0:d.clear_geometry();d.from_pydata(points,[],[tuple(reversed(range(len(points))))]);d.update()
    d.materials.append(tile);o=bpy.data.objects.new(d.name,d);col.objects.link(o);mat.metric_uv(o);o['floor_finish_only']=True
for s in bpy.data.scenes:s.use_fake_user=True
bpy.context.window.scene=bpy.data.scenes['FIEL2_sala-foto'];bpy.ops.file.pack_all()
target=data.ROOT/data.CFG['output_blend'];temporary=target.with_name(target.stem+'.finishing.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
m['build_temporary_blend']=source;m['build_temporary_sha256']=input_sha;m['temporary_blend']=temporary.relative_to(data.ROOT).as_posix();m['temporary_sha256']=data.sha(temporary)
m['finish_stages']=[{'stage':'laminado claro e cerâmica dos banheiros','input_blend':source,'input_sha256':input_sha,'output_blend':m['temporary_blend'],'output_sha256':m['temporary_sha256'],'script':'scripts/finish_current_floor.py','script_sha256':data.sha(Path(__file__)),'changed_floor_objects':changed}]
m['generators']['scripts/finish_current_floor.py']=data.sha(Path(__file__))
(data.REPORT/'modelo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_FLOOR_FINISH_OK',len(changed),'floor objects',flush=True)
