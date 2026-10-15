import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Humanoid", page_icon="🚶", layout="wide")
st.title("🚶 Pixel Humanoid Adventure")
st.caption("**WASD / Arrow** buat jalan • **E** buat interaksi • Jelajahi dunia pixel!")

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; background:#0a0a1e; font-family:monospace; overflow:hidden; }
  #wrap { display:flex; justify-content:center; align-items:center; height:100vh; }
  canvas {
    image-rendering:pixelated;
    image-rendering:crisp-edges;
    border:4px solid #0f0;
    box-shadow:0 0 30px #0f0;
    background:#000;
  }
  #hud {
    position:absolute; top:10px; left:10px;
    color:#0f0; font-family:monospace; font-size:14px;
    text-shadow:0 0 5px #0f0; pointer-events:none;
  }
  #dialog {
    position:absolute; bottom:40px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.9); border:3px solid #0f0;
    color:#0f0; padding:12px 20px; font-family:monospace;
    font-size:16px; display:none; min-width:400px; text-align:center;
    box-shadow:0 0 20px #0f0;
  }
</style>
</head>
<body>
<div id="hud">
  📍 x: <span id="px">0</span>, y: <span id="py">0</span><br>
  🪙 Coins: <span id="coins">0</span>/<span id="total">0</span><br>
  🗺️ Area: <span id="area">Meadow</span>
</div>
<div id="dialog"></div>
<div id="wrap">
  <canvas id="game" width="640" height="480"></canvas>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PX = 4; // scale pixel art (tiap "art pixel" = 4 screen px)
const TILE = 16; // tile size (dalam art pixel)

// ==== WORLD ====
const WORLD_W = 40; // tiles
const WORLD_H = 30; // tiles
let world = [];

// Tile types: 0=grass, 1=dirt path, 2=water, 3=tree, 4=flower, 5=stone
function generateWorld() {
  for (let y=0; y<WORLD_H; y++) {
    let row = [];
    for (let x=0; x<WORLD_W; x++) {
      let t = 0;
      // Path diagonal
      if (Math.abs(x - y) < 2) t = 1;
      // Air
      if (x > 30 && y < 8) t = 2;
      // Random pohon
      if (t === 0 && Math.random() < 0.06) t = 3;
      // Random bunga
      else if (t === 0 && Math.random() < 0.05) t = 4;
      // Random batu
      else if (t === 0 && Math.random() < 0.02) t = 5;
      row.push(t);
    }
    world.push(row);
  }
  // Area bawah aman (spawn)
  for (let y=WORLD_H-3; y<WORLD_H; y++)
    for (let x=0; x<WORLD_W; x++)
      if (world[y][x] === 3 || world[y][x] === 2) world[y][x] = 0;
}
generateWorld();

// ==== PLAYER ====
const player = {
  x: 20 * TILE, // dalam tile coordinates (art px)
  y: 20 * TILE,
  w: 12, h: 16, // collision box (art px)
  speed: 1.2,
  dir: 'down', // up, down, left, right
  frame: 0,
  animTimer: 0,
  walkFrame: 0, // 0=idle, 1/2=walk cycle
  moving: false,
};

// ==== NPCs ====
const npcs = [
  { x: 15*TILE, y: 15*TILE, dir:'down', color:'#ff6b6b', name:'Warga',
    dialog:'Halo petualang! Ada koin tersebar di dunia ini, ambil semuanya ya!' },
  { x: 25*TILE, y: 12*TILE, dir:'left', color:'#4ecdc4', name:'Pedagang',
    dialog:'Aku pedagang keliling. Maaf daganganku sedang kosong 😅' },
  { x: 8*TILE, y: 22*TILE, dir:'right', color:'#ffe66d', name:'Petani',
    dialog:'Hati-hati di jalan! Ada air di timur laut.' },
];

