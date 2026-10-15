import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Farm v5", page_icon="🌾", layout="wide")
st.title("🌾 Pixel Farm v5 - Suara Gede!")
st.caption("**Klik tile** buat kerja • **Drag** buat banyak • **1/2/3/4** pilih tool (tekan lagi = unequip) • **M** mute • **+/-** atur volume")

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; background:#0a0a1e; font-family:monospace; overflow:hidden; }
  #wrap { display:flex; justify-content:center; align-items:center; height:100vh; }
  canvas {
    image-rendering:pixelated;
    border:4px solid #0f0;
    box-shadow:0 0 30px #0f0;
    background:#000;
    cursor:crosshair;
  }
  #hud {
    position:absolute; top:10px; left:10px;
    color:#0f0; font-size:16px;
    text-shadow:0 0 5px #0f0; pointer-events:none;
    line-height:1.8;
  }
  #hud b { color:#ffed4a; text-shadow:0 0 8px #ffed4a; }
  #toolbar {
    position:absolute; bottom:20px; left:50%; transform:translateX(-50%);
    display:flex; gap:8px; align-items:center;
    background:rgba(0,0,0,0.85); padding:8px;
    border:2px solid #0f0; border-radius:6px;
  }
  .tool {
    padding:8px 16px;
    background:rgba(20,20,40,0.9);
    border:2px solid #444;
    color:#ccc; font-family:monospace; font-size:14px;
    cursor:pointer; border-radius:4px;
    user-select:none;
    transition:all 0.1s;
    position:relative;
  }
  .tool:hover {
    background:rgba(40,40,80,0.9);
    border-color:#888;
  }
  .tool.active {
    background:rgba(0,80,0,0.6);
    border-color:#ffed4a;
    color:#ffed4a;
    box-shadow:0 0 10px #ffed4a;
    font-weight:bold;
  }
  .tool .key {
    color:#888; font-size:11px; margin-left:4px;
  }
  .tool.active .key { color:#ffed4a; }
  .tool.active::after {
    content:'✓';
    position:absolute; top:-8px; right:-8px;
    background:#ffed4a; color:#000;
    width:18px; height:18px; border-radius:50%;
    font-size:12px; line-height:18px; text-align:center;
    font-weight:bold;
  }
  #volBox {
    display:flex; align-items:center; gap:6px;
    padding:0 8px; border-left:2px solid #444;
    margin-left:4px;
  }
  #volBox span { color:#ffed4a; font-size:14px; }
  #volSlider {
    width:100px; cursor:pointer;
    accent-color:#ffed4a;
  }
  #muteBtn {
    background:rgba(20,20,40,0.9);
    border:2px solid #444;
    color:#ffed4a; font-family:monospace;
    font-size:16px; padding:6px 10px;
    cursor:pointer; border-radius:4px;
  }
  #muteBtn:hover { border-color:#ffed4a; }
  #muteBtn.muted { color:#f44; border-color:#f44; }
  #toast {
    position:absolute; top:80px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.9); border:2px solid #ffed4a;
    color:#ffed4a; padding:10px 20px; font-size:16px;
    display:none; text-shadow:0 0 5px #ffed4a;
    pointer-events:none;
  }
  #hint {
    position:absolute; bottom:10px; right:10px;
    color:#888; font-size:11px;
    text-shadow:0 0 3px #000;
    text-align:right; line-height:1.6;
  }
</style>
</head>
<body>
<div id="hud">
  🪙 Gold: <b><span id="gold">0</span></b><br>
  🌾 Gandum: <b><span id="wheat">0</span></b><br>
  <span style="font-size:12px;color:#0a0">Tekan <b style="color:#ffed4a">J</b> = jual semua</span>
</div>
<div id="toolbar">
  <div class="tool" data-tool="hoe">🪓 Hoe <span class="key">[1]</span></div>
  <div class="tool" data-tool="seed">🌱 Seed <span class="key">[2]</span></div>
  <div class="tool" data-tool="water">💧 Water <span class="key">[3]</span></div>
  <div class="tool" data-tool="harvest">🌾 Harvest <span class="key">[4]</span></div>
  <div id="volBox">
    <span>🔊</span>
    <input type="range" id="volSlider" min="0" max="100" value="80">
    <span id="volValue">80%</span>
    <button id="muteBtn">🔊</button>
  </div>
