"""Correção pontual da primeira geração; mantém cópia anterior para auditoria."""
from pathlib import Path
import shutil
import bpy
root=Path(__file__).resolve().parents[1]
file=Path(bpy.data.filepath)
backup=root/'projeto/versoes/sala-industrial-v01-antes-ajuste-manta.blend'
if backup.exists():raise RuntimeError('A revisão inicial já está preservada; não repetir migração.')
shutil.copy2(file,backup)
o=bpy.data.objects['Manta ondulada sofa']
for v in o.data.vertices:v.co.x=(v.co.x+.16)*(.72/.93)-.16
for o in bpy.data.objects:
    if o.name.startswith('Franja manta'):
        for spline in o.data.splines:
            for p in spline.bezier_points:
                p.co.x-=.21
                p.handle_left.x-=.21;p.handle_right.x-=.21
bpy.context.scene['revisao']='02 — manta ajustada à frente do sofá, sem ocupar mesa de centro'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(file))
print('BLANKET_REFINED_AND_PREVIOUS_VERSION_PRESERVED',flush=True)
