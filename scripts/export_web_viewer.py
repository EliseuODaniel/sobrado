"""Exporta a cena atual para o visualizador, sem salvar alterações no Blender."""

import hashlib
import json
import os
import struct
import sys
from collections import defaultdict
from math import atan, pi, tan
from pathlib import Path
from tempfile import TemporaryDirectory

import bpy
import numpy as np
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "projeto/atual/casa-07-atual-fiel.blend"
OUTPUT = ROOT / "visualizador/modelo/casa-atual.glb"
SOURCE_SCENE = "FIEL2_volumetria"
GEOMETRY = {"MESH", "CURVE", "SURFACE", "FONT", "META"}
LAYERS = ("contexto", "terreo", "forro-terreo", "superior", "atico", "telhado", "caixa", "instalacoes")
ROOF_COLLECTIONS = {
    "R07_Cobertura", "R07_Teto_Superior", "ATUAL_Cobertura_Fundos",
    "ATC_Oitoes", "ATC3_Cobertura", "ATC4_Forro", "INFRA_Cobertura_Original",
}
CONTEXT_COLLECTIONS = {"R07_Contexto", "PHOTO6_Contexto_Apresentacao"}
NETWORK_PREFIX = "INFRA_Rede_"
NETWORK_VIEWS = {"0": "terreo", "1": "superior", "": "full"}
EXTERIOR_WALL_IDS = {
    "T-oeste", "T-frente-sala", "T-entrada-diagonal", "T-retorno-garagem",
    "T-garagem-lavabo", "T-geminada", "T-retorno-cozinha", "T-fundos-cozinha",
    "S-oeste", "S-geminada", "S-fachada-quarto", "S-sacada", "S-suite-sacada",
    "S-fundos-banheiros", "S-retorno-quarto-fundos", "S-fundos-quarto",
}
ANNEX_WALLS = {
    "ATUAL Muro oeste", "ATUAL Muro leste", "ATUAL Fundo lazer",
    "ATUAL Fundo lavanderia peitoril", "ATUAL Fundo lavanderia verga",
    "ATUAL Janela lateral esquerda", "ATUAL Janela lateral direita",
    "FIEL2 Fechamento superior posterior", "FIEL2 Fechamento lateral cobertura",
    "FIEL2 Fechamento lateral cobertura.001",
}
MAX_TEXTURE_EDGE = 1536
PRESETS = (
    ("fachada-frontal", "Fachada", "Exterior", 19),
    ("sala-foto", "Sala e jantar", "Térreo", 4.2),
    ("cozinha", "Cozinha", "Térreo", 2.5),
    ("bar", "Bar e churrasqueira", "Térreo", 2.5),
    ("lavanderia", "Lavanderia", "Térreo", 2.1),
    ("escada-acesso", "Escada", "Térreo", 1.5),
    ("lavabo", "Lavabo", "Térreo", 1.2),
    ("suite", "Suíte", "Superior", 2.3),
    ("suite-reversa", "Suíte · cabeceira e ar", "Superior", 2.3),
    ("quarto-frente", "Quarto da frente", "Superior", 2.2),
    ("quarto-branco-armario", "Armários do quarto da frente", "Superior", 2.4),
    ("quarto-fundos", "Quarto dos fundos", "Superior", 2.2),
    ("banheiro-suite", "Banheiro da suíte", "Superior", 1.5),
    ("banheiro-social", "Banheiro social", "Superior", 1.5),
)
VARIANTS = {
    "atual": (SOURCE, SOURCE_SCENE, "Atual fiel às fotos v02 · mobiliário revisado v03", "FIEL2_", PRESETS),
    "industrial": (
        ROOT / "projeto/industrial/casa-industrial-fotorrealista.blend",
        "PHOTO6_volumetria", "Industrial v06", "PHOTO6_",
        (
            ("fachada-frontal", "Fachada", "Exterior", 15),
            ("sala-integrada-dia", "Sala integrada", "Térreo", 3.4),
            ("sala-frente", "Sala de estar", "Térreo", 3.0),
            ("sala-tv", "Parede da TV", "Térreo", 2.4),
            ("mesa-jantar", "Mesa de jantar", "Térreo", 2.4),
            ("cozinha", "Cozinha", "Térreo", 2.5),
            ("cozinha-reversa", "Cozinha · reversa", "Térreo", 2.4),
            ("bar", "Bar e churrasqueira", "Térreo", 2.5),
            ("divisao-lazer-lavanderia", "Lazer e lavanderia", "Térreo", 2.6),
            ("lavanderia", "Lavanderia", "Térreo", 2.2),
            ("lavabo", "Lavabo", "Térreo", 1.2),
            ("escada-acesso", "Escada", "Térreo", 1.8),
            ("suite", "Suíte", "Superior", 2.0),
            ("quarto-frente", "Quarto da frente", "Superior", 2.0),
            ("quarto-fundos", "Quarto dos fundos", "Superior", 2.0),
            ("escritorio-alternativa", "Escritório (alternativa)", "Superior", 2.0),
        ),
    ),
    "estrutural": (
        ROOT / "projeto/infraestrutura/instalacoes-pavimentos-forro.blend",
        "INFRA_04_CONJUNTO_FORRO_CAIXA", "Estrutural · Instalações e forros", "INFRA_", (),
    ),
    "atico": (
        ROOT / "projeto/atico/atico-caixa-canto-escada.blend",
        "ATC5_atico-cobertura", "Ático · Caixa no canto junto à escada", "ATC5_",
        (
            ("atico-interior-frente", "Interior do ático · frente", "Ático", 2.4),
            ("atico-interior-fundos", "Interior do ático · fundos", "Ático", 2.4),
            ("atico-reservatorio", "Caixa-d’água", "Ático", 2.2),
            ("escada-u-chegada-existente", "Chegada da escada", "Superior", 2.4),
            ("escada-u-conjunto", "Escada em U · conjunto", "Ático", 5.0),
            ("atico-frente", "Fachada com ático", "Exterior", 10.0),
            ("atico-fundos", "Fundos e mansarda", "Exterior", 10.0),
        ),
    ),
}
OFFICE_COLLECTIONS = {"IND07_Escritorio_Alternativo", "PHOTO6_Acabamento_Escritorio"}
OFFICE_REPLACED_COLLECTIONS = {"ATUAL_AMB_quarto_azul"}
STATIC_PRESETS = {
    "estrutural": (
        {
            "id": "caixa-entrada-saidas", "label": "Caixa-d’água · entrada e saídas", "section": "Reservatório",
            "position": (3.15, 1.05, 7.15), "target": (5.35, 3.175, 5.85), "fov": 0.72, "aspect": 1.5,
        },
        {
            "id": "coluna-agua-quente", "label": "Coluna de água quente", "section": "Hidráulica",
            "position": (3.95, 2.35, 4.85), "target": (1.65, 5.25, 3.65), "fov": 0.72, "aspect": 1.5,
        },
        {
            "id": "hidraulica-banheiros", "label": "Hidráulica · banheiros superiores", "section": "Hidráulica",
            "position": (3.65, 2.85, 5.15), "target": (1.55, 5.05, 3.70), "fov": 0.72, "aspect": 1.5,
        },
        {
            "id": "hidraulica-cozinha", "label": "Hidráulica · cozinha e lavanderia", "section": "Hidráulica",
            "position": (2.25, 4.95, 2.45), "target": (4.95, 7.85, 1.15), "fov": 0.75, "aspect": 1.5,
        },
        {
            "id": "eletrica-terreo", "label": "Elétrica · térreo", "section": "Elétrica",
            "position": (0.75, 0.75, 2.45), "target": (3.35, 4.65, 1.30), "fov": 0.78, "aspect": 1.5,
        },
        {
            "id": "eletrica-superior", "label": "Elétrica · pavimento superior", "section": "Elétrica",
            "position": (0.85, 0.35, 5.15), "target": (3.35, 4.10, 3.85), "fov": 0.78, "aspect": 1.5,
        },
    ),
}