// ==== COINS ====
let coins = [];
function spawnCoins() {
  for (let i=0; i<15; i++) {
    let tries = 0;
    while (tries < 50) {
      const x = Math.floor(Math.random() * WORLD_W);
      const y = Math.floor(Math.random() * WORLD_H);
      if (world[y][x] === 0) {
        coins.push({ x: x*TILE + 8, y: y*TILE + 8, got: false, bob: Math.random()*Math.PI*2 });
        break;
      }
      tries++;
    }
  }
}
spawnCoins();

// ==== CAMERA ====
const camera = { x: 0, y: 0 };

// ==== INPUT ====
const keys = {};
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key === 'e' || e.key === 'E') interact();
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

// ==== COLLISION ====
function isSolid(tileX, tileY) {
  if (tileX < 0 || tileY < 0 || tileX >= WORLD_W || tileY >= WORLD_H) return true;
  const t = world[tileY][tileX];
  return t === 2 || t === 3 || t === 5; // air, pohon, batu = solid
}

function canMoveTo(newX, newY) {
  // Cek 4 sudut collision box player
  const corners = [
    { x: newX, y: newY },
    { x: newX + player.w - 1, y: newY },
    { x: newX, y: newY + player.h - 1 },
    { x: newX + player.w - 1, y: newY + player.h - 1 },
  ];
  for (const c of corners) {
    const tx = Math.floor(c.x / TILE);
    const ty = Math.floor(c.y / TILE);
    if (isSolid(tx, ty)) return false;
  }
  return true;
}

// ==== INTERACT ====
let dialogTimer = 0;
function interact() {
  // Cek NPC terdekat
  for (const npc of npcs) {
    const dx = (npc.x + 8) - (player.x + player.w/2);
    const dy = (npc.y + 8) - (player.y + player.h/2);
    if (Math.hypot(dx, dy) < 30) {
      showDialog(`[${npc.name}] ${npc.dialog}`);
      return;
    }
  }
}
function showDialog(text) {
  const d = document.getElementById('dialog');
  d.textContent = text;
  d.style.display = 'block';
  dialogTimer = 200; // frames
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

  player.moving = (dx !== 0 || dy !== 0);

  if (dx !== 0 || dy !== 0) {
    // Prioritas: cek sumbu X dan Y terpisah buat sliding
    if (dx !== 0 && canMoveTo(player.x + dx, player.y)) player.x += dx;
    if (dy !== 0 && canMoveTo(player.x, player.y + dy)) player.y += dy;

    // Update arah
    if (Math.abs(dx) > Math.abs(dy)) {
      player.dir = dx > 0 ? 'right' : 'left';
    } else {
      player.dir = dy > 0 ? 'down' : 'up';
    }

    // Animasi walk
    player.animTimer++;
    if (player.animTimer > 8) {
      player.animTimer = 0;
      player.walkFrame = (player.walkFrame + 1) % 4;
    }
  } else {
    player.walkFrame = 0;
    player.animTimer = 0;
  }

  // Camera follow
  const targetCamX = player.x - canvas.width / (2*PX) + player.w/2;
  const targetCamY = player.y - canvas.height / (2*PX) + player.h/2;
  camera.x += (targetCamX - camera.x) * 0.1;
  camera.y += (targetCamY - camera.y) * 0.1;
  camera.x = Math.max(0, Math.min(WORLD_W*TILE - canvas.width/PX, camera.x));
  camera.y = Math.max(0, Math.min(WORLD_H*TILE - canvas.height/PX, camera.y));

  // Ambil koin
  coins.forEach(c => {
    if (!c.got) {
      const dx = c.x - (player.x + player.w/2);
      const dy = c.y - (player.y + player.h/2);
      if (Math.hypot(dx, dy) < 14) {
        c.got = true;
      }
    }
    c.bob += 0.1;
  });

  // Dialog timer
  if (dialogTimer > 0) {
    dialogTimer--;
    if (dialogTimer === 0) document.getElementById('dialog').style.display = 'none';
  }

  // HUD
  document.getElementById('px').textContent = Math.floor(player.x / TILE);
  document.getElementById('py').textContent = Math.floor(player.y / TILE);
  document.getElementById('coins').textContent = coins.filter(c => c.got).length;
  document.getElementById('total').textContent = coins.length;

  // Area
  const tx = Math.floor(player.x/TILE);
  const ty = Math.floor(player.y/TILE);
  let area = 'Meadow';
  if (tx > 28 && ty < 10) area = 'Lake';
  else if (tx < 10 && ty > 20) area = 'Farm';
  else if (Math.abs(tx - ty) < 3) area = 'Path';
  document.getElementById('area').textContent = area;
}

