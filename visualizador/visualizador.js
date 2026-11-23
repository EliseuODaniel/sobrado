import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createSheetStyle } from './prancha.js';
import { createPlan, floorElevation } from './planta.js';

const canvas = document.querySelector('#canvas');
const modelSelect = document.querySelector('#model-version');
const parameters = new URLSearchParams(window.location.search);
const variant = ['atico', 'estrutural', 'industrial'].find((id) => id === parameters.get('maquete')) ?? 'atual';
modelSelect.value = variant;
modelSelect.addEventListener('change', () => {
  parameters.set('maquete', modelSelect.value);
  window.location.search = parameters.toString();
});
const viewport = document.querySelector('.viewport');
const roof = document.querySelector('#roof');
const loading = document.querySelector('#loading');
const progress = document.querySelector('#loading-progress');
const title = document.querySelector('#view-title');
const floorButtons = [...document.querySelectorAll('[data-floor]')];
const wallButtons = [...document.querySelectorAll('[data-walls]')];
const networkInputs = [...document.querySelectorAll('[data-network]')];
const navigationButtons = [...document.querySelectorAll('[data-navigation]')];
const presentationButtons = [...document.querySelectorAll('[data-presentation]')];
const arrangementButtons = [...document.querySelectorAll('[data-arrangement][type="button"]')];
const orientationButtons = [...document.querySelectorAll('[data-orientation]')];
const cutEnabled = document.querySelector('#cut-enabled');
const cutHeight = document.querySelector('#cut-height');
const cutValue = document.querySelector('#cut-value');
const planFloorSelect = document.querySelector('#plan-floor');
const overview = document.querySelector('#overview');
const recenter = document.querySelector('#recenter');
const zoomIn = document.querySelector('#zoom-in');
const zoomOut = document.querySelector('#zoom-out');
const movementPad = document.querySelector('#movement-pad');
const movementKeys = {
  w: 'forward', s: 'backward', a: 'left', d: 'right', q: 'down', e: 'up',
  arrowleft: 'lookLeft', arrowright: 'lookRight', arrowup: 'lookUp', arrowdown: 'lookDown',
};

const floorViews = {
  full: { label: 'Vista geral', category: 'Modelo 3D', layers: ['terreo', 'superior', 'atico', 'telhado', 'caixa'], direction: [0.6, 0.53, 1] },
  terreo: { label: 'Térreo', category: 'Pavimento', layers: ['terreo'], direction: [0.4, 1.62, 1] },
  superior: { label: 'Pavimento superior', category: 'Pavimento', layers: ['superior'], direction: [0.4, 1.62, 1] },
  atico: { label: 'Ático', category: 'Pavimento', layers: ['atico'], direction: [0.45, 1.2, 1] },
};
const wallDescriptions = { solid: 'sólidas', glass: 'transparentes', hidden: 'ocultas' };
const orientationDirections = { front: [0, 0.02, 1], side: [1, 0.02, 0], top: [0, 1, 0.0001] };

function prepareGlass(material) {
  if (!material.transmission) return;

  // Vidros finos usam a transparência do quadro principal, com antialiasing.
  // Sem refração em uma imagem reduzida, os caixilhos não são reamostrados
  // dentro de cada vidro enquanto a câmera se move.
  material.opacity = Math.min(material.opacity, THREE.MathUtils.lerp(0.82, 0.15, material.transmission));
  material.transmission = 0;
  material.transparent = true;
  material.depthWrite = false;
  material.forceSinglePass = true;
  material.roughness = Math.max(0.28, material.roughness);
  material.specularIntensity *= 0.55;
  material.needsUpdate = true;
}

function showFailure(message) {
  loading.hidden = false;
  document.querySelector('#loading-title').textContent = 'Não foi possível abrir o modelo';
  document.querySelector('#loading-detail').textContent = message;
  progress.hidden = true;
}

