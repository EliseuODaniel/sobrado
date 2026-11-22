import * as THREE from 'three';

// Cotas de piso acabado no sistema de coordenadas das maquetes exportadas.
export const floorElevation = { terreo: 0, superior: 2.7, atico: 6.3 };
const catalog = {
  sofa: { name: 'Sofá', width: 2.1, depth: 0.9, color: 0x778765, parts: [
    [0, 0.17, 0, 2.1, 0.34, 0.9], [0, 0.43, 0.05, 1.8, 0.19, 0.65],
    [0, 0.58, -0.35, 2.1, 0.55, 0.2],
    [-0.97, 0.42, 0, 0.16, 0.48, 0.9], [0.97, 0.42, 0, 0.16, 0.48, 0.9],
  ] },
  table: { name: 'Mesa', width: 1.5, depth: 0.85, color: 0x9d7553, parts: [
    [0, 0.73, 0, 1.5, 0.06, 0.85],
    [-0.65, 0.35, -0.33, 0.07, 0.7, 0.07], [0.65, 0.35, -0.33, 0.07, 0.7, 0.07],
    [-0.65, 0.35, 0.33, 0.07, 0.7, 0.07], [0.65, 0.35, 0.33, 0.07, 0.7, 0.07],
  ] },
  bed: { name: 'Cama', width: 1.58, depth: 1.98, color: 0xb2a384, parts: [
    [0, 0.14, 0, 1.58, 0.28, 1.98], [0, 0.37, 0.04, 1.54, 0.18, 1.87],
    [0, 0.45, -0.94, 1.58, 0.9, 0.1],
    [-0.4, 0.49, -0.66, 0.65, 0.10, 0.36], [0.4, 0.49, -0.66, 0.65, 0.10, 0.36],
  ] },
};
const floorLabels = { terreo: 'Térreo', superior: 'Superior', atico: 'Ático' };
const formatMeters = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });

function sectionLines(node, height) {
  const lines = [];
  const box = new THREE.Box3();
  const corners = Array.from({ length: 3 }, () => new THREE.Vector3());
  const intersections = [new THREE.Vector3(), new THREE.Vector3()];
  node.traverse((mesh) => {
    if (!mesh.isMesh) return;
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

export function createPlan({ layers, scene, variant, requestFrame }) {
  const canvas = document.querySelector('#plan-canvas');
  const context = canvas.getContext('2d');
  const title = document.querySelector('#plan-title');
  const floorPicker = document.querySelector('#plan-floor');
  const select = document.querySelector('#furniture-type');
  const place = document.querySelector('#furniture-place');
  const move = document.querySelector('#furniture-move');
  const rotate = document.querySelector('#furniture-rotate');
  const remove = document.querySelector('#furniture-remove');
  const status = document.querySelector('#furniture-status');
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
  let shown = false;
  let cursor = null;
  let transform = null;

  function build(entry) {
    const spec = catalog[entry.type];
    const model = new THREE.Group();
    const material = new THREE.MeshLambertMaterial({ color: spec.color });
    for (const [x, y, z, w, h, d] of spec.parts) {
      const mesh = new THREE.Mesh(box, material);
      mesh.position.set(x, y, z);
      mesh.scale.set(w, h, d);
      model.add(mesh);
    }
    const item = { ...entry, model, material };
    group.add(model);
    furniture.push(item);
    return item;
  }

  function writeStudies() {
    const entries = furniture.map(({ type, floor, x, z, angle }) => ({ type, floor, x, z, angle }));
    try {
      localStorage.setItem(storageKey, JSON.stringify(entries));
      return true;
    } catch {
      return false;
    }
  }

  try {
    const entries = JSON.parse(localStorage.getItem(storageKey) ?? '[]');
    if (Array.isArray(entries)) {
      for (const entry of entries.slice(0, 80)) {
        const bounds = layers.get(entry?.floor)?.box;
        if (Object.hasOwn(catalog, entry?.type) && Object.hasOwn(floorElevation, entry?.floor) &&
          bounds && [entry.x, entry.z, entry.angle].every(Number.isFinite) &&
          entry.x >= bounds.min.x && entry.x <= bounds.max.x &&
          entry.z >= bounds.min.z && entry.z <= bounds.max.z) build(entry);
      }
    }
  } catch {
    // Uma sessão sem armazenamento ainda permite editar o estudo em memória.
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
    move.disabled = rotate.disabled = remove.disabled = !selected;
    canvas.toggleAttribute('data-editing', Boolean(mode));
    status.textContent = message ?? (selected
      ? `${catalog[selected.type].name} selecionado · ${Math.round(THREE.MathUtils.radToDeg(selected.angle))}°`
      : 'Os móveis de estudo ficam neste navegador.');
  }

  function getOutline() {
    if (!outlines.has(floor)) {
      const { node, box: bounds } = layers.get(floor);
      const elevation = floorElevation[floor];
      outlines.set(floor, {
        bounds,
        low: sectionLines(node, elevation + 0.34),
        cut: sectionLines(node, elevation + 1.07),
      });
    }
    return outlines.get(floor);
  }

  function draw() {
    if (!shown || !canvas.clientWidth || !canvas.clientHeight) return;
    const { clientWidth: width, clientHeight: height } = canvas;
    const ratio = Math.min(window.devicePixelRatio, 2);
    if (canvas.width !== Math.round(width * ratio)) canvas.width = Math.round(width * ratio);
    if (canvas.height !== Math.round(height * ratio)) canvas.height = Math.round(height * ratio);
    const { bounds, low, cut } = getOutline();
    const scale = zoom * Math.min((width - 44) / (bounds.max.x - bounds.min.x), (height - 55) / (bounds.max.z - bounds.min.z));
    const originX = width / 2 - (bounds.min.x + bounds.max.x) * scale / 2;
    const originY = height / 2 - (bounds.min.z + bounds.max.z) * scale / 2;
    transform = { originX, originY, scale };
    const x = (n) => originX + n * scale;
    const y = (n) => originY + n * scale;
    const paper = document.body.dataset.presentation === 'prancha';
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.fillStyle = paper ? '#f0e8d5' : '#f8f8f1';
    context.fillRect(0, 0, width, height);
    context.strokeStyle = paper ? '#e4dac5' : '#e7e8df';
    context.lineWidth = 0.75;
    context.beginPath();
    const grid = (scale < 11 ? 2 : 1) * scale;
    for (let gx = originX % grid; gx < width; gx += grid) { context.moveTo(gx, 0); context.lineTo(gx, height); }
    for (let gy = originY % grid; gy < height; gy += grid) { context.moveTo(0, gy); context.lineTo(width, gy); }
    context.stroke();
    function stroke(lines, color, weight) {
      context.strokeStyle = color;
      context.lineWidth = weight;
      context.beginPath();
      for (let i = 0; i < lines.length; i += 4) {
        context.moveTo(x(lines[i]), y(lines[i + 1]));
        context.lineTo(x(lines[i + 2]), y(lines[i + 3]));
      }
      context.stroke();
    }
    stroke(low, paper ? '#bbb098' : '#aab5a7', 0.7);
    stroke(cut, paper ? '#564e3e' : '#3e524a', 1.15);
    for (const item of furniture) {
      if (item.floor !== floor) continue;
      const { width: w, depth: d } = catalog[item.type];
      context.save();
      context.translate(x(item.x), y(item.z));
      context.rotate(item.angle);
      context.fillStyle = selected === item ? '#9fc4de99' : '#a4ae9399';
      context.strokeStyle = selected === item ? '#286087' : '#56674a';
      context.lineWidth = selected === item ? 2 : 1;
      context.fillRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      context.strokeRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      context.restore();
    }
    if (cursor && mode) {
      const { width: w, depth: d } = catalog[mode === 'place' ? select.value : selected.type];
      context.save();
      context.translate(x(cursor.x), y(cursor.z));
      if (mode === 'move') context.rotate(selected.angle);
      context.strokeStyle = '#286087';
      context.setLineDash([4, 3]);
      context.strokeRect(-w * scale / 2, -d * scale / 2, w * scale, d * scale);
      context.restore();
    }
    const meters = scale > 86 ? 0.5 : scale < 18 ? 2 : 1;
    context.fillStyle = '#534a3c';
    context.fillRect(14, height - 17, meters * scale, 2);
    context.font = '11px monospace';
    context.fillText(`${formatMeters.format(meters)} m`, 14, height - 22);
  }

  function refresh(message) {
    setControls(message);
    updateModels();
    draw();
  }

  function applyPoint(x, z) {
    const { box: bounds } = layers.get(floor);
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
      selected = build({ type: select.value, floor, x, z, angle: 0 });
      if (!writeStudies()) message = 'Móvel inserido nesta sessão. O navegador não permitiu salvar.';
    } else if (mode === 'move') {
      Object.assign(selected, { x, z });
      if (!writeStudies()) message = 'Posição atualizada nesta sessão. O navegador não permitiu salvar.';
    } else {
      selected = furniture.findLast((item) => {
        if (item.floor !== floor) return false;
        const { width, depth } = catalog[item.type];
        const dx = x - item.x;
        const dz = z - item.z;
        return Math.abs(dx * Math.cos(item.angle) + dz * Math.sin(item.angle)) <= width / 2 &&
          Math.abs(-dx * Math.sin(item.angle) + dz * Math.cos(item.angle)) <= depth / 2;
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

  canvas.addEventListener('click', (event) => {
    if (!transform) return;
    const { x, z } = pointAt(event);
    applyPoint(x, z);
  });
  canvas.addEventListener('pointermove', (event) => {
    if (!mode || !transform) return;
    cursor = pointAt(event);
    draw();
  });
  canvas.addEventListener('pointerleave', () => { cursor = null; draw(); });
  canvas.addEventListener('keydown', (event) => {
    if (!mode || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter', 'Escape'].includes(event.key)) return;
    event.preventDefault();
    if (event.key === 'Escape') { edit(mode); return; }
    const bounds = layers.get(floor).box;
    const center = bounds.getCenter(new THREE.Vector3());
    cursor ??= mode === 'move' ? { x: selected.x, z: selected.z } : { x: center.x, z: center.z };
    if (event.key === 'Enter') { applyPoint(cursor.x, cursor.z); return; }
    const dx = Number(event.key === 'ArrowRight') - Number(event.key === 'ArrowLeft');
    const dz = Number(event.key === 'ArrowDown') - Number(event.key === 'ArrowUp');
    cursor.x = THREE.MathUtils.clamp(cursor.x + dx * 0.2, bounds.min.x, bounds.max.x);
    cursor.z = THREE.MathUtils.clamp(cursor.z + dz * 0.2, bounds.min.z, bounds.max.z);
    draw();
  });
  place.addEventListener('click', () => edit('place'));
  move.addEventListener('click', () => edit('move'));
  rotate.addEventListener('click', () => {
    selected.angle = (selected.angle + Math.PI / 4) % (2 * Math.PI);
    const saved = writeStudies();
    refresh(saved ? undefined : 'Rotação atualizada nesta sessão. O navegador não permitiu salvar.');
  });
  remove.addEventListener('click', () => {
    group.remove(selected.model);
    selected.material.dispose();
    furniture.splice(furniture.indexOf(selected), 1);
    selected = mode = null;
    const saved = writeStudies();
    refresh(saved ? 'Móvel removido do estudo.' : 'Móvel removido nesta sessão. O navegador não permitiu salvar.');
  });
  for (const button of document.querySelectorAll('[data-plan-zoom]')) {
    button.addEventListener('click', () => {
      const factor = Number(button.dataset.planZoom);
      zoom = factor === 1 ? 1 : THREE.MathUtils.clamp(zoom * factor, 0.6, 4);
      draw();
    });
  }
  new ResizeObserver(draw).observe(canvas);

  return {
    setVisible(visible) {
      shown = visible;
      if (!visible) { mode = selected = cursor = null; }
      refresh();
    },
    setFloor(next, shownIn3D = next) {
      visibleFloor = shownIn3D;
      const nextFloor = next === 'full' ? 'terreo' : next;
      floorPicker.value = nextFloor;
      if (floor !== nextFloor) {
        floor = nextFloor;
        title.textContent = floorLabels[floor];
        mode = selected = cursor = null;
        zoom = 1;
      }
      refresh();
    },
    pickInScene(raycaster) {
      if (!shown) return;
      if (mode) {
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -floorElevation[floor]);
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
  };
}
