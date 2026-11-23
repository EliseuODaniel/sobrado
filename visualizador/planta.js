import * as THREE from 'three';

// Cotas de piso acabado no sistema de coordenadas das maquetes exportadas (glTF Y = Blender Z).
export const floorElevation = { terreo: 0, superior: 2.7, atico: 5.45 };

const catalog = {
  sofa: { name: 'Sofá', width: 2.1, depth: 0.9, height: 0.85, color: 0x778765, parts: [
    [0, 0.17, 0, 1, 0.34, 1], [0, 0.43, 0.05, 0.86, 0.19, 0.72],
    [0, 0.58, -0.39, 1, 0.55, 0.22],
    [-0.46, 0.42, 0, 0.08, 0.48, 1], [0.46, 0.42, 0, 0.08, 0.48, 1],
  ] },
  table: { name: 'Mesa', width: 1.5, depth: 0.85, height: 0.76, color: 0x9d7553, parts: [
    [0, 0.73, 0, 1, 0.06, 1],
    [-0.43, 0.35, -0.39, 0.05, 0.7, 0.08], [0.43, 0.35, -0.39, 0.05, 0.7, 0.08],
    [-0.43, 0.35, 0.39, 0.05, 0.7, 0.08], [0.43, 0.35, 0.39, 0.05, 0.7, 0.08],
  ] },
  bed: { name: 'Cama casal', width: 1.58, depth: 1.98, height: 0.9, color: 0xb2a384, parts: [
    [0, 0.14, 0, 1, 0.28, 1], [0, 0.37, 0.02, 0.97, 0.18, 0.94],
    [0, 0.45, -0.47, 1, 0.9, 0.06],
    [-0.25, 0.49, -0.33, 0.41, 0.10, 0.18], [0.25, 0.49, -0.33, 0.41, 0.10, 0.18],
  ] },
  single_bed: { name: 'Cama solteiro', width: 0.9, depth: 1.9, height: 0.85, color: 0xc2b8a3, parts: [
    [0, 0.14, 0, 1, 0.28, 1], [0, 0.36, 0.02, 0.96, 0.18, 0.94],
    [0, 0.42, -0.47, 1, 0.84, 0.06], [0, 0.48, -0.33, 0.68, 0.10, 0.18],
  ] },
  desk: { name: 'Escrivaninha', width: 1.4, depth: 0.65, height: 0.75, color: 0xb89668, parts: [
    [0, 0.73, 0, 1, 0.05, 1],
    [-0.47, 0.36, 0, 0.05, 0.72, 0.94], [0.47, 0.36, 0, 0.05, 0.72, 0.94],
  ] },
  armchair: { name: 'Poltrona', width: 0.85, depth: 0.85, height: 0.82, color: 0x8a7965, parts: [
    [0, 0.2, 0, 0.95, 0.4, 0.95], [0, 0.54, -0.38, 0.95, 0.56, 0.22],
    [-0.43, 0.42, 0, 0.14, 0.45, 0.95], [0.43, 0.42, 0, 0.14, 0.45, 0.95],
  ] },
  wardrobe: { name: 'Armário', width: 1.6, depth: 0.6, height: 2.2, color: 0xd0cbbd, parts: [
    [0, 1.1, 0, 1, 2.2, 1],
  ] },
  fridge: { name: 'Geladeira', width: 0.7, depth: 0.7, height: 1.78, color: 0xadb8bd, parts: [
    [0, 0.89, 0, 1, 1.78, 1],
  ] },
  custom: { name: 'Móvel', width: 1.2, depth: 0.6, height: 0.8, color: 0x7aa695, parts: [
    [0, 0.4, 0, 1, 0.8, 1],
  ] },
};

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