</div>
<div id="toast"></div>
<div id="hint">
  M = mute • +/- = volume<br>
  Klik canvas dulu biar ada suara
</div>
<div id="wrap">
  <canvas id="game" width="720" height="520"></canvas>
</div>

<script>
// ==== AUDIO ENGINE ====
let audioCtx = null;
let masterGain = null;
let musicGain = null;
let sfxGain = null;
let musicPlaying = false;
let muted = false;
let masterVolume = 0.8; // 0-1

function initAudio() {
  if (audioCtx) return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();

  // Master gain (volume global)
  masterGain = audioCtx.createGain();
  masterGain.gain.value = masterVolume;
  masterGain.connect(audioCtx.destination);

  // Musik channel (lebih gede: 0.25)
  musicGain = audioCtx.createGain();
  musicGain.gain.value = 0.25;
  musicGain.connect(masterGain);

  // SFX channel (jauh lebih gede: 0.5)
  sfxGain = audioCtx.createGain();
  sfxGain.gain.value = 0.5;
  sfxGain.connect(masterGain);

  startMusic();
}

// ==== SFX (lebih punchy dengan multi-layer) ====
function playTone(freq, duration, type='square', vol=1) {
  if (!audioCtx || muted) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.value = 0.001;
  gain.gain.exponentialRampToValueAtTime(0.3 * vol, audioCtx.currentTime + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.connect(gain);
  gain.connect(sfxGain);
  osc.start();
  osc.stop(audioCtx.currentTime + duration);
}

// Noise burst buat suara "cangkul" yang lebih real
function playNoise(duration, vol=1) {
  if (!audioCtx || muted) return;
  const bufferSize = audioCtx.sampleRate * duration;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * (1 - i/bufferSize);
  }
  const src = audioCtx.createBufferSource();
  src.buffer = buffer;
  const gain = audioCtx.createGain();
  gain.gain.value = 0.4 * vol;
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = 800;
  src.connect(filter);
  filter.connect(gain);
  gain.connect(sfxGain);
  src.start();
}

function sfxHoe() {
  // Suara cangkul: noise + bass thud
  playNoise(0.15, 1);
  playTone(100, 0.2, 'sawtooth', 1.2);
  setTimeout(() => playTone(70, 0.15, 'sawtooth', 0.9), 40);
}

function sfxSeed() {
  playTone(700, 0.1, 'sine', 1.2);
  setTimeout(() => playTone(950, 0.08, 'sine', 1), 40);
}

function sfxWater() {
  playTone(1100, 0.2, 'sine', 1.2);
  setTimeout(() => playTone(800, 0.12, 'sine', 1), 60);
  setTimeout(() => playTone(550, 0.1, 'sine', 0.9), 120);
}

function sfxHarvest() {
  playTone(523, 0.1, 'square', 1.2);      // C5
  setTimeout(() => playTone(659, 0.1, 'square', 1.2), 70);  // E5
  setTimeout(() => playTone(784, 0.15, 'square', 1.2), 140); // G5
  setTimeout(() => playTone(1047, 0.2, 'square', 1.2), 210); // C6
}

function sfxSell() {
  playTone(988, 0.08, 'square', 1.2);
  setTimeout(() => playTone(1319, 0.2, 'square', 1.2), 70);
  setTimeout(() => playTone(1568, 0.15, 'square', 1), 150);
}

function sfxError() {
  playTone(180, 0.2, 'sawtooth', 1);
}

function sfxClick() {
  playTone(1400, 0.04, 'square', 0.8);
}

function sfxUnequip() {
  playTone(500, 0.06, 'triangle', 0.8);
  setTimeout(() => playTone(300, 0.08, 'triangle', 0.7), 50);
}

