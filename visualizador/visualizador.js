import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createSheetStyle } from './prancha.js?v=20261124v13';
import { createPlan, floorElevation } from './planta.js?v=20261124v13';
import { createPersonalizer } from './personalizador.js?v=20261124v13';
import { createFilmStudio } from './filme.js?v=20261124v13';

const ASSET_VERSION = '20261124v13';

const canvas = document.querySelector('#canvas');
const modelSelect = document.querySelector('#model-version');
const exportPng = document.querySelector('#export-png');
const copyLink = document.querySelector('#copy-link');
const parameters = new URLSearchParams(window.location.search);
const validVariants = ['atual', 'atico', 'estrutural', 'industrial'];
const variantLabels = { atual: 'Casa atual', atico: 'Ático', estrutural: 'Estrutural', industrial: 'Industrial' };
let variant = validVariants.find((id) => id === parameters.get('maquete')) ?? 'atual';
modelSelect.value = variant;

const viewport = document.querySelector('.viewport');
const roof = document.querySelector('#roof');
const ceilingWrap = document.querySelector('#ceiling-toggle-wrap');
const ceilingLights = document.querySelector('#ceiling-lights');
const loading = document.querySelector('#loading');
const progress = document.querySelector('#loading-progress');
const title = document.querySelector('#view-title');
const floorButtons = [...document.querySelectorAll('[data-floor]')];
const wallButtons = [...document.querySelectorAll('[data-walls]')];
const networkInputs = [...document.querySelectorAll('[data-network]')];
const networkToggleAll = document.querySelector('#network-toggle-all');
const netDocInput = document.querySelector('#net-documental');
const netPropInput = document.querySelector('#net-proposed');
const netHighlightProp = document.querySelector('#net-highlight-proposed');
const navigationButtons = [...document.querySelectorAll('[data-navigation]')];
const presentationButtons = [...document.querySelectorAll('[data-presentation]')];
const arrangementButtons = [...document.querySelectorAll('[data-arrangement][type="button"]')];
const orientationButtons = [...document.querySelectorAll('[data-orientation]')];
const lightingButtons = [...document.querySelectorAll('[data-lighting]')];
const walkButton = document.querySelector('#view-mode-walk');
const clayButton = document.querySelector('#studio-mode-clay');
const filmButton = document.querySelector('#studio-mode-film');
const toneMappingButton = document.querySelector('#tone-mapping-toggle');
const sceneXrayEl = document.querySelector('#studio-scene-xray');
const studioActionControls = [
  walkButton,
  clayButton,
  filmButton,
  document.querySelector('#studio-mode-renovate'),
  document.querySelector('#studio-mode-empty'),
  document.querySelector('#studio-mode-photo'),
  document.querySelector('#studio-style-select'),
  document.querySelector('#studio-list-toggle'),
].filter(Boolean);
const sunControl = document.querySelector('#sun-control');
const sunAngle = document.querySelector('#sun-angle');
const measureToggle = document.querySelector('#measure-toggle');
const measureReadout = document.querySelector('#measure-readout');
const measureClear = document.querySelector('#measure-clear');
const cutEnabled = document.querySelector('#cut-enabled');
const cutHeight = document.querySelector('#cut-height');
const cutValue = document.querySelector('#cut-value');
const planFloorSelect = document.querySelector('#plan-floor');
const overview = document.querySelector('#overview');
const recenter = document.querySelector('#recenter');
const zoomIn = document.querySelector('#zoom-in');
const zoomOut = document.querySelector('#zoom-out');
const movementPad = document.querySelector('#movement-pad');
const roomVariantControls = document.querySelector('#room-variant-controls');
const roomVariantOptions = document.querySelector('#room-variant-options');
const atticGuidesControls = document.querySelector('#attic-guides-controls');
const atticGuidesInput = document.querySelector('#attic-guides');
const atticClearancesList = document.querySelector('#attic-clearances');
const parkingGuidesInput = document.querySelector('#parking-guides');
const parkingCarInput = document.querySelector('#parking-car');
const parkingSpecsList = document.querySelector('#parking-specs');
const inspectCard = document.querySelector('#inspect-card');
const inspectTitle = document.querySelector('#inspect-title');
const inspectBody = document.querySelector('#inspect-body');
const inspectClose = document.querySelector('#inspect-close');
const toastEl = document.querySelector('#toast');
const sheetLegendList = document.querySelector('#sheet-legend-list');

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
const networkSystemLabels = {
  electric: 'Elétrica / Eletroduto',
  cold: 'Água fria',
  hot: 'Água quente',
  overflow: 'Extravasor',
  drain: 'Limpeza da caixa',
};
const networkLegendEntries = [
  { label: 'Edificação', color: '#918b7b' },
  { label: 'Elétrica', color: '#ee650f' },
  { label: 'Água fria', color: '#3f77e7' },
  { label: 'Água quente', color: '#d92d35' },
  { label: 'Extravasor', color: '#1d9a98' },
  { label: 'Limpeza', color: '#bd3293' },
];
const defaultLegendEntries = [
  { label: 'Edificação', color: '#918b7b' },
  { label: 'Cobertura', color: '#ae8753' },
  { label: 'Transparências', color: '#739c8e' },
];

function prepareGlass(material) {
  if (!material.transmission) return;
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

let toastTimer = null;
function showToast(message) {
  toastEl.textContent = message;
  toastEl.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastEl.hidden = true; }, 2200);
}

