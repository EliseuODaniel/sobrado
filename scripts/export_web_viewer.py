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
    ("quarto-frente", "Quarto da frente", "Superior", 2.2),
    ("quarto-branco-armario", "Armários do quarto da frente", "Superior", 2.4),
    ("quarto-fundos", "Quarto dos fundos", "Superior", 2.2),
    ("banheiro-suite", "Banheiro da suíte", "Superior", 1.5),
    ("banheiro-social", "Banheiro social", "Superior", 1.5),
)
VARIANTS = {
    "atual": (SOURCE, SOURCE_SCENE, "Atual fiel às fotos v02 · mobiliário revisado", "FIEL2_", PRESETS),
    "industrial": (
        ROOT / "projeto/industrial/casa-industrial-fotorrealista.blend",
        "PHOTO6_volumetria", "Industrial v06", "PHOTO6_",
        (
            ("fachada-frontal", "Fachada", "Exterior", 15),
            ("sala-frente", "Sala", "Térreo", 3),
            ("cozinha", "Cozinha", "Térreo", 2.5),
            ("bar", "Bar", "Térreo", 2.5),
            ("suite", "Suíte", "Superior", 2),
            ("quarto-fundos", "Quarto dos fundos", "Superior", 2),
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
            ("atico-interior-frente", "Interior do ático", "Ático", 2.3),
            ("atico-reservatorio", "Caixa-d’água", "Ático", 2),
        ),
    ),
}


def gltf_vector(vector):
    x, y, z = vector
    return [x, z, -y]


