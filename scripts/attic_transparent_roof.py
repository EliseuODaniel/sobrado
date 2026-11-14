"""Cria uma cópia de apresentação do ático v05, com cobertura transparente."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'arquivos/versoes-anteriores-2026-11-14/projeto/residencia-07-atico-v05/atico-telhado-transparente.blend'
OUT = ROOT / 'arquivos/versoes-anteriores-2026-11-14/renders/atico-telhado-transparente'
assert not DEST.exists(), f'Preserve a entrega existente antes de gerar: {DEST}'
OUT.mkdir(parents=True, exist_ok=True)

# Mistura sem refração: a finalidade é ler o interior, como em uma maquete.
mat = bpy.data.materials.new('Apresentação / cobertura 96% transparente')
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
mix = nodes.new('ShaderNodeMixShader')
mix.inputs[0].default_value = .96
surface = nodes.new('ShaderNodeBsdfDiffuse')
surface.inputs['Color'].default_value = (.25, .55, .65, 1)
transparent = nodes.new('ShaderNodeBsdfTransparent')
mat.node_tree.links.new(surface.outputs[0], mix.inputs[1])
mat.node_tree.links.new(transparent.outputs[0], mix.inputs[2])
mat.node_tree.links.new(mix.outputs[0], output.inputs['Surface'])
mat.diffuse_color = (.25, .55, .65, .04)
shells = ['ATC3_Cobertura_Transparente', 'ATC4_Forro_Transparente',
          'ATC_Oitoes_Transparentes', 'ATC3_Fachadas_Transparentes']
changed = []
for name in shells:
    for obj in bpy.data.collections[name].all_objects:
        if obj.type == 'MESH':
            obj.data = obj.data.copy()
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            changed.append(obj.name)

base = bpy.data.scenes['ATC5_atico-aberturas-transparente']
jobs = [ ('perspectiva-frontal', (13, -12, 20)),
         ('perspectiva-posterior', (-10, 16, 21)) ]
scenes = []
for name, position in jobs:
    scene = base.copy()
    scene.name = 'ATICO_TRANSPARENTE_' + name
    scene.use_fake_user = True
    camera = base.camera.copy()
    camera.data = base.camera.data.copy()
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = position
    camera.rotation_euler = (Vector((3.175, 3, 6.7)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 12.5
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.transparent_max_bounces = 64
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(OUT / (name + '.png'))
    scene['presentation_note'] = 'Telhado e forro transparentes para leitura; não representa material construtivo.'
    scenes.append(scene)

prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()
    gpu = any(d.type == 'CUDA' for d in prefs.devices)
    for device in prefs.devices:
        device.use = device.type == 'CUDA'
except Exception:
    gpu = False
for scene in scenes:
    scene.cycles.device = 'GPU' if gpu else 'CPU'
bpy.context.window.scene = scenes[0]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.shading.type = 'MATERIAL'
assert changed and all(bpy.data.collections[n].name in base.collection.children for n in shells)
bpy.ops.wm.save_as_mainfile(filepath=str(DEST), compress=True)
for scene in scenes:
    bpy.context.window.scene = scene
    bpy.ops.render.render(write_still=True, scene=scene.name)
(OUT / 'verificacao.json').write_text(json.dumps({'blend': str(DEST.relative_to(ROOT)), 'transparent_objects': len(changed), 'renders': [Path(s.render.filepath).name for s in scenes], 'gpu': gpu}, indent=2), encoding='utf-8')
print('ATICO_TRANSPARENTE_OK', len(changed), flush=True)
