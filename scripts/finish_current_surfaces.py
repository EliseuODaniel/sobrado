"""Conferência final de superfícies: banheiro branco e UVs dos acabamentos existentes."""
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data
from current_photoreal_materials import metric_uv,assign
m=json.loads((data.REPORT/'modelo.json').read_text());input_sha=data.sha(bpy.data.filepath);assert input_sha==m['blend_sha256'];previous=dict(m['generators']);changed=[];uv_fixed=[]
ceramic=bpy.data.materials['FIEL2 Ceramica']
for o in bpy.data.objects:
    if o.name.startswith('ATUAL R07 Faixa azulejo inferior'):assign(o,ceramic);changed.append(o.name)
    if o.type!='MESH' or o.data.uv_layers.get('FIEL2_Metros'):continue
    uses_metric=any(s.material and s.material.use_nodes and any(n.type=='UVMAP' and n.uv_map=='FIEL2_Metros' for n in s.material.node_tree.nodes) for s in o.material_slots)
    if uses_metric:metric_uv(o);uv_fixed.append(o.name)
for s in bpy.data.scenes:s.use_fake_user=True
bpy.context.window.scene=bpy.data.scenes['FIEL2_sala-foto'];bpy.ops.file.pack_all();dest=data.ROOT/data.CFG['output_blend'];temporary=dest.with_name(dest.stem+'.surfaces.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
m['temporary_blend']=temporary.relative_to(data.ROOT).as_posix();m['temporary_sha256']=data.sha(temporary);m['status']='built_pending_reopen';m.setdefault('finish_stages',[]).append({'stage':'Revestimento branco nos banheiros e coordenadas de textura dos acabamentos','input_sha256':input_sha,'output_sha256':m['temporary_sha256'],'material_assignments':changed,'metric_uv_repaired':uv_fixed,'structural_geometry_changed':False,'input_generator_snapshot':previous,'script':'scripts/finish_current_surfaces.py','script_sha256':data.sha(Path(__file__))})
for p in ['scripts/finish_current_surfaces.py','scripts/current_photoreal_materials.py','scripts/current_photoreal_details.py']:m['generators'][p]=data.sha(data.ROOT/p)
(data.REPORT/'modelo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_SURFACES_OK',len(changed),'white bathroom panels',len(uv_fixed),'UV repairs',flush=True)
