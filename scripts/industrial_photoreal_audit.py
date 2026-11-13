"""Reabre e confere geometria, recursos, cenas e imagens da industrial v06."""
import datetime as dt
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import residence07_industrial as base
import industrial_photoreal_data as data
import industrial_bar_policy


def camera_in_wall(scene, expected):
    origin = scene.camera.location
    for obj in scene.objects:
        if obj.name not in expected or obj.type != 'MESH' or not obj.get('wall_id'): continue
        matrix = base.world(obj); points = [matrix @ v.co for v in obj.data.vertices]
        if not all(min(p[i] for p in points) + 1e-5 < origin[i] < max(p[i] for p in points) - 1e-5 for i in range(3)): continue
        tree = BVHTree.FromPolygons(points, [list(f.vertices) for f in obj.data.polygons])
        direction = Vector((1, .231, .173)).normalized(); position = origin.copy(); hits = 0
        for _ in range(16):
            hit, normal, face, distance = tree.ray_cast(position, direction, 100)
            if hit is None: break
            hits += 1; position = hit + direction * .00001
        if hits % 2: return obj.name
    return None


def main(require_renders=False):
    root, cfg = data.ROOT, data.CFG; folder = root / cfg['report_directory']
    receipt = json.loads((folder / 'modelo.json').read_text()); checks = []

    def check(name, passed, detail=None):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})

    check('hash do modelo reaberto', data.sha(bpy.data.filepath) == receipt['blend_sha256'])
    check('base v05 preservada', data.sha(root / receipt['source_blend']) == receipt['source_sha256'])
    check('configuração exata', data.sha(data.CONFIG) == receipt['config_sha256'])
    check('geradores exatos', all(data.sha(root / p) == h for p, h in receipt['generators'].items()))
    native_libraries = [library.filepath for library in bpy.data.libraries]
    expected = receipt['protected_geometry']; actual = base.protected()
    check('mesmo conjunto arquitetônico', set(expected) == set(actual), len(actual))
    differences = [n for n, value in expected.items() if actual.get(n) != value]
    check('geometria arquitetônica inalterada', not differences, differences)
    with bpy.data.libraries.load(str(root / cfg['base_blend']), link=False) as (src, dst):
        names = [n for n in src.objects if n in expected]; dst.objects = list(names)
    source = dict(zip(names, dst.objects))
    differences = [n for n, value in expected.items() if n not in source or base.geometry_fingerprint(source[n]) != value]
    check('comparação independente com a base', not differences, differences)
    for obj in dst.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    deletion = json.loads((folder / 'descarte-v04.json').read_text())
    check('todos os alvos v04 ausentes', all(not (root / p).exists() for p in deletion['targets']))
    maintenance = json.loads((folder / 'remocao-geladeiras-fontes.json').read_text())
    v05_change = next(r for r in maintenance if r['file'] == cfg['base_blend'])
    check('manutenção autorizada da fonte v05', v05_change['before_sha256'] == deletion['preserved_native_files'][cfg['base_blend']] and v05_change['after_sha256'] == receipt['source_sha256'])
    check('demais arquivos nativos preservados', all(data.sha(root / p) == h for p, h in deletion['preserved_native_files'].items() if p != cfg['base_blend']))
    check('bar sem geladeira', not industrial_bar_policy.bar_fridges())
    check('geladeira da cozinha preservada', any(o.type == 'EMPTY' and 'geladeira cozinha' in o.name.casefold() for o in bpy.data.objects))
    check('biblioteca extraída disponível', data.sha(root / deletion['library']) == deletion['library_sha256'])
    check('quatro referências preservadas', len(receipt['references']) == 4 and all(data.sha(root / r['file']) == r['sha256'] for r in receipt['references']))
    check('sem bibliotecas externas vinculadas no arquivo salvo', not native_libraries, native_libraries)
    check('imagens necessárias empacotadas', all(im.packed_file for im in bpy.data.images if im.source == 'FILE' and im.users))
    assets = json.loads((root / cfg['asset_manifest']).read_text())['records']
    check('19 arquivos oficiais íntegros', len(assets) == 19 and all(data.sha(root / r['path']) == r['sha256'] for r in assets))
    check('todos os recursos oficiais CC0', all(r['license'] == 'CC0-1.0' for r in assets))
    check('três interfaces de tela empacotadas', len([im for im in bpy.data.images if im.name.startswith('editor-') and im.packed_file]) == 3)
    check('31 cenas exatas', set(bpy.data.scenes.keys()) == {j['scene'] for j in receipt['jobs']})
    missing_uv = [o.name for o in bpy.data.objects if o.type == 'MESH' and any(s.material and s.material.get('uv_units') == 'meters' for s in o.material_slots) and 'PHOTO6_Metros' not in o.data.uv_layers]
    check('coordenadas métricas em todas as malhas PBR correspondentes', not missing_uv, missing_uv)
    check('rodapés modelados', receipt['details']['skirting_segments'] > 0, receipt['details']['skirting_segments'])
    repaired = receipt['details']['bathroom_parents_repaired']
    check('louças superiores vinculadas aos conjuntos corretos', len(repaired) == 14 and all(bpy.data.objects[n].parent == bpy.data.objects[p] for n, p in repaired.items()))
    check('louças superiores sobre o pavimento superior', all(min((base.world(bpy.data.objects[n]) @ Vector(v)).z for v in bpy.data.objects[n].bound_box) >= 2.69 for n in repaired))
    check('cadeira com malha perfurada', any(o.name.startswith('PHOTO6 Encosto de tela perfurado') and len(o.data.polygons) > 10000 for o in bpy.data.objects if o.type == 'MESH'))
    for job in receipt['jobs']:
        scene = bpy.data.scenes[job['scene']]; id_ = job['id']
        check('entorno apenas em vistas completas ' + id_, ('PHOTO6_Entorno' in scene.collection.children) == (not job['mode'].startswith(('plan', 'iso'))))
        removed = set(receipt['details']['presentation_omitted_context_vegetation'])
        if 'protected_visibility' in job:
            visible = {o.name for o in scene.objects if o.name in expected}
            check('arquitetura visível preservada ' + id_, visible == set(job['protected_visibility']) - removed)
        check('câmera ' + id_, (scene.camera.location - Vector(job['pos'])).length < 1e-5)
        check('câmera fora das paredes ' + id_, camera_in_wall(scene, expected) is None)
        check('resolução ' + id_, [scene.render.resolution_x, scene.render.resolution_y] == cfg['resolution'])
        check('amostragem ' + id_, scene.cycles.samples == cfg['samples'] and abs(scene.cycles.adaptive_threshold - cfg['adaptive_threshold']) < 1e-6)
        check('caminho ' + id_, scene.render.filepath == str(root / job['file']))
        check('condição de luz ' + id_, scene['photoreal_lighting'] == job['lighting'])
        check('HDRI em cada cena ' + id_, any(n.type == 'TEX_ENVIRONMENT' and n.image and max(n.image.size) >= 4096 for n in scene.world.node_tree.nodes))
        check('fontes auxiliares sem discos nos reflexos ' + id_, all(not o.visible_glossy and not o.visible_transmission and not o.visible_camera for o in scene.objects if o.type == 'LIGHT' and o.data.type == 'AREA'))
        check('escritório como alternativa ' + id_, ('PHOTO6_Acabamento_Escritorio' in scene.collection.children) == (job['mode'] == 'office'))
    if require_renders:
        rows = json.loads((folder / 'renders.json').read_text())
        check('conjunto exato de imagens', {r['id'] for r in rows} == {j['id'] for j in receipt['jobs']} and len(rows) == 31)
        for row in rows:
            check('imagem nativa íntegra ' + row['id'], row['blend_sha256'] == receipt['blend_sha256'] and not row['preview'] and data.sha(root / row['file']) == row['sha256'])
    result = {'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'blend_sha256': receipt['blend_sha256'],
              'checks': checks, 'all_passed': all(c['passed'] for c in checks), 'renders_required': require_renders,
              'scope': 'Preservação geométrica e integridade da revisão industrial; não certifica medidas reais, engenharia ou fotorrealismo perceptivo.'}
    (folder / ('validacao-completa.json' if require_renders else 'validacao-modelo.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('PHOTO6_AUDIT', len(checks), result['all_passed'], flush=True)
    failures = [c for c in checks if not c['passed']]
    if failures: print(json.dumps(failures, ensure_ascii=False)); raise SystemExit(1)


if __name__ == '__main__':
    main('--require-renders' in sys.argv)
