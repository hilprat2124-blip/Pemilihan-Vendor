import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Farm RPG", page_icon="🌾", layout="wide")
st.title("🌾 Pixel Farm RPG - Fixed")
st.caption("**WASD** jalan • **Klik** action • **1-8** tool • **I** inventory • **M** mute • **E** interaksi")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#0a0a1e; font-family:'Courier New',monospace; overflow:hidden; color:#fff; }
  #gameWrap { position:relative; width:100vw; height:100vh; display:flex; justify-content:center; align-items:center; }
  canvas { image-rendering:pixelated; border:4px solid #2a2a3e; box-shadow:0 0 40px rgba(0,255,0,0.2); background:#000; cursor:crosshair; }
  #hud { position:absolute; top:12px; left:12px; display:flex; flex-direction:column; gap:6px; pointer-events:none; font-size:13px; }
  .bar { width:180px; height:22px; background:rgba(0,0,0,0.7); border:2px solid #222; border-radius:3px; position:relative; overflow:hidden; }
  .bar .fill { height:100%; transition:width 0.3s; }
  .bar .label { position:absolute; top:0; left:8px; line-height:18px; font-size:12px; font-weight:bold; text-shadow:1px 1px 0 #000; }
  #hpFill { background:linear-gradient(180deg, #ff4444, #aa0000); }
  #hungerFill { background:linear-gradient(180deg, #ffaa00, #cc6600); }
  #topRight { position:absolute; top:12px; right:12px; background:rgba(0,0,0,0.7); border:2px solid #222; border-radius:4px; padding:8px 14px; font-size:13px; text-align:right; pointer-events:none; line-height:1.6; }
  #timeOfDay { color:#ffed4a; font-weight:bold; font-size:14px; text-shadow:0 0 8px currentColor; }
  #gold { color:#ffd700; font-weight:bold; text-shadow:0 0 8px #ffd700; }
  #toolbar { position:absolute; bottom:16px; left:50%; transform:translateX(-50%); display:flex; gap:5px; background:rgba(0,0,0,0.85); padding:8px; border:2px solid #2a2a3e; border-radius:8px; flex-wrap:wrap; justify-content:center; max-width:90%; }
  .tool { padding:7px 10px; background:rgba(30,30,50,0.9); border:2px solid #333; color:#888; font-family:inherit; font-size:11px; cursor:pointer; border-radius:5px; user-select:none; transition:all 0.15s; min-width:54px; text-align:center; position:relative; }
  .tool:hover { background:rgba(50,50,80,0.9); border-color:#666; color:#ccc; transform:translateY(-2px); }
  .tool.active { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border-color:#ffed4a; color:#ffed4a; box-shadow:0 0 15px rgba(255,237,74,0.6); font-weight:bold; }
  .tool .num { position:absolute; top:1px; left:4px; font-size:9px; color:#666; }
  .tool.active .num { color:#ffed4a; }
  #inv, #shop, #achPanel { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(15,15,25,0.97); border:3px solid #2a2a3e; border-radius:10px; padding:20px; display:none; box-shadow:0 0 40px rgba(0,0,0,0.9); z-index:100; min-width:440px; max-width:600px; }
  #inv h2, #shop h2, #achPanel h2 { color:#ffed4a; margin:0 0 16px 0; font-size:18px; border-bottom:2px solid #2a2a3e; padding-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
  .closeBtn { background:none; border:1px solid #666; color:#ff6666; width:26px; height:26px; border-radius:4px; cursor:pointer; font-family:inherit; font-size:14px; }
  .closeBtn:hover { border-color:#ff6666; background:rgba(255,50,50,0.2); }
  #invGrid { display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; }
  .invSlot { aspect-ratio:1; background:rgba(30,30,50,0.7); border:2px solid #333; border-radius:6px; display:flex; flex-direction:column; align-items:center; justify-content:center; cursor:pointer; transition:all 0.15s; position:relative; min-height:60px; }
  .invSlot:hover { border-color:#ffed4a; background:rgba(50,50,80,0.9); transform:scale(1.05); }
  .invSlot .emoji { font-size:24px; line-height:1; }
  .invSlot .name { font-size:9px; color:#aaa; margin-top:2px; }
  .invSlot .count { position:absolute; bottom:2px; right:4px; font-size:11px; font-weight:bold; color:#ffed4a; text-shadow:1px 1px 0 #000; }
  #invHint { margin-top:12px; font-size:11px; color:#666; text-align:center; }
  .shopItem { display:flex; justify-content:space-between; align-items:center; padding:10px; background:rgba(30,30,50,0.7); border:2px solid #333; border-radius:6px; margin-bottom:8px; }
  .shopItem .info { display:flex; align-items:center; gap:10px; }
  .shopItem .emoji { font-size:24px; }
  .shopItem .name { color:#fff; font-size:14px; }
  .shopItem .price { color:#ffd700; font-size:13px; }
  .shopItem button { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border:2px solid #5aff5a; color:#5aff5a; padding:6px 14px; font-family:inherit; font-size:12px; border-radius:4px; cursor:pointer; font-weight:bold; }
  .shopItem button:hover { background:linear-gradient(180deg, #3a7d3a, #2a5d2a); }
  .shopItem button:disabled { opacity:0.3; cursor:not-allowed; }
  .shopTabs { display:flex; gap:6px; margin-bottom:12px; }
  .shopTab { flex:1; padding:8px; text-align:center; background:rgba(30,30,50,0.7); border:2px solid #333; color:#888; font-family:inherit; font-size:13px; border-radius:4px; cursor:pointer; user-select:none; }
  .shopTab.active { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border-color:#ffed4a; color:#ffed4a; }
  .achGrid { display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; }
  .achItem { display:flex; gap:10px; align-items:center; padding:10px; background:rgba(30,30,50,0.5); border:2px solid #333; border-radius:6px; opacity:0.4; }
  .achItem.unlocked { opacity:1; border-color:#ffed4a; background:linear-gradient(180deg, rgba(50,50,20,0.7), rgba(30,30,50,0.7)); box-shadow:0 0 10px rgba(255,237,74,0.3); }
  .achItem .emoji { font-size:28px; }
  .achItem .achName { color:#ffed4a; font-size:13px; font-weight:bold; }
  .achItem .achDesc { color:#aaa; font-size:10px; margin-top:2px; }
  #dialog { position:absolute; bottom:90px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.92); border:3px solid #ffed4a; color:#ffed4a; padding:14px 24px; font-size:15px; display:none; min-width:400px; text-align:center; box-shadow:0 0 30px rgba(255,237,74,0.4); border-radius:6px; max-width:600px; }
  #toast { position:absolute; top:100px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.9); border:2px solid #ffed4a; color:#ffed4a; padding:10px 20px; font-size:15px; display:none; box-shadow:0 0 20px rgba(255,237,74,0.5); border-radius:4px; pointer-events:none; font-weight:bold; z-index:200; }
  #achPop { position:absolute; top:160px; left:50%; transform:translateX(-50%); background:linear-gradient(180deg, rgba(80,60,0,0.98), rgba(40,30,0,0.98)); border:3px solid #ffed4a; color:#ffed4a; padding:14px 24px; display:none; box-shadow:0 0 40px rgba(255,237,74,0.8); border-radius:8px; pointer-events:none; z-index:300; min-width:300px; text-align:center; animation: achSlide 0.4s; }
  @keyframes achSlide { from { transform: translate(-50%, -30px); opacity: 0; } to { transform: translate(-50%, 0); opacity: 1; } }
  #achPop .title { font-size:12px; color:#ffaa00; letter-spacing:3px; }
  #achPop .name { font-size:18px; font-weight:bold; margin:4px 0; }
  #achPop .desc { font-size:11px; color:#aaa; }
  #damageFlash { position:absolute; inset:0; background:radial-gradient(circle, transparent 30%, rgba(255,0,0,0.6) 100%); opacity:0; pointer-events:none; transition:opacity 0.2s; z-index:50; }
  #hint { position:absolute; bottom:12px; right:12px; font-size:10px; color:#555; text-align:right; line-height:1.6; }
  #muteIcon { position:absolute; bottom:12px; left:12px; font-size:20px; cursor:pointer; padding:6px; user-select:none; transition:transform 0.2s; }
  #muteIcon:hover { transform:scale(1.2); }
  #stats { position:absolute; top:12px; left:210px; font-size:11px; color:#888; background:rgba(0,0,0,0.6); padding:6px 10px; border-radius:4px; border:1px solid #222; pointer-events:none; line-height:1.5; }
  #saveIndicator { position:absolute; top:12px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.85); color:#5aff5a; padding:6px 14px; border-radius:4px; font-size:12px; border:2px solid #5aff5a; display:none; z-index:150; box-shadow:0 0 15px rgba(90,255,90,0.4); }
  #bedPrompt { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.92); border:3px solid #4a90e2; color:#4a90e2; padding:16px 28px; font-size:16px; display:none; text-align:center; border-radius:8px; box-shadow:0 0 30px rgba(74,144,226,0.5); z-index:150; pointer-events:none; }
  #saveBtn { position:absolute; top:60px; left:12px; background:rgba(30,30,50,0.9); border:2px solid #444; color:#5aff5a; padding:6px 12px; font-family:inherit; font-size:11px; cursor:pointer; border-radius:4px; transition:all 0.15s; }
  #saveBtn:hover { border-color:#5aff5a; box-shadow:0 0 10px rgba(90,255,90,0.4); }
  #achBtn { position:absolute; top:60px; left:90px; background:rgba(30,30,50,0.9); border:2px solid #444; color:#ffed4a; padding:6px 12px; font-family:inherit; font-size:11px; cursor:pointer; border-radius:4px; }
  #achBtn:hover { border-color:#ffed4a; box-shadow:0 0 10px rgba(255,237,74,0.4); }
  #fishIndicator { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.9); border:3px solid #4a90e2; color:#4a90e2; padding:14px 24px; font-size:15px; display:none; text-align:center; border-radius:8px; box-shadow:0 0 30px rgba(74,144,226,0.5); z-index:150; pointer-events:none; min-width:280px; }
  #fishBar { width:220px; height:20px; background:rgba(0,0,0,0.7); border:2px solid #4a90e2; border-radius:3px; margin:10px auto 0; position:relative; overflow:hidden; }
  #fishBar .fill { height:100%; background:linear-gradient(90deg, #4a90e2, #5aff5a); width:0%; transition:width 0.05s; }
  .seedPicker { display:flex; gap:6px; margin-top:10px; padding:8px; background:rgba(0,0,0,0.5); border-radius:6px; }
  .seedOpt { flex:1; padding:8px; text-align:center; background:rgba(30,30,50,0.7); border:2px solid #333; color:#aaa; font-family:inherit; font-size:11px; border-radius:4px; cursor:pointer; user-select:none; }
  .seedOpt.active { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border-color:#ffed4a; color:#ffed4a; }
  #seedPickerWrap { position:absolute; bottom:110px; left:50%; transform:translateX(-50%); background:rgba(15,15,25,0.95); border:2px solid #ffed4a; border-radius:8px; padding:10px; display:none; z-index:80; }
</style>
</head>
<body>
<div id="gameWrap">
  <canvas id="game" width="820" height="560"></canvas>
  <div id="damageFlash"></div>
  <div id="hud">
    <div class="bar"><div class="fill" id="hpFill" style="width:100%"></div><div class="label">❤️ <span id="hpText">100/100</span></div></div>
    <div class="bar"><div class="fill" id="hungerFill" style="width:100%"></div><div class="label">🍗 <span id="hungerText">100/100</span></div></div>
  </div>
  <div id="topRight">
    <div id="timeOfDay">🌅 Pagi</div>
    <div>Day <span id="dayNum">1</span> — <span id="clock">06:00</span></div>
    <div>🪙 <span id="gold">0</span></div>
  </div>
  <div id="stats">🪵 <span id="wood">0</span> · 🍗 <span id="food">0</span> · 🌾 <span id="wheat">0</span> · 🏹 <span id="arrows">10</span></div>
  <div id="toolbar">
    <div class="tool" data-tool="hoe"><span class="num">1</span>🪓<br>Hoe</div>
    <div class="tool" data-tool="seed"><span class="num">2</span>🌱<br>Seed</div>
    <div class="tool" data-tool="water"><span class="num">3</span>💧<br>Water</div>
    <div class="tool" data-tool="harvest"><span class="num">4</span>🌾<br>Harvest</div>
    <div class="tool" data-tool="axe"><span class="num">5</span>🪓<br>Axe</div>
    <div class="tool" data-tool="sword"><span class="num">6</span>⚔️<br>Sword</div>
    <div class="tool" data-tool="bow"><span class="num">7</span>🏹<br>Bow</div>
    <div class="tool" data-tool="rod"><span class="num">8</span>🎣<br>Fishing</div>
  </div>
  <div id="seedPickerWrap">
    <div style="color:#ffed4a;font-size:12px;margin-bottom:6px;text-align:center">🌱 Pilih Benih:</div>
    <div class="seedPicker">
      <div class="seedOpt" data-seed="wheat">🌾 Gandum<br><small>10g</small></div>
      <div class="seedOpt" data-seed="corn">🌽 Jagung<br><small>25g</small></div>
      <div class="seedOpt" data-seed="tomato">🍅 Tomat<br><small>40g</small></div>
    </div>
  </div>
  <div id="inv"><h2>🎒 Inventory <button class="closeBtn" onclick="toggleInventory()">✕</button></h2><div id="invGrid"></div><div id="invHint">Klik food buat makan · Klik item buat jual</div></div>
  <div id="shop"><h2>🏪 Toko <button class="closeBtn" onclick="toggleShop()">✕</button></h2><div class="shopTabs"><div class="shopTab active" data-tab="buy">🛒 Beli</div><div class="shopTab" data-tab="sell">💰 Jual</div></div><div id="shopContent"></div></div>
  <div id="achPanel"><h2>🏆 Achievement <button class="closeBtn" onclick="toggleAch()">✕</button></h2><div class="achGrid" id="achGrid"></div></div>
  <div id="dialog"></div>
  <div id="toast"></div>
  <div id="achPop"><div class="title">🏆 ACHIEVEMENT UNLOCKED</div><div class="name" id="achPopName"></div><div class="desc" id="achPopDesc"></div></div>
  <div id="muteIcon">🔊</div>
  <div id="saveBtn">💾 Save</div>
  <div id="achBtn">🏆 Trophy</div>
  <div id="saveIndicator">💾 Tersimpan!</div>
  <div id="bedPrompt">🛏️<br>Tekan <b>E</b> untuk tidur<br><small>Skip ke pagi berikutnya</small></div>
  <div id="fishIndicator">🎣 <span id="fishStatus">Menunggu...</span><div id="fishBar"><div class="fill" id="fishBarFill"></div></div><div style="font-size:11px;color:#888;margin-top:6px" id="fishHint"></div></div>
  <div id="hint">WASD = jalan • Klik = action • 1-8 = tool<br>E = interaksi/toko • I = inventory • M = mute</div>
</div>

<script>
// ============================================
// ==== AUDIO ====
// ============================================
let audioCtx = null, masterGain = null, musicGain = null, sfxGain = null;
let musicPlaying = false, musicTimer = null, muted = false, masterVolume = 0.7;
let currentMusicPhase = 'dawn';

function initAudio() {
  if (audioCtx) return;
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = audioCtx.createGain(); masterGain.gain.value = masterVolume;
    masterGain.connect(audioCtx.destination);
    musicGain = audioCtx.createGain(); musicGain.gain.value = 0.20; musicGain.connect(masterGain);
    sfxGain = audioCtx.createGain(); sfxGain.gain.value = 0.4; sfxGain.connect(masterGain);
    startMusic('dawn');
  } catch(e) { console.error('Audio init error:', e); }
}
function playTone(f, d, t='square', v=1, w=0) {
  if (!audioCtx || muted) return;
  try {
    const tt = audioCtx.currentTime + w;
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.type = t; o.frequency.value = f;
    g.gain.setValueAtTime(0.001, tt);
    g.gain.exponentialRampToValueAtTime(0.25*v, tt+0.01);
    g.gain.exponentialRampToValueAtTime(0.001, tt+d);
    o.connect(g); g.connect(sfxGain);
    o.start(tt); o.stop(tt+d+0.05);
  } catch(e) {}
}
function playNoise(d, v=1, f=800) {
  if (!audioCtx || muted) return;
  try {
    const bs = audioCtx.sampleRate * d;
    const buf = audioCtx.createBuffer(1, bs, audioCtx.sampleRate);
    const dd = buf.getChannelData(0);
    for (let i=0; i<bs; i++) dd[i] = (Math.random()*2-1)*(1-i/bs);
    const s = audioCtx.createBufferSource(); s.buffer = buf;
    const g = audioCtx.createGain(); g.gain.value = 0.3*v;
    const fl = audioCtx.createBiquadFilter(); fl.type='lowpass'; fl.frequency.value = f;
    s.connect(fl); fl.connect(g); g.connect(sfxGain); s.start();
  } catch(e) {}
}
function sfxHoe() { playNoise(0.14,1,900); playTone(110,0.18,'sawtooth',1); playTone(75,0.15,'sawtooth',0.8,0.04); }
function sfxSeed() { playTone(700,0.08,'sine',1); playTone(950,0.1,'sine',0.9,0.05); }
function sfxWater() { playTone(1100,0.15,'sine',1); playTone(800,0.12,'sine',0.9,0.06); playTone(550,0.12,'sine',0.8,0.12); }
function sfxHarvest() { playTone(523,0.1,'square',1); playTone(659,0.1,'square',1,0.07); playTone(784,0.13,'square',1,0.14); playTone(1047,0.18,'square',1,0.21); }
function sfxSell() { playTone(988,0.07,'square',1); playTone(1319,0.15,'square',1,0.06); playTone(1568,0.12,'square',0.9,0.14); }
function sfxBuy() { playTone(400,0.08,'square',1); playTone(600,0.1,'square',0.9,0.06); playTone(800,0.12,'square',0.8,0.14); }
function sfxError() { playTone(180,0.15,'sawtooth',0.8); }
function sfxClick() { playTone(1400,0.03,'square',0.6); }
function sfxAxe() { playNoise(0.2,1.2,1200); playTone(160,0.15,'square',1); playTone(90,0.2,'square',0.8,0.05); }
function sfxHit() { playNoise(0.12,0.8,2000); playTone(400,0.08,'square',0.8); }
function sfxAnimalHurt() { playTone(600,0.1,'sawtooth',0.9); playTone(400,0.15,'sawtooth',0.8,0.08); }
function sfxEat() { playTone(300,0.06,'square',0.9); playTone(400,0.06,'square',0.9,0.08); playTone(500,0.08,'square',0.8,0.16); }
function sfxHurt() { playTone(200,0.2,'sawtooth',1); playTone(150,0.2,'sawtooth',0.9,0.1); }
function sfxBowShoot() { playTone(880,0.08,'triangle',1); playTone(660,0.1,'triangle',0.9,0.05); playNoise(0.06,0.5,3000); }
function sfxArrowHit() { playNoise(0.1,1,1500); playTone(300,0.08,'square',0.9); }
function sfxWolfHowl() { playTone(300,0.5,'sawtooth',1); playTone(400,0.4,'sawtooth',1,0.15); playTone(350,0.5,'sawtooth',0.9,0.4); }
function sfxWolfBite() { playNoise(0.15,1.2,500); playTone(150,0.2,'sawtooth',1); }
function sfxDoor() { playTone(350,0.1,'triangle',0.9); playTone(250,0.15,'triangle',0.8,0.08); playNoise(0.08,0.4,400); }
function sfxSleep() { playTone(523,0.15,'sine',0.8); playTone(659,0.15,'sine',0.7,0.2); playTone(784,0.15,'sine',0.7,0.4); playTone(1047,0.3,'sine',0.6,0.6); }
function sfxSave() { playTone(880,0.08,'sine',1); playTone(1175,0.12,'sine',0.9,0.06); }
function sfxFishCast() { playNoise(0.15,0.8,3000); playTone(500,0.1,'sine',0.8,0.05); }
function sfxFishBite() { playTone(700,0.08,'square',1); playTone(900,0.08,'square',1,0.06); playTone(1100,0.12,'square',1,0.12); }
function sfxFishCatch() { playTone(660,0.1,'triangle',1); playTone(880,0.12,'triangle',1,0.08); playTone(1320,0.2,'triangle',0.9,0.18); }
function sfxFishMiss() { playTone(200,0.2,'sawtooth',0.8); playTone(150,0.15,'sawtooth',0.7,0.1); }
function sfxAchievement() { playTone(523,0.12,'square',1); playTone(659,0.12,'square',1,0.1); playTone(784,0.12,'square',1,0.2); playTone(1047,0.25,'square',1,0.3); playTone(1319,0.3,'square',0.9,0.42); }

const scales = {
  dawn: [261.63, 293.66, 329.63, 392, 440, 523.25],
  day: [392, 440, 493.88, 587.33, 659.25, 783.99],
  evening: [349.23, 392, 440, 523.25, 587.33, 698.46],
  night: [220, 246.94, 261.63, 329.63, 349.23, 440],
  interior: [329.63, 392, 440, 493.88, 587.33, 659.25],
};
function startMusic(phase) {
  if (!audioCtx) return;
  if (musicPlaying && currentMusicPhase === phase) return;
  if (musicTimer) clearTimeout(musicTimer);
  musicPlaying = true; currentMusicPhase = phase; playMusicLoop();
}
function playMusicLoop() {
  if (!audioCtx || !musicPlaying) return;
  const scale = scales[currentMusicPhase] || scales.day;
  const isNight = currentMusicPhase === 'night';
  const isDawn = currentMusicPhase === 'dawn';
  const isInt = currentMusicPhase === 'interior';
  const bT = isNight ? 0.7 : isDawn ? 0.55 : isInt ? 0.6 : 0.45;
  const start = audioCtx.currentTime + 0.05;
  const TN = 16, notes = [];
  for (let i=0; i<TN; i++) {
    const r = Math.random() < (isNight ? 0.4 : isInt ? 0.5 : 0.3);
    if (r) { notes.push(null); continue; }
    const n = scale[Math.floor(Math.random()*scale.length)];
    const up = Math.random() < 0.15 ? 2 : 1;
    notes.push(n*up);
  }
  notes.forEach((n, i) => {
    if (n === null) return;
    const t = start + i*bT;
    const vol = isNight ? 0.3 : 0.45;
    const type = isNight ? 'triangle' : (isDawn || isInt ? 'sine' : 'square');
    scheduleNote(n, t, bT*0.85, type, vol);
  });
  for (let i=0; i<TN; i+=4) scheduleNote(scale[0]/4, start + i*bT, bT*3.5, 'triangle', 0.5);
  musicTimer = setTimeout(() => { if (musicPlaying) playMusicLoop(); }, TN*bT*1000);
}
function scheduleNote(f, st, dur, type, vol) {
  if (!audioCtx) return;
  try {
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.type = type; o.frequency.value = f;
    g.gain.setValueAtTime(0.001, st);
    g.gain.exponentialRampToValueAtTime(vol, st+0.02);
    g.gain.exponentialRampToValueAtTime(0.001, st+dur);
    o.connect(g); g.connect(musicGain);
    o.start(st); o.stop(st+dur+0.05);
  } catch(e) {}
}

// ============================================
// ==== GAME CONSTANTS ====
// ============================================
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;
const PX = 5, TILE = 16, WORLD_W = 40, WORLD_H = 30;

const T_GRASS=0,T_PATH=1,T_WATER=2,T_TREE=3,T_FARMLAND=4,T_CROP=5,
      T_HOUSE=6,T_STUMP=7,T_SAPLING=8,T_HOUSE_DOOR=9,T_FLOWER=10,T_LAMP=11,
      T_BED=12,T_INTERIOR_FLOOR=13,T_WALL=14,T_TABLE=15,T_SHOP=16;

const CROP_TYPES = {
  wheat:  { name:'Gandum', emoji:'🌾', price:10, seedPrice:5,  growTime:400, color:'#e8c850' },
  corn:   { name:'Jagung', emoji:'🌽', price:25, seedPrice:15, growTime:600, color:'#ffcc33' },
  tomato: { name:'Tomat',  emoji:'🍅', price:40, seedPrice:25, growTime:800, color:'#ff4444' },
};

// ============================================
// ==== GAME STATE (declare early!) ====
// ============================================
const camera = { x:0, y:0 };
const player = {
  x: 20*TILE, y: 20*TILE, w: 10, h: 14, speed: 1.0,
  dir: 'down', animTimer: 0, walkFrame: 0,
  hp: 100, hpMax: 100, hunger: 100, hungerMax: 100,
  attackCooldown: 0,
};
const time = { totalMinutes: 6*60, day: 1, minutesPerSecond: 3 };
const inventory = { wheat:0, corn:0, tomato:0, wood:0, food:0, seeds:5, seeds_corn:0, seeds_tomato:0, arrows:10, pelt:0, fish:0 };
let gameGold = 20;
let currentSeed = 'wheat';
let currentTool = null;
let showInventory = false;

let world = [];
const crops = {};
const trees = {};
let animals = [];
let wolves = [];
let arrows = [];
let npcs = [];
let currentInterior = null;
let doorCooldown = 0;
let nearDoor = false;
let nearBed = false;
let nearShop = false;
let nearWater = false;

// ============================================
// ==== UTILS (fungsi dasar dulu!) ====
// ============================================
function isSolid(tx, ty, w) {
  const ww = w || world;
  if (!ww || !ww[ty]) return true;
  if (tx < 0 || ty < 0 || tx >= ww[0].length || ty >= ww.length) return true;
  const t = ww[ty][tx];
  return [T_WATER,T_TREE,T_HOUSE,T_LAMP,T_SAPLING,T_WALL,T_TABLE,T_BED].includes(t);
}
function canMoveTo(nx, ny, w, h, ww) {
  const wref = ww || world;
  if (!wref || !wref.length) return false;
  const corners = [
    {x: nx, y: ny}, {x: nx+w-1, y: ny},
    {x: nx, y: ny+h-1}, {x: nx+w-1, y: ny+h-1}
  ];
  return corners.every(c => !isSolid(Math.floor(c.x/TILE), Math.floor(c.y/TILE), wref));
}
function getTimeOfDay() {
  const h = Math.floor(time.totalMinutes/60) % 24;
  if (h >= 5 && h < 9) return 'dawn';
  if (h >= 9 && h < 17) return 'day';
  if (h >= 17 && h < 20) return 'evening';
  return 'night';
}
function getClockString() {
  const h = Math.floor(time.totalMinutes/60)%24, m = Math.floor(time.totalMinutes%60);
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
}
function getDarkness() {
  const h = (time.totalMinutes/60)%24;
  if (h >= 9 && h < 17) return 0;
  if (h >= 5 && h < 9) return 0.35*(1-(h-5)/4);
  if (h >= 17 && h < 20) return 0.35*((h-17)/3)+0.15;
  return 0.6;
}
const skyColors = {
  dawn:'rgba(255,180,100,0.15)', day:'rgba(255,255,255,0.0)',
  evening:'rgba(255,120,80,0.2)', night:'rgba(20,20,60,0.55)',
};
function getActiveWorld() { return currentInterior ? currentInterior.world : world; }

// ============================================
// ==== UI FUNCTIONS ====
// ============================================
let dialogTimer = 0;
function showToast(msg, color='#ffed4a') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.color = color; t.style.borderColor = color;
  t.style.boxShadow = `0 0 20px ${color}`;
  t.style.display = 'block';
  clearTimeout(t._timeout);
  t._timeout = setTimeout(() => t.style.display = 'none', 1200);
}
function showDialog(text) {
  const d = document.getElementById('dialog');
  if (!d) return;
  d.textContent = text; d.style.display = 'block'; dialogTimer = 220;
}
function flashDamage() {
  const f = document.getElementById('damageFlash');
  if (!f) return;
  f.style.opacity = '1';
  setTimeout(() => f.style.opacity = '0', 150);
}
function ensureAudio() {
  if (!audioCtx) initAudio();
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
}

// ============================================
// ==== WORLD GEN ====
// ============================================
function generateWorld() {
  world = [];
  for (let y=0; y<WORLD_H; y++) {
    let row = [];
    for (let x=0; x<WORLD_W; x++) {
      let t = T_GRASS;
      if (x >= WORLD_W-3) t = T_WATER;
      else if (Math.random() < 0.05) t = T_TREE;
      else if (Math.random() < 0.04) t = T_FLOWER;
      row.push(t);
    }
    world.push(row);
  }
  for (let y=8; y<18; y++)
    for (let x=4; x<WORLD_W-4; x++) world[y][x] = T_GRASS;
  for (let x=0; x<WORLD_W; x++) { world[13][x] = T_PATH; world[14][x] = T_PATH; }
  function drawHouse(x0, y0) {
    for (let y=y0; y<y0+4; y++)
      for (let x=x0; x<x0+5; x++)
        world[y][x] = T_HOUSE;
    world[y0+3][x0+2] = T_HOUSE_DOOR;
  }
  drawHouse(4, 9);
  drawHouse(17, 9);
  drawHouse(30, 9);
  world[15][22] = T_SHOP;
  for (let x=6; x<WORLD_W-6; x+=8)
    if (world[12] && world[12][x] === T_GRASS) world[12][x] = T_LAMP;
  for (let y=18; y<WORLD_H-2; y++)
    for (let x=15; x<25; x++)
      if ([T_TREE, T_WATER, T_LAMP].includes(world[y][x])) world[y][x] = T_GRASS;

  // Init trees
  for (let y=0; y<WORLD_H; y++)
    for (let x=0; x<WORLD_W; x++)
      if (world[y][x] === T_TREE) trees[`${x},${y}`] = { stage: 3, timer: 0 };
}
generateWorld();

function generateInterior() {
  const W = 20, H = 14;
  const w = [];
  for (let y=0; y<H; y++) {
    let row = [];
    for (let x=0; x<W; x++) {
      let t = T_INTERIOR_FLOOR;
      if (y === 0 || y === H-1 || x === 0 || x === W-1) t = T_WALL;
      row.push(t);
    }
    w.push(row);
  }
  w[0][10] = T_HOUSE_DOOR;
  w[3][4] = T_BED; w[3][5] = T_BED; w[4][4] = T_BED; w[4][5] = T_BED;
  w[5][14] = T_TABLE; w[5][15] = T_TABLE; w[6][14] = T_TABLE; w[6][15] = T_TABLE;
  return w;
}
const interiors = {
  0: { world: generateInterior(), playerSpawn: {x: 10*TILE, y: 9*TILE} },
  1: { world: generateInterior(), playerSpawn: {x: 10*TILE, y: 9*TILE} },
  2: { world: generateInterior(), playerSpawn: {x: 10*TILE, y: 9*TILE} },
};

// ============================================
// ==== ACHIEVEMENTS ====
// ============================================
const achievements = {
  first_harvest:  { emoji:'🌾', name:'Panen Pertama', desc:'Panen tanaman pertama', unlocked: false },
  farmer:         { emoji:'👨‍🌾', name:'Petani Handal', desc:'Panen 10 kali', unlocked: false },
  fisherman:      { emoji:'🎣', name:'Nelayan', desc:'Tangkap 5 ikan', unlocked: false },
  hunter:         { emoji:'🏹', name:'Pemburu', desc:'Bunuh 5 hewan', unlocked: false },
  wolf_slayer:    { emoji:'🐺', name:'Pembunuh Serigala', desc:'Bunuh 3 serigala', unlocked: false },
  rich:           { emoji:'💰', name:'Kaya Raya', desc:'Kumpulkan 500 gold', unlocked: false },
  woodcutter:     { emoji:'🪓', name:'Penebang', desc:'Tebang 10 pohon', unlocked: false },
  multi_crop:     { emoji:'🌽', name:'Petani Modern', desc:'Tanam 3 jenis tanaman', unlocked: false },
  survivor:       { emoji:'🔥', name:'Survivor', desc:'Bertahan 3 hari', unlocked: false },
  trader:         { emoji:'🏪', name:'Pedagang', desc:'Beli 5 item dari toko', unlocked: false },
  sleeper:        { emoji:'🛏️', name:'Tukang Tidur', desc:'Tidur 5 kali', unlocked: false },
  fisher_master:  { emoji:'🐟', name:'Master Mancing', desc:'Tangkap 20 ikan', unlocked: false },
};
const stats = {
  harvestCount: 0, fishCaught: 0, animalsKilled: 0, wolvesKilled: 0,
  treesChopped: 0, cropsPlanted: new Set(), shopPurchases: 0,
  sleepCount: 0, maxGold: 0,
};
function unlockAchievement(key) {
  if (!achievements[key] || achievements[key].unlocked) return;
  achievements[key].unlocked = true;
  const a = achievements[key];
  const nameEl = document.getElementById('achPopName');
  const descEl = document.getElementById('achPopDesc');
  const pop = document.getElementById('achPop');
  if (!nameEl || !pop) return;
  nameEl.textContent = `${a.emoji} ${a.name}`;
  descEl.textContent = a.desc;
  pop.style.display = 'block';
  sfxAchievement();
  clearTimeout(pop._timeout);
  pop._timeout = setTimeout(() => pop.style.display = 'none', 3500);
}
function checkAchievements() {
  if (!achievements.first_harvest.unlocked && stats.harvestCount >= 1) unlockAchievement('first_harvest');
  if (!achievements.farmer.unlocked && stats.harvestCount >= 10) unlockAchievement('farmer');
  if (!achievements.fisherman.unlocked && stats.fishCaught >= 5) unlockAchievement('fisherman');
  if (!achievements.fisher_master.unlocked && stats.fishCaught >= 20) unlockAchievement('fisher_master');
  if (!achievements.hunter.unlocked && stats.animalsKilled >= 5) unlockAchievement('hunter');
  if (!achievements.wolf_slayer.unlocked && stats.wolvesKilled >= 3) unlockAchievement('wolf_slayer');
  if (!achievements.rich.unlocked && stats.maxGold >= 500) unlockAchievement('rich');
  if (!achievements.woodcutter.unlocked && stats.treesChopped >= 10) unlockAchievement('woodcutter');
  if (!achievements.multi_crop.unlocked && stats.cropsPlanted.size >= 3) unlockAchievement('multi_crop');
  if (!achievements.survivor.unlocked && time.day >= 4) unlockAchievement('survivor');
  if (!achievements.trader.unlocked && stats.shopPurchases >= 5) unlockAchievement('trader');
  if (!achievements.sleeper.unlocked && stats.sleepCount >= 5) unlockAchievement('sleeper');
}

// ============================================
// ==== NPCs & ANIMALS (declare BEFORE use!) ====
// ============================================
const ANIMAL_TYPES = {
  rabbit: { color:'#f0e0d0', hp:20, speed:0.4, dropAmt:2 },
  chicken: { color:'#f5d76e', hp:15, speed:0.5, dropAmt:1 },
  cow: { color:'#e0d0b0', hp:40, speed:0.25, dropAmt:3 },
};

function initNPCs() {
  npcs = [
    { x: 8*TILE, y: 15*TILE, dir:'down', color:'#ff6b6b', name:'Budi',
      dialog:'Nempel pintu = auto masuk rumah!',
      targetX: 8, targetY: 15, moveTimer: 3, speed: 0.3, animTimer:0, walkFrame:0, isMoving:false, pausing:false, pauseTimer:0 },
    { x: 19*TILE, y: 15*TILE, dir:'left', color:'#4ecdc4', name:'Sari',
      dialog:'Malam hari ada serigala! Hati-hati.',
      targetX: 19, targetY: 15, moveTimer: 4, speed: 0.35, animTimer:0, walkFrame:0, isMoving:false, pausing:false, pauseTimer:0 },
    { x: 32*TILE, y: 15*TILE, dir:'right', color:'#ffe66d', name:'Pak Tani',
      dialog:'Ada toko di timur! Tekan E buat buka.',
      targetX: 32, targetY: 15, moveTimer: 5, speed: 0.25, animTimer:0, walkFrame:0, isMoving:false, pausing:false, pauseTimer:0 },
  ];
}
initNPCs();

function spawnAnimals() {
  animals = [];
  const types = ['rabbit', 'chicken', 'cow'];
  for (let i=0; i<8; i++) {
    const type = types[Math.floor(Math.random()*types.length)];
    let x, y, tries = 0;
    do { x = Math.floor(Math.random()*WORLD_W); y = Math.floor(Math.random()*WORLD_H); tries++; }
    while (tries < 50 && (world[y][x] !== T_GRASS || (Math.abs(x-20)<5 && Math.abs(y-20)<5)));
    const t = ANIMAL_TYPES[type];
    animals.push({
      x: x*TILE+3, y: y*TILE+3, type, hp: t.hp, hpMax: t.hp,
      vx:0, vy:0, speed: t.speed, dir:'down', wanderTimer:0, wanderAngle:0,
      hurtFlash:0, dead:false, animTimer:0, walkFrame:0, pauseTimer:0,
    });
  }
}
spawnAnimals();

function spawnSingleAnimal(type) {
  const t = ANIMAL_TYPES[type];
  let x, y, tries = 0;
  do { x = Math.floor(Math.random()*WORLD_W); y = Math.floor(Math.random()*WORLD_H); tries++; }
  while (tries < 50 && world[y][x] !== T_GRASS);
  animals.push({
    x: x*TILE+3, y: y*TILE+3, type, hp: t.hp, hpMax: t.hp,
    vx:0, vy:0, speed: t.speed, dir:'down', wanderTimer:0, wanderAngle:0,
    hurtFlash:0, dead:false, animTimer:0, walkFrame:0, pauseTimer:0,
  });
}

function spawnWolf() {
  let side = Math.floor(Math.random()*4), tx, ty;
  if (side === 0) { tx = Math.floor(Math.random()*WORLD_W); ty = 1; }
  else if (side === 1) { tx = WORLD_W-3; ty = Math.floor(Math.random()*WORLD_H); }
  else if (side === 2) { tx = Math.floor(Math.random()*WORLD_W); ty = WORLD_H-3; }
  else { tx = 1; ty = Math.floor(Math.random()*WORLD_H); }
  wolves.push({
    x: tx*TILE, y: ty*TILE, w:12, h:12, hp:30, hpMax:30, speed:0.9,
    attackTimer:0, dir:'down', hurtFlash:0, animTimer:0, walkFrame:0, wanderTimer:0, wanderAngle:0,
  });
  sfxWolfHowl();
}

function getAnimalAt(tx, ty) {
  for (const a of animals) if (!a.dead && Math.floor(a.x/TILE) === tx && Math.floor(a.y/TILE) === ty) return a;
  return null;
}
function getWolfAt(tx, ty) {
  for (const w of wolves) if (Math.floor(w.x/TILE) === tx && Math.floor(w.y/TILE) === ty) return w;
  return null;
}

// ============================================
// ==== FISHING ====
// ============================================
const fishing = { active: false, state: 'idle', timer: 0, biteWindow: 0, progress: 0, targetTime: 0 };

function startFishing(tx, ty) {
  if (fishing.active) return;
  if (!nearWater) { sfxError(); showToast('❌ Dekati air dulu!', '#ff4444'); return; }
  fishing.active = true;
  fishing.state = 'waiting';
  fishing.timer = 2 + Math.random() * 4;
  fishing.biteWindow = 0;
  fishing.progress = 0;
  sfxFishCast();
  showFishIndicator('🎣 Menunggu ikan...', 0, 'Sabarrr...');
}
function updateFishing(dt) {
  if (!fishing.active) return;
  if (fishing.state === 'waiting') {
    fishing.timer -= dt;
    if (fishing.timer <= 0) {
      fishing.state = 'bite';
      fishing.biteWindow = 1.2;
      sfxFishBite();
      showFishIndicator('🐟 IKAN! KLIK SEKARANG!', 100, 'CEPET KLIK!');
    }
  } else if (fishing.state === 'bite') {
    fishing.biteWindow -= dt;
    if (fishing.biteWindow <= 0) {
      fishing.active = false;
      sfxFishMiss();
      hideFishIndicator();
      showToast('😢 Ikan kabur!', '#ff6666');
    }
  } else if (fishing.state === 'minigame') {
    fishing.progress += dt * 0.5;
    fishing.targetTime -= dt;
    if (fishing.targetTime <= 0) {
      const diff = Math.abs(fishing.progress - 0.5);
      let success = diff < 0.15;
      if (success) {
        const fishAmt = 1 + Math.floor(Math.random() * 2);
        inventory.fish += fishAmt;
        stats.fishCaught += fishAmt;
        sfxFishCatch();
        hideFishIndicator();
        showToast(`🐟 Dapat ${fishAmt} ikan!`, '#5aff5a');
        updateHUD(); checkAchievements();
      } else {
        sfxFishMiss();
        hideFishIndicator();
        showToast('😢 Ikan lepas!', '#ff6666');
      }
      fishing.active = false;
    }
    const p = Math.min(1, fishing.progress);
    showFishIndicator('⚡ Timing!', p * 100,
      p < 0.35 ? 'Terlalu cepet...' : p < 0.65 ? '✅ PAS!' : 'Terlalu lambat...');
  }
}
function clickFish() {
  if (!fishing.active) return;
  if (fishing.state === 'bite') {
    fishing.state = 'minigame';
    fishing.progress = 0;
    fishing.targetTime = 2.0;
    showFishIndicator('⚡ Klik di waktu yang tepat!', 0, 'Tunggu...');
  } else if (fishing.state === 'minigame') {
    const diff = Math.abs(fishing.progress - 0.5);
    let success = diff < 0.15;
    if (success) {
      const fishAmt = 1 + Math.floor(Math.random() * 2);
      inventory.fish += fishAmt;
      stats.fishCaught += fishAmt;
      sfxFishCatch();
      hideFishIndicator();
      showToast(`🐟 Dapat ${fishAmt} ikan!`, '#5aff5a');
      updateHUD(); checkAchievements();
    } else {
      sfxFishMiss();
      hideFishIndicator();
      showToast('😢 Ikan lepas!', '#ff6666');
    }
    fishing.active = false;
  }
}
function showFishIndicator(status, progress, hint) {
  const st = document.getElementById('fishStatus');
  const bf = document.getElementById('fishBarFill');
  const hh = document.getElementById('fishHint');
  const fi = document.getElementById('fishIndicator');
  if (st) st.textContent = status;
  if (bf) bf.style.width = progress + '%';
  if (hh) hh.textContent = hint;
  if (fi) fi.style.display = 'block';
}
function hideFishIndicator() {
  const fi = document.getElementById('fishIndicator');
  if (fi) fi.style.display = 'none';
}

// ============================================
// ==== SHOP ====
// ============================================
let shopTab = 'buy';
const SHOP_BUY = [
  { key: 'seeds', name: 'Benih Gandum', emoji: '🌱', price: 5 },
  { key: 'seeds_corn', name: 'Benih Jagung', emoji: '🌱', price: 15 },
  { key: 'seeds_tomato', name: 'Benih Tomat', emoji: '🌱', price: 25 },
  { key: 'arrows', name: 'Panah x5', emoji: '🏹', price: 20, qty: 5 },
  { key: 'food', name: 'Roti', emoji: '🍞', price: 15 },
];
const SHOP_SELL = [
  { key: 'wheat', name: 'Gandum', emoji: '🌾', price: 10 },
  { key: 'corn', name: 'Jagung', emoji: '🌽', price: 25 },
  { key: 'tomato', name: 'Tomat', emoji: '🍅', price: 40 },
  { key: 'wood', name: 'Kayu', emoji: '🪵', price: 3 },
  { key: 'fish', name: 'Ikan', emoji: '🐟', price: 20 },
  { key: 'pelt', name: 'Kulit Wolf', emoji: '🟤', price: 15 },
];
function renderShop() {
  const content = document.getElementById('shopContent');
  if (!content) return;
  content.innerHTML = '';
  const items = shopTab === 'buy' ? SHOP_BUY : SHOP_SELL;
  items.forEach(item => {
    const row = document.createElement('div');
    row.className = 'shopItem';
    const qty = item.qty || 1;
    const canAfford = shopTab === 'buy' ? gameGold >= item.price : (inventory[item.key] || 0) >= qty;
    const stockInfo = shopTab === 'sell' ? `<div style="color:#888;font-size:11px">Punya: ${inventory[item.key] || 0}</div>` : '';
    row.innerHTML = `
      <div class="info">
        <div class="emoji">${item.emoji}</div>
        <div>
          <div class="name">${item.name}${item.qty ? ' x' + item.qty : ''}</div>
          <div class="price">${shopTab === 'buy' ? '🪙 ' + item.price : '🪙 +' + item.price}</div>
          ${stockInfo}
        </div>
      </div>
      <button ${canAfford ? '' : 'disabled'}>${shopTab === 'buy' ? 'Beli' : 'Jual'}</button>
    `;
    row.querySelector('button').onclick = () => {
      if (shopTab === 'buy') buyItem(item);
      else sellItem(item);
    };
    content.appendChild(row);
  });
}
function buyItem(item) {
  if (gameGold < item.price) { sfxError(); return; }
  gameGold -= item.price;
  const qty = item.qty || 1;
  inventory[item.key] = (inventory[item.key] || 0) + qty;
  stats.shopPurchases++;
  sfxBuy();
  showToast(`🛒 Beli ${item.name}!`, '#5aff5a');
  updateHUD(); renderShop(); checkAchievements();
}
function sellItem(item) {
  const qty = item.qty || 1;
  if ((inventory[item.key] || 0) < qty) { sfxError(); return; }
  inventory[item.key] -= qty;
  gameGold += item.price;
  if (gameGold > stats.maxGold) stats.maxGold = gameGold;
  sfxSell();
  showToast(`💰 Jual ${item.name} +${item.price} gold`, '#ffed4a');
  updateHUD(); renderShop(); checkAchievements();
}
function toggleShop() {
  const shop = document.getElementById('shop');
  if (!shop) return;
  if (shop.style.display === 'block') shop.style.display = 'none';
  else { ensureAudio(); shop.style.display = 'block'; renderShop(); sfxClick(); }
}
function renderAchPanel() {
  const grid = document.getElementById('achGrid');
  if (!grid) return;
  grid.innerHTML = '';
  Object.entries(achievements).forEach(([k, a]) => {
    const div = document.createElement('div');
    div.className = 'achItem' + (a.unlocked ? ' unlocked' : '');
    div.innerHTML = `
      <div class="emoji">${a.emoji}</div>
      <div>
        <div class="achName">${a.unlocked ? a.name : '???'}</div>
        <div class="achDesc">${a.desc}</div>
      </div>
    `;
    grid.appendChild(div);
  });
}
function toggleAch() {
  const p = document.getElementById('achPanel');
  if (!p) return;
  if (p.style.display === 'block') p.style.display = 'none';
  else { renderAchPanel(); p.style.display = 'block'; sfxClick(); }
}

// ============================================
// ==== SAVE / LOAD ====
// ============================================
function saveGame() {
  const data = {
    world, crops, trees, inventory, gameGold,
    player: { x: player.x, y: player.y, hp: player.hp, hunger: player.hunger },
    time: { totalMinutes: time.totalMinutes, day: time.day },
    animals: animals.filter(a => !a.dead),
    achievements: Object.fromEntries(Object.entries(achievements).map(([k,a]) => [k, a.unlocked])),
    stats: { ...stats, cropsPlanted: [...stats.cropsPlanted] },
  };
  try {
    localStorage.setItem('pixelFarmSave', JSON.stringify(data));
    showSaveIndicator();
    return true;
  } catch(e) { return false; }
}
function loadGame() {
  try {
    const raw = localStorage.getItem('pixelFarmSave');
    if (!raw) return false;
    const data = JSON.parse(raw);
    if (!data.world) return false;
    world = data.world;
    Object.keys(crops).forEach(k => delete crops[k]);
    Object.keys(data.crops || {}).forEach(k => crops[k] = data.crops[k]);
    Object.keys(trees).forEach(k => delete trees[k]);
    Object.keys(data.trees || {}).forEach(k => trees[k] = data.trees[k]);
    Object.keys(inventory).forEach(k => inventory[k] = (data.inventory && data.inventory[k] != null) ? data.inventory[k] : inventory[k]);
    gameGold = data.gameGold || 0;
    player.x = data.player.x; player.y = data.player.y;
    player.hp = data.player.hp; player.hunger = data.player.hunger;
    time.totalMinutes = data.time.totalMinutes; time.day = data.time.day;
    animals = (data.animals || []).map(a => ({
      ...a, vx:0, vy:0, hurtFlash:0, dead:false, animTimer:0, walkFrame:0, pauseTimer:0, wanderTimer:0, wanderAngle:0
    }));
    if (data.achievements) {
      Object.entries(data.achievements).forEach(([k, v]) => {
        if (achievements[k]) achievements[k].unlocked = v;
      });
    }
    if (data.stats) {
      Object.assign(stats, data.stats);
      stats.cropsPlanted = new Set(data.stats.cropsPlanted || []);
    }
    return true;
  } catch(e) { return false; }
}
function showSaveIndicator() {
  const el = document.getElementById('saveIndicator');
  if (!el) return;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 1500);
}

// ============================================
// ==== GAMEPLAY FUNCTIONS ====
// ============================================
function checkNearbyInteriorTiles() {
  nearDoor = false; nearBed = false; nearShop = false;
  const bodyPoints = [
    {x: player.x, y: player.y},
    {x: player.x + player.w - 1, y: player.y},
    {x: player.x, y: player.y + player.h - 1},
    {x: player.x + player.w - 1, y: player.y + player.h - 1},
    {x: player.x + player.w/2, y: player.y + player.h/2},
  ];
  if (currentInterior) {
    bodyPoints.forEach(p => {
      const tx = Math.floor(p.x / TILE), ty = Math.floor(p.y / TILE);
      if (tx>=0 && ty>=0 && tx<currentInterior.world[0].length && ty<currentInterior.world.length) {
        if (currentInterior.world[ty][tx] === T_BED) nearBed = true;
        if (currentInterior.world[ty][tx] === T_HOUSE_DOOR) nearDoor = true;
      }
    });
  } else {
    bodyPoints.forEach(p => {
      const tx = Math.floor(p.x / TILE), ty = Math.floor(p.y / TILE);
      if (tx>=0 && ty>=0 && tx<WORLD_W && ty<WORLD_H) {
        if (world[ty][tx] === T_HOUSE_DOOR) nearDoor = true;
        if (world[ty][tx] === T_SHOP) nearShop = true;
      }
    });
  }
}
function checkNearWater() {
  const ptx = Math.floor((player.x + player.w/2) / TILE);
  const pty = Math.floor((player.y + player.h/2) / TILE);
  nearWater = false;
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      const tx = ptx + dx, ty = pty + dy;
      if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
        if (world[ty] && world[ty][tx] === T_WATER) { nearWater = true; return; }
      }
    }
  }
}
function enterHouse(doorX, doorY) {
  let houseId = 0;
  if (doorX < 12) houseId = 0;
  else if (doorX < 25) houseId = 1;
  else houseId = 2;
  const interior = interiors[houseId];
  currentInterior = {
    id: houseId,
    world: JSON.parse(JSON.stringify(interior.world)),
    exitDoor: { x: 10, y: 0 },
  };
  player.x = interior.playerSpawn.x;
  player.y = interior.playerSpawn.y;
  player.dir = 'down';
  sfxDoor();
  showToast('🏠 Masuk rumah', '#4a90e2');
  startMusic('interior');
  doorCooldown = 1.5;
}
function exitInterior() {
  const houseId = currentInterior.id;
  let doorX, doorY;
  if (houseId === 0) { doorX = 6; doorY = 12; }
  else if (houseId === 1) { doorX = 19; doorY = 12; }
  else { doorX = 32; doorY = 12; }
  player.x = doorX * TILE + 3;
  player.y = (doorY + 2) * TILE;
  currentInterior = null;
  sfxDoor();
  showToast('🚪 Keluar rumah', '#4a90e2');
  startMusic(getTimeOfDay());
  doorCooldown = 1.5;
}
function sleep() {
  const h = Math.floor(time.totalMinutes/60)%24;
  let skipMinutes;
  if (h >= 6 && h < 18) skipMinutes = (24 - h + 6) * 60;
  else skipMinutes = ((6 - h + 24) % 24) * 60;
  time.totalMinutes += skipMinutes;
  while (time.totalMinutes >= 24*60) { time.totalMinutes -= 24*60; time.day++; }
  player.hp = player.hpMax;
  player.hunger = Math.max(50, player.hunger);
  player.x = 10*TILE; player.y = 9*TILE; player.dir = 'down';
  wolves = []; arrows = [];
  stats.sleepCount++;
  sfxSleep();
  showToast('😴 Tidur... Pagi!', '#5aff5a');
  startMusic('dawn');
  showBlackFade();
  checkAchievements();
}
function showBlackFade() {
  const f = document.getElementById('damageFlash');
  if (!f) return;
  f.style.background = 'black';
  f.style.opacity = '1';
  f.style.transition = 'opacity 1s';
  setTimeout(() => {
    f.style.opacity = '0';
    setTimeout(() => {
      f.style.background = 'radial-gradient(circle, transparent 30%, rgba(255,0,0,0.6) 100%)';
      f.style.transition = 'opacity 0.2s';
    }, 1000);
  }, 500);
}
function doInteractE() {
  if (currentInterior) {
    if (nearBed) { sleep(); return; }
    showToast('💡 Cari kasur buat tidur', '#ffed4a');
    return;
  }
  if (nearShop) { toggleShop(); return; }
  for (const npc of npcs) {
    const dx = npc.x - player.x, dy = npc.y - player.y;
    if (Math.hypot(dx, dy) < 40) {
      showDialog(`[${npc.name}] ${npc.dialog}`);
      sfxClick();
      return;
    }
  }
  showToast('💡 Tidak ada yang bisa diinteraksi', '#888');
}
function attackAnimal(a) {
  const dmg = 10 + Math.floor(Math.random()*8);
  a.hp -= dmg; a.hurtFlash = 10; a.wanderTimer = 0;
  const dx = a.x - player.x, dy = a.y - player.y;
  const d = Math.hypot(dx, dy) || 1;
  a.vx = dx/d*4; a.vy = dy/d*4;
  sfxAnimalHurt();
  if (a.hp <= 0) {
    a.dead = true;
    const amt = ANIMAL_TYPES[a.type].dropAmt;
    inventory.food += amt;
    stats.animalsKilled++;
    sfxHarvest(); showToast(`🐾 +${amt} food`, '#ffaa00');
    updateHUD(); checkAchievements();
    setTimeout(() => spawnSingleAnimal(a.type), 30000);
  } else showToast(`⚔️ -${dmg} HP`, '#ff6666');
}
function attackWolf(w) {
  const dmg = 12 + Math.floor(Math.random()*10);
  w.hp -= dmg; w.hurtFlash = 10;
  sfxHit();
  if (w.hp <= 0) {
    wolves = wolves.filter(wl => wl !== w);
    inventory.pelt += 1;
    stats.wolvesKilled++;
    sfxHarvest(); showToast('🐺 Wolf killed! +1 pelt', '#ff6666');
    updateHUD(); checkAchievements();
  } else showToast(`⚔️ Wolf -${dmg} HP`, '#ff6666');
}
function sellAll() {
  ensureAudio();
  const prices = { wheat:10, corn:25, tomato:40, wood:3, pelt:15, fish:20 };
  let total = 0;
  Object.entries(prices).forEach(([k, p]) => {
    total += (inventory[k] || 0) * p;
    inventory[k] = 0;
  });
  if (total === 0) { sfxError(); showToast('❌ Nggak ada yang dijual', '#ff4444'); return; }
  gameGold += total;
  if (gameGold > stats.maxGold) stats.maxGold = gameGold;
  sfxSell(); showToast(`🪙 +${total} gold!`, '#ffed4a');
  updateHUD(); checkAchievements();
}
function toggleMute() {
  muted = !muted;
  const ic = document.getElementById('muteIcon');
  if (ic) ic.textContent = muted ? '🔇' : '🔊';
  if (masterGain) masterGain.gain.value = muted ? 0 : masterVolume;
  sfxClick();
}
function applyTool(tx, ty) {
  if (currentInterior) return;
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;
  const t = world[ty][tx];
  const key = `${tx},${ty}`;
  if (currentTool === 'rod') { startFishing(tx, ty); return; }
  if (currentTool === 'bow') {
    if (inventory.arrows <= 0) { sfxError(); showToast('❌ Panah habis!', '#ff4444'); return; }
    if (player.attackCooldown > 0) return;
    inventory.arrows--;
    player.attackCooldown = 0.4;
    const dx = mouse.tx*TILE + TILE/2 - (player.x + player.w/2);
    const dy = mouse.ty*TILE + TILE/2 - (player.y + player.h/2);
    const d = Math.hypot(dx, dy) || 1;
    arrows.push({
      x: player.x + player.w/2, y: player.y + player.h/2,
      vx: dx/d*12, vy: dy/d*12, life: 60,
    });
    sfxBowShoot(); updateHUD(); return;
  }
  if (currentTool === 'sword') {
    if (player.attackCooldown > 0) return;
    player.attackCooldown = 0.3;
    sfxHit();
    const a = getAnimalAt(tx, ty);
    if (a) { attackAnimal(a); return; }
    const w = getWolfAt(tx, ty);
    if (w) { attackWolf(w); return; }
    return;
  }
  if (!currentTool) return;
  if (currentTool === 'hoe') {
    if (t === T_GRASS || t === T_FLOWER) {
      world[ty][tx] = T_FARMLAND; crops[key] = { stage: -1 };
      sfxHoe(); showToast('🪓 Dicangkul!', '#a07040');
    } else sfxError();
  } else if (currentTool === 'seed') {
    if (t === T_FARMLAND) {
      const seedKey = 'seeds' + (currentSeed === 'wheat' ? '' : '_' + currentSeed);
      if (inventory[seedKey] <= 0) {
        sfxError(); showToast(`❌ Benih ${CROP_TYPES[currentSeed].name} habis!`, '#ff4444');
        return;
      }
      inventory[seedKey]--;
      world[ty][tx] = T_CROP;
      crops[key] = {
        stage: 0, watered: false, timer: 0,
        type: currentSeed, growTime: CROP_TYPES[currentSeed].growTime
      };
      stats.cropsPlanted.add(currentSeed);
      sfxSeed(); showToast(`🌱 ${CROP_TYPES[currentSeed].name} ditanam!`, '#5aff5a');
      updateHUD(); checkAchievements();
    } else sfxError();
  } else if (currentTool === 'water') {
    if (t === T_CROP && crops[key] && crops[key].stage < 3 && !crops[key].watered) {
      crops[key].watered = true;
      sfxWater(); showToast('💧 Disiram!', '#4a90e2');
    } else sfxError();
  } else if (currentTool === 'harvest') {
    if (t === T_CROP && crops[key] && crops[key].stage >= 3) {
      const cropType = crops[key].type || 'wheat';
      inventory[cropType] = (inventory[cropType] || 0) + 1;
      stats.harvestCount++;
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHarvest();
      showToast(`${CROP_TYPES[cropType].emoji} Panen ${CROP_TYPES[cropType].name}! +1`, '#ffed4a');
      updateHUD(); checkAchievements();
    } else sfxError();
  } else if (currentTool === 'axe') {
    if (t === T_TREE) {
      world[ty][tx] = T_STUMP;
      trees[key] = { stage: -1, timer: 0 };
      inventory.wood += 3;
      stats.treesChopped++;
      sfxAxe(); showToast('🪓 Tebang! +3 kayu', '#a07040');
      updateHUD(); checkAchievements();
    } else sfxError();
  }
}
function toggleTool(tool) {
  if (currentTool === tool) {
    currentTool = null; showToast('🚫 Tool dilepas', '#888'); sfxClick();
    const sp = document.getElementById('seedPickerWrap');
    if (sp) sp.style.display = 'none';
  } else {
    currentTool = tool;
    const names = { hoe:'🪓 Hoe', seed:'🌱 Seed', water:'💧 Water', harvest:'🌾 Harvest', axe:'🪓 Axe', sword:'⚔️ Sword', bow:'🏹 Bow', rod:'🎣 Fishing Rod' };
    showToast(`${names[tool] || tool} dipilih`, '#ffed4a'); sfxClick();
    const sp = document.getElementById('seedPickerWrap');
    if (sp) sp.style.display = (tool === 'seed') ? 'block' : 'none';
  }
  updateToolbarUI();
}
function updateToolbarUI() {
  document.querySelectorAll('.tool').forEach(el => {
    el.classList.toggle('active', el.dataset.tool === currentTool);
  });
}
const ITEM_NAMES = {
  wheat: { emoji:'🌾', name:'Gandum' }, corn: { emoji:'🌽', name:'Jagung' },
  tomato: { emoji:'🍅', name:'Tomat' }, wood: { emoji:'🪵', name:'Kayu' },
  food: { emoji:'🍗', name:'Makanan' }, seeds: { emoji:'🌱', name:'Benih G' },
  seeds_corn: { emoji:'🌱', name:'Benih J' }, seeds_tomato: { emoji:'🌱', name:'Benih T' },
  arrows: { emoji:'🏹', name:'Panah' }, pelt: { emoji:'🟤', name:'Kulit' },
  fish: { emoji:'🐟', name:'Ikan' },
};
function renderInventory() {
  const grid = document.getElementById('invGrid');
  if (!grid) return;
  grid.innerHTML = '';
  const items = [];
  for (const [k, v] of Object.entries(inventory)) {
    if (ITEM_NAMES[k]) items.push({ key: k, count: v, ...ITEM_NAMES[k] });
  }
  for (let i=0; i<20; i++) {
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
  if (!inv) return;
  if (showInventory) { renderInventory(); inv.style.display = 'block'; sfxClick(); }
  else inv.style.display = 'none';
}
function useItem(key) {
  ensureAudio();
  if (key === 'food' && inventory.food > 0) {
    if (player.hunger >= player.hungerMax && player.hp >= player.hpMax) {
      showToast('❌ Udah kenyang!', '#ff4444'); sfxError(); return;
    }
    inventory.food--;
    player.hunger = Math.min(player.hungerMax, player.hunger + 30);
    player.hp = Math.min(player.hpMax, player.hp + 15);
    sfxEat(); showToast('🍗 +30 hunger +15 HP', '#5aff5a');
    updateHUD(); renderInventory();
  } else if (key === 'fish' && inventory.fish > 0) {
    inventory.fish--;
    player.hunger = Math.min(player.hungerMax, player.hunger + 20);
    player.hp = Math.min(player.hpMax, player.hp + 10);
    sfxEat(); showToast('🐟 +20 hunger +10 HP', '#5aff5a');
    updateHUD(); renderInventory();
  } else if (['wheat','corn','tomato','wood','pelt'].includes(key) && inventory[key] > 0) {
    const prices = { wheat:10, corn:25, tomato:40, wood:3, pelt:15 };
    const e = inventory[key] * prices[key];
    inventory[key] = 0; gameGold += e;
    if (gameGold > stats.maxGold) stats.maxGold = gameGold;
    sfxSell(); showToast(`💰 +${e} gold!`, '#ffed4a');
    updateHUD(); renderInventory(); checkAchievements();
  } else if (key === 'arrows') showToast('🏹 Pakai tool Bow', '#ffed4a');
  else if (key && key.startsWith('seeds')) showToast('🌱 Pakai tool Seed', '#ffed4a');
}

// ============================================
// ==== INPUT ====
// ============================================
const keys = {};
let mouse = { x:0, y:0, tx:0, ty:0, inside:false };
let isMouseDown = false, lastDragTile = null;

document.addEventListener('keydown', e => {
  const k = e.key.toLowerCase();
  keys[k] = true;
  if (k === '1') toggleTool('hoe');
  if (k === '2') toggleTool('seed');
  if (k === '3') toggleTool('water');
  if (k === '4') toggleTool('harvest');
  if (k === '5') toggleTool('axe');
  if (k === '6') toggleTool('sword');
  if (k === '7') toggleTool('bow');
  if (k === '8') toggleTool('rod');
  if (k === 'i') toggleInventory();
  if (k === 'm') toggleMute();
  if (k === 'j') sellAll();
  if (k === 'e') { ensureAudio(); doInteractE(); }
  if (k === 'escape') {
    const invEl = document.getElementById('inv');
    const shopEl = document.getElementById('shop');
    const achEl = document.getElementById('achPanel');
    if (invEl) invEl.style.display = 'none';
    if (shopEl) shopEl.style.display = 'none';
    if (achEl) achEl.style.display = 'none';
    showInventory = false;
  }
  if (['arrowup','arrowdown','arrowleft','arrowright',' '].includes(e.key)) e.preventDefault();
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = e.clientX - rect.left; mouse.y = e.clientY - rect.top;
  mouse.tx = Math.floor((mouse.x/PX + camera.x)/TILE);
  mouse.ty = Math.floor((mouse.y/PX + camera.y)/TILE);
  mouse.inside = true;
  if (isMouseDown && !showInventory) {
    const k = `${mouse.tx},${mouse.ty}`;
    if (k !== lastDragTile) { applyTool(mouse.tx, mouse.ty); lastDragTile = k; }
  }
});
canvas.addEventListener('mouseleave', () => { mouse.inside = false; isMouseDown = false; lastDragTile = null; });
canvas.addEventListener('mousedown', e => {
  if (e.button !== 0 || showInventory) return;
  ensureAudio();
  if (fishing.active) { clickFish(); return; }
  isMouseDown = true;
  applyTool(mouse.tx, mouse.ty);
  lastDragTile = `${mouse.tx},${mouse.ty}`;
});
canvas.addEventListener('mouseup', () => { isMouseDown = false; lastDragTile = null; });

document.querySelectorAll('.tool').forEach(el => {
  el.addEventListener('click', () => { ensureAudio(); toggleTool(el.dataset.tool); });
});
document.querySelectorAll('.seedOpt').forEach(el => {
  el.onclick = () => {
    currentSeed = el.dataset.seed;
    document.querySelectorAll('.seedOpt').forEach(e => e.classList.toggle('active', e === el));
    sfxClick();
  };
});
const firstSeed = document.querySelector('.seedOpt');
if (firstSeed) firstSeed.classList.add('active');

document.querySelectorAll('.shopTab').forEach(tab => {
  tab.onclick = () => {
    shopTab = tab.dataset.tab;
    document.querySelectorAll('.shopTab').forEach(t => t.classList.toggle('active', t === tab));
    renderShop(); sfxClick();
  };
});

const saveBtnEl = document.getElementById('saveBtn');
if (saveBtnEl) saveBtnEl.onclick = () => {
  if (saveGame()) { sfxSave(); showToast('💾 Tersimpan!', '#5aff5a'); }
  else showToast('❌ Gagal save', '#ff4444');
};
const achBtnEl = document.getElementById('achBtn');
if (achBtnEl) achBtnEl.onclick = toggleAch;
const muteEl = document.getElementById('muteIcon');
if (muteEl) muteEl.onclick = toggleMute;

setInterval(() => { if (audioCtx) saveGame(); }, 30000);
setTimeout(() => {
  if (loadGame()) { showToast('💾 Save dimuat!', '#5aff5a'); updateHUD(); }
}, 100);

// ============================================
// ==== UPDATE ====
// ============================================
let frameCount = 0, hungerCounter = 0, hpRegenCounter = 0;
let lastPhase = 'dawn', wolfSpawnTimer = 0, howlTimer = 0;

function update() {
  frameCount++;
  const dt = 1/60;
  if (doorCooldown > 0) doorCooldown -= dt;
  time.totalMinutes += time.minutesPerSecond * dt;
  if (time.totalMinutes >= 24*60) {
    time.totalMinutes -= 24*60; time.day++;
    showToast('🌅 Hari baru!', '#ffed4a');
    checkAchievements();
  }
  const phase = getTimeOfDay();
  if (phase !== lastPhase) {
    lastPhase = phase;
    startMusic(currentInterior ? 'interior' : phase);
    const names = { dawn:'🌅 Pagi', day:'☀️ Siang', evening:'🌇 Sore', night:'🌙 Malam' };
    const el = document.getElementById('timeOfDay');
    if (el) el.textContent = names[phase];
  }

  // Player move
  let dx = 0, dy = 0;
  if (keys['arrowleft'] || keys['a']) dx -= player.speed;
  if (keys['arrowright'] || keys['d']) dx += player.speed;
  if (keys['arrowup'] || keys['w']) dy -= player.speed;
  if (keys['arrowdown'] || keys['s']) dy += player.speed;
  const ww = getActiveWorld();
  if (dx !== 0 || dy !== 0) {
    if (dx !== 0 && canMoveTo(player.x+dx, player.y, player.w, player.h, ww)) player.x += dx;
    if (dy !== 0 && canMoveTo(player.x, player.y+dy, player.w, player.h, ww)) player.y += dy;
    if (Math.abs(dx) > Math.abs(dy)) player.dir = dx > 0 ? 'right' : 'left';
    else player.dir = dy > 0 ? 'down' : 'up';
    player.animTimer++;
    if (player.animTimer > 10) { player.animTimer = 0; player.walkFrame = (player.walkFrame + 1) % 4; }
  } else { player.walkFrame = 0; player.animTimer = 0; }
  if (player.attackCooldown > 0) player.attackCooldown -= dt;

  checkNearbyInteriorTiles();
  if (!currentInterior) checkNearWater();

  if (doorCooldown <= 0) {
    if (nearDoor && !currentInterior) {
      const bodyPoints = [
        {x: player.x, y: player.y},
        {x: player.x + player.w - 1, y: player.y},
        {x: player.x, y: player.y + player.h - 1},
        {x: player.x + player.w - 1, y: player.y + player.h - 1},
      ];
      let foundDoor = null;
      for (const p of bodyPoints) {
        const tx = Math.floor(p.x / TILE), ty = Math.floor(p.y / TILE);
        if (tx>=0 && ty>=0 && tx<WORLD_W && ty<WORLD_H && world[ty][tx] === T_HOUSE_DOOR) {
          foundDoor = {x: tx, y: ty}; break;
        }
      }
      if (foundDoor) enterHouse(foundDoor.x, foundDoor.y);
    } else if (nearDoor && currentInterior) {
      exitInterior();
    }
  }

  updateFishing(dt);

  // Crops
  Object.keys(crops).forEach(k => {
    const c = crops[k];
    if (c.stage >= 0 && c.stage < 3) {
      const growTime = c.growTime || 400;
      c.timer = (c.timer || 0) + (c.watered ? 1.5 : 0.4);
      if (c.timer > growTime / 4) { c.stage++; c.timer = 0; c.watered = false; }
    }
  });
  // Trees
  Object.keys(trees).forEach(k => {
    const t = trees[k];
    if (t.stage >= -1 && t.stage < 3) {
      t.timer = (t.timer || 0) + 1;
      if (t.timer > 900) {
        t.stage++; t.timer = 0;
        const [tx, ty] = k.split(',').map(Number);
        if (world[ty] && world[ty][tx] !== undefined) {
          if (t.stage >= 3) world[ty][tx] = T_TREE;
          else if (t.stage >= 0) world[ty][tx] = T_SAPLING;
        }
      }
    }
  });

  // NPC wander
  if (!currentInterior) {
    npcs.forEach(npc => {
      npc.moveTimer -= dt;
      const ttx = npc.targetX*TILE, tty = npc.targetY*TILE;
      const ddx = ttx - npc.x, ddy = tty - npc.y;
      const dist = Math.hypot(ddx, ddy);
      if (dist < 4 || npc.moveTimer <= 0) {
        if (npc.moveTimer <= 0 && !npc.pausing) { npc.pausing = true; npc.pauseTimer = 1.5 + Math.random()*2.5; }
        if (npc.pausing) {
          npc.pauseTimer -= dt; npc.isMoving = false;
          if (npc.pauseTimer <= 0) {
            npc.pausing = false;
            npc.moveTimer = 3 + Math.random()*4;
            npc.targetX = 5 + Math.floor(Math.random()*(WORLD_W-10));
            npc.targetY = 15 + Math.floor(Math.random()*2);
            npc.targetX = Math.max(5, Math.min(WORLD_W-5, npc.targetX));
            npc.targetY = Math.max(15, Math.min(17, npc.targetY));
          }
        }
      } else {
        npc.isMoving = true;
        const nx = npc.x + ddx/dist*npc.speed, ny = npc.y + ddy/dist*npc.speed;
        if (canMoveTo(nx, ny, 10, 14, world)) { npc.x = nx; npc.y = ny; }
        else { npc.moveTimer = 0; npc.pausing = false; }
        if (Math.abs(ddx) > Math.abs(ddy)) npc.dir = ddx > 0 ? 'right' : 'left';
        else npc.dir = ddy > 0 ? 'down' : 'up';
        npc.animTimer++;
        if (npc.animTimer > 12) { npc.animTimer = 0; npc.walkFrame = (npc.walkFrame + 1) % 4; }
      }
      if (!npc.isMoving) { npc.walkFrame = 0; npc.animTimer = 0; }
    });
  }

  // Animals
  if (!currentInterior) {
    animals.forEach(a => {
      if (a.dead) return;
      a.x += a.vx; a.y += a.vy;
      a.vx *= 0.85; a.vy *= 0.85;
      if (a.pauseTimer > 0) { a.pauseTimer -= dt; a.walkFrame = 0; return; }
      a.wanderTimer -= 1;
      if (a.wanderTimer <= 0) {
        a.wanderTimer = 120 + Math.random()*240;
        a.wanderAngle = Math.random()*Math.PI*2;
        a.pauseTimer = 0.5 + Math.random()*1.5;
      }
      if (a.wanderAngle !== undefined && a.pauseTimer <= 0) {
        const spd = a.speed * (a.hurtFlash > 0 ? 2 : 1);
        const nx = a.x + Math.cos(a.wanderAngle)*spd;
        const ny = a.y + Math.sin(a.wanderAngle)*spd;
        const tx = Math.floor(nx/TILE), ty = Math.floor(ny/TILE);
        if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
          const t = world[ty][tx];
          if (t === T_GRASS || t === T_FLOWER || t === T_PATH) {
            a.x = nx; a.y = ny;
            if (Math.abs(Math.cos(a.wanderAngle)) > Math.abs(Math.sin(a.wanderAngle))) a.dir = Math.cos(a.wanderAngle) > 0 ? 'right' : 'left';
            else a.dir = Math.sin(a.wanderAngle) > 0 ? 'down' : 'up';
            a.animTimer++;
            if (a.animTimer > 15) { a.animTimer = 0; a.walkFrame = (a.walkFrame + 1) % 4; }
          } else a.wanderTimer = 0;
        }
      }
      a.x = Math.max(TILE, Math.min(WORLD_W*TILE-TILE, a.x));
      a.y = Math.max(TILE, Math.min(WORLD_H*TILE-TILE, a.y));
      if (a.hurtFlash > 0) a.hurtFlash--;
    });
  }

  // Wolf spawn
  if (phase === 'night' && !currentInterior) {
    wolfSpawnTimer += dt;
    if (wolfSpawnTimer > 8 && wolves.length < 5) { wolfSpawnTimer = 0; spawnWolf(); }
    howlTimer += dt;
    if (howlTimer > 15 && wolves.length > 0) { howlTimer = 0; sfxWolfHowl(); }
  } else { wolfSpawnTimer = 0; howlTimer = 0; }

  // Wolves
  if (!currentInterior) {
    wolves.forEach(w => {
      const dxp = player.x - w.x, dyp = player.y - w.y;
      const distP = Math.hypot(dxp, dyp);
      if (distP < 200 && distP > 0.1) {
        const spd = w.speed;
        const nx = w.x + dxp/distP*spd, ny = w.y + dyp/distP*spd;
        if (canMoveTo(nx, ny, w.w, w.h, world)) { w.x = nx; w.y = ny; }
        if (Math.abs(dxp) > Math.abs(dyp)) w.dir = dxp > 0 ? 'right' : 'left';
        else w.dir = dyp > 0 ? 'down' : 'up';
        if (distP < 20) {
          w.attackTimer -= dt;
          if (w.attackTimer <= 0) {
            w.attackTimer = 1.2;
            player.hp = Math.max(0, player.hp - 8);
            flashDamage(); sfxWolfBite();
            showToast('🐺 Wolf attack! -8 HP', '#ff6666');
          }
        }
      } else {
        w.wanderTimer = (w.wanderTimer || 0) - 1;
        if (w.wanderTimer <= 0) { w.wanderTimer = 120; w.wanderAngle = Math.random()*Math.PI*2; }
        const spd = w.speed * 0.5;
        const nx = w.x + Math.cos(w.wanderAngle)*spd;
        const ny = w.y + Math.sin(w.wanderAngle)*spd;
        const tx = Math.floor(nx/TILE), ty = Math.floor(ny/TILE);
        if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
          const t = world[ty][tx];
          if (t === T_GRASS || t === T_PATH || t === T_FLOWER) { w.x = nx; w.y = ny; }
          else w.wanderTimer = 0;
        }
      }
      w.animTimer = (w.animTimer || 0) + 1;
      if (w.animTimer > 8) { w.animTimer = 0; w.walkFrame = (w.walkFrame + 1) % 4; }
      if (w.hurtFlash > 0) w.hurtFlash--;
    });

    // Arrows
    arrows.forEach(arr => {
      arr.x += arr.vx; arr.y += arr.vy; arr.life--;
      for (const a of animals) {
        if (a.dead) continue;
        if (Math.hypot(arr.x - (a.x+5), arr.y - (a.y+3)) < 10) {
          a.hp -= 15; a.hurtFlash = 10; sfxArrowHit();
          if (a.hp <= 0) {
            a.dead = true;
            const amt = ANIMAL_TYPES[a.type].dropAmt;
            inventory.food += amt;
            stats.animalsKilled++;
            sfxHarvest(); showToast(`🏹 +${amt} food`, '#ffaa00');
            updateHUD(); checkAchievements();
            setTimeout(() => spawnSingleAnimal(a.type), 30000);
          }
          arr.life = 0; break;
        }
      }
      for (const w of wolves) {
        if (Math.hypot(arr.x - (w.x+6), arr.y - (w.y+6)) < 10) {
          w.hp -= 15; w.hurtFlash = 10; sfxArrowHit();
          if (w.hp <= 0) {
            wolves = wolves.filter(wl => wl !== w);
            inventory.pelt += 1;
            stats.wolvesKilled++;
            sfxHarvest(); showToast('🏹 Wolf killed! +1 pelt', '#ff6666');
            updateHUD(); checkAchievements();
          }
          arr.life = 0; break;
        }
      }
    });
    arrows = arrows.filter(a => a.life > 0 && a.x > 0 && a.x < WORLD_W*TILE && a.y > 0 && a.y < WORLD_H*TILE);
  }

  // Hunger & HP
  hungerCounter += dt;
  if (hungerCounter > 6) { hungerCounter = 0; player.hunger = Math.max(0, player.hunger - 1); }
  if (player.hunger > 60) {
    hpRegenCounter += dt;
    if (hpRegenCounter > 5) { hpRegenCounter = 0; player.hp = Math.min(player.hpMax, player.hp + 1); }
  }
  if (player.hunger <= 0 && frameCount % 90 === 0) {
    player.hp = Math.max(0, player.hp - 2); flashDamage(); sfxHurt();
  }
  if (phase === 'night' && !currentInterior && frameCount % 300 === 0) {
    const inVillage = player.y/TILE < 18 && player.y/TILE > 8;
    if (!inVillage) { player.hp = Math.max(0, player.hp - 2); flashDamage(); sfxHurt(); }
  }
  if (player.hp <= 0) {
    player.hp = player.hpMax/2; player.hunger = player.hungerMax/2;
    if (currentInterior) currentInterior = null;
    player.x = 20*TILE; player.y = 20*TILE;
    showToast('💀 Kamu pingsan!', '#ff4444'); sfxError();
  }

  // Camera
  const tX = player.x - canvas.width/(2*PX) + player.w/2;
  const tY = player.y - canvas.height/(2*PX) + player.h/2;
  camera.x += (tX - camera.x) * 0.15;
  camera.y += (tY - camera.y) * 0.15;
  const actW = getActiveWorld();
  camera.x = Math.max(0, Math.min(actW[0].length*TILE - canvas.width/PX, camera.x));
  camera.y = Math.max(0, Math.min(actW.length*TILE - canvas.height/PX, camera.y));

  if (mouse.inside) {
    mouse.tx = Math.floor((mouse.x/PX + camera.x)/TILE);
    mouse.ty = Math.floor((mouse.y/PX + camera.y)/TILE);
  }
  if (dialogTimer > 0) {
    dialogTimer--;
    if (dialogTimer === 0) {
      const d = document.getElementById('dialog');
      if (d) d.style.display = 'none';
    }
  }
  const bp = document.getElementById('bedPrompt');
  if (bp) bp.style.display = nearBed ? 'block' : 'none';

  const clk = document.getElementById('clock');
  if (clk) clk.textContent = getClockString();
  const dn = document.getElementById('dayNum');
  if (dn) dn.textContent = time.day;
  updateHUDBars();
}

function updateHUDBars() {
  const hpF = document.getElementById('hpFill');
  const hpT = document.getElementById('hpText');
  const hgF = document.getElementById('hungerFill');
  const hgT = document.getElementById('hungerText');
  if (hpF) hpF.style.width = (player.hp/player.hpMax*100)+'%';
  if (hpT) hpT.textContent = `${Math.round(player.hp)}/${player.hpMax}`;
  if (hgF) hgF.style.width = (player.hunger/player.hungerMax*100)+'%';
  if (hgT) hgT.textContent = `${Math.round(player.hunger)}/${player.hungerMax}`;
}
function updateHUD() {
  const g = document.getElementById('gold');
  const w = document.getElementById('wood');
  const f = document.getElementById('food');
  const wh = document.getElementById('wheat');
  const ar = document.getElementById('arrows');
  if (g) g.textContent = gameGold;
  if (w) w.textContent = inventory.wood;
  if (f) f.textContent = inventory.food;
  if (wh) wh.textContent = inventory.wheat;
  if (ar) ar.textContent = inventory.arrows;
  if (gameGold > stats.maxGold) stats.maxGold = gameGold;
  checkAchievements();
}

// ============================================
// ==== DRAW ====
// ============================================
function artPx(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(Math.floor((x-camera.x)*PX), Math.floor((y-camera.y)*PX), w*PX, h*PX);
}
function drawTile(t, x, y) {
  const wx = x*TILE, wy = y*TILE;
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
    if ((x*7+y*11) % 17 === 0 && Math.sin(frameCount*0.05 + x) > 0.7) artPx(wx+7, wy+6, 3, 2, '#ddd');
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
  } else if (t === T_SAPLING) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+7, wy+8, 2, 8, '#5a3a1a');
    artPx(wx+4, wy+5, 4, 4, '#2d7d3a');
    artPx(wx+8, wy+6, 4, 4, '#2d7d3a');
  } else if (t === T_FARMLAND) {
    artPx(wx, wy, TILE, TILE, '#6b4423');
    for (let i=3; i<16; i+=4) artPx(wx, wy+i, TILE, 1, '#4a2f18');
  } else if (t === T_CROP) {
    artPx(wx, wy, TILE, TILE, '#6b4423');
    for (let i=3; i<16; i+=4) artPx(wx, wy+i, TILE, 1, '#4a2f18');
    const c = crops[`${x},${y}`];
    const stage = c ? c.stage : 0;
    const cropType = c ? (c.type || 'wheat') : 'wheat';
    const cx = wx+6, cy = wy+6;
    const ct = CROP_TYPES[cropType] || CROP_TYPES.wheat;
    if (stage === 0) { artPx(cx+1, cy+6, 2, 3, '#5aff5a'); artPx(cx, cy+5, 1, 2, '#3a9d3a'); }
    else if (stage === 1) { artPx(cx+1, cy+3, 2, 6, '#5aff5a'); artPx(cx, cy+2, 1, 4, '#3a9d3a'); artPx(cx+3, cy+2, 1, 4, '#3a9d3a'); }
    else if (stage === 2) { artPx(cx+1, cy+0, 2, 9, '#7fd77f'); artPx(cx, cy-1, 1, 7, '#5aa55a'); artPx(cx+3, cy-1, 1, 7, '#5aa55a'); artPx(cx+1, cy-1, 2, 2, '#d4d44a'); }
    else if (stage >= 3) {
      const glow = Math.sin(frameCount*0.1)*0.3 + 0.7;
      ctx.shadowColor = ct.color; ctx.shadowBlur = 12*glow;
      artPx(cx+1, cy-2, 2, 11, ct.color);
      artPx(cx, cy-3, 1, 9, ct.color);
      artPx(cx+3, cy-3, 1, 9, ct.color);
      artPx(cx, cy-4, 4, 3, ct.color);
      if (cropType === 'wheat') artPx(cx, cy-4, 4, 3, '#ffed4a');
      else if (cropType === 'corn') { artPx(cx+1, cy-3, 2, 4, '#ffcc33'); artPx(cx, cy-1, 4, 2, '#5a8a2a'); }
      else if (cropType === 'tomato') { artPx(cx, cy-3, 4, 4, '#ff3333'); artPx(cx+1, cy-4, 2, 2, '#5a8a2a'); }
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
    const isNight = getTimeOfDay() === 'night' || getTimeOfDay() === 'evening';
    artPx(wx, wy, TILE, TILE, '#5a3a1a');
    artPx(wx, wy+4, TILE, TILE-4, '#c89b6a');
    artPx(wx+1, wy+1, TILE-2, 1, '#7a5030');
    if (isNight) { ctx.shadowColor = '#ffed4a'; ctx.shadowBlur = 12; artPx(wx+5, wy+8, 6, 5, '#ffed4a'); ctx.shadowBlur = 0; }
    else artPx(wx+5, wy+8, 6, 5, '#4a90e2');
  } else if (t === T_HOUSE_DOOR) {
    if (nearDoor && !currentInterior) {
      const glow = Math.sin(frameCount*0.15)*0.4 + 0.6;
      ctx.shadowColor = '#4a90e2'; ctx.shadowBlur = 25*glow;
    }
    artPx(wx, wy, TILE, TILE, '#5a3a1a');
    artPx(wx, wy+4, TILE, TILE-4, '#c89b6a');
    artPx(wx+3, wy+7, 10, 9, '#5a3a1a');
    artPx(wx+11, wy+12, 1, 1, '#ffd700');
    ctx.shadowBlur = 0;
  } else if (t === T_SHOP) {
    const glow = Math.sin(frameCount*0.08) * 0.2 + 0.8;
    ctx.shadowColor = '#ffd700'; ctx.shadowBlur = 20 * glow;
    artPx(wx, wy, TILE, TILE, '#ffd700');
    artPx(wx, wy, TILE, 4, '#ff8800');
    artPx(wx+2, wy+6, 12, 8, '#8b4513');
    artPx(wx+3, wy+7, 4, 4, '#ffd700');
    artPx(wx+9, wy+7, 4, 4, '#ffd700');
    artPx(wx+7, wy+5, 2, 10, '#fff');
    ctx.shadowBlur = 0;
  } else if (t === T_LAMP) {
    artPx(wx, wy, TILE, TILE, '#3a7d44');
    artPx(wx+6, wy+4, 4, 12, '#555');
    const isNight = getTimeOfDay() === 'night' || getTimeOfDay() === 'evening';
    if (isNight) { ctx.shadowColor = '#ffed4a'; ctx.shadowBlur = 20; artPx(wx+4, wy+1, 8, 6, '#ffed4a'); ctx.shadowBlur = 0; }
    else artPx(wx+4, wy+1, 8, 6, '#666');
  } else if (t === T_INTERIOR_FLOOR) {
    artPx(wx, wy, TILE, TILE, '#8b6f47');
    artPx(wx, wy+7, TILE, 1, '#7a5f38');
    artPx(wx+7, wy, 1, TILE, '#7a5f38');
  } else if (t === T_WALL) {
    artPx(wx, wy, TILE, TILE, '#5a3a1a');
    artPx(wx+1, wy+1, TILE-2, 2, '#7a5030');
    artPx(wx+1, wy+8, TILE-2, 2, '#7a5030');
  } else if (t === T_BED) {
    artPx(wx, wy, TILE, TILE, '#8b6f47');
    artPx(wx, wy, TILE, 6, '#ff4444');
    artPx(wx+2, wy+2, TILE-4, 3, '#ffffff');
    artPx(wx, wy+8, TILE, TILE-8, '#4a90e2');
    if (nearBed) {
      const glow = Math.sin(frameCount*0.15)*0.4 + 0.6;
      ctx.strokeStyle = '#ffed4a'; ctx.lineWidth = 2; ctx.globalAlpha = glow;
      ctx.strokeRect(Math.floor((wx-camera.x)*PX)+1, Math.floor((wy-camera.y)*PX)+1, TILE*PX-2, TILE*PX-2);
      ctx.globalAlpha = 1;
    }
  } else if (t === T_TABLE) {
    artPx(wx, wy, TILE, TILE, '#8b6f47');
    artPx(wx+1, wy+1, TILE-2, TILE-2, '#a07a50');
  }
}
function drawHumanoid(x, y, dir, walkFrame, color, skin='#ffcc99', shirtColor=null) {
  const skinTone = skin, shirt = shirtColor || color, pants = '#1a3a8a', hair = '#3a2010';
  const bob = (walkFrame === 1 || walkFrame === 3) ? -1 : 0;
  ctx.globalAlpha = 0.3; artPx(x+2, y+15, 8, 2, '#000'); ctx.globalAlpha = 1;
  artPx(x+3, y+0+bob, 6, 6, skinTone);
  if (dir === 'down') {
    artPx(x+3, y+0+bob, 6, 2, hair);
    artPx(x+4, y+3+bob, 1, 1, '#000'); artPx(x+7, y+3+bob, 1, 1, '#000');
  } else if (dir === 'up') artPx(x+3, y+0+bob, 6, 4, hair);
  else if (dir === 'left') { artPx(x+3, y+0+bob, 6, 2, hair); artPx(x+5, y+0+bob, 4, 4, hair); artPx(x+4, y+3+bob, 1, 1, '#000'); }
  else { artPx(x+3, y+0+bob, 6, 2, hair); artPx(x+3, y+0+bob, 4, 4, hair); artPx(x+7, y+3+bob, 1, 1, '#000'); }
  artPx(x+3, y+6+bob, 6, 5, shirt);
  artPx(x+2, y+7+bob, 1, 3, skinTone);
  artPx(x+9, y+7+bob, 1, 3, skinTone);
  const legY = y + 11 + bob;
  if (walkFrame === 1) { artPx(x+3, legY, 2, 5, pants); artPx(x+7, legY+1, 2, 4, pants); }
  else if (walkFrame === 3) { artPx(x+3, legY+1, 2, 4, pants); artPx(x+7, legY, 2, 5, pants); }
  else { artPx(x+3, legY, 2, 5, pants); artPx(x+7, legY, 2, 5, pants); }
  artPx(x+3, legY+4, 2, 1, '#000'); artPx(x+7, legY+4, 2, 1, '#000');
}
function drawAnimal(a) {
  if (a.dead) return;
  const x = a.x, y = a.y;
  const t = ANIMAL_TYPES[a.type];
  let color = t.color;
  if (a.hurtFlash > 0 && a.hurtFlash % 4 < 2) color = '#ff4444';
  ctx.globalAlpha = 0.3; artPx(x-2, y+10, 10, 2, '#000'); ctx.globalAlpha = 1;
  const bob = (a.walkFrame === 1 || a.walkFrame === 3) ? -1 : 0;
  artPx(x-2, y-4+bob, 10, 10, color);
  if (a.type === 'rabbit') {
    artPx(x-1, y-8+bob, 2, 5, color); artPx(x+3, y-8+bob, 2, 5, color);
    artPx(x-2, y-5+bob, 10, 4, color);
    artPx(x+0, y-3+bob, 1, 1, '#000'); artPx(x+4, y-3+bob, 1, 1, '#000');
  } else if (a.type === 'chicken') {
    artPx(x+1, y-8+bob, 4, 5, color);
    artPx(x+2, y-10+bob, 2, 3, '#ff4444');
    artPx(x+5, y-6+bob, 3, 2, '#ff8800');
    artPx(x+2, y-6+bob, 1, 1, '#000');
  } else if (a.type === 'cow') {
    artPx(x-3, y-8+bob, 12, 8, color);
    artPx(x-4, y-7+bob, 2, 2, '#333'); artPx(x+8, y-7+bob, 2, 2, '#333');
    artPx(x-1, y-5+bob, 2, 2, '#000'); artPx(x+5, y-5+bob, 2, 2, '#000');
    artPx(x+1, y-2+bob, 4, 2, '#ffaaaa');
  }
  if (a.hp < a.hpMax) {
    const w = 20;
    const hx = Math.floor((x-camera.x)*PX)-4;
    const hy = Math.floor((y-camera.y)*PX)-20;
    ctx.fillStyle = '#000'; ctx.fillRect(hx-1, hy-1, w+2, 5);
    ctx.fillStyle = '#ff4444'; ctx.fillRect(hx, hy, w*(a.hp/a.hpMax), 3);
  }
}
function drawWolf(w) {
  const x = w.x, y = w.y;
  let color = '#666';
  if (w.hurtFlash > 0 && w.hurtFlash % 4 < 2) color = '#ff4444';
  ctx.globalAlpha = 0.3; artPx(x-2, y+12, 14, 2, '#000'); ctx.globalAlpha = 1;
  const bob = (w.walkFrame === 1 || w.walkFrame === 3) ? -1 : 0;
  artPx(x-2, y-4+bob, 14, 10, color);
  artPx(x-4, y-8+bob, 8, 8, color);
  artPx(x-4, y-11+bob, 2, 3, color); artPx(x+0, y-11+bob, 2, 3, color);
  artPx(x-7, y-4+bob, 4, 3, '#444');
  ctx.shadowColor = '#ff0'; ctx.shadowBlur = 8;
  artPx(x-3, y-6+bob, 2, 2, '#ff0'); artPx(x+1, y-6+bob, 2, 2, '#ff0');
  ctx.shadowBlur = 0;
  artPx(x+12, y-2+bob, 4, 2, color);
  if (w.hp < w.hpMax) {
    const ww = 22;
    const hx = Math.floor((x-camera.x)*PX)-6;
    const hy = Math.floor((y-camera.y)*PX)-24;
    ctx.fillStyle = '#000'; ctx.fillRect(hx-1, hy-1, ww+2, 5);
    ctx.fillStyle = '#ff3333'; ctx.fillRect(hx, hy, ww*(w.hp/w.hpMax), 3);
  }
}
function drawArrow(a) {
  ctx.fillStyle = '#8b5a2b';
  ctx.fillRect(Math.floor((a.x-camera.x)*PX)-3, Math.floor((a.y-camera.y)*PX)-1, 6, 2);
  ctx.fillStyle = '#ddd';
  ctx.fillRect(Math.floor((a.x-camera.x)*PX)+3, Math.floor((a.y-camera.y)*PX)-1, 3, 2);
}
function drawNpc(npc) {
  drawHumanoid(npc.x, npc.y, npc.dir, npc.walkFrame, npc.color, '#e8b088', npc.color);
  const dx = npc.x - player.x, dy = npc.y - player.y;
  if (Math.hypot(dx, dy) < 60) {
    const sx = Math.floor((npc.x-camera.x)*PX)+15;
    const sy = Math.floor((npc.y-camera.y)*PX)-10;
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.font = 'bold 11px monospace'; ctx.textAlign = 'center';
    const w = ctx.measureText(npc.name).width + 8;
    ctx.fillRect(sx - w/2, sy - 10, w, 14);
    ctx.fillStyle = '#ffed4a'; ctx.fillText(npc.name, sx, sy);
  }
}
function drawCursorHighlight() {
  if (!mouse.inside || currentInterior) return;
  const tx = mouse.tx, ty = mouse.ty;
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;
  const px = Math.floor((tx*TILE-camera.x)*PX);
  const py = Math.floor((ty*TILE-camera.y)*PX);
  let color = '#444', alpha = 0.3;
  if (currentTool) {
    const t = world[ty][tx];
    const key = `${tx},${ty}`;
    if (currentTool === 'hoe' && (t === T_GRASS || t === T_FLOWER)) { color = '#a07040'; alpha = 0.7; }
    else if (currentTool === 'seed' && t === T_FARMLAND) { color = '#5aff5a'; alpha = 0.7; }
    else if (currentTool === 'water' && t === T_CROP && crops[key] && !crops[key].watered && crops[key].stage < 3) { color = '#4a90e2'; alpha = 0.7; }
    else if (currentTool === 'harvest' && t === T_CROP && crops[key] && crops[key].stage >= 3) { color = '#ffed4a'; alpha = 0.9; }
    else if (currentTool === 'axe' && t === T_TREE) { color = '#ff8800'; alpha = 0.8; }
    else if (currentTool === 'sword') {
      const a = getAnimalAt(tx, ty); const w = getWolfAt(tx, ty);
      if (a || w) { color = '#ff3333'; alpha = 0.9; } else { color = '#88f'; alpha = 0.5; }
    }
    else if (currentTool === 'bow') { color = '#8b5a2b'; alpha = 0.7; }
    else if (currentTool === 'rod') { color = '#4a90e2'; alpha = 0.7; }
  }
  ctx.strokeStyle = color;
  ctx.lineWidth = currentTool ? 3 : 2;
  ctx.globalAlpha = alpha;
  ctx.strokeRect(px+1, py+1, TILE*PX-2, TILE*PX-2);
  ctx.globalAlpha = alpha * 0.25;
  ctx.fillStyle = color;
  ctx.fillRect(px, py, TILE*PX, TILE*PX);
  ctx.globalAlpha = 1;
}
function drawSkyOverlay() {
  if (currentInterior) {
    const grad = ctx.createRadialGradient(canvas.width/2, canvas.height/2, 200, canvas.width/2, canvas.height/2, canvas.width*0.8);
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(1, 'rgba(0,0,0,0.4)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    return;
  }
  const phase = getTimeOfDay();
  ctx.fillStyle = skyColors[phase];
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const darkness = getDarkness();
  if (darkness > 0) {
    const grad = ctx.createRadialGradient(canvas.width/2, canvas.height/2, 100, canvas.width/2, canvas.height/2, canvas.width*0.7);
    grad.addColorStop(0, 'rgba(0,0,0,0)');
    grad.addColorStop(0.7, `rgba(10,10,40,${darkness*0.5})`);
    grad.addColorStop(1, `rgba(10,10,40,${darkness})`);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  const h = (time.totalMinutes/60)%24;
  let iconX, iconY, iconEmoji;
  if (h >= 5 && h < 19) {
    const progress = (h-5)/14;
    iconX = canvas.width*0.1 + canvas.width*0.8*progress;
    iconY = 60 + Math.sin(progress*Math.PI)*-20;
    iconEmoji = h < 9 ? '🌅' : h < 17 ? '☀️' : '🌇';
  } else {
    const nh = h >= 19 ? h-19 : h+5;
    const progress = nh/10;
    iconX = canvas.width*0.1 + canvas.width*0.8*progress;
    iconY = 60 + Math.sin(progress*Math.PI)*-20;
    iconEmoji = '🌙';
  }
  ctx.font = '32px serif'; ctx.textAlign = 'center';
  ctx.fillText(iconEmoji, iconX, iconY);
  if (fishing.active && fishing.state === 'waiting') {
    ctx.font = '20px monospace';
    ctx.fillStyle = '#4a90e2';
    ctx.textAlign = 'center';
    ctx.fillText('🎣...', canvas.width/2, canvas.height - 100);
  }
}
function draw() {
  ctx.fillStyle = currentInterior ? '#1a1a2e' : '#000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const ww = getActiveWorld();
  const startX = Math.max(0, Math.floor(camera.x/TILE)-1);
  const endX = Math.min(ww[0].length, Math.ceil((camera.x + canvas.width/PX)/TILE)+1);
  const startY = Math.max(0, Math.floor(camera.y/TILE)-1);
  const endY = Math.min(ww.length, Math.ceil((camera.y + canvas.height/PX)/TILE)+1);
  for (let y=startY; y<endY; y++)
    for (let x=startX; x<endX; x++)
      if (ww[y] && ww[y][x] !== undefined) drawTile(ww[y][x], x, y);

  if (!currentInterior) {
    const entities = [];
    npcs.forEach(n => entities.push({y: n.y, draw: () => drawNpc(n)}));
    animals.forEach(a => { if (!a.dead) entities.push({y: a.y, draw: () => drawAnimal(a)}); });
    wolves.forEach(w => entities.push({y: w.y, draw: () => drawWolf(w)}));
    entities.push({y: player.y, draw: () => {
      drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2', '#ffcc99', '#4a90e2');
    }});
    entities.sort((a,b) => a.y - b.y).forEach(e => e.draw());
    arrows.forEach(drawArrow);
  } else {
    drawHumanoid(player.x, player.y, player.dir, player.walkFrame, '#4a90e2', '#ffcc99', '#4a90e2');
  }
  drawCursorHighlight();
  drawSkyOverlay();
}
function loop() {
  try {
    update();
    draw();
  } catch(err) {
    console.error('Game loop error:', err);
    // Draw error message di canvas
    ctx.fillStyle = '#f00';
    ctx.font = '16px monospace';
    ctx.fillText('ERROR: ' + err.message, 20, 30);
  }
  requestAnimationFrame(loop);
}
document.body.addEventListener('click', () => ensureAudio(), { once: false });
updateHUD(); updateToolbarUI(); updateHUDBars(); loop();
</script>
</body>
</html>
"""

components.html(game_html, height=650)