def gltf_vector(vector):
    x, y, z = vector
    return [x, z, -y]


def camera_presets(prefix, definitions, variant=None):
    presets = []
    for name, label, section, distance in definitions:
        bpy.context.window.scene = bpy.data.scenes[f"{prefix}{name}"]
        bpy.context.view_layer.update()
        scene = bpy.context.scene
        camera = scene.camera.evaluated_get(bpy.context.evaluated_depsgraph_get())
        position = camera.matrix_world.translation
        forward = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        target = position + forward * distance
        if prefix == "FIEL2_" and name == "lavanderia":
            position = Vector((4.85, 9.68, 1.52))
            target = Vector((4.85, 7.30, 1.24))
        if prefix == "FIEL2_" and name == "suite":
            position = Vector((2.86, -0.20, 4.20))
            target = Vector((1.65, 1.70, 3.88))
        if prefix == "FIEL2_" and name == "suite-reversa":
            position = Vector((0.88, 2.75, 4.18))
            target = Vector((2.78, 0.55, 3.92))
        if prefix == "FIEL2_" and name == "quarto-branco-armario":
            target = Vector((4.82, 1.72, 3.92))
        if prefix == "FIEL2_" and name == "quarto-frente":
            # Posição ajustada para circulação livre após a revisão do roupeiro e estante.
            position = Vector((3.76, 1.48, 4.18))
            target = Vector((5.55, -.35, 3.88))
        if prefix == "PHOTO6_" and name == "suite":
            position = Vector((2.86, -0.20, 4.20))
            target = Vector((1.65, 1.70, 3.88))
        render = scene.render
        aspect = render.resolution_x * render.pixel_aspect_x / (
            render.resolution_y * render.pixel_aspect_y
        )
        # As câmeras da entrega usam o sensor horizontal em imagens horizontais.
        vertical_fov = 2 * atan(tan(camera.data.angle_x / 2) / aspect)
        entry = {
            "id": name, "label": label, "section": section,
            "position": gltf_vector(position), "target": gltf_vector(target),
            "fov": vertical_fov, "aspect": aspect,
        }
        if prefix == "PHOTO6_" and name == "escritorio-alternativa":
            entry["roomVariant"] = "escritorio"
        elif prefix == "PHOTO6_" and name == "quarto-fundos":
            entry["roomVariant"] = "quarto"
        presets.append(entry)
    for item in STATIC_PRESETS.get(variant, ()):
        presets.append({
            "id": item["id"], "label": item["label"], "section": item["section"],
            "position": gltf_vector(item["position"]), "target": gltf_vector(item["target"]),
            "fov": item["fov"], "aspect": item["aspect"],
        })
    return presets


def layer_for(obj, collections, min_z):
    if collections & ROOF_COLLECTIONS:
        return "telhado"
    if "INFRA_Caixa_Original" in collections:
        return "caixa"
    if collections & {"INFRA_Forro_Terreo", "INFRA_Arquitetura_Terreo"}:
        return "terreo"
    if collections & {"INFRA_Forro_Superior", "INFRA_Arquitetura_Superior"}:
        return "superior"
    if any(collection.startswith("ATC") for collection in collections):
        return "atico"
    if "FIEL2_Detalhes_Cobertura" in collections:
        return "terreo" if obj.name.startswith("FIEL2 Fechamento") else "telhado"
    if collections & {"FIEL2_Contexto", "PHOTO6_Entorno"} or obj.name.startswith("FIEL2 Pavimento externo observado"):
        return "contexto"
    if "FIEL2_Luminarias_Terreo" in collections:
        return "forro-terreo"
    if "R07_Escada" in collections or obj.name.startswith(("ATUAL R07 Degrau", "FIEL2 Espelho granito degrau")):
        return "terreo"
    if "FIEL2_Mobiliario_Superior" in collections or obj.get("level") == 1:
        return "superior"
    if "FIEL2_Mobiliario_Terreo" in collections:
        return "terreo"
    return "superior" if min_z >= 2.55 - 1e-4 else "terreo"


def keep_separate(mesh):
    # A ordenação do vidro no navegador depende da posição de cada peça.
    for material in mesh.materials:
        if not material:
            continue
        if any(word in material.name.lower() for word in ("vidro", "glass", "espelho")):
            return True
        if not material.node_tree:
            continue
        for node in material.node_tree.nodes:
            if node.type == "BSDF_TRANSPARENT":
                return True
            if node.type == "BSDF_PRINCIPLED":
                alpha = node.inputs["Alpha"]
                transmission = node.inputs["Transmission Weight"]
                if alpha.is_linked or alpha.default_value < 1 or transmission.is_linked or transmission.default_value > 0:
                    return True
    return False


def exterior_wall_key(obj, collections):
    wall_id = obj.get("wall_id")
    if wall_id in EXTERIOR_WALL_IDS:
        return wall_id
    name = obj.name.removeprefix("INFRA ")
    if name in ANNEX_WALLS or name.startswith("R07 Parede corta-fogo"):
        return obj.name
    if collections & {"ATC_Oitoes", "ATC3_Fachadas_Mansardas"}:
        return obj.name
    return None


def source_geometry(scene):
    memberships = defaultdict(set)

    def visit(collection, branch):
        if collection.hide_render:
            return
        for obj in collection.objects:
            memberships[obj].add(branch)
        for child in collection.children:
            visit(child, branch)

    for branch in scene.collection.children:
        if branch.name not in CONTEXT_COLLECTIONS:
            visit(branch, branch.name)
    for obj in scene.collection.objects:
        memberships[obj].add(scene.collection.name)
    return memberships