// ==== CHIPTUNE BGM (volume lebih gede) ====
const melody = [
  {n: 'C5', d: 0.15}, {n: 'E5', d: 0.15}, {n: 'G5', d: 0.15}, {n: 'E5', d: 0.15},
  {n: 'A4', d: 0.15}, {n: 'C5', d: 0.15}, {n: 'E5', d: 0.15}, {n: 'C5', d: 0.15},
  {n: 'F4', d: 0.15}, {n: 'A4', d: 0.15}, {n: 'C5', d: 0.15}, {n: 'A4', d: 0.15},
  {n: 'G4', d: 0.15}, {n: 'B4', d: 0.15}, {n: 'D5', d: 0.15}, {n: 'B4', d: 0.15},
  {n: 'C5', d: 0.15}, {n: 'E5', d: 0.15}, {n: 'G5', d: 0.15}, {n: 'C6', d: 0.15},
  {n: 'A5', d: 0.15}, {n: 'E5', d: 0.15}, {n: 'C5', d: 0.3},
  {n: 'F5', d: 0.15}, {n: 'C5', d: 0.15}, {n: 'A4', d: 0.3},
  {n: 'G5', d: 0.15}, {n: 'D5', d: 0.15}, {n: 'B4', d: 0.3},
];

const bass = [
  {n: 'C3', d: 0.3}, {n: 'C3', d: 0.3}, {n: 'A2', d: 0.3}, {n: 'A2', d: 0.3},
  {n: 'F2', d: 0.3}, {n: 'F2', d: 0.3}, {n: 'G2', d: 0.3}, {n: 'G2', d: 0.3},
  {n: 'C3', d: 0.3}, {n: 'C3', d: 0.3}, {n: 'A2', d: 0.3}, {n: 'A2', d: 0.3},
  {n: 'F2', d: 0.3}, {n: 'F2', d: 0.3}, {n: 'G2', d: 0.3}, {n: 'G2', d: 0.3},
];

const noteFreq = {
  'A2':110, 'B2':123.47, 'C3':130.81, 'D3':146.83, 'E3':164.81, 'F3':174.61, 'G3':196,
  'A3':220, 'B3':246.94, 'C4':261.63, 'D4':293.66, 'E4':329.63, 'F4':349.23, 'G4':392,
  'A4':440, 'B4':493.88, 'C5':523.25, 'D5':587.33, 'E5':659.25, 'F5':698.46, 'G5':783.99,
  'A5':880, 'B5':987.77, 'C6':1046.50
};

