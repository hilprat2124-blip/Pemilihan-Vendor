import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simple FPS", page_icon="🔫", layout="wide")

st.title("🔫 Simple FPS - Target Shooter")
st.caption("Klik area game dulu → **WASD** gerak, **Mouse** aim, **Klik** nembak, **R** reload")

# Game HTML + JS
fps_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; background:#111; overflow:hidden; font-family: monospace; }
  canvas { display:block; cursor: crosshair; }
  #hud {
    position:absolute; top:10px; left:10px; color:#0f0;
    font-size:18px; text-shadow:0 0 5px #0f0; pointer-events:none;
  }
  #crosshair {
    position:absolute; pointer-events:none; color:#0f0;
    font-size:24px; transform:translate(-50%,-50%);
    text-shadow:0 0 5px #0f0;
  }
  #gameover {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    color:#f00; font-size:48px; text-align:center; display:none;
    text-shadow:0 0 20px #f00;
  }
</style>
</head>
<body>
<canvas id="game"></canvas>
<div id="hud">HP: <span id="hp">100</span> | KILLS: <span id="kills">0</span> | AMMO: <span id="ammo">12</span>/12</div>
<div id="crosshair">+</div>
<div id="gameover">GAME OVER<br><small style="font-size:20px">Tekan R untuk restart</small></div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

// Resize canvas
function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight - 100;
}
resize();
window.addEventListener('resize', resize);

// State
let keys = {};
let mouseX = canvas.width/2;
let mouseY = canvas.height/2;
let player = { x: canvas.width/2, y: canvas.height/2, hp:100, speed:4 };
let kills = 0;
let ammo = 12;
let maxAmmo = 12;
let reloading = false;
let enemies = [];
let bullets = [];
let particles = [];
let gameOver = false;
let lastEnemySpawn = 0;
let spawnInterval = 1200; // ms

// Input
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key.toLowerCase() === 'r' && !reloading && ammo < maxAmmo && !gameOver) {
    reload();
  }
  if (e.key.toLowerCase() === 'r' && gameOver) {
    resetGame();
  }
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  mouseX = e.clientX - rect.left;
  mouseY = e.clientY - rect.top;
  document.getElementById('crosshair').style.left = e.clientX + 'px';
  document.getElementById('crosshair').style.top = (e.clientY - rect.top + canvas.offsetTop) + 'px';
});

canvas.addEventListener('mousedown', e => {
  if (e.button === 0) shoot();
});

function shoot() {
  if (gameOver || reloading || ammo <= 0) {
    if (ammo <= 0 && !reloading) reload();
    return;
  }
  ammo--;
  updateHUD();

  // Hitung arah dari player ke mouse
  const dx = mouseX - player.x;
  const dy = mouseY - player.y;
  const dist = Math.hypot(dx, dy);

  bullets.push({
    x: player.x, y: player.y,
    vx: dx/dist * 18, vy: dy/dist * 18,
    life: 60
  });

  // Muzzle flash
  for (let i=0;i<5;i++){
    particles.push({
      x:player.x, y:player.y,
      vx:(Math.random()-0.5)*6, vy:(Math.random()-0.5)*6,
      life:10, color:'#ff0'
    });
  }
}

function reload() {
  reloading = true;
  setTimeout(() => {
    ammo = maxAmmo;
    reloading = false;
    updateHUD();
  }, 1000);
}

function spawnEnemy() {
  // Spawn di pinggir layar
  const side = Math.floor(Math.random()*4);
  let x, y;
  if (side===0){ x=Math.random()*canvas.width; y=-30; }
  else if (side===1){ x=canvas.width+30; y=Math.random()*canvas.height; }
  else if (side===2){ x=Math.random()*canvas.width; y=canvas.height+30; }
  else { x=-30; y=Math.random()*canvas.height; }

  enemies.push({
    x, y, r:20, hp:1,
    speed:1.2 + Math.random()*0.8,
    color:`hsl(${Math.random()*60},80%,50%)` // merah-kuning
  });
}

function updateHUD() {
  document.getElementById('hp').textContent = player.hp;
  document.getElementById('kills').textContent = kills;
  document.getElementById('ammo').textContent = ammo;
}

function resetGame() {
  player.hp = 100;
  kills = 0;
  ammo = 12;
  enemies = [];
  bullets = [];
  particles = [];
  gameOver = false;
  document.getElementById('gameover').style.display = 'none';
  updateHUD();
}