def evaluated_geometry(scene, depsgraph, include_instances):
    memberships = source_geometry(scene)
    for obj, collections in sorted(memberships.items(), key=lambda item: item[0].name):
        if obj.type in GEOMETRY and not obj.hide_render:
            evaluated = obj.evaluated_get(depsgraph)
            networks = sorted(name for name in collections if name.startswith(NETWORK_PREFIX))
            for network in networks or [None]:
                yield obj, evaluated, evaluated.matrix_world.copy(), collections, network
    # Os móveis industriais incluem instâncias de coleções editáveis.
    if not include_instances:
        return
    for instance in depsgraph.object_instances:
        if not instance.is_instance or not instance.parent:
            continue
        owner = instance.parent.original
        evaluated = instance.object
        if owner in memberships and not owner.hide_render and evaluated.type in GEOMETRY and not evaluated.hide_render:
            if any(name.startswith(NETWORK_PREFIX) for name in memberships[owner]):
                continue
            yield evaluated.original, evaluated, instance.matrix_world.copy(), memberships[owner], None


def rotate_between(origin, destination, angle, scale=(1, 1, 1)):
    return (
        Matrix.Translation(destination)
        @ Matrix.Rotation(angle, 4, "Z")
        @ Matrix.Diagonal((*scale, 1))
        @ Matrix.Translation(-Vector(origin))
    )


def suite_layout():
    # Coordenadas da suíte de FIEL2_volumetria em metros. Rotacionar cada
    # conjunto inteiro mantém ferragens, cabeceira e tela alinhadas.
    # O roupeiro ocupa o vão entre a sacada e o banheiro, com junta de 1 cm em cada ponta.
    wardrobe_start, wardrobe_end = -.39, 3.19
    wardrobe_center = (wardrobe_start + wardrobe_end) / 2
    wardrobe_scale = (wardrobe_end - wardrobe_start) / 2.88
    return (
        (("ATUAL Roupeiro suite", "FIEL2 Roupeiro trilho"),
         rotate_between((1.615, 2.89, 0), (0.45, wardrobe_center, 0), pi / 2, (wardrobe_scale, 1, 1))),
        (("ATUAL Cama suite", "ATUAL Cabeceira suite", "ATUAL Apoio lateral cabeceira",
          "ATUAL Mesa cabeceira", "ATUAL Travesseiro suite",
          "FIEL2 Suite cabeceira modulo", "FIEL2 Suite colcha drapeada", "FIEL2 Suite travesseiro"),
         rotate_between((1.30, .95, 0), (2.17, .95, 0), pi)),
        # quartosuite2/3: painel de madeira vai do piso ao teto rente à porta do banheiro.
        (("ATUAL Painel TV suite",),
         rotate_between((3.265, .65, 4.10), (2.04, 3.15, 3.97), pi / 2, (1, 1, 2.52))),
        (("ATUAL TV suite", "ATUAL Movel lareira suite", "ATUAL Nicho lareira"),
         rotate_between((3.265, .65, 0), (2.04, 3.15, 0), pi / 2)),
        # quartosuite1/3: split instalado próximo à cortina da sacada (lado da janela).
        (("FIEL2 Suite ar condicionado",),
         rotate_between((.29, 2.35, 0), (3.17, .16, 0), pi)),
        (("FIEL2 Suite aletas split",),
         rotate_between((.29, 2.35, 0), (2.90, .16, 0), pi)),
        # O painel acompanha a cabeceira e termina antes da porta da suíte.
        (("FIEL2 Suite fundo cabeceira", "FIEL2 Suite friso vertical"),
         rotate_between((.165, 1.36, 0), (3.28, .95, 0), pi, (1, .74, 1))),
    )


def front_bedroom_layout():
    # quartobranco1/2: roupeiro ao lado da entrada, aéreo contíguo ao roupeiro e TV/estante junto à porta.
    wardrobe = rotate_between((3.79, .55, 0), (5.26, 1.68, 0), -pi / 2, (1, 1.85 / 1.60, 1))
    return (
        (("ATUAL Roupeiro quarto branco",), wardrobe),
        (("FIEL2 Roupeiro branco porta", "FIEL2 Roupeiro branco puxador"),
         wardrobe @ Matrix.Translation((0, .26, 0))),
        (("FIEL2 Quarto branco TV", "FIEL2 Quarto branco estante"),
         rotate_between((4.45, 1.99, 0), (3.48, 1.25, 0), pi / 2)),
        (("ATUAL Armario suspenso", "FIEL2 Aereo branco"),
         rotate_between((5.94, .25, 0), (5.94, .205, 0), 0, (1, 2.33 / 1.90, 1))),
        (("ATUAL Estrado cama.001", "ATUAL Colchão cama.001", "ATUAL Pé cama.004",
          "ATUAL Pé cama.005", "ATUAL Pé cama.006", "ATUAL Pé cama.007",
          "FIEL2 Cama branca", "FIEL2 Quarto branco colcha", "FIEL2 Quarto branco travesseiro",
          "FIEL2 Quarto branco papel coracoes"),
         Matrix.Translation((0, -.26, 0))),
    )


def kitchen_layout():
    # cozinha1/2 e sala1: geladeira encostada na parede leste com portas voltadas para o interior (-X).
    # sala1/2/6/7: ripado recuado para o fundo cobrindo a parede entre a cozinha e a sala (T-retorno-cozinha: Y = 5.625..7.125).
    fridge = rotate_between((5.90, 4.73, 0), (5.93, 4.66, 0), pi / 2)
    ripado = rotate_between((3.29, 4.92, 0), (3.275, 6.375, 0), 0, (1, 1.52 / 1.068, 1))
    return (
        (("=ATUAL Corpo geladeira.001", "=ATUAL Porta geladeira.002", "=ATUAL Porta geladeira.003",
          "=ATUAL Puxador geladeira.002", "=ATUAL Puxador geladeira.003"), fridge),
        (("ATUAL Ripado cozinha",), ripado),
    )


def bathrooms_layout():
    # suite1: chuveiro do banheiro da suíte na parede direita do box (X = 1.65), oposta à bancada.
    return (
        (("=ATUAL R07 Chuveiro",), rotate_between((.90, 6.10, 0), (.90, 6.10, 0), pi)),
    )


def living_room_tv_layout():
    # sala2/3/4: painel da TV, parede de acabamento e rack ficam contidos no trecho
    # da parede T-retorno-garagem (Y = 0.72..2.075), sem avançar sobre a porta de entrada diagonal (P3-entrada).
    panel = rotate_between((3.22, 1.50, 0), (3.22, 1.40, 0), 0, (1, 1.31 / 2.70, 1))
    rack = rotate_between((3.245, 1.51, 0), (3.245, 1.40, 0), 0, (.82, 1.26 / 2.23, 1))
    tv = rotate_between((3.13, 1.51, 0), (3.13, 1.40, 0), 0, (1, .88, 1))
    return (
        (("FIEL2 Parede acabamento TV", "FIEL2 Painel TV branco arredondado",
          "FIEL2 Friso LED TV", "FIEL2 Spot aro", "FIEL2 Spot difusor"), panel),
        (("FIEL2 Rack",), rack),
        (("FIEL2 TV",), tv),
    )


def match_layout_name(name, patterns):
    for pattern in patterns:
        if pattern.startswith("="):
            if name == pattern[1:]:
                return True
        elif name.startswith(pattern):
            return True
    return False