function scheduleNote(freq, startTime, duration, type, vol) {
  if (!audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(0.001, startTime);
  gain.gain.exponentialRampToValueAtTime(vol, startTime + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration - 0.02);
  osc.connect(gain);
  gain.connect(musicGain);
  osc.start(startTime);
  osc.stop(startTime + duration);
}

let musicLoopTimer = null;
function startMusic() {
  if (musicPlaying || !audioCtx) return;
  musicPlaying = true;
  playMusicLoop();
}

function playMusicLoop() {
  if (!audioCtx || !musicPlaying) return;

  const start = audioCtx.currentTime + 0.05;

  let t = start;
  for (const note of melody) {
    if (noteFreq[note.n]) {
      scheduleNote(noteFreq[note.n], t, note.d * 0.9, 'square', 0.6);
    }
    t += note.d;
  }
  const melodyDuration = t - start;

  let bt = start;
  for (const note of bass) {
    if (noteFreq[note.n]) {
      scheduleNote(noteFreq[note.n], bt, note.d * 0.9, 'triangle', 0.9);
    }
    bt += note.d;
  }

  const loopDuration = Math.max(melodyDuration, bt - start);
  musicLoopTimer = setTimeout(() => {
    if (musicPlaying) playMusicLoop();
  }, loopDuration * 1000);
}

// ==== VOLUME CONTROL ====
const volSlider = document.getElementById('volSlider');
const volValue = document.getElementById('volValue');
const muteBtn = document.getElementById('muteBtn');

volSlider.addEventListener('input', e => {
  masterVolume = parseInt(e.target.value) / 100;
  volValue.textContent = e.target.value + '%';
  if (masterGain && !muted) {
    masterGain.gain.value = masterVolume;
  }
  // Update tombol mute visual
  if (masterVolume === 0) {
    muteBtn.classList.add('muted');
  } else if (!muted) {
    muteBtn.classList.remove('muted');
  }
});

muteBtn.addEventListener('click', () => toggleMute());

function toggleMute() {
  muted = !muted;
  if (muted) {
    muteBtn.textContent = '🔇';
    muteBtn.classList.add('muted');
    if (masterGain) masterGain.gain.value = 0;
  } else {
    muteBtn.textContent = '🔊';
    muteBtn.classList.remove('muted');
    if (masterGain) masterGain.gain.value = masterVolume;
  }
}

// ==== MAIN GAME ====
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PX = 5;
const TILE = 16;
const WORLD_W = 30;
const WORLD_H = 22;

const T_GRASS = 0;
const T_PATH = 1;
const T_WATER = 2;
const T_TREE = 3;
const T_FARMLAND = 4;
const T_CROP = 5;

let world = [];
function generateWorld() {
  world = [];
  for (let y=0; y<WORLD_H; y++) {
    let row = [];
    for (let x=0; x<WORLD_W; x++) {
      let t = T_GRASS;
      if (x >= WORLD_W - 2) t = T_WATER;
      else if (Math.random() < 0.04) t = T_TREE;
      row.push(t);
    }
    world.push(row);
  }
  for (let y=WORLD_H-6; y<WORLD_H-2; y++)
    for (let x=8; x<20; x++)
      world[y][x] = T_GRASS;
  for (let x=0; x<WORLD_W; x++) world[10][x] = T_PATH;
}
generateWorld();

const crops = {};

const player = {
  x: 12 * TILE, y: 14 * TILE,
  w: 10, h: 14, speed: 1.6,
  dir: 'down', animTimer: 0, walkFrame: 0,
};

const inv = { gold: 0, wheat: 0 };
const camera = { x: 0, y: 0 };

let currentTool = null;

// ==== MOUSE ====
let mouse = { x: 0, y: 0, tx: 0, ty: 0, inside: false };
let isMouseDown = false;
let lastDragTile = null;

canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;
  mouse.tx = Math.floor((mouse.x / PX + camera.x) / TILE);
  mouse.ty = Math.floor((mouse.y / PX + camera.y) / TILE);
  mouse.inside = true;

  if (isMouseDown) {
    const tileKey = `${mouse.tx},${mouse.ty}`;
    if (tileKey !== lastDragTile) {
      applyTool(mouse.tx, mouse.ty);
      lastDragTile = tileKey;
    }
  }
});

canvas.addEventListener('mouseleave', () => {
  mouse.inside = false;
  isMouseDown = false;
  lastDragTile = null;
});

canvas.addEventListener('mousedown', e => {
  if (e.button !== 0) return;
  if (!audioCtx) initAudio();
  if (audioCtx.state === 'suspended') audioCtx.resume();

  isMouseDown = true;
  applyTool(mouse.tx, mouse.ty);
  lastDragTile = `${mouse.tx},${mouse.ty}`;
});

canvas.addEventListener('mouseup', () => {
  isMouseDown = false;
  lastDragTile = null;
});

// ==== TOOLBAR ====
document.querySelectorAll('.tool').forEach(el => {
  el.addEventListener('click', () => {
    if (!audioCtx) initAudio();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    toggleTool(el.dataset.tool);
  });
});

function toggleTool(tool) {
  if (currentTool === tool) {
    currentTool = null;
    showToast('🚫 Tool dilepas', '#888');
    sfxUnequip();
  } else {
    currentTool = tool;
    const names = { hoe: '🪓 Hoe', seed: '🌱 Seed', water: '💧 Water', harvest: '🌾 Harvest' };
    showToast(`${names[tool]} dipilih`, '#ffed4a');
    sfxClick();
  }
  updateToolbarUI();
}

