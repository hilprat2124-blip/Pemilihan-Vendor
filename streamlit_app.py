import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Farm v2", page_icon="🌾", layout="wide")
st.title("🌾 Pixel Farm v2 - Gampang!")
st.caption("**WASD** jalan • **E** kerjakan (auto!) • **J** jual gandum • Nggak perlu hafal apa-apa!")

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
    color:#0f0; font-size:16px;
    text-shadow:0 0 5px #0f0; pointer-events:none;
    line-height:1.8;
  }
  #hud b { color:#ffed4a; text-shadow:0 0 8px #ffed4a; }
  #action {
    position:absolute; bottom:20px; left:50%; transform:translateX(-50%);
    color:#ffed4a; font-size:18px; font-weight:bold;
    text-shadow:0 0 10px #ffed4a, 0 0 20px #ff8800;
    background:rgba(0,0,0,0.8); padding:8px 20px;
    border:2px solid #ffed4a; border-radius:4px;
    pointer-events:none;
  }
  #toast {
    position:absolute; top:80px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.9); border:2px solid #ffed4a;
    color:#ffed4a; padding:10px 20px; font-size:16px;
    display:none; text-shadow:0 0 5px #ffed4a;
    pointer-events:none;
  }
  #help {
    position:absolute; bottom:10px; right:10px;
    color:#888; font-size:12px; pointer-events:none;
    text-align:right; line-height:1.6;
  }
</style>
</head>
<body>
<div id="hud">
  🪙 Gold: <b><span id="gold">0</span></b><br>
  🌱 Benih: <b><span id="seeds">∞</span></b><br>
  🌾 Gandum: <b><span id="wheat">0</span></b><br>
  <span style="font-size:12px;color:#0a0">Tekan <b style="color:#ffed4a">J</b> buat jual gandum</span>
</div>
<div id="help">
  WASD / Arrow = Jalan<br>
  E = Kerjakan (auto)<br>
  J = Jual gandum
</div>
<div id="action"></div>
<div id="toast"></div>
<div id="wrap">
  <canvas id="game" width="720" height="520"></canvas>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PX = 5;        // scale up pixel (lebih gede biar jelas)
const TILE = 16;     // tile size

// ==== WORLD ====
const WORLD_W = 30;
const WORLD_H = 22;
let world = [];

const T_GRASS = 0;
const T_PATH = 1;
const T_WATER = 2;
const T_TREE = 3;
const T_FARMLAND = 4;
const T_CROP = 5;

function generateWorld() {
  world = [];
  for (let y=0; y<WORLD_H; y++) {
    let row = [];
    for (let x=0; x<WORLD_W; x++) {
      let t = T_GRASS;
      // Air di pinggir kanan
      if (x >= WORLD_W - 2) t = T_WATER;
      // Beberapa pohon random (jarang)
      else if (Math.random() < 0.04) t = T_TREE;
      row.push(t);
    }
    world.push(row);
  }
  // Area start bersih (tengah-bawah)
  for (let y=WORLD_H-4; y<WORLD_H; y++)
    for (let x=8; x<18; x++)
      world[y][x] = T_GRASS;

  // Path horizontal di tengah
  for (let x=0; x<WORLD_W; x++) world[11][x] = T_PATH;
}
generateWorld();

// Crop data
const crops = {}; // key "x,y" → { stage: 0-3, watered: bool, timer: float }

// ==== PLAYER ====
const player = {
  x: 12 * TILE,
  y: 14 * TILE,
  w: 10, h: 14,
  speed: 1.6, // lebih cepat
  dir: 'down',
  animTimer: 0,
  walkFrame: 0,
};

// ==== INVENTORY ====
const inv = {
  gold: 0,
  wheat: 0,
  // benih unlimited! nggak perlu tracking
};

// ==== CAMERA ====
const camera = { x: 0, y: 0 };

// ==== INPUT ====
const keys = {};
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key === 'e' || e.key === 'E') doAction();
  if (e.key === 'j' || e.key === 'J') sellWheat();
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
  t._timeout = setTimeout(() => t.style.display = 'none', 1200);
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

// ==== FACING TILE ====
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

// ==== ACTION (AUTO!) ====
function doAction() {
  const f = getFacingTile();
  if (f.x < 0 || f.y < 0 || f.x >= WORLD_W || f.y >= WORLD_H) return;
  const t = world[f.y][f.x];
  const key = `${f.x},${f.y}`;

  // Auto-detect apa yang harus dilakukan
  if (t === T_GRASS) {
    // Cangkul
    world[f.y][f.x] = T_FARMLAND;
    crops[key] = { stage: -1 };
    showToast('🪓 Tanah dicangkul!', '#a07040');
  } else if (t === T_FARMLAND) {
    // Tanam benih
    world[f.y][f.x] = T_CROP;
    crops[key] = { stage: 0, watered: false, timer: 0 };
    showToast('🌱 Benih ditanam!', '#5aff5a');
  } else if (t === T_CROP) {
    const c = crops[key];
    if (!c) return;
    if (c.stage >= 3) {
      // Panen
      inv.wheat++;
      world[f.y][f.x] = T_FARMLAND;
      crops[key] = { stage: -1 };
      showToast('🌾 Panen! +1 gandum', '#ffed4a');
      updateHUD();
    } else if (!c.watered) {
      // Siram (kalau belum disiram)
      c.watered = true;
      showToast('💧 Disiram! Tumbuh cepat', '#4a90e2');
    } else {
      showToast('⏳ Sedang tumbuh... tunggu ya', '#888');
    }
  } else {
    showToast('❌ Nggak bisa dikerjakan', '#ff4444');
  }
}

