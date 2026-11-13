"""Conferência do acesso: cortina limitada à parede reta e folha fechada na apresentação."""
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data
from residence07_current import world_matrix
m=json.loads((data.REPORT/'modelo.json').read_text());input_sha=data.sha(bpy.data.filepath);assert input_sha==m['blend_sha256'];previous=dict(m['generators'])
changed=[]
curtain=bpy.data.objects['FIEL2 Cortina sala voil'];left=min(v.co.x for v in curtain.data.vertices);right=max(v.co.x for v in curtain.data.vertices);factor=(2.63-.18)/(right-left)
for o in bpy.data.objects:
    if not o.name.startswith('FIEL2 Cortina sala'):continue
    o.data=o.data.copy()
    if o.type=='MESH':
        for v in o.data.vertices:v.co.x=.18+(v.co.x-left)*factor
    elif o.type=='CURVE':
        for spline in o.data.splines:
            for p in spline.points:p.co.x=.18+(p.co.x-left)*factor
    changed.append(o.name)
o=bpy.data.objects['FIEL2 Cortineiro sala'];o.location.x=1.42;o.scale.x*=2.52/o.dimensions.x
proxies=[bpy.data.collections['FIEL2_Apresentacao_ATUAL_Arquitetura'],bpy.data.collections['FIEL2_Vizinho_Contexto']]
for old_copy in list(bpy.data.objects):
    if old_copy.name.startswith(('FIEL2 Entrada fechada ','FIEL2 Porta em posicao fechada ')):bpy.data.objects.remove(old_copy,do_unlink=True)
closed_doors=[]
for hinge in list(bpy.data.objects):
    if not hinge.name.startswith('ATUAL BASE R07 Folha '):continue
    door_id=hinge.name.removeprefix('ATUAL BASE R07 Folha ')
    hinge_world=world_matrix(hinge);closed=hinge_world@Matrix.Rotation(math.radians(-170),4,'Z');delta=closed@hinge_world.inverted_safe()
    for part in ['Porta ','Maçaneta ']:
        name='ATUAL BASE R07 '+part+door_id;old=bpy.data.objects.get(name)
        if old is None:continue
        new=old.copy();new.name='FIEL2 Porta em posicao fechada '+name;new.parent=None;new.matrix_world=delta@world_matrix(old);new['presentation_pose']='closed';new['official_source_object']=old.name
        for c in proxies:
            if old.name in c.objects:c.objects.unlink(old)
            c.objects.link(new)
    closed_doors.append(door_id)
for s in bpy.data.scenes:s.use_fake_user=True
bpy.context.window.scene=bpy.data.scenes['FIEL2_sala-foto'];bpy.ops.file.pack_all();dest=data.ROOT/data.CFG['output_blend'];temporary=dest.with_name(dest.stem+'.entry.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
m['temporary_blend']=temporary.relative_to(data.ROOT).as_posix();m['temporary_sha256']=data.sha(temporary);m['status']='built_pending_reopen'
m.setdefault('finish_stages',[]).append({'stage':'Cortina dentro da parede reta e folhas em posição fechada, sem atravessar ambientes adjacentes','input_sha256':input_sha,'output_sha256':m['temporary_sha256'],'changed_furniture':changed,'structural_geometry_changed':False,'official_opening_preserved':True,'closed_doors':closed_doors,'input_generator_snapshot':previous,'script':'scripts/finish_current_entry.py','script_sha256':data.sha(Path(__file__))})
for p in ['scripts/finish_current_entry.py','scripts/current_photoreal_furniture.py','scripts/current_photoreal_audit.py']:m['generators'][p]=data.sha(data.ROOT/p)
(data.REPORT/'modelo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_ENTRY_OK',len(changed),'curtain objects',flush=True)