LAUNDRY_REMOVED_OBJECTS = (
    "ATUAL Caixilho janela lavanderia",
    "ATUAL Vidro janela lavanderia",
    "ATUAL Janela lateral esquerda",
    "ATUAL Janela lateral direita",
    "ATUAL Fundo lavanderia verga",
)

INDUSTRIAL_REMOVED_OBJECTS = (
    "ATUAL Colchão cama.002",
    "ATUAL Colchão cama.003",
    "ATUAL Degrau escada beliche",
    "ATUAL Estrado cama.002",
    "ATUAL Estrado cama.003",
    "ATUAL Pilar beliche",
    "ATUAL Pé cama.008",
    "ATUAL Pé cama.009",
    "ATUAL Pé cama.010",
    "ATUAL Pé cama.011",
    "ATUAL Travesseiro.002",
    "ATUAL Travesseiro.003",
)


def laundry_layout():
    # lavanderia1 + cozinha2: a parede dos fundos (Y = 10.25) é cega (sem janela para fora).
    # A janela acima do tanque é J4-cozinha (Y = 7.20), com retorno em L na parede leste (X = 6.25)
    # e porta de correr do bar deslocada para Y = 8.45..9.25 ao lado da geladeira do bar.
    flip = rotate_between((4.85, 8.725, 0), (4.85, 8.725, 0), pi)
    back = flip @ Matrix.Translation((.31, -.105, 0))
    return (
        # Fecha o vão da janela falsa nos fundos elevando o peitoril até Z = 2.80 m.
        (("=ATUAL Fundo lavanderia peitoril",),
         rotate_between((4.80, 10.325, 0), (4.80, 10.325, 0), 0, (1, 1, 2.80 / 1.05))),
        # Desloca a porta de correr bar/lavanderia para Y = 8.45..9.25, liberando a parede da lavadora.
        (("=ATUAL Divisao frente",),
         rotate_between((3.375, 7.20, 0), (3.375, 7.20, 0), 0, (1, 1.25 / .45, 1))),
        (("=ATUAL Divisao fundo",),
         rotate_between((3.375, 10.40, 0), (3.375, 10.40, 0), 0, (1, 1.15 / 1.95, 1))),
        (("=ATUAL Divisao verga", "ATUAL Caixilho divisao", "=ATUAL Vidro divisao", "FIEL2 Porta divisao"),
         Matrix.Translation((0, .80, 0))),
        # Conjunto da lavanderia rotacionado 180° para a parede da cozinha (Y = 7.20).
        (("ATUAL Bancada lavanderia fundo", "ATUAL Gabinete lavanderia",
          "ATUAL Puxador gabinete lavanderia", "FIEL2 Tanque profundo"), back),
        (("FIEL2 Tanque torneira", "FIEL2 Tanque bica"), flip @ Matrix.Translation((.31, 0, 0))),
        (("FIEL2 Lavadora superior",), flip @ Matrix.Translation((0, -.11, 0))),
        (("FIEL2 Lavadora",), back),
        (("ATUAL Bancada lavanderia lateral esquerda",),
         flip @ rotate_between((3.77, 10.005, 0), (3.77, 9.08, 0), 0, (1, 1.16 / .63, 1))),
        (("ATUAL Armário aéreo lavanderia.001",), flip @ Matrix.Translation((.08, -.11, 0))),
        (("ATUAL Armário aéreo lavanderia",),
         flip @ rotate_between((3.75, 10.195, 0), (3.65, 9.33, 0), pi / 2, (2.65, 1, 1))),
        (("FIEL2 Canto bancada lavanderia", "FIEL2 Gabinete retorno lavanderia"), flip),
        (("FIEL2 Vaso lavanderia", "FIEL2 Planta lavanderia"),
         flip @ rotate_between((4.60, 10.19, 0), (4.92, 10.19, 0), 0, (.68, 1, 1))),
    )


def add_observed_furniture(source):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import blender_primitives as primitives

    bpy.context.window.scene = source
    collection = bpy.data.collections.new("FIEL2_Moveis_Revistos_Web")
    source.collection.children.link(collection)
    primitives.C[collection.name] = collection

    def box(name, position, size, material, bevel):
        return primitives.box(name, position, size, bpy.data.materials[f"FIEL2 {material}"], collection.name, bevel)

    # O retorno termina junto ao tampo posterior (rotacionado 180° em laundry_layout).
    granite = bpy.data.objects["ATUAL Bancada lavanderia lateral esquerda"].active_material
    primitives.box("FIEL2 Canto bancada lavanderia", (3.645, 9.955, .90),
                   (.34, .59, .04), granite, collection.name, .003)
    for y in (8.79, 9.37):
        box("FIEL2 Gabinete retorno lavanderia", (3.75, y, .44), (.54, .575, .88), "Branco laqueado", .006)

    # sala1/2/6/7: fechamento e retornos do ripado cobrindo a parede T-retorno-cozinha (X=3.30..3.45, Y=5.625..7.125).
    slat_source = bpy.data.objects.get("ATUAL Ripado cozinha")
    slat_mat = slat_source.active_material if slat_source else bpy.data.materials["FIEL2 Branco laqueado"]
    for i in range(3):
        x = 3.29 + i * 0.068
        primitives.box(f"FIEL2 Ripado retorno frente {i}", (x, 5.605, 1.28), (.028, .054, 2.55), slat_mat, collection.name, .002)
        primitives.box(f"FIEL2 Ripado retorno fundo {i}", (x, 7.145, 1.28), (.028, .054, 2.55), slat_mat, collection.name, .002)
    primitives.box("FIEL2 Ripado nucleo", (3.292, 6.375, 1.28), (.022, 1.53, 2.55), slat_mat, collection.name, .002)

    # quartoazul2: módulo estreito entre a bancada e a janela, à frente do beliche.
    box("FIEL2 Armário estreito quarto azul", (3.705, 6.792, 3.95), (.47, .49, 2.46), "Branco laqueado", .01)
    for y in (6.668, 6.916):
        box("FIEL2 Porta armário quarto azul", (3.949, y, 3.95), (.018, .243, 2.44), "Branco laqueado", .004)
    for y in (6.762, 6.822):
        box("FIEL2 Puxador armário quarto azul", (3.969, y, 3.87), (.023, .012, .24), "Inox", .004)

    # sala1/5: banco estofado no trecho posterior ao pilar (Y > 5.70), antes das banquetas.
    box("FIEL2 Base banco estofado jantar", (.41, 6.92, .19), (.47, 1.18, .30), "Cabeceira bege", .035)
    for y in (6.528, 6.92, 7.312):
        box("FIEL2 Assento banco estofado jantar", (.41, y, .377), (.47, .388, .11), "Cabeceira bege", .033)

    # quartosuite2/3: prateleira branca sobre a TV da suíte.
    box("FIEL2 Prateleira TV suite", (2.04, 3.05, 4.54), (.76, .15, .028), "Branco laqueado", .004)

    # quartobranco1: duas prateleiras brancas junto à parede divisória perto da janela.
    for z in (4.00, 4.32):
        box("FIEL2 Prateleira quarto branco", (3.57, .28, z), (.22, .56, .025), "Branco laqueado", .003)

    # banheiro2: gabinete em madeira clara, distinto da madeira escura da suíte.
    social_vanity = bpy.data.objects.get("ATUAL R07 Gabinete banho.002")
    if social_vanity:
        light_wood = bpy.data.materials.new("FIEL2 Madeira clara banho social")
        light_wood.use_nodes = True
        bsdf = light_wood.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.76, 0.70, 0.61, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.42
        social_vanity.data = social_vanity.data.copy()
        social_vanity.data.materials.clear()
        social_vanity.data.materials.append(light_wood)

    # sala1/5/6/7: mesa de jantar com 8 cadeiras (3 por lateral + 2 nas cabeceiras).
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    side_chair_objs = [
        obj for obj in list(source.objects)
        if obj.type in {"MESH", "CURVE"} and not obj.hide_render and obj.name.startswith("FIEL2 Cadeira jantar ")
    ]
    chair_collection = bpy.data.collections.get("FIEL2_Mobiliario_Terreo") or collection
    for obj in side_chair_objs:
        ev = obj.evaluated_get(graph)
        mesh = ev.to_mesh()
        if not mesh.vertices:
            ev.to_mesh_clear()
            continue
        ys = [(ev.matrix_world @ v.co).y for v in mesh.vertices]
        center_y = (min(ys) + max(ys)) / 2
        ev.to_mesh_clear()
        if center_y < 4.50:
            dup = obj.copy()
            dup.data = obj.data.copy()
            dup.name = f"{obj.name} meio"
            dup.matrix_world = Matrix.Translation((0, .46, 0)) @ obj.matrix_world
            chair_collection.objects.link(dup)
            obj.matrix_world = Matrix.Translation((0, -.17, 0)) @ obj.matrix_world
        else:
            obj.matrix_world = Matrix.Translation((0, .17, 0)) @ obj.matrix_world


