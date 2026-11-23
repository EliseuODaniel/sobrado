"""Confere o arranjo revisto na origem avaliada pelo Blender, em metros."""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_web_viewer import (
    SOURCE_SCENE, add_observed_furniture, bathrooms_layout, front_bedroom_layout,
    kitchen_layout, laundry_layout, living_room_tv_layout, match_layout_name, suite_layout,
)


def main():
    scene = bpy.data.scenes[SOURCE_SCENE]
    add_observed_furniture(scene)
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    layout = (
        suite_layout() + front_bedroom_layout() + kitchen_layout()
        + bathrooms_layout() + living_room_tv_layout() + laundry_layout()
    )

    def bounds(*prefixes):
        matching = [
            obj for obj in scene.objects
            if obj.type in {"MESH", "CURVE"} and not obj.hide_render and match_layout_name(obj.name, prefixes)
        ]
        assert matching, prefixes
        vertices = []
        for obj in matching:
            evaluated = obj.evaluated_get(graph)
            world = evaluated.matrix_world.copy()
            for names, transform in layout:
                if match_layout_name(obj.name, names):
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
    tv_min, tv_max = bounds("FIEL2 Quarto branco TV", "FIEL2 Quarto branco estante")
    assert tv_max[0] < 3.76 and tv_min[1] > 0.90 and tv_max[1] < 1.85
    aereo_min, aereo_max = bounds("ATUAL Armario suspenso")
    wbody_min, _ = bounds("ATUAL Roupeiro quarto branco")
    assert aereo_min[1] < -0.90 and abs(wbody_min[1] - aereo_max[1]) < 0.02, (aereo_min, aereo_max, wbody_min)

    cabinet_min, cabinet_max = bounds(
        "FIEL2 Armário estreito quarto azul", "FIEL2 Porta armário quarto azul", "FIEL2 Puxador armário quarto azul"
    )
    _, desk_max = bounds("ATUAL Escrivaninha quarto fundos", "FIEL2 Quarto azul tampo apoio")
    assert cabinet_min[1] > desk_max[1] and cabinet_max[1] < 7.05
    assert cabinet_max[0] < 4.0

    # Banco estofado completamente após a transição do pilar (Y >= 5.70) e antes das banquetas (Y <= 8.19).
    bench_min, bench_max = bounds("FIEL2 Base banco estofado jantar", "FIEL2 Assento banco estofado jantar")
    assert bench_min[0] >= .15 and bench_max[0] < .66
    assert bench_min[1] > 5.75 and bench_max[1] < 8.10

    # 8 cadeiras na mesa de jantar (6 laterais + 2 nas cabeceiras).
    side_seats = [o for o in scene.objects if o.name.startswith("FIEL2 Cadeira jantar assento")]
    assert len(side_seats) == 6, len(side_seats)

    # Suíte: painel cabeceira, ar próximo à cortina e painel TV piso-teto rente à porta do banheiro.
    panel_min, panel_max = bounds("FIEL2 Suite fundo cabeceira", "FIEL2 Suite friso vertical")
    assert panel_min[0] > 3.25 and panel_max[0] < 3.3 and panel_max[1] < 2.3
    ac_min, ac_max = bounds("FIEL2 Suite ar condicionado")
    assert ac_min[1] > -0.35 and ac_max[1] < 0.70
    tvp_min, tvp_max = bounds("ATUAL Painel TV suite")
    assert 1.56 < tvp_min[0] < 1.65 and tvp_min[2] < 2.75 and tvp_max[2] > 5.18

    # Cozinha: geladeira encostada na parede leste (X ~ 6.25) com portas voltadas para -X (X < corpo).
    fbody_min, fbody_max = bounds("=ATUAL Corpo geladeira.001")
    fdoor_min, fdoor_max = bounds("=ATUAL Porta geladeira.002", "=ATUAL Porta geladeira.003")
    assert fbody_max[0] < 6.26 and fdoor_max[0] <= fbody_min[0] + 0.02
    assert fbody_min[1] > 4.30 and fbody_max[1] < 5.04

    # Banheiro da suíte: chuveiro na parede direita do box (X > 1.1).
    shower_min, shower_max = bounds("=ATUAL R07 Chuveiro")
    assert shower_min[0] > 1.15 and shower_max[0] < 1.65

    # Ripado recuado para o fundo cobrindo a parede T-retorno-cozinha (X ~ 3.27, Y = 5.61..7.14).
    rip_min, rip_max = bounds("ATUAL Ripado cozinha")
    assert 3.23 < rip_min[0] < 3.31 and 3.28 < rip_max[0] < 3.33
    assert 5.58 < rip_min[1] < 5.66 and 7.10 < rip_max[1] < 7.16

    # Parede/painel/rack da TV da sala contidos em T-retorno-garagem (Y = 0.72..2.075), sem sair pela porta de entrada.
    tv_wall_min, tv_wall_max = bounds("FIEL2 Parede acabamento TV", "FIEL2 Painel TV branco arredondado", "FIEL2 Rack")
    assert tv_wall_min[1] > 0.73 and tv_wall_max[1] < 2.07

    # Lavanderia: parede dos fundos cega (Z até 2.80 m) e conjunto rotacionado para a parede da cozinha (Y = 7.20).
    backwall_min, backwall_max = bounds("=ATUAL Fundo lavanderia peitoril")
    assert backwall_min[2] <= 0.01 and backwall_max[2] >= 2.79
    lateral_min, lateral_max = bounds("ATUAL Bancada lavanderia lateral esquerda")
    back_min, back_max = bounds("ATUAL Bancada lavanderia fundo")
    front_min, front_max = bounds("FIEL2 Lavadora frontal corpo")
    top_min, top_max = bounds("FIEL2 Lavadora superior corpo")
    assert lateral_max[0] > 6.15 and lateral_max[1] - lateral_min[1] > 1.1
    assert abs(lateral_min[1] - back_max[1]) < .012
    assert 0 < front_min[0] - top_max[0] < .05
    assert abs(back_min[0] - front_min[0]) < .07 and top_min[0] > 3.45 and back_min[1] < 7.30
    print("Posições e folgas verificadas em todos os ambientes revisados.")


if __name__ == "__main__":
    main()