function updateToolbarUI() {
  document.querySelectorAll('.tool').forEach(el => {
    el.classList.toggle('active', el.dataset.tool === currentTool);
  });
}

// ==== KEYBOARD ====
const keys = {};
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;

  if (e.key === '1') toggleTool('hoe');
  if (e.key === '2') toggleTool('seed');
  if (e.key === '3') toggleTool('water');
  if (e.key === '4') toggleTool('harvest');
  if (e.key === 'j' || e.key === 'J') sellWheat();
  if (e.key === 'm' || e.key === 'M') toggleMute();

  // Volume shortcut: + dan -
  if (e.key === '+' || e.key === '=') {
    masterVolume = Math.min(1, masterVolume + 0.1);
    volSlider.value = Math.round(masterVolume * 100);
    volValue.textContent = Math.round(masterVolume * 100) + '%';
    if (masterGain && !muted) masterGain.gain.value = masterVolume;
    showToast(`🔊 Volume: ${Math.round(masterVolume*100)}%`, '#ffed4a');
  }
  if (e.key === '-' || e.key === '_') {
    masterVolume = Math.max(0, masterVolume - 0.1);
    volSlider.value = Math.round(masterVolume * 100);
    volValue.textContent = Math.round(masterVolume * 100) + '%';
    if (masterGain && !muted) masterGain.gain.value = masterVolume;
    showToast(`🔊 Volume: ${Math.round(masterVolume*100)}%`, '#ffed4a');
  }

  if (['arrowup','arrowdown','arrowleft','arrowright'].includes(e.key)) e.preventDefault();
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

// ==== TOAST ====
function showToast(msg, color='#ffed4a') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.color = color;
  t.style.borderColor = color;
  t.style.textShadow = `0 0 5px ${color}`;
  t.style.display = 'block';
  clearTimeout(t._timeout);
  t._timeout = setTimeout(() => t.style.display = 'none', 1000);
}

// ==== APPLY TOOL ====
function applyTool(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;

  if (!currentTool) {
    if (world[ty][tx] === T_CROP && crops[`${tx},${ty}`] && crops[`${tx},${ty}`].stage >= 3) {
      showToast('💡 Pilih tool Harvest dulu [4]', '#ffed4a');
    } else {
      showToast('💡 Pilih tool dulu [1-4]', '#ffed4a');
    }
    return;
  }

  const t = world[ty][tx];
  const key = `${tx},${ty}`;

  if (currentTool === 'hoe') {
    if (t === T_GRASS) {
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHoe();
      showToast('🪓 Dicangkul!', '#a07040');
    } else {
      sfxError();
    }
  } else if (currentTool === 'seed') {
    if (t === T_FARMLAND) {
      world[ty][tx] = T_CROP;
      crops[key] = { stage: 0, watered: false, timer: 0 };
      sfxSeed();
      showToast('🌱 Ditanam!', '#5aff5a');
    } else {
      sfxError();
    }
  } else if (currentTool === 'water') {
    if (t === T_CROP && crops[key] && crops[key].stage < 3) {
      if (!crops[key].watered) {
        crops[key].watered = true;
        sfxWater();
        showToast('💧 Disiram!', '#4a90e2');
      }
    } else {
      sfxError();
    }
  } else if (currentTool === 'harvest') {
    if (t === T_CROP && crops[key] && crops[key].stage >= 3) {
      inv.wheat++;
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHarvest();
      showToast('🌾 Panen! +1', '#ffed4a');
      updateHUD();
    } else {
      sfxError();
    }
  }
}

function sellWheat() {
  if (inv.wheat === 0) {
    sfxError();
    showToast('❌ Nggak ada gandum', '#ff4444');
    return;
  }
  const earn = inv.wheat * 10;
  inv.gold += earn;
  sfxSell();
  showToast(`🪙 +${earn} gold!`, '#ffed4a');
  inv.wheat = 0;
  updateHUD();
}

// ==== COLLISION ====
function isSolid(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return true;
  const t = world[ty][tx];
  return t === T_WATER || t === T_TREE;
}