export function createPlan({ layers, scene, variant, requestFrame, onMeasureUpdate }) {
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
  const highlight = new THREE.MeshLambertMaterial({ color: 0x3574a5 });
  const box = new THREE.BoxGeometry();
  const storageKey = `sobrado.estudo-mobiliario.${variant}`;
  scene.add(group);

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

  function itemDimensions(entry) {
    const spec = catalog[entry.type] ?? catalog.custom;
    const width = Number.isFinite(entry.width) && entry.width >= 0.2 ? entry.width : spec.width;
    const depth = Number.isFinite(entry.depth) && entry.depth >= 0.2 ? entry.depth : spec.depth;
    return { width, depth, spec };
  }

  function build(entry) {
    const { width, depth, spec } = itemDimensions(entry);
    const model = new THREE.Group();
    const material = new THREE.MeshLambertMaterial({ color: spec.color });
    for (const [rx, y, rz, rw, h, rd] of spec.parts) {
      const mesh = new THREE.Mesh(box, material);
      mesh.position.set(rx * width, y, rz * depth);
      mesh.scale.set(rw * width, h, rd * depth);
      model.add(mesh);
    }
    const item = { ...entry, width, depth, model, material };
    group.add(model);
    furniture.push(item);
    return item;
  }

  function writeStudies() {
    const entries = furniture.map(({ type, floor: f, x, z, angle, width, depth }) => ({
      type, floor: f, x, z, angle, width, depth,
    }));
    try {
      localStorage.setItem(storageKey, JSON.stringify(entries));
      return true;
    } catch {
      return false;
    }
  }

  function loadEntries(entries) {
    for (const item of furniture) {
      group.remove(item.model);
      item.material.dispose();
    }
    furniture.length = 0;
    selected = null;
    if (!Array.isArray(entries)) return;
    for (const entry of entries.slice(0, 80)) {
      const bounds = layers.get(entry?.floor)?.box;
      if (Object.hasOwn(catalog, entry?.type) && Object.hasOwn(floorElevation, entry?.floor) &&
        bounds && [entry.x, entry.z, entry.angle].every(Number.isFinite) &&
        entry.x >= bounds.min.x && entry.x <= bounds.max.x &&
        entry.z >= bounds.min.z && entry.z <= bounds.max.z) {
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
      item.model.visible = visibleFloor === 'full' || visibleFloor === item.floor;
      for (const mesh of item.model.children) mesh.material = selected === item ? highlight : item.material;
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
      if (item.floor !== floor) continue;
      const { width: w, depth: d } = item;
      context.save();
      context.translate(x(item.x), y(item.z));
      context.rotate(item.angle);
      context.fillStyle = selected === item ? '#83c7ef4d' : color('--selected');
      context.strokeStyle = selected === item ? '#a6d9fc' : color('--accent');
      context.lineWidth = selected === item ? 2 : 1;
      context.fillRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      context.strokeRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      if (w * scale > 28) {
        context.fillStyle = color('--ink');
        context.font = '10px "Segoe UI", sans-serif';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(catalog[item.type].name, 0, 0);
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

  function refresh(message) {
    setControls(message);
    updateModels();
    draw();
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
    refresh(saved ? undefined : 'Rotação atualizada nesta sessão. O navegador não permitiu salvar.');
  }

  place.addEventListener('click', () => edit('place'), { signal });
  move.addEventListener('click', () => edit('move'), { signal });
  rotateFine.addEventListener('click', () => rotateSelected(Math.PI / 12), { signal });
  rotate.addEventListener('click', () => rotateSelected(Math.PI / 4), { signal });
  remove.addEventListener('click', () => {
    if (!selected) return;
    group.remove(selected.model);
    selected.material.dispose();
    furniture.splice(furniture.indexOf(selected), 1);
    selected = mode = null;
    const saved = writeStudies();
    refresh(saved ? 'Móvel removido do estudo.' : 'Móvel removido nesta sessão. O navegador não permitiu salvar.');
  }, { signal });
  labelsToggle?.addEventListener('change', draw, { signal });
  exportBtn?.addEventListener('click', () => {
    const data = JSON.stringify({
      variant,
      entries: furniture.map(({ type, floor: f, x, z, angle, width, depth }) => ({
        type, floor: f, x, z, angle, width, depth,
      })),
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
      if (!visible) { mode = selected = cursor = null; }
      refresh();
    },
    setFloor(next, shownIn3D = next) {
      visibleFloor = shownIn3D;
      const nextFloor = next === 'full' ? 'terreo' : (layers.has(next) ? next : 'terreo');
      floorPicker.value = nextFloor;
      if (floor !== nextFloor) {
        floor = nextFloor;
        title.textContent = floorLabels[floor] ?? floor;
        mode = selected = cursor = null;
        zoom = 1;
        panX = 0;
        panY = 0;
        measurePoints = [];
      }
      refresh();
    },
    setCameraPose(pose) {
      cameraPose = pose;
      if (shown) draw();
    },
    setMeasuring(active) {
      measuring = active;
      if (!active) measurePoints = [];
      refresh();
    },
    clearMeasure() {
      measurePoints = [];
      refresh();
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
        selected = itemsOnFloor.find((item) => item.model === hit.object.parent);
        refresh();
      }
    },
    draw,
    dispose() {
      ac.abort();
      resizeObserver.disconnect();
      for (const item of furniture) item.material.dispose();
      highlight.dispose();
      box.dispose();
      scene.remove(group);
    },
  };
}
