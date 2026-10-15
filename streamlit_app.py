import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Farm RPG", page_icon="🌾", layout="wide")
st.title("🌾 Pixel Farm RPG - Realistic")
st.caption("**WASD** jalan • **Klik** action • **1-6** tool • **I** inventory • **M** mute")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#0a0a1e; font-family:'Courier New',monospace; overflow:hidden; color:#fff; }
  #gameWrap { position:relative; width:100vw; height:100vh; display:flex; justify-content:center; align-items:center; }
  canvas {
    image-rendering:pixelated;
    border:4px solid #2a2a3e;
    box-shadow:0 0 40px rgba(0,255,0,0.2);
    background:#000;
    cursor:crosshair;
  }
  #hud {
    position:absolute; top:12px; left:12px;
    display:flex; flex-direction:column; gap:6px;
    pointer-events:none; font-size:13px;
  }
  .bar {
    width:180px; height:22px; background:rgba(0,0,0,0.7);
    border:2px solid #222; border-radius:3px;
    position:relative; overflow:hidden;
    box-shadow:0 2px 8px rgba(0,0,0,0.5);
  }
  .bar .fill { height:100%; transition:width 0.3s; }
  .bar .label {
    position:absolute; top:0; left:8px;
    line-height:18px; font-size:12px; font-weight:bold;
    text-shadow:1px 1px 0 #000;
  }
  #hpFill { background:linear-gradient(180deg, #ff4444, #aa0000); }
  #hungerFill { background:linear-gradient(180deg, #ffaa00, #cc6600); }
  #topRight {
    position:absolute; top:12px; right:12px;
    background:rgba(0,0,0,0.7);
    border:2px solid #222; border-radius:4px;
    padding:8px 14px; font-size:13px;
    text-align:right; pointer-events:none;
    line-height:1.6;
  }
  #timeOfDay { color:#ffed4a; font-weight:bold; font-size:14px; text-shadow:0 0 8px currentColor; }
  #gold { color:#ffd700; font-weight:bold; text-shadow:0 0 8px #ffd700; }
  #toolbar {
    position:absolute; bottom:16px; left:50%; transform:translateX(-50%);
    display:flex; gap:6px; background:rgba(0,0,0,0.85);
    padding:8px; border:2px solid #2a2a3e; border-radius:8px;
  }
  .tool {
    padding:8px 12px; background:rgba(30,30,50,0.9);
    border:2px solid #333; color:#888;
    font-family:inherit; font-size:12px;
    cursor:pointer; border-radius:5px;
    user-select:none; transition:all 0.15s;
    min-width:60px; text-align:center; position:relative;
  }
  .tool:hover { background:rgba(50,50,80,0.9); border-color:#666; color:#ccc; transform:translateY(-2px); }
  .tool.active {
    background:linear-gradient(180deg, #2a5d2a, #1a3d1a);
    border-color:#ffed4a; color:#ffed4a;
    box-shadow:0 0 15px rgba(255,237,74,0.6);
    font-weight:bold;
  }
  .tool .num { position:absolute; top:2px; left:5px; font-size:10px; color:#666; }
  .tool.active .num { color:#ffed4a; }
  #inv {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    background:rgba(15,15,25,0.97);
    border:3px solid #2a2a3e; border-radius:10px;
    padding:20px; display:none;
    box-shadow:0 0 40px rgba(0,0,0,0.9); z-index:100; min-width:400px;
  }
  #inv h2 { color:#ffed4a; margin:0 0 16px 0; font-size:18px; border-bottom:2px solid #2a2a3e; padding-bottom:8px; }
  #invGrid { display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; }
  .invSlot {
    aspect-ratio:1; background:rgba(30,30,50,0.7);
    border:2px solid #333; border-radius:6px;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    cursor:pointer; transition:all 0.15s;
    position:relative; min-height:60px;
  }
  .invSlot:hover { border-color:#ffed4a; background:rgba(50,50,80,0.9); transform:scale(1.05); }
  .invSlot .emoji { font-size:24px; line-height:1; }
  .invSlot .name { font-size:9px; color:#aaa; margin-top:2px; }
  .invSlot .count {
    position:absolute; bottom:2px; right:4px;
    font-size:11px; font-weight:bold; color:#ffed4a;
    text-shadow:1px 1px 0 #000;
  }
  #invHint { margin-top:12px; font-size:11px; color:#666; text-align:center; }
  #dialog {
    position:absolute; bottom:90px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.92); border:3px solid #ffed4a;
    color:#ffed4a; padding:14px 24px; font-size:15px;
    display:none; min-width:400px; text-align:center;
    box-shadow:0 0 30px rgba(255,237,74,0.4);
    border-radius:6px; max-width:600px;
  }
  #toast {
    position:absolute; top:100px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.9); border:2px solid #ffed4a;
    color:#ffed4a; padding:10px 20px; font-size:15px;
    display:none; box-shadow:0 0 20px rgba(255,237,74,0.5);
    border-radius:4px; pointer-events:none; font-weight:bold;
  }
  #damageFlash {
    position:absolute; inset:0;
    background:radial-gradient(circle, transparent 30%, rgba(255,0,0,0.6) 100%);
    opacity:0; pointer-events:none; transition:opacity 0.2s;
  }
  #hint { position:absolute; bottom:12px; right:12px; font-size:11px; color:#555; text-align:right; line-height:1.6; }
  #muteIcon {
    position:absolute; bottom:12px; left:12px;
    font-size:20px; cursor:pointer; padding:6px;
    user-select:none; transition:transform 0.2s;
  }
  #muteIcon:hover { transform:scale(1.2); }
  #stats {
    position:absolute; top:12px; left:210px;
    font-size:11px; color:#888;
    background:rgba(0,0,0,0.6);
    padding:6px 10px; border-radius:4px;
    border:1px solid #222; pointer-events:none;
    line-height:1.5;
  }
</style>
</head>
<body>
<div id="gameWrap">
  <canvas id="game" width="800" height="560"></canvas>
  <div id="damageFlash"></div>
  <div id="hud">
    <div class="bar">
      <div class="fill" id="hpFill" style="width:100%"></div>
      <div class="label">❤️ <span id="hpText">100/100</span></div>
    </div>
    <div class="bar">
      <div class="fill" id="hungerFill" style="width:100%"></div>
      <div class="label">🍗 <span id="hungerText">100/100</span></div>
    </div>
  </div>
  <div id="topRight">
    <div id="timeOfDay">🌅 Pagi</div>
    <div>Day <span id="dayNum">1</span> — <span id="clock">06:00</span></div>
    <div>🪙 <span id="gold">0</span></div>
  </div>
  <div id="stats">
    🪵 <span id="wood">0</span> · 🍗 <span id="food">0</span> · 🌾 <span id="wheat">0</span>
  </div>
  <div id="toolbar">
    <div class="tool" data-tool="hoe"><span class="num">1</span>🪓<br>Hoe</div>
    <div class="tool" data-tool="seed"><span class="num">2</span>🌱<br>Seed</div>
    <div class="tool" data-tool="water"><span class="num">3</span>💧<br>Water</div>
    <div class="tool" data-tool="harvest"><span class="num">4</span>🌾<br>Harvest</div>
    <div class="tool" data-tool="axe"><span class="num">5</span>🪓<br>Axe</div>
    <div class="tool" data-tool="weapon"><span class="num">6</span>⚔️<br>Attack</div>
  </div>
  <div id="inv">
    <h2>🎒 Inventory</h2>
    <div id="invGrid"></div>
    <div id="invHint">Klik food buat makan · Klik wood/wheat buat jual</div>
  </div>
  <div id="dialog"></div>
  <div id="toast"></div>
  <div id="muteIcon">🔊</div>
  <div id="hint">
    WASD = jalan • Klik = action • 1-6 = tool<br>
    I = inventory • M = mute
  </div>