function canMoveTo(nx, ny) {
  const corners = [
    {x: nx, y: ny},
    {x: nx + player.w - 1, y: ny},
    {x: nx, y: ny + player.h - 1},
    {x: nx + player.w - 1, y: ny + player.h - 1},
  ];
  return corners.every(c =>
    !isSolid(Math.floor(c.x/TILE), Math.floor(c.y/TILE))
  );
}

// ==== UPDATE ====
let frameCount = 0;
function update() {
  frameCount++;

  let dx = 0, dy = 0;
  if (keys['arrowleft'] || keys['a']) dx -= player.speed;
  if (keys['arrowright'] || keys['d']) dx += player.speed;
  if (keys['arrowup'] || keys['w']) dy -= player.speed;
  if (keys['arrowdown'] || keys['s']) dy += player.speed;

  if (dx !== 0 || dy !== 0) {
    if (dx !== 0 && canMoveTo(player.x + dx, player.y)) player.x += dx;
    if (dy !== 0 && canMoveTo(player.x, player.y + dy)) player.y += dy;
    if (Math.abs(dx) > Math.abs(dy)) player.dir = dx > 0 ? 'right' : 'left';
    else player.dir = dy > 0 ? 'down' : 'up';
    player.animTimer++;
    if (player.animTimer > 7) {
      player.animTimer = 0;
      player.walkFrame = (player.walkFrame + 1) % 4;
    }
  } else {
    player.walkFrame = 0;
    player.animTimer = 0;
  }

  Object.keys(crops).forEach(k => {
    const c = crops[k];
    if (c.stage >= 0 && c.stage < 3) {
      c.timer = (c.timer || 0) + (c.watered ? 2 : 1);
      if (c.timer > 180) {
        c.stage++;
        c.timer = 0;
        c.watered = false;
      }
    }
  });

  const tx = player.x - canvas.width / (2*PX) + player.w/2;
  const ty = player.y - canvas.height / (2*PX) + player.h/2;
  camera.x += (tx - camera.x) * 0.15;
  camera.y += (ty - camera.y) * 0.15;
  camera.x = Math.max(0, Math.min(WORLD_W*TILE - canvas.width/PX, camera.x));
  camera.y = Math.max(0, Math.min(WORLD_H*TILE - canvas.height/PX, camera.y));

  if (mouse.inside) {
    mouse.tx = Math.floor((mouse.x / PX + camera.x) / TILE);
    mouse.ty = Math.floor((mouse.y / PX + camera.y) / TILE);
  }
}

function updateHUD() {
  document.getElementById('gold').textContent = inv.gold;
  document.getElementById('wheat').textContent = inv.wheat;
}

// ==== DRAW ====
function artPx(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(
    Math.floor((x - camera.x) * PX),
    Math.floor((y - camera.y) * PX),
    w*PX, h*PX
  );
}

