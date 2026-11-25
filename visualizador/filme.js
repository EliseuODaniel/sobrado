import * as THREE from 'three';

export const BUILD_STAGES = [
  { id: 'base', label: 'Terreno & Base', color: '#d9a55b', hex: 0xd9a55b, foley: 'stone' },
  { id: 'terreo_estrutura', label: 'Térreo · Paredes', color: '#6cc5d9', hex: 0x6cc5d9, foley: 'stone' },
  { id: 'terreo_interior', label: 'Térreo · Mobília', color: '#8ad4b0', hex: 0x8ad4b0, foley: 'wood' },
  { id: 'superior_estrutura', label: 'Superior · Paredes', color: '#a790e8', hex: 0xa790e8, foley: 'stone' },
  { id: 'superior_interior', label: 'Superior · Suíte', color: '#eb8f78', hex: 0xeb8f78, foley: 'wood' },
  { id: 'cobertura', label: 'Ático & Cobertura', color: '#f2c968', hex: 0xf2c968, foley: 'metal' },
];

function easeOutCubic(t) {
  return 1 - Math.pow(1 - THREE.MathUtils.clamp(t, 0, 1), 3);
}

function easeInOutCubic(t) {
  const x = THREE.MathUtils.clamp(t, 0, 1);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}

// Motor de Foley procedural (Web Audio API) inspirado no "Step 10. Score It" de Nyxera0x.
function createFoleyEngine() {
  let ctx = null;
  let enabled = true;
  let lastLandAt = 0;

  function ensureContext() {
    if (!enabled) return null;
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
    }
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});
    return ctx;
  }

  function playLand(kind = 'stone') {
    const nowMs = performance.now();
    if (nowMs - lastLandAt < 48) return;
    lastLandAt = nowMs;
    const ac = ensureContext();
    if (!ac) return;
    const t = ac.currentTime;

    const osc = ac.createOscillator();
    const gain = ac.createGain();

    if (kind === 'stone') {
      osc.type = 'triangle';
      const f = 92 + Math.random() * 32;
      osc.frequency.setValueAtTime(f, t);
      osc.frequency.exponentialRampToValueAtTime(42, t + 0.08);
      gain.gain.setValueAtTime(0.09, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.09);
      osc.connect(gain).connect(ac.destination);
      osc.start(t);
      osc.stop(t + 0.095);
    } else if (kind === 'wood') {
      osc.type = 'sine';
      const f = 290 + Math.random() * 140;
      osc.frequency.setValueAtTime(f, t);
      osc.frequency.exponentialRampToValueAtTime(f * 0.62, t + 0.065);
      gain.gain.setValueAtTime(0.065, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.075);
      osc.connect(gain).connect(ac.destination);
      osc.start(t);
      osc.stop(t + 0.08);
    } else {
      // Metal / cobertura
      osc.type = 'sine';
      const f = 880 + Math.random() * 340;
      osc.frequency.setValueAtTime(f, t);
      osc.frequency.exponentialRampToValueAtTime(f * 0.85, t + 0.06);
      gain.gain.setValueAtTime(0.04, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.07);
      osc.connect(gain).connect(ac.destination);
      osc.start(t);
      osc.stop(t + 0.075);
    }
  }

  function playWaveSwell() {
    const ac = ensureContext();
    if (!ac) return;
    const t = ac.currentTime;
    const filter = ac.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(240, t);
    filter.frequency.exponentialRampToValueAtTime(2200, t + 1.15);
    filter.frequency.exponentialRampToValueAtTime(480, t + 2.8);

    const master = ac.createGain();
    master.gain.setValueAtTime(0.001, t);
    master.gain.linearRampToValueAtTime(0.075, t + 0.9);
    master.gain.exponentialRampToValueAtTime(0.001, t + 2.9);
    filter.connect(master).connect(ac.destination);

    // Acorde Cmaj9 quente na transição da onda de materiais
    const freqs = [130.81, 196.0, 246.94, 293.66, 329.63];
    for (const freq of freqs) {
      const osc = ac.createOscillator();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, t);
      osc.connect(filter);
      osc.start(t);
      osc.stop(t + 3.0);
    }
  }

  return {
    playLand,
    playWaveSwell,
    setEnabled(val) { enabled = Boolean(val); },
    isEnabled: () => enabled,
  };
}

