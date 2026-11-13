"""Aplicar tecidos capturados e refinar o arranjo observado, após a revisão 4K."""
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data
import current_photoreal_refinement as refinement
m=json.loads((data.REPORT/'modelo.json').read_text());input_sha=data.sha(bpy.data.filepath);assert input_sha==m['blend_sha256'];previous=dict(m['generators'])
materials=refinement.fabrics();flowers=refinement.orchids()
for s in bpy.data.scenes:s.use_fake_user=True
bpy.context.window.scene=bpy.data.scenes['FIEL2_sala-foto'];bpy.ops.file.pack_all();dest=data.ROOT/data.CFG['output_blend'];temporary=dest.with_name(dest.stem+'.textiles.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
m['temporary_blend']=temporary.relative_to(data.ROOT).as_posix();m['temporary_sha256']=data.sha(temporary);m['status']='built_pending_reopen';m.setdefault('finish_stages',[]).append({'stage':'Tecidos capturados e orquídea branca após revisão em resolução nativa','input_sha256':input_sha,'output_sha256':m['temporary_sha256'],'fabric_materials':materials,'orchid_refinement':flowers,'fabric_manifest_sha256':data.sha(data.ROOT/'assets/atual-fiel-v02/tecidos/manifesto.json'),'structural_geometry_changed':False,'input_generator_snapshot':previous,'script':'scripts/finish_current_textiles.py','script_sha256':data.sha(Path(__file__))})
for p in ['scripts/finish_current_textiles.py','scripts/current_photoreal_refinement.py','scripts/fetch_current_fabrics.py']:m['generators'][p]=data.sha(data.ROOT/p)
(data.REPORT/'modelo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_TEXTILES_OK',materials,flowers['flower_count'],'flowers',flush=True)
