"""Ensaio de ponto de vista lateral; não altera arquivos de trabalho."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1];s=bpy.context.scene;cam=s.camera
s.cycles.device='CPU';s.cycles.samples=20;s.render.resolution_percentage=50
for o in s.objects:
    if o.name.startswith('MESA_Jantar') or o.name.startswith('Arranjo centro jantar'):o.location.x-=.68
    if o.get('categoria')=='cadeira_jantar':o.location.x-=.68
    if o.name.startswith('Pendente principal jantar'):o.location.x-=.68
    if o.name.startswith('Luz Pendente principal jantar'):o.location.x-=.68
    if o.name.startswith(('MESA_Centro','Arranjo vaso vidro centro','Livros mesa centro')):o.location.x-=1.21;o.location.y+=.15
    if o.name.startswith('Tigela mesa centro'):o.location.x-=1.21;o.location.y+=.15
cam.location=(.5,-.7,1.65);cam.data.lens=23;cam.data.shift_x=0
cam.rotation_euler=(Vector((3.6,6,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(root/'renders/previa-camera-lateral-01.png');bpy.ops.render.render(write_still=True)
cam.location=(.75,-.8,1.65);cam.data.lens=24
cam.rotation_euler=(Vector((3.65,6,1.44))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(root/'renders/previa-camera-lateral-02.png');bpy.ops.render.render(write_still=True)
cam.location=(1.3,-.8,1.65);cam.data.lens=24;cam.data.shift_x=.06
cam.rotation_euler=(Vector((3.15,6,1.40))-cam.location).to_track_quat('-Z','Y').to_euler()
for o in s.objects:
    if o.name.startswith(('MESA_Centro','Arranjo vaso vidro centro','Livros mesa centro','Tigela mesa centro')):o.location.x+=.3
s.render.filepath=str(root/'renders/previa-camera-lateral-03.png');bpy.ops.render.render(write_still=True)