function drawTile(t, x, y) {
  const wx = x * TILE;
  const wy = y * TILE;

  if (t === T_GRASS) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+2, wy+3, 1, 1, '#4a9d54');
    artPx(wx+10, wy+6, 1, 1, '#4a9d54');
    artPx(wx+6, wy+11, 1, 1, '#2d5f35');
  } else if (t === T_PATH) {
    artPx(wx, wy, TILE, TILE, '#8b6f47');
    artPx(wx+3, wy+5, 1, 1, '#6f5638');
    artPx(wx+9, wy+9, 1, 1, '#6f5638');
  } else if (t === T_WATER) {
    artPx(wx, wy, TILE, TILE, '#2a5db0');
    const wave = Math.sin(frameCount*0.05 + x + y) * 2;
    artPx(wx+3+wave, wy+4, 3, 1, '#4a7dd0');
    artPx(wx+9-wave, wy+10, 3, 1, '#4a7dd0');
  } else if (t === T_TREE) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+6, wy+10, 4, 6, '#5a3a1a');
    artPx(wx+2, wy+2, 12, 10, '#1e5a2a');
    artPx(wx+3, wy+1, 10, 2, '#2d7d3a');
    artPx(wx+4, wy+3, 3, 3, '#4a9d54');
  } else if (t === T_FARMLAND) {
    artPx(wx, wy, TILE, TILE, '#6b4423');
    artPx(wx, wy+3, TILE, 1, '#4a2f18');
    artPx(wx, wy+7, TILE, 1, '#4a2f18');
    artPx(wx, wy+11, TILE, 1, '#4a2f18');
    artPx(wx, wy+15, TILE, 1, '#4a2f18');
    artPx(wx, wy+4, TILE, 1, '#8b5a2b');
    artPx(wx, wy+8, TILE, 1, '#8b5a2b');
  } else if (t === T_CROP) {
    artPx(wx, wy, TILE, TILE, '#6b4423');
    artPx(wx, wy+3, TILE, 1, '#4a2f18');
    artPx(wx, wy+7, TILE, 1, '#4a2f18');
    artPx(wx, wy+11, TILE, 1, '#4a2f18');
    artPx(wx, wy+15, TILE, 1, '#4a2f18');

    const c = crops[`${x},${y}`];
    const stage = c ? c.stage : 0;
    const cx = wx + 6;
    const cy = wy + 6;

    if (stage === 0) {
      artPx(cx+1, cy+6, 2, 3, '#5aff5a');
      artPx(cx, cy+5, 1, 2, '#3a9d3a');
    } else if (stage === 1) {
      artPx(cx+1, cy+3, 2, 6, '#5aff5a');
      artPx(cx, cy+2, 1, 4, '#3a9d3a');
      artPx(cx+3, cy+2, 1, 4, '#3a9d3a');
    } else if (stage === 2) {
      artPx(cx+1, cy+0, 2, 9, '#7fd77f');
      artPx(cx, cy-1, 1, 7, '#5aa55a');
      artPx(cx+3, cy-1, 1, 7, '#5aa55a');
      artPx(cx+1, cy-1, 2, 2, '#d4d44a');
    } else if (stage >= 3) {
      const glow = Math.sin(frameCount*0.1) * 0.3 + 0.7;
      ctx.shadowColor = '#ffed4a';
      ctx.shadowBlur = 15 * glow;
      artPx(cx+1, cy-2, 2, 11, '#e8c850');
      artPx(cx, cy-3, 1, 9, '#c8a830');
      artPx(cx+3, cy-3, 1, 9, '#c8a830');
      artPx(cx, cy-4, 4, 3, '#ffed4a');
      artPx(cx+1, cy-5, 2, 2, '#fff59d');
      ctx.shadowBlur = 0;
    }
  }
}

function drawHumanoid(x, y, dir, walkFrame, color) {
  const skin = '#ffcc99';
  const shirt = color;
  const pants = '#1a3a8a';
  const hair = '#3a2010';
  const bob = (walkFrame === 1 || walkFrame === 3) ? -1 : 0;

  ctx.globalAlpha = 0.3;
  artPx(x+2, y+15, 8, 2, '#000');
  ctx.globalAlpha = 1;

  artPx(x+3, y+0+bob, 6, 6, skin);
  if (dir === 'down') {
    artPx(x+3, y+0+bob, 6, 2, hair);
    artPx(x+4, y+3+bob, 1, 1, '#000');
    artPx(x+7, y+3+bob, 1, 1, '#000');
  } else if (dir === 'up') {
    artPx(x+3, y+0+bob, 6, 4, hair);
  } else if (dir === 'left') {
    artPx(x+3, y+0+bob, 6, 2, hair);
    artPx(x+5, y+0+bob, 4, 4, hair);
    artPx(x+4, y+3+bob, 1, 1, '#000');
  } else {
    artPx(x+3, y+0+bob, 6, 2, hair);
    artPx(x+3, y+0+bob, 4, 4, hair);
    artPx(x+7, y+3+bob, 1, 1, '#000');
  }

  artPx(x+3, y+6+bob, 6, 5, shirt);
  artPx(x+2, y+7+bob, 1, 3, skin);
  artPx(x+9, y+7+bob, 1, 3, skin);

  const legY = y + 11 + bob;
  if (walkFrame === 1) {
    artPx(x+3, legY, 2, 5, pants);
    artPx(x+7, legY+1, 2, 4, pants);
  } else if (walkFrame === 3) {
    artPx(x+3, legY+1, 2, 4, pants);
    artPx(x+7, legY, 2, 5, pants);
  } else {
    artPx(x+3, legY, 2, 5, pants);
    artPx(x+7, legY, 2, 5, pants);
  }
  artPx(x+3, legY+4, 2, 1, '#000');
  artPx(x+7, legY+4, 2, 1, '#000');
}