function update(dt) {
  if (gameOver) return;

  // Movement
  if (keys['w']) player.y -= player.speed;
  if (keys['s']) player.y += player.speed;
  if (keys['a']) player.x -= player.speed;
  if (keys['d']) player.x += player.speed;
  player.x = Math.max(15, Math.min(canvas.width-15, player.x));
  player.y = Math.max(15, Math.min(canvas.height-15, player.y));

  // Spawn musuh
  const now = Date.now();
  if (now - lastEnemySpawn > spawnInterval) {
    spawnEnemy();
    lastEnemySpawn = now;
    // Makin lama makin susah
    spawnInterval = Math.max(400, spawnInterval - 20);
  }

  // Update bullets
  bullets.forEach(b => {
    b.x += b.vx; b.y += b.vy; b.life--;
  });
  bullets = bullets.filter(b => b.life>0 && b.x>0 && b.x<canvas.width && b.y>0 && b.y<canvas.height);

  // Update enemies — chase player
  enemies.forEach(en => {
    const dx = player.x - en.x;
    const dy = player.y - en.y;
    const d = Math.hypot(dx, dy) || 1;
    en.x += dx/d * en.speed;
    en.y += dy/d * en.speed;
  });

  // Bullet vs enemy collision
  bullets.forEach(b => {
    enemies.forEach(en => {
      if (en.hp > 0 && Math.hypot(b.x-en.x, b.y-en.y) < en.r) {
        en.hp = 0;
        b.life = 0;
        kills++;
        updateHUD();
        // blood particles
        for (let i=0;i<12;i++){
          particles.push({
            x:en.x, y:en.y,
            vx:(Math.random()-0.5)*8, vy:(Math.random()-0.5)*8,
            life:25, color:'#f00'
          });
        }
      }
    });
  });
  enemies = enemies.filter(e => e.hp > 0);

  // Enemy vs player
  enemies.forEach(en => {
    if (Math.hypot(en.x-player.x, en.y-player.y) < en.r + 12) {
      player.hp -= 0.5;
      if (player.hp <= 0) {
        player.hp = 0;
        gameOver = true;
        document.getElementById('gameover').style.display = 'block';
        updateHUD();
      }
    }
  });

  // Update particles
  particles.forEach(p => {
    p.x += p.vx; p.y += p.vy; p.life--;
    p.vx *= 0.95; p.vy *= 0.95;
  });
  particles = particles.filter(p => p.life>0);
}

function draw() {
  // Background grid
  ctx.fillStyle = '#111';
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.strokeStyle = '#1a1a1a';
  ctx.lineWidth = 1;
  for (let x=0; x<canvas.width; x+=50){
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke();
  }
  for (let y=0; y<canvas.height; y+=50){
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke();
  }

  // Player
  ctx.beginPath();
  ctx.arc(player.x, player.y, 14, 0, Math.PI*2);
  ctx.fillStyle = '#0f0';
  ctx.shadowColor = '#0f0'; ctx.shadowBlur = 15;
  ctx.fill();
  ctx.shadowBlur = 0;

  // Arah hadap
  const angle = Math.atan2(mouseY-player.y, mouseX-player.x);
  ctx.beginPath();
  ctx.moveTo(player.x, player.y);
  ctx.lineTo(player.x + Math.cos(angle)*25, player.y + Math.sin(angle)*25);
  ctx.strokeStyle = '#0f0'; ctx.lineWidth = 4;
  ctx.stroke();

  // Bullets
  bullets.forEach(b => {
    ctx.beginPath();
    ctx.arc(b.x, b.y, 3, 0, Math.PI*2);
    ctx.fillStyle = '#ff0';
    ctx.shadowColor = '#ff0'; ctx.shadowBlur = 10;
    ctx.fill();
  });
  ctx.shadowBlur = 0;

  // Enemies
  enemies.forEach(en => {
    ctx.beginPath();
    ctx.arc(en.x, en.y, en.r, 0, Math.PI*2);
    ctx.fillStyle = en.color;
    ctx.shadowColor = '#f00'; ctx.shadowBlur = 15;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Mata musuh
    ctx.fillStyle = '#fff';
    ctx.beginPath(); ctx.arc(en.x-6, en.y-4, 3, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(en.x+6, en.y-4, 3, 0, Math.PI*2); ctx.fill();
  });

  // Particles
  particles.forEach(p => {
    ctx.globalAlpha = p.life/25;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 3, 0, Math.PI*2);
    ctx.fillStyle = p.color;
    ctx.fill();
  });
  ctx.globalAlpha = 1;

  // Crosshair beneran di canvas (fallback kalau div gagal)
  ctx.strokeStyle = '#0f0';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(mouseX-10, mouseY); ctx.lineTo(mouseX-4, mouseY);
  ctx.moveTo(mouseX+4, mouseY); ctx.lineTo(mouseX+10, mouseY);
  ctx.moveTo(mouseX, mouseY-10); ctx.lineTo(mouseX, mouseY-4);
  ctx.moveTo(mouseX, mouseY+4); ctx.lineTo(mouseX, mouseY+10);
  ctx.stroke();
}

let lastTime = 0;
function loop(t) {
  update(t - lastTime);
  draw();
  lastTime = t;
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
</script>
</body>
</html>
"""

components.html(fps_html, height=700, scrolling=False)
