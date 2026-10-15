import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Farm", page_icon="🌾", layout="wide")
st.title("🌾 Pixel Farm - Wheat Farming")
st.caption("**WASD** jalan • **E** interaksi • **1/2/3** pilih tool (Hoe/Seed/Water) • Jual gandum ke Pedagang!")

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
  }
  #hud {
    position:absolute; top:10px; left:10px;
    color:#0f0; font-size:14px;
    text-shadow:0 0 5px #0f0; pointer-events:none;
    line-height:1.6;
  }
  #toolbar {
    position:absolute; top:10px; right:10px;
    color:#0f0; font-size:14px; text-align:right;
    text-shadow:0 0 5px #0f0; pointer-events:none;
    line-height:1.6;
  }
  #toolbar .active { color:#ffed4a; font-weight:bold; text-shadow:0 0 8px #ffed4a; }
  #dialog {
    position:absolute; bottom:40px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.95); border:3px solid #0f0;
    color:#0f0; padding:12px 20px; font-size:16px; display:none;
    min-width:400px; text-align:center;
    box-shadow:0 0 20px #0f0;
  }
  #toast {
    position:absolute; top:80px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.9); border:2px solid #ffed4a;
    color:#ffed4a; padding:8px 16px; font-size:14px;
    display:none; text-shadow:0 0 5px #ffed4a;
  }
</style>
</head>
<body>
<div id="hud">
  🪙 Gold: <span id="gold">0</span><br>
  🌱 Seeds: <span id="seeds">5</span><br>
  🌾 Wheat: <span id="wheat">0</span><br>
  🛠️ Tool: <span id="currentTool">Hoe</span>
</div>
<div id="toolbar">
  [1] 🪓 Hoe<br>
  [2] 🌱 Seed<br>
  [3] 💧 Water
</div>
<div id="dialog"></div>
<div id="toast"></div>
<div id="wrap">
  <canvas id="game" width="640" height="480"></canvas>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PX = 4;
const TILE = 16;

// ==== WORLD ====
const WORLD_W = 40;
const WORLD_H = 30;
let world = [];

// Tile types
const T_GRASS = 0;
const T_PATH = 1;
const T_WATER = 2;
const T_TREE = 3;
const T_FLOWER = 4;
const T_STONE = 5;
const T_FARMLAND = 6; // cangkul
const T_CROP = 7;     // ditanam
const T_HOUSE = 8;

function generateWorld() {
  for (let y=0; y<WORLD_H; y++) {
    let row = [];
    for (let x=0; x<WORLD_W; x++) {
      let t = T_GRASS;
      if (Math.abs(x - y) < 2) t = T_PATH;
      if (x > 30 && y < 8) t = T_WATER;
      else if (t === T_GRASS && Math.random() < 0.06) t = T_TREE;
      else if (t === T_GRASS && Math.random() < 0.05) t = T_FLOWER;
      else if (t === T_GRASS && Math.random() < 0.02) t = T_STONE;
      row.push(t);
    }
    world.push(row);
  }
  // Clear area bawah buat spawn & farm
  for (let y=WORLD_H-8; y<WORLD_H; y++)
    for (let x=0; x<WORLD_W; x++)
      if ([T_TREE, T_WATER, T_STONE, T_HOUSE].includes(world[y][x])) world[y][x] = T_GRASS;

  // Rumah pedagang
  for (let y=5; y<8; y++)
    for (let x=5; x<9; x++)
      world[y][x] = T_HOUSE;
  // Pintu rumah jadi path
  world[7][7] = T_PATH;

  // Area farm awal (tanah kosong di kiri-bawah)
  for (let y=WORLD_H-6; y<WORLD_H-2; y++)
    for (let x=3; x<8; x++)
      world[y][x] = T_GRASS;
}
generateWorld();

// Crop data per tile
const crops = {}; // key: "x,y" → {stage, wateredTick, plantedTick}

// ==== PLAYER ====
const player = {
  x: 20 * TILE,
  y: 20 * TILE,
  w: 12, h: 16,
  speed: 1.2,
  dir: 'down',
  animTimer: 0,
  walkFrame: 0,
};

// ==== INVENTORY ====
const inv = {
  gold: 0,
  seeds: 5,
  wheat: 0,
  tool: 'hoe', // hoe, seed, water
};

