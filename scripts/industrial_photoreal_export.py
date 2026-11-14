"""Intercâmbio de geometria/UVs e teste de unidade; shaders ficam no Blender."""
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import industrial_photoreal_data as data
from industrial_bar_policy import bar_fridges

ROOT, CFG = data.ROOT, data.CFG
OUT = ROOT / 'exports/industrial'
REPORT = ROOT / CFG['report_directory']


def bounds(obj):
    points = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    return [[min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]]


def export(scene, name):
    bpy.context.window.scene = scene; bpy.context.view_layer.update()
    assert abs(scene.unit_settings.scale_length - 1) < 1e-8
    dest = OUT / (name + '.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest), export_format='GLB', use_active_scene=True,
                             export_materials='PLACEHOLDER', export_apply=True, export_extras=True,
                             export_yup=True, export_texcoords=True, export_normals=True,
                             export_cameras=False, export_lights=False)
    with dest.open('rb') as stream:
        magic, version, length = struct.unpack('<4sII', stream.read(12))
        assert magic == b'glTF' and version == 2 and length == dest.stat().st_size
        size, kind = struct.unpack('<I4s', stream.read(8)); assert kind == b'JSON'
        doc = json.loads(stream.read(size))
    return {'file': str(dest.relative_to(ROOT)), 'sha256': data.sha(dest), 'meshes': len(doc.get('meshes', [])),
            'nodes': len(doc.get('nodes', [])), 'units': 'meters', 'materials': 'named placeholders; not converted shaders'}


def main():
    model = json.loads((REPORT / 'modelo.json').read_text()); assert data.sha(bpy.data.filepath) == model['blend_sha256']
    assert not bar_fridges(); OUT.mkdir(parents=True, exist_ok=True)
    scene = bpy.data.scenes['PHOTO6_fachada-frontal']; bpy.context.window.scene = scene; bpy.context.view_layer.update()
    controls = {o.name: bounds(o) for o in scene.objects if o.type == 'MESH' and o.get('wall_id')}
    controls = dict(sorted(controls.items())[:3]); assert controls
    exports = [export(scene, 'residencia-07-industrial-geometria'), export(bpy.data.scenes['PHOTO6_escritorio-dia'], 'escritorio-alternativo-geometria')]
    assert data.sha(ROOT / model['blend']) == model['blend_sha256']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.ops.mesh.primitive_cube_add(size=1)
    bpy.context.object.name = 'Referencia_1_metro'
    exports.append(export(bpy.context.scene, 'referencia-1-metro'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / exports[-1]['file']))
    bpy.context.view_layer.update(); meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    unit_ok = len(meshes) == 1 and all(abs(d - 1) < 1e-6 for d in meshes[0].dimensions)
    assert unit_ok
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / exports[0]['file'])); bpy.context.view_layer.update()
    differences = {}
    for name, expected in controls.items():
        obj = bpy.data.objects.get(name); assert obj, name
        actual = bounds(obj); delta = max(abs(actual[i][j] - expected[i][j]) for i in range(2) for j in range(3))
        differences[name] = delta; assert delta < .001, (name, delta)
    result = {'blend_sha256': model['blend_sha256'], 'exporter_sha256': data.sha(__file__), 'exports': exports,
              'unit_cube_roundtrip_passed': unit_ok, 'wall_bounds_roundtrip_error_m': differences,
              'source_native_unchanged': data.sha(ROOT / model['blend']) == model['blend_sha256'],
              'scope': 'Geometry and UV interchange. No Unreal import, shader conversion, lighting or runtime performance test.'}
    (REPORT / 'intercambio.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'LEIA-ME.md').write_text('''# Intercâmbio industrial v06

Os GLBs contêm geometria, UVs e nomes dos materiais, em metros. A casa principal e o escritório alternativo são arquivos separados. O cubo de referência mede 1 m em cada eixo e foi reimportado no Blender para conferir a unidade; três paredes da casa também tiveram seus limites comparados, com tolerância de 1 mm.

**Os materiais são placeholders.** Para reproduzir as imagens desta revisão, use o Blender editável, que contém os shaders completos. Materiais procedurais, correções de cor, relevo, vidros, luz e exposição precisam ser convertidos/reconstruídos no Unreal. As texturas licenciadas estão em `assets/fotorrealismo-industrial`; os grafos completos permanecem no `.blend`.

Não houve importação ou benchmark no Unreal. Ao importar, conferir que o cubo de 1 m chega como 100 cm na unidade padrão do motor; este teste ainda está pendente. Recibo em `relatorios/industrial/intercambio.json`.
''')
    print('PHOTO6_EXPORT_VERIFIED', len(exports), differences, flush=True)


if __name__ == '__main__': main()
