import * as THREE from 'three';
import { floorElevation, furnitureCatalog } from './planta.js?v=20261124v13';

// Catálogo de ambientes com áreas estimadas (m²), foco de câmera, pavimento e sugestões contextuais.
export const ROOM_SCOPES = [
  {
    id: 'whole', label: 'Casa inteira', area: '98 m²', floor: 'full',
    center: [3.15, 0, -4.6], walkPos: [1.65, 1.62, -0.8], walkTarget: [1.8, 1.55, -4.8],
    chips: [
      'Minimalista quente',
      'Escuro e aconchegante',
      'Piso nogueira em tudo',
      'Paredes verde sálvia',
      'Escandinavo claro',
      'Mobiliar sala com travertino',
    ],
  },
  {
    id: 'sala', label: 'Sala de estar', area: '16 m²', floor: 'terreo',
    bounds: { minX: 0.2, maxX: 3.3, minZ: -3.6, maxZ: -0.2 },
    center: [1.65, 0, -1.7], walkPos: [1.55, 1.62, -0.55], walkTarget: [1.75, 1.48, -3.5],
    compareKey: 'sala',
    chips: [
      'Estilo Mid-Century',
      'Paredes verde sálvia',
      'Sofá couro caramelo',
      'Adicionar mesa travertino',
      'Adicionar tapete e planta',
      'Reorganizar sala',
    ],
  },
  {
    id: 'jantar', label: 'Sala de jantar', area: '10 m²', floor: 'terreo',
    bounds: { minX: 0.2, maxX: 3.3, minZ: -6.2, maxZ: -3.4 },
    center: [1.65, 0, -4.7], walkPos: [1.65, 1.62, -3.1], walkTarget: [1.65, 1.4, -6.0],
    compareKey: 'sala',
    chips: [
      'Madeira carvalho quente',
      'Paredes areia quente',
      'Adicionar aparador',
      'Adicionar luminária piso',
    ],
  },
  {
    id: 'cozinha', label: 'Cozinha', area: '11 m²', floor: 'terreo',
    bounds: { minX: 3.4, maxX: 6.1, minZ: -7.2, maxZ: -4.1 },
    center: [4.85, 0, -5.6], walkPos: [3.75, 1.62, -4.55], walkTarget: [5.4, 1.4, -6.2],
    compareKey: 'cozinha',
    chips: [
      'Armários verde oliva',
      'Armários grafite fosco',
      'Bancada mármore branco',
      'Ripado carvalho claro',
      'Cozinha off-white',
    ],
  },
  {
    id: 'bar', label: 'Bar / Lazer', area: '12 m²', floor: 'terreo',
    bounds: { minX: 0.2, maxX: 3.3, minZ: -9.8, maxZ: -6.8 },
    center: [1.65, 0, -8.3], walkPos: [1.7, 1.62, -6.9], walkTarget: [1.65, 1.45, -9.5],
    compareKey: 'bar',
    chips: [
      'Clima bar noturno',
      'Pedra escura e nogueira',
      'Adicionar poltrona',
      'Adicionar planta',
    ],
  },
  {
    id: 'lavanderia', label: 'Lavanderia', area: '6 m²', floor: 'terreo',
    bounds: { minX: 3.4, maxX: 6.1, minZ: -9.8, maxZ: -7.4 },
    center: [4.9, 0, -8.9], walkPos: [4.1, 1.62, -7.8], walkTarget: [5.3, 1.4, -9.5],
    compareKey: 'lavanderia',
    chips: [
      'Branco clean',
      'Armários grafite',
      'Piso cimento queimado',
    ],
  },
  {
    id: 'suite', label: 'Suíte casal', area: '14 m²', floor: 'superior',
    bounds: { minX: 0.2, maxX: 3.3, minZ: -3.5, maxZ: 0.8 },
    center: [1.7, 2.7, -1.2], walkPos: [2.6, 4.32, -2.5], walkTarget: [1.1, 4.0, -0.4],
    compareKey: 'suite',
    chips: [
      'Suíte Japandi areia',
      'Paredes verde musgo',
      'Piso nogueira',
      'Enxoval linho terracota',
      'Adicionar poltrona',
    ],
  },
  {
    id: 'quarto-frente', label: 'Quarto frente', area: '9 m²', floor: 'superior',
    bounds: { minX: 3.4, maxX: 6.1, minZ: -2.6, maxZ: 1.0 },
    center: [4.85, 2.7, -0.5], walkPos: [4.0, 4.32, -1.9], walkTarget: [5.2, 4.05, 0.4],
    compareKey: 'quarto-frente',
    chips: [
      'Parede azul petróleo',
      'Parede terracota suave',
      'Adicionar escrivaninha',
      'Piso laminado claro',
    ],
  },
  {
    id: 'quarto-fundos', label: 'Quarto fundos', area: '10 m²', floor: 'superior',
    bounds: { minX: 3.4, maxX: 6.1, minZ: -7.0, maxZ: -3.8 },
    center: [4.85, 2.7, -5.4], walkPos: [4.1, 4.32, -4.1], walkTarget: [5.3, 4.05, -6.4],
    compareKey: 'quarto-fundos',
    chips: [
      'Home office escandinavo',
      'Parede verde sálvia',
      'Adicionar escrivaninha',
      'Adicionar luminária piso',
    ],
  },
  {
    id: 'banheiros', label: 'Banheiros', area: '7 m²', floor: 'superior',
    bounds: { minX: 0.2, maxX: 3.3, minZ: -6.2, maxZ: -3.6 },
    center: [1.7, 2.7, -4.8], walkPos: [2.55, 4.32, -3.9], walkTarget: [2.55, 4.05, -5.6],
    compareKey: 'banheiro-social',
    chips: [
      'Bancada travertino',
      'Metais dourado latão',
      'Cimento queimado claro',
    ],
  },
  {
    id: 'fachada', label: 'Fachada externa', area: 'Externa', floor: 'full',
    center: [3.15, 2.5, 1.5], walkPos: [3.15, 1.65, 7.2], walkTarget: [3.15, 2.6, 0],
    compareKey: 'fachada',
    chips: [
      'Fachada cinza grafite',
      'Fachada areia mediterrânea',
      'Fachada off-white',
      'Esquadrias bronze',
    ],
  },
];

// Grupos semânticos de superfícies editáveis diretamente no 3D.
export const SURFACE_SLOTS = {
  walls: { label: 'Paredes internas', short: 'Paredes' },
  accentWall: { label: 'Parede destaque / TV', short: 'Destaque' },
  floorMain: { label: 'Piso principal (Térreo)', short: 'Piso térreo' },
  floorWood: { label: 'Piso dos quartos', short: 'Piso quartos' },
  wood: { label: 'Madeira / Ripado', short: 'Madeira' },
  cabinets: { label: 'Armários / Cozinha', short: 'Armários' },
  counters: { label: 'Bancadas / Pedras', short: 'Bancadas' },
  upholstery: { label: 'Estofados / Tecidos', short: 'Estofados' },
  facade: { label: 'Fachada externa', short: 'Fachada' },
  metal: { label: 'Metais / Esquadrias', short: 'Metais' },
};

// Paletas arquitetônicas curadas por tipo de superfície.
export const SLOT_SWATCHES = {
  walls: [
    { name: 'Off-white quente', color: '#ede7dc', roughness: 0.88, pattern: 'paint' },
    { name: 'Verde sálvia', color: '#8ea08c', roughness: 0.88, pattern: 'paint' },
    { name: 'Areia linho', color: '#d7cab8', roughness: 0.88, pattern: 'paint' },
    { name: 'Cimento queimado', color: '#9a9b98', roughness: 0.82, pattern: 'concrete' },
    { name: 'Grafite suave', color: '#454a4d', roughness: 0.86, pattern: 'paint' },
    { name: 'Terracota claro', color: '#c4866b', roughness: 0.88, pattern: 'paint' },
    { name: 'Azul nórdico', color: '#6e8494', roughness: 0.88, pattern: 'paint' },
    { name: 'Branco neve', color: '#f3f4f2', roughness: 0.86, pattern: 'paint' },
  ],
  accentWall: [
    { name: 'Verde musgo escuro', color: '#3b4f44', roughness: 0.86, pattern: 'paint' },
    { name: 'Verde sálvia', color: '#7c917b', roughness: 0.86, pattern: 'paint' },
    { name: 'Petróleo mineral', color: '#2f4b56', roughness: 0.84, pattern: 'paint' },
    { name: 'Terracota', color: '#b06449', roughness: 0.86, pattern: 'paint' },
    { name: 'Cimento grafite', color: '#505456', roughness: 0.80, pattern: 'concrete' },
    { name: 'Taupe quente', color: '#9c8f81', roughness: 0.86, pattern: 'paint' },
    { name: 'Travertino claro', color: '#d9cfc0', roughness: 0.68, pattern: 'travertine' },
  ],
  floorMain: [
    { name: 'Porcelanato areia', color: '#d6ccb9', roughness: 0.34, pattern: 'tile' },
    { name: 'Nogueira americana', color: '#6b4a33', roughness: 0.56, pattern: 'wood' },
    { name: 'Carvalho natural', color: '#b99368', roughness: 0.54, pattern: 'wood' },
    { name: 'Cimento queimado', color: '#8f918d', roughness: 0.62, pattern: 'concrete' },
    { name: 'Mármore carrara', color: '#e6e4df', roughness: 0.24, pattern: 'marble' },
    { name: 'Bétula clara', color: '#d9c5a7', roughness: 0.56, pattern: 'wood' },
  ],
  floorWood: [
    { name: 'Carvalho natural', color: '#ba9469', roughness: 0.56, pattern: 'wood' },
    { name: 'Nogueira escura', color: '#5f402c', roughness: 0.56, pattern: 'wood' },
    { name: 'Bétula escandinava', color: '#d8c5a8', roughness: 0.58, pattern: 'wood' },
    { name: 'Freijó mel', color: '#a57548', roughness: 0.54, pattern: 'wood' },
    { name: 'Cimento claro', color: '#a7a7a1', roughness: 0.68, pattern: 'concrete' },
  ],
  wood: [
    { name: 'Carvalho quente', color: '#b48758', roughness: 0.56, pattern: 'wood' },
    { name: 'Nogueira', color: '#5d3e2a', roughness: 0.58, pattern: 'wood' },
    { name: 'Freijó mel', color: '#9f6e40', roughness: 0.54, pattern: 'wood' },
    { name: 'Bétula clara', color: '#d6c1a2', roughness: 0.60, pattern: 'wood' },
    { name: 'Ébano fosco', color: '#2b2826', roughness: 0.62, pattern: 'wood' },
  ],
  cabinets: [
    { name: 'Grafite fosco', color: '#393e41', roughness: 0.48, pattern: 'paint' },
    { name: 'Verde oliva', color: '#566552', roughness: 0.50, pattern: 'paint' },
    { name: 'Off-white laqueado', color: '#ebe6dc', roughness: 0.36, pattern: 'paint' },
    { name: 'Azul petróleo', color: '#37515c', roughness: 0.48, pattern: 'paint' },
    { name: 'Carvalho natural', color: '#b4885c', roughness: 0.56, pattern: 'wood' },
    { name: 'Areia fendi', color: '#b4aa9a', roughness: 0.46, pattern: 'paint' },
  ],
  counters: [
    { name: 'Granito preto', color: '#232527', roughness: 0.24, pattern: 'marble' },
    { name: 'Mármore branco', color: '#ebe9e4', roughness: 0.22, pattern: 'marble' },
    { name: 'Travertino romano', color: '#d7ccbb', roughness: 0.54, pattern: 'travertine' },
    { name: 'Quartzo cinza', color: '#8f9395', roughness: 0.30, pattern: 'concrete' },
  ],
  upholstery: [
    { name: 'Couro caramelo', color: '#9e5e38', roughness: 0.52, pattern: 'linen' },
    { name: 'Linho off-white', color: '#e1d9cb', roughness: 0.90, pattern: 'linen' },
    { name: 'Veludo verde musgo', color: '#4c6352', roughness: 0.88, pattern: 'linen' },
    { name: 'Cinza grafite', color: '#4d5256', roughness: 0.88, pattern: 'linen' },
    { name: 'Terracota', color: '#b26b52', roughness: 0.88, pattern: 'linen' },
    { name: 'Azul marinho', color: '#34495e', roughness: 0.88, pattern: 'linen' },
  ],
  facade: [
    { name: 'Bege areia', color: '#d4c8b6', roughness: 0.88, pattern: 'paint' },
    { name: 'Cinza grafite', color: '#464b4e', roughness: 0.86, pattern: 'concrete' },
    { name: 'Off-white', color: '#ece9e1', roughness: 0.86, pattern: 'paint' },
    { name: 'Cimento aparente', color: '#8f918d', roughness: 0.84, pattern: 'concrete' },
    { name: 'Terracota suave', color: '#bd856b', roughness: 0.88, pattern: 'paint' },
  ],
  metal: [
    { name: 'Preto fosco', color: '#222426', roughness: 0.38, metalness: 0.75, pattern: 'paint' },
    { name: 'Latão dourado', color: '#c49d56', roughness: 0.28, metalness: 0.85, pattern: 'paint' },
    { name: 'Bronze escovado', color: '#6b5340', roughness: 0.34, metalness: 0.78, pattern: 'paint' },
    { name: 'Aço inox', color: '#c7cdd1', roughness: 0.26, metalness: 0.85, pattern: 'paint' },
  ],
};