def repair_official_openings():
    # Restaura as posições oficiais das esquadrias (porta do lavabo P1-lavabo, porta de entrada P3-entrada,
    # janela da sala J3-sala e demais vãos) a partir da planta original R07, evitando que fiquem na origem (0,0,0) sobre a parede da sala.
    official_path = ROOT / "relatorios/atual/esquadrias-originais.json"
    if official_path.is_file():
        official = json.loads(official_path.read_text(encoding="utf-8"))
        for row in official:
            obj = bpy.data.objects.get("ATUAL BASE " + row["name"])
            if obj is not None:
                obj.parent = None
                obj.matrix_world = Matrix(row["matrix_world"])
    # Posiciona as folhas de porta fechadas dentro dos respectivos batentes (como na Casa atual).
    for hinge in list(bpy.data.objects):
        if not hinge.name.startswith("ATUAL BASE R07 Folha "):
            continue
        door_id = hinge.name.removeprefix("ATUAL BASE R07 Folha ")
        hw = hinge.matrix_world.copy()
        delta = (hw @ Matrix.Rotation(-170 * pi / 180, 4, "Z")) @ hw.inverted_safe()
        for part in ("Porta ", "Maçaneta "):
            obj = bpy.data.objects.get("ATUAL BASE R07 " + part + door_id)
            if obj is not None:
                obj.parent = None
                obj.matrix_world = delta @ obj.matrix_world
    # Restaura o vínculo pai-filho das louças/gabinetes superiores quando presentes.
    for suffix in (".001", ".002"):
        for root_name, children in (
            ("Vaso sanitario", ("Louca base", "Louca assento", "Louca abertura")),
            ("Lavatorio", ("Gabinete banho", "Bancada banho", "Cuba banho", "Espelho banho")),
        ):
            parent = bpy.data.objects.get("ATUAL R07 " + root_name + suffix)
            if parent is None:
                continue
            for child in children:
                obj = bpy.data.objects.get("ATUAL R07 " + child + suffix)
                if obj is not None:
                    local = obj.matrix_basis.copy()
                    obj.parent = parent
                    obj.matrix_parent_inverse = Matrix.Identity(4)
                    obj.matrix_basis = local


def prepare_industrial(source):
    repair_official_openings()
    for name in OFFICE_COLLECTIONS:
        col = bpy.data.collections.get(name)
        if col and col.name not in source.collection.children:
            source.collection.children.link(col)


def add_attic_tank_enclosure(source):
    """Cria parede em L de fechamento do compartimento da caixa-d'água até o forro inclinado."""
    import bmesh

    repair_official_openings()
    bpy.context.window.scene = source
    collection = bpy.data.collections.new("ATC5_Fechamento_Caixa_Web")
    source.collection.children.link(collection)

    wall_mat = bpy.data.materials.new("ATC5 Drywall caixa")
    wall_mat.use_nodes = True
    bsdf = wall_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.87, 0.86, 0.83, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.72

    door_mat = bpy.data.materials.new("ATC5 Porta manutencao caixa")
    door_mat.use_nodes = True
    dbsdf = door_mat.node_tree.nodes.get("Principled BSDF")
    if dbsdf:
        dbsdf.inputs["Base Color"].default_value = (0.76, 0.73, 0.68, 1.0)
        dbsdf.inputs["Roughness"].default_value = 0.55

    handle_mat = bpy.data.materials.new("ATC5 Puxador porta caixa")
    handle_mat.use_nodes = True
    hbsdf = handle_mat.node_tree.nodes.get("Principled BSDF")
    if hbsdf:
        hbsdf.inputs["Base Color"].default_value = (0.28, 0.30, 0.32, 1.0)
        hbsdf.inputs["Metallic"].default_value = 0.7
        hbsdf.inputs["Roughness"].default_value = 0.35

    def roof_z(y):
        # Rampa exata de ATC3 Forro acabado 08 com folga de 3 cm abaixo da face interna.
        return max(5.43, 9.14 - 0.9191 * (y - 3.0))

    def add_sloped_prism(name, x0, x1, y0, y1, z_bottom, z_top_y0, z_top_y1, mat):
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        v = [
            bm.verts.new((x0, y0, z_bottom)),
            bm.verts.new((x1, y0, z_bottom)),
            bm.verts.new((x1, y1, z_bottom)),
            bm.verts.new((x0, y1, z_bottom)),
            bm.verts.new((x0, y0, z_top_y0)),
            bm.verts.new((x1, y0, z_top_y0)),
            bm.verts.new((x1, y1, z_top_y1)),
            bm.verts.new((x0, y1, z_top_y1)),
        ]
        for face in (
            (0, 3, 2, 1), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (0, 4, 7, 3), (1, 2, 6, 5),
        ):
            bm.faces.new([v[i] for i in face])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat)
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        return obj

    # Parede sul (entre a escada Y=4.15 e a caixa Y=4.34), indo de X=4.15 até o oitão leste X=6.235.
    add_sloped_prism(
        "ATC5 Parede sul caixa dagua",
        4.15, 6.235, 4.18, 4.28, 5.40, roof_z(4.18), roof_z(4.28), wall_mat,
    )
    # Parede oeste (fora da janela X<=4.00 e à esquerda da caixa X>=4.34), acompanhando o caimento até os fundos.
    add_sloped_prism(
        "ATC5 Parede oeste caixa dagua",
        4.15, 4.25, 4.28, 7.05, 5.40, roof_z(4.28), roof_z(7.05), wall_mat,
    )
    # Porta de acesso/manutenção na face oeste do compartimento (0,70 x 1,72 m) + puxador.
    add_sloped_prism(
        "ATC5 Porta manutencao caixa",
        4.132, 4.152, 4.52, 5.22, 5.42, 7.14, 7.14, door_mat,
    )
    add_sloped_prism(
        "ATC5 Puxador porta caixa",
        4.105, 4.132, 5.10, 5.13, 6.22, 6.40, 6.40, handle_mat,
    )