// ==== DRAWING HELPERS ====
function artPx(x, y, w, h, color) {
  // x,y dalam art pixel (koordinat world)
  ctx.fillStyle = color;
  const sx = Math.floor((x - camera.x) * PX);
  const sy = Math.floor((y - camera.y) * PX);
  ctx.fillRect(sx, sy, w*PX, h*PX);
}

// ==== DRAW TILES ====
function drawTile(t, x, y) {
  const wx = x * TILE;
  const wy = y * TILE;
  if (t === 0) {
    // Grass
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    // detail rumput
    artPx(wx+2, wy+3, 1, 1, '#4a9d54');
    artPx(wx+10, wy+6, 1, 1, '#4a9d54');
    artPx(wx+6, wy+11, 1, 1, '#2d5f35');
  } else if (t === 1) {
    // Dirt path
    artPx(wx, wy, TILE, TILE, '#8b6f47');
    artPx(wx+3, wy+5, 1, 1, '#6f5638');
    artPx(wx+9, wy+9, 1, 1, '#6f5638');
    artPx(wx+12, wy+3, 1, 1, '#a08056');
  } else if (t === 2) {
    // Water
    artPx(wx, wy, TILE, TILE, '#2a5db0');
    const wave = Math.sin(frameCount*0.05 + x + y) * 2;
    artPx(wx+3+wave, wy+4, 3, 1, '#4a7dd0');
    artPx(wx+9-wave, wy+10, 3, 1, '#4a7dd0');
  } else if (t === 3) {
    // Tree
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    // Trunk
    artPx(wx+6, wy+10, 4, 6, '#5a3a1a');
    // Foliage
    artPx(wx+2, wy+2, 12, 10, '#1e5a2a');
    artPx(wx+3, wy+1, 10, 2, '#2d7d3a');
    artPx(wx+4, wy+3, 3, 3, '#4a9d54');
  } else if (t === 4) {
    // Flower
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+6, wy+7, 4, 4, '#ff6b9d');
    artPx(wx+7, wy+8, 2, 2, '#ffeb3b');
    artPx(wx+4, wy+4, 2, 2, '#ff6b9d');
    artPx(wx+10, wy+10, 2, 2, '#ff6b9d');
  } else if (t === 5) {
    // Stone
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+3, wy+4, 10, 8, '#777');
    artPx(wx+4, wy+5, 8, 6, '#999');
    artPx(wx+5, wy+6, 3, 2, '#bbb');
  }
}