</div>

<script>
// ============================================
// ==== AUDIO ENGINE ====
// ============================================
let audioCtx = null;
let masterGain = null;
let musicGain = null;
let sfxGain = null;
let musicPlaying = false;
let musicTimer = null;
let muted = false;
let masterVolume = 0.7;
let currentMusicPhase = 'dawn';

function initAudio() {
  if (audioCtx) return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  masterGain = audioCtx.createGain();
  masterGain.gain.value = masterVolume;
  masterGain.connect(audioCtx.destination);
  musicGain = audioCtx.createGain();
  musicGain.gain.value = 0.20;
  musicGain.connect(masterGain);
  sfxGain = audioCtx.createGain();
  sfxGain.gain.value = 0.4;
  sfxGain.connect(masterGain);
  startMusic('dawn');
}

function playTone(freq, duration, type='square', vol=1, when=0) {
  if (!audioCtx || muted) return;
  const t = audioCtx.currentTime + when;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(0.001, t);
  gain.gain.exponentialRampToValueAtTime(0.25 * vol, t + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.001, t + duration);
  osc.connect(gain);
  gain.connect(sfxGain);
  osc.start(t);
  osc.stop(t + duration + 0.05);
}

function playNoise(duration, vol=1, filterFreq=800) {
  if (!audioCtx || muted) return;
  const bufferSize = audioCtx.sampleRate * duration;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) data[i] = (Math.random()*2-1) * (1-i/bufferSize);
  const src = audioCtx.createBufferSource();
  src.buffer = buffer;
  const gain = audioCtx.createGain();
  gain.gain.value = 0.3 * vol;
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = filterFreq;
  src.connect(filter); filter.connect(gain); gain.connect(sfxGain);
  src.start();
}

function sfxHoe() { playNoise(0.14, 1, 900); playTone(110, 0.18, 'sawtooth', 1); playTone(75, 0.15, 'sawtooth', 0.8, 0.04); }
function sfxSeed() { playTone(700, 0.08, 'sine', 1); playTone(950, 0.1, 'sine', 0.9, 0.05); }
function sfxWater() { playTone(1100, 0.15, 'sine', 1); playTone(800, 0.12, 'sine', 0.9, 0.06); playTone(550, 0.12, 'sine', 0.8, 0.12); }
function sfxHarvest() { playTone(523, 0.1, 'square', 1); playTone(659, 0.1, 'square', 1, 0.07); playTone(784, 0.13, 'square', 1, 0.14); playTone(1047, 0.18, 'square', 1, 0.21); }
function sfxSell() { playTone(988, 0.07, 'square', 1); playTone(1319, 0.15, 'square', 1, 0.06); playTone(1568, 0.12, 'square', 0.9, 0.14); }
function sfxError() { playTone(180, 0.15, 'sawtooth', 0.8); }
function sfxClick() { playTone(1400, 0.03, 'square', 0.6); }
function sfxAxe() { playNoise(0.2, 1.2, 1200); playTone(160, 0.15, 'square', 1); playTone(90, 0.2, 'square', 0.8, 0.05); }
function sfxHit() { playNoise(0.12, 0.8, 2000); playTone(400, 0.08, 'square', 0.8); }
function sfxAnimalHurt() { playTone(600, 0.1, 'sawtooth', 0.9); playTone(400, 0.15, 'sawtooth', 0.8, 0.08); }
function sfxEat() { playTone(300, 0.06, 'square', 0.9); playTone(400, 0.06, 'square', 0.9, 0.08); playTone(500, 0.08, 'square', 0.8, 0.16); }
function sfxHurt() { playTone(200, 0.2, 'sawtooth', 1); playTone(150, 0.2, 'sawtooth', 0.9, 0.1); }

const scales = {
  dawn: [261.63, 293.66, 329.63, 392, 440, 523.25],
  day: [392, 440, 493.88, 587.33, 659.25, 783.99],
  evening: [349.23, 392, 440, 523.25, 587.33, 698.46],
  night: [220, 246.94, 261.63, 329.63, 349.23, 440],
};

function startMusic(phase) {
  if (!audioCtx) return;
  if (musicPlaying && currentMusicPhase === phase) return;
  if (musicTimer) clearTimeout(musicTimer);
  musicPlaying = true;
  currentMusicPhase = phase;
  playMusicLoop();
}

function playMusicLoop() {
  if (!audioCtx || !musicPlaying) return;
  const scale = scales[currentMusicPhase] || scales.day;
  const isNight = currentMusicPhase === 'night';
  const isDawn = currentMusicPhase === 'dawn';
  const isEvening = currentMusicPhase === 'evening';

  // Tempo lebih lambat & chill
  const baseTempo = isNight ? 0.7 : isDawn ? 0.55 : isEvening ? 0.55 : 0.45;
  const noteDuration = baseTempo;

  const start = audioCtx.currentTime + 0.05;
  const notes = [];
  const totalNotes = 16;

  for (let i = 0; i < totalNotes; i++) {
    const isRest = Math.random() < (isNight ? 0.4 : 0.3);
    if (isRest) { notes.push(null); continue; }
    const note = scale[Math.floor(Math.random() * scale.length)];
    const octaveUp = Math.random() < 0.15 ? 2 : 1;
    notes.push(note * octaveUp);
  }

  notes.forEach((note, i) => {
    if (note === null) return;
    const t = start + i * noteDuration;
    const vol = isNight ? 0.3 : 0.45;
    const type = isNight ? 'triangle' : (isDawn ? 'sine' : 'square');
    scheduleNote(note, t, noteDuration * 0.85, type, vol);
  });

  const bassNote = scale[0] / 4;
  for (let i = 0; i < totalNotes; i += 4) {
    scheduleNote(bassNote, start + i * noteDuration, noteDuration * 3.5, 'triangle', 0.5);
  }

  const totalDuration = totalNotes * noteDuration;
  musicTimer = setTimeout(() => {
    if (musicPlaying) playMusicLoop();
  }, totalDuration * 1000);
}