def convert_geometry(source, export_scene, groups, layout=(), include_instances=False, skip_prefixes=()):
    bpy.context.window.scene = source
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    batches = defaultdict(list)
    counts = dict.fromkeys(LAYERS, 0)
    wall_groups = {}
    network_groups = {}
    variant_groups = {}
    network_summary = {"total": 0, "proposed": 0, "documental": 0, "systems": defaultdict(int)}
    for obj, evaluated, world, collections, network in evaluated_geometry(source, depsgraph, include_instances):
        if obj.name == "R07 Plano cenario" or (skip_prefixes and obj.name.startswith(skip_prefixes)):
            continue
        for patterns, transform in layout:
            if match_layout_name(obj.name, patterns):
                world = transform @ world
                break
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
        if not mesh.polygons:
            bpy.data.meshes.remove(mesh)
            continue
        min_z = min((world @ Vector(corner)).z for corner in evaluated.bound_box)
        room_variant = (
            "escritorio" if collections & OFFICE_COLLECTIONS
            else ("quarto" if collections & OFFICE_REPLACED_COLLECTIONS else None)
        )
        layer = (
            "instalacoes" if network
            else ("superior" if room_variant else layer_for(obj, collections, min_z))
        )
        wall_key = exterior_wall_key(obj, collections)
        parent = groups[layer]
        has_net_meta = False
        if network:
            if network not in network_groups:
                group = bpy.data.objects.new(network, None)
                export_scene.collection.objects.link(group)
                group.parent = parent
                key, _, level = network.removeprefix(NETWORK_PREFIX).partition("_Piso_")
                group["web_network"] = key
                group["web_network_view"] = NETWORK_VIEWS[level]
                network_groups[network] = group
            parent = network_groups[network]
        elif room_variant:
            vkey = (layer, room_variant)
            if vkey not in variant_groups:
                vgroup = bpy.data.objects.new(f"Variante · {room_variant}", None)
                export_scene.collection.objects.link(vgroup)
                vgroup.parent = parent
                vgroup["web_room_variant"] = room_variant
                variant_groups[vkey] = vgroup
            parent = variant_groups[vkey]
        if wall_key:
            if layer not in wall_groups:
                parent = bpy.data.objects.new(f"Paredes externas · {layer}", None)
                export_scene.collection.objects.link(parent)
                parent.parent = groups[layer]
                parent["web_exterior_walls"] = True
                wall_groups[layer] = parent
            parent = wall_groups[layer]
        clone = bpy.data.objects.new(obj.name, mesh)
        export_scene.collection.objects.link(clone)
        clone.parent = parent
        clone.matrix_world = world
        if network:
            if "system" in obj or "network_node" in obj or "flow_direction" in obj:
                has_net_meta = True
                if "system" in obj:
                    clone["web_net_system"] = str(obj["system"])
                if "node_a" in obj:
                    clone["web_net_node_a"] = str(obj["node_a"])
                if "node_b" in obj:
                    clone["web_net_node_b"] = str(obj["node_b"])
                if "nominal_diameter_m" in obj:
                    clone["web_net_diameter_mm"] = round(float(obj["nominal_diameter_m"]) * 1000, 1)
                if "proposed_segment" in obj:
                    proposed = bool(obj["proposed_segment"])
                    clone["web_net_proposed"] = proposed
                    if "_Piso_" not in network:
                        network_summary["total"] += 1
                        network_summary["proposed" if proposed else "documental"] += 1
                        if "system" in obj:
                            network_summary["systems"][str(obj["system"])] += 1
                if "source" in obj:
                    clone["web_net_source"] = str(obj["source"])
                if "kind" in obj:
                    clone["web_net_kind"] = str(obj["kind"])
                if "network_node" in obj:
                    clone["web_net_node"] = str(obj["network_node"])
                if "flow_direction" in obj:
                    clone["web_net_flow"] = bool(obj["flow_direction"])
        counts[layer] += 1
        if not keep_separate(mesh) and not has_net_meta:
            # As malhas unidas precisam usar o mesmo conjunto de mapas UV.
            uv_layout = tuple(uv.name for uv in mesh.uv_layers), mesh.uv_layers.active_index
            # Mantém cada parede e cada variante de ambiente separadas.
            batches[layer, network or wall_key, room_variant, uv_layout].append(clone)

    bpy.context.window.scene = export_scene
    bpy.context.view_layer.update()
    for (layer, wall_key, room_variant, _), objects in batches.items():
        if len(objects) < 2:
            continue
        with bpy.context.temp_override(active_object=objects[0], selected_editable_objects=objects):
            bpy.ops.object.join()
        tag = wall_key or room_variant
        objects[0].name = f"Paredes externas · {wall_key}" if wall_key else (
            f"Variante · {room_variant}" if room_variant else f"Malhas · {layer}"
        )
    network_summary["systems"] = dict(network_summary["systems"])
    return counts, network_summary


def prepare_infrastructure(scene):
    for name in ("INFRA_06_TERREO", "INFRA_07_SUPERIOR"):
        for group in bpy.data.scenes[name].collection.children:
            if group.name.startswith(NETWORK_PREFIX):
                scene.collection.children.link(group)

    # Os materiais Diffuse/Mix do Blender passam a usar cor e alfa lidos pelo glTF.
    for material in bpy.data.materials:
        if "presentation_opacity" not in material:
            continue
        color = tuple(material.diffuse_color)
        opacity = material["presentation_opacity"]
        tree = material.node_tree
        tree.nodes.clear()
        shader = tree.nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = (*color[:3], 1)
        shader.inputs["Roughness"].default_value = 0.8
        shader.inputs["Alpha"].default_value = opacity
        if opacity < 1:
            material.surface_render_method = "BLENDED"
        else:
            shader.inputs["Emission Color"].default_value = (*color[:3], 1)
            shader.inputs["Emission Strength"].default_value = 0.4
        output = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(shader.outputs[0], output.inputs["Surface"])


def read_pixels(image):
    width, height = image.size
    pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(pixels)
    return pixels.reshape(height, width, -1)


def texture_image(name, rgba, color_space):
    height, width = rgba.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    image.colorspace_settings.name = color_space
    image.pixels.foreach_set(rgba.ravel())
    image.update()
    return image


