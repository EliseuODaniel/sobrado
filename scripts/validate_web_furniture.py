"""Confere o arranjo revisto na origem avaliada pelo Blender, em metros."""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_web_viewer import (
    SOURCE_SCENE, add_observed_furniture, front_bedroom_layout, suite_layout,
)


def main():
    scene = bpy.data.scenes[SOURCE_SCENE]
    add_observed_furniture(scene)
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    layout = suite_layout() + front_bedroom_layout()

    def bounds(*prefixes):
        matching = [
            obj for obj in scene.objects
            if obj.type in {"MESH", "CURVE"} and not obj.hide_render and obj.name.startswith(prefixes)
        ]
        assert matching, prefixes
        vertices = []
        for obj in matching:
            evaluated = obj.evaluated_get(graph)
            world = evaluated.matrix_world.copy()
            for names, transform in layout:
                if obj.name.startswith(names):
                    world = transform @ world
                    break
            mesh = evaluated.to_mesh()
            vertices.extend(world @ Vector(vertex.co) for vertex in mesh.vertices)
            evaluated.to_mesh_clear()
        assert vertices, prefixes
        return tuple(tuple(limit(v[i] for v in vertices) for i in range(3)) for limit in (min, max))

    wardrobe_min, wardrobe_max = bounds("ATUAL Roupeiro quarto branco", "FIEL2 Roupeiro branco")
    _, bed_max = bounds("FIEL2 Cama branca", "FIEL2 Quarto branco colcha", "ATUAL Estrado cama.001")
    assert wardrobe_min[0] > 4.25 and wardrobe_max[0] < 6.25
    assert wardrobe_max[1] < 2.001
    assert wardrobe_min[1] - bed_max[1] > .07
    _, tv_max = bounds("FIEL2 Quarto branco TV", "FIEL2 Quarto branco estante")
    assert tv_max[0] < 3.76

    cabinet_min, cabinet_max = bounds(
        "FIEL2 Armário estreito quarto azul", "FIEL2 Porta armário quarto azul", "FIEL2 Puxador armário quarto azul"
    )
    _, desk_max = bounds("ATUAL Escrivaninha quarto fundos", "FIEL2 Quarto azul tampo apoio")
    assert cabinet_min[1] > desk_max[1] and cabinet_max[1] < 7.05
    assert cabinet_max[0] < 4.0

    bench_min, bench_max = bounds("FIEL2 Base banco estofado jantar", "FIEL2 Assento banco estofado jantar")
    assert bench_min[0] >= .15 and bench_max[0] < .66
    assert bench_min[1] > 5.4 and bench_max[1] < 7.0

    panel_min, panel_max = bounds("FIEL2 Suite fundo cabeceira", "FIEL2 Suite friso vertical")
    assert panel_min[0] > 3.25 and panel_max[0] < 3.3 and panel_max[1] < 2.3
    print("Posições e folgas verificadas: quarto da frente, quarto dos fundos, banco do jantar e cabeceira da suíte.")


if __name__ == "__main__":
    main()