function scheduleNote(freq, startTime, duration, type, vol) {
  if (!audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(0.001, startTime);
  gain.gain.exponentialRampToValueAtTime(vol, startTime + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
  osc.connect(gain); gain.connect(musicGain);
  osc.start(startTime); osc.stop(startTime + duration + 0.05);
}

// ============================================
// ==== GAME ====
// ============================================
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PX = 5;
const TILE = 16;
const WORLD_W = 40;
const WORLD_H = 30;

const T_GRASS = 0;
const T_PATH = 1;
const T_WATER = 2;
const T_TREE = 3;
const T_FARMLAND = 4;
const T_CROP = 5;
const T_HOUSE = 6;
const T_STUMP = 7;
const T_SAPLING = 8;
const T_HOUSE_DOOR = 9;
const T_FLOWER = 10;
const T_LAMP = 11;

let world = [];

function generateWorld() {
  world = [];
  for (let y=0; y<WORLD_H; y++) {
    let row = [];
    for (let x=0; x<WORLD_W; x++) {
      let t = T_GRASS;
      if (x >= WORLD_W - 2) t = T_WATER;
      else if (Math.random() < 0.05) t = T_TREE;
      else if (Math.random() < 0.04) t = T_FLOWER;
      row.push(t);
    }
    world.push(row);
  }

  // ==== VILLAGE (tengah) ====
  // Clear area village dulu
  for (let y=8; y<18; y++) {
    for (let x=4; x<WORLD_W-4; x++) {
      world[y][x] = T_GRASS;
    }
  }
  // Jalan horizontal
  for (let x=0; x<WORLD_W; x++) {
    world[13][x] = T_PATH;
    world[14][x] = T_PATH;
  }

  // Rumah 5x4 tile (lebih besar & proporsional)
  function drawHouse(x0, y0) {
    // Atap & dinding rumah
    for (let y=y0; y<y0+4; y++)
      for (let x=x0; x<x0+5; x++)
        world[y][x] = T_HOUSE;
    // Pintu di tengah bawah
    world[y0+3][x0+2] = T_HOUSE_DOOR;
  }
  drawHouse(4, 9);
  drawHouse(17, 9);
  drawHouse(30, 9);

  // Lampu jalan (jarang)
  for (let x=6; x<WORLD_W-6; x+=8) {
    if (world[12][x] === T_GRASS) world[12][x] = T_LAMP;
  }

  // Clear area spawn bawah
  for (let y=18; y<WORLD_H-2; y++)
    for (let x=15; x<25; x++) {
      if ([T_TREE, T_WATER, T_LAMP].includes(world[y][x])) world[y][x] = T_GRASS;
    }
}
generateWorld();

const crops = {};
const trees = {};
for (let y=0; y<WORLD_H; y++) {
  for (let x=0; x<WORLD_W; x++) {
    if (world[y][x] === T_TREE) trees[`${x},${y}`] = { stage: 3, timer: 0 };
  }
}

// ============================================
// ==== PLAYER (realistic speed) ====
// ============================================
const player = {
  x: 20 * TILE, y: 20 * TILE,
  w: 10, h: 14,
  speed: 1.0, // dari 1.7 → 1.0 (realistic)
  dir: 'down', animTimer: 0, walkFrame: 0,
  hp: 100, hpMax: 100,
  hunger: 100, hungerMax: 100,
};

// ============================================
// ==== TIME (LEBIH LAMBAT!) ====
// ============================================
// 1 hari game = 8 menit real = 480 detik
// 24 jam = 1440 menit game
// 1440 / 480 = 3 menit game per detik real
const time = {
  totalMinutes: 6 * 60,
  day: 1,
  minutesPerSecond: 3, // dari 30 → 3 (10x lebih lambat)
  phase: 'dawn',
};

function getTimeOfDay() {
  const h = Math.floor(time.totalMinutes / 60) % 24;
  if (h >= 5 && h < 9) return 'dawn';
  if (h >= 9 && h < 17) return 'day';
  if (h >= 17 && h < 20) return 'evening';
  return 'night';
}

function getClockString() {
  const h = Math.floor(time.totalMinutes / 60) % 24;
  const m = Math.floor(time.totalMinutes % 60);
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
}

const skyColors = {
  dawn:    { ambient: 'rgba(255,180,100,0.15)' },
  day:     { ambient: 'rgba(255,255,255,0.0)' },
  evening: { ambient: 'rgba(255,120,80,0.2)' },
  night:   { ambient: 'rgba(20,20,60,0.55)' },
};

function getDarkness() {
  const h = (time.totalMinutes / 60) % 24;
  // Smooth transition
  if (h >= 9 && h < 17) return 0;        // siang terang
  if (h >= 5 && h < 9) {                  // dawn fade in
    return 0.35 * (1 - (h - 5) / 4);
  }
  if (h >= 17 && h < 20) {                // evening fade out
    return 0.35 * ((h - 17) / 3) + 0.15;
  }
  return 0.6; // night
}

// ============================================
// ==== INVENTORY ====
// ============================================
const inventory = { wheat: 0, wood: 0, food: 0, seeds: 10 };

// ============================================
// ==== COLLISION ====
// ============================================
function isSolid(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return true;
  const t = world[ty][tx];
  return t === T_WATER || t === T_TREE || t === T_HOUSE || t === T_HOUSE_DOOR || t === T_LAMP || t === T_SAPLING;
}

function canMoveTo(nx, ny, w, h) {
  const corners = [
    {x: nx, y: ny},
    {x: nx + w - 1, y: ny},
    {x: nx, y: ny + h - 1},
    {x: nx + w - 1, y: ny + h - 1},
  ];
  return corners.every(c =>
    !isSolid(Math.floor(c.x/TILE), Math.floor(c.y/TILE))
  );
}

// ============================================
// ==== NPCs (SLOW + realistic wander) ====
// ============================================
const npcs = [
  { x: 8*TILE, y: 15*TILE, dir:'down', color:'#ff6b6b', name:'Budi',
    dialog:'Selamat datang di desa kami!',
    targetX: 8, targetY: 15, moveTimer: 3, speed: 0.3, // SLOW
    animTimer: 0, walkFrame: 0, isMoving: false },
  { x: 19*TILE, y: 15*TILE, dir:'left', color:'#4ecdc4', name:'Sari',
    dialog:'Hati-hati malam tiba. Jangan keluar desa.',
    targetX: 19, targetY: 15, moveTimer: 4, speed: 0.35,
    animTimer: 0, walkFrame: 0, isMoving: false },
  { x: 32*TILE, y: 15*TILE, dir:'right', color:'#ffe66d', name:'Pak Tani',
    dialog:'Tebang pohon buat kayu, jual buat gold.',
    targetX: 32, targetY: 15, moveTimer: 5, speed: 0.25,
    animTimer: 0, walkFrame: 0, isMoving: false },
];

// ============================================
// ==== ANIMALS (SLOW + wander) ====
// ============================================
const ANIMAL_TYPES = {
  rabbit: { color:'#f0e0d0', hp:20, speed:0.4, drop:'food', dropAmt:2, size:10 },
  chicken: { color:'#f5d76e', hp:15, speed:0.5, drop:'food', dropAmt:1, size:10 },
  cow: { color:'#e0d0b0', hp:40, speed:0.25, drop:'food', dropAmt:3, size:14 },
};

let animals = [];

function spawnAnimals() {
  animals = [];
  const types = ['rabbit', 'chicken', 'cow'];
  for (let i = 0; i < 8; i++) {
    const type = types[Math.floor(Math.random()*types.length)];
    let x, y, tries = 0;
    do {
      x = Math.floor(Math.random()*WORLD_W);
      y = Math.floor(Math.random()*WORLD_H);
      tries++;
    } while (tries < 50 && (world[y][x] !== T_GRASS || (Math.abs(x-20) < 5 && Math.abs(y-20) < 5)));
    const t = ANIMAL_TYPES[type];
    animals.push({
      x: x*TILE + 3, y: y*TILE + 3,
      type, hp: t.hp, hpMax: t.hp,
      vx: 0, vy: 0, speed: t.speed, dir: 'down',
      wanderTimer: 0, wanderAngle: 0,
      hurtFlash: 0, dead: false, size: t.size,
      animTimer: 0, walkFrame: 0,
      pauseTimer: 0, // pause antar langkah
    });
  }
}
spawnAnimals();

const camera = { x: 0, y: 0 };

// ============================================
// ==== INPUT ====
// ============================================
const keys = {};
let currentTool = null;
let showInventory = false;

document.addEventListener('keydown', e => {
  const k = e.key.toLowerCase();
  keys[k] = true;
  if (k === '1') toggleTool('hoe');
  if (k === '2') toggleTool('seed');
  if (k === '3') toggleTool('water');
  if (k === '4') toggleTool('harvest');
  if (k === '5') toggleTool('axe');
  if (k === '6') toggleTool('weapon');
  if (k === 'i') toggleInventory();
  if (k === 'm') toggleMute();
  if (k === 'j') sellAll();
  if (['arrowup','arrowdown','arrowleft','arrowright'].includes(e.key)) e.preventDefault();
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

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
  if (isMouseDown && !showInventory) {
    const tileKey = `${mouse.tx},${mouse.ty}`;
    if (tileKey !== lastDragTile) {
      applyTool(mouse.tx, mouse.ty);
      lastDragTile = tileKey;
    }
  }
});
canvas.addEventListener('mouseleave', () => { mouse.inside = false; isMouseDown = false; lastDragTile = null; });
canvas.addEventListener('mousedown', e => {
  if (e.button !== 0 || showInventory) return;
  ensureAudio();
  isMouseDown = true;
  applyTool(mouse.tx, mouse.ty);
  lastDragTile = `${mouse.tx},${mouse.ty}`;
});
canvas.addEventListener('mouseup', () => { isMouseDown = false; lastDragTile = null; });

function ensureAudio() {
  if (!audioCtx) initAudio();
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
}

// ==== TOOLBAR ====
document.querySelectorAll('.tool').forEach(el => {
  el.addEventListener('click', () => { ensureAudio(); toggleTool(el.dataset.tool); });
});

function toggleTool(tool) {
  if (currentTool === tool) {
    currentTool = null;
    showToast('🚫 Tool dilepas', '#888');
    sfxClick();
  } else {
    currentTool = tool;
    const names = { hoe:'🪓 Hoe', seed:'🌱 Seed', water:'💧 Water', harvest:'🌾 Harvest', axe:'🪓 Axe', weapon:'⚔️ Attack' };
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

// ==== UI ====
let dialogTimer = 0;
function showToast(msg, color='#ffed4a') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.color = color;
  t.style.borderColor = color;
  t.style.boxShadow = `0 0 20px ${color}`;
  t.style.display = 'block';
  clearTimeout(t._timeout);
  t._timeout = setTimeout(() => t.style.display = 'none', 1200);
}

function showDialog(text) {
  const d = document.getElementById('dialog');
  d.textContent = text;
  d.style.display = 'block';
  dialogTimer = 220;
}

function flashDamage() {
  const f = document.getElementById('damageFlash');
  f.style.opacity = '1';
  setTimeout(() => f.style.opacity = '0', 150);
}

// ==== INVENTORY ====
const ITEM_NAMES = {
  wheat: { emoji: '🌾', name: 'Gandum' },
  wood: { emoji: '🪵', name: 'Kayu' },
  food: { emoji: '🍗', name: 'Makanan' },
  seeds: { emoji: '🌱', name: 'Benih' },
};

function renderInventory() {
  const grid = document.getElementById('invGrid');
  grid.innerHTML = '';
  const items = [];
  for (const [k, v] of Object.entries(inventory)) items.push({ key: k, count: v, ...ITEM_NAMES[k] });
  const totalSlots = 20;
  for (let i = 0; i < totalSlots; i++) {
    const slot = document.createElement('div');
    slot.className = 'invSlot';
    if (i < items.length && items[i].count > 0) {
      const item = items[i];
      slot.innerHTML = `<div class="emoji">${item.emoji}</div><div class="name">${item.name}</div><div class="count">${item.count}</div>`;
      slot.onclick = () => useItem(item.key);
    }
    grid.appendChild(slot);
  }
}

function toggleInventory() {
  showInventory = !showInventory;
  const inv = document.getElementById('inv');
  if (showInventory) { renderInventory(); inv.style.display = 'block'; sfxClick(); }
  else inv.style.display = 'none';
}

function useItem(key) {
  ensureAudio();
  if (key === 'food' && inventory.food > 0) {
    if (player.hunger >= player.hungerMax && player.hp >= player.hpMax) {
      showToast('❌ Udah kenyang & sehat!', '#ff4444'); sfxError(); return;
    }
    inventory.food--;
    player.hunger = Math.min(player.hungerMax, player.hunger + 30);
    player.hp = Math.min(player.hpMax, player.hp + 15);
    sfxEat();
    showToast('🍗 Makan! +30 hunger +15 HP', '#5aff5a');
    updateHUD(); renderInventory();
  } else if (key === 'wood' && inventory.wood > 0) {
    const earn = inventory.wood * 3;
    inventory.wood = 0; gameGold += earn;
    sfxSell();
    showToast(`🪵 Jual kayu +${earn} gold!`, '#ffed4a');
    updateHUD(); renderInventory();
  } else if (key === 'wheat' && inventory.wheat > 0) {
    const earn = inventory.wheat * 10;
    inventory.wheat = 0; gameGold += earn;
    sfxSell();
    showToast(`🌾 Jual gandum +${earn} gold!`, '#ffed4a');
    updateHUD(); renderInventory();
  } else if (key === 'seeds') {
    showToast('🌱 Gunakan tool Seed buat tanam', '#ffed4a');
  }
}

let gameGold = 0;

// ==== APPLY TOOL ====
function applyTool(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;
  const t = world[ty][tx];
  const key = `${tx},${ty}`;

  if (currentTool === 'weapon') {
    const animal = getAnimalAt(tx, ty);
    if (animal && !animal.dead) { attackAnimal(animal); return; }
    return;
  }

  if (!currentTool) {
    for (const npc of npcs) {
      const dx = npc.x - tx*TILE;
      const dy = npc.y - ty*TILE;
      if (Math.abs(dx) < TILE*1.5 && Math.abs(dy) < TILE*1.5) {
        showDialog(`[${npc.name}] ${npc.dialog}`);
        sfxClick();
        return;
      }
    }
    return;
  }

  if (currentTool === 'hoe') {
    if (t === T_GRASS || t === T_FLOWER) {
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHoe(); showToast('🪓 Dicangkul!', '#a07040');
    } else sfxError();
  } else if (currentTool === 'seed') {
    if (t === T_FARMLAND && inventory.seeds > 0) {
      world[ty][tx] = T_CROP;
      crops[key] = { stage: 0, watered: false, timer: 0 };
      inventory.seeds--;
      sfxSeed(); showToast('🌱 Ditanam!', '#5aff5a');
      updateHUD();
    } else if (inventory.seeds <= 0) { sfxError(); showToast('❌ Benih habis!', '#ff4444'); }
    else sfxError();
  } else if (currentTool === 'water') {
    if (t === T_CROP && crops[key] && crops[key].stage < 3 && !crops[key].watered) {
      crops[key].watered = true;
      sfxWater(); showToast('💧 Disiram!', '#4a90e2');
    } else sfxError();
  } else if (currentTool === 'harvest') {
    if (t === T_CROP && crops[key] && crops[key].stage >= 3) {
      inventory.wheat++;
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHarvest(); showToast('🌾 Panen! +1', '#ffed4a');
      updateHUD();
    } else sfxError();
  } else if (currentTool === 'axe') {
    if (t === T_TREE) {
      world[ty][tx] = T_STUMP;
      trees[key] = { stage: -1, timer: 0 };
      inventory.wood += 3;
      sfxAxe(); showToast('🪓 Tebang! +3 kayu', '#a07040');
      updateHUD();
    } else sfxError();
  }
}

function getAnimalAt(tx, ty) {
  for (const a of animals) {
    if (a.dead) continue;
    if (Math.floor(a.x / TILE) === tx && Math.floor(a.y / TILE) === ty) return a;
  }
  return null;
}

function attackAnimal(animal) {
  const dmg = 10 + Math.floor(Math.random()*8);
  animal.hp -= dmg;
  animal.hurtFlash = 10;
  animal.wanderTimer = 0;
  const dx = animal.x - player.x, dy = animal.y - player.y;
  const d = Math.hypot(dx, dy) || 1;
  animal.vx = dx/d * 4; animal.vy = dy/d * 4;
  sfxHit(); sfxAnimalHurt();
  if (animal.hp <= 0) {
    animal.dead = true;
    const amt = ANIMAL_TYPES[animal.type].dropAmt;
    inventory.food += amt;
    sfxHarvest();
    showToast(`🐾 +${amt} food`, '#ffaa00');
    updateHUD();
    setTimeout(() => spawnSingleAnimal(animal.type), 30000);
  } else showToast(`⚔️ Hit! -${dmg} HP`, '#ff6666');
}

function spawnSingleAnimal(type) {
  const t = ANIMAL_TYPES[type];
  let x, y, tries = 0;
  do { x = Math.floor(Math.random()*WORLD_W); y = Math.floor(Math.random()*WORLD_H); tries++; }
  while (tries < 50 && world[y][x] !== T_GRASS);
  animals.push({
    x: x*TILE + 3, y: y*TILE + 3,
    type, hp: t.hp, hpMax: t.hp,
    vx: 0, vy: 0, speed: t.speed, dir: 'down',
    wanderTimer: 0, wanderAngle: 0, hurtFlash: 0, dead: false, size: t.size,
    animTimer: 0, walkFrame: 0, pauseTimer: 0,
  });
}

function sellAll() {
  ensureAudio();
  const total = inventory.wheat * 10 + inventory.wood * 3;
  if (total === 0) { sfxError(); showToast('❌ Nggak ada yang bisa dijual', '#ff4444'); return; }
  gameGold += total;
  inventory.wheat = 0; inventory.wood = 0;
  sfxSell(); showToast(`🪙 +${total} gold!`, '#ffed4a');
  updateHUD();
}

function toggleMute() {
  muted = !muted;
  const ic = document.getElementById('muteIcon');
  if (muted) { ic.textContent = '🔇'; if (masterGain) masterGain.gain.value = 0; }
  else { ic.textContent = '🔊'; if (masterGain) masterGain.gain.value = masterVolume; }
  sfxClick();
}
document.getElementById('muteIcon').onclick = toggleMute;

// ============================================
// ==== UPDATE ====
// ============================================
let frameCount = 0;
let gameSeconds = 0;
let hungerCounter = 0;
let hpRegenCounter = 0;
let lastPhase = 'dawn';

function update() {
  frameCount++;
  const dt = 1/60;

  // ==== TIME ====
  time.totalMinutes += time.minutesPerSecond * dt;
  if (time.totalMinutes >= 24*60) {
    time.totalMinutes -= 24*60;
    time.day++;
    showToast('🌅 Hari baru!', '#ffed4a');
  }

  const phase = getTimeOfDay();
  if (phase !== lastPhase) {
    lastPhase = phase;
    startMusic(phase);
    const phaseNames = { dawn:'🌅 Pagi', day:'☀️ Siang', evening:'🌇 Sore', night:'🌙 Malam' };
    document.getElementById('timeOfDay').textContent = phaseNames[phase];
  }

  // ==== PLAYER MOVE ====
  let dx = 0, dy = 0;
  if (keys['arrowleft'] || keys['a']) dx -= player.speed;
  if (keys['arrowright'] || keys['d']) dx += player.speed;
  if (keys['arrowup'] || keys['w']) dy -= player.speed;
  if (keys['arrowdown'] || keys['s']) dy += player.speed;

  if (dx !== 0 || dy !== 0) {
    if (dx !== 0 && canMoveTo(player.x + dx, player.y, player.w, player.h)) player.x += dx;
    if (dy !== 0 && canMoveTo(player.x, player.y + dy, player.w, player.h)) player.y += dy;
    if (Math.abs(dx) > Math.abs(dy)) player.dir = dx > 0 ? 'right' : 'left';
    else player.dir = dy > 0 ? 'down' : 'up';
    player.animTimer++;
    if (player.animTimer > 10) { // lebih lambat = animasi lebih natural
      player.animTimer = 0;
      player.walkFrame = (player.walkFrame + 1) % 4;
    }
  } else {
    player.walkFrame = 0;
    player.animTimer = 0;
  }

  // ==== CROPS (LEBIH LAMBAT) ====
  Object.keys(crops).forEach(k => {
    const c = crops[k];
    if (c.stage >= 0 && c.stage < 3) {
      c.timer = (c.timer || 0) + (c.watered ? 1.5 : 0.4); // lebih lambat
      if (c.timer > 400) { // dari 180 → 400
        c.stage++;
        c.timer = 0;
        c.watered = false;
      }
    }
  });

  // ==== TREES (LEBIH LAMBAT) ====
  Object.keys(trees).forEach(k => {
    const t = trees[k];
    if (t.stage >= -1 && t.stage < 3) {
      t.timer = (t.timer || 0) + 1;
      if (t.timer > 900) { // dari 400 → 900
        t.stage++;
        t.timer = 0;
        const [tx, ty] = k.split(',').map(Number);
        if (t.stage >= 3) world[ty][tx] = T_TREE;
        else if (t.stage >= 0) world[ty][tx] = T_SAPLING;
      }
    }
  });

  // ==== NPC WANDER (SLOW + REALISTIC) ====
  npcs.forEach(npc => {
    npc.moveTimer -= dt;

    // Kalau udah sampe target atau timer abis, pilih target baru & pause
    const ttx = npc.targetX * TILE;
    const tty = npc.targetY * TILE;
    const ddx = ttx - npc.x;
    const ddy = tty - npc.y;
    const dist = Math.hypot(ddx, ddy);

    if (dist < 4 || npc.moveTimer <= 0) {
      // Pause dulu (kayak lagi mikir)
      if (npc.moveTimer <= 0 && !npc.pausing) {
        npc.pausing = true;
        npc.pauseTimer = 1.5 + Math.random() * 2.5; // pause 1.5-4 detik
      }
      if (npc.pausing) {
        npc.pauseTimer -= dt;
        npc.isMoving = false;
        if (npc.pauseTimer <= 0) {
          npc.pausing = false;
          npc.moveTimer = 3 + Math.random() * 4;
          // Pilih target random DI AREA VILLAGE SAJA (bawah rumah)
          npc.targetX = 5 + Math.floor(Math.random() * (WORLD_W - 10));
          // Hanya area jalan (y=15-16) atau bawah rumah
          npc.targetY = 15 + Math.floor(Math.random() * 2);
          // Clamp biar nggak di air/luar
          npc.targetX = Math.max(5, Math.min(WORLD_W-5, npc.targetX));
          npc.targetY = Math.max(15, Math.min(17, npc.targetY));
        }
      }
    } else {
      // Gerak menuju target
      npc.isMoving = true;
      const nx = npc.x + ddx/dist * npc.speed;
      const ny = npc.y + ddy/dist * npc.speed;

      // Cek collision — kalau kena solid, stop & pilih target baru
      if (canMoveTo(nx, ny, 10, 14)) {
        npc.x = nx;
        npc.y = ny;
      } else {
        npc.moveTimer = 0;
        npc.pausing = false;
      }

      if (Math.abs(ddx) > Math.abs(ddy)) npc.dir = ddx > 0 ? 'right' : 'left';
      else npc.dir = ddy > 0 ? 'down' : 'up';

      // Walk animation
      npc.animTimer++;
      if (npc.animTimer > 12) {
        npc.animTimer = 0;
        npc.walkFrame = (npc.walkFrame + 1) % 4;
      }
    }

    if (!npc.isMoving) {
      npc.walkFrame = 0;
      npc.animTimer = 0;
    }
  });

  // ==== ANIMALS (SLOW + PAUSE) ====
  animals.forEach(a => {
    if (a.dead) return;
    a.x += a.vx; a.y += a.vy;
    a.vx *= 0.85; a.vy *= 0.85;

    // Pause timer
    if (a.pauseTimer > 0) {
      a.pauseTimer -= dt;
      a.walkFrame = 0;
      return;
    }

    a.wanderTimer -= 1;
    if (a.wanderTimer <= 0) {
      a.wanderTimer = 120 + Math.random() * 240;
      a.wanderAngle = Math.random() * Math.PI * 2;
      a.pauseTimer = 0.5 + Math.random() * 1.5; // pause 0.5-2 detik
    }

    if (a.wanderAngle !== undefined && a.pauseTimer <= 0) {
      const spd = a.speed * (a.hurtFlash > 0 ? 2 : 1);
      const nx = a.x + Math.cos(a.wanderAngle) * spd;
      const ny = a.y + Math.sin(a.wanderAngle) * spd;
      const tx = Math.floor(nx / TILE);
      const ty = Math.floor(ny / TILE);
      if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
        const t = world[ty][tx];
        if (t === T_GRASS || t === T_FLOWER || t === T_PATH) {
          a.x = nx; a.y = ny;
          if (Math.abs(Math.cos(a.wanderAngle)) > Math.abs(Math.sin(a.wanderAngle))) {
            a.dir = Math.cos(a.wanderAngle) > 0 ? 'right' : 'left';
          } else {
            a.dir = Math.sin(a.wanderAngle) > 0 ? 'down' : 'up';
          }
          a.animTimer++;
          if (a.animTimer > 15) { a.animTimer = 0; a.walkFrame = (a.walkFrame + 1) % 4; }
        } else {
          a.wanderTimer = 0;
        }
      }
    }
    a.x = Math.max(TILE, Math.min(WORLD_W*TILE - TILE, a.x));
    a.y = Math.max(TILE, Math.min(WORLD_H*TILE - TILE, a.y));
    if (a.hurtFlash > 0) a.hurtFlash--;
  });

  // ==== HUNGER (LEBIH LAMBAT) ====
  hungerCounter += dt;
  if (hungerCounter > 6) { // dari 3 → 6 detik per 1 hunger
    hungerCounter = 0;
    player.hunger = Math.max(0, player.hunger - 1);
  }

  if (player.hunger > 60) {
    hpRegenCounter += dt;
    if (hpRegenCounter > 5) {
      hpRegenCounter = 0;
      player.hp = Math.min(player.hpMax, player.hp + 1);
    }
  }

  if (player.hunger <= 0) {
    if (frameCount % 90 === 0) { // dari 60 → 90 (lebih lambat)
      player.hp = Math.max(0, player.hp - 2);
      flashDamage(); sfxHurt();
    }
  }

  // Night damage (kurang agresif)
  const phase2 = getTimeOfDay();
  if (phase2 === 'night' && frameCount % 300 === 0) { // dari 180 → 300
    const inVillage = player.y / TILE < 18 && player.y / TILE > 8;
    if (!inVillage) {
      player.hp = Math.max(0, player.hp - 2);
      flashDamage(); sfxHurt();
    }
  }

  if (player.hp <= 0) {
    player.hp = player.hpMax / 2;
    player.hunger = player.hungerMax / 2;
    player.x = 20 * TILE; player.y = 20 * TILE;
    showToast('💀 Kamu pingsan! Respawn...', '#ff4444');
    sfxError();
  }

  // ==== CAMERA ====
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

  if (dialogTimer > 0) {
    dialogTimer--;
    if (dialogTimer === 0) document.getElementById('dialog').style.display = 'none';
  }

  document.getElementById('clock').textContent = getClockString();
  document.getElementById('dayNum').textContent = time.day;
  updateHUDBars();
}

function updateHUDBars() {
  document.getElementById('hpFill').style.width = (player.hp / player.hpMax * 100) + '%';
  document.getElementById('hpText').textContent = `${Math.round(player.hp)}/${player.hpMax}`;
  document.getElementById('hungerFill').style.width = (player.hunger / player.hungerMax * 100) + '%';
  document.getElementById('hungerText').textContent = `${Math.round(player.hunger)}/${player.hungerMax}`;
}

function updateHUD() {
  document.getElementById('gold').textContent = gameGold;
  document.getElementById('wood').textContent = inventory.wood;
  document.getElementById('food').textContent = inventory.food;
  document.getElementById('wheat').textContent = inventory.wheat;
}

// ============================================
// ==== DRAW ====
// ============================================
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
    const wave = Math.sin(frameCount*0.03 + x + y) * 2;
    artPx(wx+3+wave, wy+4, 3, 1, '#4a7dd0');
    artPx(wx+9-wave, wy+10, 3, 1, '#4a7dd0');
  } else if (t === T_TREE) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+6, wy+11, 4, 5, '#5a3a1a');
    artPx(wx+1, wy+1, 14, 11, '#1e5a2a');
    artPx(wx+2, wy+0, 12, 3, '#2d7d3a');
    artPx(wx+4, wy+2, 3, 3, '#4a9d54');
    artPx(wx+9, wy+5, 3, 3, '#4a9d54');
  } else if (t === T_STUMP) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+4, wy+8, 8, 6, '#5a3a1a');
    artPx(wx+5, wy+8, 6, 2, '#7a5030');
    artPx(wx+6, wy+8, 4, 1, '#8a6040');
  } else if (t === T_SAPLING) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+7, wy+8, 2, 8, '#5a3a1a');
    artPx(wx+4, wy+5, 4, 4, '#2d7d3a');
    artPx(wx+8, wy+6, 4, 4, '#2d7d3a');
    artPx(wx+5, wy+6, 2, 2, '#4a9d54');
  } else if (t === T_FARMLAND) {
    artPx(wx, wy, TILE, TILE, '#6b4423');
    for (let i = 3; i < 16; i += 4) artPx(wx, wy+i, TILE, 1, '#4a2f18');
  } else if (t === T_CROP) {
    artPx(wx, wy, TILE, TILE, '#6b4423');
    for (let i = 3; i < 16; i += 4) artPx(wx, wy+i, TILE, 1, '#4a2f18');
    const c = crops[`${x},${y}`];
    const stage = c ? c.stage : 0;
    const cx = wx + 6, cy = wy + 6;
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
      ctx.shadowBlur = 12 * glow;
      artPx(cx+1, cy-2, 2, 11, '#e8c850');
      artPx(cx, cy-3, 1, 9, '#c8a830');
      artPx(cx+3, cy-3, 1, 9, '#c8a830');
      artPx(cx, cy-4, 4, 3, '#ffed4a');
      ctx.shadowBlur = 0;
    }
  } else if (t === T_FLOWER) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+2, wy+3, 1, 1, '#4a9d54');
    const colors = ['#ff6b9d', '#ffaa55', '#aa6bff', '#6bd8ff'];
    const c = colors[(x*7+y*3) % colors.length];
    artPx(wx+6, wy+7, 4, 4, c);
    artPx(wx+7, wy+8, 2, 2, '#ffeb3b');
  } else if (t === T_HOUSE) {
    // Rumah: atap gelap atas, dinding terang bawah
    const isNight = getTimeOfDay() === 'night' || getTimeOfDay() === 'evening';
    // Atap (4px atas)
    artPx(wx, wy, TILE, TILE, '#5a3a1a');
    artPx(wx, wy+4, TILE, TILE-4, '#c89b6a');
    // Detail atap
    artPx(wx+1, wy+1, TILE-2, 1, '#7a5030');
    // Jendela nyala kalau gelap
    if (isNight) {
      ctx.shadowColor = '#ffed4a';
      ctx.shadowBlur = 12;
      artPx(wx+5, wy+8, 6, 5, '#ffed4a');
      ctx.shadowBlur = 0;
    } else {
      artPx(wx+5, wy+8, 6, 5, '#4a90e2');
    }
  } else if (t === T_HOUSE_DOOR) {
    const isNight = getTimeOfDay() === 'night' || getTimeOfDay() === 'evening';
    artPx(wx, wy, TILE, TILE, '#5a3a1a');
    artPx(wx, wy+4, TILE, TILE-4, '#c89b6a');
    // Pintu
    artPx(wx+3, wy+7, 10, 9, '#5a3a1a');
    artPx(wx+11, wy+12, 1, 1, '#ffd700');
    // Kalau malam, pintu ada glow
    if (isNight) {
      ctx.shadowColor = '#ffed4a';
      ctx.shadowBlur = 8;
      artPx(wx+3, wy+7, 10, 1, '#ffed4a');
      ctx.shadowBlur = 0;
    }
  } else if (t === T_LAMP) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+6, wy+4, 4, 12, '#555');
    const isNight = getTimeOfDay() === 'night' || getTimeOfDay() === 'evening';
    if (isNight) {
      ctx.shadowColor = '#ffed4a';
      ctx.shadowBlur = 20;
      artPx(wx+4, wy+1, 8, 6, '#ffed4a');
      ctx.shadowBlur = 0;
    } else {
      artPx(wx+4, wy+1, 8, 6, '#666');
    }
  }
}

