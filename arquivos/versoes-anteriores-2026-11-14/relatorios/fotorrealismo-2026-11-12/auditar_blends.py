"""Inventário somente leitura. Executar pelo Blender; não salva arquivos .blend.

python3 scripts/run_blender.py --background --factory-startup --python \
  relatorios/fotorrealismo-2026-11-12/auditar_blends.py
"""
import bpy
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MODELS = [
    ("original", "projeto/residencia-07/casa-07.blend", None),
    ("atual", "projeto/residencia-07-atual/casa-07-atual.blend", "ATUAL_sala-fundos"),
    ("instalacoes", "projeto/residencia-07/casa-07-instalacoes.blend", None),
    ("industrial", "projeto/industrial-v05/casa-industrial-residencia07-atual.blend", "IND07_sala-fundos"),
    ("atico", "projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend", "ATC5_atico-interior-frente"),
]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def nodes(tree, visited=None):
    visited = set() if visited is None else visited
    if tree is None or tree.as_pointer() in visited:
        return []
    visited.add(tree.as_pointer())
    result = list(tree.nodes)
    for node in tree.nodes:
        if node.type == "GROUP":
            result.extend(nodes(node.node_tree, visited))
    return result


def render_objects(scene):
    active = set()

    def walk(layer, parent=True):
        enabled = parent and not layer.exclude and not layer.collection.hide_render
        if enabled:
            active.update(o for o in layer.collection.objects if not o.hide_render)
        for child in layer.children:
            walk(child, enabled)

    walk(scene.view_layers[0].layer_collection)
    return sorted(active, key=lambda obj: obj.name)


def inventory(objects):
    meshes = [o for o in objects if o.type == "MESH"]
    unique_meshes = set(o.data for o in meshes)
    materials = set()
    for obj in meshes:
        materials.update(slot.material for slot in obj.material_slots if slot.material)
    node_list = [n for m in materials for n in nodes(m.node_tree)]
    images = set(n.image for n in node_list if n.type == "TEX_IMAGE" and n.image)
    image_data = []
    for img in sorted(images, key=lambda value: value.name):
        path = Path(bpy.path.abspath(img.filepath, library=img.library)) if img.filepath else None
        packed = bool(img.packed_file or img.packed_files)
        image_data.append({"name": img.name, "size": list(img.size), "source": img.source,
                           "packed": packed, "external_exists": path.exists() if path else None,
                           "missing": img.source in {"FILE", "TILED"} and not packed and (path is None or not path.exists())})
    return {
        "objects": len(objects), "mesh_objects": len(meshes), "unique_mesh_data": len(unique_meshes),
        "unique_source_vertices": sum(len(m.vertices) for m in unique_meshes),
        "unique_source_polygons": sum(len(m.polygons) for m in unique_meshes),
        "mesh_objects_without_uv": sum(not bool(o.data.uv_layers) for o in meshes),
        "mesh_objects_with_bevel": sum(any(mod.type == "BEVEL" for mod in o.modifiers) for o in meshes),
        "material_count": len(materials),
        "materials_with_image_nodes": sum(any(n.type == "TEX_IMAGE" for n in nodes(m.node_tree)) for m in materials),
        "node_types": dict(sorted(collections.Counter(n.bl_idname for n in node_list).items())),
        "image_textures": image_data,
        "light_types": dict(collections.Counter(o.data.type for o in objects if o.type == "LIGHT")),
    }


result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "blender_version": bpy.app.version_string,
          "method": "Unique source meshes before evaluating modifiers. Selected-scene objects follow first view layer exclusions and hide_render; no frustum/occlusion culling. UV presence does not establish UV quality. Image nodes may be disconnected. No blend save operation.", "models": []}
for key, relative, preferred in MODELS:
    path = ROOT / relative
    before = sha(path)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.data.scenes.get(preferred) if preferred else bpy.context.scene
    if scene is None:
        raise RuntimeError(f"Scene missing: {preferred}")
    camera = scene.camera
    world_nodes = nodes(scene.world.node_tree) if scene.world else []
    cycles = scene.cycles
    entry = {
        "id": key, "file": relative, "size_bytes": path.stat().st_size, "sha256_before": before,
        "scenes": len(bpy.data.scenes), "selected_scene": scene.name,
        "global": inventory(list(bpy.data.objects)),
        "selected_scene_render_enabled": inventory(render_objects(scene)),
        "render": {"engine": scene.render.engine, "resolution": [scene.render.resolution_x, scene.render.resolution_y],
                   "percentage": scene.render.resolution_percentage, "samples": cycles.samples,
                   "adaptive": cycles.use_adaptive_sampling, "adaptive_threshold": cycles.adaptive_threshold,
                   "denoising": cycles.use_denoising, "view_transform": scene.view_settings.view_transform,
                   "exposure": scene.view_settings.exposure,
                   "camera": {"name": camera.name, "type": camera.data.type, "lens_mm": camera.data.lens,
                              "dof": camera.data.dof.use_dof} if camera else None,
                   "world_environment_texture_nodes": sum(n.type == "TEX_ENVIRONMENT" for n in world_nodes),
                   "world_sky_nodes": sum(n.type == "TEX_SKY" for n in world_nodes)},
        "sha256_after": sha(path),
    }
    entry["unchanged"] = before == entry["sha256_after"]
    result["models"].append(entry)
    print("AUDIT", key, entry["selected_scene"], entry["unchanged"], flush=True)
    (OUT / "auditoria-modelos.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
if not all(m["unchanged"] for m in result["models"]):
    raise RuntimeError("Native input checksum changed")