// ==== NPC ====
const npcs = [
  { x: 15*TILE, y: 20*TILE, dir:'down', color:'#ff6b6b', name:'Petani Tua',
    dialog:'Tekan 1 buat cangkul, 2 buat tanam, 3 buat siram. Tunggu gandum tumbuh 3 tahap, baru panen!' },
  { x: 7*TILE, y: 8*TILE, dir:'down', color:'#4ecdc4', name:'Pedagang',
    dialog:'JUAL: 1 gandum = 10 gold. BELI: 1 benih = 5 gold. Tekan E lagi buat transaksi!' },
];

// ==== CAMERA ====
const camera = { x: 0, y: 0 };

// ==== INPUT ====
const keys = {};
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key === 'e' || e.key === 'E') interact();
  if (e.key === '1') { inv.tool = 'hoe'; updateHUD(); }
  if (e.key === '2') { inv.tool = 'seed'; updateHUD(); }
  if (e.key === '3') { inv.tool = 'water'; updateHUD(); }
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

// ==== COLLISION ====
function isSolid(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return true;
  const t = world[ty][tx];
  return t === T_WATER || t === T_TREE || t === T_STONE || t === T_HOUSE;
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

// ==== INTERACTION ====
let dialogTimer = 0;
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(t._timeout);
  t._timeout = setTimeout(() => t.style.display = 'none', 1500);
}

function showDialog(text) {
  const d = document.getElementById('dialog');
  d.textContent = text;
  d.style.display = 'block';
  dialogTimer = 220;
}

// Tile yang dihadapi player (1 tile ke arah hadap)
function getFacingTile() {
  const cx = Math.floor((player.x + player.w/2) / TILE);
  const cy = Math.floor((player.y + player.h/2) / TILE);
  let fx = cx, fy = cy;
  if (player.dir === 'up') fy -= 1;
  else if (player.dir === 'down') fy += 1;
  else if (player.dir === 'left') fx -= 1;
  else if (player.dir === 'right') fx += 1;
  return { x: fx, y: fy };
}

function interact() {
  // Cek NPC dulu
  for (const npc of npcs) {
    const dx = (npc.x + 8) - (player.x + player.w/2);
    const dy = (npc.y + 8) - (player.y + player.h/2);
    if (Math.hypot(dx, dy) < 40) {
      handleNPC(npc);
      return;
    }
  }

  // Kalau nggak ada NPC, pakai tool ke tile depan
  useTool();
}

function handleNPC(npc) {
  if (npc.name === 'Pedagang') {
    // Auto transaksi: jual gandum dulu, kalau nggak ada baru beli benih
    if (inv.wheat > 0) {
      const earn = inv.wheat * 10;
      inv.gold += earn;
      showDialog(`Jual ${inv.wheat} gandum → +${earn} gold!`);
      inv.wheat = 0;
    } else if (inv.gold >= 5) {
      inv.gold -= 5;
      inv.seeds += 1;
      showDialog(`Beli 1 benih → -5 gold. Sisa: ${inv.gold} gold`);
    } else {
      showDialog('Kamu miskin! Panen gandum dulu buat jual.');
    }
    updateHUD();
  } else {
    showDialog(`[${npc.name}] ${npc.dialog}`);
  }
}

function useTool() {
  const f = getFacingTile();
  if (f.x < 0 || f.y < 0 || f.x >= WORLD_W || f.y >= WORLD_H) return;
  const t = world[f.y][f.x];
  const key = `${f.x},${f.y}`;

  if (inv.tool === 'hoe') {
    if (t === T_GRASS) {
      world[f.y][f.x] = T_FARMLAND;
      crops[key] = { stage: -1, watered: false }; // -1 = kosong
      showToast('🪓 Tanah dicangkul!');
    } else {
      showToast('❌ Cuma bisa cangkul rumput!');
    }
  } else if (inv.tool === 'seed') {
    if (t === T_FARMLAND && (!crops[key] || crops[key].stage === -1)) {
      if (inv.seeds <= 0) { showToast('❌ Benih habis!'); return; }
      inv.seeds--;
      world[f.y][f.x] = T_CROP;
      crops[key] = { stage: 0, watered: false, timer: 0 };
      showToast('🌱 Benih ditanam!');
      updateHUD();
    } else {
      showToast('❌ Harus di tanah pertanian kosong!');
    }
  } else if (inv.tool === 'water') {
    if (t === T_CROP && crops[key]) {
      crops[key].watered = true;
      showToast('💧 Disiram!');
    } else {
      showToast('❌ Nggak ada tanaman di sini!');
    }
  }
}