// Presets completos de estilo arquitetônico (como o dropdown Custom / Style do vídeo).
export const STYLE_PRESETS = {
  original: {
    id: 'original',
    label: 'Original (Maquete)',
    description: 'Acabamentos originais da maquete exportada',
    overrides: {},
    lighting: { mode: 'day', intensity: 1.0 },
  },
  'warm-minimal': {
    id: 'warm-minimal',
    label: 'Minimalista quente',
    description: 'Paredes off-white quentes, carvalho natural, linho areia e travertino',
    overrides: {
      walls: { color: '#eee8de', roughness: 0.88, pattern: 'paint', name: 'Off-white quente' },
      accentWall: { color: '#d9cfc0', roughness: 0.78, pattern: 'travertine', name: 'Travertino claro' },
      floorMain: { color: '#d7ccb9', roughness: 0.38, pattern: 'tile', name: 'Porcelanato areia' },
      floorWood: { color: '#c4a27b', roughness: 0.56, pattern: 'wood', name: 'Carvalho natural' },
      wood: { color: '#ba9062', roughness: 0.56, pattern: 'wood', name: 'Carvalho quente' },
      cabinets: { color: '#e5dfd3', roughness: 0.42, pattern: 'paint', name: 'Off-white fosco' },
      counters: { color: '#dfd6c7', roughness: 0.46, pattern: 'travertine', name: 'Travertino' },
      upholstery: { color: '#dfd7c8', roughness: 0.90, pattern: 'linen', name: 'Linho natural' },
      facade: { color: '#e8e2d7', roughness: 0.86, pattern: 'paint', name: 'Off-white areia' },
      metal: { color: '#5e4c3d', roughness: 0.35, metalness: 0.75, pattern: 'paint', name: 'Bronze fosco' },
    },
    lighting: { mode: 'day', intensity: 1.08 },
  },
  'dark-moody': {
    id: 'dark-moody',
    label: 'Escuro & aconchegante',
    description: 'Paredes verde-carvão profundas, piso nogueira, couro caramelo e luz quente',
    overrides: {
      walls: { color: '#3b413f', roughness: 0.88, pattern: 'paint', name: 'Carvão mineral' },
      accentWall: { color: '#2b3b34', roughness: 0.84, pattern: 'paint', name: 'Verde floresta' },
      floorMain: { color: '#5f412d', roughness: 0.54, pattern: 'wood', name: 'Nogueira escura' },
      floorWood: { color: '#573a27', roughness: 0.56, pattern: 'wood', name: 'Nogueira escura' },
      wood: { color: '#61412b', roughness: 0.54, pattern: 'wood', name: 'Nogueira' },
      cabinets: { color: '#2c3033', roughness: 0.48, pattern: 'paint', name: 'Grafite profundo' },
      counters: { color: '#1f2123', roughness: 0.24, pattern: 'marble', name: 'Granito nero' },
      upholstery: { color: '#9c5c36', roughness: 0.54, pattern: 'linen', name: 'Couro caramelo' },
      facade: { color: '#3f4447', roughness: 0.86, pattern: 'concrete', name: 'Grafite fosco' },
      metal: { color: '#c49d56', roughness: 0.28, metalness: 0.85, pattern: 'paint', name: 'Latão dourado' },
    },
    lighting: { mode: 'night', intensity: 1.15 },
  },
  scandi: {
    id: 'scandi',
    label: 'Escandinavo claro',
    description: 'Branco neve luminoso, piso bétula clara, madeira clara e toques verde sálvia',
    overrides: {
      walls: { color: '#f2f3f0', roughness: 0.86, pattern: 'paint', name: 'Branco neve' },
      accentWall: { color: '#96a895', roughness: 0.86, pattern: 'paint', name: 'Verde sálvia' },
      floorMain: { color: '#dccab0', roughness: 0.56, pattern: 'wood', name: 'Bétula clara' },
      floorWood: { color: '#decbb2', roughness: 0.56, pattern: 'wood', name: 'Bétula clara' },
      wood: { color: '#d4be9e', roughness: 0.58, pattern: 'wood', name: 'Bétula natural' },
      cabinets: { color: '#e6e8e4', roughness: 0.42, pattern: 'paint', name: 'Gelo fosco' },
      counters: { color: '#eceae5', roughness: 0.24, pattern: 'marble', name: 'Mármore branco' },
      upholstery: { color: '#cdd3ce', roughness: 0.90, pattern: 'linen', name: 'Linho cinza claro' },
      facade: { color: '#eef0ed', roughness: 0.86, pattern: 'paint', name: 'Branco nórdico' },
      metal: { color: '#2b2e30', roughness: 0.42, metalness: 0.68, pattern: 'paint', name: 'Preto fosco' },
    },
    lighting: { mode: 'day', intensity: 1.16 },
  },
  'mid-century': {
    id: 'mid-century',
    label: 'Mid-Century Moderno',
    description: 'Verde sálvia, nogueira quente, sofá caramelo e detalhes em latão',
    overrides: {
      walls: { color: '#ece5d6', roughness: 0.88, pattern: 'paint', name: 'Creme retrô' },
      accentWall: { color: '#6b826d', roughness: 0.86, pattern: 'paint', name: 'Verde sálvia médio' },
      floorMain: { color: '#785236', roughness: 0.52, pattern: 'wood', name: 'Teca / Nogueira' },
      floorWood: { color: '#785236', roughness: 0.54, pattern: 'wood', name: 'Teca / Nogueira' },
      wood: { color: '#8b5732', roughness: 0.52, pattern: 'wood', name: 'Teca quente' },
      cabinets: { color: '#4d6152', roughness: 0.50, pattern: 'paint', name: 'Verde oliva' },
      counters: { color: '#e2d9c9', roughness: 0.44, pattern: 'travertine', name: 'Travertino' },
      upholstery: { color: '#a86037', roughness: 0.56, pattern: 'linen', name: 'Couro conhaque' },
      facade: { color: '#dad0be', roughness: 0.88, pattern: 'paint', name: 'Areia cálida' },
      metal: { color: '#c8a054', roughness: 0.26, metalness: 0.85, pattern: 'paint', name: 'Latão escovado' },
    },
    lighting: { mode: 'day', intensity: 1.04 },
  },
  industrial: {
    id: 'industrial',
    label: 'Industrial urbano',
    description: 'Cimento queimado, aço preto fosco, carvalho rústico e granito escuro',
    overrides: {
      walls: { color: '#9c9e9a', roughness: 0.84, pattern: 'concrete', name: 'Cimento queimado' },
      accentWall: { color: '#4c5154', roughness: 0.82, pattern: 'concrete', name: 'Concreto grafite' },
      floorMain: { color: '#868986', roughness: 0.56, pattern: 'concrete', name: 'Cimento acetinado' },
      floorWood: { color: '#96704c', roughness: 0.58, pattern: 'wood', name: 'Carvalho demolição' },
      wood: { color: '#986d45', roughness: 0.56, pattern: 'wood', name: 'Carvalho rústico' },
      cabinets: { color: '#34393c', roughness: 0.46, pattern: 'paint', name: 'Grafite acetinado' },
      counters: { color: '#26282a', roughness: 0.26, pattern: 'marble', name: 'Granito escuro' },
      upholstery: { color: '#8d5634', roughness: 0.55, pattern: 'linen', name: 'Couro envelhecido' },
      facade: { color: '#6b7072', roughness: 0.86, pattern: 'concrete', name: 'Concreto aparente' },
      metal: { color: '#1d1f21', roughness: 0.36, metalness: 0.82, pattern: 'paint', name: 'Aço preto' },
    },
    lighting: { mode: 'day', intensity: 0.98 },
  },
  japandi: {
    id: 'japandi',
    label: 'Japandi',
    description: 'Areia mineral, freijó claro, tecidos crus e serenidade orgânica',
    overrides: {
      walls: { color: '#e4ddd0', roughness: 0.90, pattern: 'paint', name: 'Argila clara' },
      accentWall: { color: '#bfb4a2', roughness: 0.86, pattern: 'travertine', name: 'Areia mineral' },
      floorMain: { color: '#cab89e', roughness: 0.58, pattern: 'wood', name: 'Freijó pálido' },
      floorWood: { color: '#cab89e', roughness: 0.58, pattern: 'wood', name: 'Freijó pálido' },
      wood: { color: '#b4946c', roughness: 0.58, pattern: 'wood', name: 'Freijó natural' },
      cabinets: { color: '#bfb5a5', roughness: 0.54, pattern: 'paint', name: 'Fendi fosco' },
      counters: { color: '#dad1c2', roughness: 0.52, pattern: 'travertine', name: 'Pedra calcária' },
      upholstery: { color: '#d7cfc1', roughness: 0.92, pattern: 'linen', name: 'Bouclé cru' },
      facade: { color: '#d8cfc0', roughness: 0.88, pattern: 'paint', name: 'Calcário claro' },
      metal: { color: '#33312e', roughness: 0.42, metalness: 0.65, pattern: 'paint', name: 'Ferro fosco' },
    },
    lighting: { mode: 'day', intensity: 1.06 },
  },
  mediterranean: {
    id: 'mediterranean',
    label: 'Mediterrâneo',
    description: 'Reboco solar claro, terracota acolhedora, pedra calcária e oliva',
    overrides: {
      walls: { color: '#f1eadf', roughness: 0.90, pattern: 'paint', name: 'Cal solar' },
      accentWall: { color: '#bd7c60', roughness: 0.88, pattern: 'paint', name: 'Terracota solar' },
      floorMain: { color: '#dfd2bc', roughness: 0.48, pattern: 'travertine', name: 'Pedra calcária' },
      floorWood: { color: '#b88f64', roughness: 0.56, pattern: 'wood', name: 'Carvalho solar' },
      wood: { color: '#a8784d', roughness: 0.58, pattern: 'wood', name: 'Madeira lavada' },
      cabinets: { color: '#697861', roughness: 0.54, pattern: 'paint', name: 'Verde oliveira' },
      counters: { color: '#e6dccb', roughness: 0.46, pattern: 'travertine', name: 'Travertino' },
      upholstery: { color: '#e5ddd0', roughness: 0.90, pattern: 'linen', name: 'Linho lavado' },
      facade: { color: '#eadfcf', roughness: 0.90, pattern: 'paint', name: 'Reboco bege claro' },
      metal: { color: '#6e5642', roughness: 0.36, metalness: 0.72, pattern: 'paint', name: 'Bronze antigo' },
    },
    lighting: { mode: 'day', intensity: 1.14 },
  },
};