// Classifica cada malha do GLB em uma das 6 etapas construtivas.
function classifyMeshStage(mesh, layerKey, worldCenterY) {
  if (layerKey === 'contexto') return 0;
  if (layerKey === 'telhado' || layerKey === 'atico' || layerKey === 'caixa') return 5;
  if (layerKey === 'instalacoes') return 5;

  const name = (mesh.name ?? '').toLowerCase();
  const matName = (Array.isArray(mesh.material) ? mesh.material[0]?.name : mesh.material?.name ?? '').toLowerCase();
  const isWallOrSlab = /(parede|laje|pilar|viga|fachada|reboco|cimento fino|concreto|alvenaria|muro)/.test(`${name} ${matName}`);
  const isExteriorGroup = Boolean(mesh.parent?.userData?.web_exterior_walls);

  if (layerKey === 'terreo' || layerKey === 'forro-terreo') {
    if (worldCenterY < 0.14 && /(piso|laje|terreno|concreto|paver|asfalto|grama|porcelanato)/.test(`${name} ${matName}`)) return 0;
    if (isWallOrSlab || isExteriorGroup) return 1;
    return 2;
  }
  if (layerKey === 'superior') {
    if (isWallOrSlab || isExteriorGroup) return 3;
    return 4;
  }
  if (worldCenterY > 5.2) return 5;
  if (worldCenterY > 2.55) return isWallOrSlab ? 3 : 4;
  return isWallOrSlab ? 1 : 2;
}

function getLayerKeyForNode(node) {
  let cur = node;
  while (cur) {
    if (cur.userData?.web_layer) return cur.userData.web_layer;
    cur = cur.parent;
  }
  return 'terreo';
}