// ==== DRAW HUMANOID ====
function drawHumanoid(x, y, dir, walkFrame, color, isPlayer) {
  // x,y = world pixel coord (top-left)
  const skin = isPlayer ? '#ffcc99' : '#e8b088';
  const shirt = color;
  const pants = isPlayer ? '#1a3a8a' : '#553322';
  const hair = isPlayer ? '#3a2010' : '#222';

  // Offset animasi (naik turun sedikit)
  const bob = (walkFrame === 1 || walkFrame === 3) ? -1 : 0;
  const step = (walkFrame === 1) ? 1 : (walkFrame === 3) ? -1 : 0;

  // y = top of head. Total tinggi 16px
  // Kepala 6px, badan 5px, kaki 5px

  // HEAD (6x6)
  artPx(x+3, y+0+bob, 6, 6, skin);

  // Hair (tergantung arah)
  if (dir === 'down') {
    artPx(x+3, y+0+bob, 6, 2, hair);
    // mata
    artPx(x+4, y+3+bob, 1, 1, '#000');
    artPx(x+7, y+3+bob, 1, 1, '#000');
  } else if (dir === 'up') {
    artPx(x+3, y+0+bob, 6, 4, hair); // full head hair
  } else if (dir === 'left') {
    artPx(x+3, y+0+bob, 6, 2, hair);
    artPx(x+5, y+0+bob, 4, 4, hair); // rambut sisi kanan
    artPx(x+4, y+3+bob, 1, 1, '#000');
  } else { // right
    artPx(x+3, y+0+bob, 6, 2, hair);
    artPx(x+3, y+0+bob, 4, 4, hair);
    artPx(x+7, y+3+bob, 1, 1, '#000');
  }

  // BODY (6x5)
  artPx(x+3, y+6+bob, 6, 5, shirt);
  // tangan
  artPx(x+2, y+7+bob, 1, 3, skin);
  artPx(x+9, y+7+bob, 1, 3, skin);

  // LEGS (2 kaki 2px)
  const legY = y + 11 + bob;
  if (walkFrame === 1) {
    // Langkah kiri
    artPx(x+3, legY, 2, 5, pants);
    artPx(x+7, legY+1, 2, 4, pants);
  } else if (walkFrame === 3) {
    // Langkah kanan
    artPx(x+3, legY+1, 2, 4, pants);
    artPx(x+7, legY, 2, 5, pants);
  } else {
    // Idle
    artPx(x+3, legY, 2, 5, pants);
    artPx(x+7, legY, 2, 5, pants);
  }
  // Sepatu
  artPx(x+3, legY+4, 2, 1, '#000');
  artPx(x+7, legY+4, 2, 1, '#000');
}

// ==== DRAW NPC ====
function drawNpc(npc) {
  // Dilihat dari arah tertentu (idle)
  drawHumanoid(npc.x, npc.y, npc.dir, 0, npc.color, false);
}

// ==== DRAW COIN ====
function drawCoin(c) {
  if (c.got) return;
  const bob = Math.sin(c.bob) * 1.5;
  artPx(c.x - 4, c.y - 4 + bob, 6, 6, '#ffd700');
  artPx(c.x - 3, c.y - 3 + bob, 4, 4, '#ffed4a');
  artPx(c.x - 2, c.y - 2 + bob, 2, 2, '#fff');
}

// ==== MAIN DRAW ====
function draw() {
  // Background
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Visible tiles range
  const startX = Math.max(0, Math.floor(camera.x / TILE) - 1);
  const endX = Math.min(WORLD_W, Math.ceil((camera.x + canvas.width/PX) / TILE) + 1);
  const startY = Math.max(0, Math.floor(camera.y / TILE) - 1);
  const endY = Math.min(WORLD_H, Math.ceil((camera.y + canvas.height/PX) / TILE) + 1);

  for (let y=startY; y<endY; y++) {
    for (let x=startX; x<endX; x++) {
      drawTile(world[y][x], x, y);
    }
  }

  // Coins
  coins.forEach(drawCoin);

  // Sort entities by Y supaya yang di depan nutupin yang belakang
  const entities = [
    ...npcs.map(n => ({type:'npc', y:n.y, obj:n})),
    { type: 'player', y: player.y, obj: player },
  ];
  entities.sort((a,b) => a.y - b.y);

  entities.forEach(e => {
    if (e.type === 'player') {
      drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2', true);
    } else {
      drawNpc(e.obj);
    }
  });

  // Overlay gradient (mood)
  const grad = ctx.createRadialGradient(
    canvas.width/2, canvas.height/2, 100,
    canvas.width/2, canvas.height/2, canvas.width
  );
  grad.addColorStop(0, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,0,0.4)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// ==== LOOP ====
function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=560)
