import * as THREE from 'three';

// Cotas de piso acabado no sistema de coordenadas das maquetes exportadas (glTF Y = Blender Z).
export const floorElevation = { terreo: 0, superior: 2.7, atico: 5.45 };

export const furnitureCatalog = {
  sofa: {
    name: 'Sofá', category: 'seating', width: 2.1, depth: 0.9, height: 0.85, color: 0x778765, roughness: 0.85,
    parts: [
      [0, 0.17, 0, 1, 0.34, 1], [0, 0.43, 0.05, 0.86, 0.19, 0.72],
      [0, 0.58, -0.39, 1, 0.55, 0.22],
      [-0.46, 0.42, 0, 0.08, 0.48, 1], [0.46, 0.42, 0, 0.08, 0.48, 1],
    ],
  },
  armchair: {
    name: 'Poltrona', category: 'seating', width: 0.85, depth: 0.85, height: 0.82, color: 0xa46c44, roughness: 0.78,
    parts: [
      [0, 0.2, 0, 0.95, 0.4, 0.95], [0, 0.54, -0.38, 0.95, 0.56, 0.22],
      [-0.43, 0.42, 0, 0.14, 0.45, 0.95], [0.43, 0.42, 0, 0.14, 0.45, 0.95],
    ],
  },
  coffee_round: {
    name: 'Mesa redonda travertino', category: 'coffee_table', shape: 'round', width: 0.95, depth: 0.95, height: 0.40, color: 0xd9cfc1, roughness: 0.65,
    customBuild: 'round_travertine',
  },
  coffee_oak: {
    name: 'Mesa centro carvalho', category: 'coffee_table', width: 1.14, depth: 0.70, height: 0.40, color: 0xb68a5c, roughness: 0.62,
    customBuild: 'oak_books',
  },
  coffee_glass: {
    name: 'Mesa vidro e latão', category: 'coffee_table', width: 1.10, depth: 0.65, height: 0.40, color: 0xc59d52, roughness: 0.28,
    customBuild: 'glass_brass',
  },
  table: {
    name: 'Mesa de jantar', category: 'table', width: 1.5, depth: 0.85, height: 0.76, color: 0x9d7553, roughness: 0.62,
    parts: [
      [0, 0.73, 0, 1, 0.06, 1],
      [-0.43, 0.35, -0.39, 0.05, 0.7, 0.08], [0.43, 0.35, -0.39, 0.05, 0.7, 0.08],
      [-0.43, 0.35, 0.39, 0.05, 0.7, 0.08], [0.43, 0.35, 0.39, 0.05, 0.7, 0.08],
    ],
  },
  sideboard: {
    name: 'Aparador / Buffet', category: 'storage', width: 1.60, depth: 0.45, height: 0.80, color: 0x7c5b41, roughness: 0.6,
    parts: [
      [0, 0.48, 0, 1, 0.62, 1],
      [-0.44, 0.09, -0.38, 0.04, 0.18, 0.08], [0.44, 0.09, -0.38, 0.04, 0.18, 0.08],
      [-0.44, 0.09, 0.38, 0.04, 0.18, 0.08], [0.44, 0.09, 0.38, 0.04, 0.18, 0.08],
    ],
  },
  bed: {
    name: 'Cama casal', category: 'bed', width: 1.58, depth: 1.98, height: 0.9, color: 0xc8bfb0, roughness: 0.86,
    parts: [
      [0, 0.14, 0, 1, 0.28, 1], [0, 0.37, 0.02, 0.97, 0.18, 0.94],
      [0, 0.45, -0.47, 1, 0.9, 0.06],
      [-0.25, 0.49, -0.33, 0.41, 0.10, 0.18], [0.25, 0.49, -0.33, 0.41, 0.10, 0.18],
    ],
  },
  single_bed: {
    name: 'Cama solteiro', category: 'bed', width: 0.9, depth: 1.9, height: 0.85, color: 0xc2b8a3, roughness: 0.86,
    parts: [
      [0, 0.14, 0, 1, 0.28, 1], [0, 0.36, 0.02, 0.96, 0.18, 0.94],
      [0, 0.42, -0.47, 1, 0.84, 0.06], [0, 0.48, -0.33, 0.68, 0.10, 0.18],
    ],
  },
  desk: {
    name: 'Escrivaninha', category: 'table', width: 1.4, depth: 0.65, height: 0.75, color: 0xb89668, roughness: 0.62,
    parts: [
      [0, 0.73, 0, 1, 0.05, 1],
      [-0.47, 0.36, 0, 0.05, 0.72, 0.94], [0.47, 0.36, 0, 0.05, 0.72, 0.94],
    ],
  },
  wardrobe: {
    name: 'Armário', category: 'storage', width: 1.6, depth: 0.6, height: 2.2, color: 0xd0cbbd, roughness: 0.58,
    parts: [
      [0, 1.1, 0, 1, 2.2, 1],
    ],
  },
  fridge: {
    name: 'Geladeira', category: 'appliance', width: 0.7, depth: 0.7, height: 1.78, color: 0xadb8bd, roughness: 0.32, metalness: 0.45,
    parts: [
      [0, 0.89, 0, 1, 1.78, 1],
    ],
  },
  rug: {
    name: 'Tapete tecido', category: 'decor', width: 2.2, depth: 1.5, height: 0.025, color: 0xc8bca8, roughness: 0.95,
    parts: [
      [0, 0.012, 0, 1, 0.024, 1],
    ],
  },
  plant: {
    name: 'Planta em vaso', category: 'decor', shape: 'round', width: 0.48, depth: 0.48, height: 1.18, color: 0x4e7a52, roughness: 0.72,
    customBuild: 'plant_pot',
  },
  lamp: {
    name: 'Luminária piso', category: 'lighting', shape: 'round', width: 0.42, depth: 0.42, height: 1.62, color: 0xdcb978, roughness: 0.35,
    customBuild: 'floor_lamp',
  },
  custom: {
    name: 'Móvel', category: 'custom', width: 1.2, depth: 0.6, height: 0.8, color: 0x7aa695, roughness: 0.7,
    parts: [
      [0, 0.4, 0, 1, 0.8, 1],
    ],
  },
};
const catalog = furnitureCatalog;

const roomLabels = {
  terreo: [
    { label: 'Sala', x: 1.65, z: -1.65 },
    { label: 'Jantar', x: 1.65, z: -4.5 },
    { label: 'Bar / Lazer', x: 1.65, z: -8.3 },
    { label: 'Cozinha', x: 4.9, z: -5.6 },
    { label: 'Lavanderia', x: 4.9, z: -9.1 },
    { label: 'Lavabo', x: 4.5, z: -2.6 },
    { label: 'Escada', x: 5.0, z: -3.6 },
    { label: 'Garagem', x: 4.8, z: -0.6 },
  ],
  superior: [
    { label: 'Suíte', x: 1.7, z: -1.3 },
    { label: 'Quarto frente', x: 4.85, z: -0.5 },
    { label: 'Quarto fundos', x: 4.85, z: -5.6 },
    { label: 'Banh. suíte', x: 0.9, z: -4.8 },
    { label: 'Banh. social', x: 2.55, z: -4.8 },
  ],
  atico: [
    { label: 'Ático', x: 2.4, z: -3.2 },
    { label: 'Escada', x: 5.0, z: -3.1 },
    { label: 'Caixa 1000L', x: 5.1, z: -5.1 },
  ],
};

