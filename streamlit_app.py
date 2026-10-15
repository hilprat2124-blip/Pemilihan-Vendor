import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Catcher", page_icon="🎮", layout="centered")
st.title("🎮 Pixel Catcher")
st.caption("← → atau A/D buat gerak. Tangkap kotak, hindari bom!")

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; background:#1a1a2e; font-family:monospace; }
  canvas {
    display:block; margin:0 auto;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    border: 4px solid #0f0;
    box-shadow: 0 0 20px #0f0;
  }
  #hud {
    text-align:center; color:#0f0; font-size:20px;
    padding:10px; font-family:monospace;
    text-shadow: 0 0 5px #0f0;
  }
</style>
</head>
<body>
<div id="hud">SCORE: <span id="score">0</span> | LIVES: <span id="lives">❤❤❤</span></div>
<canvas id="game" width="480" height="480"></canvas>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PIXEL = 4;  // ukuran 1 pixel "art"
const W = canvas.width;
const H = canvas.height;

let keys = {};
let score = 0;
let lives = 3;
let player = { x: W/2 - 24, y: H - 40, w: 48, h: 16, speed: 6 };
let items = [];
let particles = [];
let stars = [];
let spawnTimer = 0;
let spawnInterval = 60;
let gameOver = false;
let frame = 0;

// Bintang latar
for (let i=0;i<40;i++){
  stars.push({x:Math.random()*W, y:Math.random()*H, s:Math.random()*2+1});
}

// Input
document.addEventListener('keydown', e => keys[e.key.toLowerCase()]=true);
document.addEventListener('keyup', e => keys[e.key.toLowerCase()]=false);

function drawPixel(x, y, size, color) {
  ctx.fillStyle = color;
  ctx.fillRect(Math.floor(x/PIXEL)*PIXEL, Math.floor(y/PIXEL)*PIXEL, size, size);
}

function drawPlayer() {
  // Keranjang pixel
  const x = player.x, y = player.y;
  // Body
  drawPixel(x, y+8, 48, '#8B4513');
  // Atas
  drawPixel(x, y+4, 48, '#A0522D');
  // Garis-garis pixel
  for (let i=0;i<48;i+=8){
    drawPixel(x+i, y+8, 4, '#6B3410');
    drawPixel(x+i, y+16, 4, '#6B3410');
  }
  // Rim highlight
  drawPixel(x, y, 48, '#D2691E');
}

function spawnItem() {
  const isBomb = Math.random() < 0.25;
  items.push({
    x: Math.floor(Math.random() * (W-24) / PIXEL) * PIXEL,
    y: -20,
    w: 16,
    h: 16,
    vy: 2 + Math.random()*2,
    type: isBomb ? 'bomb' : 'coin',
  });
}

function drawItem(it) {
  if (it.type === 'coin') {
    // Koin pixel emas
    drawPixel(it.x, it.y, 16, '#FFD700');
    drawPixel(it.x+4, it.y+4, 8, '#FFA500');
    drawPixel(it.x+8, it.y+8, 4, '#FFF700');
  } else {
    // Bom pixel
    drawPixel(it.x, it.y+4, 16, '#333');
    drawPixel(it.x+4, it.y, 8, '#333');
    drawPixel(it.x+6, it.y-4, 4, '#FF4500');
    drawPixel(it.x+4, it.y+8, 4, '#666');
    drawPixel(it.x+8, it.y+8, 4, '#666');
  }
}

function addParticles(x, y, color) {
  for (let i=0;i<10;i++){
    particles.push({
      x, y,
      vx: (Math.random()-0.5)*6,
      vy: (Math.random()-0.5)*6,
      life: 20,
      color
    });
  }
}

function update() {
  if (gameOver) return;
  frame++;

  // Gerak player
  if (keys['arrowleft'] || keys['a']) player.x -= player.speed;
  if (keys['arrowright'] || keys['d']) player.x += player.speed;
  player.x = Math.max(0, Math.min(W - player.w, player.x));

  // Spawn item
  spawnTimer++;
  if (spawnTimer > spawnInterval) {
    spawnItem();
    spawnTimer = 0;
    spawnInterval = Math.max(25, spawnInterval - 0.5);
  }

  // Update items
  items.forEach(it => it.y += it.vy);
  items = items.filter(it => it.y < H + 30);

  // Collision
  items.forEach(it => {
    if (it.y + it.h > player.y &&
        it.y < player.y + player.h &&
        it.x + it.w > player.x &&
        it.x < player.x + player.w) {
      if (it.type === 'coin') {
        score += 10;
        addParticles(it.x+8, it.y+8, '#FFD700');
      } else {
        lives--;
        addParticles(it.x+8, it.y+8, '#FF0000');
        if (lives <= 0) gameOver = true;
      }
      it.y = H + 100; // hilang
    }
  });

  // Particles
  particles.forEach(p => { p.x+=p.vx; p.y+=p.vy; p.life--; p.vy+=0.2; });
  particles = particles.filter(p => p.life > 0);

  // Update HUD
  document.getElementById('score').textContent = score;
  document.getElementById('lives').textContent = '❤'.repeat(Math.max(0, lives));
}

function drawBackground() {
  // Gradient gelap
  const grad = ctx.createLinearGradient(0,0,0,H);
  grad.addColorStop(0, '#0a0a1e');
  grad.addColorStop(1, '#1a1a3e');
  ctx.fillStyle = grad;
  ctx.fillRect(0,0,W,H);

  // Bintang pixel
  stars.forEach(s => {
    ctx.fillStyle = `rgba(255,255,255,${0.3 + Math.sin(frame*0.05 + s.x)*0.2})`;
    ctx.fillRect(Math.floor(s.x/PIXEL)*PIXEL, Math.floor(s.y/PIXEL)*PIXEL, PIXEL, PIXEL);
  });

  // Lantai pixel
  for (let i=0;i<W;i+=PIXEL*4){
    ctx.fillStyle = i % (PIXEL*8) === 0 ? '#2a2a4e' : '#252545';
    ctx.fillRect(i, H - PIXEL*2, PIXEL*4, PIXEL*2);
  }
}

function drawGameOver() {
  ctx.fillStyle = 'rgba(0,0,0,0.8)';
  ctx.fillRect(0, H/2 - 60, W, 120);
  ctx.fillStyle = '#f00';
  ctx.font = 'bold 32px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('GAME OVER', W/2, H/2);
  ctx.fillStyle = '#0f0';
  ctx.font = 'bold 16px monospace';
  ctx.fillText('SCORE: ' + score, W/2, H/2 + 30);
  ctx.fillText('Klik untuk main lagi', W/2, H/2 + 50);
}

function draw() {
  drawBackground();
  items.forEach(drawItem);
  drawPlayer();

  // Particles pixel
  particles.forEach(p => {
    ctx.globalAlpha = p.life/20;
    ctx.fillStyle = p.color;
    ctx.fillRect(Math.floor(p.x/PIXEL)*PIXEL, Math.floor(p.y/PIXEL)*PIXEL, PIXEL, PIXEL);
  });
  ctx.globalAlpha = 1;

  if (gameOver) drawGameOver();
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

canvas.addEventListener('click', () => {
  if (gameOver) {
    score = 0; lives = 3; items = []; particles = [];
    player.x = W/2 - 24; gameOver = false;
    spawnInterval = 60; spawnTimer = 0;
  }
});

loop();
</script>
</body>
</html>
"""

components.html(game_html, height=560)