// Mapeamento de ambientes para imagens comparativas (renders + fotos reais em ./comparacoes/).
export const COMPARISON_ROOMS = [
  { id: 'sala', label: 'Sala de estar', presetHints: ['sala'], atual: 'atual-sala.jpg', industrial: 'industrial-sala.jpg', real: 'real-sala.jpg' },
  { id: 'cozinha', label: 'Cozinha', presetHints: ['cozinha'], atual: 'atual-cozinha.jpg', industrial: 'industrial-cozinha.jpg', real: 'real-cozinha.jpg' },
  { id: 'bar', label: 'Bar / Lazer', presetHints: ['bar', 'lazer', 'fundos'], atual: 'atual-bar.jpg', industrial: 'industrial-bar.jpg', real: 'real-bar.jpg' },
  { id: 'lavanderia', label: 'Lavanderia', presetHints: ['lavanderia'], atual: 'atual-lavanderia.jpg', industrial: 'industrial-lavanderia.jpg', real: 'real-lavanderia.jpg' },
  { id: 'lavabo', label: 'Lavabo', presetHints: ['lavabo'], atual: 'atual-lavabo.jpg', industrial: 'industrial-lavabo.jpg', real: 'real-lavabo.jpg' },
  { id: 'suite', label: 'Suíte casal', presetHints: ['suite'], atual: 'atual-suite.jpg', industrial: 'industrial-suite.jpg', real: 'real-suite.jpg' },
  { id: 'quarto-frente', label: 'Quarto frente', presetHints: ['quarto-frente', 'azul'], atual: 'atual-quarto-frente.jpg', industrial: 'industrial-quarto-frente.jpg', real: 'real-quarto-frente.jpg' },
  { id: 'quarto-fundos', label: 'Quarto fundos', presetHints: ['quarto-fundos', 'branco', 'escritorio'], atual: 'atual-quarto-fundos.jpg', industrial: 'industrial-quarto-fundos.jpg', real: 'real-quarto-fundos.jpg' },
  { id: 'banheiro-social', label: 'Banheiro social', presetHints: ['banheiro'], atual: 'atual-banheiro-social.jpg', industrial: null, real: 'real-banheiro-social.jpg' },
  { id: 'fachada', label: 'Fachada frontal', presetHints: ['fachada', 'volumetria', 'geral'], atual: 'atual-fachada.jpg', industrial: null, real: 'real-fachada.jpg' },
];

// Paleta de substituição rápida por categoria de móvel selecionado (como os chips de objeto do vídeo).
const OBJECT_SWAP_CHIPS = {
  coffee_table: [
    { label: 'Mesa redonda travertino', patch: { type: 'coffee_round', color: 0xd9cfc1, label: 'Mesa redonda travertino' } },
    { label: 'Mesa carvalho c/ livros', patch: { type: 'coffee_oak', color: 0xb68a5c, label: 'Mesa centro carvalho' } },
    { label: 'Vidro com pés latão', patch: { type: 'coffee_glass', color: 0xc59d52, label: 'Mesa vidro e latão' } },
    { label: 'Nogueira escura', patch: { color: 0x5d3e2a } },
  ],
  seating: [
    { label: 'Couro caramelo', patch: { color: 0xa45e37 } },
    { label: 'Linho off-white', patch: { color: 0xe3dbd0 } },
    { label: 'Veludo verde musgo', patch: { color: 0x4b6251 } },
    { label: 'Trocar por poltrona', patch: { type: 'armchair' } },
    { label: 'Trocar por sofá', patch: { type: 'sofa' } },
  ],
  table: [
    { label: 'Carvalho quente', patch: { color: 0xb68a5c } },
    { label: 'Nogueira escura', patch: { color: 0x5e3f2b } },
    { label: 'Travertino claro', patch: { color: 0xd9cfc1 } },
    { label: 'Trocar por escrivaninha', patch: { type: 'desk' } },
    { label: 'Trocar por mesa jantar', patch: { type: 'table' } },
  ],
  bed: [
    { label: 'Linho areia', patch: { color: 0xd4c9b8 } },
    { label: 'Cinza acolchoado', patch: { color: 0x767c80 } },
    { label: 'Terracota suave', patch: { color: 0xb5755c } },
    { label: 'Cama casal', patch: { type: 'bed' } },
    { label: 'Cama solteiro', patch: { type: 'single_bed' } },
  ],
  default: [
    { label: 'Carvalho quente', patch: { color: 0xb68a5c } },
    { label: 'Travertino', patch: { color: 0xd9cfc1 } },
    { label: 'Verde sálvia', patch: { color: 0x7d927c } },
    { label: 'Grafite fosco', patch: { color: 0x3b4043 } },
    { label: 'Couro caramelo', patch: { color: 0xa45e37 } },
  ],
};

// Classificação semântica dos materiais reais dos GLBs do Sobrado.
function classifyMaterial(matName = '') {
  const n = matName.toLowerCase();
  if (!n) return null;
  if (/(vidro|espelho|led|luz|tela|interface|agua|borracha|asfalto|grama|terra|paver|telha|louca|orquidea|petala|garganta|miolo|folha|potted_plant|calathea|caixa)/.test(n)) {
    return null;
  }
  if (/(fachada)/.test(n)) return 'facade';
  if (/(parede tv|azul parede|taupe|papel|petroleo|pedra oxidada)/.test(n)) return 'accentWall';
  if (/(parede|reboco|cimento fino|teto fosco|drywall|branco fosco|^branco$|^atual branco)/.test(n)) return 'walls';
  if (/(laminado|atc madeira)/.test(n)) return 'floorWood';
  if (/(porcelanato|piso|ceramica creme|fiel2 ceramica)/.test(n)) return 'floorMain';
  if (/(cozinha|grafite|laqueado)/.test(n)) return 'cabinets';
  if (/(granito|travertino|pedra|mosaico|azulejo)/.test(n)) return 'counters';
  if (/(sofa|cadeiras tecido|cabeceira|colcha|cortina|tecido|linho|couro|costura|tapete)/.test(n)) return 'upholstery';
  if (/(madeira|carvalho|ripado)/.test(n)) return 'wood';
  if (/(metal|aco|aço|preto|inox|cromado|ouro)/.test(n)) return 'metal';
  return null;
}

// Materiais que pertencem exclusivamente a móveis/decoração solta (ocultáveis no modo "Vazio").
function isMovableDecorMaterial(matName = '') {
  const n = matName.toLowerCase();
  return /(sofa|cadeiras|colcha|cabeceira|cortina|tecido|linho|couro|costura|tapete|tela|interface|folha|orquidea|petala|garganta|miolo|potted_plant|calathea|vidro fumê mesa|vidro mesa|ouro pendente|cerâmica preta)/.test(n);
}

// Mapeamento fino de materiais exclusivos de ambientes específicos (quando o escopo é um ambiente).
function materialBelongsToRoom(matName = '', roomId = 'whole') {
  if (roomId === 'whole') return true;
  const n = matName.toLowerCase();
  const roomMatchers = {
    sala: /(parede tv|sofa|porcelanato|parede branco|cimento fino|madeira mel|carvalho|vidro fumê mesa|linho|couro|tapete)/,
    jantar: /(cadeiras|vidro mesa|porcelanato|parede branco|cimento fino|madeira|carvalho|ouro pendente)/,
    cozinha: /(cozinha|granito|grafite|porcelanato|parede branco|cimento fino|madeira mel|carvalho|azulejo|branco laqueado)/,
    bar: /(pedra bar|pedra mosaico|madeira bar|porcelanato|parede branco|cimento fino|carvalho|grafite)/,
    lavanderia: /(porcelanato|granito|azulejo|parede branco|cimento fino|cozinha|grafite)/,
    suite: /(suite|colcha|cabeceira|laminado|parede branco|cimento fino|madeira suite|carvalho|linho|cortina)/,
    'quarto-frente': /(azul parede|papel geometrico|laminado|parede branco|cimento fino|carvalho|branco laqueado)/,
    'quarto-fundos': /(papel coracoes|laminado|parede branco|cimento fino|carvalho|branco laqueado|linho)/,
    banheiros: /(banho|azulejo|travertino|granito|ceramica|metal|cromado|ouro|cimento fino|parede branco)/,
    fachada: /(fachada|concreto|metal|aco|aço|preto|paver)/,
  };
  return roomMatchers[roomId]?.test(n) ?? true;
}