export function createFilmStudio({
  scene,
  renderer,
  getCurrentRoot,
  setCamera,
  requestFrame,
  showToast,
  onFilmStateChange,
  onStatsUpdated,
}) {
  const hud = document.querySelector('#film-hud');
  const playPauseBtn = document.querySelector('#film-play-pause');
  const restartBtn = document.querySelector('#film-restart');
  const jumpWaveBtn = document.querySelector('#film-jump-wave');
  const jumpTourBtn = document.querySelector('#film-jump-tour');
  const muteBtn = document.querySelector('#film-mute');
  const exitBtn = document.querySelector('#film-exit');
  const scrubber = document.querySelector('#film-scrubber');
  const stageBadge = document.querySelector('#film-stage-badge');
  const stageDot = document.querySelector('#film-stage-dot');
  const counterEl = document.querySelector('#film-part-counter');
  const phaseLabel = document.querySelector('#film-phase-label');

  const foley = createFoleyEngine();

  // Materiais da maquete branca (White Clay) + flash por etapa
  const clayMat = new THREE.MeshStandardMaterial({
    color: 0xece9e2,
    roughness: 0.86,
    metalness: 0.02,
  });
  const clayGlassMat = new THREE.MeshPhysicalMaterial({
    color: 0xd9e8ec,
    transparent: true,
    opacity: 0.32,
    roughness: 0.25,
    depthWrite: false,
  });
  const stageFlashMats = BUILD_STAGES.map((st) => new THREE.MeshStandardMaterial({
    color: st.hex,
    emissive: st.hex,
    emissiveIntensity: 0.35,
    roughness: 0.55,
  }));

  // Grupo de overlays do filme (planta-base no chão + anel de onda de materiais)
  const filmGroup = new THREE.Group();
  filmGroup.visible = false;
  scene.add(filmGroup);

  const blueprintMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0,
    depthWrite: false,
  });
  const blueprintPlane = new THREE.Mesh(new THREE.PlaneGeometry(11.4, 13.8), blueprintMat);
  blueprintPlane.rotation.x = -Math.PI / 2;
  blueprintPlane.position.set(3.15, 0.008, -4.5);
  filmGroup.add(blueprintPlane);

  // Carrega a textura da planta arquitetônica sob demanda
  let blueprintLoaded = false;
  function ensureBlueprintTexture() {
    if (blueprintLoaded) return;
    blueprintLoaded = true;
    new THREE.TextureLoader().load('./comparacoes/planta-base-terreo.jpg?v=20261124v12', (tex) => {
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = 4;
      blueprintMat.map = tex;
      blueprintMat.needsUpdate = true;
      requestFrame();
    });
  }

  // Anel luminoso da onda de materialização
  const waveMat = new THREE.MeshBasicMaterial({
    color: 0x9bd5b9,
    transparent: true,
    opacity: 0,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const waveRing = new THREE.Mesh(new THREE.RingGeometry(0.86, 1.0, 64), waveMat);
  waveRing.rotation.x = -Math.PI / 2;
  waveRing.position.set(3.15, 0.07, -4.5);
  waveRing.visible = false;
  filmGroup.add(waveRing);

  // Curvas cinematográficas (espiral de entrada + tour interno evitando paredes vazias de perto)
  const spiralCamCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(3.15, 19.5, -4.1),   // Topo reto sobre a planta (como lente longa)
    new THREE.Vector3(10.8, 12.6, 4.4),    // Espiral descendo sobre a fachada frontal
    new THREE.Vector3(11.4, 7.6, 6.2),     // 3/4 herói acompanhando as etapas subirem
    new THREE.Vector3(-4.8, 6.8, 5.2),     // Giro suave pelo lado da sala/suíte
    new THREE.Vector3(8.8, 6.4, 6.8),      // Posição de impacto para a Onda de Materiais
  ]);
  const spiralTargetCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(3.15, 0.0, -4.5),
    new THREE.Vector3(3.15, 1.5, -4.2),
    new THREE.Vector3(3.15, 2.2, -4.2),
    new THREE.Vector3(3.15, 2.4, -4.4),
    new THREE.Vector3(3.15, 2.3, -4.2),
  ]);

  // Tour interno suave: entra pela sala, recua olhando para cozinha/jantar (nunca encara parede lisa), sobe ao pavimento superior e fecha em vista herói.
  const tourCamCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(8.8, 6.4, 6.8),      // Fim da onda
    new THREE.Vector3(3.4, 2.1, 4.8),      // Aproxima pela fachada e carros
    new THREE.Vector3(1.6, 1.65, -0.7),    // Entra na sala olhando fundo (jantar + cozinha)
    new THREE.Vector3(1.75, 1.62, -3.6),   // Avança pela sala de jantar olhando lustre e cozinha
    new THREE.Vector3(2.4, 1.68, -6.6),    // Gira olhando bar/lazer e cozinha
    new THREE.Vector3(2.1, 4.35, -2.1),    // Sobe ao pavimento superior (suíte/circulação)
    new THREE.Vector3(9.6, 7.2, 7.6),      // Recuo final cinematográfico mostrando o sobrado inteiro
  ]);
  const tourTargetCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(3.15, 2.3, -4.2),
    new THREE.Vector3(3.1, 1.8, -1.8),
    new THREE.Vector3(2.4, 1.45, -5.8),
    new THREE.Vector3(4.2, 1.45, -5.8),
    new THREE.Vector3(1.8, 1.4, -8.8),
    new THREE.Vector3(1.5, 3.85, -0.2),
    new THREE.Vector3(3.15, 2.4, -4.0),
  ]);

  let records = []; // { mesh, stage, baseY, baseVisible, origMaterial, isGlass, worldCenter, distFromCenter, startT, endT, landed }
  let sceneStats = null;
  let clayMode = false;
  let filmActive = false;
  let filmPlaying = false;
  let filmProgress = 0; // 0..1
  let lastFrameMs = 0;
  let rafId = null;
  let waveSoundPlayed = false;
  const FILM_DURATION_SEC = 24;

  // Analisa todas as malhas do modelo carregado para etapas e Raio-X de geometria
  function bindModel(root) {
    exitFilm({ silent: true });
    if (clayMode) setClayMode(false, { silent: true });
    records = [];
    sceneStats = null;
    if (!root) return;

    root.updateWorldMatrix(true, true);
    const waveOrigin = new THREE.Vector3(3.15, 0, -4.5);
    const box = new THREE.Box3();
    const center = new THREE.Vector3();
    const stageCounts = BUILD_STAGES.map(() => ({ meshes: 0, triangles: 0 }));
    const matSet = new Set();
    let totalTriangles = 0;
    const heaviest = [];

    root.traverse((node) => {
      if (!node.isMesh || !node.geometry) return;
      const layerKey = getLayerKeyForNode(node);
      box.setFromObject(node);
      box.getCenter(center);
      const stage = classifyMeshStage(node, layerKey, center.y);
      const geom = node.geometry;
      const triCount = geom.index ? Math.floor(geom.index.count / 3) : Math.floor((geom.attributes.position?.count ?? 0) / 3);
      totalTriangles += triCount;
      stageCounts[stage].meshes += 1;
      stageCounts[stage].triangles += triCount;

      const mats = Array.isArray(node.material) ? node.material : [node.material];
      mats.forEach((m) => { if (m) matSet.add(m.name || m.uuid); });
      const isGlass = mats.some((m) => m?.transparent && (m.opacity ?? 1) < 0.75);

      heaviest.push({
        name: node.name || mats[0]?.name || 'Malha',
        material: mats[0]?.name || '',
        triangles: triCount,
        stage,
      });

      records.push({
        mesh: node,
        stage,
        baseY: node.position.y,
        baseVisible: node.visible,
        origMaterial: node.material,
        isGlass,
        distFromCenter: Math.hypot(center.x - waveOrigin.x, center.z - waveOrigin.z),
        startT: 0,
        endT: 0,
        landed: false,
      });
    });

    // Organiza janelas de entrada por etapa entre t = 0.08 e t = 0.56
    const buildStart = 0.08;
    const buildSpan = 0.48;
    const stageBuckets = BUILD_STAGES.map(() => []);
    for (const r of records) stageBuckets[r.stage].push(r);

    const nonEmptyStages = stageBuckets.map((b, i) => ({ b, i })).filter(({ b }) => b.length > 0);
    const perStageSpan = buildSpan / Math.max(1, nonEmptyStages.length);

    nonEmptyStages.forEach(({ b }, idx) => {
      // Ordena da base para o topo dentro da etapa
      b.sort((a, c) => a.distFromCenter - c.distFromCenter);
      const s0 = buildStart + idx * perStageSpan;
      b.forEach((rec, j) => {
        const frac = b.length > 1 ? j / (b.length - 1) : 0;
        rec.startT = s0 + frac * perStageSpan * 0.65;
        rec.endT = Math.min(0.56, rec.startT + Math.max(0.025, perStageSpan * 0.42));
      });
    });

    heaviest.sort((a, b) => b.triangles - a.triangles);
    sceneStats = {
      totalMeshes: records.length,
      totalTriangles,
      totalMaterials: matSet.size,
      stages: BUILD_STAGES.map((st, idx) => ({
        ...st,
        meshes: stageCounts[idx].meshes,
        triangles: stageCounts[idx].triangles,
      })),
      heaviest: heaviest.slice(0, 5),
    };
    onStatsUpdated?.(sceneStats);
  }

  // Modo Maquete Branca (White Clay) fora do filme
  function setClayMode(enabled, { silent = false } = {}) {
    if (filmActive && enabled) exitFilm({ silent: true });
    clayMode = Boolean(enabled);
    for (const rec of records) {
      if (clayMode) {
        rec.origMaterial = rec.mesh.material;
        rec.mesh.material = rec.isGlass ? clayGlassMat : clayMat;
      } else if (rec.origMaterial) {
        rec.mesh.material = rec.origMaterial;
      }
    }
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
    if (!silent) showToast(clayMode ? 'Maquete branca (Argila) ativada' : 'Materiais reais restaurados');
    return clayMode;
  }

  function applyFilmFrame(t, { allowFoley = true, updateCamera = true } = {}) {
    filmProgress = THREE.MathUtils.clamp(t, 0, 1);
    if (scrubber) scrubber.value = String(Math.round(filmProgress * 1000));

    // 1. Planta-base no chão (visível no início e dissolve na onda)
    if (filmProgress < 0.56) {
      blueprintMat.opacity = Math.min(0.92, filmProgress / 0.05) * 0.92;
      blueprintPlane.visible = true;
    } else if (filmProgress < 0.70) {
      const fade = 1 - (filmProgress - 0.56) / 0.14;
      blueprintMat.opacity = Math.max(0, fade * 0.92);
      blueprintPlane.visible = fade > 0.01;
    } else {
      blueprintPlane.visible = false;
    }

    // 2. Onda de materialização (0.56 .. 0.69)
    const waveStart = 0.56;
    const waveEnd = 0.69;
    const inWave = filmProgress >= waveStart && filmProgress <= waveEnd;
    const waveNorm = THREE.MathUtils.clamp((filmProgress - waveStart) / (waveEnd - waveStart), 0, 1);
    const waveRadius = filmProgress < waveStart ? -1 : easeInOutCubic(waveNorm) * 16.5;

    if (inWave) {
      waveRing.visible = true;
      const r = Math.max(0.25, waveRadius);
      waveRing.scale.set(r, r, 1);
      waveMat.opacity = Math.sin(waveNorm * Math.PI) * 0.78;
      if (allowFoley && !waveSoundPlayed) {
        waveSoundPlayed = true;
        foley.playWaveSwell();
      }
    } else {
      waveRing.visible = false;
      if (filmProgress < waveStart) waveSoundPlayed = false;
    }

    // 3. Posicionamento, flash de etapa e transição Argila -> Material Real por malha
    let landedCount = 0;
    let activeStageIdx = 0;

    for (const rec of records) {
      if (!rec.baseVisible) {
        rec.mesh.visible = false;
        continue;
      }
      if (filmProgress < rec.startT) {
        rec.mesh.visible = false;
        rec.mesh.position.y = rec.baseY + 3.2;
        rec.landed = false;
        continue;
      }

      rec.mesh.visible = true;
      const localT = THREE.MathUtils.clamp((filmProgress - rec.startT) / Math.max(0.001, rec.endT - rec.startT), 0, 1);
      const eased = easeOutCubic(localT);
      rec.mesh.position.y = rec.baseY + (1 - eased) * 3.2;

      if (localT >= 0.98) {
        landedCount += 1;
        activeStageIdx = Math.max(activeStageIdx, rec.stage);
        if (!rec.landed) {
          rec.landed = true;
          if (allowFoley && filmProgress < waveStart) {
            foley.playLand(BUILD_STAGES[rec.stage].foley);
          }
        }
      } else {
        activeStageIdx = Math.max(activeStageIdx, rec.stage);
      }

      // Material: flash na aterrissagem -> argila branca -> onda -> material real
      const flashWindow = localT > 0.72 && localT < 1.0 && filmProgress < waveStart;
      if (waveRadius >= rec.distFromCenter) {
        rec.mesh.material = rec.origMaterial;
      } else if (flashWindow) {
        rec.mesh.material = stageFlashMats[rec.stage];
      } else {
        rec.mesh.material = rec.isGlass ? clayGlassMat : clayMat;
      }
    }

    // 4. Câmera cinematográfica (espiral + tour interno)
    if (updateCamera) {
      if (filmProgress < waveEnd) {
        const u = THREE.MathUtils.clamp(filmProgress / waveEnd, 0, 1);
        const pos = spiralCamCurve.getPoint(easeInOutCubic(u));
        const tgt = spiralTargetCurve.getPoint(easeInOutCubic(u));
        setCamera(pos, tgt);
      } else {
        const u = THREE.MathUtils.clamp((filmProgress - waveEnd) / (1 - waveEnd), 0, 1);
        const pos = tourCamCurve.getPoint(easeInOutCubic(u));
        const tgt = tourTargetCurve.getPoint(easeInOutCubic(u));
        setCamera(pos, tgt);
      }
    }

    // 5. Atualiza contador HUD ao vivo
    const visibleTotal = records.filter((r) => r.baseVisible).length;
    if (counterEl) counterEl.textContent = `${landedCount} / ${visibleTotal} peças`;
    const st = BUILD_STAGES[activeStageIdx] ?? BUILD_STAGES[0];
    if (stageDot) stageDot.style.background = st.color;

    if (filmProgress < 0.08) {
      if (phaseLabel) phaseLabel.textContent = 'Planta arquitetônica';
      if (stageBadge) stageBadge.textContent = 'Abertura sobre a planta';
    } else if (filmProgress < waveStart) {
      if (phaseLabel) phaseLabel.textContent = `Etapa ${activeStageIdx + 1}/${BUILD_STAGES.length}`;
      if (stageBadge) stageBadge.textContent = st.label;
    } else if (filmProgress < waveEnd) {
      if (phaseLabel) phaseLabel.textContent = 'Onda de materiais';
      if (stageBadge) stageBadge.textContent = 'Argila → Materiais reais';
    } else {
      if (phaseLabel) phaseLabel.textContent = 'Tour interno';
      if (stageBadge) stageBadge.textContent = 'Caminhada pelos ambientes';
    }

    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function tick(now) {
    if (!filmActive || !filmPlaying) {
      rafId = null;
      return;
    }
    const dt = Math.min(0.08, (now - (lastFrameMs || now)) / 1000);
    lastFrameMs = now;
    const nextT = filmProgress + dt / FILM_DURATION_SEC;
    if (nextT >= 1) {
      applyFilmFrame(1, { allowFoley: true, updateCamera: true });
      filmPlaying = false;
      syncPlayButton();
      rafId = null;
      showToast('Filme concluído! Use o controle de linha do tempo ou saia para explorar livremente.');
      return;
    }
    applyFilmFrame(nextT, { allowFoley: true, updateCamera: true });
    rafId = requestAnimationFrame(tick);
  }

  function syncPlayButton() {
    if (playPauseBtn) playPauseBtn.textContent = filmPlaying ? '⏸ Pausar' : '▶ Reproduzir';
    if (muteBtn) {
      const on = foley.isEnabled();
      muteBtn.textContent = on ? '🔊 Som' : '🔇 Mudo';
      muteBtn.setAttribute('aria-pressed', String(on));
    }
  }

  function startFilm() {
    const root = getCurrentRoot();
    if (!root || !records.length) return;
    if (clayMode) setClayMode(false, { silent: true });

    // Captura estado atual (materiais personalizados e visibilidade de cada camada)
    for (const rec of records) {
      rec.baseY = rec.mesh.position.y;
      rec.baseVisible = rec.mesh.visible;
      rec.origMaterial = rec.mesh.material;
      rec.landed = false;
    }

    ensureBlueprintTexture();
    filmActive = true;
    filmPlaying = true;
    filmProgress = 0;
    waveSoundPlayed = false;
    filmGroup.visible = true;
    if (hud) hud.hidden = false;
    document.body.dataset.film = 'active';
    onFilmStateChange?.(true);
    syncPlayButton();
    applyFilmFrame(0, { allowFoley: false, updateCamera: true });
    lastFrameMs = performance.now();
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }

  function exitFilm({ silent = false } = {}) {
    if (!filmActive) return;
    filmActive = false;
    filmPlaying = false;
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    filmGroup.visible = false;
    waveRing.visible = false;
    if (hud) hud.hidden = true;
    delete document.body.dataset.film;

    for (const rec of records) {
      rec.mesh.position.y = rec.baseY;
      rec.mesh.visible = rec.baseVisible;
      rec.mesh.material = rec.origMaterial;
      rec.landed = false;
    }
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
    onFilmStateChange?.(false);
    if (!silent) showToast('Modo Construção / Filme encerrado');
  }

  // Eventos dos controles do HUD do Filme
  playPauseBtn?.addEventListener('click', () => {
    if (!filmActive) { startFilm(); return; }
    if (filmProgress >= 0.995) filmProgress = 0;
    filmPlaying = !filmPlaying;
    syncPlayButton();
    if (filmPlaying) {
      lastFrameMs = performance.now();
      rafId = requestAnimationFrame(tick);
    }
  });
  restartBtn?.addEventListener('click', () => {
    if (!filmActive) { startFilm(); return; }
    waveSoundPlayed = false;
    for (const r of records) r.landed = false;
    filmPlaying = true;
    syncPlayButton();
    applyFilmFrame(0, { allowFoley: false, updateCamera: true });
    lastFrameMs = performance.now();
    if (!rafId) rafId = requestAnimationFrame(tick);
  });
  jumpWaveBtn?.addEventListener('click', () => {
    if (!filmActive) return;
    waveSoundPlayed = false;
    filmPlaying = true;
    syncPlayButton();
    applyFilmFrame(0.555, { allowFoley: false, updateCamera: true });
    lastFrameMs = performance.now();
    if (!rafId) rafId = requestAnimationFrame(tick);
  });
  jumpTourBtn?.addEventListener('click', () => {
    if (!filmActive) return;
    filmPlaying = true;
    syncPlayButton();
    applyFilmFrame(0.695, { allowFoley: false, updateCamera: true });
    lastFrameMs = performance.now();
    if (!rafId) rafId = requestAnimationFrame(tick);
  });
  scrubber?.addEventListener('input', () => {
    if (!filmActive) return;
    filmPlaying = false;
    syncPlayButton();
    applyFilmFrame(Number(scrubber.value) / 1000, { allowFoley: false, updateCamera: true });
  });
  muteBtn?.addEventListener('click', () => {
    foley.setEnabled(!foley.isEnabled());
    syncPlayButton();
  });
  exitBtn?.addEventListener('click', () => exitFilm());

  // Esc também sai do modo filme
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && filmActive) exitFilm();
  });

  return {
    bindModel,
    startFilm,
    exitFilm,
    isFilmActive: () => filmActive,
    setClayMode,
    isClayMode: () => clayMode,
    getSceneStats: () => sceneStats,
    pauseCameraOnUserDrag() {
      if (filmActive && filmPlaying) {
        filmPlaying = false;
        syncPlayButton();
      }
    },
  };
}