function disposeObjectTree(object) {
  if (!object) return;
  object.traverse((node) => {
    if (node.geometry) node.geometry.dispose();
    if (node.material) {
      const mats = Array.isArray(node.material) ? node.material : [node.material];
      for (const m of mats) {
        for (const value of Object.values(m)) {
          if (value?.isTexture) value.dispose();
        }
        m.dispose();
      }
    }
  });
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

  // Luzes quentes internas ativadas no modo Noite.
  const nightLightsGroup = new THREE.Group();
  const interiorPoints = [
    [1.65, 2.25, -1.8, 3.8],
    [1.65, 2.25, -4.5, 4.2],
    [1.65, 2.35, -8.5, 4.0],
    [4.9, 2.25, -5.6, 3.5],
    [1.7, 4.95, -1.2, 3.6],
    [4.85, 4.95, -0.5, 3.2],
    [4.85, 4.95, -5.6, 3.2],
  ];
  for (const [lx, ly, lz, intensity] of interiorPoints) {
    const pt = new THREE.PointLight(0xffcf94, intensity, 8.5, 1.6);
    pt.position.set(lx, ly, lz);
    nightLightsGroup.add(pt);
  }
  nightLightsGroup.visible = false;
  scene.add(nightLightsGroup);

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
  const camDir = new THREE.Vector3();

  function requestFrame() {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame((now) => {
      framePending = false;
      updateMotion(now);
      if (controls.enabled) controls.update();
      renderer.render(scene, camera);
      if (plan && arrangement !== '3d') {
        camera.getWorldDirection(camDir);
        plan.setCameraPose({ x: camera.position.x, z: camera.position.z, dx: camDir.x, dz: camDir.z });
      }
      if (heldKeys.size || heldPointers.size) requestFrame();
    });
  }
  controls.addEventListener('change', requestFrame);

  let floor = ['full', 'terreo', 'superior', 'atico'].includes(parameters.get('piso')) ? parameters.get('piso') : 'full';
  let initialRoof = variant !== 'atico' && variant !== 'estrutural';
  let roofPreferred = initialRoof;
  let wallMode = ['solid', 'glass', 'hidden'].includes(parameters.get('paredes')) ? parameters.get('paredes') : 'glass';
  let navigation = parameters.get('vista') === 'prancha' ? 'orbit' : 'free';
  let lightingMode = ['day', 'dusk', 'night'].includes(parameters.get('luz')) ? parameters.get('luz') : 'day';
  let toneMappingMode = 'agx'; // 'agx' | 'neutral' (Khronos PBR Neutral)
  let studioLightFactor = 1.0;
  let studio = null;
  let film = null;
  let activePreset = null;
  let orientation = 'isometric';
  let modelReady = false;
  let presentation = parameters.get('vista') === 'prancha' ? 'prancha' : 'model';
  let arrangement = ['planta', 'dupla'].find((id) => parameters.get('arranjo') === id) ?? '3d';
  let activeRoomVariant = 'quarto';
  let currentRoot = null;
  let currentMeta = null;
  let sheetStyle = null;
  let plan = null;
  let atticGuidesGroup = null;
  let loadSeq = 0;

  if (parameters.get('sol') && Number.isFinite(Number(parameters.get('sol')))) {
    sunAngle.value = String(THREE.MathUtils.clamp(Number(parameters.get('sol')), 0, 360));
  }

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
  const networkItems = [];
  const roomVariantGroups = [];
  let inspectedItem = null;

  const glass = new THREE.MeshPhysicalMaterial({
    color: 0xa4d9df,
    opacity: 0.22,
    transparent: true,
    depthWrite: false,
    roughness: 0.38,
    metalness: 0.10,
    clearcoat: 0.15,
  });
  const proposedHighlightMat = new THREE.MeshStandardMaterial({
    color: 0xf6c96c, emissive: 0xd98a1e, emissiveIntensity: 0.55, roughness: 0.4,
  });
  const selectedNetMat = new THREE.MeshStandardMaterial({
    color: 0x8be2ff, emissive: 0x2ba8e0, emissiveIntensity: 0.65, roughness: 0.3,
  });

  // Grupo da trena 3D.
  const measureGroup = new THREE.Group();
  measureGroup.renderOrder = 999;
  scene.add(measureGroup);
  let measuring = false;
  let measurePoints3D = [];

  function updateMeasureReadout(stats) {
    if (!stats) {
      measureReadout.hidden = true;
      measureClear.hidden = true;
      return;
    }
    measureReadout.textContent = stats.vert > 0.01
      ? `d ${cutFormat.format(stats.total)} m · Δxy ${cutFormat.format(stats.horiz)} m · Δh ${cutFormat.format(stats.vert)} m`
      : `d ${cutFormat.format(stats.total)} m`;
    measureReadout.hidden = false;
    measureClear.hidden = false;
  }

  function rebuildMeasure3D() {
    while (measureGroup.children.length) {
      const child = measureGroup.children.pop();
      child.geometry?.dispose();
      child.material?.dispose();
    }
    const dotGeom = new THREE.SphereGeometry(0.045, 14, 14);
    const dotMat = new THREE.MeshBasicMaterial({ color: 0xf6c96c, depthTest: false });
    for (const pt of measurePoints3D) {
      const s = new THREE.Mesh(dotGeom.clone(), dotMat.clone());
      s.position.copy(pt);
      s.renderOrder = 1000;
      measureGroup.add(s);
    }
    dotGeom.dispose();
    dotMat.dispose();
    if (measurePoints3D.length === 2) {
      const [a, b] = measurePoints3D;
      const lineGeom = new THREE.BufferGeometry().setFromPoints([a, b]);
      const lineMat = new THREE.LineBasicMaterial({ color: 0xf6c96c, depthTest: false });
      const line = new THREE.Line(lineGeom, lineMat);
      line.renderOrder = 999;
      measureGroup.add(line);
      const total = a.distanceTo(b);
      const horiz = Math.hypot(b.x - a.x, b.z - a.z);
      const vert = Math.abs(b.y - a.y);
      updateMeasureReadout({ total, horiz, vert });
    }
    requestFrame();
  }

  function clearMeasure() {
    measurePoints3D = [];
    rebuildMeasure3D();
    plan?.clearMeasure();
    updateMeasureReadout(null);
  }

  function setMeasuring(active) {
    measuring = active;
    measureToggle.setAttribute('aria-pressed', String(active));
    canvas.toggleAttribute('data-measuring', active);
    if (!active) clearMeasure();
    plan?.setMeasuring(active);
    if (active) showToast('Trena ativa: clique em dois pontos no 3D ou na planta');
  }

  function applyToneMapping() {
    const isNeutral = toneMappingMode === 'neutral';
    renderer.toneMapping = isNeutral && THREE.NeutralToneMapping
      ? THREE.NeutralToneMapping
      : THREE.AgXToneMapping;
    if (toneMappingButton) {
      toneMappingButton.textContent = isNeutral ? 'PBR Neutral' : 'AgX';
      toneMappingButton.setAttribute('aria-pressed', String(isNeutral));
    }
    requestFrame();
  }

  function applyLighting() {
    document.body.dataset.lighting = lightingMode;
    const isNight = lightingMode === 'night';
    const isDusk = lightingMode === 'dusk';
    const lf = THREE.MathUtils.clamp(studioLightFactor, 0.45, 1.5);
    for (const button of lightingButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.lighting === lightingMode));
    }
    sunControl.hidden = isNight;
    if (isNight) {
      sky.color.setHex(0x283a52);
      sky.groundColor.setHex(0x10151c);
      sky.intensity = 0.48 * lf;
      sun.color.setHex(0x7ca2d6);
      sun.intensity = 0.45 * lf;
      sun.position.set(8, 15, -9);
      fill.intensity = 0.18 * lf;
      scene.environmentIntensity = 0.18 * lf;
      renderer.toneMappingExposure = 1.05 * Math.sqrt(lf);
      nightLightsGroup.visible = true;
      for (const pt of nightLightsGroup.children) pt.intensity = 3.8;
    } else if (isDusk) {
      // Look Crepúsculo / Pôr do sol (Step 7 Nyxera0x: sol baixo quente + céu azulado + luzes internas a meia força)
      const rad = THREE.MathUtils.degToRad(Number(sunAngle.value));
      sky.color.setHex(0x6e8cb8);
      sky.groundColor.setHex(0x2e2933);
      sky.intensity = 0.88 * lf;
      sun.color.setHex(0xff9c54);
      sun.intensity = 2.35 * lf;
      sun.position.set(3.2 + Math.cos(rad) * 18, 5.2, -4 + Math.sin(rad) * 18);
      fill.color.setHex(0x7d9fd1);
      fill.intensity = 0.42 * lf;
      scene.environmentIntensity = 0.38 * lf;
      renderer.toneMappingExposure = 1.10 * Math.sqrt(lf);
      nightLightsGroup.visible = true;
      for (const pt of nightLightsGroup.children) pt.intensity = 2.2;
    } else {
      const rad = THREE.MathUtils.degToRad(Number(sunAngle.value));
      sky.color.setHex(0xfff8e9);
      sky.groundColor.setHex(0xb1bac0);
      sky.intensity = 1.5 * lf;
      sun.color.setHex(0xffead3);
      sun.intensity = 2.05 * lf;
      sun.position.set(3.2 + Math.cos(rad) * 14, 17, -4 + Math.sin(rad) * 14);
      fill.color.setHex(0xe3ecff);
      fill.intensity = 0.65 * lf;
      scene.environmentIntensity = 0.63 * lf;
      renderer.toneMappingExposure = 1.12 * Math.sqrt(lf);
      nightLightsGroup.visible = false;
    }
    applyToneMapping();
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function renderSceneXray(stats) {
    if (!sceneXrayEl) return;
    if (!stats) { sceneXrayEl.innerHTML = ''; return; }
    const fmt = new Intl.NumberFormat('pt-BR');
    const maxStageMeshes = Math.max(1, ...stats.stages.map((s) => s.meshes));
    const stageRows = stats.stages
      .filter((s) => s.meshes > 0)
      .map((s) => {
        const pct = Math.max(6, Math.round((s.meshes / maxStageMeshes) * 100));
        return `
          <div class="xray-stage-row">
            <div class="xray-stage-head">
              <span><i class="xray-dot" style="background:${s.color}"></i>${s.label}</span>
              <small>${s.meshes} peças · ${fmt.format(s.triangles)} tri</small>
            </div>
            <div class="xray-bar"><span style="width:${pct}%;background:${s.color}"></span></div>
          </div>`;
      }).join('');
    const heavyRows = stats.heaviest
      .map((h) => `<li><span>${h.material || h.name}</span><small>${fmt.format(h.triangles)} tri</small></li>`)
      .join('');
    sceneXrayEl.innerHTML = `
      <div class="xray-summary">
        <div><strong>${fmt.format(stats.totalMeshes)}</strong><span>Malhas</span></div>
        <div><strong>${fmt.format(stats.totalTriangles)}</strong><span>Triângulos</span></div>
        <div><strong>${fmt.format(stats.totalMaterials)}</strong><span>Materiais</span></div>
      </div>
      <div class="xray-stages">${stageRows}</div>
      <details class="xray-heavy">
        <summary>Maiores malhas por polígonos (VRAM)</summary>
        <ul>${heavyRows}</ul>
      </details>
    `;
  }

  function updateLegend() {
    const entries = variant === 'estrutural' ? networkLegendEntries : defaultLegendEntries;
    sheetLegendList.innerHTML = '';
    for (const { label, color } of entries) {
      const li = document.createElement('li');
      li.style.setProperty('--swatch', color);
      li.textContent = label;
      sheetLegendList.append(li);
    }
  }

  function clearInspection() {
    if (inspectedItem) {
      inspectedItem = null;
      applyNetworkStyles();
    }
    inspectCard.hidden = true;
  }

  function showInspection(item) {
    inspectedItem = item;
    applyNetworkStyles();
    const u = item.mesh.userData;
    const sys = networkSystemLabels[u.web_net_system] ?? u.web_net_system ?? 'Instalação';
    inspectTitle.textContent = sys;
    const rows = [];
    if (u.web_net_node_a && u.web_net_node_b) rows.push(['Trecho', `${u.web_net_node_a} → ${u.web_net_node_b}`]);
    else if (u.web_net_node) rows.push(['Ponto', u.web_net_node]);
    else rows.push(['Elemento', item.mesh.name]);
    if (u.web_net_diameter_mm) rows.push(['Diâmetro', `Ø ${u.web_net_diameter_mm} mm`]);
    if (u.web_net_kind) rows.push(['Tipo', u.web_net_kind]);
    if (typeof u.web_net_proposed === 'boolean') {
      rows.push(['Status', u.web_net_proposed
        ? '<span class="badge-proposed">Proposto</span>'
        : '<span class="badge-doc">Documental</span>']);
    }
    if (u.web_net_source) rows.push(['Origem', u.web_net_source]);
    inspectBody.innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
    inspectCard.hidden = false;
    requestFrame();
  }

  function updateNetworkToggleAllLabel() {
    if (!networkToggleAll) return;
    const activeInputs = networkInputs.filter((input) => !input.disabled);
    const anyChecked = activeInputs.some((input) => input.checked);
    networkToggleAll.textContent = anyChecked ? 'Desmarcar todos' : 'Marcar todos';
    networkToggleAll.disabled = !activeInputs.length;
  }

  function applyNetworkStyles() {
    const showDoc = netDocInput.checked;
    const showProp = netPropInput.checked;
    const highlightProp = netHighlightProp.checked;
    for (const item of networkItems) {
      const isProposed = item.isProposed;
      item.mesh.visible = isProposed ? showProp : showDoc;
      if (inspectedItem === item) {
        item.mesh.material = selectedNetMat;
      } else if (highlightProp && isProposed) {
        item.mesh.material = proposedHighlightMat;
      } else {
        item.mesh.material = item.originalMaterial;
      }
    }
    requestFrame();
  }

  function buildAtticGuides(guides) {
    if (atticGuidesGroup) {
      scene.remove(atticGuidesGroup);
      disposeObjectTree(atticGuidesGroup);
      atticGuidesGroup = null;
    }
    atticClearancesList.innerHTML = '';
    if (!guides) {
      atticGuidesControls.hidden = true;
      return;
    }
    atticGuidesControls.hidden = false;
    const group = new THREE.Group();
    group.visible = atticGuidesInput.checked;

    const { bounds, headroomLevels, tank } = guides;
    const width = bounds.maxX - bounds.minX;
    const depth = bounds.maxZ - bounds.minZ;
    const cx = (bounds.minX + bounds.maxX) / 2;
    const cz = (bounds.minZ + bounds.maxZ) / 2;

    for (const level of headroomLevels) {
      const planeGeom = new THREE.PlaneGeometry(width, depth);
      const planeMat = new THREE.MeshBasicMaterial({
        color: level.color, transparent: true, opacity: 0.14, side: THREE.DoubleSide, depthWrite: false,
      });
      const plane = new THREE.Mesh(planeGeom, planeMat);
      plane.rotation.x = -Math.PI / 2;
      plane.position.set(cx, level.y, cz);
      const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(planeGeom),
        new THREE.LineBasicMaterial({ color: level.color, transparent: true, opacity: 0.75 }),
      );
      plane.add(edges);
      group.add(plane);
    }

    if (tank) {
      const envR = tank.radius + tank.maintenanceMargin;
      const envH = tank.height + tank.maintenanceMargin;
      const cylGeom = new THREE.CylinderGeometry(envR, envR, envH, 32, 1, true);
      const cylMat = new THREE.MeshBasicMaterial({
        color: 0xe5a93c, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false,
      });
      const cyl = new THREE.Mesh(cylGeom, cylMat);
      cyl.position.set(tank.center[0], tank.baseY + envH / 2, tank.center[2]);
      const ringGeom = new THREE.RingGeometry(envR - 0.03, envR + 0.03, 40);
      const ring = new THREE.Mesh(ringGeom, new THREE.MeshBasicMaterial({ color: 0xe5a93c, side: THREE.DoubleSide }));
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(tank.center[0], tank.baseY + 0.02, tank.center[2]);
      group.add(cyl, ring);

      for (const item of tank.clearances ?? []) {
        const li = document.createElement('li');
        if (!item.critical) li.className = 'ok';
        li.textContent = item.label;
        atticClearancesList.append(li);
      }
      for (const level of headroomLevels) {
        const li = document.createElement('li');
        li.className = 'ok';
        li.textContent = `${level.label} (cota +${cutFormat.format(level.y)} m)`;
        atticClearancesList.append(li);
      }
    }
    atticClearancesList.hidden = !atticGuidesInput.checked;
    atticGuidesGroup = group;
    scene.add(atticGuidesGroup);
  }

  function makeGroundLabel(text, worldWidth, worldHeight, { bg = 'rgba(17, 25, 22, 0.88)', fg = '#e5f2ea', border = '#8ad4b0' } = {}) {
    const c = document.createElement('canvas');
    c.width = 512;
    c.height = Math.max(88, Math.round(512 * (worldHeight / worldWidth)));
    const ctx = c.getContext('2d');
    const pad = 10;
    const radius = 16;
    ctx.fillStyle = bg;
    ctx.beginPath();
    ctx.roundRect(pad, pad, c.width - pad * 2, c.height - pad * 2, radius);
    ctx.fill();
    ctx.strokeStyle = border;
    ctx.lineWidth = 4;
    ctx.stroke();
    ctx.fillStyle = fg;
    ctx.font = '700 32px "Segoe UI", system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, c.width / 2, c.height / 2 + 1);
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(worldWidth, worldHeight),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }),
    );
    mesh.rotation.x = -Math.PI / 2;
    return mesh;
  }

  function makeDashedRect(minX, maxX, minZ, maxZ, y, color, { dash = 0.16, gap = 0.10 } = {}) {
    const pts = [
      new THREE.Vector3(minX, y, minZ),
      new THREE.Vector3(maxX, y, minZ),
      new THREE.Vector3(maxX, y, maxZ),
      new THREE.Vector3(minX, y, maxZ),
      new THREE.Vector3(minX, y, minZ),
    ];
    const geom = new THREE.BufferGeometry().setFromPoints(pts);
    const line = new THREE.Line(geom, new THREE.LineDashedMaterial({ color, dashSize: dash, gapSize: gap }));
    line.computeLineDistances();
    return line;
  }

  function makeDimLine(ax, az, bx, bz, y, color, tick = 0.12) {
    const dx = bx - ax;
    const dz = bz - az;
    const len = Math.hypot(dx, dz) || 1;
    const nx = (-dz / len) * tick;
    const nz = (dx / len) * tick;
    const pts = [
      new THREE.Vector3(ax, y, az), new THREE.Vector3(bx, y, bz),
      new THREE.Vector3(ax - nx, y, az - nz), new THREE.Vector3(ax + nx, y, az + nz),
      new THREE.Vector3(bx - nx, y, bz - nz), new THREE.Vector3(bx + nx, y, bz + nz),
    ];
    return new THREE.LineSegments(
      new THREE.BufferGeometry().setFromPoints(pts),
      new THREE.LineBasicMaterial({ color }),
    );
  }

  function buildParkingGuides() {
    const group = new THREE.Group();
    const yFloor = 0.024;
    const yLine = 0.032;
    const yLabel = 0.038;

    // 1. Faixa frontal completa do lote até a via interna (ARQ01: 6,35 x 2,50 m).
    const lotFrontFill = new THREE.Mesh(
      new THREE.PlaneGeometry(6.35, 2.50),
      new THREE.MeshBasicMaterial({ color: 0x9bd5b9, transparent: true, opacity: 0.06, depthWrite: false }),
    );
    lotFrontFill.rotation.x = -Math.PI / 2;
    lotFrontFill.position.set(3.175, yFloor - 0.004, 1.25);
    group.add(lotFrontFill);
    group.add(makeDashedRect(0.0, 6.35, 0.0, 2.50, yLine, 0xc9dbd2, { dash: 0.22, gap: 0.14 }));

    // 2. Vão da garagem coberta (ARQ03: 2,85 m de largura x 3,20 m cobertos).
    group.add(makeDashedRect(3.40, 6.25, -2.00, 1.20, yLine, 0x9bd5b9, { dash: 0.14, gap: 0.10 }));

    // 3. Vaga 1 oficial demarcada (ARQ01: 2,20 x 4,50 m -> X=3.56..5.76, Z=-2.00..+2.50).
    // Parte coberta (3,20 m: Z=-2.00..+1.20) em verde-menta e descoberta (1,30 m: Z=+1.20..+2.50) em âmbar.
    const slot1Covered = new THREE.Mesh(
      new THREE.PlaneGeometry(2.20, 3.20),
      new THREE.MeshBasicMaterial({ color: 0x4fb686, transparent: true, opacity: 0.22, depthWrite: false }),
    );
    slot1Covered.rotation.x = -Math.PI / 2;
    slot1Covered.position.set(4.66, yFloor, -0.40);
    group.add(slot1Covered);

    const slot1Open = new THREE.Mesh(
      new THREE.PlaneGeometry(2.20, 1.30),
      new THREE.MeshBasicMaterial({ color: 0xe6b24c, transparent: true, opacity: 0.22, depthWrite: false }),
    );
    slot1Open.rotation.x = -Math.PI / 2;
    slot1Open.position.set(4.66, yFloor, 1.85);
    group.add(slot1Open);

    const slot1Border = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(3.56, yLine + 0.002, -2.00),
        new THREE.Vector3(5.76, yLine + 0.002, -2.00),
        new THREE.Vector3(5.76, yLine + 0.002, 2.50),
        new THREE.Vector3(3.56, yLine + 0.002, 2.50),
      ]),
      new THREE.LineBasicMaterial({ color: 0x8be2b6 }),
    );
    group.add(slot1Border);

    // 4. Vaga 2 lateral em frente à janela da sala com medição graduada para o Renault Sandero 1.0 2018 (4,06 x 1,733 m):
    // - 0,00..1,20 m (1,20 m coberto sob a sacada)
    // - 1,20..2,50 m (+1,30 m até o limite oficial do lote ARQ01 = 2,50 m)
    // - 2,50..3,25 m (+0,75 m até o limite da faixa branca da via / eixo dianteiro do Sandero em 3,28 m)
    // - 3,25..4,09 m (+0,84 m de projeção do para-choque dianteiro do Sandero além da faixa / +1,59 m além do lote).
    const slot2Covered = new THREE.Mesh(
      new THREE.PlaneGeometry(2.00, 1.20),
      new THREE.MeshBasicMaterial({ color: 0x4fb686, transparent: true, opacity: 0.18, depthWrite: false }),
    );
    slot2Covered.rotation.x = -Math.PI / 2;
    slot2Covered.position.set(1.68, yFloor, 0.60);
    group.add(slot2Covered);

    const slot2LotOpen = new THREE.Mesh(
      new THREE.PlaneGeometry(2.00, 1.30),
      new THREE.MeshBasicMaterial({ color: 0xe6b24c, transparent: true, opacity: 0.18, depthWrite: false }),
    );
    slot2LotOpen.rotation.x = -Math.PI / 2;
    slot2LotOpen.position.set(1.68, yFloor, 1.85);
    group.add(slot2LotOpen);

    const slot2Stripe = new THREE.Mesh(
      new THREE.PlaneGeometry(2.00, 0.75),
      new THREE.MeshBasicMaterial({ color: 0x7cb6dc, transparent: true, opacity: 0.18, depthWrite: false }),
    );
    slot2Stripe.rotation.x = -Math.PI / 2;
    slot2Stripe.position.set(1.68, yFloor, 2.875);
    group.add(slot2Stripe);

    const slot2Overhang = new THREE.Mesh(
      new THREE.PlaneGeometry(2.00, 0.84),
      new THREE.MeshBasicMaterial({ color: 0xe5735c, transparent: true, opacity: 0.24, depthWrite: false }),
    );
    slot2Overhang.rotation.x = -Math.PI / 2;
    slot2Overhang.position.set(1.68, yFloor, 3.67);
    group.add(slot2Overhang);

    const slot2Border = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0.68, yLine + 0.002, 0.00),
        new THREE.Vector3(2.68, yLine + 0.002, 0.00),
        new THREE.Vector3(2.68, yLine + 0.002, 3.25),
        new THREE.Vector3(0.68, yLine + 0.002, 3.25),
      ]),
      new THREE.LineBasicMaterial({ color: 0x9ac8e8 }),
    );
    group.add(slot2Border);

    const slot2OverhangBorder = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0.68, yLine + 0.003, 3.25),
        new THREE.Vector3(2.68, yLine + 0.003, 3.25),
        new THREE.Vector3(2.68, yLine + 0.003, 4.09),
        new THREE.Vector3(0.68, yLine + 0.003, 4.09),
      ]),
      new THREE.LineBasicMaterial({ color: 0xf08c77 }),
    );
    group.add(slot2OverhangBorder);

    // Protetores de para-choque reais nas paredes (conforme fotos exterior1 / exterior2).
    const guardBackMat = new THREE.MeshStandardMaterial({ color: 0x1a1d20, roughness: 0.7 });
    const guardStripeMat = new THREE.MeshStandardMaterial({ color: 0xf0c432, roughness: 0.4 });
    const guardPositions = [
      [4.50, -1.985], [4.82, -1.985], // Parede fundo da garagem (Vaga 1)
      [1.52, 0.015], [1.84, 0.015],   // Parede sob a janela da sala (Vaga 2 lateral)
    ];
    for (const [gx, gz] of guardPositions) {
      const gBase = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.46, 0.03), guardBackMat);
      gBase.position.set(gx, 0.48, gz);
      const gStripe = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.36, 0.034), guardStripeMat);
      gStripe.position.set(gx, 0.48, gz);
      group.add(gBase, gStripe);
    }

    // Linha de projeção do balanço superior (Z = +1,20 m).
    const overhangLine = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0.00, yLine + 0.003, 1.20),
        new THREE.Vector3(6.25, yLine + 0.003, 1.20),
      ]),
      new THREE.LineBasicMaterial({ color: 0xf6c96c }),
    );
    group.add(overhangLine);

    // Linhas de cota graduadas com tiques para mensuração das duas vagas.
    group.add(makeDimLine(3.56, 2.66, 5.76, 2.66, yLine, 0x8be2b6));        // Largura Vaga 1 (2,20 m)
    group.add(makeDimLine(3.40, 2.94, 6.25, 2.94, yLine, 0xc9dbd2));        // Largura garagem (2,85 m)
    group.add(makeDimLine(3.46, -2.00, 3.46, 2.50, yLine, 0x8be2b6, 0.08)); // Compr. Vaga 1 (4,50 m)
    group.add(makeDimLine(0.68, 4.22, 2.68, 4.22, yLine, 0x9ac8e8));        // Largura Vaga 2 (2,00 m)
    group.add(makeDimLine(0.54, 0.00, 0.54, 2.50, yLine, 0xe6b24c, 0.08));  // Recuo lote Vaga 2 (2,50 m)
    group.add(makeDimLine(0.54, 2.50, 0.54, 3.25, yLine, 0x9ac8e8, 0.08));  // Faixa rua Vaga 2 (+0,75 m = 3,25 m)
    group.add(makeDimLine(0.54, 3.25, 0.54, 4.09, yLine, 0xf08c77, 0.08));  // Avanço bico Sandero (+0,84 m = 4,09 m)

    // Etiquetas no piso com as medidas exatas para mensuração.
    const slot1Label = makeGroundLabel('VAGA 1 · 2,20 × 4,50 m', 2.35, 0.40, { fg: '#9fe6c3', border: '#8be2b6' });
    slot1Label.position.set(4.66, yLabel, 3.25);
    group.add(slot1Label);

    const car1SpecLabel = makeGroundLabel('SUV máx. 4,48 × 1,84 m', 2.35, 0.36, { fg: '#f6d488', border: '#e6b24c' });
    car1SpecLabel.position.set(4.66, yLabel, 3.68);
    group.add(car1SpecLabel);

    const slot2Label = makeGroundLabel('SANDERO 1.0 2018 · 4,06 × 1,73 m', 2.45, 0.38, { fg: '#b9dbf5', border: '#9ac8e8' });
    slot2Label.position.set(1.68, yLabel, 4.52);
    group.add(slot2Label);

    const car2SpecLabel = makeGroundLabel('+1,59 m lote · +0,84 m faixa (rodas OK)', 2.45, 0.36, { fg: '#f8b4a6', border: '#f08c77' });
    car2SpecLabel.position.set(1.68, yLabel, 4.94);
    group.add(car2SpecLabel);

    scene.add(group);
    return group;
  }

  function createVehicleMesh({
    length, width, height, wheelbase, wheelRadius,
    bodyColor, roofColor, isCompactHatch = false,
  }) {
    const car = new THREE.Group();
    const halfL = length / 2;
    const halfW = width / 2;

    const bodyMat = new THREE.MeshStandardMaterial({ color: bodyColor, metalness: 0.48, roughness: 0.30 });
    const roofMat = roofColor
      ? new THREE.MeshStandardMaterial({ color: roofColor, metalness: 0.35, roughness: 0.25 })
      : bodyMat;
    const trimMat = new THREE.MeshStandardMaterial({ color: 0x1e2328, metalness: 0.15, roughness: 0.72 });
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x151f28, metalness: 0.38, roughness: 0.11 });
    const tireMat = new THREE.MeshStandardMaterial({ color: 0x1a1c1e, roughness: 0.88, metalness: 0.05 });
    const rimMat = new THREE.MeshStandardMaterial({ color: 0xd0d7dd, metalness: 0.80, roughness: 0.22 });
    const headLightMat = new THREE.MeshStandardMaterial({ color: 0xfff6dc, emissive: 0xffe4a3, emissiveIntensity: 0.38, roughness: 0.2 });
    const tailLightMat = new THREE.MeshStandardMaterial({ color: 0xc42424, emissive: 0xa41919, emissiveIntensity: 0.38, roughness: 0.24 });
    const plateMat = new THREE.MeshStandardMaterial({ color: 0xedf1f4, roughness: 0.5 });

    // Sombra suave de contato no piso.
    const shadowPlane = new THREE.Mesh(
      new THREE.PlaneGeometry(width + 0.12, length + 0.10),
      new THREE.MeshBasicMaterial({ color: 0x090d0b, transparent: true, opacity: 0.34, depthWrite: false }),
    );
    shadowPlane.rotation.x = -Math.PI / 2;
    shadowPlane.position.y = 0.014;
    car.add(shadowPlane);

    const beltY = height * 0.61;
    const hoodTipY = height * 0.48;
    const groundClearY = wheelRadius * 0.74;
    const hoodStart = isCompactHatch ? halfL * 0.40 : halfL * 0.46;

    // Perfil lateral da carroceria inferior.
    const lowerShape = new THREE.Shape();
    lowerShape.moveTo(-halfL + 0.03, groundClearY);
    lowerShape.lineTo(halfL - 0.06, groundClearY);
    lowerShape.quadraticCurveTo(halfL, groundClearY + 0.02, halfL, groundClearY + 0.20);
    lowerShape.lineTo(halfL - 0.03, hoodTipY);
    lowerShape.quadraticCurveTo(halfL - 0.10, beltY - 0.06, halfL - 0.36, beltY - 0.03);
    lowerShape.lineTo(hoodStart, beltY);
    lowerShape.lineTo(-halfL + 0.18, beltY + 0.02);
    lowerShape.quadraticCurveTo(-halfL + 0.03, beltY - 0.02, -halfL + 0.01, hoodTipY);
    lowerShape.lineTo(-halfL, groundClearY + 0.12);
    lowerShape.quadraticCurveTo(-halfL, groundClearY, -halfL + 0.03, groundClearY);

    const bodyDepth = width - 0.12;
    const lowerGeom = new THREE.ExtrudeGeometry(lowerShape, {
      depth: bodyDepth, bevelEnabled: true, bevelThickness: 0.055, bevelSize: 0.038, bevelSegments: 2,
    });
    lowerGeom.center();
    const lowerBody = new THREE.Mesh(lowerGeom, bodyMat);
    lowerBody.rotation.y = -Math.PI / 2;
    lowerBody.position.set(0, (groundClearY + beltY) * 0.5 + 0.01, 0);
    car.add(lowerBody);

    // Saia plástica inferior / para-choques.
    const skirt = new THREE.Mesh(new THREE.BoxGeometry(width - 0.06, 0.15, length - 0.06), trimMat);
    skirt.position.set(0, groundClearY + 0.02, 0);
    car.add(skirt);

    // Cabine / teto.
    const cabinRear = -halfL + (isCompactHatch ? 0.16 : 0.34);
    const cabinFront = hoodStart + 0.04;
    const roofFront = isCompactHatch ? halfL * 0.12 : halfL * 0.18;
    const roofRear = -halfL + (isCompactHatch ? 0.42 : 0.78);
    const cabinCenterZ = (cabinRear + cabinFront) / 2;

    const cabinShape = new THREE.Shape();
    cabinShape.moveTo(cabinRear, beltY - 0.03);
    cabinShape.lineTo(cabinFront, beltY - 0.03);
    cabinShape.lineTo(roofFront, height - 0.03);
    cabinShape.lineTo(roofRear, height - 0.03);
    cabinShape.quadraticCurveTo(cabinRear + 0.10, height - 0.07, cabinRear, beltY - 0.03);

    const cabinDepth = width * 0.77;
    const cabinGeom = new THREE.ExtrudeGeometry(cabinShape, {
      depth: cabinDepth, bevelEnabled: true, bevelThickness: 0.045, bevelSize: 0.032, bevelSegments: 2,
    });
    cabinGeom.center();
    const cabin = new THREE.Mesh(cabinGeom, roofMat);
    cabin.rotation.y = -Math.PI / 2;
    cabin.position.set(0, (beltY + height) * 0.5 - 0.02, cabinCenterZ);
    car.add(cabin);

    // Vidros envolventes (para-brisa, laterais e vigia traseiro) salientes 1 cm sobre a cabine.
    const glassShape = new THREE.Shape();
    glassShape.moveTo(cabinRear - 0.01, beltY + 0.02);
    glassShape.lineTo(cabinFront + 0.01, beltY + 0.02);
    glassShape.lineTo(roofFront + 0.02, height - 0.10);
    glassShape.lineTo(roofRear - 0.01, height - 0.10);
    glassShape.closePath();

    const glassGeom = new THREE.ExtrudeGeometry(glassShape, {
      depth: cabinDepth + 0.11, bevelEnabled: false,
    });
    glassGeom.center();
    const greenhouse = new THREE.Mesh(glassGeom, glassMat);
    greenhouse.rotation.y = -Math.PI / 2;
    greenhouse.position.set(0, (beltY + height) * 0.5 - 0.03, cabinCenterZ);
    car.add(greenhouse);

    // Racks longitudinais no teto (apenas no SUV).
    if (!isCompactHatch) {
      for (const sx of [-width * 0.30, width * 0.30]) {
        const rail = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, (roofFront - roofRear) * 0.88), trimMat);
        rail.position.set(sx, height + 0.01, (roofFront + roofRear) * 0.5);
        car.add(rail);
      }
    }

    // 4 rodas posicionadas exatamente no entre-eixos real (wheelbase).
    const halfWB = wheelbase / 2;
    const wheelX = halfW - 0.09;
    const wheelPositions = [
      [-wheelX, wheelRadius, halfWB], [wheelX, wheelRadius, halfWB],
      [-wheelX, wheelRadius, -halfWB], [wheelX, wheelRadius, -halfWB],
    ];
    const tireGeom = new THREE.CylinderGeometry(wheelRadius, wheelRadius, 0.21, 22);
    const rimGeom = new THREE.CylinderGeometry(wheelRadius * 0.64, wheelRadius * 0.64, 0.22, 14);
    const hubGeom = new THREE.CylinderGeometry(wheelRadius * 0.21, wheelRadius * 0.21, 0.23, 12);
    for (const [wx, wy, wz] of wheelPositions) {
      const wGroup = new THREE.Group();
      wGroup.position.set(wx, wy, wz);
      wGroup.rotation.z = Math.PI / 2;
      wGroup.add(
        new THREE.Mesh(tireGeom, tireMat),
        new THREE.Mesh(rimGeom, rimMat),
        new THREE.Mesh(hubGeom, trimMat),
      );
      car.add(wGroup);
    }

    // Retrovisores laterais.
    for (const sx of [-(halfW + 0.04), halfW + 0.04]) {
      const mirror = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.09, 0.13), roofMat);
      mirror.position.set(sx, beltY + 0.04, hoodStart - 0.15);
      car.add(mirror);
    }

    // Grade dianteira, faróis (+Z = rua) e lanternas traseiras (-Z = parede).
    const grille = new THREE.Mesh(new THREE.BoxGeometry(width * 0.50, 0.22, 0.06), trimMat);
    grille.position.set(0, hoodTipY - 0.12, halfL - 0.01);
    car.add(grille);

    for (const sx of [-width * 0.34, width * 0.34]) {
      const hl = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.12, 0.07), headLightMat);
      hl.position.set(sx, hoodTipY - 0.04, halfL - 0.02);
      const tl = new THREE.Mesh(new THREE.BoxGeometry(0.36, isCompactHatch ? 0.22 : 0.13, 0.07), tailLightMat);
      tl.position.set(sx, beltY - 0.14, -halfL + 0.02);
      car.add(hl, tl);
    }

    const frontPlate = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.11, 0.03), plateMat);
    frontPlate.position.set(0, groundClearY + 0.14, halfL);
    const rearPlate = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.11, 0.03), plateMat);
    rearPlate.position.set(0, groundClearY + 0.26, -halfL);
    car.add(frontPlate, rearPlate);

    car.traverse((node) => {
      if (node.isMesh && node !== shadowPlane) {
        node.castShadow = true;
        node.receiveShadow = true;
      }
    });
    return car;
  }

  function buildParkedCar() {
    const group = new THREE.Group();

    // Carro 1 (Vaga 1 garagem principal 4,50 m): SUV em ocupação máxima da vaga
    // 4,48 m compr. × 1,84 m larg. × 1,63 m alt., entre-eixos 2,64 m (Z = -1,99..+2,49 m -> 99,6% dos 4,50 m).
    const suv = createVehicleMesh({
      length: 4.48,
      width: 1.84,
      height: 1.63,
      wheelbase: 2.64,
      wheelRadius: 0.34,
      bodyColor: 0x5c7080,
      roofColor: null,
      isCompactHatch: false,
    });
    suv.position.set(4.66, 0.015, 0.25);
    group.add(suv);

    // Carro 2 (Vaga 2 lateral em frente à sala): Renault Sandero 1.0 12V SCe 2018 (medidas oficiais de fábrica)
    // 4,060 m compr. × 1,733 m larg. (1,994 m c/ retrovisores) × 1,536 m alt., entre-eixos 2,590 m (Z = +0,03..+4,09 m).
    const sandero = createVehicleMesh({
      length: 4.06,
      width: 1.733,
      height: 1.536,
      wheelbase: 2.59,
      wheelRadius: 0.31,
      bodyColor: 0xc4d4de,
      roofColor: null,
      isCompactHatch: true,
    });
    sandero.position.set(1.68, 0.015, 2.06);
    group.add(sandero);

    scene.add(group);
    return group;
  }

  const parkingGuidesGroup = buildParkingGuides();
  const parkedCarGroup = buildParkedCar();

  function updateParkingVisibility() {
    const showOnFloor = floor === 'full' || floor === 'terreo';
    const showGuides = parkingGuidesInput.checked;
    const showCar = parkingCarInput.checked;
    parkingGuidesGroup.visible = showOnFloor && showGuides;
    parkedCarGroup.visible = showOnFloor && showCar;
    parkingSpecsList.hidden = !showGuides && !showCar;
    plan?.setParkingOptions({ showGuides, showCar });
  }

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

    const view = floorViews[floor] ?? floorViews.full;
    const bounds = new THREE.Box3();
    for (const key of view.layers) {
      const layer = layers.get(key);
      if (layer?.node.visible) bounds.union(layer.box);
    }
    if (bounds.isEmpty()) return;
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

  function setRoomVariant(nextVariant) {
    activeRoomVariant = nextVariant;
    for (const node of roomVariantGroups) {
      node.visible = node.userData.web_room_variant === activeRoomVariant;
    }
    for (const button of roomVariantOptions.querySelectorAll('button')) {
      button.setAttribute('aria-pressed', String(button.dataset.roomVariant === activeRoomVariant));
    }
    plan?.invalidateOutlines();
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function updateView() {
    if (!modelReady) return;
    const full = floor === 'full';
    const visibleRoof = layers.has('telhado') && full && roofPreferred;
    const showCeilingLights = ceilingLights.checked;
    for (const [key, { node }] of layers) {
      if (key === 'telhado') node.visible = visibleRoof;
      else if (key === 'forro-terreo') node.visible = showCeilingLights && (full || floor === 'terreo');
      else node.visible = full || key === floor || key === 'instalacoes' || (floor === 'terreo' && key === 'contexto');
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
    sheetStyle?.apply(presentation === 'prancha', wallMaterials);
    for (const button of wallButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.walls === wallMode));
    }
    for (const input of networkInputs) {
      const matching = networks.filter((node) => node.userData.web_network === input.dataset.network);
      for (const node of matching) node.visible = input.checked && node.userData.web_network_view === floor;
      input.disabled = !matching.some((node) => node.userData.web_network_view === floor);
    }
    updateNetworkToggleAllLabel();
    applyNetworkStyles();
    for (const node of roomVariantGroups) {
      node.visible = node.userData.web_room_variant === activeRoomVariant;
    }
    const view = floorViews[floor] ?? floorViews.full;
    title.textContent = activePreset?.label ?? view.label;
    document.querySelector('#view-category').textContent = activePreset?.section ??
      (full && presentation === 'prancha' ? 'Prancha' : view.category);
    document.querySelector('#view-status').textContent =
      `${title.textContent}. Telhado ${visibleRoof ? 'visível' : 'oculto'}.` +
      (wallGroups.length ? ` Paredes externas ${wallDescriptions[wallMode]}.` : '');
    updateMovementPadVisibility();
    updateParkingVisibility();
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function selectView(nextFloor, preset = null, { reframe = true } = {}) {
    floor = layers.has(nextFloor) || nextFloor === 'full' ? nextFloor : 'full';
    activePreset = preset;
    orientation = 'isometric';
    if (preset?.roomVariant && roomVariantGroups.length) {
      setRoomVariant(preset.roomVariant);
    }
    const planFloor = floor === 'full' && preset?.section === 'Superior' ? 'superior' : floor;
    plan?.setFloor(planFloor, floor);
    const floorBox = layers.get(floor)?.box;
    cutHeight.min = (floorElevation[floor] ?? 0) + 0.15;
    cutHeight.max = floorBox ? Math.ceil(floorBox.max.y * 20) / 20 :
      Math.ceil(Math.max(...[...layers.values()].map(({ box }) => box.max.y)) * 20) / 20;
    cutHeight.value = floorBox ? (floorElevation[floor] ?? 0) + 1.1 : 3.8;
    updateCut();
    updateView();
    if (reframe) frameActiveView();
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
    requestFrame();
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
    plan?.draw();
  }

  function buildPresets(presets) {
    const list = document.querySelector('#presets');
    list.innerHTML = '';
    presetButtons.clear();
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

  function updateMovementPadVisibility() {
    const isOverview = floor === 'full' && !activePreset;
    movementPad.hidden = navigation !== 'free' || isOverview;
  }

  function setNavigation(mode) {
    navigation = mode;
    stopMotion();
    const free = mode === 'free';
    controls.maxPolarAngle = free ? Math.PI : Math.PI * 0.92;
    if (camera.isOrthographicCamera !== usesAxonometry()) frameActiveView();
    else setCamera(camera.position.clone(), controls.target.clone());
    updateMovementPadVisibility();
    for (const button of navigationButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.navigation === mode));
    }
  }

  let clickStart = null;
  const sceneRay = new THREE.Raycaster();
  const pointerInScene = new THREE.Vector2();

  function raycastSurfaces(x, y) {
    pointerInScene.set(x, y);
    sceneRay.setFromCamera(pointerInScene, camera);
    const surfaces = [];
    currentRoot?.traverseVisible((node) => { if (node.isMesh) surfaces.push(node); });
    return sceneRay.intersectObjects(surfaces, false).find(({ point }) =>
      !cutEnabled.checked || cutPlane.distanceToPoint(point) >= 0);
  }

  function focusSurface(x, y) {
    const hit = raycastSurfaces(x, y);
    if (!hit) return;
    if (camera.isOrthographicCamera) {
      camera.zoom = Math.max(camera.zoom, 2);
      camera.updateProjectionMatrix();
    }
    const offset = camera.position.clone().sub(controls.target).setLength(Math.min(3, controls.getDistance()));
    setCamera(hit.point.clone().add(offset), hit.point);
  }

  canvas.addEventListener('dblclick', (event) => {
    if (!modelReady || arrangement === 'dupla' || measuring) return;
    const rect = canvas.getBoundingClientRect();
    focusSurface(2 * (event.clientX - rect.left) / rect.width - 1, 1 - 2 * (event.clientY - rect.top) / rect.height);
  });
  canvas.addEventListener('pointerdown', (event) => {
    if (event.isPrimary && event.button === 0) {
      canvas.focus({ preventScroll: true });
      clickStart = [event.clientX, event.clientY];
      film?.pauseCameraOnUserDrag();
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
    const nx = 2 * (x - bounds.left) / bounds.width - 1;
    const ny = 1 - 2 * (y - bounds.top) / bounds.height;

    if (measuring) {
      const hit = raycastSurfaces(nx, ny);
      if (hit) {
        if (measurePoints3D.length >= 2) measurePoints3D = [hit.point.clone()];
        else measurePoints3D.push(hit.point.clone());
        rebuildMeasure3D();
      }
      return;
    }

    if (variant === 'estrutural' && networkItems.length) {
      pointerInScene.set(nx, ny);
      sceneRay.setFromCamera(pointerInScene, camera);
      const visibleNetMeshes = networkItems.filter((i) => i.mesh.visible && i.mesh.parent?.visible).map((i) => i.mesh);
      const hit = sceneRay.intersectObjects(visibleNetMeshes, false)[0];
      if (hit) {
        const found = networkItems.find((i) => i.mesh === hit.object);
        if (found) { showInspection(found); return; }
      }
    }

    if (studio?.isRenovateMode()) {
      pointerInScene.set(nx, ny);
      sceneRay.setFromCamera(pointerInScene, camera);
      if (studio.handleSceneClick(sceneRay)) return;
    }

    if (arrangement === 'dupla') {
      pointerInScene.set(nx, ny);
      sceneRay.setFromCamera(pointerInScene, camera);
      plan?.pickInScene(sceneRay);
    }
  });

  canvas.addEventListener('keydown', (event) => {
    if (!modelReady || event.altKey || event.ctrlKey || event.metaKey) return;
    const key = event.key.toLowerCase();
    if (key === 'escape' && measuring) { setMeasuring(false); return; }
    if (key === 'f') { event.preventDefault(); if (!event.repeat) focusSurface(0, 0); return; }
    const direction = movementKeys[key];
    if (!direction) return;
    event.preventDefault();
    if (heldKeys.has(key)) return;
    heldKeys.set(key, direction);
    beginMotion(direction);
  });
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && measuring) setMeasuring(false);
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
  for (const button of floorButtons) {
    button.addEventListener('click', () => selectView(button.dataset.floor));
  }
  overview.addEventListener('click', () => {
    studio?.setWalkMode(false);
    roofPreferred = initialRoof;
    wallMode = 'glass';
    cutEnabled.checked = false;
    clearInspection();
    selectView('full');
  });
  walkButton?.addEventListener('click', () => {
    if (!modelReady) return;
    if (arrangement === 'planta') {
      setArrangement('3d');
      replaceParameter('arranjo', null);
    }
    if (presentation === 'prancha') setPresentation('model');
    if (navigation !== 'free') setNavigation('free');
    studio?.setWalkMode(!studio.isWalkMode());
  });
  roof.addEventListener('change', () => {
    roofPreferred = roof.checked;
    updateView();
  });
  ceilingLights.addEventListener('change', updateView);
  for (const button of wallButtons) {
    button.addEventListener('click', () => {
      wallMode = button.dataset.walls;
      updateView();
    });
  }
  for (const input of networkInputs) input.addEventListener('change', updateView);
  networkToggleAll?.addEventListener('click', () => {
    const activeInputs = networkInputs.filter((input) => !input.disabled);
    const shouldCheck = !activeInputs.some((input) => input.checked);
    for (const input of activeInputs) input.checked = shouldCheck;
    if (!shouldCheck) clearInspection();
    updateView();
  });
  netDocInput.addEventListener('change', applyNetworkStyles);
  netPropInput.addEventListener('change', applyNetworkStyles);
  netHighlightProp.addEventListener('change', applyNetworkStyles);
  inspectClose.addEventListener('click', clearInspection);
  atticGuidesInput.addEventListener('change', () => {
    if (atticGuidesGroup) atticGuidesGroup.visible = atticGuidesInput.checked;
    atticClearancesList.hidden = !atticGuidesInput.checked;
    requestFrame();
  });
  for (const input of [parkingGuidesInput, parkingCarInput]) {
    input.addEventListener('change', () => {
      updateParkingVisibility();
      renderer.shadowMap.needsUpdate = true;
      requestFrame();
    });
  }

  recenter.addEventListener('click', frameActiveView);
  zoomIn.addEventListener('click', () => zoom(0.83));
  zoomOut.addEventListener('click', () => zoom(1 / 0.83));
  measureToggle.addEventListener('click', () => setMeasuring(!measuring));
  measureClear.addEventListener('click', clearMeasure);

  for (const button of lightingButtons) {
    button.addEventListener('click', () => {
      lightingMode = button.dataset.lighting;
      // Crepúsculo usa Khronos PBR Neutral automaticamente para preservar o laranja do pôr do sol (dica Nyxera0x).
      if (lightingMode === 'dusk') toneMappingMode = 'neutral';
      applyLighting();
    });
  }
  toneMappingButton?.addEventListener('click', () => {
    toneMappingMode = toneMappingMode === 'agx' ? 'neutral' : 'agx';
    applyToneMapping();
    showToast(toneMappingMode === 'neutral'
      ? 'Curva Khronos PBR Neutral ativa (cores reais no pôr do sol)'
      : 'Curva AgX cinematográfica ativa');
  });
  clayButton?.addEventListener('click', () => {
    if (!modelReady || !film) return;
    const next = film.setClayMode(!film.isClayMode());
    clayButton.setAttribute('aria-pressed', String(next));
  });
  filmButton?.addEventListener('click', () => {
    if (!modelReady || !film) return;
    if (film.isFilmActive()) {
      film.exitFilm();
      return;
    }
    if (arrangement !== '3d') {
      setArrangement('3d');
      replaceParameter('arranjo', null);
    }
    if (presentation === 'prancha') setPresentation('model');
    studio?.setWalkMode(false);
    selectView('full', null, { reframe: false });
    film.startFilm();
  });
  sunAngle.addEventListener('input', applyLighting);

  exportPng.addEventListener('click', () => {
    const targetCanvas = arrangement === 'planta' ? document.querySelector('#plan-canvas') : canvas;
    if (arrangement !== 'planta') renderer.render(scene, camera);
    const dataUrl = targetCanvas.toDataURL('image/png');
    const slug = (activePreset?.id ?? floor).replace(/[^a-z0-9-]+/gi, '-').toLowerCase();
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `sobrado-${variant}-${slug}.png`;
    a.click();
    showToast('Captura PNG salva');
  });

  copyLink.addEventListener('click', async () => {
    const url = new URL(window.location.href);
    url.searchParams.set('maquete', variant);
    if (presentation === 'prancha') url.searchParams.set('vista', 'prancha');
    else url.searchParams.delete('vista');
    if (arrangement !== '3d') url.searchParams.set('arranjo', arrangement);
    else url.searchParams.delete('arranjo');
    if (floor !== 'full') url.searchParams.set('piso', floor);
    else url.searchParams.delete('piso');
    if (wallMode !== 'glass') url.searchParams.set('paredes', wallMode);
    else url.searchParams.delete('paredes');
    if (lightingMode !== 'day') url.searchParams.set('luz', lightingMode);
    else url.searchParams.delete('luz');
    url.searchParams.set('sol', sunAngle.value);
    const nums = [
      camera.position.x, camera.position.y, camera.position.z,
      controls.target.x, controls.target.y, controls.target.z,
    ].map((n) => n.toFixed(2));
    url.searchParams.set('cam', nums.join(','));
    history.replaceState(null, '', url.toString());
    try {
      await navigator.clipboard.writeText(url.toString());
      showToast('Link da vista copiado');
    } catch {
      showToast('URL atualizada na barra de endereço');
    }
  });

  for (const button of arrangementButtons) {
    button.disabled = true;
    button.addEventListener('click', () => {
      studio?.setWalkMode(false);
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

  modelSelect.addEventListener('change', () => {
    const next = modelSelect.value;
    if (next === variant) return;
    loadModel(next, { preserveCamera: true });
  });

  studio = createPersonalizer({
    scene,
    renderer,
    getCamera: () => camera,
    setCamera,
    getControls: () => controls,
    getPlan: () => plan,
    getVariant: () => variant,
    getCurrentRoot: () => currentRoot,
    getCurrentMeta: () => currentMeta,
    getActivePreset: () => activePreset,
    selectView,
    setLightingFromStudio: (nextMode, intensity) => {
      if (nextMode === 'day' || nextMode === 'dusk' || nextMode === 'night') lightingMode = nextMode;
      if (Number.isFinite(intensity)) studioLightFactor = intensity;
      applyLighting();
    },
    requestFrame,
    showToast,
  });

  film = createFilmStudio({
    scene,
    renderer,
    getCurrentRoot: () => currentRoot,
    setCamera,
    requestFrame,
    showToast,
    onFilmStateChange: (active) => {
      filmButton?.setAttribute('aria-pressed', String(active));
      clayButton?.setAttribute('aria-pressed', 'false');
    },
    onStatsUpdated: renderSceneXray,
  });

  setPresentation(presentation);
  applyLighting();

  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);

  async function loadModel(nextVariant, { preserveCamera = false, initialCam = null } = {}) {
    const seq = ++loadSeq;
    const savedPos = preserveCamera ? camera.position.clone() : null;
    const savedTarget = preserveCamera ? controls.target.clone() : null;
    const savedFloor = preserveCamera ? floor : (initialCam ? floor : 'full');

    variant = nextVariant;
    modelSelect.value = variant;
    replaceParameter('maquete', variant === 'atual' ? null : variant);
    clearInspection();
    clearMeasure();

    loading.hidden = false;
    progress.hidden = false;
    progress.value = 0;
    document.querySelector('#loading-title').textContent = `Carregando ${variantLabels[variant] ?? variant}`;
    document.querySelector('#loading-detail').textContent = '';

    try {
      const model = await loader.loadAsync(`./modelo/casa-${variant}.glb?v=${ASSET_VERSION}`, (event) => {
        if (seq !== loadSeq) return;
        if (event.lengthComputable) progress.value = 100 * event.loaded / event.total;
        if (event.lengthComputable && event.loaded === event.total) {
          document.querySelector('#loading-title').textContent = 'Preparando a cena 3D';
        }
      });
      if (seq !== loadSeq) {
        disposeObjectTree(model.scene);
        return;
      }

      // Descarta o modelo anterior antes de montar o novo.
      if (currentRoot) {
        scene.remove(currentRoot);
        disposeObjectTree(currentRoot);
        currentRoot = null;
      }
      sheetStyle?.dispose();
      sheetStyle = null;
      plan?.dispose();
      plan = null;
      layers.clear();
      wallGroups.length = 0;
      wallMeshes.length = 0;
      wallMaterials.clear();
      networks.length = 0;
      networkItems.length = 0;
      roomVariantGroups.length = 0;

      const root = model.scene.children.find((node) => node.userData.sobrado);
      if (!root) throw new Error('Metadados da cena ausentes.');
      const metadata = JSON.parse(root.userData.sobrado);
      currentRoot = root;
      currentMeta = metadata;
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

      // Atualiza seletor de pavimento da planta (adiciona/remove Ático conforme a maquete).
      const hasAtico = layers.has('atico');
      const existingAticoOpt = planFloorSelect.querySelector('[value="atico"]');
      if (hasAtico && !existingAticoOpt) {
        const opt = document.createElement('option');
        opt.value = 'atico';
        opt.textContent = 'Ático';
        planFloorSelect.append(opt);
      } else if (!hasAtico && existingAticoOpt) {
        existingAticoOpt.remove();
      }

      root.traverse((node) => {
        if (node.userData.web_exterior_walls) wallGroups.push(node);
        if (node.userData.web_network) networks.push(node);
        if (node.userData.web_room_variant) roomVariantGroups.push(node);
        if (!node.isMesh) return;
        node.receiveShadow = true;
        const materials = Array.isArray(node.material) ? node.material : [node.material];
        materials.forEach(prepareGlass);
        node.castShadow = materials.every((material) => !material.transparent);
        const parentNet = node.parent?.userData?.web_network;
        if (parentNet || node.userData.web_net_system || node.userData.web_net_node) {
          const u = node.userData;
          const isProposed = typeof u.web_net_proposed === 'boolean'
            ? u.web_net_proposed
            : (/propost|esquem[aá]tic/i.test(u.web_net_source ?? '') || ['hot', 'overflow', 'drain'].includes(parentNet));
          networkItems.push({ mesh: node, originalMaterial: node.material, isProposed });
        }
      });

      sheetStyle = createSheetStyle(root);
      plan = createPlan({
        layers, scene, variant, requestFrame,
        onMeasureUpdate: (stats) => updateMeasureReadout(stats),
        onSelectionChange: (item) => studio?.onFurnitureSelectionChange(item),
        onFurnitureChange: () => studio?.onFurnitureListChange(),
      });
      studio?.bindModel(root);
      film?.bindModel(root);
      clayButton?.setAttribute('aria-pressed', 'false');
      filmButton?.setAttribute('aria-pressed', 'false');

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

      initialRoof = variant !== 'atico' && variant !== 'estrutural';
      if (!preserveCamera) roofPreferred = initialRoof;

      document.querySelector('#wall-controls').hidden = !wallMeshes.length;
      document.querySelector('#network-controls').hidden = !networks.length;
      ceilingWrap.hidden = !layers.has('forro-terreo');
      if (metadata.networkSummary) {
        const s = metadata.networkSummary;
        document.querySelector('#network-hint').textContent =
          `${s.total} trechos (${s.documental} documentais · ${s.proposed} propostos). Clique em um trecho para detalhes.`;
      }

      // Alternador Quarto dos fundos / Escritório na Industrial.
      roomVariantOptions.innerHTML = '';
      if (metadata.roomVariants?.length) {
        roomVariantControls.hidden = false;
        activeRoomVariant = metadata.roomVariants[0].id;
        for (const rv of metadata.roomVariants) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'segment-button';
          btn.dataset.roomVariant = rv.id;
          btn.setAttribute('aria-pressed', String(rv.id === activeRoomVariant));
          btn.textContent = rv.label;
          btn.addEventListener('click', () => setRoomVariant(rv.id));
          roomVariantOptions.append(btn);
        }
      } else {
        roomVariantControls.hidden = true;
      }

      buildAtticGuides(metadata.atticGuides ?? null);
      updateLegend();

      document.querySelector('#version').textContent = metadata.version;
      document.querySelector('.cameras').hidden = !metadata.presets.length;
      document.querySelector('.roof-toggle').hidden = !layers.has('telhado');
      buildPresets(metadata.presets);

      for (const button of floorButtons) {
        if (button.dataset.floor === 'atico') button.hidden = !hasAtico;
        button.disabled = false;
      }
      for (const button of [
        overview, recenter, zoomIn, zoomOut, exportPng, copyLink, measureToggle,
        ...navigationButtons, ...orientationButtons, ...studioActionControls,
      ]) {
        button.disabled = false;
      }

      modelReady = true;
      controls.enabled = true;
      if (!preserveCamera && variant !== 'estrutural') {
        studio?.setRenovateMode(true, { silent: true });
      } else if (variant === 'estrutural') {
        studio?.setRenovateMode(false, { silent: true });
      }
      selectView(savedFloor, null, { reframe: !preserveCamera && !initialCam });
      setNavigation(navigation);
      if (preserveCamera && savedPos && savedTarget) {
        setCamera(savedPos, savedTarget);
      } else if (initialCam) {
        setCamera(new THREE.Vector3(...initialCam.slice(0, 3)), new THREE.Vector3(...initialCam.slice(3, 6)));
      }
      loading.hidden = true;
      setArrangement(arrangement);
      if (preserveCamera) showToast(`Alternado para ${variantLabels[variant]} mantendo a câmera`);
    } catch (error) {
      console.error(error);
      showFailure(`Confira se a exportação em modelo/casa-${variant}.glb está disponível e recarregue a página.`);
    }
  }

  let initialCam = null;
  const camParam = parameters.get('cam');
  if (camParam) {
    const parts = camParam.split(',').map(Number);
    if (parts.length === 6 && parts.every(Number.isFinite)) initialCam = parts;
  }

  await loadModel(variant, { preserveCamera: false, initialCam });
}

start().catch((error) => {
  console.error(error);
  showFailure('Confira se a aceleração gráfica está habilitada e tente recarregar a página.');
});