const floorLabels = { terreo: 'Térreo', superior: 'Superior', atico: 'Ático' };
const formatMeters = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });

// Cotas oficiais de estacionamento (ARQ01 / ARQ03 + simulação máxima com Renault Sandero 1.0 2018 na Vaga 2).
const PARKING = {
  lotMinX: 0,
  lotMaxX: 6.35,
  frontMinZ: 0,
  frontMaxZ: 2.5,
  garageMinX: 3.4,
  garageMaxX: 6.25,
  garageMinZ: -2.0,
  overhangZ: 1.2,
  // Vaga 1 (garagem principal ARQ01: 2,20 x 4,50 m) e SUV em ocupação máxima (4,48 x 1,84 m)
  slot1MinX: 3.56,
  slot1MaxX: 5.76,
  slot1MinZ: -2.0,
  slot1MaxZ: 2.5,
  car1CenterX: 4.66,
  car1CenterZ: 0.25,
  car1Width: 1.84,
  car1Length: 4.48,
  car1Label: 'SUV máx. 4,48×1,84m',
  // Vaga 2 (lateral sala: 2,00 x 2,50 m no lote / 3,25 m faixa rua) com Renault Sandero 1.0 2018 (4,06 x 1,733 m)
  slot2MinX: 0.68,
  slot2MaxX: 2.68,
  slot2MinZ: 0.0,
  slot2LotMaxZ: 2.5,
  slot2StripeMaxZ: 3.25,
  slot2MaxZ: 4.09,
  car2CenterX: 1.68,
  car2CenterZ: 2.06,
  car2Width: 1.733,
  car2Length: 4.06,
  car2Label: 'Sandero 2018 · 4,06×1,73m',
};

function sectionLines(node, height) {
  const lines = [];
  const box = new THREE.Box3();
  const corners = Array.from({ length: 3 }, () => new THREE.Vector3());
  const intersections = [new THREE.Vector3(), new THREE.Vector3()];
  node.traverse((mesh) => {
    if (!mesh.isMesh || !mesh.visible) return;
    const { geometry, matrixWorld } = mesh;
    const { index, attributes: { position } } = geometry;
    if (!geometry.boundingBox) geometry.computeBoundingBox();
    box.copy(geometry.boundingBox).applyMatrix4(matrixWorld);
    if (height <= box.min.y || height >= box.max.y) return;
    const count = index?.count ?? position.count;
    for (let start = 0; start + 2 < count; start += 3) {
      for (let i = 0; i < 3; i++) {
        corners[i].fromBufferAttribute(position, index ? index.getX(start + i) : start + i).applyMatrix4(matrixWorld);
      }
      let hits = 0;
      for (let i = 0; i < 3; i++) {
        const a = corners[i];
        const b = corners[(i + 1) % 3];
        if ((a.y < height) === (b.y < height)) continue;
        intersections[hits++].lerpVectors(a, b, (height - a.y) / (b.y - a.y));
      }
      if (hits === 2) lines.push(intersections[0].x, intersections[0].z, intersections[1].x, intersections[1].z);
    }
  });
  return lines;
}