function sellWheat() {
  if (inv.wheat === 0) {
    showToast('❌ Nggak ada gandum buat dijual', '#ff4444');
    return;
  }
  const earn = inv.wheat * 10;
  inv.gold += earn;
  showToast(`🪙 Jual ${inv.wheat} gandum → +${earn} gold!`, '#ffed4a');
  inv.wheat = 0;
  updateHUD();
}

// ==== ACTION HINT (emoji di tile depan) ====
function getActionHint() {
  const f = getFacingTile();
  if (f.x < 0 || f.y < 0 || f.x >= WORLD_W || f.y >= WORLD_H) return null;
  const t = world[f.y][f.x];
  const key = `${f.x},${f.y}`;

  if (t === T_GRASS) return { emoji: '🪓', text: 'E: Cangkul', color: '#a07040' };
  if (t === T_FARMLAND) return { emoji: '🌱', text: 'E: Tanam', color: '#5aff5a' };
  if (t === T_CROP) {
    const c = crops[key];
    if (!c) return null;
    if (c.stage >= 3) return { emoji: '🌾', text: 'E: Panen!', color: '#ffed4a' };
    if (!c.watered) return { emoji: '💧', text: 'E: Siram', color: '#4a90e2' };
    return { emoji: '⏳', text: 'Tunggu tumbuh...', color: '#888' };
  }
  return null;
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

  if (dx !== 0 || dy !== 0) {
    // Sliding movement
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

  // Growth crops
  Object.keys(crops).forEach(k => {
    const c = crops[k];
    if (c.stage >= 0 && c.stage < 3) {
      c.timer = (c.timer || 0) + (c.watered ? 2 : 1);
      if (c.timer > 180) { // ~3 detik base, 1.5 kalau disiram
        c.stage++;
        c.timer = 0;
        c.watered = false;
      }
    }
  });

  // Camera
  const tx = player.x - canvas.width / (2*PX) + player.w/2;
  const ty = player.y - canvas.height / (2*PX) + player.h/2;
  camera.x += (tx - camera.x) * 0.15;
  camera.y += (ty - camera.y) * 0.15;
  camera.x = Math.max(0, Math.min(WORLD_W*TILE - canvas.width/PX, camera.x));
  camera.y = Math.max(0, Math.min(WORLD_H*TILE - canvas.height/PX, camera.y));

  // Update action hint
  const hint = getActionHint();
  const aEl = document.getElementById('action');
  if (hint) {
    aEl.textContent = `${hint.emoji} ${hint.text}`;
    aEl.style.color = hint.color;
    aEl.style.borderColor = hint.color;
    aEl.style.textShadow = `0 0 10px ${hint.color}, 0 0 20px ${hint.color}`;
    aEl.style.display = 'block';
  } else {
    aEl.style.display = 'none';
  }
}

function updateHUD() {
  document.getElementById('gold').textContent = inv.gold;
  document.getElementById('wheat').textContent = inv.wheat;
}

// ==== DRAW HELPERS ====
function artPx(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(
    Math.floor((x - camera.x) * PX),
    Math.floor((y - camera.y) * PX),
    w*PX, h*PX
  );
}

// ==== DRAW TILES ====
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
    // Kalau ada crop kosong (stage -1), tetap tanah
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
      // Gandum matang - glow!
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

// ==== DRAW HUMANOID ====
function drawHumanoid(x, y, dir, walkFrame, color) {
  const skin = '#ffcc99';
  const shirt = color;
  const pants = '#1a3a8a';
  const hair = '#3a2010';
  const bob = (walkFrame === 1 || walkFrame === 3) ? -1 : 0;

  // Shadow
  ctx.globalAlpha = 0.3;
  artPx(x+2, y+15, 8, 2, '#000');
  ctx.globalAlpha = 1;

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

// ==== FACING HIGHLIGHT ====
function drawFacingHighlight() {
  const f = getFacingTile();
  if (f.x < 0 || f.y < 0 || f.x >= WORLD_W || f.y >= WORLD_H) return;
  const wx = f.x * TILE;
  const wy = f.y * TILE;
  const hint = getActionHint();

  const glow = Math.sin(frameCount*0.15) * 0.4 + 0.6;
  ctx.strokeStyle = hint ? hint.color : '#ffff00';
  ctx.globalAlpha = 0.6 + glow * 0.4;
  ctx.lineWidth = 3;
  ctx.strokeRect(
    Math.floor((wx - camera.x) * PX) - 2,
    Math.floor((wy - camera.y) * PX) - 2,
    TILE * PX + 4,
    TILE * PX + 4
  );
  ctx.globalAlpha = 1;

  // Kalau ada hint, tampilkan emoji besar di atas tile
  if (hint) {
    const px = Math.floor((wx - camera.x) * PX);
    const py = Math.floor((wy - camera.y) * PX);
    ctx.font = `${TILE * PX * 0.8}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.globalAlpha = 0.9;
    ctx.fillText(hint.emoji, px + TILE*PX/2, py + TILE*PX/2);
    ctx.globalAlpha = 1;
  }
}

// ==== DRAW ====
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

  drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2');

  // Vignette
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
updateHUD();
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=600)
