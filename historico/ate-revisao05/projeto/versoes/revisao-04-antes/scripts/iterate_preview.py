"""Ensaio descartável de câmera/materiais, sem sobrescrever .blend nem configuração."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
cam=scene.camera
scene.cycles.device='CPU';scene.cycles.samples=16;scene.render.resolution_percentage=50
cam.location=(3.6,-.3,1.65)
cam.rotation_euler=(Vector((3.18,6,1.32))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=19
scene.view_settings.exposure=-.45
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for node in mat.node_tree.nodes:
        if node.type=='VALTORGB':
            factor=.40 if mat.name.startswith('Pedra quadrada') else .55 if mat.name=='Couro caramelo' else .63 if 'Madeira' in mat.name else .80 if mat.name in ['Concreto quente','Reboco painel TV','Porcelanato acetinado'] else 1
            for e in node.color_ramp.elements:
                e.color=tuple(c*factor for c in e.color[:3])+(1,)
for o in scene.objects:
    if o.type=='LIGHT' and o.name.startswith('Claridade cobertura'):o.data.energy*=.60
    if o.type=='LIGHT' and o.name.startswith(('Preenchimento','Luz natural frontal')):o.data.energy*=.50
    if o.name.startswith(('MESA_Centro','Arranjo vaso vidro centro','Livros mesa centro')):o.location.y+=.45
    if o.name.startswith('Tigela mesa centro'):o.location.y+=.45
    if o.name.startswith('TV_Painel e rack'):o.location.y+=.9
    if o.name.startswith(('Vaso alto sobre rack','Livros rack','Luminaria vidro rack')):o.location.y+=.9
    if o.name.startswith('Tigela rack'):o.location.y+=.9
    if o.name.startswith('Luz barra ambar'):o.location.y+=.9
    if o.name.startswith('Luminaria vidro rack') and o.type=='LIGHT':o.location.y+=.9
scene.render.filepath=str(root/'renders/previa-ajuste-01.png')
bpy.ops.render.render(write_still=True)
# Segunda hipótese conserva os objetos e testa lente e visada.
cam.location=(3.65,-.35,1.65)
cam.rotation_euler=(Vector((3.15,6,1.42))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=21
scene.render.filepath=str(root/'renders/previa-ajuste-02.png')
bpy.ops.render.render(write_still=True)
