import * as THREE from 'three';

const ink = 0xf2d9b0;
const palettes = {
  telhado: [0x54402d, 0x967545],
  default: [0x383730, 0x757064],
};

export function createSheetStyle(root) {
  const meshes = [];
  const materials = new Map();
  const edges = new Map();
  const pencil = new THREE.LineBasicMaterial({
    color: ink, transparent: true, opacity: 0.50, depthWrite: false,
  });
  const sitePencil = new THREE.LineBasicMaterial({
    color: ink, transparent: true, opacity: 0.19, depthWrite: false,
  });

  root.traverse((node) => {
    if (!node.isMesh) return;
    let layer = node.parent;
    while (layer && !layer.userData.web_layer) layer = layer.parent;
    const key = layer?.userData.web_layer;
    if (key === 'instalacoes') return;
    meshes.push({ mesh: node, key, original: node.material });
  });

  function paperMaterial(source, layer) {
    if (!materials.has(source)) materials.set(source, new Map());
    const variants = materials.get(source);
    if (variants.has(layer)) return variants.get(layer);
    const [dark, light] = palettes[layer] ?? palettes.default;
    const color = source.color ?? new THREE.Color(0xffffff);
    const value = color.r * 0.2126 + color.g * 0.7152 + color.b * 0.0722;
    const tint = new THREE.Color(dark).lerp(new THREE.Color(light), Math.sqrt(value));
    const surface = {
      color: source.transparent ? 0x739c8e : tint,
      transparent: source.transparent,
      opacity: source.transparent ? Math.min(source.opacity, 0.32) : 1,
      depthWrite: !source.transparent,
      side: source.side,
      forceSinglePass: true,
      polygonOffset: !source.transparent,
      polygonOffsetFactor: 1,
      polygonOffsetUnits: 1,
    };
    const material = layer === 'contexto' && !source.transparent
      ? new THREE.MeshBasicMaterial({ ...surface, color: 0x302b25, toneMapped: false })
      : new THREE.MeshLambertMaterial(surface);
    if (layer === 'telhado' && !source.transparent) {
      material.onBeforeCompile = (shader) => {
        shader.vertexShader = shader.vertexShader
          .replace('#include <common>', '#include <common>\nvarying vec3 sheetPosition;')
          .replace('#include <begin_vertex>', '#include <begin_vertex>\nsheetPosition = (modelMatrix * vec4(position, 1.0)).xyz;');
        shader.fragmentShader = shader.fragmentShader
          .replace('#include <common>', '#include <common>\nvarying vec3 sheetPosition;')
          .replace('#include <color_fragment>', `#include <color_fragment>
            float spacing = dot(sheetPosition, vec3(6.0, 2.0, 1.0));
            float softness = fwidth(spacing);
            float stroke = 1.0 - smoothstep(0.02, 0.09 + softness, abs(fract(spacing) - 0.5));
            diffuseColor.rgb *= 1.0 - stroke * 0.21 * (1.0 - smoothstep(0.15, 0.6, softness));
          `);
      };
    }
    variants.set(layer, material);
    return material;
  }

  return {
    apply(enabled, wallMaterials) {
      for (const entry of meshes) {
        const { mesh, key, original } = entry;
        const source = wallMaterials.get(mesh) ?? original;
        const slots = Array.isArray(source) ? source : [source];
        mesh.material = enabled
          ? (Array.isArray(source) ? slots.map((material) => paperMaterial(material, key)) : paperMaterial(source, key))
          : source;
        const opaque = slots.every((material) => !material.transparent);
        if (enabled && opaque && entry.outline === undefined) {
          const geometry = mesh.geometry;
          const vertices = geometry.index?.count ?? geometry.attributes.position.count;
          // Os detalhes densos mantêm o sombreamento da prancha, sem gerar
          // contornos para cada peça de uma malha de mobiliário.
          entry.outline = null;
          if (vertices <= 9000 && !mesh.isInstancedMesh && !mesh.isSkinnedMesh) {
            if (!edges.has(geometry)) edges.set(geometry, new THREE.EdgesGeometry(geometry, 26));
            const lines = edges.get(geometry);
            if (lines.attributes.position.count) {
              entry.outline = new THREE.LineSegments(lines, key === 'contexto' ? sitePencil : pencil);
              mesh.add(entry.outline);
            }
          }
        }
        if (entry.outline) entry.outline.visible = enabled && opaque;
      }
    },
  };
}