function drawCursorHighlight() {
  if (!mouse.inside) return;
  const tx = mouse.tx;
  const ty = mouse.ty;
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;

  const wx = tx * TILE;
  const wy = ty * TILE;
  const px = Math.floor((wx - camera.x) * PX);
  const py = Math.floor((wy - camera.y) * PX);

  let color = '#444';
  let alpha = 0.3;

  if (currentTool) {
    const t = world[ty][tx];
    const key = `${tx},${ty}`;

    if (currentTool === 'hoe' && t === T_GRASS) { color = '#a07040'; alpha = 0.7; }
    else if (currentTool === 'seed' && t === T_FARMLAND) { color = '#5aff5a'; alpha = 0.7; }
    else if (currentTool === 'water' && t === T_CROP && crops[key] && !crops[key].watered && crops[key].stage < 3) { color = '#4a90e2'; alpha = 0.7; }
    else if (currentTool === 'harvest' && t === T_CROP && crops[key] && crops[key].stage >= 3) { color = '#ffed4a'; alpha = 0.9; }
    else { color = '#666'; alpha = 0.4; }
  }

  ctx.strokeStyle = color;
  ctx.lineWidth = currentTool ? 3 : 2;
  ctx.globalAlpha = alpha;
  ctx.strokeRect(px + 1, py + 1, TILE*PX - 2, TILE*PX - 2);

  ctx.globalAlpha = alpha * 0.3;
  ctx.fillStyle = color;
  ctx.fillRect(px, py, TILE*PX, TILE*PX);

  if (currentTool) {
    const t = world[ty][tx];
    const key = `${tx},${ty}`;
    let emoji = null;
    if (currentTool === 'hoe' && t === T_GRASS) emoji = '🪓';
    else if (currentTool === 'seed' && t === T_FARMLAND) emoji = '🌱';
    else if (currentTool === 'water' && t === T_CROP && crops[key] && !crops[key].watered && crops[key].stage < 3) emoji = '💧';
    else if (currentTool === 'harvest' && t === T_CROP && crops[key] && crops[key].stage >= 3) emoji = '🌾';

    if (emoji) {
      ctx.globalAlpha = 0.85;
      ctx.font = `${TILE * PX * 0.7}px serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(emoji, px + TILE*PX/2, py + TILE*PX/2);
    }
  }

  ctx.globalAlpha = 1;
}

function draw() {
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const startX = Math.max(0, Math.floor(camera.x / TILE) - 1);
  const endX = Math.min(WORLD_W, Math.ceil((camera.x + canvas.width/PX) / TILE) + 1);
  const startY = Math.max(0, Math.floor(camera.y / TILE) - 1);
  const endY = Math.min(WORLD_H, Math.ceil((camera.y + canvas.height/PX) / TILE) + 1);

  for (let y=startY; y<endY; y++)
    for (let x=startX; x<endX; x++)
      drawTile(world[y][x], x, y);

  drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2');

  drawCursorHighlight();

  const grad = ctx.createRadialGradient(
    canvas.width/2, canvas.height/2, 150,
    canvas.width/2, canvas.height/2, canvas.width
  );
  grad.addColorStop(0, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,0,0.5)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

// Init audio saat interaksi pertama
document.body.addEventListener('click', () => {
  if (!audioCtx) initAudio();
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
}, { once: false });

updateHUD();
updateToolbarUI();
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=620)