def camera_presets(prefix, definitions):
    presets = []
    for name, label, section, distance in definitions:
        bpy.context.window.scene = bpy.data.scenes[f"{prefix}{name}"]
        bpy.context.view_layer.update()
        scene = bpy.context.scene
        camera = scene.camera.evaluated_get(bpy.context.evaluated_depsgraph_get())
        position = camera.matrix_world.translation
        forward = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        target = position + forward * distance
        if prefix == "FIEL2_" and name == "suite":
            position = Vector((2.86, -0.20, 4.20))
            target = Vector((1.70, 1.48, 3.86))
        if prefix == "FIEL2_" and name == "quarto-branco-armario":
            target = Vector((4.82, 1.72, 3.92))
        render = scene.render
        aspect = render.resolution_x * render.pixel_aspect_x / (
            render.resolution_y * render.pixel_aspect_y
        )
        # As câmeras da entrega usam o sensor horizontal em imagens horizontais.
        vertical_fov = 2 * atan(tan(camera.data.angle_x / 2) / aspect)
        presets.append({
            "id": name, "label": label, "section": section,
            "position": gltf_vector(position), "target": gltf_vector(target),
            "fov": vertical_fov, "aspect": aspect,
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
        (("ATUAL Cama suite", "ATUAL Apoio lateral cabeceira", "ATUAL Mesa cabeceira",
          "FIEL2 Suite cabeceira modulo", "FIEL2 Suite colcha drapeada", "FIEL2 Suite travesseiro"),
         rotate_between((1.30, .95, 0), (2.17, .95, 0), pi)),
        (("ATUAL Painel TV suite", "ATUAL TV suite", "ATUAL Movel lareira suite", "ATUAL Nicho lareira"),
         rotate_between((3.265, .65, 0), (2.26, 3.15, 0), pi / 2)),
        (("FIEL2 Suite ar condicionado",),
         rotate_between((.29, 2.35, 0), (3.17, 1.22, 0), pi)),
        (("FIEL2 Suite aletas split",),
         rotate_between((.29, 2.35, 0), (2.90, 1.22, 0), pi)),
        # O painel acompanha a cabeceira e termina antes da porta da suíte.
        (("FIEL2 Suite fundo cabeceira", "FIEL2 Suite friso vertical"),
         rotate_between((.165, 1.36, 0), (3.28, .95, 0), pi, (1, .74, 1))),
    )


def front_bedroom_layout():
    # quartobranco1/2: roupeiro ao lado da entrada e TV/estante diante da cama.
    wardrobe = rotate_between((3.79, .55, 0), (5.26, 1.68, 0), -pi / 2, (1, 1.85 / 1.60, 1))
    return (
        (("ATUAL Roupeiro quarto branco",), wardrobe),
        (("FIEL2 Roupeiro branco porta", "FIEL2 Roupeiro branco puxador"),
         wardrobe @ Matrix.Translation((0, .26, 0))),
        (("FIEL2 Quarto branco TV", "FIEL2 Quarto branco estante"),
         rotate_between((4.45, 1.99, 0), (3.48, .55, 0), pi / 2)),
        (("ATUAL Estrado cama.001", "ATUAL Colchão cama.001", "ATUAL Pé cama.004",
          "ATUAL Pé cama.005", "ATUAL Pé cama.006", "ATUAL Pé cama.007",
          "FIEL2 Cama branca", "FIEL2 Quarto branco colcha", "FIEL2 Quarto branco travesseiro",
          "ATUAL Armario suspenso", "FIEL2 Aereo branco", "FIEL2 Quarto branco papel coracoes"),
         Matrix.Translation((0, -.26, 0))),
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

    # quartoazul2: módulo estreito entre a bancada e a janela, à frente do beliche.
    box("FIEL2 Armário estreito quarto azul", (3.705, 6.792, 3.95), (.47, .49, 2.46), "Branco laqueado", .01)
    for y in (6.668, 6.916):
        box("FIEL2 Porta armário quarto azul", (3.949, y, 3.95), (.018, .243, 2.44), "Branco laqueado", .004)
    for y in (6.762, 6.822):
        box("FIEL2 Puxador armário quarto azul", (3.969, y, 3.87), (.023, .012, .24), "Inox", .004)

    # sala5: banco estofado encostado à parede lateral, depois da mesa.
    box("FIEL2 Base banco estofado jantar", (.41, 6.12, .19), (.47, 1.18, .30), "Cabeceira bege", .035)
    for y in (5.728, 6.12, 6.512):
        box("FIEL2 Assento banco estofado jantar", (.41, y, .377), (.47, .388, .11), "Cabeceira bege", .033)


def convert_geometry(source, export_scene, groups, layout=(), include_instances=False):
    bpy.context.window.scene = source
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    batches = defaultdict(list)
    counts = dict.fromkeys(LAYERS, 0)
    wall_groups = {}
    network_groups = {}
    for obj, evaluated, world, collections, network in evaluated_geometry(source, depsgraph, include_instances):
        if obj.name == "R07 Plano cenario":
            continue
        for prefixes, transform in layout:
            if obj.name.startswith(prefixes):
                world = transform @ world
                break
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
        if not mesh.polygons:
            bpy.data.meshes.remove(mesh)
            continue
        min_z = min((world @ Vector(corner)).z for corner in evaluated.bound_box)
        layer = "instalacoes" if network else layer_for(obj, collections, min_z)
        wall_key = exterior_wall_key(obj, collections)
        parent = groups[layer]
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
        counts[layer] += 1
        if not keep_separate(mesh):
            # As malhas unidas precisam usar o mesmo conjunto de mapas UV.
            uv_layout = tuple(uv.name for uv in mesh.uv_layers), mesh.uv_layers.active_index
            # Mantém cada parede separada para ordenar as superfícies de vidro por distância.
            batches[layer, network or wall_key, uv_layout].append(clone)

    bpy.context.window.scene = export_scene
    bpy.context.view_layer.update()
    for (layer, wall_key, _), objects in batches.items():
        if len(objects) < 2:
            continue
        with bpy.context.temp_override(active_object=objects[0], selected_editable_objects=objects):
            bpy.ops.object.join()
        objects[0].name = f"Paredes externas · {wall_key}" if wall_key else f"Malhas · {layer}"
    return counts


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


def prepare_textures():
    for image in bpy.data.images:
        width, height = image.size
        edge = max(width, height)
        if image.source == "FILE" and edge > MAX_TEXTURE_EDGE:
            image.scale(round(width * MAX_TEXTURE_EDGE / edge), round(height * MAX_TEXTURE_EDGE / edge))

    prepare_paver()
    for name in ("Sofa camurca cinza", "Cadeiras tecido cinza", "Colcha branca"):
        prepare_fabric(name)

    # Estes acabamentos definem uma cor-base além do padrão procedural.
    # O exportador representa essa cor diretamente quando o padrão não é suportado.
    for name in ("Granito cinza", "Granito preto", "Porcelanato bege polido"):
        material = bpy.data.materials.get(f"FIEL2 {name}")
        if material:
            tree = material.node_tree
            base = tree.nodes["Principled BSDF"].inputs["Base Color"]
            for link in list(base.links):
                tree.links.remove(link)


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
    presets = camera_presets(prefix, definitions)
    if variant == "estrutural":
        prepare_infrastructure(source)
    if variant == "atual":
        add_observed_furniture(source)
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
    counts = convert_geometry(
        source, export_scene, groups,
        layout=suite_layout() + front_bedroom_layout() if variant == "atual" else (),
        include_instances=variant != "atual",
    )
    prepare_textures()
    if not all(counts[key] for key in ("terreo", "superior")):
        raise ValueError(f"Camadas sem geometria: {counts}")
    root["sobrado"] = json.dumps({
        "version": version,
        "source": source_path.relative_to(ROOT).as_posix(),
        "scene": scene_name,
        "sha256": source_hash,
        "layers": counts,
        "presets": presets,
    }, ensure_ascii=False)

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as directory:
        temporary = Path(directory) / output.name
        result = bpy.ops.export_scene.gltf(
            filepath=str(temporary), export_format="GLB", use_active_scene=True,
            export_extras=True, export_animations=False, export_yup=True,
            export_meshopt_compression_enable=True,
            export_image_format="WEBP" if variant == "atual" else "JPEG",
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