function drawHumanoid(x, y, dir, walkFrame, color, skin='#ffcc99', shirtColor=null) {
  const skinTone = skin;
  const shirt = shirtColor || color;
  const pants = '#1a3a8a';
  const hair = '#3a2010';
  const bob = (walkFrame === 1 || walkFrame === 3) ? -1 : 0;

  ctx.globalAlpha = 0.3;
  artPx(x+2, y+15, 8, 2, '#000');
  ctx.globalAlpha = 1;

  artPx(x+3, y+0+bob, 6, 6, skinTone);
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
  artPx(x+2, y+7+bob, 1, 3, skinTone);
  artPx(x+9, y+7+bob, 1, 3, skinTone);

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

function drawAnimal(a) {
  if (a.dead) return;
  const x = a.x, y = a.y;
  const t = ANIMAL_TYPES[a.type];
  let color = t.color;
  if (a.hurtFlash > 0 && a.hurtFlash % 4 < 2) color = '#ff4444';

  ctx.globalAlpha = 0.3;
  artPx(x-2, y+10, 10, 2, '#000');
  ctx.globalAlpha = 1;

  // Body bob saat walk
  const bob = (a.walkFrame === 1 || a.walkFrame === 3) ? -1 : 0;

  artPx(x-2, y-4+bob, 10, 10, color);

  if (a.type === 'rabbit') {
    artPx(x-1, y-8+bob, 2, 5, color);
    artPx(x+3, y-8+bob, 2, 5, color);
    artPx(x-2, y-5+bob, 10, 4, color);
    artPx(x+0, y-3+bob, 1, 1, '#000');
    artPx(x+4, y-3+bob, 1, 1, '#000');
  } else if (a.type === 'chicken') {
    artPx(x+1, y-8+bob, 4, 5, color);
    artPx(x+2, y-10+bob, 2, 3, '#ff4444');
    artPx(x+5, y-6+bob, 3, 2, '#ff8800');
    artPx(x+2, y-6+bob, 1, 1, '#000');
  } else if (a.type === 'cow') {
    artPx(x-3, y-8+bob, 12, 8, color);
    artPx(x-4, y-7+bob, 2, 2, '#333');
    artPx(x+8, y-7+bob, 2, 2, '#333');
    artPx(x-1, y-5+bob, 2, 2, '#000');
    artPx(x+5, y-5+bob, 2, 2, '#000');
    artPx(x+1, y-2+bob, 4, 2, '#ffaaaa');
  }

  if (a.hp < a.hpMax) {
    const w = 20;
    const hx = Math.floor((x - camera.x) * PX) - 4;
    const hy = Math.floor((y - camera.y) * PX) - 20;
    ctx.fillStyle = '#000';
    ctx.fillRect(hx-1, hy-1, w+2, 5);
    ctx.fillStyle = '#ff4444';
    ctx.fillRect(hx, hy, w * (a.hp/a.hpMax), 3);
  }
}

function drawNpc(npc) {
  drawHumanoid(npc.x, npc.y, npc.dir, npc.walkFrame, npc.color, '#e8b088', npc.color);
  const dx = npc.x - player.x;
  const dy = npc.y - player.y;
  if (Math.hypot(dx, dy) < 60) {
    const sx = Math.floor((npc.x - camera.x) * PX) + 15;
    const sy = Math.floor((npc.y - camera.y) * PX) - 10;
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.font = 'bold 11px monospace';
    ctx.textAlign = 'center';
    const w = ctx.measureText(npc.name).width + 8;
    ctx.fillRect(sx - w/2, sy - 10, w, 14);
    ctx.fillStyle = '#ffed4a';
    ctx.fillText(npc.name, sx, sy);
  }
}

function drawCursorHighlight() {
  if (!mouse.inside) return;
  const tx = mouse.tx, ty = mouse.ty;
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;
  const px = Math.floor((tx * TILE - camera.x) * PX);
  const py = Math.floor((ty * TILE - camera.y) * PX);

  let color = '#444', alpha = 0.3;
  if (currentTool) {
    const t = world[ty][tx];
    const key = `${tx},${ty}`;
    if (currentTool === 'hoe' && (t === T_GRASS || t === T_FLOWER)) { color = '#a07040'; alpha = 0.7; }
    else if (currentTool === 'seed' && t === T_FARMLAND) { color = '#5aff5a'; alpha = 0.7; }
    else if (currentTool === 'water' && t === T_CROP && crops[key] && !crops[key].watered && crops[key].stage < 3) { color = '#4a90e2'; alpha = 0.7; }
    else if (currentTool === 'harvest' && t === T_CROP && crops[key] && crops[key].stage >= 3) { color = '#ffed4a'; alpha = 0.9; }
    else if (currentTool === 'axe' && t === T_TREE) { color = '#ff8800'; alpha = 0.8; }
    else if (currentTool === 'weapon') {
      const a = getAnimalAt(tx, ty);
      if (a) { color = '#ff3333'; alpha = 0.9; }
    }
  }

  ctx.strokeStyle = color;
  ctx.lineWidth = currentTool ? 3 : 2;
  ctx.globalAlpha = alpha;
  ctx.strokeRect(px + 1, py + 1, TILE*PX - 2, TILE*PX - 2);
  ctx.globalAlpha = alpha * 0.25;
  ctx.fillStyle = color;
  ctx.fillRect(px, py, TILE*PX, TILE*PX);
  ctx.globalAlpha = 1;
}

function drawSkyOverlay() {
  const phase = getTimeOfDay();
  const colors = skyColors[phase];
  ctx.fillStyle = colors.ambient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const darkness = getDarkness();
  if (darkness > 0) {
    const grad = ctx.createRadialGradient(
      canvas.width/2, canvas.height/2, 100,
      canvas.width/2, canvas.height/2, canvas.width * 0.7
    );
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(0.7, `rgba(10,10,40,${darkness * 0.5})`);
    grad.addColorStop(1, `rgba(10,10,40,${darkness})`);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  // Sun/Moon
  const h = (time.totalMinutes / 60) % 24;
  let iconX, iconY, iconEmoji;
  if (h >= 5 && h < 19) {
    const progress = (h - 5) / 14;
    iconX = canvas.width * 0.1 + canvas.width * 0.8 * progress;
    iconY = 60 + Math.sin(progress * Math.PI) * -20;
    iconEmoji = h < 9 ? '🌅' : h < 17 ? '☀️' : '🌇';
  } else {
    const nightH = h >= 19 ? h - 19 : h + 5;
    const progress = nightH / 10;
    iconX = canvas.width * 0.1 + canvas.width * 0.8 * progress;
    iconY = 60 + Math.sin(progress * Math.PI) * -20;
    iconEmoji = '🌙';
  }
  ctx.font = '32px serif';
  ctx.textAlign = 'center';
  ctx.fillText(iconEmoji, iconX, iconY);
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

  const entities = [];
  npcs.forEach(n => entities.push({y: n.y, draw: () => drawNpc(n)}));
  animals.forEach(a => { if (!a.dead) entities.push({y: a.y, draw: () => drawAnimal(a)}); });
  entities.push({y: player.y, draw: () => {
    drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2', '#ffcc99', '#4a90e2');
  }});
  entities.sort((a,b) => a.y - b.y).forEach(e => e.draw());

  drawCursorHighlight();
  drawSkyOverlay();
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

document.body.addEventListener('click', () => ensureAudio(), { once: false });

updateHUD();
updateToolbarUI();
updateHUDBars();
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=650)