export function createPlan({
  layers, scene, variant, requestFrame, onMeasureUpdate,
  onSelectionChange, onFurnitureChange,
}) {
  const canvas = document.querySelector('#plan-canvas');
  const context = canvas.getContext('2d');
  const title = document.querySelector('#plan-title');
  const floorPicker = document.querySelector('#plan-floor');
  const labelsToggle = document.querySelector('#plan-labels');
  const select = document.querySelector('#furniture-type');
  const widthInput = document.querySelector('#furniture-width');
  const depthInput = document.querySelector('#furniture-depth');
  const place = document.querySelector('#furniture-place');
  const move = document.querySelector('#furniture-move');
  const rotateFine = document.querySelector('#furniture-rotate-fine');
  const rotate = document.querySelector('#furniture-rotate');
  const remove = document.querySelector('#furniture-remove');
  const snapToggle = document.querySelector('#furniture-snap');
  const exportBtn = document.querySelector('#furniture-export');
  const importBtn = document.querySelector('#furniture-import');
  const fileInput = document.querySelector('#furniture-file');
  const status = document.querySelector('#furniture-status');

  const ac = new AbortController();
  const { signal } = ac;
  const outlines = new Map();
  const furniture = [];
  const group = new THREE.Group();
  const highlight = new THREE.MeshStandardMaterial({ color: 0x62b4d9, roughness: 0.45, metalness: 0.08 });
  const box = new THREE.BoxGeometry();
  const storageKey = `sobrado.estudo-mobiliario.${variant}`;
  scene.add(group);

  let nextItemId = 1;
  let floor = 'terreo';
  let visibleFloor = 'full';
  let selected = null;
  let mode = null;
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let shown = false;
  let cursor = null;
  let transform = null;
  let cameraPose = null;
  let measuring = false;
  let measurePoints = [];
  let draggingPan = null;
  let movedDuringDrag = false;
  let showParkingGuides = true;
  let showParkingCar = true;
  let emptyHidden = false;

  function itemDimensions(entry) {
    const spec = catalog[entry.type] ?? catalog.custom;
    const width = Number.isFinite(entry.width) && entry.width >= 0.2 ? entry.width : spec.width;
    const depth = Number.isFinite(entry.depth) && entry.depth >= 0.2 ? entry.depth : spec.depth;
    const height = Number.isFinite(entry.height) && entry.height >= 0.02 ? entry.height : spec.height;
    return { width, depth, height, spec };
  }

  function disposeModelGeometry(model, extraMaterials) {
    model.traverse((node) => {
      if (node.isMesh && node.geometry && node.geometry !== box) {
        node.geometry.dispose();
      }
    });
    for (const m of extraMaterials ?? []) m.dispose();
  }

  function populateModel(model, spec, width, depth, height, material) {
    const extraMaterials = [];
    const addPart = (mesh, isPrimary = true) => {
      mesh.castShadow = height > 0.05;
      mesh.receiveShadow = true;
      mesh.userData.isPrimaryMat = isPrimary;
      model.add(mesh);
    };

    if (spec.customBuild === 'round_travertine') {
      const r = Math.min(width, depth) / 2;
      const top = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 0.055, 28), material);
      top.position.y = height - 0.028;
      const ped = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.42, r * 0.48, height - 0.055, 22), material);
      ped.position.y = (height - 0.055) / 2;
      addPart(top, true);
      addPart(ped, true);
    } else if (spec.customBuild === 'oak_books') {
      const top = new THREE.Mesh(box, material);
      top.position.set(0, height - 0.03, 0);
      top.scale.set(width, 0.06, depth);
      addPart(top, true);
      const legMat = new THREE.MeshStandardMaterial({ color: 0x3b352f, roughness: 0.55, metalness: 0.25 });
      extraMaterials.push(legMat);
      for (const sx of [-0.42, 0.42]) {
        for (const sz of [-0.38, 0.38]) {
          const leg = new THREE.Mesh(box, legMat);
          leg.position.set(sx * width, (height - 0.06) / 2, sz * depth);
          leg.scale.set(0.05, height - 0.06, 0.05);
          addPart(leg, false);
        }
      }
      // Pilha de livros decorativos (como no vídeo referência)
      const bookColors = [0xd8d0c4, 0x5c6f5e, 0xb88b61];
      bookColors.forEach((col, i) => {
        const bm = new THREE.MeshStandardMaterial({ color: col, roughness: 0.78 });
        extraMaterials.push(bm);
        const book = new THREE.Mesh(box, bm);
        book.position.set(-width * 0.14, height + 0.015 + i * 0.028, depth * 0.06);
        book.rotation.y = (i - 1) * 0.11;
        book.scale.set(0.28 - i * 0.02, 0.024, 0.21 - i * 0.015);
        addPart(book, false);
      });
    } else if (spec.customBuild === 'glass_brass') {
      const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0xdaf0f5, transparent: true, opacity: 0.42, roughness: 0.08, metalness: 0.05,
      });
      extraMaterials.push(glassMat);
      const top = new THREE.Mesh(box, glassMat);
      top.position.set(0, height - 0.015, 0);
      top.scale.set(width, 0.022, depth);
      addPart(top, false);
      const frame = new THREE.Mesh(box, material);
      frame.position.set(0, height - 0.036, 0);
      frame.scale.set(width * 0.96, 0.02, depth * 0.96);
      addPart(frame, true);
      for (const sx of [-0.45, 0.45]) {
        for (const sz of [-0.42, 0.42]) {
          const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, height - 0.03, 12), material);
          leg.position.set(sx * width, (height - 0.03) / 2, sz * depth);
          addPart(leg, true);
        }
      }
    } else if (spec.customBuild === 'plant_pot') {
      const potR = Math.min(width, depth) * 0.36;
      const potMat = new THREE.MeshStandardMaterial({ color: 0xcabca9, roughness: 0.78 });
      const soilMat = new THREE.MeshStandardMaterial({ color: 0x3b2f26, roughness: 0.95 });
      extraMaterials.push(potMat, soilMat);
      const pot = new THREE.Mesh(new THREE.CylinderGeometry(potR, potR * 0.78, height * 0.34, 18), potMat);
      pot.position.y = height * 0.17;
      addPart(pot, false);
      const soil = new THREE.Mesh(new THREE.CylinderGeometry(potR * 0.92, potR * 0.92, 0.03, 16), soilMat);
      soil.position.y = height * 0.33;
      addPart(soil, false);
      const crownOffsets = [
        [0, height * 0.68, 0, potR * 1.18],
        [potR * 0.52, height * 0.58, potR * 0.3, potR * 0.85],
        [-potR * 0.48, height * 0.62, -potR * 0.32, potR * 0.88],
        [potR * 0.25, height * 0.82, -potR * 0.28, potR * 0.75],
      ];
      for (const [ox, oy, oz, rad] of crownOffsets) {
        const leaf = new THREE.Mesh(new THREE.DodecahedronGeometry(rad, 1), material);
        leaf.position.set(ox, oy, oz);
        addPart(leaf, true);
      }
    } else if (spec.customBuild === 'floor_lamp') {
      const r = Math.min(width, depth) * 0.45;
      const baseMat = new THREE.MeshStandardMaterial({ color: 0x26282b, roughness: 0.42, metalness: 0.55 });
      const shadeMat = new THREE.MeshStandardMaterial({
        color: 0xf7ecd7, emissive: 0xffd596, emissiveIntensity: 0.48, roughness: 0.85, side: THREE.DoubleSide,
      });
      extraMaterials.push(baseMat, shadeMat);
      const base = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.72, r * 0.78, 0.03, 20), baseMat);
      base.position.y = 0.015;
      addPart(base, false);
      const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, height * 0.84, 12), material);
      stem.position.y = height * 0.42;
      addPart(stem, true);
      const shade = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.68, r, height * 0.22, 22, 1, true), shadeMat);
      shade.position.y = height * 0.88;
      addPart(shade, false);
    } else {
      for (const [rx, y, rz, rw, h, rd] of spec.parts) {
        const mesh = new THREE.Mesh(box, material);
        mesh.position.set(rx * width, y, rz * depth);
        mesh.scale.set(rw * width, h, rd * depth);
        addPart(mesh, true);
      }
    }
    return extraMaterials;
  }

  function build(entry) {
    const { width, depth, height, spec } = itemDimensions(entry);
    const model = new THREE.Group();
    const baseColor = Number.isFinite(entry.color) ? entry.color : spec.color;
    const material = new THREE.MeshStandardMaterial({
      color: baseColor,
      roughness: spec.roughness ?? 0.72,
      metalness: spec.metalness ?? (spec.customBuild === 'glass_brass' ? 0.72 : 0.06),
    });
    const extraMaterials = populateModel(model, spec, width, depth, height, material);
    const id = entry.id ?? `mob-${nextItemId++}`;
    const item = {
      id,
      type: entry.type,
      floor: entry.floor,
      x: entry.x,
      z: entry.z,
      angle: entry.angle ?? 0,
      width,
      depth,
      height,
      color: baseColor,
      finish: entry.finish ?? null,
      label: entry.label ?? null,
      model,
      material,
      extraMaterials,
    };
    model.userData.furnitureId = id;
    group.add(model);
    furniture.push(item);
    return item;
  }

  function rebuildItemMesh(item) {
    const { width, depth, height, spec } = itemDimensions(item);
    item.width = width;
    item.depth = depth;
    item.height = height;
    disposeModelGeometry(item.model, item.extraMaterials);
    item.model.clear();
    item.material.color.setHex(Number.isFinite(item.color) ? item.color : spec.color);
    item.material.roughness = spec.roughness ?? 0.72;
    item.material.metalness = spec.metalness ?? (spec.customBuild === 'glass_brass' ? 0.72 : 0.06);
    item.material.needsUpdate = true;
    item.extraMaterials = populateModel(item.model, spec, width, depth, height, item.material);
  }

  function serializeEntries() {
    return furniture.map(({ id, type, floor: f, x, z, angle, width, depth, color, finish, label }) => ({
      id, type, floor: f, x, z, angle, width, depth, color, finish, label,
    }));
  }

  function writeStudies() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(serializeEntries()));
      return true;
    } catch {
      return false;
    }
  }

  function loadEntries(entries) {
    for (const item of furniture) {
      group.remove(item.model);
      disposeModelGeometry(item.model, item.extraMaterials);
      item.material.dispose();
    }
    furniture.length = 0;
    selected = null;
    if (!Array.isArray(entries)) return;
    for (const entry of entries.slice(0, 80)) {
      const bounds = layers.get(entry?.floor)?.box;
      if (Object.hasOwn(catalog, entry?.type) && Object.hasOwn(floorElevation, entry?.floor) &&
        bounds && [entry.x, entry.z, entry.angle].every(Number.isFinite) &&
        entry.x >= bounds.min.x - 0.5 && entry.x <= bounds.max.x + 0.5 &&
        entry.z >= bounds.min.z - 0.5 && entry.z <= bounds.max.z + 0.5) {
        build(entry);
      }
    }
  }

  try {
    loadEntries(JSON.parse(localStorage.getItem(storageKey) ?? '[]'));
  } catch {
    // Sessão sem armazenamento continua funcionando em memória.
  }

  function updateModels() {
    for (const item of furniture) {
      item.model.position.set(item.x, floorElevation[item.floor] + 0.01, item.z);
      item.model.rotation.y = -item.angle;
      item.model.visible = !emptyHidden && (visibleFloor === 'full' || visibleFloor === item.floor);
      for (const mesh of item.model.children) {
        if (mesh.userData.isPrimaryMat !== false) {
          mesh.material = selected === item && shown ? highlight : item.material;
        }
      }
    }
    requestFrame();
  }

  function setControls(message) {
    place.setAttribute('aria-pressed', String(mode === 'place'));
    move.setAttribute('aria-pressed', String(mode === 'move'));
    move.disabled = rotate.disabled = rotateFine.disabled = remove.disabled = !selected;
    canvas.toggleAttribute('data-editing', Boolean(mode || measuring));
    if (message) {
      status.textContent = message;
      return;
    }
    if (measuring) {
      status.textContent = measurePoints.length === 1
        ? 'Clique no segundo ponto da planta para medir.'
        : 'Trena ativa: clique em dois pontos da planta.';
      return;
    }
    status.textContent = selected
      ? `${catalog[selected.type].name} (${formatMeters.format(selected.width)} × ${formatMeters.format(selected.depth)} m) · ${Math.round(THREE.MathUtils.radToDeg(selected.angle))}°`
      : 'Arraste para deslocar, role para zoom. Os móveis de estudo ficam neste navegador.';
  }

  function getOutline() {
    if (!outlines.has(floor)) {
      const targetLayer = layers.get(floor) ?? layers.get('terreo');
      const { node, box: bounds } = targetLayer;
      const elevation = floorElevation[floor] ?? 0;
      outlines.set(floor, {
        bounds,
        low: sectionLines(node, elevation + 0.34),
        cut: sectionLines(node, elevation + 1.07),
      });
    }
    return outlines.get(floor);
  }

  function snapCoord(value) {
    return snapToggle.checked ? Math.round(value * 10) / 10 : value;
  }

  function draw() {
    if (!shown || !canvas.clientWidth || !canvas.clientHeight) return;
    const { clientWidth: width, clientHeight: height } = canvas;
    const ratio = Math.min(window.devicePixelRatio, 2);
    if (canvas.width !== Math.round(width * ratio)) canvas.width = Math.round(width * ratio);
    if (canvas.height !== Math.round(height * ratio)) canvas.height = Math.round(height * ratio);
    const { bounds: rawBounds, low, cut } = getOutline();
    const bounds = rawBounds.clone();
    if (floor === 'terreo' && (showParkingGuides || showParkingCar)) {
      bounds.min.x = Math.min(bounds.min.x, PARKING.lotMinX);
      bounds.max.x = Math.max(bounds.max.x, PARKING.lotMaxX);
      bounds.max.z = Math.max(bounds.max.z, PARKING.slot2MaxZ + 0.45);
    }
    const baseScale = Math.min((width - 44) / Math.max(0.5, bounds.max.x - bounds.min.x), (height - 55) / Math.max(0.5, bounds.max.z - bounds.min.z));
    const scale = zoom * baseScale;
    const originX = width / 2 - (bounds.min.x + bounds.max.x) * scale / 2 + panX;
    const originY = height / 2 - (bounds.min.z + bounds.max.z) * scale / 2 + panY;
    transform = { originX, originY, scale };
    const x = (n) => originX + n * scale;
    const y = (n) => originY + n * scale;
    const theme = getComputedStyle(canvas);
    const color = (token) => theme.getPropertyValue(token).trim();

    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.fillStyle = color('--well');
    context.fillRect(0, 0, width, height);

    context.strokeStyle = color('--plan-grid');
    context.lineWidth = 0.75;
    context.beginPath();
    const grid = (scale < 11 ? 2 : 1) * scale;
    for (let gx = ((originX % grid) + grid) % grid; gx < width; gx += grid) { context.moveTo(gx, 0); context.lineTo(gx, height); }
    for (let gy = ((originY % grid) + grid) % grid; gy < height; gy += grid) { context.moveTo(0, gy); context.lineTo(width, gy); }
    context.stroke();

    // Demarcação do recuo frontal, Vaga 1 (garagem ARQ01) e Vaga 2 (lateral sala) no pavimento térreo.
    if (floor === 'terreo' && showParkingGuides) {
      context.save();
      // Faixa frontal do lote até a via interna (6,35 x 2,50 m).
      context.fillStyle = 'rgba(155, 213, 185, 0.04)';
      context.fillRect(
        x(PARKING.lotMinX), y(PARKING.frontMinZ),
        (PARKING.lotMaxX - PARKING.lotMinX) * scale, (PARKING.frontMaxZ - PARKING.frontMinZ) * scale,
      );
      context.strokeStyle = 'rgba(205, 219, 212, 0.35)';
      context.lineWidth = 1;
      context.setLineDash([5, 4]);
      context.strokeRect(
        x(PARKING.lotMinX), y(PARKING.frontMinZ),
        (PARKING.lotMaxX - PARKING.lotMinX) * scale, (PARKING.frontMaxZ - PARKING.frontMinZ) * scale,
      );

      // Vão da garagem coberta (2,85 x 3,20 m).
      context.strokeStyle = 'rgba(155, 213, 185, 0.45)';
      context.setLineDash([3, 3]);
      context.strokeRect(
        x(PARKING.garageMinX), y(PARKING.garageMinZ),
        (PARKING.garageMaxX - PARKING.garageMinX) * scale, (PARKING.overhangZ - PARKING.garageMinZ) * scale,
      );

      // Vaga 1 oficial 2,20 x 4,50 m (parte coberta 3,20 m + descoberta 1,30 m).
      const slot1W = (PARKING.slot1MaxX - PARKING.slot1MinX) * scale;
      context.fillStyle = 'rgba(122, 205, 166, 0.17)';
      context.fillRect(x(PARKING.slot1MinX), y(PARKING.slot1MinZ), slot1W, (PARKING.overhangZ - PARKING.slot1MinZ) * scale);
      context.fillStyle = 'rgba(246, 201, 108, 0.17)';
      context.fillRect(x(PARKING.slot1MinX), y(PARKING.overhangZ), slot1W, (PARKING.slot1MaxZ - PARKING.overhangZ) * scale);
      context.strokeStyle = '#8ad4b0';
      context.lineWidth = 1.4;
      context.setLineDash([6, 3]);
      context.strokeRect(
        x(PARKING.slot1MinX), y(PARKING.slot1MinZ),
        slot1W, (PARKING.slot1MaxZ - PARKING.slot1MinZ) * scale,
      );

      // Vaga 2 lateral 2,00 m: 1,20 m sob sacada + 1,30 m recuo lote (2,50 m) + 0,75 m faixa rua (3,25 m) + 0,84 m avanço bico Sandero (4,09 m).
      const slot2W = (PARKING.slot2MaxX - PARKING.slot2MinX) * scale;
      context.fillStyle = 'rgba(122, 205, 166, 0.14)';
      context.fillRect(x(PARKING.slot2MinX), y(PARKING.slot2MinZ), slot2W, (PARKING.overhangZ - PARKING.slot2MinZ) * scale);
      context.fillStyle = 'rgba(246, 201, 108, 0.14)';
      context.fillRect(x(PARKING.slot2MinX), y(PARKING.overhangZ), slot2W, (PARKING.slot2LotMaxZ - PARKING.overhangZ) * scale);
      context.fillStyle = 'rgba(124, 182, 220, 0.14)';
      context.fillRect(x(PARKING.slot2MinX), y(PARKING.slot2LotMaxZ), slot2W, (PARKING.slot2StripeMaxZ - PARKING.slot2LotMaxZ) * scale);
      context.fillStyle = 'rgba(229, 115, 92, 0.20)';
      context.fillRect(x(PARKING.slot2MinX), y(PARKING.slot2StripeMaxZ), slot2W, (PARKING.slot2MaxZ - PARKING.slot2StripeMaxZ) * scale);

      context.strokeStyle = '#9ac8e8';
      context.lineWidth = 1.3;
      context.setLineDash([5, 3]);
      context.strokeRect(
        x(PARKING.slot2MinX), y(PARKING.slot2MinZ),
        slot2W, (PARKING.slot2StripeMaxZ - PARKING.slot2MinZ) * scale,
      );
      context.strokeStyle = '#e8836b';
      context.strokeRect(
        x(PARKING.slot2MinX), y(PARKING.slot2StripeMaxZ),
        slot2W, (PARKING.slot2MaxZ - PARKING.slot2StripeMaxZ) * scale,
      );

      // Linha de projeção do balanço superior (Z = +1,20 m).
      context.strokeStyle = '#f6c96c';
      context.lineWidth = 1.1;
      context.setLineDash([4, 3]);
      context.beginPath();
      context.moveTo(x(PARKING.lotMinX), y(PARKING.overhangZ));
      context.lineTo(x(PARKING.garageMaxX), y(PARKING.overhangZ));
      context.stroke();
      context.restore();
    }

    function stroke(lines, strokeColor, weight) {
      context.strokeStyle = strokeColor;
      context.lineWidth = weight;
      context.beginPath();
      for (let i = 0; i < lines.length; i += 4) {
        context.moveTo(x(lines[i]), y(lines[i + 1]));
        context.lineTo(x(lines[i + 2]), y(lines[i + 3]));
      }
      context.stroke();
    }
    stroke(low, color('--plan-detail'), 0.7);
    stroke(cut, color('--plan-cut'), 1.2);

    // Silhuetas 2D dos 2 carros reais (Carro 1: Corolla Cross 4,46x1,83 m; Carro 2: Chery iCar 3,20x1,67 m).
    if (floor === 'terreo' && showParkingCar) {
      const cars2D = [
        {
          cx: x(PARKING.car1CenterX), cy: y(PARKING.car1CenterZ),
          cw: PARKING.car1Width * scale, cl: PARKING.car1Length * scale,
          fill: 'rgba(116, 162, 198, 0.36)', stroke: '#b9dbf5', label: PARKING.car1Label,
        },
        {
          cx: x(PARKING.car2CenterX), cy: y(PARKING.car2CenterZ),
          cw: PARKING.car2Width * scale, cl: PARKING.car2Length * scale,
          fill: 'rgba(168, 208, 224, 0.34)', stroke: '#d2eaf6', label: PARKING.car2Label,
        },
      ];
      for (const c of cars2D) {
        const r = Math.min(c.cw, c.cl) * 0.18;
        context.save();
        context.translate(c.cx, c.cy);
        context.beginPath();
        context.roundRect(-c.cw / 2, -c.cl / 2, c.cw, c.cl, r);
        context.fillStyle = c.fill;
        context.fill();
        context.strokeStyle = c.stroke;
        context.lineWidth = 1.5;
        context.stroke();
        // Para-brisa dianteiro (+Z = frente/rua) e vidro traseiro (-Z).
        context.fillStyle = 'rgba(20, 34, 46, 0.55)';
        context.fillRect(-c.cw * 0.38, c.cl * 0.08, c.cw * 0.76, c.cl * 0.17);
        context.fillRect(-c.cw * 0.36, -c.cl * 0.32, c.cw * 0.72, c.cl * 0.12);
        // Retrovisores.
        context.fillStyle = c.stroke;
        context.fillRect(-c.cw * 0.56, c.cl * 0.14, c.cw * 0.08, c.cl * 0.05);
        context.fillRect(c.cw * 0.48, c.cl * 0.14, c.cw * 0.08, c.cl * 0.05);
        // Faróis (+Z).
        context.fillStyle = '#ffe9b8';
        context.fillRect(-c.cw * 0.40, c.cl * 0.45, c.cw * 0.18, c.cl * 0.04);
        context.fillRect(c.cw * 0.22, c.cl * 0.45, c.cw * 0.18, c.cl * 0.04);
        if (c.cw > 30) {
          context.fillStyle = '#eef6fc';
          context.font = '600 9px "Segoe UI", system-ui, sans-serif';
          context.textAlign = 'center';
          context.textBaseline = 'middle';
          context.fillText(c.label, 0, -c.cl * 0.06);
        }
        context.restore();
      }
    }

    if (floor === 'terreo' && showParkingGuides) {
      context.save();
      context.font = '600 8.8px "Segoe UI", system-ui, sans-serif';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      const badges = [
        { text: 'Sandero: +1,59 m lote (+0,84 m faixa)', px: x(PARKING.car2CenterX), py: y(PARKING.slot2MaxZ + 0.24), fg: '#f4a593' },
        { text: 'Vaga 1 ARQ01: 2,20 × 4,50 m', px: x(PARKING.car1CenterX), py: y(PARKING.slot1MaxZ + 0.24), fg: '#9bd5b9' },
      ];
      for (const b of badges) {
        const bw = context.measureText(b.text).width + 10;
        context.fillStyle = '#111916d9';
        context.fillRect(b.px - bw / 2, b.py - 8, bw, 16);
        context.fillStyle = b.fg;
        context.fillText(b.text, b.px, b.py);
      }
      context.restore();
    }

    if (labelsToggle?.checked && roomLabels[floor]) {
      context.save();
      context.font = '600 10px "Segoe UI", system-ui, sans-serif';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      for (const room of roomLabels[floor]) {
        const rx = x(room.x);
        const ry = y(room.z);
        const w = context.measureText(room.label).width + 10;
        context.fillStyle = '#111916b8';
        context.fillRect(rx - w / 2, ry - 8, w, 16);
        context.fillStyle = color('--muted');
        context.fillText(room.label, rx, ry);
      }
      context.restore();
    }

    for (const item of furniture) {
      if (emptyHidden || item.floor !== floor) continue;
      const { width: w, depth: d } = item;
      const spec = catalog[item.type] ?? catalog.custom;
      context.save();
      context.translate(x(item.x), y(item.z));
      context.rotate(item.angle);
      context.fillStyle = selected === item ? '#83c7ef4d' : color('--selected');
      context.strokeStyle = selected === item ? '#a6d9fc' : color('--accent');
      context.lineWidth = selected === item ? 2 : 1;
      if (spec.shape === 'round') {
        context.beginPath();
        context.ellipse(0, 0, w * scale / 2, d * scale / 2, 0, 0, Math.PI * 2);
        context.fill();
        context.stroke();
      } else {
        context.fillRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
        context.strokeRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      }
      if (w * scale > 28) {
        context.fillStyle = color('--ink');
        context.font = '10px "Segoe UI", sans-serif';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(item.label ?? spec.name, 0, 0);
      }
      context.restore();
    }

    if (cursor && mode) {
      const w = mode === 'place' ? Number(widthInput.value) || catalog[select.value].width : selected.width;
      const d = mode === 'place' ? Number(depthInput.value) || catalog[select.value].depth : selected.depth;
      context.save();
      context.translate(x(snapCoord(cursor.x)), y(snapCoord(cursor.z)));
      if (mode === 'move') context.rotate(selected.angle);
      context.strokeStyle = '#a6d9fc';
      context.setLineDash([4, 3]);
      context.strokeRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      context.restore();
    }

    // Indicador ao vivo da câmera 3D na planta.
    if (cameraPose) {
      const cx = x(cameraPose.x);
      const cy = y(cameraPose.z);
      const ang = Math.atan2(cameraPose.dz, cameraPose.dx);
      context.save();
      context.translate(cx, cy);
      context.beginPath();
      context.moveTo(0, 0);
      context.arc(0, 0, 26, ang - 0.38, ang + 0.38);
      context.closePath();
      context.fillStyle = '#9bd5b935';
      context.fill();
      context.beginPath();
      context.arc(0, 0, 4.5, 0, Math.PI * 2);
      context.fillStyle = color('--accent');
      context.fill();
      context.strokeStyle = color('--on-accent');
      context.lineWidth = 1.5;
      context.stroke();
      context.restore();
    }

    // Medição 2D (trena na planta).
    if (measurePoints.length) {
      const [a, b] = measurePoints;
      const target = b ?? (measuring ? cursor : null);
      context.save();
      context.fillStyle = '#f6c96c';
      context.strokeStyle = '#f6c96c';
      context.lineWidth = 2;
      if (target) {
        context.setLineDash(b ? [] : [5, 4]);
        context.beginPath();
        context.moveTo(x(a.x), y(a.z));
        context.lineTo(x(target.x), y(target.z));
        context.stroke();
        const dist = Math.hypot(target.x - a.x, target.z - a.z);
        const mx = (x(a.x) + x(target.x)) / 2;
        const my = (y(a.z) + y(target.z)) / 2;
        const text = `${formatMeters.format(dist)} m`;
        context.font = '700 11px Consolas, monospace';
        const tw = context.measureText(text).width + 10;
        context.fillStyle = '#141c19eb';
        context.fillRect(mx - tw / 2, my - 10, tw, 18);
        context.fillStyle = '#f6c96c';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(text, mx, my - 1);
      }
      for (const pt of measurePoints) {
        context.beginPath();
        context.arc(x(pt.x), y(pt.z), 4, 0, Math.PI * 2);
        context.fillStyle = '#f6c96c';
        context.fill();
      }
      context.restore();
    }

    const meters = scale > 86 ? 0.5 : scale < 18 ? 2 : 1;
    context.fillStyle = color('--ink');
    context.fillRect(14, height - 17, meters * scale, 2);
    context.font = '11px monospace';
    context.fillText(`${formatMeters.format(meters)} m`, 14, height - 22);
  }

  function refresh(message, { notify = true } = {}) {
    setControls(message);
    updateModels();
    draw();
    if (notify) onSelectionChange?.(selected);
  }

  function removeItem(item, { silent = false } = {}) {
    if (!item) return false;
    const idx = furniture.indexOf(item);
    if (idx < 0) return false;
    group.remove(item.model);
    disposeModelGeometry(item.model, item.extraMaterials);
    item.material.dispose();
    furniture.splice(idx, 1);
    if (selected === item) {
      selected = null;
      mode = null;
    }
    const saved = writeStudies();
    if (!silent) {
      onFurnitureChange?.();
      refresh(saved ? 'Móvel removido do estudo.' : 'Móvel removido nesta sessão. O navegador não permitiu salvar.');
    }
    return true;
  }

  function applyPoint(rawX, rawZ) {
    if (measuring) {
      const pt = { x: snapCoord(rawX), z: snapCoord(rawZ) };
      if (measurePoints.length >= 2) measurePoints = [pt];
      else measurePoints.push(pt);
      if (measurePoints.length === 2) {
        const dx = measurePoints[1].x - measurePoints[0].x;
        const dz = measurePoints[1].z - measurePoints[0].z;
        const dist = Math.hypot(dx, dz);
        onMeasureUpdate?.({ total: dist, horiz: dist, vert: 0 });
      }
      refresh();
      return;
    }

    const x = mode ? snapCoord(rawX) : rawX;
    const z = mode ? snapCoord(rawZ) : rawZ;
    const { box: bounds } = layers.get(floor) ?? layers.get('terreo');
    if (mode && (x < bounds.min.x || x > bounds.max.x || z < bounds.min.z || z > bounds.max.z)) {
      setControls('Escolha um ponto dentro do enquadramento do pavimento.');
      return;
    }
    let message;
    if (mode === 'place') {
      if (furniture.length >= 80) {
        setControls('Remova um móvel de estudo antes de inserir outro.');
        return;
      }
      const w = THREE.MathUtils.clamp(Number(widthInput.value) || catalog[select.value].width, 0.25, 5);
      const d = THREE.MathUtils.clamp(Number(depthInput.value) || catalog[select.value].depth, 0.25, 5);
      selected = build({ type: select.value, floor, x, z, angle: 0, width: w, depth: d });
      if (!writeStudies()) message = 'Móvel inserido nesta sessão. O navegador não permitiu salvar.';
    } else if (mode === 'move') {
      Object.assign(selected, { x, z });
      if (!writeStudies()) message = 'Posição atualizada nesta sessão. O navegador não permitiu salvar.';
    } else {
      selected = furniture.findLast((item) => {
        if (item.floor !== floor) return false;
        const dx = x - item.x;
        const dz = z - item.z;
        return Math.abs(dx * Math.cos(item.angle) + dz * Math.sin(item.angle)) <= item.width / 2 &&
          Math.abs(-dx * Math.sin(item.angle) + dz * Math.cos(item.angle)) <= item.depth / 2;
      }) ?? null;
    }
    mode = null;
    refresh(message);
  }

  function edit(nextMode) {
    mode = mode === nextMode ? null : nextMode;
    cursor = null;
    refresh(mode ? 'Clique para posicionar, ou use as setas e Enter na planta.' : undefined);
    if (mode) canvas.focus({ preventScroll: true });
  }

  function pointAt(event) {
    const bounds = canvas.getBoundingClientRect();
    const { originX, originY, scale } = transform;
    return { x: (event.clientX - bounds.left - originX) / scale, z: (event.clientY - bounds.top - originY) / scale };
  }

  function syncDimInputs() {
    const spec = catalog[select.value];
    if (!spec) return;
    widthInput.value = spec.width.toFixed(2);
    depthInput.value = spec.depth.toFixed(2);
  }
  select.addEventListener('change', syncDimInputs, { signal });
  syncDimInputs();

  canvas.addEventListener('pointerdown', (event) => {
    if (event.button !== 0 || mode || measuring) return;
    draggingPan = { x: event.clientX, y: event.clientY, startPanX: panX, startPanY: panY };
    movedDuringDrag = false;
  }, { signal });
  canvas.addEventListener('pointermove', (event) => {
    if (draggingPan) {
      const dx = event.clientX - draggingPan.x;
      const dy = event.clientY - draggingPan.y;
      if (Math.hypot(dx, dy) > 4) movedDuringDrag = true;
      if (movedDuringDrag) {
        panX = draggingPan.startPanX + dx;
        panY = draggingPan.startPanY + dy;
        draw();
      }
      return;
    }
    if ((!mode && !measuring) || !transform) return;
    cursor = pointAt(event);
    draw();
  }, { signal });
  window.addEventListener('pointerup', () => { draggingPan = null; }, { signal });
  canvas.addEventListener('click', (event) => {
    if (movedDuringDrag) { movedDuringDrag = false; return; }
    if (!transform) return;
    const { x, z } = pointAt(event);
    applyPoint(x, z);
  }, { signal });
  canvas.addEventListener('wheel', (event) => {
    if (!transform) return;
    event.preventDefault();
    const factor = event.deltaY < 0 ? 1.14 : 1 / 1.14;
    const nextZoom = THREE.MathUtils.clamp(zoom * factor, 0.5, 6);
    if (nextZoom === zoom) return;
    const bounds = canvas.getBoundingClientRect();
    const px = event.clientX - bounds.left - bounds.width / 2;
    const py = event.clientY - bounds.top - bounds.height / 2;
    const ratio = nextZoom / zoom;
    panX = px - (px - panX) * ratio;
    panY = py - (py - panY) * ratio;
    zoom = nextZoom;
    draw();
  }, { passive: false, signal });
  canvas.addEventListener('pointerleave', () => { cursor = null; draw(); }, { signal });
  canvas.addEventListener('keydown', (event) => {
    if (!mode || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter', 'Escape'].includes(event.key)) return;
    event.preventDefault();
    if (event.key === 'Escape') { edit(mode); return; }
    const bounds = (layers.get(floor) ?? layers.get('terreo')).box;
    const center = bounds.getCenter(new THREE.Vector3());
    cursor ??= mode === 'move' ? { x: selected.x, z: selected.z } : { x: center.x, z: center.z };
    if (event.key === 'Enter') { applyPoint(cursor.x, cursor.z); return; }
    const dx = Number(event.key === 'ArrowRight') - Number(event.key === 'ArrowLeft');
    const dz = Number(event.key === 'ArrowDown') - Number(event.key === 'ArrowUp');
    const step = snapToggle.checked ? 0.1 : 0.2;
    cursor.x = THREE.MathUtils.clamp(cursor.x + dx * step, bounds.min.x, bounds.max.x);
    cursor.z = THREE.MathUtils.clamp(cursor.z + dz * step, bounds.min.z, bounds.max.z);
    draw();
  }, { signal });

  function rotateSelected(radians) {
    if (!selected) return;
    selected.angle = (selected.angle + radians) % (2 * Math.PI);
    const saved = writeStudies();
    onFurnitureChange?.();
    refresh(saved ? undefined : 'Rotação atualizada nesta sessão. O navegador não permitiu salvar.');
  }

  place.addEventListener('click', () => edit('place'), { signal });
  move.addEventListener('click', () => edit('move'), { signal });
  rotateFine.addEventListener('click', () => rotateSelected(Math.PI / 12), { signal });
  rotate.addEventListener('click', () => rotateSelected(Math.PI / 4), { signal });
  remove.addEventListener('click', () => removeItem(selected), { signal });
  labelsToggle?.addEventListener('change', draw, { signal });
  exportBtn?.addEventListener('click', () => {
    const data = JSON.stringify({
      variant,
      entries: serializeEntries(),
    }, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sobrado-mobiliario-${variant}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setControls('Estudo de mobiliário exportado em JSON.');
  }, { signal });
  importBtn?.addEventListener('click', () => fileInput?.click(), { signal });
  fileInput?.addEventListener('change', async () => {
    const file = fileInput.files?.[0];
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text());
      const entries = Array.isArray(parsed) ? parsed : parsed?.entries;
      loadEntries(entries);
      writeStudies();
      onFurnitureChange?.();
      refresh(`Estudo importado (${furniture.length} móvel/is).`);
    } catch {
      setControls('Arquivo JSON inválido para estudo de mobiliário.');
    } finally {
      fileInput.value = '';
    }
  }, { signal });

  for (const button of document.querySelectorAll('[data-plan-zoom]')) {
    button.addEventListener('click', () => {
      const factor = Number(button.dataset.planZoom);
      if (factor === 1) { zoom = 1; panX = 0; panY = 0; }
      else zoom = THREE.MathUtils.clamp(zoom * factor, 0.5, 6);
      draw();
    }, { signal });
  }
  const resizeObserver = new ResizeObserver(draw);
  resizeObserver.observe(canvas);

  return {
    setVisible(visible) {
      shown = visible;
      if (!visible) { mode = cursor = null; }
      refresh(undefined, { notify: false });
    },
    setFloor(next, shownIn3D = next) {
      visibleFloor = shownIn3D;
      const nextFloor = next === 'full' ? 'terreo' : (layers.has(next) ? next : 'terreo');
      floorPicker.value = nextFloor;
      if (floor !== nextFloor) {
        floor = nextFloor;
        title.textContent = floorLabels[floor] ?? floor;
        mode = cursor = null;
        zoom = 1;
        panX = 0;
        panY = 0;
        measurePoints = [];
      }
      refresh(undefined, { notify: false });
    },
    setCameraPose(pose) {
      cameraPose = pose;
      if (shown) draw();
    },
    setMeasuring(active) {
      measuring = active;
      if (!active) measurePoints = [];
      refresh(undefined, { notify: false });
    },
    clearMeasure() {
      measurePoints = [];
      refresh(undefined, { notify: false });
    },
    invalidateOutlines() {
      outlines.clear();
      if (shown) draw();
    },
    setParkingOptions({ showGuides, showCar }) {
      showParkingGuides = Boolean(showGuides);
      showParkingCar = Boolean(showCar);
      if (shown) draw();
    },
    setEmptyHidden(hidden) {
      emptyHidden = Boolean(hidden);
      if (emptyHidden) selected = null;
      refresh();
    },
    getCatalog() { return catalog; },
    getItems() { return furniture.slice(); },
    getSnapshot() { return serializeEntries(); },
    restoreSnapshot(entries) {
      loadEntries(entries);
      writeStudies();
      refresh();
    },
    getSelected() { return selected; },
    selectItem(itemOrId) {
      const target = typeof itemOrId === 'string'
        ? furniture.find((i) => i.id === itemOrId) ?? null
        : (furniture.includes(itemOrId) ? itemOrId : null);
      selected = target;
      refresh();
      return selected;
    },
    clearSelection() {
      if (!selected) return;
      selected = null;
      refresh();
    },
    addItem(entry) {
      if (furniture.length >= 80) return null;
      const spec = catalog[entry.type] ?? catalog.custom;
      const f = Object.hasOwn(floorElevation, entry.floor) ? entry.floor : floor;
      const item = build({
        type: Object.hasOwn(catalog, entry.type) ? entry.type : 'custom',
        floor: f,
        x: entry.x,
        z: entry.z,
        angle: entry.angle ?? 0,
        width: entry.width ?? spec.width,
        depth: entry.depth ?? spec.depth,
        color: entry.color ?? spec.color,
        finish: entry.finish ?? null,
        label: entry.label ?? null,
      });
      selected = item;
      writeStudies();
      onFurnitureChange?.();
      refresh();
      return item;
    },
    updateSelected(patch = {}) {
      if (!selected) return null;
      let needsRebuild = false;
      if (patch.type && Object.hasOwn(catalog, patch.type) && patch.type !== selected.type) {
        const nextSpec = catalog[patch.type];
        selected.type = patch.type;
        if (!Number.isFinite(patch.width)) selected.width = nextSpec.width;
        if (!Number.isFinite(patch.depth)) selected.depth = nextSpec.depth;
        if (!Number.isFinite(patch.height)) selected.height = nextSpec.height;
        if (!Number.isFinite(patch.color)) selected.color = nextSpec.color;
        if (patch.label === undefined) selected.label = null;
        needsRebuild = true;
      }
      if (Number.isFinite(patch.width)) { selected.width = THREE.MathUtils.clamp(patch.width, 0.2, 5); needsRebuild = true; }
      if (Number.isFinite(patch.depth)) { selected.depth = THREE.MathUtils.clamp(patch.depth, 0.2, 5); needsRebuild = true; }
      if (Number.isFinite(patch.height)) { selected.height = THREE.MathUtils.clamp(patch.height, 0.02, 3); needsRebuild = true; }
      if (Number.isFinite(patch.color)) { selected.color = patch.color; needsRebuild = true; }
      if (patch.finish !== undefined) selected.finish = patch.finish;
      if (patch.label !== undefined) selected.label = patch.label;
      if (Number.isFinite(patch.x)) selected.x = patch.x;
      if (Number.isFinite(patch.z)) selected.z = patch.z;
      if (Number.isFinite(patch.angle)) selected.angle = patch.angle % (2 * Math.PI);
      if (needsRebuild) rebuildItemMesh(selected);
      writeStudies();
      onFurnitureChange?.();
      refresh();
      return selected;
    },
    rotateSelected,
    duplicateSelected() {
      if (!selected || furniture.length >= 80) return null;
      return this.addItem({
        type: selected.type,
        floor: selected.floor,
        x: selected.x + 0.35,
        z: selected.z + 0.35,
        angle: selected.angle,
        width: selected.width,
        depth: selected.depth,
        color: selected.color,
        finish: selected.finish,
        label: selected.label,
      });
    },
    removeSelected() { return removeItem(selected); },
    removeItemById(id) { return removeItem(furniture.find((i) => i.id === id) ?? null); },
    moveSelectedTo(rawX, rawZ, useSnap = true) {
      if (!selected) return;
      const bounds = layers.get(selected.floor)?.box;
      const nx = useSnap ? Math.round(rawX * 20) / 20 : rawX;
      const nz = useSnap ? Math.round(rawZ * 20) / 20 : rawZ;
      if (bounds) {
        selected.x = THREE.MathUtils.clamp(nx, bounds.min.x + 0.15, bounds.max.x - 0.15);
        selected.z = THREE.MathUtils.clamp(nz, bounds.min.z + 0.15, bounds.max.z - 0.15);
      } else {
        selected.x = nx;
        selected.z = nz;
      }
      writeStudies();
      refresh();
    },
    rearrangeRoom(roomBounds, targetFloor = 'terreo') {
      const items = furniture.filter((i) =>
        i.floor === targetFloor &&
        i.x >= roomBounds.minX && i.x <= roomBounds.maxX &&
        i.z >= roomBounds.minZ && i.z <= roomBounds.maxZ);
      if (!items.length) return 0;
      const cx = (roomBounds.minX + roomBounds.maxX) / 2;
      const cz = (roomBounds.minZ + roomBounds.maxZ) / 2;
      for (const item of items) {
        const dx = item.x - cx;
        const dz = item.z - cz;
        item.x = THREE.MathUtils.clamp(cx - dz * 0.75, roomBounds.minX + 0.35, roomBounds.maxX - 0.35);
        item.z = THREE.MathUtils.clamp(cz + dx * 0.75, roomBounds.minZ + 0.35, roomBounds.maxZ - 0.35);
        item.angle = (item.angle + Math.PI / 2) % (2 * Math.PI);
      }
      writeStudies();
      onFurnitureChange?.();
      refresh();
      return items.length;
    },
    pickInScene3D(raycaster) {
      if (emptyHidden) return null;
      const visibleItems = furniture.filter((item) => item.model.visible);
      if (!visibleItems.length) return null;
      const hit = raycaster.intersectObjects(visibleItems.map((item) => item.model), true)[0];
      if (!hit) return null;
      let obj = hit.object;
      while (obj && obj.parent && !obj.userData?.furnitureId) obj = obj.parent;
      const found = visibleItems.find((item) => item.model === obj || item.id === obj?.userData?.furnitureId) ?? null;
      if (found) {
        selected = found;
        refresh();
      }
      return found;
    },
    pickInScene(raycaster) {
      if (!shown) return;
      if (mode) {
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -(floorElevation[floor] ?? 0));
        const point = raycaster.ray.intersectPlane(plane, new THREE.Vector3());
        if (point) applyPoint(point.x, point.z);
        return;
      }
      const itemsOnFloor = furniture.filter((item) => item.floor === floor);
      const hit = raycaster.intersectObjects(itemsOnFloor.map((item) => item.model), true)[0];
      if (hit) {
        let obj = hit.object;
        while (obj && obj.parent && !obj.userData?.furnitureId) obj = obj.parent;
        selected = itemsOnFloor.find((item) => item.model === obj) ?? null;
        refresh();
      }
    },
    draw,
    dispose() {
      ac.abort();
      resizeObserver.disconnect();
      for (const item of furniture) {
        disposeModelGeometry(item.model, item.extraMaterials);
        item.material.dispose();
      }
      highlight.dispose();
      box.dispose();
      scene.remove(group);
    },
  };
}