// Gerador de texturas procedurais PBR em Canvas (cacheado por padrão + cor).
const textureCache = new Map();
function getProceduralTexture(pattern, hexColor) {
  if (!pattern || pattern === 'paint') return null;
  const key = `${pattern}:${hexColor}`;
  if (textureCache.has(key)) return textureCache.get(key);

  const size = 256;
  const c = document.createElement('canvas');
  c.width = size;
  c.height = size;
  const ctx = c.getContext('2d');
  const base = new THREE.Color(hexColor);
  const r = Math.round(base.r * 255);
  const g = Math.round(base.g * 255);
  const b = Math.round(base.b * 255);

  ctx.fillStyle = `rgb(${r},${g},${b})`;
  ctx.fillRect(0, 0, size, size);

  if (pattern === 'wood') {
    // Réguas e veios orgânicos de madeira
    const planks = 4;
    const ph = size / planks;
    for (let p = 0; p < planks; p++) {
      const shade = (p % 2 === 0 ? 6 : -6);
      ctx.fillStyle = `rgba(${shade > 0 ? 255 : 0},${shade > 0 ? 255 : 0},${shade > 0 ? 255 : 0},0.05)`;
      ctx.fillRect(0, p * ph, size, ph);
      ctx.strokeStyle = 'rgba(20,12,6,0.22)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(0, p * ph);
      ctx.lineTo(size, p * ph);
      ctx.stroke();
    }
    for (let y = 0; y < size; y += 2) {
      const wave = Math.sin(y * 0.14) * 0.5 + Math.cos(y * 0.05) * 0.5;
      ctx.fillStyle = wave > 0 ? 'rgba(255,245,230,0.06)' : 'rgba(25,15,5,0.09)';
      ctx.fillRect(0, y, size, 1.5);
    }
  } else if (pattern === 'travertine') {
    for (let y = 0; y < size; y += 3) {
      const a = 0.04 + (Math.sin(y * 0.21) * 0.5 + 0.5) * 0.09;
      ctx.fillStyle = y % 6 === 0 ? `rgba(255,250,242,${a})` : `rgba(85,72,56,${a})`;
      ctx.fillRect(0, y, size, 2);
    }
    for (let i = 0; i < 45; i++) {
      const px = (i * 53) % size;
      const py = (i * 37) % size;
      ctx.fillStyle = 'rgba(90,78,62,0.12)';
      ctx.fillRect(px, py, 10 + (i % 14), 2);
    }
  } else if (pattern === 'concrete') {
    for (let i = 0; i < 240; i++) {
      const px = (i * 71) % size;
      const py = (i * 43) % size;
      const rad = 8 + (i % 24);
      const grad = ctx.createRadialGradient(px, py, 1, px, py, rad);
      const light = i % 2 === 0;
      grad.addColorStop(0, light ? 'rgba(255,255,255,0.06)' : 'rgba(20,24,22,0.07)');
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(px - rad, py - rad, rad * 2, rad * 2);
    }
  } else if (pattern === 'marble') {
    ctx.strokeStyle = (r + g + b) / 3 > 128 ? 'rgba(110,112,116,0.16)' : 'rgba(225,228,232,0.14)';
    ctx.lineWidth = 2;
    for (let v = 0; v < 7; v++) {
      ctx.beginPath();
      let x = (v * 41) % size;
      let y = 0;
      ctx.moveTo(x, y);
      for (let s = 1; s <= 12; s++) {
        x += Math.sin(s * 0.9 + v) * 18;
        y = (s / 12) * size;
        ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  } else if (pattern === 'tile') {
    ctx.strokeStyle = 'rgba(70,66,58,0.18)';
    ctx.lineWidth = 2;
    const step = 64;
    for (let i = 0; i <= size; i += step) {
      ctx.beginPath();
      ctx.moveTo(i, 0); ctx.lineTo(i, size);
      ctx.moveTo(0, i); ctx.lineTo(size, i);
      ctx.stroke();
    }
  } else if (pattern === 'linen') {
    ctx.fillStyle = 'rgba(255,255,255,0.05)';
    for (let x = 0; x < size; x += 4) ctx.fillRect(x, 0, 1, size);
    ctx.fillStyle = 'rgba(0,0,0,0.05)';
    for (let y = 0; y < size; y += 4) ctx.fillRect(0, y, size, 1);
  }

  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(pattern === 'wood' ? 2.5 : 3, pattern === 'wood' ? 2.5 : 3);
  tex.anisotropy = 4;
  textureCache.set(key, tex);
  return tex;
}

// Dicionário de cores PT-BR para o parser de linguagem natural.
const COLOR_KEYWORDS = [
  { re: /verde\s*s[aá]lvia|s[aá]lvia|sage/i, name: 'verde sálvia', color: '#839781' },
  { re: /verde\s*(escuro|musgo|floresta|oliva)/i, name: 'verde musgo escuro', color: '#45594a' },
  { re: /verde/i, name: 'verde suave', color: '#6f8b74' },
  { re: /nogueira|walnut/i, name: 'nogueira', color: '#61412b', pattern: 'wood' },
  { re: /carvalho|oak|freij[oó]/i, name: 'carvalho quente', color: '#b48758', pattern: 'wood' },
  { re: /b[eé]tula|madeira\s*clara/i, name: 'madeira clara', color: '#d6c1a2', pattern: 'wood' },
  { re: /caramelo|conhaque|cognac|couro/i, name: 'couro caramelo', color: '#9e5e38', pattern: 'linen' },
  { re: /terracota|tijolo|barro/i, name: 'terracota', color: '#b86e52' },
  { re: /petr[oó]leo/i, name: 'azul petróleo', color: '#2f4b56' },
  { re: /azul\s*(marinho|escuro)/i, name: 'azul marinho', color: '#33485e' },
  { re: /azul/i, name: 'azul nórdico', color: '#6b8496' },
  { re: /cimento(\s*queimado)?|concreto/i, name: 'cimento queimado', color: '#939591', pattern: 'concrete' },
  { re: /travertino/i, name: 'travertino', color: '#d7ccbb', pattern: 'travertine' },
  { re: /m[aá]rmore(\s*branco)?|carrara/i, name: 'mármore branco', color: '#e9e7e2', pattern: 'marble' },
  { re: /granito\s*(preto|escuro)|preto|nero|[eé]bano/i, name: 'preto fosco', color: '#25282a' },
  { re: /grafite|chumbo|cinza\s*escuro/i, name: 'grafite fosco', color: '#42474a' },
  { re: /cinza|prata/i, name: 'cinza suave', color: '#9a9fa1' },
  { re: /off[-\s]?white|gelo|branco\s*quente/i, name: 'off-white quente', color: '#ede7dc' },
  { re: /branco|clean|neve/i, name: 'branco neve', color: '#f2f3f0' },
  { re: /areia|bege|linho|fendi|taupe|creme/i, name: 'areia quente', color: '#d6cab8' },
  { re: /lat[aã]o|dourado|ouro/i, name: 'latão dourado', color: '#c49d56', metalness: 0.85, roughness: 0.28 },
  { re: /bronze/i, name: 'bronze escovado', color: '#6b5340', metalness: 0.78, roughness: 0.34 },
];

function findColorMatch(text) {
  for (const entry of COLOR_KEYWORDS) {
    if (entry.re.test(text)) return entry;
  }
  return null;
}

export function createPersonalizer({
  scene,
  renderer,
  getCamera,
  setCamera,
  getControls,
  getPlan,
  getVariant,
  getCurrentRoot,
  getCurrentMeta,
  getActivePreset,
  selectView,
  setLightingFromStudio,
  requestFrame,
  showToast,
}) {
  // Elementos da UI do Estúdio de Personalização
  const undoBtn = document.querySelector('#studio-undo');
  const redoBtn = document.querySelector('#studio-redo');
  const modeRenovateBtn = document.querySelector('#studio-mode-renovate');
  const modeEmptyBtn = document.querySelector('#studio-mode-empty');
  const modePhotoBtn = document.querySelector('#studio-mode-photo');
  const styleSelect = document.querySelector('#studio-style-select');
  const listToggleBtn = document.querySelector('#studio-list-toggle');
  const walkBtn = document.querySelector('#view-mode-walk');

  const promptDock = document.querySelector('#studio-dock');
  const scopeSelect = document.querySelector('#studio-scope');
  const chipsContainer = document.querySelector('#studio-chips');
  const promptForm = document.querySelector('#studio-prompt-form');
  const promptInput = document.querySelector('#studio-prompt-input');
  const voiceBtn = document.querySelector('#studio-voice-btn');
  const bannerEl = document.querySelector('#studio-banner');
  const bannerText = document.querySelector('#studio-banner-text');
  const bannerAction = document.querySelector('#studio-banner-action');

  const lightSlider = document.querySelector('#studio-light-slider');
  const lightValue = document.querySelector('#studio-light-value');

  // Floating pill de edição de objeto / superfície selecionada no 3D
  const selectionPill = document.querySelector('#studio-selection-pill');
  const selTitle = document.querySelector('#studio-sel-title');
  const selMeta = document.querySelector('#studio-sel-meta');
  const selActions = document.querySelector('#studio-sel-actions');
  const selSwatches = document.querySelector('#studio-sel-swatches');
  const selClose = document.querySelector('#studio-sel-close');

  // Drawer lateral de Inventário & Acabamentos ("Lista")
  const listDrawer = document.querySelector('#studio-list-drawer');
  const listClose = document.querySelector('#studio-list-close');
  const listRooms = document.querySelector('#studio-list-rooms');
  const listFinishes = document.querySelector('#studio-list-finishes');
  const listFurniture = document.querySelector('#studio-list-furniture');
  const listResetBtn = document.querySelector('#studio-reset-all');
  const listExportBtn = document.querySelector('#studio-export-design');
  const listImportBtn = document.querySelector('#studio-import-design');
  const listImportFile = document.querySelector('#studio-import-file');

  // Modal de comparação 3D vs Foto/Render ("Foto")
  const photoModal = document.querySelector('#photo-compare-modal');
  const photoClose = document.querySelector('#photo-modal-close');
  const photoRoomSelect = document.querySelector('#photo-room-select');
  const photoSourceBtns = [...document.querySelectorAll('[data-photo-source]')];
  const photoImg3D = document.querySelector('#photo-img-3d');
  const photoImgRef = document.querySelector('#photo-img-ref');
  const photoClip = document.querySelector('#photo-compare-clip');
  const photoDivider = document.querySelector('#photo-compare-divider');
  const photoStage = document.querySelector('#photo-compare-stage');
  const photoRefLabel = document.querySelector('#photo-ref-label');
  const photoDownload = document.querySelector('#photo-modal-download');

  // Estado interno
  let renovateMode = false;
  let emptyMode = false;
  let walkMode = false;
  let activeScope = 'whole';
  let activeStyle = 'original';
  let lightIntensity = 1.0;
  let dragging3DItem = null;
  let selectedSurfaceSlot = null;
  let selectedSurfaceRoom = 'whole';

  // Mapa de overrides aplicados: { [slotKey]: { color, roughness, metalness, pattern, name } }
  // slotKey pode ser 'walls' (casa inteira) ou 'sala:walls' (escopo de ambiente)
  let materialOverrides = {};

  // Registro dos materiais e malhas do modelo atualmente carregado
  const materialRegistry = new Map(); // material -> { slot, name, original: {...}, meshes: [] }
  const movableDecorMeshes = [];

  // Gizmo 3D de seleção (BoxHelper)
  let selectionBox = null;

  // Pilha Undo / Redo
  const undoStack = [];
  const redoStack = [];
  let bannerTimer = null;

  function storageKey() {
    return `sobrado.personalizacao.${getVariant()}`;
  }

  function showBanner(message, actionLabel = null, onAction = null) {
    if (!bannerEl) return;
    bannerText.textContent = message;
    if (actionLabel && onAction) {
      bannerAction.textContent = actionLabel;
      bannerAction.hidden = false;
      bannerAction.onclick = () => { onAction(); bannerEl.hidden = true; };
    } else {
      bannerAction.hidden = true;
      bannerAction.onclick = null;
    }
    bannerEl.hidden = false;
    clearTimeout(bannerTimer);
    bannerTimer = setTimeout(() => { bannerEl.hidden = true; }, 4500);
  }

  function captureState() {
    return {
      style: activeStyle,
      emptyMode,
      lightIntensity,
      overrides: JSON.parse(JSON.stringify(materialOverrides)),
      furniture: getPlan()?.getSnapshot() ?? [],
    };
  }

  function pushHistory() {
    undoStack.push(captureState());
    if (undoStack.length > 40) undoStack.shift();
    redoStack.length = 0;
    updateHistoryButtons();
  }

  function updateHistoryButtons() {
    if (undoBtn) undoBtn.disabled = undoStack.length === 0;
    if (redoBtn) redoBtn.disabled = redoStack.length === 0;
  }

  function saveStateToStorage() {
    try {
      localStorage.setItem(storageKey(), JSON.stringify({
        style: activeStyle,
        emptyMode,
        lightIntensity,
        overrides: materialOverrides,
      }));
    } catch {
      // Silencioso se localStorage bloqueado.
    }
  }

  function restoreState(snapshot, { save = true } = {}) {
    activeStyle = snapshot.style ?? 'original';
    emptyMode = Boolean(snapshot.emptyMode);
    lightIntensity = Number.isFinite(snapshot.lightIntensity) ? snapshot.lightIntensity : 1.0;
    materialOverrides = JSON.parse(JSON.stringify(snapshot.overrides ?? {}));
    if (Array.isArray(snapshot.furniture)) {
      getPlan()?.restoreSnapshot(snapshot.furniture);
    }
    applyAllOverrides();
    applyEmptyState();
    syncLightControl();
    syncUI();
    if (save) saveStateToStorage();
  }

  function undo() {
    if (!undoStack.length) return;
    redoStack.push(captureState());
    const prev = undoStack.pop();
    restoreState(prev);
    updateHistoryButtons();
    showToast('Alteração desfeita');
  }

  function redo() {
    if (!redoStack.length) return;
    undoStack.push(captureState());
    const next = redoStack.pop();
    restoreState(next);
    updateHistoryButtons();
    showToast('Alteração refeita');
  }

  // Varre a cena carregada para indexar materiais editáveis e móveis ocultáveis no modo Vazio.
  function bindModel(root) {
    materialRegistry.clear();
    movableDecorMeshes.length = 0;
    clearSelectionGizmo();
    selectedSurfaceSlot = null;
    hideSelectionPill();

    if (!root) return;
    root.traverse((node) => {
      if (!node.isMesh) return;
      const mats = Array.isArray(node.material) ? node.material : [node.material];
      for (const mat of mats) {
        if (!mat || !mat.color) continue;
        if (isMovableDecorMaterial(mat.name)) {
          movableDecorMeshes.push(node);
        }
        const slot = classifyMaterial(mat.name);
        if (!slot) continue;
        if (!materialRegistry.has(mat)) {
          materialRegistry.set(mat, {
            slot,
            name: mat.name ?? '',
            original: {
              color: mat.color.clone(),
              map: mat.map ?? null,
              roughness: mat.roughness,
              metalness: mat.metalness,
            },
            meshes: [],
          });
        }
        materialRegistry.get(mat).meshes.push(node);
      }
    });

    // Restaura personalização salva desta maquete (se houver)
    undoStack.length = 0;
    redoStack.length = 0;
    materialOverrides = {};
    activeStyle = 'original';
    emptyMode = false;
    lightIntensity = 1.0;
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey()) ?? 'null');
      if (saved && typeof saved === 'object') {
        activeStyle = saved.style ?? 'original';
        emptyMode = Boolean(saved.emptyMode);
        lightIntensity = Number.isFinite(saved.lightIntensity) ? saved.lightIntensity : 1.0;
        materialOverrides = saved.overrides ?? {};
      }
    } catch {
      // Ignora estado corrompido.
    }

    applyAllOverrides();
    applyEmptyState();
    syncLightControl();
    updateHistoryButtons();
    syncUI();
  }

  function applyAllOverrides() {
    for (const [mat, info] of materialRegistry) {
      // Primeiro restaura o original
      mat.color.copy(info.original.color);
      mat.map = info.original.map;
      if (typeof info.original.roughness === 'number') mat.roughness = info.original.roughness;
      if (typeof info.original.metalness === 'number') mat.metalness = info.original.metalness;

      // Aplica override global do slot (se houver)
      let spec = materialOverrides[info.slot] ?? null;

      // Sobrescreve com override específico de ambiente (se esse material pertence àquele ambiente)
      for (const [key, val] of Object.entries(materialOverrides)) {
        if (!key.includes(':')) continue;
        const [roomId, slotKey] = key.split(':');
        if (slotKey === info.slot && materialBelongsToRoom(info.name, roomId)) {
          spec = val;
        }
      }

      if (spec) {
        if (spec.color) mat.color.set(spec.color);
        if (spec.pattern) {
          const tex = getProceduralTexture(spec.pattern, spec.color ?? '#cccccc');
          mat.map = tex; // null para 'paint' remove textura original e dá pintura lisa
        }
        if (typeof spec.roughness === 'number' && 'roughness' in mat) mat.roughness = spec.roughness;
        if (typeof spec.metalness === 'number' && 'metalness' in mat) mat.metalness = spec.metalness;
      }
      mat.needsUpdate = true;
    }
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
    renderListDrawer();
  }

  function applyEmptyState() {
    for (const mesh of movableDecorMeshes) {
      mesh.visible = !emptyMode;
    }
    getPlan()?.setEmptyHidden(emptyMode);
    if (emptyMode) clearSelectionGizmo();
    renderer.shadowMap.needsUpdate = true;
    requestFrame();
  }

  function setOverride(slot, spec, roomId = 'whole') {
    const key = roomId && roomId !== 'whole' ? `${roomId}:${slot}` : slot;
    if (!spec) delete materialOverrides[key];
    else materialOverrides[key] = { ...spec };
    if (activeStyle !== 'custom') activeStyle = 'custom';
    applyAllOverrides();
    saveStateToStorage();
    syncUI();
  }

  function applyStylePreset(styleId, { recordHistory = true } = {}) {
    const preset = STYLE_PRESETS[styleId];
    if (!preset) return;
    if (recordHistory) pushHistory();
    activeStyle = styleId;
    materialOverrides = JSON.parse(JSON.stringify(preset.overrides ?? {}));
    if (preset.lighting) {
      lightIntensity = preset.lighting.intensity ?? 1.0;
      setLightingFromStudio?.(preset.lighting.mode, lightIntensity);
    }
    applyAllOverrides();
    syncLightControl();
    saveStateToStorage();
    syncUI();
    showBanner(
      styleId === 'original'
        ? 'Acabamentos originais da maquete restaurados'
        : `Estilo "${preset.label}" aplicado: ${preset.description}`,
      styleId !== 'original' ? 'Comparar Foto' : null,
      () => openPhotoModal(),
    );
  }

  function syncLightControl() {
    if (!lightSlider) return;
    lightSlider.value = String(Math.round(lightIntensity * 100));
    if (lightValue) lightValue.textContent = `${Math.round(lightIntensity * 100)}%`;
    setLightingFromStudio?.(null, lightIntensity);
  }

  // Gizmo 3D ao redor de móvel selecionado
  function clearSelectionGizmo() {
    if (selectionBox) {
      scene.remove(selectionBox);
      selectionBox.geometry?.dispose();
      selectionBox.material?.dispose();
      selectionBox = null;
      requestFrame();
    }
  }

  function updateSelectionGizmo(item) {
    clearSelectionGizmo();
    if (!item || !item.model || !item.model.visible) return;
    selectionBox = new THREE.BoxHelper(item.model, 0x9bd5b9);
    selectionBox.renderOrder = 950;
    scene.add(selectionBox);
    requestFrame();
  }

  function hideSelectionPill() {
    if (selectionPill) selectionPill.hidden = true;
  }

  // Mostra barra flutuante do móvel selecionado (nome, L×P×A cm, ações rápidas, cores e trocas)
  function showObjectPill(item) {
    if (!selectionPill || !item) { hideSelectionPill(); return; }
    selectedSurfaceSlot = null;
    const spec = furnitureCatalog[item.type] ?? furnitureCatalog.custom;
    const cm = (m) => Math.round(m * 100);
    selTitle.textContent = item.label ?? spec.name;
    selMeta.textContent = `${cm(item.width)} × ${cm(item.depth)} × ${cm(item.height)} cm · ${Math.round(THREE.MathUtils.radToDeg(item.angle))}°`;

    selActions.innerHTML = '';
    const mkBtn = (label, title, onClick, pressed = false) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'studio-mini-btn';
      b.textContent = label;
      b.title = title;
      if (pressed) b.setAttribute('aria-pressed', 'true');
      b.addEventListener('click', onClick);
      selActions.append(b);
    };
    mkBtn(dragging3DItem === item ? 'Soltar' : 'Mover 3D', 'Arraste no piso 3D para reposicionar', () => {
      dragging3DItem = dragging3DItem === item ? null : item;
      showToast(dragging3DItem ? 'Clique no piso 3D para reposicionar o móvel' : 'Posição fixada');
      showObjectPill(item);
    }, dragging3DItem === item);
    mkBtn('↻ 45°', 'Girar 45°', () => { pushHistory(); getPlan()?.rotateSelected(Math.PI / 4); updateSelectionGizmo(item); showObjectPill(item); });
    mkBtn('⧉', 'Duplicar móvel', () => { pushHistory(); const copy = getPlan()?.duplicateSelected(); if (copy) showToast('Móvel duplicado'); });
    mkBtn('✕', 'Remover móvel', () => { pushHistory(); dragging3DItem = null; getPlan()?.removeSelected(); hideSelectionPill(); clearSelectionGizmo(); });

    selSwatches.innerHTML = '';
    const swaps = OBJECT_SWAP_CHIPS[spec.category] ?? OBJECT_SWAP_CHIPS.default;
    for (const sw of swaps) {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'studio-chip';
      chip.textContent = sw.label;
      chip.addEventListener('click', () => {
        pushHistory();
        const updated = getPlan()?.updateSelected(sw.patch);
        if (updated) {
          updateSelectionGizmo(updated);
          showObjectPill(updated);
          showBanner(`Móvel atualizado para "${sw.label}"`);
        }
      });
      selSwatches.append(chip);
    }

    selectionPill.hidden = false;
    updatePromptContext();
  }

  // Mostra barra flutuante quando o usuário clica diretamente em uma parede/piso/armário no 3D
  function showSurfacePill(slot, roomId = 'whole', rawMatName = '') {
    if (!selectionPill || !SURFACE_SLOTS[slot]) return;
    getPlan()?.clearSelection();
    clearSelectionGizmo();
    dragging3DItem = null;
    selectedSurfaceSlot = slot;
    selectedSurfaceRoom = roomId;

    const info = SURFACE_SLOTS[slot];
    const roomObj = ROOM_SCOPES.find((r) => r.id === roomId);
    selTitle.textContent = info.label;
    selMeta.textContent = roomId === 'whole'
      ? (rawMatName ? `Material: ${rawMatName}` : 'Aplicar em toda a casa')
      : `Escopo: ${roomObj?.label ?? roomId}`;

    selActions.innerHTML = '';
    const toggleScopeBtn = document.createElement('button');
    toggleScopeBtn.type = 'button';
    toggleScopeBtn.className = 'studio-mini-btn';
    toggleScopeBtn.textContent = roomId === 'whole' ? 'Só ambiente' : 'Casa inteira';
    toggleScopeBtn.addEventListener('click', () => {
      const nextRoom = roomId === 'whole' ? (activeScope === 'whole' ? 'sala' : activeScope) : 'whole';
      showSurfacePill(slot, nextRoom, rawMatName);
    });
    selActions.append(toggleScopeBtn);

    const resetBtn = document.createElement('button');
    resetBtn.type = 'button';
    resetBtn.className = 'studio-mini-btn';
    resetBtn.textContent = 'Original';
    resetBtn.addEventListener('click', () => {
      pushHistory();
      setOverride(slot, null, selectedSurfaceRoom);
      showBanner(`${info.label} restaurado para o original`);
    });
    selActions.append(resetBtn);

    selSwatches.innerHTML = '';
    for (const sw of SLOT_SWATCHES[slot] ?? []) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'studio-swatch-btn';
      btn.title = sw.name;
      btn.innerHTML = `<span class="studio-swatch-dot" style="background:${sw.color}"></span><span>${sw.name}</span>`;
      btn.addEventListener('click', () => {
        pushHistory();
        setOverride(slot, sw, selectedSurfaceRoom);
        showBanner(`${info.label} alterado para ${sw.name}`);
      });
      selSwatches.append(btn);
    }

    selectionPill.hidden = false;
    updatePromptContext();
  }

  // Atualiza placeholder e chips da barra de prompt de acordo com escopo (Casa inteira / Ambiente / Objeto selecionado)
  function updatePromptContext() {
    if (!chipsContainer || !promptInput) return;
    const selectedItem = getPlan()?.getSelected();
    chipsContainer.innerHTML = '';

    if (selectedItem) {
      const spec = furnitureCatalog[selectedItem.type] ?? furnitureCatalog.custom;
      const name = (selectedItem.label ?? spec.name).toLowerCase();
      promptInput.placeholder = `O que este(a) ${name} deve virar?`;
      const swaps = OBJECT_SWAP_CHIPS[spec.category] ?? OBJECT_SWAP_CHIPS.default;
      for (const sw of swaps.slice(0, 4)) {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'studio-chip';
        chip.textContent = sw.label;
        chip.addEventListener('click', () => {
          pushHistory();
          const updated = getPlan()?.updateSelected(sw.patch);
          if (updated) {
            updateSelectionGizmo(updated);
            showObjectPill(updated);
            showBanner(`Alterado para ${sw.label}`);
          }
        });
        chipsContainer.append(chip);
      }
      return;
    }

    const scopeObj = ROOM_SCOPES.find((r) => r.id === activeScope) ?? ROOM_SCOPES[0];
    promptInput.placeholder = activeScope === 'whole'
      ? 'Personalizar a casa inteira... (ex: paredes verde sálvia e piso nogueira)'
      : `Mudar ${scopeObj.label.toLowerCase()}... (ex: estilo mid-century, piso carvalho)`;

    for (const text of scopeObj.chips) {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'studio-chip';
      chip.textContent = text;
      chip.addEventListener('click', () => executePrompt(text));
      chipsContainer.append(chip);
    }
  }

  // Parser semântico de comandos em português para remodelação instantânea em 3D.
  function executePrompt(rawText) {
    const text = (rawText ?? '').trim();
    if (!text) return;
    const lower = text.toLowerCase();
    const plan = getPlan();
    const selectedItem = plan?.getSelected();
    const scopeObj = ROOM_SCOPES.find((r) => r.id === activeScope) ?? ROOM_SCOPES[0];
    const actionsDone = [];

    pushHistory();

    // 1. Se há um móvel selecionado e o comando fala em trocar/transformar o móvel
    if (selectedItem) {
      const patch = {};
      if (/travertino|redond/i.test(lower)) { patch.type = 'coffee_round'; patch.color = 0xd9cfc1; patch.label = 'Mesa redonda travertino'; }
      else if (/vidro|lat[aã]o/i.test(lower)) { patch.type = 'coffee_glass'; patch.color = 0xc59d52; patch.label = 'Mesa vidro e latão'; }
      else if (/livro|carvalho.*centro/i.test(lower)) { patch.type = 'coffee_oak'; patch.color = 0xb68a5c; patch.label = 'Mesa centro carvalho'; }
      else if (/poltrona/i.test(lower)) { patch.type = 'armchair'; }
      else if (/sof[aá]/i.test(lower)) { patch.type = 'sofa'; }
      else if (/escrivaninha|mesa.*escrit/i.test(lower)) { patch.type = 'desk'; }
      else if (/aparador|buffet/i.test(lower)) { patch.type = 'sideboard'; }
      else if (/planta|vaso/i.test(lower)) { patch.type = 'plant'; }
      else if (/lumin[aá]ria|abajur/i.test(lower)) { patch.type = 'lamp'; }
      else if (/tapete/i.test(lower)) { patch.type = 'rug'; }
      else if (/remover|excluir|apagar/i.test(lower)) {
        plan.removeSelected();
        hideSelectionPill();
        clearSelectionGizmo();
        showBanner('Móvel removido do ambiente');
        return;
      }
      const cm = findColorMatch(lower);
      if (cm && !patch.color) patch.color = new THREE.Color(cm.color).getHex();
      if (Object.keys(patch).length) {
        const updated = plan.updateSelected(patch);
        if (updated) {
          updateSelectionGizmo(updated);
          showObjectPill(updated);
          showBanner(`Móvel atualizado: ${text}`);
        }
        return;
      }
    }

    // 2. Comandos de restauração / esvaziar / mobiliar
    if (/restaurar|original|reset/i.test(lower)) {
      applyStylePreset('original', { recordHistory: false });
      return;
    }
    if (/esvaziar|vazio|limpar\s*m[oó]veis/i.test(lower)) {
      emptyMode = true;
      applyEmptyState();
      saveStateToStorage();
      syncUI();
      showBanner('Modo vazio ativado: móveis e decorações ocultados');
      return;
    }

    // 3. Estilos completos
    if (/escuro|aconchegante|moody|noturno/i.test(lower)) {
      applyStylePreset('dark-moody', { recordHistory: false });
      return;
    }
    if (/escandinav|n[oó]rdic/i.test(lower)) {
      applyStylePreset('scandi', { recordHistory: false });
      return;
    }
    if (/mid[-\s]?century|retr[oô]/i.test(lower)) {
      applyStylePreset('mid-century', { recordHistory: false });
      return;
    }
    if (/minimalista/i.test(lower)) {
      applyStylePreset('warm-minimal', { recordHistory: false });
      return;
    }
    if (/industrial/i.test(lower)) {
      applyStylePreset('industrial', { recordHistory: false });
      return;
    }
    if (/japandi/i.test(lower)) {
      applyStylePreset('japandi', { recordHistory: false });
      return;
    }
    if (/mediterr[aâ]ne/i.test(lower)) {
      applyStylePreset('mediterranean', { recordHistory: false });
      return;
    }

    // 4. Reorganizar móveis do ambiente
    if (/reorganizar|arrumar|girar/i.test(lower)) {
      const b = scopeObj.bounds ?? ROOM_SCOPES[1].bounds;
      const fl = scopeObj.floor === 'full' ? 'terreo' : scopeObj.floor;
      const moved = plan?.rearrangeRoom(b, fl) ?? 0;
      if (moved > 0) {
        showBanner(`${moved} móvel(is) reorganizado(s) em ${scopeObj.label}`);
        return;
      }
      // Se ainda não há móveis de estudo no ambiente, insere um conjunto harmônico!
      actionsDone.push(...populateStudySet(scopeObj));
    }

    // 5. Inserção de móveis / decoração ("adicionar mesa travertino", "mobiliar sala", "adicionar planta e tapete")
    let handledMobiliar = false;
    if (/mobiliar|decorar/i.test(lower)) {
      if (emptyMode) { emptyMode = false; applyEmptyState(); }
      actionsDone.push(...populateStudySet(scopeObj));
      handledMobiliar = true;
    }
    if (/adicionar|colocar|inserir|botar/i.test(lower)) {
      if (emptyMode) { emptyMode = false; applyEmptyState(); }
      const targetFloor = scopeObj.floor === 'full' ? 'terreo' : scopeObj.floor;
      const [cx, , cz] = scopeObj.center;
      const addOne = (type, dx = 0, dz = 0, colorHex = null) => {
        const created = plan?.addItem({
          type, floor: targetFloor, x: cx + dx, z: cz + dz,
          color: colorHex ?? furnitureCatalog[type]?.color,
        });
        if (created) {
          updateSelectionGizmo(created);
          showObjectPill(created);
          actionsDone.push(`${furnitureCatalog[type].name} inserido(a)`);
        }
      };
      if (/travertino|mesa\s*(de\s*centro|redonda)/i.test(lower)) addOne('coffee_round', 0, 0.15);
      if (/vidro.*lat[aã]o/i.test(lower)) addOne('coffee_glass', 0, 0.15);
      if (/tapete/i.test(lower)) addOne('rug', 0, 0);
      if (/planta|vaso/i.test(lower)) addOne('plant', -0.95, -0.65);
      if (/lumin[aá]ria|abajur/i.test(lower)) addOne('lamp', 0.95, -0.65);
      if (/poltrona/i.test(lower)) addOne('armchair', 0.85, 0.45);
      if (/sof[aá]/i.test(lower)) addOne('sofa', 0, -0.65);
      if (/aparador|buffet/i.test(lower)) addOne('sideboard', -0.9, 0);
      if (/escrivaninha|home office/i.test(lower)) addOne('desk', 0.4, -0.4);
      if (/cama/i.test(lower)) addOne('bed', 0, 0);
    }

    // 6. Alterações de materiais / tintas / pisos / armários / bancadas / fachada (suporta frases compostas: "paredes verde sálvia e piso nogueira")
    const globalColor = findColorMatch(lower);
    const targetRoom = activeScope;
    const clauses = lower
      .split(/\s*(?:,|;|\be\b|\bcom\b)\s*/i)
      .map((s) => s.trim())
      .filter(Boolean);

    const applySlot = (slot, chosen, defaultPattern = 'paint') => {
      if (!chosen) return;
      const spec = {
        name: chosen.name,
        color: chosen.color,
        pattern: chosen.pattern ?? defaultPattern,
        roughness: chosen.roughness ?? (defaultPattern === 'wood' ? 0.56 : defaultPattern === 'marble' ? 0.24 : 0.86),
        metalness: chosen.metalness ?? 0.05,
      };
      const key = targetRoom !== 'whole' ? `${targetRoom}:${slot}` : slot;
      materialOverrides[key] = spec;
      actionsDone.push(`${SURFACE_SLOTS[slot].short}: ${chosen.name}`);
    };

    let matchedSurface = false;
    if (!handledMobiliar) {
      for (const clause of clauses) {
        const cColor = findColorMatch(clause) ?? globalColor;
        if (/parede|pintar|tinta|reboco/i.test(clause)) {
          applySlot('walls', cColor, cColor?.pattern ?? 'paint');
          applySlot('accentWall', cColor, cColor?.pattern ?? 'paint');
          matchedSurface = true;
        }
        if (/piso|ch[aã]o|porcelanato|laminado|assoalho/i.test(clause)) {
          applySlot('floorMain', cColor, cColor?.pattern ?? 'wood');
          applySlot('floorWood', cColor, cColor?.pattern ?? 'wood');
          matchedSurface = true;
        }
        if (/arm[aá]rio|cozinha|marcenaria/i.test(clause)) {
          applySlot('cabinets', cColor, cColor?.pattern ?? 'paint');
          matchedSurface = true;
        }
        if (/ripado|madeira|carvalho|nogueira/i.test(clause) && !/piso/i.test(clause)) {
          applySlot('wood', cColor, 'wood');
          matchedSurface = true;
        }
        if (/bancada|pedra|granito|m[aá]rmore|travertino/i.test(clause) && !/mesa/i.test(clause)) {
          applySlot('counters', cColor, cColor?.pattern ?? 'marble');
          matchedSurface = true;
        }
        if (/sof[aá]|estofado|tecido|enxoval|cortina|couro/i.test(clause) && !/adicionar/i.test(clause)) {
          applySlot('upholstery', cColor, 'linen');
          matchedSurface = true;
        }
        if (/fachada|extern/i.test(clause)) {
          applySlot('facade', cColor, cColor?.pattern ?? 'paint');
          matchedSurface = true;
        }
        if (/metal|esquadria|lat[aã]o|bronze|inox/i.test(clause) && !/mesa/i.test(clause)) {
          applySlot('metal', cColor, 'paint');
          matchedSurface = true;
        }
      }
    }

    // Se citou só uma cor (ex: "verde sálvia") sem especificar superfície, aplica nas paredes destaque/internas do escopo
    if (!matchedSurface && !actionsDone.length && globalColor) {
      if (globalColor.pattern === 'wood') {
        applySlot('floorMain', globalColor, 'wood');
        applySlot('wood', globalColor, 'wood');
      } else {
        applySlot('accentWall', globalColor, globalColor.pattern ?? 'paint');
        applySlot('walls', globalColor, globalColor.pattern ?? 'paint');
      }
      matchedSurface = true;
    }

    if (matchedSurface) {
      activeStyle = 'custom';
      applyAllOverrides();
      saveStateToStorage();
      syncUI();
    }

    if (actionsDone.length) {
      showBanner(`${scopeObj.label}: ${actionsDone.join(' · ')}`, 'Comparar Foto', () => openPhotoModal());
    } else {
      undoStack.pop();
      updateHistoryButtons();
      showToast('Tente ex.: "paredes verde sálvia", "piso nogueira", "estilo mid-century" ou "adicionar mesa travertino"');
    }
  }

  function populateStudySet(scopeObj) {
    const plan = getPlan();
    if (!plan) return [];
    const targetFloor = scopeObj.floor === 'full' ? 'terreo' : scopeObj.floor;
    const [cx, , cz] = scopeObj.center;
    const added = [];
    if (scopeObj.id === 'quarto-frente' || scopeObj.id === 'quarto-fundos') {
      plan.addItem({ type: 'desk', floor: targetFloor, x: cx + 0.35, z: cz - 0.3, angle: 0 });
      plan.addItem({ type: 'lamp', floor: targetFloor, x: cx - 0.65, z: cz - 0.5, angle: 0 });
      added.push('Escrivaninha e luminária adicionadas');
    } else {
      plan.addItem({ type: 'rug', floor: targetFloor, x: cx, z: cz, angle: 0 });
      plan.addItem({ type: 'plant', floor: targetFloor, x: cx - 0.9, z: cz - 0.7, angle: 0 });
      const table = plan.addItem({ type: 'coffee_round', floor: targetFloor, x: cx, z: cz, angle: 0 });
      if (table) {
        plan.selectItem(table.id);
        updateSelectionGizmo(table);
        showObjectPill(table);
      }
      added.push('Conjunto tapete + mesa travertino + planta inserido');
    }
    return added;
  }

  // Modo Caminhar (Walk) em primeira pessoa dentro da casa
  function setWalkMode(enabled) {
    walkMode = Boolean(enabled);
    if (walkBtn) walkBtn.setAttribute('aria-pressed', String(walkMode));
    if (walkMode) {
      const scopeObj = ROOM_SCOPES.find((r) => r.id === activeScope) ?? ROOM_SCOPES[1];
      const pos = new THREE.Vector3(...(scopeObj.walkPos ?? [1.55, 1.62, -0.55]));
      const tgt = new THREE.Vector3(...(scopeObj.walkTarget ?? [1.75, 1.48, -3.5]));
      selectView('full', null, { reframe: false });
      setCamera(pos, tgt);
      showBanner(`Modo Caminhar em ${scopeObj.label} — use WASD para andar e arraste para olhar`);
    }
    return walkMode;
  }

  // Renderiza o painel lateral "Lista" (Ambientes + Acabamentos + Inventário de móveis)
  function renderListDrawer() {
    if (!listDrawer || listDrawer.hidden) return;

    // 1. Ambientes com m²
    listRooms.innerHTML = '';
    for (const r of ROOM_SCOPES) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'studio-list-row';
      if (r.id === activeScope) btn.dataset.active = 'true';
      btn.innerHTML = `<span>${r.label}</span><small>${r.area}</small>`;
      btn.addEventListener('click', () => {
        setScope(r.id, { focusCamera: true });
        renderListDrawer();
      });
      listRooms.append(btn);
    }

    // 2. Acabamentos ativos (clicáveis para trocar cor na hora)
    listFinishes.innerHTML = '';
    for (const [slot, info] of Object.entries(SURFACE_SLOTS)) {
      const activeSpec = materialOverrides[`${activeScope}:${slot}`] ?? materialOverrides[slot] ?? null;
      const row = document.createElement('div');
      row.className = 'studio-finish-row';
      row.innerHTML = `
        <div class="studio-finish-label">
          <span class="studio-swatch-dot" style="background:${activeSpec?.color ?? '#6c7a72'}"></span>
          <div><strong>${info.short}</strong><small>${activeSpec?.name ?? 'Original da maquete'}</small></div>
        </div>
        <button type="button" class="studio-mini-btn">Editar</button>
      `;
      row.querySelector('button').addEventListener('click', () => {
        setRenovateMode(true);
        showSurfacePill(slot, activeScope);
      });
      listFinishes.append(row);
    }

    // 3. Inventário de móveis personalizados
    listFurniture.innerHTML = '';
    const items = getPlan()?.getItems() ?? [];
    if (!items.length) {
      const p = document.createElement('p');
      p.className = 'studio-empty-note';
      p.textContent = 'Nenhum móvel de personalização inserido ainda. Use o prompt (ex.: "Adicionar mesa travertino") ou a Planta.';
      listFurniture.append(p);
    } else {
      const cm = (m) => Math.round(m * 100);
      for (const item of items) {
        const spec = furnitureCatalog[item.type] ?? furnitureCatalog.custom;
        const row = document.createElement('div');
        row.className = 'studio-finish-row';
        const hex = `#${(item.color ?? spec.color).toString(16).padStart(6, '0')}`;
        row.innerHTML = `
          <div class="studio-finish-label">
            <span class="studio-swatch-dot" style="background:${hex}"></span>
            <div><strong>${item.label ?? spec.name}</strong><small>${cm(item.width)}×${cm(item.depth)}×${cm(item.height)} cm · ${item.floor}</small></div>
          </div>
          <div class="studio-row-actions">
            <button type="button" class="studio-mini-btn" data-act="focus">Ver</button>
            <button type="button" class="studio-mini-btn" data-act="del">✕</button>
          </div>
        `;
        row.querySelector('[data-act="focus"]').addEventListener('click', () => {
          setRenovateMode(true);
          const sel = getPlan()?.selectItem(item.id);
          if (sel) {
            updateSelectionGizmo(sel);
            showObjectPill(sel);
            const y = (floorElevation[sel.floor] ?? 0) + 0.4;
            setCamera(new THREE.Vector3(sel.x + 1.9, y + 1.5, sel.z + 2.1), new THREE.Vector3(sel.x, y, sel.z));
          }
        });
        row.querySelector('[data-act="del"]').addEventListener('click', () => {
          pushHistory();
          getPlan()?.removeItemById(item.id);
          clearSelectionGizmo();
          hideSelectionPill();
          renderListDrawer();
        });
        listFurniture.append(row);
      }
    }
  }

  function setScope(nextScope, { focusCamera = false } = {}) {
    activeScope = ROOM_SCOPES.some((r) => r.id === nextScope) ? nextScope : 'whole';
    if (scopeSelect) scopeSelect.value = activeScope;
    updatePromptContext();
    if (focusCamera) {
      const r = ROOM_SCOPES.find((x) => x.id === activeScope);
      if (r) {
        if (r.id === 'whole') {
          selectView('full');
        } else if (walkMode && r.walkPos && r.walkTarget) {
          setCamera(new THREE.Vector3(...r.walkPos), new THREE.Vector3(...r.walkTarget));
        } else if (r.walkPos && r.walkTarget) {
          // Foca na vista do ambiente selecionado sem perder a orientação 3D
          const targetFloor = r.floor === 'full' ? 'full' : r.floor;
          selectView(targetFloor, null, { reframe: false });
          const c = new THREE.Vector3(...r.center);
          setCamera(new THREE.Vector3(c.x + 1.8, c.y + 3.1, c.z + 2.8), new THREE.Vector3(c.x, c.y + 0.6, c.z));
        }
      }
    }
  }

  function setRenovateMode(active, { silent = false } = {}) {
    renovateMode = Boolean(active);
    if (modeRenovateBtn) modeRenovateBtn.setAttribute('aria-pressed', String(renovateMode));
    if (promptDock) promptDock.hidden = !renovateMode;
    document.body.dataset.studio = renovateMode ? 'renovate' : 'view';
    if (!renovateMode) {
      dragging3DItem = null;
      selectedSurfaceSlot = null;
      hideSelectionPill();
      clearSelectionGizmo();
    } else {
      updatePromptContext();
      if (!silent) showToast('Personalizar ativo: clique em qualquer parede, piso ou móvel no 3D ou digite um comando');
    }
  }

  function syncUI() {
    if (modeRenovateBtn) modeRenovateBtn.setAttribute('aria-pressed', String(renovateMode));
    if (modeEmptyBtn) modeEmptyBtn.setAttribute('aria-pressed', String(emptyMode));
    if (styleSelect) styleSelect.value = STYLE_PRESETS[activeStyle] ? activeStyle : 'custom';
    if (scopeSelect) scopeSelect.value = activeScope;
    updatePromptContext();
    renderListDrawer();
  }

  // Manipulador de clique direto no canvas 3D quando Personalizar está ativo
  function handleSceneClick(raycaster) {
    if (!renovateMode) return false;
    const plan = getPlan();

    // 1. Se está arrastando/movendo um móvel no piso 3D, posiciona no ponto clicado
    if (dragging3DItem) {
      const planeY = floorElevation[dragging3DItem.floor] ?? 0;
      const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -planeY);
      const pt = raycaster.ray.intersectPlane(floorPlane, new THREE.Vector3());
      if (pt) {
        pushHistory();
        plan?.moveSelectedTo(pt.x, pt.z, true);
        updateSelectionGizmo(dragging3DItem);
        showObjectPill(dragging3DItem);
        dragging3DItem = null;
        showToast('Móvel reposicionado no 3D');
        return true;
      }
    }

    // 2. Verifica clique em móveis personalizáveis 3D
    const pickedFurniture = plan?.pickInScene3D(raycaster);
    if (pickedFurniture) {
      updateSelectionGizmo(pickedFurniture);
      showObjectPill(pickedFurniture);
      return true;
    }

    // 3. Verifica clique em superfícies arquitetônicas do modelo GLB
    const root = getCurrentRoot();
    if (!root) return false;
    const meshes = [];
    root.traverseVisible((node) => { if (node.isMesh) meshes.push(node); });
    const hit = raycaster.intersectObjects(meshes, false)[0];
    if (hit) {
      const mats = Array.isArray(hit.object.material) ? hit.object.material : [hit.object.material];
      const mat = mats[0];
      const slot = classifyMaterial(mat?.name ?? '');
      if (slot) {
        showSurfacePill(slot, activeScope, mat.name);
        return true;
      }
    }

    plan?.clearSelection();
    clearSelectionGizmo();
    hideSelectionPill();
    updatePromptContext();
    return false;
  }

  // ---------------- Modal de Comparação 3D vs Foto / Render ----------------
  let activePhotoSource = 'atual';
  let splitRatio = 0.5;

  function setPhotoSplit(ratio) {
    splitRatio = THREE.MathUtils.clamp(ratio, 0.04, 0.96);
    const pct = `${(splitRatio * 100).toFixed(1)}%`;
    if (photoClip) photoClip.style.clipPath = `inset(0 ${(100 - splitRatio * 100).toFixed(1)}% 0 0)`;
    if (photoDivider) photoDivider.style.left = pct;
  }

  function updatePhotoReference() {
    if (!photoRoomSelect) return;
    const room = COMPARISON_ROOMS.find((r) => r.id === photoRoomSelect.value) ?? COMPARISON_ROOMS[0];
    let file = room[activePhotoSource];
    if (!file) {
      // Fallback automático se o ambiente não tiver render industrial
      activePhotoSource = room.real ? 'real' : 'atual';
      file = room[activePhotoSource];
    }
    const labels = { atual: 'Render fotorrealista (Atual)', industrial: 'Render Industrial', real: 'Foto real da casa' };
    for (const btn of photoSourceBtns) {
      const src = btn.dataset.photoSource;
      btn.disabled = !room[src];
      btn.setAttribute('aria-pressed', String(src === activePhotoSource));
    }
    if (photoRefLabel) photoRefLabel.textContent = labels[activePhotoSource] ?? 'Foto';
    if (photoImgRef && file) photoImgRef.src = `./comparacoes/${file}?v=20261124v11`;
  }

  function openPhotoModal() {
    if (!photoModal) return;
    // Captura frame atual do canvas 3D ao vivo
    const cam = getCamera();
    if (cam) renderer.render(scene, cam);
    if (photoImg3D) photoImg3D.src = renderer.domElement.toDataURL('image/png');

    // Sincroniza ambiente inicial com o preset ativo ou escopo selecionado
    const activePreset = getActivePreset?.();
    const hint = (activePreset?.id ?? activeScope ?? 'sala').toLowerCase();
    const matched = COMPARISON_ROOMS.find((r) => r.id === hint || r.presetHints.some((h) => hint.includes(h))) ?? COMPARISON_ROOMS[0];
    photoRoomSelect.value = matched.id;
    activePhotoSource = getVariant() === 'industrial' && matched.industrial ? 'industrial' : 'atual';

    updatePhotoReference();
    setPhotoSplit(0.5);
    photoModal.hidden = false;
  }

  // Preenche selects de escopo, estilos e quartos do comparador Foto
  if (scopeSelect) {
    scopeSelect.innerHTML = ROOM_SCOPES.map((r) => `<option value="${r.id}">${r.label}</option>`).join('');
    scopeSelect.addEventListener('change', () => setScope(scopeSelect.value, { focusCamera: true }));
  }
  if (styleSelect) {
    styleSelect.innerHTML = [
      ...Object.values(STYLE_PRESETS).map((s) => `<option value="${s.id}">${s.label}</option>`),
      '<option value="custom">Personalizado</option>',
    ].join('');
    styleSelect.addEventListener('change', () => {
      if (styleSelect.value === 'custom') return;
      applyStylePreset(styleSelect.value);
    });
  }
  if (photoRoomSelect) {
    photoRoomSelect.innerHTML = COMPARISON_ROOMS.map((r) => `<option value="${r.id}">${r.label}</option>`).join('');
    photoRoomSelect.addEventListener('change', updatePhotoReference);
  }

  // Eventos da barra superior, prompt, voz, luz, drawer Lista e modal Foto
  undoBtn?.addEventListener('click', undo);
  redoBtn?.addEventListener('click', redo);
  modeRenovateBtn?.addEventListener('click', () => setRenovateMode(!renovateMode));
  modeEmptyBtn?.addEventListener('click', () => {
    pushHistory();
    emptyMode = !emptyMode;
    applyEmptyState();
    saveStateToStorage();
    syncUI();
    showBanner(emptyMode ? 'Casa em modo vazio (móveis ocultos)' : 'Móveis restaurados');
  });
  modePhotoBtn?.addEventListener('click', openPhotoModal);

  listToggleBtn?.addEventListener('click', () => {
    if (!listDrawer) return;
    listDrawer.hidden = !listDrawer.hidden;
    listToggleBtn.setAttribute('aria-pressed', String(!listDrawer.hidden));
    if (!listDrawer.hidden) renderListDrawer();
  });
  listClose?.addEventListener('click', () => {
    if (!listDrawer) return;
    listDrawer.hidden = true;
    listToggleBtn?.setAttribute('aria-pressed', 'false');
  });
  listResetBtn?.addEventListener('click', () => {
    applyStylePreset('original');
    emptyMode = false;
    applyEmptyState();
  });
  listExportBtn?.addEventListener('click', () => {
    const payload = JSON.stringify({
      variant: getVariant(),
      ...captureState(),
    }, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sobrado-personalizacao-${getVariant()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Projeto personalizado exportado em JSON');
  });
  listImportBtn?.addEventListener('click', () => listImportFile?.click());
  listImportFile?.addEventListener('change', async () => {
    const file = listImportFile.files?.[0];
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text());
      pushHistory();
      restoreState(parsed);
      showBanner('Projeto personalizado importado com sucesso');
    } catch {
      showToast('Arquivo JSON inválido');
    } finally {
      listImportFile.value = '';
    }
  });

  selClose?.addEventListener('click', () => {
    dragging3DItem = null;
    selectedSurfaceSlot = null;
    getPlan()?.clearSelection();
    clearSelectionGizmo();
    hideSelectionPill();
    updatePromptContext();
  });

  promptForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    const val = promptInput.value.trim();
    if (!val) return;
    executePrompt(val);
    promptInput.value = '';
  });

  // Entrada por voz (Web Speech API pt-BR)
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (voiceBtn) {
    if (!SpeechRec) {
      voiceBtn.disabled = true;
      voiceBtn.title = 'Ditado por voz não suportado neste navegador';
    } else {
      let listening = false;
      const rec = new SpeechRec();
      rec.lang = 'pt-BR';
      rec.interimResults = false;
      rec.addEventListener('result', (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript ?? '';
        if (transcript) {
          promptInput.value = transcript;
          executePrompt(transcript);
          promptInput.value = '';
        }
      });
      rec.addEventListener('end', () => {
        listening = false;
        voiceBtn.setAttribute('aria-pressed', 'false');
      });
      voiceBtn.addEventListener('click', () => {
        if (listening) { rec.stop(); return; }
        listening = true;
        voiceBtn.setAttribute('aria-pressed', 'true');
        showToast('Ouvindo comando em português...');
        rec.start();
      });
    }
  }

  lightSlider?.addEventListener('input', () => {
    lightIntensity = Number(lightSlider.value) / 100;
    syncLightControl();
    saveStateToStorage();
  });

  // Interação do slider de comparação Foto
  photoClose?.addEventListener('click', () => { photoModal.hidden = true; });
  photoModal?.addEventListener('click', (event) => {
    if (event.target === photoModal) photoModal.hidden = true;
  });
  for (const btn of photoSourceBtns) {
    btn.addEventListener('click', () => {
      activePhotoSource = btn.dataset.photoSource;
      updatePhotoReference();
    });
  }
  if (photoStage) {
    let draggingSplit = false;
    const updateFromPointer = (clientX) => {
      const rect = photoStage.getBoundingClientRect();
      setPhotoSplit((clientX - rect.left) / Math.max(1, rect.width));
    };
    photoStage.addEventListener('pointerdown', (e) => {
      draggingSplit = true;
      photoStage.setPointerCapture(e.pointerId);
      updateFromPointer(e.clientX);
    });
    photoStage.addEventListener('pointermove', (e) => {
      if (draggingSplit) updateFromPointer(e.clientX);
    });
    photoStage.addEventListener('pointerup', () => { draggingSplit = false; });
    photoStage.addEventListener('pointercancel', () => { draggingSplit = false; });
  }
  photoDownload?.addEventListener('click', () => {
    if (!photoImg3D?.complete || !photoImgRef?.complete) return;
    const w = photoImg3D.naturalWidth || 1280;
    const h = photoImg3D.naturalHeight || 720;
    const out = document.createElement('canvas');
    out.width = w;
    out.height = h;
    const ctx = out.getContext('2d');
    ctx.drawImage(photoImgRef, 0, 0, w, h);
    const splitX = Math.round(w * splitRatio);
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, splitX, h);
    ctx.clip();
    ctx.drawImage(photoImg3D, 0, 0, w, h);
    ctx.restore();
    ctx.fillStyle = '#9bd5b9';
    ctx.fillRect(splitX - 2, 0, 4, h);
    const a = document.createElement('a');
    a.href = out.toDataURL('image/png');
    a.download = `sobrado-comparativo-${photoRoomSelect.value}.png`;
    a.click();
    showToast('Comparativo 3D vs Foto salvo em PNG');
  });

  // Atalhos globais Ctrl+Z / Ctrl+Y e Esc
  window.addEventListener('keydown', (event) => {
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement) {
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
      event.preventDefault();
      if (event.shiftKey) redo();
      else undo();
    } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'y') {
      event.preventDefault();
      redo();
    } else if (event.key === 'Escape') {
      if (photoModal && !photoModal.hidden) { photoModal.hidden = true; return; }
      if (listDrawer && !listDrawer.hidden) { listDrawer.hidden = true; listToggleBtn?.setAttribute('aria-pressed', 'false'); return; }
      if (dragging3DItem) { dragging3DItem = null; showToast('Movimento cancelado'); return; }
      if (selectedSurfaceSlot || getPlan()?.getSelected()) {
        selectedSurfaceSlot = null;
        getPlan()?.clearSelection();
        clearSelectionGizmo();
        hideSelectionPill();
        updatePromptContext();
      }
    }
  });

  return {
    bindModel,
    handleSceneClick,
    setRenovateMode,
    isRenovateMode: () => renovateMode,
    setWalkMode,
    isWalkMode: () => walkMode,
    openPhotoModal,
    getLightIntensity: () => lightIntensity,
    onFurnitureSelectionChange(item) {
      if (item && renovateMode) {
        updateSelectionGizmo(item);
        showObjectPill(item);
      } else if (!item) {
        clearSelectionGizmo();
        if (!selectedSurfaceSlot) hideSelectionPill();
        updatePromptContext();
      }
      renderListDrawer();
    },
    onFurnitureListChange() {
      renderListDrawer();
    },
  };
}