async function start() {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch {
    showFailure('Abra em um navegador com WebGL 2 e aceleração gráfica habilitada.');
    return;
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.shadowMap.autoUpdate = false;

  const scene = new THREE.Scene();
  const environment = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(environment, 0.035).texture;
  scene.environmentIntensity = 0.63;
  environment.dispose();
  pmrem.dispose();

  const sky = new THREE.HemisphereLight(0xfff8e9, 0xb1bac0, 1.5);
  const sun = new THREE.DirectionalLight(0xffead3, 2.05);
  sun.position.set(-9, 17, 9);
  sun.target.position.set(3.2, 1.5, -4);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1536, 1536);
  Object.assign(sun.shadow.camera, { left: -12, right: 12, top: 13, bottom: -13, near: 0.1, far: 42 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.normalBias = 0.025;
  sun.shadow.bias = -0.0002;
  const fill = new THREE.DirectionalLight(0xe3ecff, 0.65);
  fill.position.set(6, 6, -10);
  scene.add(sky, sun, sun.target, fill);

  const perspective = new THREE.PerspectiveCamera(39, 1, 0.025, 145);
  const axonometric = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.025, 145);
  let camera = perspective;
  let aspect = 1;
  let sheetHalfHeight = 1;
  const controls = new OrbitControls(camera, canvas);
  controls.zoomToCursor = true;
  controls.zoomSpeed = 0.9;
  controls.enabled = false;
  controls.enableDamping = true;
  controls.dampingFactor = 0.105;
  controls.minDistance = 0.18;
  controls.maxDistance = 90;
  controls.minZoom = 0.25;
  controls.maxZoom = 16;

  const heldKeys = new Map();
  const heldPointers = new Map();
  let lastMotionAt = null;
  let framePending = false;
  function requestFrame() {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame((now) => {
      framePending = false;
      updateMotion(now);
      if (controls.enabled) controls.update();
      renderer.render(scene, camera);
      if (heldKeys.size || heldPointers.size) requestFrame();
    });
  }
  controls.addEventListener('change', requestFrame);

  let floor = 'full';
  const initialRoof = variant !== 'atico' && variant !== 'estrutural';
  let roofPreferred = initialRoof;
  let wallMode = 'glass';
  let navigation = parameters.get('vista') === 'prancha' ? 'orbit' : 'free';
  let activePreset = null;
  let orientation = 'isometric';
  let modelReady = false;
  let presentation = parameters.get('vista') === 'prancha' ? 'prancha' : 'model';
  let arrangement = ['planta', 'dupla'].find((id) => parameters.get('arranjo') === id) ?? '3d';
  let sheetStyle;
  let plan;
  const cutPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), Number(cutHeight.value));
  const clippingPlanes = [cutPlane];
  const noClippingPlanes = [];
  const cutFormat = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const layers = new Map();
  const presetButtons = new Map();
  const wallGroups = [];
  const wallMeshes = [];
  const wallMaterials = new Map();
  const networks = [];
  const glass = new THREE.MeshPhysicalMaterial({
    color: 0xa4d9df,
    opacity: 0.22,
    transparent: true,
    depthWrite: false,
    roughness: 0.38,
    metalness: 0.10,
    clearcoat: 0.15,
  });

  function usesAxonometry() {
    return presentation === 'prancha' && navigation !== 'free' && !activePreset;
  }

  function updateProjection() {
    if (camera.isOrthographicCamera) {
      camera.left = -sheetHalfHeight * aspect;
      camera.right = sheetHalfHeight * aspect;
      camera.top = sheetHalfHeight;
      camera.bottom = -sheetHalfHeight;
      camera.updateProjectionMatrix();
      return;
    }
    camera.aspect = aspect;
    const fov = activePreset ? THREE.MathUtils.radToDeg(activePreset.fov) : 39;
    const narrow = activePreset
      ? Math.max(1, Math.min(activePreset.aspect, 1.15) / camera.aspect)
      : 1;
    camera.fov = Math.min(92, THREE.MathUtils.radToDeg(
      2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(fov / 2)) * narrow),
    ));
    camera.updateProjectionMatrix();
  }

  function setCamera(position, target) {
    // Descarta movimento residual para repetir a posição da câmera com precisão.
    controls.enableDamping = false;
    controls.update();
    controls.target.copy(target);
    camera.position.copy(position);
    controls.update();
    controls.enableDamping = true;
    requestFrame();
  }

  function frameActiveView() {
    const nextCamera = usesAxonometry() ? axonometric : perspective;
    if (camera !== nextCamera) {
      controls.enableDamping = false;
      controls.update();
      nextCamera.position.copy(camera.position);
      nextCamera.quaternion.copy(camera.quaternion);
      controls.object = camera = nextCamera;
      controls.enableDamping = true;
    }
    document.querySelector('#sheet-projection').textContent =
      camera.isOrthographicCamera ? 'Axonometria' : 'Perspectiva';
    updateProjection();
    if (activePreset) {
      setCamera(new THREE.Vector3(...activePreset.position), new THREE.Vector3(...activePreset.target));
      return;
    }

    const view = floorViews[floor];
    const bounds = new THREE.Box3();
    for (const key of view.layers) {
      const layer = layers.get(key);
      if (layer?.node.visible) bounds.union(layer.box);
    }
    const center = bounds.getCenter(new THREE.Vector3());
    const direction = new THREE.Vector3(...(orientationDirections[orientation] ?? (
      camera.isOrthographicCamera && floor === 'full' ? [0.85, 0.93, 1] : view.direction
    ))).normalize();
    const right = new THREE.Vector3().crossVectors(camera.up, direction).normalize();
    const up = new THREE.Vector3().crossVectors(direction, right);
    const vertical = Math.tan(THREE.MathUtils.degToRad(perspective.fov / 2));
    const fitScale = camera.isOrthographicCamera ? 0.76 : 0.83;
    let distance = 0;
    let halfHeight = 0;
    for (const x of [bounds.min.x, bounds.max.x]) {
      for (const y of [bounds.min.y, bounds.max.y]) {
        for (const z of [bounds.min.z, bounds.max.z]) {
          const corner = new THREE.Vector3(x, y, z).sub(center);
          const fit = Math.max(Math.abs(corner.dot(right)) / aspect, Math.abs(corner.dot(up)));
          halfHeight = Math.max(halfHeight, fit / fitScale);
          distance = Math.max(distance, corner.dot(direction) + fit / (vertical * fitScale));
        }
      }
    }
    if (camera.isOrthographicCamera) {
      sheetHalfHeight = halfHeight;
      camera.zoom = 1;
      updateProjection();
    }
    setCamera(center.clone().addScaledVector(direction, distance), center);
  }

  function updateView() {
    const full = floor === 'full';
    const visibleRoof = layers.has('telhado') && full && roofPreferred;
    for (const [key, { node }] of layers) {
      node.visible = key === 'telhado' ? visibleRoof :
        full || key === floor || key === 'instalacoes' || (floor === 'terreo' && key === 'contexto');
    }
    roof.checked = visibleRoof;
    roof.disabled = !full || !layers.has('telhado');
    for (const button of floorButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.floor === floor));
    }
    for (const [id, button] of presetButtons) {
      button.setAttribute('aria-pressed', String(id === activePreset?.id));
    }
    const glassWalls = wallMode === 'glass';
    for (const group of wallGroups) group.visible = wallMode !== 'hidden';
    for (const { mesh, material, glassMaterial, castShadow } of wallMeshes) {
      wallMaterials.set(mesh, glassWalls ? glassMaterial : material);
      mesh.castShadow = !glassWalls && castShadow;
      mesh.receiveShadow = !glassWalls;
    }
    sheetStyle.apply(presentation === 'prancha', wallMaterials);
    for (const button of wallButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.walls === wallMode));
    }
    for (const input of networkInputs) {
      const matching = networks.filter((node) => node.userData.web_network === input.dataset.network);
      for (const node of matching) node.visible = input.checked && node.userData.web_network_view === floor;
      input.disabled = !matching.some((node) => node.userData.web_network_view === floor);
    }
    const view = floorViews[floor];
    title.textContent = activePreset?.label ?? view.label;
    document.querySelector('#view-category').textContent = activePreset?.section ??
      (full && presentation === 'prancha' ? 'Prancha' : view.category);
    document.querySelector('#view-status').textContent =
      `${title.textContent}. Telhado ${visibleRoof ? 'visível' : 'oculto'}.` +
      (wallGroups.length ? ` Paredes externas ${wallDescriptions[wallMode]}.` : '');
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function selectView(nextFloor, preset = null) {
    floor = nextFloor;
    activePreset = preset;
    orientation = 'isometric';
    const planFloor = floor === 'full' && preset?.section === 'Superior' ? 'superior' : floor;
    plan.setFloor(planFloor, floor);
    const floorBox = layers.get(floor)?.box;
    cutHeight.min = (floorElevation[floor] ?? 0) + 0.15;
    cutHeight.max = floorBox ? Math.ceil(floorBox.max.y * 20) / 20 :
      Math.ceil(Math.max(...[...layers.values()].map(({ box }) => box.max.y)) * 20) / 20;
    cutHeight.value = floorBox ? floorElevation[floor] + 1.1 : 3.8;
    updateCut();
    updateView();
    frameActiveView();
  }

  function updateCut() {
    cutHeight.disabled = !cutEnabled.checked;
    cutPlane.constant = Number(cutHeight.value);
    cutValue.value = cutEnabled.checked ? `${cutFormat.format(cutPlane.constant)} m` : '';
    renderer.clippingPlanes = cutEnabled.checked ? clippingPlanes : noClippingPlanes;
    renderer.shadowMap.enabled = !cutEnabled.checked && presentation !== 'prancha';
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function setArrangement(next) {
    arrangement = next;
    document.querySelector('.view-panes').dataset.arrangement = next;
    document.querySelector('.plan-pane').hidden = next === '3d';
    viewport.hidden = next === 'planta';
    document.querySelector('.cut-controls').hidden = next === 'planta' || !modelReady;
    for (const button of arrangementButtons) {
      button.disabled = !modelReady;
      button.setAttribute('aria-pressed', String(button.dataset.arrangement === next));
    }
    plan?.setVisible(next !== '3d');
    if (next === 'planta') stopMotion();
  }

  function replaceParameter(key, value) {
    if (value) parameters.set(key, value);
    else parameters.delete(key);
    const query = parameters.toString();
    history.replaceState(null, '', `${location.pathname}${query ? `?${query}` : ''}${location.hash}`);
  }

  function setPresentation(nextPresentation) {
    presentation = nextPresentation;
    document.body.dataset.presentation = presentation;
    updateCut();
    for (const button of presentationButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.presentation === presentation));
    }
    if (!modelReady) return;
    if (presentation === 'prancha' && navigation !== 'orbit') setNavigation('orbit');
    updateView();
    frameActiveView();
    plan.draw();
  }

  function buildPresets(presets) {
    const list = document.querySelector('#presets');
    const sections = new Map();
    for (const preset of presets) {
      if (!sections.has(preset.section)) {
        const group = document.createElement('div');
        group.className = 'preset-group';
        const heading = document.createElement('h3');
        heading.textContent = preset.section;
        group.append(heading);
        list.append(group);
        sections.set(preset.section, group);
      }
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'preset-button';
      const arrow = document.createElement('span');
      arrow.setAttribute('aria-hidden', 'true');
      arrow.textContent = '↗';
      button.append(preset.label, arrow);
      button.addEventListener('click', () => {
        if (arrangement === 'planta') {
          setArrangement('dupla');
          replaceParameter('arranjo', 'dupla');
        }
        selectView('full', preset);
        if (viewport.getBoundingClientRect().bottom < 180) viewport.scrollIntoView({ block: 'start' });
      });
      sections.get(preset.section).append(button);
      presetButtons.set(preset.id, button);
    }
  }

  function resize() {
    const { clientWidth, clientHeight } = viewport;
    if (!clientWidth || !clientHeight) return;
    const previousAspect = aspect;
    aspect = clientWidth / clientHeight;
    renderer.setSize(clientWidth, clientHeight, false);
    updateProjection();
    if (modelReady && !activePreset && Math.abs(previousAspect - aspect) > 0.12) {
      frameActiveView();
    }
    requestFrame();
  }
  new ResizeObserver(resize).observe(viewport);
  resize();

  function zoom(factor) {
    if (camera.isOrthographicCamera) {
      camera.zoom = THREE.MathUtils.clamp(camera.zoom / factor, controls.minZoom, controls.maxZoom);
      camera.updateProjectionMatrix();
      requestFrame();
      return;
    }
    const offset = camera.position.clone().sub(controls.target);
    const distance = THREE.MathUtils.clamp(offset.length() * factor, controls.minDistance, controls.maxDistance);
    setCamera(controls.target.clone().add(offset.setLength(distance)), controls.target);
  }

  const heading = new THREE.Vector3();
  const right = new THREE.Vector3();
  const displacement = new THREE.Vector3();
  const screenUp = new THREE.Vector3();
  const attitude = new THREE.Euler(0, 0, 0, 'YXZ');

  function look(yaw, pitch) {
    const distance = controls.getDistance();
    attitude.setFromQuaternion(camera.quaternion);
    attitude.y += yaw;
    attitude.x = THREE.MathUtils.clamp(attitude.x + pitch, -Math.PI / 2 + 0.008, Math.PI / 2 - 0.008);
    attitude.z = 0;
    camera.quaternion.setFromEuler(attitude);
    camera.getWorldDirection(heading);
    controls.target.copy(camera.position).addScaledVector(heading, distance);
    requestFrame();
  }

  function moveCamera(directions, fraction, lookStep) {
    const axis = (positive, negative) => Number(directions.has(positive)) - Number(directions.has(negative));
    const yaw = axis('lookLeft', 'lookRight');
    const pitch = axis('lookUp', 'lookDown');
    if (yaw || pitch) look(yaw * lookStep, pitch * lookStep);
    camera.getWorldDirection(heading);
    if (navigation === 'orbit') heading.y = 0;
    heading.normalize();
    right.crossVectors(heading, camera.up).normalize();
    screenUp.set(0, 1, 0).applyQuaternion(camera.quaternion);
    displacement.copy(heading).multiplyScalar(axis('forward', 'backward'))
      .addScaledVector(right, axis('right', 'left'))
      .addScaledVector(screenUp, axis('up', 'down'));
    const distance = THREE.MathUtils.clamp(controls.getDistance() * 0.07, 0.08, 0.9) * fraction;
    displacement.clampLength(0, 1).multiplyScalar(distance);
    camera.position.add(displacement);
    controls.target.add(displacement);
  }

  function updateMotion(now) {
    if (heldKeys.size === 0 && heldPointers.size === 0) {
      lastMotionAt = null;
      return;
    }
    const elapsed = Math.min(0.05, (now - (lastMotionAt ?? now)) / 1000);
    lastMotionAt = now;
    moveCamera(new Set([...heldKeys.values(), ...heldPointers.values()]), elapsed * 12, elapsed * 1.45);
  }

  function stopMotion() {
    heldKeys.clear();
    heldPointers.clear();
    lastMotionAt = null;
  }

  function beginMotion(direction) {
    moveCamera(new Set([direction]), 1, 0.035);
    requestFrame();
  }

  function setNavigation(mode) {
    navigation = mode;
    stopMotion();
    const free = mode === 'free';
    controls.maxPolarAngle = free ? Math.PI : Math.PI * 0.92;
    if (camera.isOrthographicCamera !== usesAxonometry()) frameActiveView();
    else setCamera(camera.position.clone(), controls.target.clone());
    movementPad.hidden = !free;
    for (const button of navigationButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.navigation === mode));
    }
  }

  let clickStart = null;
  const sceneRay = new THREE.Raycaster();
  const pointerInScene = new THREE.Vector2();
  function focusSurface(x, y) {
    pointerInScene.set(x, y);
    sceneRay.setFromCamera(pointerInScene, camera);
    const surfaces = [];
    scene.traverseVisible((node) => { if (node.isMesh) surfaces.push(node); });
    const hit = sceneRay.intersectObjects(surfaces, false).find(({ point }) =>
      !cutEnabled.checked || cutPlane.distanceToPoint(point) >= 0);
    if (!hit) return;
    if (camera.isOrthographicCamera) {
      camera.zoom = Math.max(camera.zoom, 2);
      camera.updateProjectionMatrix();
    }
    const offset = camera.position.clone().sub(controls.target).setLength(Math.min(3, controls.getDistance()));
    setCamera(hit.point.clone().add(offset), hit.point);
  }
  canvas.addEventListener('dblclick', (event) => {
    if (!modelReady || arrangement === 'dupla') return;
    const rect = canvas.getBoundingClientRect();
    focusSurface(2 * (event.clientX - rect.left) / rect.width - 1, 1 - 2 * (event.clientY - rect.top) / rect.height);
  });
  canvas.addEventListener('pointerdown', (event) => {
    if (event.isPrimary && event.button === 0) canvas.focus({ preventScroll: true });
    if (event.isPrimary && event.button === 0 && arrangement === 'dupla') {
      clickStart = [event.clientX, event.clientY];
    }
  });
  canvas.addEventListener('pointercancel', () => { clickStart = null; });
  canvas.addEventListener('pointermove', (event) => {
    if (event.isPrimary && clickStart &&
        Math.hypot(event.clientX - clickStart[0], event.clientY - clickStart[1]) > 5) clickStart = null;
  });
  canvas.addEventListener('pointerup', (event) => {
    if (!clickStart || !event.isPrimary) return;
    const [x, y] = clickStart;
    clickStart = null;
    if (Math.hypot(event.clientX - x, event.clientY - y) > 5) return;
    const bounds = canvas.getBoundingClientRect();
    pointerInScene.set(2 * (x - bounds.left) / bounds.width - 1, 1 - 2 * (y - bounds.top) / bounds.height);
    sceneRay.setFromCamera(pointerInScene, camera);
    plan?.pickInScene(sceneRay);
  });
  canvas.addEventListener('keydown', (event) => {
    if (!modelReady || event.altKey || event.ctrlKey || event.metaKey) return;
    const key = event.key.toLowerCase();
    if (key === 'f') { event.preventDefault(); if (!event.repeat) focusSurface(0, 0); return; }
    const direction = movementKeys[key];
    if (!direction) return;
    event.preventDefault();
    if (heldKeys.has(key)) return;
    heldKeys.set(key, direction);
    beginMotion(direction);
  });
  window.addEventListener('keyup', (event) => heldKeys.delete(event.key.toLowerCase()));
  canvas.addEventListener('blur', () => heldKeys.clear());
  window.addEventListener('blur', stopMotion);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopMotion(); });
  for (const button of movementPad.querySelectorAll('[data-move]')) {
    button.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;
      event.preventDefault();
      button.setPointerCapture(event.pointerId);
      heldPointers.set(event.pointerId, button.dataset.move);
      beginMotion(button.dataset.move);
    });
    button.addEventListener('lostpointercapture', (event) => heldPointers.delete(event.pointerId));
    button.addEventListener('click', (event) => {
      if (event.detail === 0) beginMotion(button.dataset.move);
    });
  }
  for (const button of navigationButtons) {
    button.addEventListener('click', () => {
      setNavigation(button.dataset.navigation);
      canvas.focus({ preventScroll: true });
    });
  }

  setPresentation(presentation);
  for (const button of arrangementButtons) {
    button.disabled = true;
    button.addEventListener('click', () => {
      setArrangement(button.dataset.arrangement);
      replaceParameter('arranjo', arrangement === '3d' ? null : arrangement);
    });
  }
  cutEnabled.addEventListener('change', updateCut);
  cutHeight.addEventListener('input', updateCut);
  planFloorSelect.addEventListener('change', () => selectView(planFloorSelect.value));
  for (const button of orientationButtons) {
    button.disabled = true;
    button.addEventListener('click', () => {
      activePreset = null;
      orientation = button.dataset.orientation;
      updateView();
      frameActiveView();
    });
  }
  for (const button of presentationButtons) {
    button.addEventListener('click', () => {
      const next = button.dataset.presentation;
      if (next === presentation) return;
      replaceParameter('vista', next === 'prancha' ? next : null);
      setPresentation(next);
    });
  }

  try {
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    const model = await loader.loadAsync(`./modelo/casa-${variant}.glb`, (event) => {
      if (event.lengthComputable) progress.value = 100 * event.loaded / event.total;
      if (event.lengthComputable && event.loaded === event.total) {
        document.querySelector('#loading-title').textContent = 'Preparando a cena 3D';
      }
    });
    const root = model.scene.children.find((node) => node.userData.sobrado);
    if (!root) throw new Error('Metadados da cena ausentes.');
    const metadata = JSON.parse(root.userData.sobrado);
    scene.add(root);
    root.updateWorldMatrix(true, true);
    for (const node of root.children) {
      if (node.userData.web_layer) {
        const box = new THREE.Box3().setFromObject(node, true);
        if (!box.isEmpty()) layers.set(node.userData.web_layer, { node, box });
      }
    }
    for (const key of ['terreo', 'superior']) {
      if (!layers.has(key)) throw new Error(`Camada ausente: ${key}`);
    }
    if (!layers.has('atico')) planFloorSelect.querySelector('[value="atico"]').remove();
    root.traverse((node) => {
      if (node.userData.web_exterior_walls) wallGroups.push(node);
      if (node.userData.web_network) networks.push(node);
      if (!node.isMesh) return;
      node.receiveShadow = true;
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      materials.forEach(prepareGlass);
      node.castShadow = materials.every((material) => !material.transparent);
    });
    sheetStyle = createSheetStyle(root);
    plan = createPlan({ layers, scene, variant, requestFrame });
    const solidMaterials = new Map();
    function solidMaterial(material) {
      if (!solidMaterials.has(material)) {
        const solid = material.clone();
        solid.opacity = 1;
        solid.transparent = false;
        solid.depthWrite = true;
        solidMaterials.set(material, solid);
      }
      return solidMaterials.get(material);
    }
    for (const group of wallGroups) {
      group.traverse((mesh) => {
        if (!mesh.isMesh) return;
        const material = mesh.material;
        if (variant === 'estrutural') {
          const solid = Array.isArray(material) ? material.map(solidMaterial) : solidMaterial(material);
          wallMeshes.push({ mesh, material: solid, glassMaterial: material, castShadow: true });
        } else {
          wallMeshes.push({ mesh, material, glassMaterial: glass, castShadow: mesh.castShadow });
        }
      });
    }
    document.querySelector('#wall-controls').hidden = !wallMeshes.length;
    document.querySelector('#network-controls').hidden = !networks.length;
    for (const input of networkInputs) input.addEventListener('change', updateView);

    document.querySelector('#version').textContent = metadata.version;
    document.querySelector('.cameras').hidden = !metadata.presets.length;
    document.querySelector('.roof-toggle').hidden = !layers.has('telhado');
    buildPresets(metadata.presets);
    for (const button of floorButtons) {
      if (button.dataset.floor === 'atico') button.hidden = !layers.has('atico');
      button.disabled = false;
      button.addEventListener('click', () => selectView(button.dataset.floor));
    }
    overview.addEventListener('click', () => {
      roofPreferred = initialRoof;
      wallMode = 'glass';
      cutEnabled.checked = false;
      selectView('full');
    });
    roof.addEventListener('change', () => {
      roofPreferred = roof.checked;
      updateView();
    });
    for (const button of wallButtons) {
      button.addEventListener('click', () => {
        wallMode = button.dataset.walls;
        updateView();
      });
    }
    recenter.addEventListener('click', frameActiveView);
    zoomIn.addEventListener('click', () => zoom(0.83));
    zoomOut.addEventListener('click', () => zoom(1 / 0.83));
    for (const button of [overview, recenter, zoomIn, zoomOut, ...navigationButtons, ...orientationButtons]) button.disabled = false;
    modelReady = true;
    controls.enabled = true;
    for (const button of document.querySelectorAll('[data-turn]')) {
      button.disabled = false;
      button.addEventListener('click', () => moveCamera(new Set([button.dataset.turn]), 0, 0.16));
    }
    selectView('full');
    setNavigation(navigation);
    loading.hidden = true;
    setArrangement(arrangement);
  } catch (error) {
    console.error(error);
    showFailure(`Confira se a exportação em modelo/casa-${variant}.glb está disponível e recarregue a página.`);
  }
}

start().catch((error) => {
  console.error(error);
  showFailure('Confira se a aceleração gráfica está habilitada e tente recarregar a página.');
});
