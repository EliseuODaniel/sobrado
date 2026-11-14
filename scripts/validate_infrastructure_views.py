"""Valida o Blender reaberto, sem renderizar imagens."""
from pathlib import Path
import json, hashlib
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
report = ROOT/'relatorios/infraestrutura'
record = json.loads((report/'modelo.json').read_text(encoding='utf-8'))
path = ROOT/record['blend']
bpy.ops.wm.open_mainfile(filepath=str(path))
assert bpy.context.window.scene.name == record['default_scene']
assert len(bpy.data.scenes) == 7
assert hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest() == record['source_sha256']
assert all(c.name.startswith('INFRA_') for c in bpy.data.collections)
full = bpy.data.scenes['INFRA_04_CONJUNTO_FORRO_CAIXA']
bpy.context.window.scene = full; full.frame_set(full.frame_current); bpy.context.view_layer.update()
tank = next(o for o in bpy.data.collections['INFRA_Caixa_Original'].objects if o.get('capacity_liters'))
assert (tank.matrix_world.translation-Vector((5.35, 3.175, 5.45))).length < 1e-4
assert not any('ATC' in o.name or 'atico' in o.name.lower() for s in bpy.data.scenes for o in s.objects)
nodes = {n['id']: n for n in record['graph']['nodes']}
checked = 0; markers = 0
for system in ['cold', 'hot', 'electric', 'overflow', 'drain']:
    col = bpy.data.collections['INFRA_Rede_'+system]
    for obj in col.objects:
        if 'graph_edge_index' in obj:
            edge = record['graph']['edges'][obj['graph_edge_index']]
            points = [obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
            assert len(points) == 2
            assert (points[0]-Vector(nodes[edge['a']]['xyz'])).length < 1e-4
            assert (points[1]-Vector(nodes[edge['b']]['xyz'])).length < 1e-4
            checked += 1
        if obj.get('network_node'):
            assert (obj.matrix_world.translation-Vector(nodes[obj['network_node']]['xyz'])).length < 1e-4
            markers += 1
for name in ['INFRA_Forro_Terreo', 'INFRA_Forro_Superior']:
    col = bpy.data.collections[name]; assert len(col.objects) > 0, name
    for obj in col.objects:
        assert obj.data.materials[0]['presentation_opacity'] < .1
for name in ['INFRA_Arquitetura_Terreo', 'INFRA_Arquitetura_Superior']:
    walls = [o for o in bpy.data.collections[name].objects if o.get('wall_id')]
    assert walls and all('CORTE ' not in o.name for o in walls)
for name in ['INFRA_01_COMPARACAO_GERAL', 'INFRA_02_COMPARACAO_ELETRICA', 'INFRA_03_COMPARACAO_HIDRAULICA']:
    scene = bpy.data.scenes[name]; bpy.context.window.scene = scene
    scene.frame_set(scene.frame_current); bpy.context.view_layer.update()
    tanks = [o for o in scene.objects if o.get('capacity_liters')]
    assert len(tanks) == 1
    assert (tanks[0].matrix_world.translation-Vector((10.55, 3.175, 5.45))).length < 1e-4
    # Cada marcador deve conservar a posição da rede após o deslocamento do painel.
    for obj in scene.objects:
        if obj.get('wall_id'):
            for corner in obj.bound_box:
                projected = world_to_camera_view(scene, scene.camera, obj.matrix_world@Vector(corner))
                assert 0 <= projected.x <= 1 and 0 <= projected.y <= 1, (name, obj.name, tuple(projected))
        node_id = obj.get('network_node')
        if node_id:
            dx = -5.2 if ' TERREO ' in obj.name else 5.2
            expected = Vector(nodes[node_id]['xyz'])+Vector((dx, 0, 0))
            assert (obj.matrix_world.translation-expected).length < 1e-4, obj.name
result = dict(status='passed', scenes=7, tank_original_xyz=[5.35, 3.175, 5.45],
              attic_present=False, full_network_segments_verified=checked,
              point_positions_verified=markers, forros_translucent=True,
              comparison_walls_in_camera_frame=True,
              original_sources_preserved=True, new_images_rendered=False,
              executable_design_verified=False,
              limitations='Traçados 3D são interpretativos; conexões reais, dimensionamento e interferências não verificados.')
(report/'validacao.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('INFRA_VALIDACAO_OK', result, flush=True)