def replace_uv_scale(tree, vector_scale, scale):
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = scale
    tree.links.new(vector_scale.inputs[0].links[0].from_socket, mapping.inputs["Vector"])
    for link in list(vector_scale.outputs[0].links):
        tree.links.new(mapping.outputs["Vector"], link.to_socket)


def prepare_paver():
    # O glTF usa mapa de normais. Converte o relevo escalar do piso externo
    # em normais e troca a escala do nó vetorial por um mapeamento exportável.
    material = bpy.data.materials.get("FIEL2 Paver espinha de peixe")
    if not material:
        return
    tree = material.node_tree
    bump = next(node for node in tree.nodes if node.type == "BUMP")
    height_texture = bump.inputs["Height"].links[0].from_node
    vector_scale = height_texture.inputs["Vector"].links[0].from_node
    scale = vector_scale.inputs["Scale"].default_value
    width, height = height_texture.image.size
    field = read_pixels(height_texture.image)[:, :, 0]
    distance = bump.inputs["Distance"].default_value
    normal = np.ones((height, width, 4), dtype=np.float32)
    for channel, axis, size in [(0, 1, width), (1, 0, height)]:
        normal[:, :, channel] = (
            np.roll(field, 1, axis=axis) - np.roll(field, -1, axis=axis)
        ) * (distance * scale * size / 2)
    normal[:, :, :3] /= np.linalg.norm(normal[:, :, :3], axis=2, keepdims=True)
    normal[:, :, :3] = normal[:, :, :3] * 0.5 + 0.5
    height_texture.image = texture_image("Paver · normal para glTF", normal, "Non-Color")
    replace_uv_scale(tree, vector_scale, (scale, scale, scale))
    normal_map = tree.nodes.new("ShaderNodeNormalMap")
    normal_map.uv_map = "FIEL2_Metros"
    normal_map.inputs["Strength"].default_value = bump.inputs["Strength"].default_value
    tree.links.new(height_texture.outputs["Color"], normal_map.inputs["Color"])
    tree.links.new(normal_map.outputs["Normal"], bump.outputs[0].links[0].to_socket)


def prepare_fabric(name):
    material = bpy.data.materials.get(f"FIEL2 {name}")
    if not material or not material.get("source_asset"):
        return
    tree = material.node_tree
    base = next(node for node in tree.nodes if node.type == "BSDF_PRINCIPLED").inputs["Base Color"]
    tint = base.links[0].from_node
    ramp = tint.inputs[2].links[0].from_node
    divide = ramp.inputs["Value"].links[0].from_node
    grayscale = divide.inputs[0].links[0].from_node
    diffuse = grayscale.inputs[0].links[0].from_node

    # Reproduz a correção de cor da cena FIEL2 na própria imagem do tecido.
    pixels = read_pixels(diffuse.image)[:, :, :3]
    linear = np.where(pixels <= 0.04045, pixels / 12.92, ((pixels + 0.055) / 1.055) ** 2.4)
    luminance = linear @ np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
    luminance /= divide.inputs[1].default_value
    low, high, mapped_low, mapped_high = (
        ramp.inputs[key].default_value for key in ("From Min", "From Max", "To Min", "To Max")
    )
    shade = np.interp(luminance, (low, high), (mapped_low, mapped_high))
    color = np.clip(shade[:, :, None] * np.array(tint.inputs[1].default_value[:3]), 0, 1)
    rgba = np.ones((*luminance.shape, 4), dtype=np.float32)
    rgba[:, :, :3] = np.where(color <= 0.0031308, color * 12.92, 1.055 * color ** (1 / 2.4) - 0.055)
    diffuse.image = texture_image(f"{name} · cor para glTF", rgba, "sRGB")
    tree.links.new(diffuse.outputs["Color"], base)
    vector_scale = diffuse.inputs["Vector"].links[0].from_node
    replace_uv_scale(tree, vector_scale, tuple(vector_scale.inputs[1].default_value))


