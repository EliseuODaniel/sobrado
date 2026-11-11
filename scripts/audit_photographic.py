"""Auditoria independente dos recursos e da editabilidade do arquivo salvo."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import photographic_interiors as photo


def main():
    model, envelope = photo.validate()
    libraries = [library.filepath for library in bpy.data.libraries]
    assert not libraries, libraries
    assert bpy.context.scene.name == 'PHOTO_Sala'
    images = [image for image in bpy.data.images if image.source == 'FILE']
    assert images and all(image.packed_file for image in images)
    assert len(images) == model['packed_images']
    materials = [material for material in bpy.data.materials if material.use_nodes]
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    assert any(obj.name.startswith('SRC sofa_02 ') and len(obj.data.vertices) > 1000 for obj in meshes)
    assert any(obj.name.startswith('PHOTO Edredom com pregas') for obj in meshes)
    assert bpy.data.scenes.get('EDITAR_Ativos')
    scenes = {}
    for job in photo.CFG['jobs']:
        scene = bpy.data.scenes[job['scene']]
        assert scene.camera.type == 'CAMERA' and scene.camera.data.dof.use_dof
        assert [scene.render.resolution_x, scene.render.resolution_y] == photo.CFG['resolution']
        assert scene.cycles.samples == photo.CFG['samples']
        assert scene.cycles.use_adaptive_sampling and scene.cycles.use_denoising
        scenes[scene.name] = {'camera': scene.camera.name, 'samples_max': scene.cycles.samples,
            'adaptive_threshold': scene.cycles.adaptive_threshold,
            'resolution': [scene.render.resolution_x, scene.render.resolution_y]}
    with Path(bpy.data.filepath).open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    receipt = {'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'blend_sha256':digest, 'blender_version':bpy.app.version_string, 'external_libraries':libraries,
        'packed_file_images':len(images), 'mesh_objects':len(meshes),
        'vertices_in_mesh_datablocks':sum(len(mesh.vertices) for mesh in bpy.data.meshes),
        'node_materials':len(materials), 'editable_asset_instances':len(model['placements']),
        'geometry_compared':len(model['geometry_before']), 'envelope':envelope,
        'scenes':scenes, 'all_passed':True}
    (photo.REPORTS/'recursos-nativos.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print('PHOTO_RESOURCES_VALIDATED',len(meshes),'mesh objects;',len(images),'packed images')


if __name__ == '__main__':
    main()