// Panen: E di tile yang ada gandum matang
function checkHarvest() {
  const f = getFacingTile();
  const key = `${f.x},${f.y}`;
  if (world[f.y] && world[f.y][f.x] === T_CROP && crops[key] && crops[key].stage >= 3) {
    if (inv.tool === 'hoe') { // pakai hoe buat panen
      inv.wheat++;
      world[f.y][f.x] = T_FARMLAND;
      crops[key] = { stage: -1, watered: false };
      showToast('🌾 Panen! +1 gandum');
      updateHUD();
      return true;
    }
  }
  return false;
}

// ==== UPDATE ====
let frameCount = 0;
function update() {
  frameCount++;

  // Gerak
  let dx = 0, dy = 0;
  if (keys['arrowleft'] || keys['a']) dx -= player.speed;
  if (keys['arrowright'] || keys['d']) dx += player.speed;
  if (keys['arrowup'] || keys['w']) dy -= player.speed;
  if (keys['arrowdown'] || keys['s']) dy += player.speed;

  const moving = dx !== 0 || dy !== 0;

  if (moving) {
    if (dx !== 0 && canMoveTo(player.x + dx, player.y)) player.x += dx;
    if (dy !== 0 && canMoveTo(player.x, player.y + dy)) player.y += dy;

    if (Math.abs(dx) > Math.abs(dy)) player.dir = dx > 0 ? 'right' : 'left';
    else player.dir = dy > 0 ? 'down' : 'up';

    player.animTimer++;
    if (player.animTimer > 8) {
      player.animTimer = 0;
      player.walkFrame = (player.walkFrame + 1) % 4;
    }
  } else {
    player.walkFrame = 0;
    player.animTimer = 0;
  }

  // Auto-harvest kalau hadap crop matang & pakai hoe
  if (inv.tool === 'hoe') checkHarvest();

  // Growth crops (tiap 300 frame = ~5 detik per stage)
  Object.keys(crops).forEach(k => {
    const c = crops[k];
    if (c.stage >= 0 && c.stage < 3) {
      c.timer = (c.timer || 0) + (c.watered ? 2 : 0.5);
      if (c.timer > 300) {
        c.stage++;
        c.timer = 0;
        c.watered = false;
      }
    }
  });

  // Camera
  const tx = player.x - canvas.width / (2*PX) + player.w/2;
  const ty = player.y - canvas.height / (2*PX) + player.h/2;
  camera.x += (tx - camera.x) * 0.1;
  camera.y += (ty - camera.y) * 0.1;
  camera.x = Math.max(0, Math.min(WORLD_W*TILE - canvas.width/PX, camera.x));
  camera.y = Math.max(0, Math.min(WORLD_H*TILE - canvas.height/PX, camera.y));

  // Dialog timer
  if (dialogTimer > 0) {
    dialogTimer--;
    if (dialogTimer === 0) document.getElementById('dialog').style.display = 'none';
  }
}