def bake_procedural_surface(name, kind):
    material = bpy.data.materials.get(f"FIEL2 {name}")
    if not material or not material.use_nodes:
        return
    tree = material.node_tree
    bsdf = tree.nodes.get("Principled BSDF")
    if not bsdf:
        return
    base = bsdf.inputs["Base Color"]
    for link in list(base.links):
        tree.links.remove(link)

    rng = np.random.default_rng(abs(hash(name)) % (2**32))
    size = 512
    rgba = np.ones((size, size, 4), dtype=np.float32)
    if kind == "granito_cinza":
        coarse = rng.uniform(-0.14, 0.14, (size // 4, size // 4, 1)).repeat(4, 0).repeat(4, 1)
        fine = rng.uniform(-0.18, 0.18, (size, size, 1))
        mica = (rng.random((size, size, 1)) > 0.92).astype(np.float32) * 0.22
        dark = (rng.random((size, size, 1)) > 0.84).astype(np.float32) * -0.26
        val = np.clip(0.50 + coarse + fine + mica + dark, 0.12, 0.88)
        rgba[:, :, 0] = np.clip(val[:, :, 0] * 1.01, 0, 1)
        rgba[:, :, 1] = np.clip(val[:, :, 0] * 0.99, 0, 1)
        rgba[:, :, 2] = np.clip(val[:, :, 0] * 0.96, 0, 1)
        scale = (3.0, 3.0, 3.0)
    elif kind == "granito_preto":
        fine = rng.uniform(-0.04, 0.04, (size, size, 1))
        fleck = (rng.random((size, size, 1)) > 0.90).astype(np.float32) * 0.13
        warm = (rng.random((size, size, 1)) > 0.96).astype(np.float32) * 0.08
        val = np.clip(0.11 + fine + fleck, 0.04, 0.34)
        rgba[:, :, 0] = np.clip(val[:, :, 0] + warm[:, :, 0], 0, 1)
        rgba[:, :, 1] = np.clip(val[:, :, 0] + warm[:, :, 0] * 0.85, 0, 1)
        rgba[:, :, 2] = np.clip(val[:, :, 0] * 0.95, 0, 1)
        scale = (3.5, 3.5, 3.5)
    else:  # porcelanato_bege
        # Placa bege polida 60x60 cm com leve variação tonal e rejunte fino.
        y, x = np.mgrid[0:size, 0:size]
        cloud = (
            np.sin(x * 2 * pi / size * 2.0) * 0.012
            + np.cos(y * 2 * pi / size * 3.0) * 0.010
            + rng.uniform(-0.008, 0.008, (size, size))
        )
        rgba[:, :, 0] = np.clip(0.86 + cloud, 0.72, 0.94)
        rgba[:, :, 1] = np.clip(0.81 + cloud * 0.95, 0.68, 0.90)
        rgba[:, :, 2] = np.clip(0.72 + cloud * 0.85, 0.60, 0.82)
        grout = (x < 3) | (y < 3) | ((x >= size // 2) & (x < size // 2 + 2)) | ((y >= size // 2) & (y < size // 2 + 2))
        rgba[grout, :3] *= 0.84
        scale = (1.0, 1.0, 1.0)

    img = texture_image(f"{name} · textura glTF", rgba, "sRGB")
    tex_coord = tree.nodes.new("ShaderNodeTexCoord")
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = scale
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tree.links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    tree.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    tree.links.new(tex.outputs["Color"], base)


def prepare_textures():
    for image in bpy.data.images:
        width, height = image.size
        edge = max(width, height)
        if image.source == "FILE" and edge > MAX_TEXTURE_EDGE:
            image.scale(round(width * MAX_TEXTURE_EDGE / edge), round(height * MAX_TEXTURE_EDGE / edge))

    prepare_paver()
    for name in ("Sofa camurca cinza", "Cadeiras tecido cinza", "Colcha branca"):
        prepare_fabric(name)

    # Gera texturas tileáveis para acabamentos procedurais (granitos e porcelanato).
    bake_procedural_surface("Granito cinza", "granito_cinza")
    bake_procedural_surface("Granito preto", "granito_preto")
    bake_procedural_surface("Porcelanato bege polido", "porcelanato_bege")


def verify_export(glb, required_wall_layers):
    with glb.open("rb") as stream:
        magic, version, size, length, kind = struct.unpack("<4sIII4s", stream.read(20))
        if (magic, version, size, kind) != (b"glTF", 2, glb.stat().st_size, b"JSON"):
            raise ValueError("O Blender gerou um GLB incompleto.")
        data = json.loads(stream.read(length))
    for index, texture in enumerate(data.get("textures", [])):
        webp = texture.get("extensions", {}).get("EXT_texture_webp", {})
        source = webp.get("source", texture.get("source"))
        if source is None or source >= len(data["images"]):
            raise ValueError(f"A textura {index} não tem imagem no GLB.")
    nodes = data["nodes"]
    wall_layers = {
        node["extras"].get("web_layer")
        for node in nodes if "web_layer" in node.get("extras", {})
        if any(
            nodes[index].get("extras", {}).get("web_exterior_walls") and nodes[index].get("children")
            for index in node.get("children", [])
        )
    }
    if wall_layers != required_wall_layers:
        raise ValueError(f"Paredes externas exportadas nas camadas inesperadas: {wall_layers}")


def main():
    variant = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "atual"
    source_path, scene_name, version, prefix, definitions = VARIANTS[variant]
    output = OUTPUT.with_name(f"casa-{variant}.glb")
    if Path(bpy.data.filepath).resolve() != source_path:
        raise ValueError(f"Abra {source_path.relative_to(ROOT)} ao chamar o exportador.")
    source = bpy.data.scenes[scene_name]
    if source.unit_settings.scale_length != 1:
        raise ValueError("A exportação espera uma unidade interna igual a um metro.")
    with source_path.open("rb") as stream:
        source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    presets = camera_presets(prefix, definitions, variant=variant)
    if variant == "estrutural":
        prepare_infrastructure(source)
    if variant == "atual":
        add_observed_furniture(source)
    if variant == "industrial":
        prepare_industrial(source)
    if variant == "atico":
        add_attic_tank_enclosure(source)
    export_scene = bpy.data.scenes.new(f"Sobrado · {version}")
    root = bpy.data.objects.new("Sobrado web", None)
    export_scene.collection.objects.link(root)
    groups = {}
    for layer in LAYERS:
        group = bpy.data.objects.new(layer, None)
        export_scene.collection.objects.link(group)
        group.parent = root
        group["web_layer"] = layer
        groups[layer] = group
    if variant == "atual":
        active_layout = (
            suite_layout() + front_bedroom_layout() + kitchen_layout()
            + bathrooms_layout() + living_room_tv_layout() + laundry_layout()
        )
        skip_prefixes = LAUNDRY_REMOVED_OBJECTS
    elif variant == "industrial":
        active_layout = suite_layout() + (
            (("ATUAL Ripado cozinha",), rotate_between((3.29, 4.92, 0), (3.275, 6.375, 0), 0, (1, 1.52 / 1.068, 1))),
        )
        skip_prefixes = INDUSTRIAL_REMOVED_OBJECTS
    else:
        active_layout = ()
        skip_prefixes = ()
    counts, network_summary = convert_geometry(
        source, export_scene, groups,
        layout=active_layout,
        include_instances=variant == "industrial",
        skip_prefixes=skip_prefixes,
    )
    prepare_textures()
    if not all(counts[key] for key in ("terreo", "superior")):
        raise ValueError(f"Camadas sem geometria: {counts}")
    meta = {
        "version": version,
        "source": source_path.relative_to(ROOT).as_posix(),
        "scene": scene_name,
        "sha256": source_hash,
        "layers": counts,
        "presets": presets,
    }
    if variant == "estrutural":
        meta["networkSummary"] = network_summary
    if variant == "industrial":
        meta["roomVariants"] = [
            {"id": "quarto", "label": "Quarto dos fundos"},
            {"id": "escritorio", "label": "Escritório"},
        ]
    if variant == "atico":
        meta["atticGuides"] = {
            "floorY": 5.45,
            "headroomLevels": [
                {"label": "Pé-direito 1,80 m", "y": 7.25, "color": "#e5a93c"},
                {"label": "Pé-direito 2,10 m", "y": 7.55, "color": "#5ec28f"},
            ],
            "bounds": {"minX": 0.15, "maxX": 6.20, "minZ": -7.05, "maxZ": 1.05},
            "tank": {
                "center": gltf_vector((5.10, 5.10, 5.45 + 0.97 / 2)),
                "baseY": 5.45,
                "radius": 0.76,
                "height": 0.97,
                "maintenanceMargin": 0.60,
                "clearances": [
                    {"label": "Escada: 19 cm (rec. 60 cm)", "critical": True},
                    {"label": "Divisa leste: 39 cm (rec. 60 cm)", "critical": True},
                    {"label": "Forro no ponto baixo: 12 cm livres", "critical": True},
                ],
            },
        }
    root["sobrado"] = json.dumps(meta, ensure_ascii=False)

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as directory:
        temporary = Path(directory) / output.name
        result = bpy.ops.export_scene.gltf(
            filepath=str(temporary), export_format="GLB", use_active_scene=True,
            export_extras=True, export_animations=False, export_yup=True,
            export_meshopt_compression_enable=True,
            export_image_format="WEBP",
            export_image_quality=88, export_image_webp_fallback=False,
        )
        if result != {"FINISHED"} or not temporary.is_file():
            raise RuntimeError(f"Falha ao exportar a cena: {result}")
        required_walls = {"terreo", "superior", "telhado"}
        if variant == "atico":
            required_walls.add("atico")
        verify_export(temporary, required_walls)
        with source_path.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != source_hash:
                raise RuntimeError("O Blender de origem mudou durante a exportação. Execute novamente.")
        os.replace(temporary, output)
    print(f"GLB pronto: {output} ({output.stat().st_size:,} bytes). Objetos de origem: {counts}")


if __name__ == "__main__":
    main()