function updateHUD() {
  document.getElementById('gold').textContent = inv.gold;
  document.getElementById('seeds').textContent = inv.seeds;
  document.getElementById('wheat').textContent = inv.wheat;
  document.getElementById('currentTool').textContent =
    inv.tool === 'hoe' ? '🪓 Hoe' : inv.tool === 'seed' ? '🌱 Seed' : '💧 Water';
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
  } else if (t === T_FLOWER) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+6, wy+7, 4, 4, '#ff6b9d');
    artPx(wx+7, wy+8, 2, 2, '#ffeb3b');
  } else if (t === T_STONE) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+3, wy+4, 10, 8, '#777');
    artPx(wx+4, wy+5, 8, 6, '#999');
  } else if (t === T_FARMLAND) {
    // Tanah cangkul - ada alur
    artPx(wx, wy, TILE, TILE, '#6b4423');
    // Alur horizontal
    artPx(wx, wy+2, TILE, 1, '#4a2f18');
    artPx(wx, wy+6, TILE, 1, '#4a2f18');
    artPx(wx, wy+10, TILE, 1, '#4a2f18');
    artPx(wx, wy+14, TILE, 1, '#4a2f18');
    // Highlight
    artPx(wx, wy+3, TILE, 1, '#8b5a2b');
    artPx(wx, wy+7, TILE, 1, '#8b5a2b');
    // Kalau ada crop kosong (stage -1), tetap tanah
  } else if (t === T_CROP) {
    // Tanah
    artPx(wx, wy, TILE, TILE, '#6b4423');
    artPx(wx, wy+2, TILE, 1, '#4a2f18');
    artPx(wx, wy+6, TILE, 1, '#4a2f18');
    artPx(wx, wy+10, TILE, 1, '#4a2f18');
    artPx(wx, wy+14, TILE, 1, '#4a2f18');

    const c = crops[`${x},${y}`];
    const stage = c ? c.stage : 0;

    // Tanaman tumbuh berdasarkan stage
    // Stage 0: tunas kecil
    // Stage 1: batang
    // Stage 2: hampir matang
    // Stage 3: gandum matang (warna emas)
    const cx = wx + 6; // center
    const cy = wy + 6;

    if (stage === 0) {
      // Tunas kecil (2 pixel hijau)
      artPx(cx+1, cy+6, 2, 3, '#5aff5a');
      artPx(cx, cy+5, 1, 2, '#3a9d3a');
    } else if (stage === 1) {
      // Batang lebih tinggi
      artPx(cx+1, cy+3, 2, 6, '#5aff5a');
      artPx(cx, cy+2, 1, 4, '#3a9d3a');
      artPx(cx+3, cy+2, 1, 4, '#3a9d3a');
    } else if (stage === 2) {
      // Batang tinggi hampir matang
      artPx(cx+1, cy+0, 2, 9, '#7fd77f');
      artPx(cx, cy-1, 1, 7, '#5aa55a');
      artPx(cx+3, cy-1, 1, 7, '#5aa55a');
      // Bulir mulai menguning
      artPx(cx+1, cy-1, 2, 2, '#d4d44a');
    } else if (stage >= 3) {
      // Gandum matang - warna emas!
      artPx(cx+1, cy-2, 2, 11, '#e8c850');
      artPx(cx, cy-3, 1, 9, '#c8a830');
      artPx(cx+3, cy-3, 1, 9, '#c8a830');
      // Bulir emas di atas
      artPx(cx, cy-4, 4, 3, '#ffed4a');
      artPx(cx-1, cy-3, 1, 2, '#ffed4a');
      artPx(cx+4, cy-3, 1, 2, '#ffed4a');
      // Bulir detail
      artPx(cx+1, cy-5, 2, 2, '#fff59d');
    }
  } else if (t === T_HOUSE) {
    // Rumah - cek posisi
    // Atap coklat tua, dinding coklat muda
    artPx(wx, wy, TILE, TILE, '#8b5a2b');
    artPx(wx, wy, TILE, 6, '#5a3a1a'); // atap
    artPx(wx, wy+6, TILE, TILE-6, '#c89b6a'); // dinding
    // jendela
    artPx(wx+4, wy+9, 4, 4, '#4a90e2');
    artPx(wx+5, wy+10, 2, 2, '#a0d0ff');
  }
}

function drawHumanoid(x, y, dir, walkFrame, color, isPlayer) {
  const skin = isPlayer ? '#ffcc99' : '#e8b088';
  const shirt = color;
  const pants = isPlayer ? '#1a3a8a' : '#553322';
  const hair = isPlayer ? '#3a2010' : '#222';

  const bob = (walkFrame === 1 || walkFrame === 3) ? -1 : 0;

  // HEAD
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

  // BODY
  artPx(x+3, y+6+bob, 6, 5, shirt);
  artPx(x+2, y+7+bob, 1, 3, skin);
  artPx(x+9, y+7+bob, 1, 3, skin);

  // LEGS
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

function drawNpc(npc) {
  drawHumanoid(npc.x, npc.y, npc.dir, 0, npc.color, false);
}

// Highlight tile yang dihadapi
function drawFacingHighlight() {
  const f = getFacingTile();
  const wx = f.x * TILE;
  const wy = f.y * TILE;
  ctx.strokeStyle = '#ffed4a';
  ctx.lineWidth = 2;
  ctx.strokeRect(
    Math.floor((wx - camera.x) * PX),
    Math.floor((wy - camera.y) * PX),
    TILE * PX,
    TILE * PX
  );
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

  drawFacingHighlight();

  // Entities sorted by Y
  const entities = [
    ...npcs.map(n => ({y:n.y, draw:() => drawNpc(n)})),
    { y: player.y, draw: () => drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2', true) },
  ];
  entities.sort((a,b) => a.y - b.y).forEach(e => e.draw());

  // Vignette
  const grad = ctx.createRadialGradient(
    canvas.width/2, canvas.height/2, 100,
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
updateHUD();
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=560)
