import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pixel Farm RPG", page_icon="🌾", layout="wide")
st.title("🌾 Pixel Farm RPG")
st.caption("**WASD** jalan • **Klik** action • **1-9** tool • **H** hire • **R** army • **G** guard • **I** inventory • **B** shop • **E** interaksi")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#0a0a1e; font-family:'Courier New',monospace; overflow:hidden; color:#fff; }
  
  #gameWrap { position:relative; width:100%; height:100vh; display:flex; justify-content:center; align-items:center; background:#0a0a1e; overflow:hidden; }
  
  canvas { 
    image-rendering:pixelated; 
    border:4px solid #2a2a3e; 
    box-shadow:0 0 40px rgba(0,255,0,0.2); 
    background:#000; 
    cursor:crosshair; 
    display: block;
  }

  #hud { position:absolute; top:12px; left:12px; display:flex; flex-direction:column; gap:6px; pointer-events:none; font-size:13px; }
  .bar { width:180px; height:22px; background:rgba(0,0,0,0.7); border:2px solid #222; border-radius:3px; position:relative; overflow:hidden; }
  .bar .fill { height:100%; transition:width 0.3s; }
  .bar .label { position:absolute; top:0; left:8px; line-height:18px; font-size:12px; font-weight:bold; text-shadow:1px 1px 0 #000; }
  #hpFill { background:linear-gradient(180deg, #ff4444, #aa0000); }
  #hungerFill { background:linear-gradient(180deg, #ffaa00, #cc6600); }

  #topRight { position:absolute; top:12px; right:12px; background:rgba(0,0,0,0.75); border:2px solid #222; border-radius:4px; padding:8px 14px; font-size:13px; text-align:right; pointer-events:none; line-height:1.6; }
  #timeOfDay { color:#ffed4a; font-weight:bold; font-size:14px; text-shadow:0 0 8px currentColor; }
  #gold { color:#ffd700; font-weight:bold; text-shadow:0 0 8px #ffd700; }

  #stats { position:absolute; top:12px; left:210px; font-size:11px; color:#888; background:rgba(0,0,0,0.6); padding:6px 10px; border-radius:4px; border:1px solid #222; pointer-events:none; line-height:1.5; }

  #topToolbar {
    position:absolute; top:80px; left:50%; transform:translateX(-50%);
    display:flex; gap:4px; background:rgba(0,0,0,0.85);
    padding:6px; border:2px solid #2a2a3e; border-radius:8px; z-index:20;
  }
  .menuBtn {
    display:flex; align-items:center; gap:6px;
    padding:7px 14px; background:rgba(30,30,50,0.9);
    border:2px solid #333; color:#888;
    font-family:inherit; font-size:12px; font-weight:bold;
    cursor:pointer; border-radius:5px;
    transition:all 0.15s; user-select:none; white-space:nowrap;
  }
  .menuBtn:hover { background:rgba(50,50,80,0.9); border-color:#666; color:#fff; transform:translateY(-2px); }
  #saveBtn { color:#5aff5a; }
  #saveBtn:hover { border-color:#5aff5a; box-shadow:0 0 12px rgba(90,255,90,0.5); }
  #achBtn { color:#ffed4a; }
  #achBtn:hover { border-color:#ffed4a; box-shadow:0 0 12px rgba(255,237,74,0.5); }
  #shopBtn { color:#ffd700; }
  #shopBtn:hover { border-color:#ffd700; box-shadow:0 0 12px rgba(255,215,0,0.5); }
  #hireBtn { color:#ffaa55; }
  #hireBtn:hover { border-color:#ffaa55; box-shadow:0 0 12px rgba(255,170,85,0.5); }
  #armyBtn { color:#ff5555; }
  #armyBtn:hover { border-color:#ff5555; box-shadow:0 0 12px rgba(255,85,85,0.5); }

  #toolbar { position:absolute; bottom:16px; left:50%; transform:translateX(-50%); display:flex; gap:5px; background:rgba(0,0,0,0.85); padding:8px; border:2px solid #2a2a3e; border-radius:8px; flex-wrap:wrap; justify-content:center; max-width:95%; }
  .tool { padding:7px 10px; background:rgba(30,30,50,0.9); border:2px solid #333; color:#888; font-family:inherit; font-size:11px; cursor:pointer; border-radius:5px; user-select:none; transition:all 0.15s; min-width:54px; text-align:center; position:relative; }
  .tool:hover { background:rgba(50,50,80,0.9); border-color:#666; color:#ccc; transform:translateY(-2px); }
  .tool.active { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border-color:#ffed4a; color:#ffed4a; box-shadow:0 0 15px rgba(255,237,74,0.6); font-weight:bold; }
  .tool .num { position:absolute; top:1px; left:4px; font-size:9px; color:#666; }
  .tool.active .num { color:#ffed4a; }

  #inv, #shop, #achPanel, #hirePanel, #armyPanel {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    background:rgba(15,15,25,0.97); border:3px solid #2a2a3e; border-radius:10px;
    padding:20px; display:none; box-shadow:0 0 40px rgba(0,0,0,0.9); z-index:100;
    min-width:440px; max-width:600px; max-height:80vh; overflow-y:auto;
  }
  #inv h2, #shop h2, #achPanel h2, #hirePanel h2, #armyPanel h2 { color:#ffed4a; margin:0 0 16px 0; font-size:18px; border-bottom:2px solid #2a2a3e; padding-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
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
  .shopItem .desc { color:#888; font-size:11px; margin-top:2px; }
  .shopItem button { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border:2px solid #5aff5a; color:#5aff5a; padding:6px 14px; font-family:inherit; font-size:12px; border-radius:4px; cursor:pointer; font-weight:bold; }
  .shopItem button:hover { background:linear-gradient(180deg, #3a7d3a, #2a5d2a); }
  .shopItem button:disabled { opacity:0.3; cursor:not-allowed; }
  .shopItem .hireBtn { background:linear-gradient(180deg, #4a3d2a, #2a1d1a); border-color:#ffaa55; color:#ffaa55; }
  .shopItem .hireBtn:hover { background:linear-gradient(180deg, #6a5d4a, #3a2d2a); }
  .shopItem .armyBtn { background:linear-gradient(180deg, #5d2a2a, #3d1a1a); border-color:#ff5555; color:#ff5555; }
  .shopItem .armyBtn:hover { background:linear-gradient(180deg, #7d3a3a, #5d2a2a); }
  .shopTabs { display:flex; gap:6px; margin-bottom:12px; }
  .shopTab { flex:1; padding:8px; text-align:center; background:rgba(30,30,50,0.7); border:2px solid #333; color:#888; font-family:inherit; font-size:13px; border-radius:4px; cursor:pointer; user-select:none; }
  .shopTab.active { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border-color:#ffed4a; color:#ffed4a; }
  .achGrid { display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; }
  .achItem { display:flex; gap:10px; align-items:center; padding:10px; background:rgba(30,30,50,0.5); border:2px solid #333; border-radius:6px; opacity:0.4; }
  .achItem.unlocked { opacity:1; border-color:#ffed4a; background:linear-gradient(180deg, rgba(50,50,20,0.7), rgba(30,30,50,0.7)); box-shadow:0 0 10px rgba(255,237,74,0.3); }
  .achItem .emoji { font-size:28px; }
  .achItem .achName { color:#ffed4a; font-size:13px; font-weight:bold; }
  .achItem .achDesc { color:#aaa; font-size:10px; margin-top:2px; }
  #dialog { position:absolute; bottom:90px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.92); border:3px solid #ffed4a; color:#ffed4a; padding:14px 24px; font-size:15px; display:none; min-width:400px; text-align:center; box-shadow:0 0 30px rgba(255,237,74,0.4); border-radius:6px; max-width:600px; z-index:80; }
  #toast { position:absolute; top:140px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.9); border:2px solid #ffed4a; color:#ffed4a; padding:10px 20px; font-size:15px; display:none; box-shadow:0 0 20px rgba(255,237,74,0.5); border-radius:4px; pointer-events:none; font-weight:bold; z-index:200; }
  #achPop { position:absolute; top:200px; left:50%; transform:translateX(-50%); background:linear-gradient(180deg, rgba(80,60,0,0.98), rgba(40,30,0,0.98)); border:3px solid #ffed4a; color:#ffed4a; padding:14px 24px; display:none; box-shadow:0 0 40px rgba(255,237,74,0.8); border-radius:8px; pointer-events:none; z-index:300; min-width:300px; text-align:center; }
  #achPop .title { font-size:12px; color:#ffaa00; letter-spacing:3px; }
  #achPop .name { font-size:18px; font-weight:bold; margin:4px 0; }
  #achPop .desc { font-size:11px; color:#aaa; }
  #damageFlash { position:absolute; inset:0; background:radial-gradient(circle, transparent 30%, rgba(255,0,0,0.6) 100%); opacity:0; pointer-events:none; transition:opacity 0.2s; z-index:50; }
  #hint { position:absolute; bottom:12px; right:12px; font-size:10px; color:#555; text-align:right; line-height:1.6; }
  #muteIcon { position:absolute; bottom:12px; left:12px; font-size:20px; cursor:pointer; padding:6px; user-select:none; transition:transform 0.2s; z-index:20; }
  #muteIcon:hover { transform:scale(1.2); }
  #saveIndicator { position:absolute; top:60px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.85); color:#5aff5a; padding:6px 14px; border-radius:4px; font-size:12px; border:2px solid #5aff5a; display:none; z-index:150; box-shadow:0 0 15px rgba(90,255,90,0.4); }
  #bedPrompt { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.95); border:3px solid #5aff5a; color:#5aff5a; padding:20px 36px; font-size:18px; display:none; text-align:center; border-radius:10px; box-shadow:0 0 40px rgba(90,255,90,0.7); z-index:150; pointer-events:none; animation: bedPulse 1.2s infinite; }
  #doorPrompt { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.95); border:3px solid #4a90e2; color:#4a90e2; padding:16px 28px; font-size:18px; display:none; text-align:center; border-radius:10px; box-shadow:0 0 40px rgba(74,144,226,0.7); z-index:150; pointer-events:none; animation: bedPulse 1.2s infinite; }
  @keyframes bedPulse {
    0%, 100% { transform: translate(-50%,-50%) scale(1); }
    50% { transform: translate(-50%,-50%) scale(1.05); }
  }
  #fishIndicator { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.9); border:3px solid #4a90e2; color:#4a90e2; padding:14px 24px; font-size:15px; display:none; text-align:center; border-radius:8px; box-shadow:0 0 30px rgba(74,144,226,0.5); z-index:150; pointer-events:none; min-width:280px; }
  #fishBar { width:220px; height:20px; background:rgba(0,0,0,0.7); border:2px solid #4a90e2; border-radius:3px; margin:10px auto 0; position:relative; overflow:hidden; }
  #fishBar .fill { height:100%; background:linear-gradient(90deg, #4a90e2, #5aff5a); width:0%; }
  .seedPicker { display:flex; gap:6px; margin-top:10px; padding:8px; background:rgba(0,0,0,0.5); border-radius:6px; }
  .seedOpt { flex:1; padding:8px; text-align:center; background:rgba(30,30,50,0.7); border:2px solid #333; color:#aaa; font-family:inherit; font-size:11px; border-radius:4px; cursor:pointer; user-select:none; }
  .seedOpt.active { background:linear-gradient(180deg, #2a5d2a, #1a3d1a); border-color:#ffed4a; color:#ffed4a; }
  #seedPickerWrap { position:absolute; bottom:110px; left:50%; transform:translateX(-50%); background:rgba(15,15,25,0.95); border:2px solid #ffed4a; border-radius:8px; padding:10px; display:none; z-index:80; }
  .unitRow { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:rgba(30,30,50,0.6); border:2px solid #333; border-radius:6px; margin-bottom:6px; }
  .unitRow.guard { border-color:#ffd700; box-shadow:0 0 8px rgba(255,215,0,0.4); }
  .unitRow .info { display:flex; align-items:center; gap:10px; flex:1; }
  .unitRow .emoji { font-size:22px; }
  .unitRow .name { color:#fff; font-size:13px; }
  .unitRow .status { color:#888; font-size:11px; }
  .unitRow .status.working { color:#5aff5a; }
  .unitRow .status.idle { color:#ffaa00; }
  .unitRow .status.fighting { color:#ff5555; }
  .unitRow .status.guard { color:#ffd700; }
  .unitRow .slotInfo { color:#ffaa55; font-size:10px; }
  .unitRow button { background:linear-gradient(180deg, #5d2a2a, #3d1a1a); border:2px solid #ff5555; color:#ff5555; padding:4px 10px; font-family:inherit; font-size:11px; border-radius:4px; cursor:pointer; font-weight:bold; margin-left:4px; }
  .unitRow button:hover { background:linear-gradient(180deg, #7d3a3a, #5d2a2a); }
  .unitRow button.guardBtn { background:linear-gradient(180deg, #5d5a2a, #3d3a1a); border-color:#ffd700; color:#ffd700; }
  .unitRow button.guardBtn:hover { background:linear-gradient(180deg, #7d7a3a, #5d5a2a); }
  .unitRow button.guardBtn.active { background:linear-gradient(180deg, #ffd700, #aa8800); color:#000; }

  .cropSelectRow {
    display:flex; gap:8px; margin-top:12px; padding:12px;
    background:rgba(0,0,0,0.4); border:2px dashed #444; border-radius:8px;
  }
  .cropSelectRow .cropOpt {
    flex:1; padding:10px 8px; text-align:center;
    background:rgba(30,30,50,0.7);
    border:2px solid #333; color:#aaa;
    font-family:inherit; font-size:12px;
    border-radius:6px; cursor:pointer;
    user-select:none; transition:all 0.15s;
  }
  .cropSelectRow .cropOpt:hover {
    background:rgba(50,50,80,0.9);
    border-color:#888;
    color:#fff;
  }
  .cropSelectRow .cropOpt.active {
    background:linear-gradient(180deg, #2a5d2a, #1a3d1a);
    border-color:#ffed4a; color:#ffed4a;
    box-shadow:0 0 10px rgba(255,237,74,0.4);
    font-weight:bold;
  }
  .cropSelectRow .cropOpt .cropEmoji { font-size:24px; display:block; }
  .cropSelectRow .cropOpt .cropName { font-size:11px; margin-top:4px; }
  .cropSelectRow .cropOpt .cropStock { font-size:9px; color:#666; margin-top:2px; }
  .cropSelectRow .cropOpt.active .cropStock { color:#ffed4a; }

  .toggleRow {
    display:flex; justify-content:space-between; align-items:center;
    padding:10px 14px; background:rgba(0,0,0,0.4);
    border:2px solid #444; border-radius:8px;
    margin-top:12px;
  }
  .toggleRow .label { color:#ffed4a; font-size:13px; font-weight:bold; }
  .toggleRow .subLabel { color:#888; font-size:10px; margin-top:2px; }
  .toggleBtn {
    padding:6px 16px; font-family:inherit; font-size:12px;
    border-radius:20px; cursor:pointer; font-weight:bold;
    transition:all 0.2s;
  }
  .toggleBtn.on { background:linear-gradient(180deg, #2a7d2a, #1a5d1a); border:2px solid #5aff5a; color:#5aff5a; box-shadow:0 0 12px rgba(90,255,90,0.5); }
  .toggleBtn.off { background:linear-gradient(180deg, #5d2a2a, #3d1a1a); border:2px solid #ff5555; color:#ff5555; }

  .bigBtn {
    width:100%; padding:12px;
    background:linear-gradient(180deg, #2a5d8a, #1a3d6a);
    border:2px solid #4a90e2; color:#4a90e2;
    font-family:inherit; font-size:14px; font-weight:bold;
    border-radius:8px; cursor:pointer;
    margin-top:12px;
    transition:all 0.15s;
  }
  .bigBtn:hover { background:linear-gradient(180deg, #3a7daa, #2a5d8a); box-shadow:0 0 15px rgba(74,144,226,0.6); }
  .bigBtn:disabled { opacity:0.4; cursor:not-allowed; }

  #placementHint {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    background:rgba(0,0,0,0.95); border:3px solid #4a90e2;
    color:#4a90e2; padding:16px 28px;
    font-size:16px; display:none; text-align:center;
    border-radius:8px; box-shadow:0 0 40px rgba(74,144,226,0.8);
    z-index:180; pointer-events:none;
    animation: bedPulse 1.5s infinite;
  }
</style>
</head>
<body>
<div id="gameWrap">
  <canvas id="game" width="960" height="640"></canvas>
  <div id="damageFlash"></div>
  <div id="hud">
    <div class="bar"><div class="fill" id="hpFill" style="width:100%"></div><div class="label">❤️ <span id="hpText">100/100</span></div></div>
    <div class="bar"><div class="fill" id="hungerFill" style="width:100%"></div><div class="label">🍗 <span id="hungerText">100/100</span></div></div>
  </div>
  <div id="topRight">
    <div id="timeOfDay">🌅 Pagi</div>
    <div>Day <span id="dayNum">1</span> — <span id="clock">06:00</span></div>
    <div>🪙 <span id="gold">0</span></div>
    <div style="font-size:11px;color:#ffaa55">👨‍🌾 <span id="workerCount">0</span> · ⚔️ <span id="armyCount">0</span> · 🛡️ <span id="guardCount">0</span>/2</div>
  </div>
  <div id="stats">🪵 <span id="wood">0</span> · 🍗 <span id="food">0</span> · 🌾 <span id="wheat">0</span> · 🏹 <span id="arrows">10</span></div>

  <div id="topToolbar">
    <button id="saveBtn" class="menuBtn">💾 Save</button>
    <button id="achBtn" class="menuBtn">🏆 Trophy</button>
    <button id="shopBtn" class="menuBtn">🏪 Shop</button>
    <button id="hireBtn" class="menuBtn">👨‍🌾 Hire</button>
    <button id="armyBtn" class="menuBtn">⚔️ Army</button>
  </div>

  <div id="toolbar">
    <div class="tool" data-tool="hoe"><span class="num">1</span>🪓<br>Hoe</div>
    <div class="tool" data-tool="seed"><span class="num">2</span>🌱<br>Seed</div>
    <div class="tool" data-tool="water"><span class="num">3</span>💧<br>Water</div>
    <div class="tool" data-tool="harvest"><span class="num">4</span>🌾<br>Harvest</div>
    <div class="tool" data-tool="axe"><span class="num">5</span>🪓<br>Axe</div>
    <div class="tool" data-tool="sword"><span class="num">6</span>⚔️<br>Sword</div>
    <div class="tool" data-tool="bow"><span class="num">7</span>🏹<br>Bow</div>
    <div class="tool" data-tool="rod"><span class="num">8</span>🎣<br>Fishing</div>
    <div class="tool" data-tool="shovel"><span class="num">9</span>🪏<br>Shovel</div>
  </div>
  <div id="seedPickerWrap">
    <div style="color:#ffed4a;font-size:12px;margin-bottom:6px;text-align:center">🌱 Pilih Benih:</div>
    <div class="seedPicker">
      <div class="seedOpt active" data-seed="wheat">🌾 Gandum<br><small>10g</small></div>
      <div class="seedOpt" data-seed="corn">🌽 Jagung<br><small>25g</small></div>
      <div class="seedOpt" data-seed="tomato">🍅 Tomat<br><small>40g</small></div>
    </div>
  </div>
  <div id="inv"><h2>🎒 Inventory <button class="closeBtn" id="closeInvBtn">✕</button></h2><div id="invGrid"></div><div id="invHint">Klik food buat makan · Klik item buat jual</div></div>
  <div id="shop"><h2>🏪 Toko <button class="closeBtn" id="closeShopBtn">✕</button></h2><div class="shopTabs"><div class="shopTab active" data-tab="buy">🛒 Beli</div><div class="shopTab" data-tab="sell">💰 Jual</div></div><div id="shopContent"></div></div>
  <div id="hirePanel"><h2>👨‍🌾 Hire Worker <button class="closeBtn" id="closeHireBtn">✕</button></h2><div id="hireContent"></div></div>
  <div id="armyPanel"><h2>⚔️ Barak Prajurit <button class="closeBtn" id="closeArmyBtn">✕</button></h2><div id="armyContent"></div></div>
  <div id="achPanel"><h2>🏆 Achievement <button class="closeBtn" id="closeAchBtn">✕</button></h2><div class="achGrid" id="achGrid"></div></div>
  <div id="dialog"></div>
  <div id="toast"></div>
  <div id="achPop"><div class="title">🏆 ACHIEVEMENT UNLOCKED</div><div class="name" id="achPopName"></div><div class="desc" id="achPopDesc"></div></div>
  <div id="muteIcon">🔊</div>
  <div id="saveIndicator">💾 Tersimpan!</div>
  <div id="bedPrompt">🛏️ <b>Tidur?</b><br>Tekan <b style="color:#ffed4a;font-size:22px">E</b> untuk tidur</div>
  <div id="doorPrompt">🚪 <b>Pintu</b><br>Tekan <b style="color:#4a90e2;font-size:22px">E</b> untuk masuk/keluar</div>
  <div id="placementHint">📍 Klik di tanah buat tentukan area farm (3×3)<br><small>ESC buat batal</small></div>
  <div id="fishIndicator">🎣 <span id="fishStatus">Menunggu...</span><div id="fishBar"><div class="fill" id="fishBarFill"></div></div><div style="font-size:11px;color:#888;margin-top:6px" id="fishHint"></div></div>
  <div id="hint">WASD = jalan • Klik = action • 1-9 = tool<br>B = shop • H = hire • R = army • G = guard</div>
</div>

<script>
'use strict';
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
  } catch(e) { console.warn('Audio error:', e); }
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
function sfxShovel() { playNoise(0.18,1,700); playTone(100,0.2,'sawtooth',0.9); }
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
function sfxHire() { playTone(440,0.1,'triangle',1); playTone(660,0.12,'triangle',1,0.1); playTone(880,0.15,'triangle',1,0.2); }
function sfxRecruit() { playTone(300,0.12,'sawtooth',1); playTone(400,0.12,'sawtooth',1,0.1); playTone(600,0.2,'sawtooth',1,0.2); playNoise(0.15,0.5,1500); }
function sfxCoin() { playTone(1319,0.05,'square',0.9); playTone(1760,0.08,'square',0.7,0.04); }
function sfxSword() { playNoise(0.1,1.2,2500); playTone(500,0.08,'triangle',0.9); playTone(250,0.15,'triangle',0.8,0.05); }
function sfxArmor() { playNoise(0.08,0.8,1800); playTone(300,0.1,'square',0.6); playTone(200,0.1,'square',0.5,0.05); }
function sfxFence() { playNoise(0.12,0.8,500); playTone(200,0.15,'square',0.8); playTone(150,0.12,'square',0.7,0.05); }

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
  try {
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
  } catch(e) {}
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
// ==== CONSTANTS ====
// ============================================
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const PX = 5, TILE = 32, WORLD_W = 40, WORLD_H = 30;

const T_GRASS=0,T_PATH=1,T_WATER=2,T_TREE=3,T_FARMLAND=4,T_CROP=5,
      T_HOUSE=6,T_STUMP=7,T_SAPLING=8,T_HOUSE_DOOR=9,T_FLOWER=10,T_LAMP=11,
      T_BED=12,T_INTERIOR_FLOOR=13,T_WALL=14,T_TABLE=15,T_SHOP=16,T_CAMP=17,
      T_FENCE=18;

const CROP_TYPES = {
  wheat:  { name:'Gandum', emoji:'🌾', price:10, seedPrice:5,  growTime:400, color:'#e8c850' },
  corn:   { name:'Jagung', emoji:'🌽', price:25, seedPrice:15, growTime:600, color:'#ffcc33' },
  tomato: { name:'Tomat',  emoji:'🍅', price:40, seedPrice:25, growTime:800, color:'#ff4444' },
};

const WORKER_MAX_FARMLAND = 9;
const FARM_AREA_W = 3;
const FARM_AREA_H = 3;
const MAX_GUARDS = 2;

const ARMY_TYPES = {
  swordsman: {
    name: 'Swordsman', emoji: '⚔️', cost: 150,
    desc: 'Melee HP 60, DMG 15, Armor 2',
    color: '#8b3a3a', shirt: '#c0392b',
    hp: 60, hpMax: 60, dmg: 15, range: 22, speed: 1.2, attackDelay: 0.8,
    armor: 2, armorColor: '#b0b0b0', armorStyle: 'chain',
  },
  archer: {
    name: 'Archer', emoji: '🏹', cost: 180,
    desc: 'Ranged HP 45, DMG 12, Armor 1',
    color: '#3a5a8b', shirt: '#2980b9',
    hp: 45, hpMax: 45, dmg: 12, range: 130, speed: 1.0, attackDelay: 1.0,
    armor: 1, armorColor: '#5a3a1a', armorStyle: 'leather',
  },
  knight: {
    name: 'Knight', emoji: '🛡️', cost: 400,
    desc: 'Tank HP 140, DMG 25, Armor 4',
    color: '#5a5a5a', shirt: '#7f8c8d',
    hp: 140, hpMax: 140, dmg: 25, range: 24, speed: 0.8, attackDelay: 0.6,
    armor: 4, armorColor: '#c0c0c0', armorStyle: 'plate',
  },
};

// ============================================
// ==== STATE ====
// ============================================
const camera = { x:0, y:0 };
const player = {
  x: 20*TILE, y: 20*TILE, w: 20, h: 28, speed: 2.0,
  dir: 'down', animTimer: 0, walkFrame: 0,
  hp: 100, hpMax: 100, hunger: 100, hungerMax: 100,
  attackCooldown: 0,
};
const time = { totalMinutes: 6*60, day: 1, minutesPerSecond: 3 };
const inventory = { wheat:0, corn:0, tomato:0, wood:0, food:0, seeds:5, seeds_corn:0, seeds_tomato:0, arrows:10, pelt:0, fish:0 };
let gameGold = 500;
let currentSeed = 'wheat';
let workerSeed = 'wheat';
let currentTool = null;
let showInventory = false;

let autoSell = false;

let placementMode = false;
let placementPreviewX = 0;
let placementPreviewY = 0;

let world = [];
const crops = {};
const trees = {};
let animals = [];
let wolves = [];
let arrows = [];
let npcs = [];
let workers = [];
let army = [];
let projectiles = [];
let currentInterior = null;
let doorCooldown = 0;
let nearDoor = false;
let nearBed = false;
let nearShop = false;
let nearWater = false;
let nearShopTile = null;

// ============================================
// ==== UTILS ====
// ============================================
function isSolid(tx, ty, w) {
  const ww = w || world;
  if (!ww || !ww[ty]) return true;
  if (tx < 0 || ty < 0 || tx >= ww[0].length || ty >= ww.length) return true;
  const t = ww[ty][tx];
  // T_FENCE TETAP SOLID KARENA KITA UDAH BIKIN GATE DI AREA FARM
  // TAPI BUAT PLAYER, KITA KECUALIKAN T_HOUSE_DOOR BIAR BISA MASUK
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

function getSeedKey(cropType) {
  return 'seeds' + (cropType === 'wheat' ? '' : '_' + cropType);
}

function isInsideAnyFarmArea(tx, ty) {
  for (const w of workers) {
    if (!w.farmArea) continue;
    if (tx >= w.farmArea.x && tx < w.farmArea.x + FARM_AREA_W &&
        ty >= w.farmArea.y && ty < w.farmArea.y + FARM_AREA_H) {
      return w;
    }
  }
  return null;
}
function isFarmAreaOverlap(fx, fy) {
  for (const w of workers) {
    if (!w.farmArea) continue;
    if (fx < w.farmArea.x + FARM_AREA_W && fx + FARM_AREA_W > w.farmArea.x &&
        fy < w.farmArea.y + FARM_AREA_H && fy + FARM_AREA_H > w.farmArea.y) {
      return true;
    }
  }
  return false;
}

// ============================================
// ==== UI ====
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
  t._timeout = setTimeout(() => t.style.display = 'none', 1400);
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

  world[15][25] = T_SHOP;
  world[15][24] = T_PATH;
  world[15][26] = T_PATH;
  world[16][25] = T_PATH;

  world[22][8] = T_CAMP;
  world[22][9] = T_CAMP;
  world[23][8] = T_CAMP;
  world[23][9] = T_CAMP;
  for (let y=21; y<25; y++)
    for (let x=7; x<12; x++)
      if (world[y] && [T_TREE, T_WATER, T_LAMP].includes(world[y][x])) world[y][x] = T_GRASS;

  for (let x=6; x<WORLD_W-6; x+=8)
    if (world[12] && world[12][x] === T_GRASS) world[12][x] = T_LAMP;

  for (let y=18; y<WORLD_H-2; y++)
    for (let x=15; x<25; x++)
      if ([T_TREE, T_WATER, T_LAMP].includes(world[y][x])) world[y][x] = T_GRASS;
  for (let y=15; y<18; y++)
    for (let x=24; x<28; x++)
      if (world[y] && [T_TREE, T_WATER, T_LAMP].includes(world[y][x])) world[y][x] = T_GRASS;

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
  boss:           { emoji:'👨‍💼', name:'Bos Besar', desc:'Punya 5 petani', unlocked: false },
  general:        { emoji:'⚔️', name:'Jenderal', desc:'Punya 5 prajurit', unlocked: false },
  army_full:      { emoji:'🏰', name:'Benteng Berjalan', desc:'Punya 10 prajurit', unlocked: false },
  guardian:       { emoji:'🛡️', name:'Pelindung', desc:'2 army mendampingi', unlocked: false },
  auto_seller:    { emoji:'💸', name:'Pengusaha', desc:'Aktifin Auto-Sell', unlocked: false },
};
const stats = {
  harvestCount: 0, fishCaught: 0, animalsKilled: 0, wolvesKilled: 0,
  treesChopped: 0, cropsPlanted: new Set(), shopPurchases: 0,
  sleepCount: 0, maxGold: 0, workersHired: 0, soldiersRecruited: 0,
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
  if (!achievements.boss.unlocked && workers.length >= 5) unlockAchievement('boss');
  if (!achievements.general.unlocked && army.length >= 5) unlockAchievement('general');
  if (!achievements.army_full.unlocked && army.length >= 10) unlockAchievement('army_full');
  const guardCount = army.filter(s => s.guard).length;
  if (!achievements.guardian.unlocked && guardCount >= 2) unlockAchievement('guardian');
  if (!achievements.auto_seller.unlocked && autoSell) unlockAchievement('auto_seller');
}

// ============================================
// ==== NPCs & ANIMALS ====
// ============================================
const ANIMAL_TYPES = {
  rabbit: { color:'#f0e0d0', hp:20, speed:0.8, dropAmt:2 },
  chicken: { color:'#f5d76e', hp:15, speed:1.0, dropAmt:1 },
  cow: { color:'#e0d0b0', hp:40, speed:0.5, dropAmt:3 },
};

function initNPCs() {
  npcs = [
    { x: 8*TILE, y: 15*TILE, dir:'down', color:'#ff6b6b', name:'Budi',
      dialog:'Hire petani (H) atau rekrut prajurit (R)!',
      targetX: 8, targetY: 15, moveTimer: 3, speed: 0.6, animTimer:0, walkFrame:0 },
    { x: 19*TILE, y: 15*TILE, dir:'left', color:'#4ecdc4', name:'Sari',
      dialog:'Tentukan area farm sendiri biar petani fokus!',
      targetX: 19, targetY: 15, moveTimer: 4, speed: 0.7, animTimer:0, walkFrame:0 },
    { x: 32*TILE, y: 15*TILE, dir:'right', color:'#ffe66d', name:'Pak Tani',
      dialog:'Ada toko di timur! Tekan B buat buka.',
      targetX: 32, targetY: 15, moveTimer: 5, speed: 0.5, animTimer:0, walkFrame:0 },
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
      x: x*TILE+6, y: y*TILE+6, type, hp: t.hp, hpMax: t.hp,
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
    x: x*TILE+6, y: y*TILE+6, type, hp: t.hp, hpMax: t.hp,
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
    x: tx*TILE, y: ty*TILE, w:24, h:24, hp:30, hpMax:30, speed:1.8,
    attackTimer:0, dir:'down', hurtFlash:0, animTimer:0, walkFrame:0, wanderTimer:0, wanderAngle:0,
    target: null,
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
// ==== FARM AREA PLACEMENT ====
// ============================================
function startPlacement() {
  if (gameGold < 100) {
    sfxError();
    showToast(`❌ Butuh 100 gold buat hire!`, '#ff4444');
    return;
  }
  placementMode = true;
  closeAllPanels();
  document.getElementById('placementHint').style.display = 'block';
  showToast('📍 Klik di tanah buat tentukan area 3×3', '#4a90e2');
}

function cancelPlacement() {
  placementMode = false;
  document.getElementById('placementHint').style.display = 'none';
}

function tryPlaceFarmArea(fx, fy) {
  for (let dy = 0; dy < FARM_AREA_H; dy++) {
    for (let dx = 0; dx < FARM_AREA_W; dx++) {
      const tx = fx + dx, ty = fy + dy;
      if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) {
        sfxError(); showToast('❌ Area keluar dari map!', '#ff4444');
        return false;
      }
      const t = world[ty][tx];
      if (t !== T_GRASS && t !== T_FLOWER) {
        sfxError(); showToast('❌ Area harus tanah kosong/bunga!', '#ff4444');
        return false;
      }
    }
  }
  if (isFarmAreaOverlap(fx, fy)) {
    sfxError(); showToast('❌ Overlap dengan area petani lain!', '#ff4444');
    return false;
  }
  const ptx = Math.floor((player.x + player.w/2) / TILE);
  const pty = Math.floor((player.y + player.h/2) / TILE);
  if (ptx >= fx && ptx < fx + FARM_AREA_W && pty >= fy && pty < fy + FARM_AREA_H) {
    sfxError(); showToast('❌ Kamu lagi di area itu!', '#ff4444');
    return false;
  }
  return hireWorkerAtArea(fx, fy);
}

function hireWorkerAtArea(fx, fy) {
  if (gameGold < 100) {
    sfxError(); showToast(`❌ Butuh 100 gold!`, '#ff4444');
    return false;
  }
  gameGold -= 100;

  // 1. Bersihin tile di DALAM area (paksa jadi rumput biar bisa dicangkul)
  for (let dy = 0; dy < FARM_AREA_H; dy++) {
    for (let dx = 0; dx < FARM_AREA_W; dx++) {
      const tx = fx + dx, ty = fy + dy;
      if (world[ty] && world[ty][tx] !== undefined) {
        if (world[ty][tx] !== T_GRASS && world[ty][tx] !== T_FARMLAND && world[ty][tx] !== T_CROP) {
          world[ty][tx] = T_GRASS; 
        }
      }
    }
  }

  // 2. Pagar Atas
  for (let dx = -1; dx <= FARM_AREA_W; dx++) {
    const tx = fx + dx, ty = fy - 1;
    if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
      if (world[ty][tx] === T_GRASS || world[ty][tx] === T_FLOWER) {
        world[ty][tx] = T_FENCE;
      }
    }
  }

  // 3. Pagar Kiri
  for (let dy = 0; dy < FARM_AREA_H; dy++) {
    const tx = fx - 1, ty = fy + dy;
    if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
      if (world[ty][tx] === T_GRASS || world[ty][tx] === T_FLOWER) {
        world[ty][tx] = T_FENCE;
      }
    }
  }

  // 4. Pagar Kanan
  for (let dy = 0; dy < FARM_AREA_H; dy++) {
    const tx = fx + FARM_AREA_W, ty = fy + dy;
    if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
      if (world[ty][tx] === T_GRASS || world[ty][tx] === T_FLOWER) {
        world[ty][tx] = T_FENCE;
      }
    }
  }

  // 5. Pagar Bawah + Gerbang Tengah
  const gateX = fx + Math.floor(FARM_AREA_W / 2); 
  for (let dx = -1; dx <= FARM_AREA_W; dx++) {
    const tx = fx + dx, ty = fy + FARM_AREA_H;
    if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
      if (tx !== gateX) {
        if (world[ty][tx] === T_GRASS || world[ty][tx] === T_FLOWER) {
          world[ty][tx] = T_FENCE;
        }
      } else {
        if (world[ty][tx] === T_FENCE || world[ty][tx] === T_FLOWER) {
          world[ty][tx] = T_GRASS; // Buka gerbang
        }
      }
    }
  }

  sfxFence();

  const spawnX = (fx + Math.floor(FARM_AREA_W/2)) * TILE + 6;
  const spawnY = (fy + Math.floor(FARM_AREA_H/2)) * TILE + 6;

  workers.push({
    x: spawnX, y: spawnY,
    w: 20, h: 28,
    name: `Petani #${workers.length+1}`,
    color: '#8b6f47', shirt: '#5a8a3a',
    speed: 1.2,
    actionDelay: 1.5,
    actionTimer: 0,
    dir: 'down',
    animTimer: 0, walkFrame: 0,
    state: 'idle',
    targetTile: null,
    salary: 5,
    salaryTimer: 60,
    currentCropType: workerSeed,
    farmArea: { x: fx, y: fy, w: FARM_AREA_W, h: FARM_AREA_H },
  });
  stats.workersHired++;
  sfxHire();
  const cropInfo = CROP_TYPES[workerSeed];
  showToast(`👨‍🌾 Petani hired! Area 3×3 · Tanam ${cropInfo.emoji}`, '#5aff5a');
  updateHUD();
  checkAchievements();
  return true;
}

function fireWorker(index) {
  if (index < 0 || index >= workers.length) return;
  const w = workers[index];
  if (w.farmArea) {
    const fx = w.farmArea.x, fy = w.farmArea.y;
    for (let dx = -1; dx <= FARM_AREA_W; dx++) {
      const tx = fx + dx;
      for (const ty of [fy - 1, fy + FARM_AREA_H]) {
        if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
          if (world[ty][tx] === T_FENCE) world[ty][tx] = T_GRASS;
        }
      }
    }
    for (let dy = 0; dy < FARM_AREA_H; dy++) {
      for (const tx of [fx - 1, fx + FARM_AREA_W]) {
        const ty = fy + dy;
        if (tx >= 0 && ty >= 0 && tx < WORLD_W && ty < WORLD_H) {
          if (world[ty][tx] === T_FENCE) world[ty][tx] = T_GRASS;
        }
      }
    }
  }
  workers.splice(index, 1);
  sfxClick();
  showToast(`👋 ${w.name} dipecat`, '#ffaa55');
  updateHUD();
  renderHirePanel();
}

// ============================================
// ==== AUTO-SELL ====
// ============================================
function toggleAutoSell() {
  autoSell = !autoSell;
  sfxClick();
  showToast(autoSell ? '💸 Auto-Sell: ON' : '💸 Auto-Sell: OFF', autoSell ? '#5aff5a' : '#888');
  renderHirePanel();
  checkAchievements();
}

function autoSellCrop(cropType, amount) {
  const info = CROP_TYPES[cropType];
  if (!info) return;
  const earned = info.price * amount;
  gameGold += earned;
  if (gameGold > stats.maxGold) stats.maxGold = gameGold;
  sfxCoin();
  showToast(`💸 Auto-sell ${info.emoji} ${amount} → +${earned}g`, '#ffed4a');
}

// ============================================
// ==== WORKER (PETANI) ====
// ============================================
function updateWorkers(dt) {
  workers.forEach(w => {
    w.salaryTimer -= dt;
    if (w.salaryTimer <= 0) {
      w.salaryTimer = 60;
      if (gameGold >= w.salary) {
        gameGold -= w.salary;
        showToast(`💰 Bayar upah ${w.name} -${w.salary}g`, '#ffd700');
        sfxCoin();
      } else {
        showToast(`⚠️ Gold kurang! ${w.name} mogok kerja`, '#ff4444');
        w.state = 'idle';
      }
    }

    w.actionTimer -= dt;

    if (w.state === 'idle' || !w.targetTile) {
      const task = findFarmTask(w);
      if (task) {
        w.targetTile = task.tile;
        w.state = task.type;
      } else {
        if (Math.random() < 0.005) {
          w.dir = ['up','down','left','right'][Math.floor(Math.random()*4)];
        }
        return;
      }
    }

    if (w.targetTile) {
      const tx = w.targetTile.x * TILE + 6;
      const ty = w.targetTile.y * TILE + 6;
      const d = Math.hypot(tx - w.x, ty - w.y);

      if (d < 10) {
        if (w.actionTimer <= 0) {
          doWorkerAction(w);
          w.actionTimer = w.actionDelay;
        }
      } else {
        const dx = (tx - w.x) / d * w.speed;
        const dy = (ty - w.y) / d * w.speed;
        if (canMoveTo(w.x + dx, w.y, 20, 28, world)) w.x += dx;
        if (canMoveTo(w.x, w.y + dy, 20, 28, world)) w.y += dy;
        if (Math.abs(dx) > Math.abs(dy)) w.dir = dx > 0 ? 'right' : 'left';
        else w.dir = dy > 0 ? 'down' : 'up';
        w.animTimer++;
        if (w.animTimer > 10) { w.animTimer = 0; w.walkFrame = (w.walkFrame + 1) % 4; }
      }
    }
  });
}

function findFarmTask(w) {
  if (!w.farmArea) return null;
  const fx = w.farmArea.x, fy = w.farmArea.y;
  const fw = w.farmArea.w, fh = w.farmArea.h;

  for (let dy = 0; dy < fh; dy++) {
    for (let dx = 0; dx < fw; dx++) {
      const tx = fx + dx, ty = fy + dy;
      const key = `${tx},${ty}`;
      const c = crops[key];
      const t = world[ty] && world[ty][tx];
      if (t === T_CROP && c && c.stage >= 3) {
        return { type: 'harvest', tile: {x:tx, y:ty} };
      }
    }
  }

  const seedKey = getSeedKey(w.currentCropType);
  if (inventory[seedKey] > 0) {
    for (let dy = 0; dy < fh; dy++) {
      for (let dx = 0; dx < fw; dx++) {
        const tx = fx + dx, ty = fy + dy;
        const key = `${tx},${ty}`;
        const c = crops[key];
        const t = world[ty] && world[ty][tx];
        if (t === T_FARMLAND && (!c || c.stage === -1)) {
          return { type: 'plant', tile: {x:tx, y:ty} };
        }
      }
    }
  }

  let farmlandCount = 0;
  for (let dy = 0; dy < fh; dy++) {
    for (let dx = 0; dx < fw; dx++) {
      const tx = fx + dx, ty = fy + dy;
      const t = world[ty] && world[ty][tx];
      if (t === T_FARMLAND || t === T_CROP) farmlandCount++;
    }
  }
  if (farmlandCount < fw * fh) {
    for (let dy = 0; dy < fh; dy++) {
      for (let dx = 0; dx < fw; dx++) {
        const tx = fx + dx, ty = fy + dy;
        const t = world[ty] && world[ty][tx];
        if (t === T_GRASS || t === T_FLOWER) {
          return { type: 'hoe', tile: {x:tx, y:ty} };
        }
      }
    }
  }

  for (let dy = 0; dy < fh; dy++) {
    for (let dx = 0; dx < fw; dx++) {
      const tx = fx + dx, ty = fy + dy;
      const key = `${tx},${ty}`;
      const c = crops[key];
      const t = world[ty] && world[ty][tx];
      if (t === T_CROP && c && c.stage < 3 && !c.watered) {
        return { type: 'water', tile: {x:tx, y:ty} };
      }
    }
  }

  return null;
}

function doWorkerAction(w) {
  if (!w.targetTile) return;
  const tx = w.targetTile.x, ty = w.targetTile.y;
  const key = `${tx},${ty}`;
  const t = world[ty] && world[ty][tx];

  if (w.state === 'hoe') {
    if (t === T_GRASS || t === T_FLOWER) {
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHoe();
    }
    w.targetTile = null;
    w.state = 'idle';
  } 
  else if (w.state === 'plant') {
    const seedKey = getSeedKey(w.currentCropType);
    if (t === T_FARMLAND && inventory[seedKey] > 0) {
      inventory[seedKey]--;
      world[ty][tx] = T_CROP;
      const cropInfo = CROP_TYPES[w.currentCropType] || CROP_TYPES.wheat;
      crops[key] = { 
        stage: 0, 
        watered: false, 
        timer: 0, 
        type: w.currentCropType,
        growTime: cropInfo.growTime,
      };
      stats.cropsPlanted.add(w.currentCropType);
      sfxSeed();
    }
    w.targetTile = null;
    w.state = 'idle';
  } 
  else if (w.state === 'water') {
    if (t === T_CROP && crops[key] && !crops[key].watered && crops[key].stage < 3) {
      crops[key].watered = true;
      sfxWater();
    }
    w.targetTile = null;
    w.state = 'idle';
  } 
  else if (w.state === 'harvest') {
    if (t === T_CROP && crops[key] && crops[key].stage >= 3) {
      const cropType = crops[key].type || 'wheat';
      stats.harvestCount++;
      
      if (autoSell) {
        autoSellCrop(cropType, 1);
      } else {
        inventory[cropType] = (inventory[cropType] || 0) + 1;
        showToast(`👨‍🌾 ${w.name} panen ${CROP_TYPES[cropType].emoji}!`, '#5aff5a');
      }
      
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHarvest();
      updateHUD();
    }
    w.targetTile = null;
    w.state = 'idle';
  }
}

// ============================================
// ==== ARMY ====
// ============================================
function recruitSoldier(type) {
  const at = ARMY_TYPES[type];
  if (!at) return false;
  if (gameGold < at.cost) {
    sfxError();
    showToast(`❌ Butuh ${at.cost} gold!`, '#ff4444');
    return false;
  }
  gameGold -= at.cost;
  const campX = 8.5 * TILE, campY = 22.5 * TILE;
  army.push({
    x: campX + (Math.random()-0.5)*80,
    y: campY + (Math.random()-0.5)*80,
    w: 20, h: 28,
    type: type,
    name: `${at.name} #${army.length+1}`,
    color: at.color, shirt: at.shirt,
    hp: at.hp, hpMax: at.hpMax,
    dmg: at.dmg, range: at.range * 2, speed: at.speed * 2,
    attackDelay: at.attackDelay, attackTimer: 0,
    armor: at.armor,
    armorColor: at.armorColor,
    armorStyle: at.armorStyle,
    hurtFlash: 0,
    dir: 'down',
    animTimer: 0, walkFrame: 0,
    state: 'patrol',
    target: null,
    patrolTarget: { x: campX, y: campY },
    patrolTimer: Math.random() * 3,
    guard: false,
  });
  stats.soldiersRecruited++;
  sfxRecruit();
  showToast(`${at.emoji} ${at.name} direkrut! (-${at.cost}g)`, '#ff5555');
  updateHUD();
  checkAchievements();
  return true;
}
function dismissSoldier(index) {
  if (index < 0 || index >= army.length) return;
  const s = army[index];
  army.splice(index, 1);
  sfxClick();
  showToast(`👋 ${s.name} dibubarkan`, '#ffaa55');
  updateHUD();
  renderArmyPanel();
}
function toggleGuard(index) {
  if (index < 0 || index >= army.length) return;
  const s = army[index];
  const currentGuards = army.filter(x => x.guard).length;
  if (!s.guard && currentGuards >= MAX_GUARDS) {
    sfxError();
    showToast(`❌ Max ${MAX_GUARDS} prajurit mendampingi!`, '#ff4444');
    return;
  }
  s.guard = !s.guard;
  sfxClick();
  showToast(s.guard ? `🛡️ ${s.name} mendampingi kamu!` : `${s.name} kembali patroli`, s.guard ? '#ffd700' : '#888');
  updateHUD();
  renderArmyPanel();
  checkAchievements();
}

function updateArmy(dt) {
  army.forEach(s => {
    if (s.hurtFlash > 0) s.hurtFlash--;

    let nearestWolf = null;
    let nearestDist = 99999;
    wolves.forEach(w => {
      const d = Math.hypot(w.x - s.x, w.y - s.y);
      if (d < 500 && d < nearestDist) {
        nearestWolf = w;
        nearestDist = d;
      }
    });

    s.attackTimer -= dt;

    if (s.guard) {
      if (nearestWolf && nearestDist < 300) {
        chaseAndAttack(s, nearestWolf, dt);
      } else {
        const dxp = player.x - s.x;
        const dyp = player.y - s.y;
        const distP = Math.hypot(dxp, dyp);
        if (distP > 90) {
          const dx = dxp / distP * s.speed * 1.2;
          const dy = dyp / distP * s.speed * 1.2;
          if (canMoveTo(s.x + dx, s.y, 20, 28, world)) s.x += dx;
          if (canMoveTo(s.x, s.y + dy, 20, 28, world)) s.y += dy;
          if (Math.abs(dx) > Math.abs(dy)) s.dir = dx > 0 ? 'right' : 'left';
          else s.dir = dy > 0 ? 'down' : 'up';
          s.animTimer++;
          if (s.animTimer > 8) { s.animTimer = 0; s.walkFrame = (s.walkFrame + 1) % 4; }
        } else {
          s.walkFrame = 0;
        }
        s.state = 'guard';
      }
      return;
    }

    if (nearestWolf) {
      chaseAndAttack(s, nearestWolf, dt);
    } else {
      s.state = 'patrol';
      s.target = null;
      s.patrolTimer -= dt;
      if (s.patrolTimer <= 0) {
        s.patrolTimer = 3 + Math.random() * 4;
        s.patrolTarget = {
          x: (8.5 + (Math.random()-0.5)*8) * TILE,
          y: (22.5 + (Math.random()-0.5)*8) * TILE,
        };
      }
      const dx = s.patrolTarget.x - s.x;
      const dy = s.patrolTarget.y - s.y;
      const d = Math.hypot(dx, dy);
      if (d > 8) {
        const nx = dx / d * s.speed * 0.5;
        const ny = dy / d * s.speed * 0.5;
        if (canMoveTo(s.x + nx, s.y, 20, 28, world)) s.x += nx;
        if (canMoveTo(s.x, s.y + ny, 20, 28, world)) s.y += ny;
        if (Math.abs(nx) > Math.abs(ny)) s.dir = nx > 0 ? 'right' : 'left';
        else s.dir = ny > 0 ? 'down' : 'up';
        s.animTimer++;
        if (s.animTimer > 12) { s.animTimer = 0; s.walkFrame = (s.walkFrame + 1) % 4; }
      }
    }
  });
}

function chaseAndAttack(s, wolf, dt) {
  const d = Math.hypot(wolf.x - s.x, wolf.y - s.y);
  s.target = wolf;

  if (d <= s.range) {
    s.state = 'attack';
    if (s.attackTimer <= 0) {
      s.attackTimer = s.attackDelay;
      if (s.type === 'archer') {
        const dx = (wolf.x - s.x) / (d || 1);
        const dy = (wolf.y - s.y) / (d || 1);
        projectiles.push({
          x: s.x + 10, y: s.y + 10,
          vx: dx * 16, vy: dy * 16,
          life: 60, dmg: s.dmg,
        });
        sfxBowShoot();
      } else {
        wolf.hp -= s.dmg;
        wolf.hurtFlash = 10;
        sfxSword();
        if (wolf.hp <= 0) {
          wolves = wolves.filter(wl => wl !== wolf);
          inventory.pelt += 1;
          stats.wolvesKilled++;
          showToast(`⚔️ ${s.name} bunuh wolf! +1 pelt`, '#ff6666');
          updateHUD(); checkAchievements();
        }
      }
    }
  } else {
    s.state = 'chase';
    const dx = (wolf.x - s.x) / d * s.speed;
    const dy = (wolf.y - s.y) / d * s.speed;
    if (canMoveTo(s.x + dx, s.y, 20, 28, world)) s.x += dx;
    if (canMoveTo(s.x, s.y + dy, 20, 28, world)) s.y += dy;
    if (Math.abs(dx) > Math.abs(dy)) s.dir = dx > 0 ? 'right' : 'left';
    else s.dir = dy > 0 ? 'down' : 'up';
    s.animTimer++;
    if (s.animTimer > 8) { s.animTimer = 0; s.walkFrame = (s.walkFrame + 1) % 4; }
  }
}

// ============================================
// ==== PANELS ====
// ============================================
function renderHirePanel() {
  const c = document.getElementById('hireContent');
  if (!c) return;
  const canAfford = gameGold >= 100;
  let html = `
    <div class="shopItem">
      <div class="info">
        <div class="emoji">👨‍🌾</div>
        <div>
          <div class="name">Petani</div>
          <div class="price">🪙 100 gold (upah 5g/menit)</div>
          <div class="desc">Kerja di area 3×3 yang kamu tentukan</div>
        </div>
      </div>
    </div>
    <div style="margin-top:16px;color:#ffed4a;font-weight:bold;text-align:center;font-size:14px">🌱 Pilih Benih yang ditanam petani:</div>
    <div class="cropSelectRow">
      <div class="cropOpt ${workerSeed === 'wheat' ? 'active' : ''}" data-crop="wheat">
        <span class="cropEmoji">🌾</span>
        <div class="cropName">Gandum</div>
        <div class="cropStock">Stok: ${inventory.seeds}</div>
      </div>
      <div class="cropOpt ${workerSeed === 'corn' ? 'active' : ''}" data-crop="corn">
        <span class="cropEmoji">🌽</span>
        <div class="cropName">Jagung</div>
        <div class="cropStock">Stok: ${inventory.seeds_corn}</div>
      </div>
      <div class="cropOpt ${workerSeed === 'tomato' ? 'active' : ''}" data-crop="tomato">
        <span class="cropEmoji">🍅</span>
        <div class="cropName">Tomat</div>
        <div class="cropStock">Stok: ${inventory.seeds_tomato}</div>
      </div>
    </div>
    
    <div class="toggleRow">
      <div>
        <div class="label">💸 Auto-Sell</div>
        <div class="subLabel">Hasil panen petani langsung dijual</div>
      </div>
      <button class="toggleBtn ${autoSell ? 'on' : 'off'}">${autoSell ? 'ON' : 'OFF'}</button>
    </div>
    
    <button class="bigBtn" ${canAfford ? '' : 'disabled'}>📍 Tentukan Lokasi Farm & Hire</button>
  `;
  if (workers.length > 0) {
    html += `<div style="margin-top:16px;border-top:2px solid #2a2a3e;padding-top:12px;color:#ffed4a;font-weight:bold">👨‍🌾 Petani Kamu (${workers.length})</div>`;
    workers.forEach((w, i) => {
      const stateLabels = {
        idle: 'Nganggur...',
        hoe: 'Mencangkul 🪓',
        plant: 'Menanam 🌱',
        water: 'Menyiram 💧',
        harvest: 'Memanen 🌾',
      };
      const statusText = stateLabels[w.state] || w.state;
      const statusClass = w.state === 'idle' ? 'idle' : 'working';
      const cropInfo = CROP_TYPES[w.currentCropType] || CROP_TYPES.wheat;
      const areaText = w.farmArea ? `Area (${w.farmArea.x}, ${w.farmArea.y})` : 'No area';
      html += `
        <div class="unitRow">
          <div class="info">
            <div class="emoji">👨‍🌾</div>
            <div>
              <div class="name">${w.name}</div>
              <div class="status ${statusClass}">${statusText}</div>
              <div class="slotInfo">${cropInfo.emoji} ${cropInfo.name} · ${areaText}</div>
            </div>
          </div>
          <button data-fire-worker="${i}">Pecat</button>
        </div>
      `;
    });
  }
  c.innerHTML = html;
  
  c.querySelectorAll('.cropOpt').forEach(el => {
    el.onclick = () => {
      workerSeed = el.dataset.crop;
      sfxClick();
      renderHirePanel();
    };
  });
  c.querySelectorAll('button[data-fire-worker]').forEach(btn => {
    btn.onclick = () => fireWorker(parseInt(btn.dataset.fireWorker));
  });
  const bigBtn = c.querySelector('.bigBtn');
  if (bigBtn) bigBtn.onclick = () => { startPlacement(); };
  const toggleBtn = c.querySelector('.toggleBtn');
  if (toggleBtn) toggleBtn.onclick = () => { toggleAutoSell(); };
}

function renderArmyPanel() {
  const c = document.getElementById('armyContent');
  if (!c) return;
  const currentGuards = army.filter(s => s.guard).length;
  let html = `<div style="color:#ffaa55;font-size:12px;margin-bottom:12px;text-align:center">🛡️ Pengawal: ${currentGuards}/${MAX_GUARDS} (klik 🛡️ buat set guard)</div>`;
  Object.entries(ARMY_TYPES).forEach(([key, at]) => {
    const canAfford = gameGold >= at.cost;
    html += `
      <div class="shopItem">
        <div class="info">
          <div class="emoji">${at.emoji}</div>
          <div>
            <div class="name">${at.name}</div>
            <div class="price">🪙 ${at.cost} gold</div>
            <div class="desc">${at.desc}</div>
          </div>
        </div>
        <button class="armyBtn" data-recruit="${key}" ${canAfford ? '' : 'disabled'}>Rekrut</button>
      </div>
    `;
  });
  if (army.length > 0) {
    html += `<div style="margin-top:16px;border-top:2px solid #2a2a3e;padding-top:12px;color:#ff5555;font-weight:bold">⚔️ Prajurit Kamu (${army.length})</div>`;
    army.forEach((s, i) => {
      let statusText = 'Berpatroli';
      let statusClass = 'idle';
      if (s.guard) { statusText = '🛡️ Mendampingi kamu'; statusClass = 'guard'; }
      else if (s.state === 'chase') { statusText = 'Mengejar musuh!'; statusClass = 'fighting'; }
      else if (s.state === 'attack') { statusText = 'Bertarung!'; statusClass = 'fighting'; }
      const isGuard = s.guard ? 'guard' : '';
      html += `
        <div class="unitRow ${isGuard}">
          <div class="info">
            <div class="emoji">${ARMY_TYPES[s.type].emoji}</div>
            <div>
              <div class="name">${s.name}</div>
              <div class="status ${statusClass}">${statusText}</div>
              <div class="status">❤️ ${Math.round(s.hp)}/${s.hpMax} · ⚔️ ${s.dmg} · 🛡️ ${s.armor}</div>
            </div>
          </div>
          <div>
            <button class="guardBtn ${s.guard ? 'active' : ''}" data-guard-army="${i}">🛡️</button>
            <button data-dismiss-army="${i}">Bubarkan</button>
          </div>
        </div>
      `;
    });
  }
  c.innerHTML = html;
  c.querySelectorAll('button[data-recruit]').forEach(btn => {
    btn.onclick = () => { recruitSoldier(btn.dataset.recruit); renderArmyPanel(); };
  });
  c.querySelectorAll('button[data-dismiss-army]').forEach(btn => {
    btn.onclick = () => dismissSoldier(parseInt(btn.dataset.dismissArmy));
  });
  c.querySelectorAll('button[data-guard-army]').forEach(btn => {
    btn.onclick = () => toggleGuard(parseInt(btn.dataset.guardArmy));
  });
}

function closeAllPanels() {
  ['shop','inv','achPanel','armyPanel','hirePanel'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
  showInventory = false;
}

function toggleHirePanel() {
  const el = document.getElementById('hirePanel');
  const isOpen = el.style.display === 'block';
  closeAllPanels();
  if (!isOpen) {
    el.style.display = 'block';
    renderHirePanel();
  }
}
function toggleArmyPanel() {
  const el = document.getElementById('armyPanel');
  const isOpen = el.style.display === 'block';
  closeAllPanels();
  if (!isOpen) {
    el.style.display = 'block';
    renderArmyPanel();
  }
}
function toggleInventory() {
  const el = document.getElementById('inv');
  const isOpen = el.style.display === 'block';
  closeAllPanels();
  if (!isOpen) {
    el.style.display = 'block';
    renderInventory();
    showInventory = true;
  }
}
function toggleShop() {
  const el = document.getElementById('shop');
  const isOpen = el.style.display === 'block';
  closeAllPanels();
  if (!isOpen) {
    el.style.display = 'block';
    renderShop('buy');
  }
}
function toggleAchievements() {
  const el = document.getElementById('achPanel');
  const isOpen = el.style.display === 'block';
  closeAllPanels();
  if (!isOpen) {
    el.style.display = 'block';
    renderAchievements();
  }
}

// ============================================
// ==== INVENTORY ====
// ============================================
const ITEM_INFO = {
  wheat:      { emoji:'🌾', name:'Gandum', sellPrice:10 },
  corn:       { emoji:'🌽', name:'Jagung', sellPrice:25 },
  tomato:     { emoji:'🍅', name:'Tomat',  sellPrice:40 },
  wood:       { emoji:'🪵', name:'Kayu',   sellPrice:5 },
  food:       { emoji:'🍗', name:'Makanan', sellPrice:0, food:true, hunger:30 },
  seeds:      { emoji:'🌱', name:'Benih Gandum', sellPrice:0 },
  seeds_corn: { emoji:'🌱', name:'Benih Jagung', sellPrice:0 },
  seeds_tomato:{ emoji:'🌱', name:'Benih Tomat', sellPrice:0 },
  arrows:     { emoji:'🏹', name:'Panah',  sellPrice:2 },
  pelt:       { emoji:'🟫', name:'Kulit',  sellPrice:15 },
  fish:       { emoji:'🐟', name:'Ikan',   sellPrice:20, food:true, hunger:25 },
};

function renderInventory() {
  const grid = document.getElementById('invGrid');
  if (!grid) return;
  grid.innerHTML = '';
  Object.entries(inventory).forEach(([key, count]) => {
    if (count <= 0) return;
    const info = ITEM_INFO[key];
    if (!info) return;
    const slot = document.createElement('div');
    slot.className = 'invSlot';
    slot.innerHTML = `
      <div class="emoji">${info.emoji}</div>
      <div class="name">${info.name}</div>
      <div class="count">${count}</div>
    `;
    slot.onclick = () => {
      sfxClick();
      if (info.food) {
        const heal = info.hunger || 20;
        player.hunger = Math.min(player.hungerMax, player.hunger + heal);
        inventory[key]--;
        sfxEat();
        showToast(`🍗 +${heal} hunger`, '#5aff5a');
        updateHUD();
        renderInventory();
      } else if (info.sellPrice > 0) {
        gameGold += info.sellPrice * count;
        if (gameGold > stats.maxGold) stats.maxGold = gameGold;
        inventory[key] = 0;
        sfxSell();
        showToast(`💰 +${info.sellPrice * count}g`, '#ffd700');
        updateHUD();
        renderInventory();
        checkAchievements();
      }
    };
    grid.appendChild(slot);
  });
  if (grid.children.length === 0) {
    grid.innerHTML = '<div style="grid-column:span 5;text-align:center;color:#666;padding:20px">Inventory kosong</div>';
  }
}

// ============================================
// ==== SHOP ====
// ============================================
const SHOP_ITEMS = {
  buy: [
    { key:'seeds',        emoji:'🌱', name:'Benih Gandum', price:5,  desc:'Grow 400ms' },
    { key:'seeds_corn',   emoji:'🌱', name:'Benih Jagung', price:15, desc:'Grow 600ms' },
    { key:'seeds_tomato', emoji:'🌱', name:'Benih Tomat',  price:25, desc:'Grow 800ms' },
    { key:'food',         emoji:'🍗', name:'Makanan',      price:20, desc:'+30 hunger' },
    { key:'arrows',       emoji:'🏹', name:'Panah x5',     price:10, desc:'Buat bow' },
  ],
  sell: [
    { key:'wheat',  emoji:'🌾', name:'Gandum', price:10 },
    { key:'corn',   emoji:'🌽', name:'Jagung', price:25 },
    { key:'tomato', emoji:'🍅', name:'Tomat',  price:40 },
    { key:'wood',   emoji:'🪵', name:'Kayu',   price:5 },
    { key:'pelt',   emoji:'🟫', name:'Kulit',  price:15 },
    { key:'fish',   emoji:'🐟', name:'Ikan',   price:20 },
  ],
};

function renderShop(tab) {
  const c = document.getElementById('shopContent');
  if (!c) return;
  document.querySelectorAll('.shopTab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });

  if (tab === 'buy') {
    c.innerHTML = SHOP_ITEMS.buy.map(item => {
      const canAfford = gameGold >= item.price;
      return `
        <div class="shopItem">
          <div class="info">
            <div class="emoji">${item.emoji}</div>
            <div>
              <div class="name">${item.name}</div>
              <div class="price">🪙 ${item.price}</div>
              <div class="desc">${item.desc}</div>
            </div>
          </div>
          <button data-buy="${item.key}" data-price="${item.price}" ${canAfford ? '' : 'disabled'}>Beli</button>
        </div>
      `;
    }).join('');
  } else {
    c.innerHTML = SHOP_ITEMS.sell.map(item => {
      const have = inventory[item.key] || 0;
      return `
        <div class="shopItem">
          <div class="info">
            <div class="emoji">${item.emoji}</div>
            <div>
              <div class="name">${item.name}</div>
              <div class="price">🪙 ${item.price} each</div>
              <div class="desc">Punya: ${have}</div>
            </div>
          </div>
          <button data-sell="${item.key}" data-price="${item.price}" ${have > 0 ? '' : 'disabled'}>Jual 1</button>
        </div>
      `;
    }).join('');
  }

  c.querySelectorAll('button[data-buy]').forEach(btn => {
    btn.onclick = () => {
      const key = btn.dataset.buy;
      const price = parseInt(btn.dataset.price);
      if (gameGold < price) { sfxError(); return; }
      gameGold -= price;
      if (key === 'arrows') inventory.arrows = (inventory.arrows || 0) + 5;
      else inventory[key] = (inventory[key] || 0) + 1;
      stats.shopPurchases++;
      sfxBuy();
      showToast(`🛒 Beli ${key}`, '#5aff5a');
      updateHUD();
      renderShop('buy');
      checkAchievements();
    };
  });

  c.querySelectorAll('button[data-sell]').forEach(btn => {
    btn.onclick = () => {
      const key = btn.dataset.sell;
      const price = parseInt(btn.dataset.price);
      if ((inventory[key] || 0) <= 0) return;
      inventory[key]--;
      gameGold += price;
      if (gameGold > stats.maxGold) stats.maxGold = gameGold;
      sfxSell();
      showToast(`💰 +${price}g`, '#ffd700');
      updateHUD();
      renderShop('sell');
      checkAchievements();
    };
  });
}

// ============================================
// ==== ACHIEVEMENTS ====
// ============================================
function renderAchievements() {
  const grid = document.getElementById('achGrid');
  if (!grid) return;
  grid.innerHTML = '';
  Object.entries(achievements).forEach(([key, a]) => {
    const div = document.createElement('div');
    div.className = 'achItem' + (a.unlocked ? ' unlocked' : '');
    div.innerHTML = `
      <div class="emoji">${a.emoji}</div>
      <div>
        <div class="achName">${a.name}</div>
        <div class="achDesc">${a.desc}</div>
      </div>
    `;
    grid.appendChild(div);
  });
}

// ============================================
// ==== CROP GROWTH ====
// ============================================
function updateCrops(dt) {
  Object.entries(crops).forEach(([key, c]) => {
    if (!c || c.stage < 0 || c.stage >= 3) return;
    if (!c.watered) return;
    c.timer = (c.timer || 0) + dt * 16;
    if (c.timer >= (c.growTime || 400) / 3) {
      c.timer = 0;
      c.stage++;
      c.watered = false;
    }
  });
}

// ============================================
// ==== TOOLS ====
// ============================================
function useTool(worldX, worldY) {
  const tx = Math.floor(worldX / TILE);
  const ty = Math.floor(worldY / TILE);
  if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) return;
  const t = world[ty][tx];
  const key = `${tx},${ty}`;

  if (currentTool === 'hoe') {
    if (t === T_GRASS || t === T_FLOWER) {
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHoe();
    }
  } else if (currentTool === 'seed') {
    if (t === T_FARMLAND) {
      const seedKey = getSeedKey(currentSeed);
      if (inventory[seedKey] > 0) {
        inventory[seedKey]--;
        world[ty][tx] = T_CROP;
        const cropInfo = CROP_TYPES[currentSeed];
        crops[key] = { stage:0, watered:false, timer:0, type:currentSeed, growTime:cropInfo.growTime };
        stats.cropsPlanted.add(currentSeed);
        sfxSeed();
        updateHUD();
      } else {
        sfxError();
        showToast('❌ Benih habis!', '#ff4444');
      }
    }
  } else if (currentTool === 'water') {
    if (t === T_CROP && crops[key] && !crops[key].watered && crops[key].stage < 3) {
      crops[key].watered = true;
      sfxWater();
    }
  } else if (currentTool === 'harvest') {
    if (t === T_CROP && crops[key] && crops[key].stage >= 3) {
      const cropType = crops[key].type || 'wheat';
      inventory[cropType] = (inventory[cropType] || 0) + 1;
      stats.harvestCount++;
      world[ty][tx] = T_FARMLAND;
      crops[key] = { stage: -1 };
      sfxHarvest();
      showToast(`🌾 +1 ${CROP_TYPES[cropType].emoji}`, '#5aff5a');
      updateHUD();
      checkAchievements();
    }
  } else if (currentTool === 'axe') {
    if (t === T_TREE) {
      delete trees[key];
      world[ty][tx] = T_STUMP;
      inventory.wood = (inventory.wood || 0) + 3;
      stats.treesChopped++;
      sfxAxe();
      showToast('🪵 +3 kayu', '#5aff5a');
      updateHUD();
      checkAchievements();
    } else if (t === T_SAPLING) {
      world[ty][tx] = T_GRASS;
      inventory.wood = (inventory.wood || 0) + 1;
      sfxAxe();
      updateHUD();
    }
  } else if (currentTool === 'shovel') {
    if (t === T_FARMLAND || t === T_CROP) {
      delete crops[key];
      world[ty][tx] = T_GRASS;
      sfxShovel();
    } else if (t === T_STUMP) {
      world[ty][tx] = T_GRASS;
      sfxShovel();
    }
  } else if (currentTool === 'sword') {
    attackNearby(worldX, worldY);
  } else if (currentTool === 'bow') {
    if (inventory.arrows > 0) {
      inventory.arrows--;
      const dx = player.dir === 'right' ? 1 : player.dir === 'left' ? -1 : 0;
      const dy = player.dir === 'down' ? 1 : player.dir === 'up' ? -1 : 0;
      projectiles.push({
        x: player.x + 10, y: player.y + 10,
        vx: dx * 16, vy: dy * 16,
        life: 60, dmg: 12, fromPlayer: true,
      });
      sfxBowShoot();
      updateHUD();
    } else {
      sfxError();
      showToast('❌ Panah habis!', '#ff4444');
    }
  } else if (currentTool === 'rod') {
    startFishing(worldX, worldY);
  }
}

function attackNearby(wx, wy) {
  const tx = Math.floor(wx / TILE);
  const ty = Math.floor(wy / TILE);
  const animal = getAnimalAt(tx, ty);
  const wolf = getWolfAt(tx, ty);
  if (wolf) {
    wolf.hp -= 20;
    wolf.hurtFlash = 10;
    sfxSword();
    if (wolf.hp <= 0) {
      wolves = wolves.filter(w => w !== wolf);
      inventory.pelt = (inventory.pelt || 0) + 1;
      stats.wolvesKilled++;
      showToast('⚔️ Wolf dibunuh! +1 pelt', '#ff6666');
      updateHUD();
      checkAchievements();
    }
  } else if (animal && !animal.dead) {
    animal.hp -= 20;
    animal.hurtFlash = 10;
    sfxHit();
    if (animal.hp <= 0) {
      animal.dead = true;
      const t = ANIMAL_TYPES[animal.type];
      inventory.food = (inventory.food || 0) + t.dropAmt;
      stats.animalsKilled++;
      sfxAnimalHurt();
      showToast(`🍗 +${t.dropAmt} makanan`, '#5aff5a');
      updateHUD();
      checkAchievements();
    }
  } else {
    sfxHit();
  }
}

// ============================================
// ==== FISHING MINI-GAME ====
// ============================================
let fishing = { active:false, timer:0, duration:0, barPos:0, barDir:1, phase:'waiting' };

function startFishing(wx, wy) {
  const tx = Math.floor(wx / TILE);
  const ty = Math.floor(wy / TILE);
  let nearWaterTile = false;
  for (let dy=-1; dy<=1; dy++) {
    for (let dx=-1; dx<=1; dx++) {
      if (world[ty+dy] && world[ty+dy][tx+dx] === T_WATER) nearWaterTile = true;
    }
  }
  if (!nearWaterTile) {
    sfxError();
    showToast('❌ Harus di dekat air!', '#ff4444');
    return;
  }
  fishing.active = true;
  fishing.phase = 'waiting';
  fishing.timer = 0;
  fishing.duration = 1.5 + Math.random() * 2;
  document.getElementById('fishIndicator').style.display = 'block';
  document.getElementById('fishStatus').textContent = 'Menunggu ikan...';
  document.getElementById('fishBarFill').style.width = '0%';
  document.getElementById('fishHint').textContent = '';
  sfxFishCast();
}

function updateFishing(dt) {
  if (!fishing.active) return;
  fishing.timer += dt;
  const indicator = document.getElementById('fishIndicator');
  if (!indicator) return;

  if (fishing.phase === 'waiting') {
    if (fishing.timer >= fishing.duration) {
      fishing.phase = 'action';
      fishing.timer = 0;
      fishing.barPos = 0;
      fishing.barDir = 1;
      document.getElementById('fishStatus').textContent = '🐟 IKAN! Tekan SPASI!';
      document.getElementById('fishHint').textContent = 'SPASI untuk strike!';
      sfxFishBite();
    }
  } else if (fishing.phase === 'action') {
    fishing.barPos += fishing.barDir * dt * 120;
    if (fishing.barPos >= 100) { fishing.barPos = 100; fishing.barDir = -1; }
    if (fishing.barPos <= 0) { fishing.barPos = 0; fishing.barDir = 1; }
    document.getElementById('fishBarFill').style.width = fishing.barPos + '%';
    fishing.timer += dt;
    if (fishing.timer > 1.2) {
      fishing.active = false;
      indicator.style.display = 'none';
      sfxFishMiss();
      showToast('❌ Ikan lepas...', '#ff4444');
    }
  }
}

function fishingStrike() {
  if (!fishing.active || fishing.phase !== 'action') return;
  if (fishing.barPos >= 30 && fishing.barPos <= 70) {
    fishing.active = false;
    document.getElementById('fishIndicator').style.display = 'none';
    inventory.fish = (inventory.fish || 0) + 1;
    stats.fishCaught++;
    sfxFishCatch();
    showToast('🐟 +1 Ikan!', '#5aff5a');
    updateHUD();
    checkAchievements();
  } else {
    fishing.active = false;
    document.getElementById('fishIndicator').style.display = 'none';
    sfxFishMiss();
    showToast('❌ Meleset!', '#ff4444');
  }
}

// ============================================
// ==== WOLF AI ====
// ============================================
function updateWolves(dt) {
  wolves.forEach(w => {
    if (w.hurtFlash > 0) w.hurtFlash--;
    w.attackTimer -= dt;

    let target = null, targetDist = 99999;
    const dp = Math.hypot(player.x - w.x, player.y - w.y);
    if (dp < 400) { target = player; targetDist = dp; }
    army.forEach(s => {
      const d = Math.hypot(s.x - w.x, s.y - w.y);
      if (d < targetDist && d < 400) { target = s; targetDist = d; }
    });

    if (target) {
      if (targetDist < 40) {
        if (w.attackTimer <= 0) {
          w.attackTimer = 1.0;
          sfxWolfBite();
          if (target === player) {
            const dmg = Math.max(1, 8 - Math.floor((army.filter(s=>s.guard).length) * 2));
            player.hp -= dmg;
            flashDamage();
            sfxHurt();
            if (player.hp <= 0) {
              player.hp = player.hpMax;
              player.hunger = Math.max(10, player.hunger - 20);
              player.x = 20*TILE; player.y = 20*TILE;
              showToast('💀 Kamu tumbang! Respawn...', '#ff4444');
            }
            updateHUD();
          } else {
            const dmg = Math.max(1, 10 - (target.armor || 0));
            target.hp -= dmg;
            target.hurtFlash = 10;
            if (target.hp <= 0) {
              showToast(`💀 ${target.name} gugur!`, '#ff4444');
              army = army.filter(s => s !== target);
              updateHUD();
            }
          }
        }
      } else {
        const dx = (target.x - w.x) / targetDist * w.speed;
        const dy = (target.y - w.y) / targetDist * w.speed;
        if (canMoveTo(w.x + dx, w.y, 24, 24, world)) w.x += dx;
        if (canMoveTo(w.x, w.y + dy, 24, 24, world)) w.y += dy;
        if (Math.abs(dx) > Math.abs(dy)) w.dir = dx > 0 ? 'right' : 'left';
        else w.dir = dy > 0 ? 'down' : 'up';
        w.animTimer++;
        if (w.animTimer > 10) { w.animTimer = 0; w.walkFrame = (w.walkFrame + 1) % 4; }
      }
    } else {
      w.wanderTimer -= dt;
      if (w.wanderTimer <= 0) {
        w.wanderTimer = 2 + Math.random() * 3;
        w.wanderAngle = Math.random() * Math.PI * 2;
      }
      const dx = Math.cos(w.wanderAngle) * w.speed * 0.5;
      const dy = Math.sin(w.wanderAngle) * w.speed * 0.5;
      if (canMoveTo(w.x + dx, w.y, 24, 24, world)) w.x += dx;
      if (canMoveTo(w.x, w.y + dy, 24, 24, world)) w.y += dy;
      w.animTimer++;
      if (w.animTimer > 12) { w.animTimer = 0; w.walkFrame = (w.walkFrame + 1) % 4; }
    }
  });
}

// ============================================
// ==== ANIMALS ====
// ============================================
function updateAnimals(dt) {
  animals.forEach(a => {
    if (a.dead) return;
    if (a.hurtFlash > 0) a.hurtFlash--;

    a.wanderTimer -= dt;
    if (a.wanderTimer <= 0) {
      a.wanderTimer = 1.5 + Math.random() * 3;
      if (Math.random() < 0.4) {
        a.vx = 0; a.vy = 0;
      } else {
        const angle = Math.random() * Math.PI * 2;
        a.vx = Math.cos(angle) * a.speed;
        a.vy = Math.sin(angle) * a.speed;
      }
    }

    const dp = Math.hypot(player.x - a.x, player.y - a.y);
    if (dp < 120) {
      const dx = (a.x - player.x) / dp * a.speed * 2;
      const dy = (a.y - player.y) / dp * a.speed * 2;
      a.vx = dx; a.vy = dy;
    }

    if (canMoveTo(a.x + a.vx, a.y, 20, 20, world)) a.x += a.vx;
    else a.vx = 0;
    if (canMoveTo(a.x, a.y + a.vy, 20, 20, world)) a.y += a.vy;
    else a.vy = 0;

    if (Math.abs(a.vx) > Math.abs(a.vy)) a.dir = a.vx > 0 ? 'right' : 'left';
    else if (a.vy !== 0) a.dir = a.vy > 0 ? 'down' : 'up';

    a.animTimer++;
    if (a.animTimer > 12) { a.animTimer = 0; a.walkFrame = (a.walkFrame + 1) % 4; }
  });

  if (animals.length < 6 && Math.random() < 0.001) {
    spawnSingleAnimal(['rabbit','chicken','cow'][Math.floor(Math.random()*3)]);
  }
}

// ============================================
// ==== PROJECTILES ====
// ============================================
function updateProjectiles(dt) {
  projectiles.forEach(p => {
    p.x += p.vx; p.y += p.vy;
    p.life--;
    wolves.forEach(w => {
      if (Math.abs(w.x - p.x) < 24 && Math.abs(w.y - p.y) < 24) {
        w.hp -= p.dmg;
        w.hurtFlash = 10;
        p.life = 0;
        sfxArrowHit();
        if (w.hp <= 0) {
          wolves = wolves.filter(wl => wl !== w);
          inventory.pelt = (inventory.pelt || 0) + 1;
          stats.wolvesKilled++;
          showToast('🏹 Wolf dibunuh! +1 pelt', '#ff6666');
          updateHUD();
          checkAchievements();
        }
      }
    });
    if (p.fromPlayer) {
      animals.forEach(a => {
        if (a.dead) return;
        if (Math.abs(a.x - p.x) < 24 && Math.abs(a.y - p.y) < 24) {
          a.hp -= p.dmg;
          a.hurtFlash = 10;
          p.life = 0;
          if (a.hp <= 0) {
            a.dead = true;
            const t = ANIMAL_TYPES[a.type];
            inventory.food = (inventory.food || 0) + t.dropAmt;
            stats.animalsKilled++;
            showToast(`🏹 +${t.dropAmt} makanan`, '#5aff5a');
            updateHUD();
            checkAchievements();
          }
        }
      });
    }
  });
  projectiles = projectiles.filter(p => p.life > 0);
}

// ============================================
// ==== NPC ====
// ============================================
function updateNPCs(dt) {
  npcs.forEach(n => {
    n.moveTimer -= dt;
    if (n.moveTimer <= 0) {
      n.moveTimer = 3 + Math.random() * 5;
      n.targetX = n.x / TILE + (Math.random() - 0.5) * 6;
      n.targetY = n.y / TILE + (Math.random() - 0.5) * 6;
      n.targetX = Math.max(2, Math.min(WORLD_W - 2, n.targetX));
      n.targetY = Math.max(2, Math.min(WORLD_H - 2, n.targetY));
    }
    const dx = n.targetX * TILE - n.x;
    const dy = n.targetY * TILE - n.y;
    const d = Math.hypot(dx, dy);
    if (d > 8) {
      const nx = dx / d * n.speed;
      const ny = dy / d * n.speed;
      if (canMoveTo(n.x + nx, n.y, 20, 28, world)) n.x += nx;
      if (canMoveTo(n.x, n.y + ny, 20, 28, world)) n.y += ny;
      if (Math.abs(nx) > Math.abs(ny)) n.dir = nx > 0 ? 'right' : 'left';
      else n.dir = ny > 0 ? 'down' : 'up';
      n.animTimer++;
      if (n.animTimer > 12) { n.animTimer = 0; n.walkFrame = (n.walkFrame + 1) % 4; }
    }
  });
}

// ============================================
// ==== PLAYER ====
// ============================================
const keys = {};
window.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  const k = e.key.toLowerCase();
  if (k >= '1' && k <= '9') {
    const tools = ['hoe','seed','water','harvest','axe','sword','bow','rod','shovel'];
    setTool(tools[parseInt(k)-1]);
  }
  if (k === 'h') { ensureAudio(); toggleHirePanel(); }
  if (k === 'r') { ensureAudio(); toggleArmyPanel(); }
  if (k === 'i') { ensureAudio(); toggleInventory(); }
  if (k === 'b') { ensureAudio(); toggleShop(); }
  if (k === 'e') {
    ensureAudio();
    if (nearBed) sleep();
    if (nearDoor) {
      if (!currentInterior) {
        currentInterior = interiors[0];
        player.x = currentInterior.playerSpawn.x;
        player.y = currentInterior.playerSpawn.y;
        // SNAP KAMERA
        camera.x = player.x + player.w/2 - canvas.width/2;
        camera.y = player.y + player.h/2 - canvas.height/2;
        sfxDoor();
        showToast('🚪 Masuk ke rumah', '#4a90e2');
      } else {
        currentInterior = null;
        player.x = 17.5 * TILE;
        player.y = 13 * TILE;
        // SNAP KAMERA
        camera.x = player.x + player.w/2 - canvas.width/2;
        camera.y = player.y + player.h/2 - canvas.height/2;
        sfxDoor();
        showToast('🚪 Keluar rumah', '#4a90e2');
      }
    }
  }
  if (k === 'escape') {
    closeAllPanels();
    cancelPlacement();
    setTool(null);
  }
  if (k === ' ') {
    e.preventDefault();
    fishingStrike();
  }
  if (['arrowup','arrowdown','arrowleft','arrowright'].includes(e.key.toLowerCase())) {
    e.preventDefault();
  }
});
window.addEventListener('keyup', e => {
  keys[e.key.toLowerCase()] = false;
});

function setTool(tool) {
  currentTool = tool;
  document.querySelectorAll('.tool').forEach(t => {
    t.classList.toggle('active', t.dataset.tool === tool);
  });
  const seedWrap = document.getElementById('seedPickerWrap');
  if (seedWrap) seedWrap.style.display = tool === 'seed' ? 'block' : 'none';
}

function updatePlayer(dt) {
  if (placementMode) return;

  let dx = 0, dy = 0;
  if (keys['w'] || keys['arrowup']) dy = -1;
  if (keys['s'] || keys['arrowdown']) dy = 1;
  if (keys['a'] || keys['arrowleft']) dx = -1;
  if (keys['d'] || keys['arrowright']) dx = 1;

  if (dx && dy) { dx *= 0.707; dy *= 0.707; }

  const speed = player.speed * 1.4;
  if (dx !== 0 || dy !== 0) {
    const nx = dx * speed;
    const ny = dy * speed;
    if (canMoveTo(player.x + nx, player.y, player.w, player.h, getActiveWorld())) player.x += nx;
    if (canMoveTo(player.x, player.y + ny, player.w, player.h, getActiveWorld())) player.y += ny;
    if (Math.abs(dx) > Math.abs(dy)) player.dir = dx > 0 ? 'right' : 'left';
    else if (dy !== 0) player.dir = dy > 0 ? 'down' : 'up';
    player.animTimer++;
    if (player.animTimer > 8) { player.animTimer = 0; player.walkFrame = (player.walkFrame + 1) % 4; }
  } else {
    player.walkFrame = 0;
  }

  player.x = Math.max(0, Math.min(WORLD_W*TILE - player.w, player.x));
  player.y = Math.max(0, Math.min(WORLD_H*TILE - player.h, player.y));

  const ptx = Math.floor((player.x + player.w/2) / TILE);
  const pty = Math.floor((player.y + player.h/2) / TILE);
  nearBed = false; nearDoor = false; nearShop = false; nearWater = false;

  const aw = getActiveWorld();
  if (aw[pty] && aw[pty][ptx] === T_BED) nearBed = true;
  if (aw[pty] && aw[pty][ptx] === T_HOUSE_DOOR) nearDoor = true;
  if (world[pty] && world[pty][ptx] === T_SHOP) nearShop = true;
  
  for (let dy2=-1; dy2<=1; dy2++) {
    for (let dx2=-1; dx2<=1; dx2++) {
      if (aw[pty+dy2] && aw[pty+dy2][ptx+dx2] === T_WATER) nearWater = true;
    }
  }

  const bp = document.getElementById('bedPrompt');
  if (bp) bp.style.display = (nearBed && currentInterior) ? 'block' : 'none';
  
  const dp = document.getElementById('doorPrompt');
  if (dp) dp.style.display = nearDoor ? 'block' : 'none';
}

function sleep() {
  sfxSleep();
  const h = (time.totalMinutes/60) % 24;
  if (h >= 20 || h < 6) {
    time.day++;
    time.totalMinutes = 6 * 60;
    player.hp = player.hpMax;
    player.hunger = Math.min(player.hungerMax, player.hunger + 40);
    stats.sleepCount++;
    showToast(`🌅 Hari ${time.day}! HP & hunger pulih.`, '#5aff5a');
    checkAchievements();
  } else {
    showToast('😴 Belum waktunya tidur (malam hari)', '#ffaa55');
  }
  updateHUD();
}

let mouseX = 0, mouseY = 0;
canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  mouseX = (e.clientX - rect.left) * scaleX;
  mouseY = (e.clientY - rect.top) * scaleY;

  if (placementMode) {
    const wx = mouseX + camera.x;
    const wy = mouseY + camera.y;
    placementPreviewX = Math.floor(wx / TILE) - 1;
    placementPreviewY = Math.floor(wy / TILE) - 1;
  }
});

canvas.addEventListener('click', e => {
  ensureAudio();
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const mx = (e.clientX - rect.left) * scaleX;
  const my = (e.clientY - rect.top) * scaleY;
  const wx = mx + camera.x;
  const wy = my + camera.y;

  if (placementMode) {
    const fx = Math.floor(wx / TILE) - 1;
    const fy = Math.floor(wy / TILE) - 1;
    if (tryPlaceFarmArea(fx, fy)) {
      cancelPlacement();
    }
    return;
  }

  for (const n of npcs) {
    if (Math.abs(n.x - wx) < 30 && Math.abs(n.y - wy) < 30) {
      showDialog(`${n.name}: ${n.dialog}`);
      return;
    }
  }

  if (currentTool) {
    useTool(wx, wy);
  }
});

canvas.addEventListener('contextmenu', e => {
  e.preventDefault();
  if (placementMode) cancelPlacement();
});

// ============================================
// ==== RENDERING ====
// ============================================
function drawTile(t, sx, sy) {
  if (t === T_GRASS) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#4a8d4a';
    ctx.fillRect(sx+4, sy+4, 8, 8);
    ctx.fillRect(sx+18, sy+14, 6, 6);
  } else if (t === T_PATH) {
    ctx.fillStyle = '#8a7a5a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#9a8a6a';
    ctx.fillRect(sx+2, sy+2, 28, 28);
  } else if (t === T_WATER) {
    ctx.fillStyle = '#2a5a9a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#3a6aaa';
    const wave = Math.sin(Date.now()/500 + sx/20) * 4;
    ctx.fillRect(sx+6, sy+10+wave, 20, 4);
    ctx.fillRect(sx+10, sy+20+wave, 12, 4);
  } else if (t === T_TREE) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+12, sy+16, 8, 16);
    ctx.fillStyle = '#2a6d2a';
    ctx.fillRect(sx+4, sy+4, 24, 20);
    ctx.fillStyle = '#3a8d3a';
    ctx.fillRect(sx+8, sy+6, 16, 12);
  } else if (t === T_FARMLAND) {
    ctx.fillStyle = '#6a4a2a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#7a5a3a';
    ctx.fillRect(sx+4, sy+6, 24, 4);
    ctx.fillRect(sx+4, sy+16, 24, 4);
    ctx.fillRect(sx+4, sy+26, 24, 4);
  } else if (t === T_CROP) {
    ctx.fillStyle = '#6a4a2a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#7a5a3a';
    ctx.fillRect(sx+4, sy+26, 24, 4);
  } else if (t === T_HOUSE) {
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#aa8a6a';
    ctx.fillRect(sx+2, sy+2, 28, 28);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx, sy, 32, 8);
  } else if (t === T_HOUSE_DOOR) {
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+4, sy+8, 24, 24);
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(sx+22, sy+20, 4, 4);
  } else if (t === T_FLOWER) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    const colors = ['#ff6b6b', '#ffed4a', '#4a90e2', '#ff69b4'];
    ctx.fillStyle = colors[(sx+sy) % colors.length];
    ctx.fillRect(sx+10, sy+10, 12, 12);
    ctx.fillStyle = '#fff';
    ctx.fillRect(sx+14, sy+14, 4, 4);
  } else if (t === T_LAMP) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+14, sy+12, 6, 20);
    ctx.fillStyle = '#ffed4a';
    ctx.fillRect(sx+10, sy+4, 14, 14);
    ctx.fillStyle = '#fff8a0';
    ctx.fillRect(sx+12, sy+6, 10, 10);
  } else if (t === T_STUMP) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+8, sy+16, 16, 12);
    ctx.fillStyle = '#7a5a3a';
    ctx.fillRect(sx+10, sy+18, 12, 8);
  } else if (t === T_SAPLING) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+14, sy+16, 4, 10);
    ctx.fillStyle = '#2a6d2a';
    ctx.fillRect(sx+10, sy+8, 12, 10);
  } else if (t === T_BED) {
    ctx.fillStyle = '#4a4a6a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#6a6a9a';
    ctx.fillRect(sx+4, sy+4, 24, 24);
    ctx.fillStyle = '#fff';
    ctx.fillRect(sx+6, sy+6, 20, 10);
  } else if (t === T_INTERIOR_FLOOR) {
    ctx.fillStyle = '#6a5a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#7a6a5a';
    ctx.fillRect(sx+2, sy+2, 28, 28);
  } else if (t === T_WALL) {
    ctx.fillStyle = '#4a3a2a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a4a3a';
    ctx.fillRect(sx+2, sy+2, 28, 28);
  } else if (t === T_TABLE) {
    ctx.fillStyle = '#6a5a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx+2, sy+2, 28, 28);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+4, sy+4, 24, 6);
  } else if (t === T_SHOP) {
    ctx.fillStyle = '#5a4a3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx+2, sy+2, 28, 28);
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(sx+6, sy+6, 20, 10);
    ctx.fillStyle = '#fff';
    ctx.font = '16px monospace';
    ctx.fillText('$', sx+12, sy+16);
  } else if (t === T_CAMP) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a5a3a';
    ctx.fillRect(sx+6, sy+10, 20, 16);
    ctx.fillStyle = '#aa7a5a';
    ctx.fillRect(sx+10, sy+6, 12, 12);
  } else if (t === T_FENCE) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a5a2a';
    ctx.fillRect(sx+4, sy+4, 24, 24);
    ctx.fillStyle = '#aa7a4a';
    ctx.fillRect(sx+8, sy+8, 16, 16);
    ctx.fillStyle = '#6a4a1a';
    ctx.fillRect(sx+12, sy+12, 8, 8);
  }
}

function drawCrop(key, c, sx, sy) {
  if (c.stage < 0) return;
  const cropInfo = CROP_TYPES[c.type] || CROP_TYPES.wheat;
  if (c.stage === 0) {
    ctx.fillStyle = '#5aff5a';
    ctx.fillRect(sx+14, sy+20, 4, 6);
  } else if (c.stage === 1) {
    ctx.fillStyle = '#5aff5a';
    ctx.fillRect(sx+12, sy+14, 8, 12);
    ctx.fillStyle = '#7aff7a';
    ctx.fillRect(sx+14, sy+10, 4, 6);
  } else if (c.stage === 2) {
    ctx.fillStyle = '#5aff5a';
    ctx.fillRect(sx+10, sy+8, 12, 18);
    ctx.fillStyle = '#7aff7a';
    ctx.fillRect(sx+12, sy+4, 8, 8);
  } else if (c.stage >= 3) {
    ctx.fillStyle = cropInfo.color;
    ctx.fillRect(sx+8, sy+4, 16, 24);
    ctx.fillStyle = '#fff';
    ctx.fillRect(sx+10, sy+6, 4, 4);
    ctx.fillRect(sx+18, sy+10, 4, 4);
    ctx.fillStyle = 'rgba(255,255,100,0.3)';
    ctx.fillRect(sx+4, sy, 24, 32);
  }
}

function drawPlayer(x, y) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(x-4, y+24, 28, 8);
  
  ctx.fillStyle = '#4a90e2';
  ctx.fillRect(x, y+12, 20, 16);
  ctx.fillStyle = '#3a70b2';
  ctx.fillRect(x, y+20, 20, 8);
  
  ctx.fillStyle = '#f0c8a0';
  ctx.fillRect(x+2, y, 16, 14);
  ctx.fillStyle = '#3a2a1a';
  ctx.fillRect(x, y-2, 20, 8);
  
  const eyeX = player.dir === 'left' ? 2 : player.dir === 'right' ? 14 : 6;
  ctx.fillStyle = '#000';
  ctx.fillRect(x+eyeX, y+6, 4, 4);
  if (player.dir !== 'left' && player.dir !== 'right') {
    ctx.fillRect(x+eyeX+6, y+6, 4, 4);
  }
  
  const legOff = player.walkFrame === 1 ? -2 : player.walkFrame === 3 ? 2 : 0;
  ctx.fillStyle = '#2a2a3e';
  ctx.fillRect(x+2+legOff, y+28, 6, 6);
  ctx.fillRect(x+12-legOff, y+28, 6, 6);
}

function drawWorker(w) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(w.x-4, w.y+24, 28, 8);
  
  ctx.fillStyle = w.shirt;
  ctx.fillRect(w.x, w.y+12, 20, 16);
  ctx.fillStyle = w.color;
  ctx.fillRect(w.x, w.y+20, 20, 8);
  
  ctx.fillStyle = '#f0c8a0';
  ctx.fillRect(w.x+2, w.y, 16, 14);
  ctx.fillStyle = '#8a6a2a';
  ctx.fillRect(w.x, w.y-2, 20, 8);
  
  ctx.fillStyle = '#000';
  ctx.fillRect(w.x+6, w.y+6, 4, 4);
  ctx.fillRect(w.x+12, w.y+6, 4, 4);
  
  const legOff = w.walkFrame === 1 ? -2 : w.walkFrame === 3 ? 2 : 0;
  ctx.fillStyle = '#2a2a3e';
  ctx.fillRect(w.x+2+legOff, w.y+28, 6, 6);
  ctx.fillRect(w.x+12-legOff, w.y+28, 6, 6);
}

function drawSoldier(s) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(s.x-4, s.y+24, 28, 8);
  
  if (s.hurtFlash > 0) {
    ctx.fillStyle = '#ff8888';
    ctx.fillRect(s.x, s.y, 20, 32);
    return;
  }
  
  ctx.fillStyle = s.armorColor || '#888';
  ctx.fillRect(s.x, s.y+12, 20, 16);
  ctx.fillStyle = s.shirt;
  ctx.fillRect(s.x+2, s.y+14, 16, 12);
  
  ctx.fillStyle = '#f0c8a0';
  ctx.fillRect(s.x+2, s.y, 16, 14);
  ctx.fillStyle = s.color;
  ctx.fillRect(s.x, s.y-2, 20, 8);
  
  if (s.type === 'archer') {
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(s.x+18, s.y+8, 4, 16);
  } else if (s.type === 'knight') {
    ctx.fillStyle = '#c0c0c0';
    ctx.fillRect(s.x-4, s.y+10, 4, 20);
    ctx.fillRect(s.x+20, s.y+10, 4, 20);
  } else {
    ctx.fillStyle = '#ccc';
    ctx.fillRect(s.x+18, s.y+4, 4, 20);
    ctx.fillStyle = '#8a5a2a';
    ctx.fillRect(s.x+18, s.y+22, 8, 4);
  }
  
  if (s.guard) {
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(s.x+6, s.y-12, 8, 8);
  }
}

function drawAnimal(a) {
  if (a.dead) return;
  const info = ANIMAL_TYPES[a.type];
  ctx.fillStyle = 'rgba(0,0,0,0.2)';
  ctx.fillRect(a.x-2, a.y+16, 24, 6);
  
  let color = info.color;
  if (a.hurtFlash > 0) color = '#ff8888';
  ctx.fillStyle = color;
  ctx.fillRect(a.x, a.y+6, 20, 14);
  ctx.fillRect(a.x+4, a.y, 12, 10);
  
  ctx.fillStyle = '#000';
  ctx.fillRect(a.x+6, a.y+2, 2, 2);
  ctx.fillRect(a.x+12, a.y+2, 2, 2);
  
  const legOff = a.walkFrame === 1 ? -2 : a.walkFrame === 3 ? 2 : 0;
  ctx.fillStyle = color;
  ctx.fillRect(a.x+2+legOff, a.y+18, 4, 6);
  ctx.fillRect(a.x+14-legOff, a.y+18, 4, 6);
}

function drawWolf(w) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(w.x-4, w.y+16, 32, 8);
  
  let color = '#6a6a7a';
  if (w.hurtFlash > 0) color = '#ff8888';
  ctx.fillStyle = color;
  ctx.fillRect(w.x, w.y+6, 24, 16);
  ctx.fillRect(w.x+6, w.y, 14, 10);
  
  ctx.fillRect(w.x+6, w.y-4, 4, 6);
  ctx.fillRect(w.x+16, w.y-4, 4, 6);
  
  ctx.fillStyle = '#ff4444';
  ctx.fillRect(w.x+8, w.y+4, 4, 4);
  ctx.fillRect(w.x+14, w.y+4, 4, 4);
  
  const legOff = w.walkFrame === 1 ? -2 : w.walkFrame === 3 ? 2 : 0;
  ctx.fillStyle = color;
  ctx.fillRect(w.x+2+legOff, w.y+20, 6, 6);
  ctx.fillRect(w.x+16-legOff, w.y+20, 6, 6);
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  const aw = getActiveWorld();
  const startX = Math.floor(camera.x / TILE);
  const startY = Math.floor(camera.y / TILE);
  const endX = Math.min(startX + Math.ceil(canvas.width / TILE) + 1, aw[0].length);
  const endY = Math.min(startY + Math.ceil(canvas.height / TILE) + 1, aw.length);

  for (let ty = startY; ty < endY; ty++) {
    for (let tx = startX; tx < endX; tx++) {
      if (!aw[ty] || aw[ty][tx] === undefined) continue;
      const sx = tx * TILE - camera.x;
      const sy = ty * TILE - camera.y;
      drawTile(aw[ty][tx], sx, sy);
      
      const key = `${tx},${ty}`;
      if (crops[key] && aw[ty][tx] === T_CROP) {
        drawCrop(key, crops[key], sx, sy);
      }
    }
  }

  if (placementMode) {
    const fx = placementPreviewX, fy = placementPreviewY;
    let valid = true;
    for (let dy = 0; dy < FARM_AREA_H; dy++) {
      for (let dx = 0; dx < FARM_AREA_W; dx++) {
        const tx = fx + dx, ty = fy + dy;
        if (tx < 0 || ty < 0 || tx >= WORLD_W || ty >= WORLD_H) { valid = false; break; }
        const t = world[ty][tx];
        if (t !== T_GRASS && t !== T_FLOWER) { valid = false; break; }
      }
      if (!valid) break;
    }
    if (valid && isFarmAreaOverlap(fx, fy)) valid = false;
    
    ctx.fillStyle = valid ? 'rgba(90,255,90,0.3)' : 'rgba(255,80,80,0.3)';
    ctx.strokeStyle = valid ? '#5aff5a' : '#ff4444';
    ctx.lineWidth = 2;
    for (let dy = 0; dy < FARM_AREA_H; dy++) {
      for (let dx = 0; dx < FARM_AREA_W; dx++) {
        const sx = (fx + dx) * TILE - camera.x;
        const sy = (fy + dy) * TILE - camera.y;
        ctx.fillRect(sx, sy, TILE, TILE);
        ctx.strokeRect(sx, sy, TILE, TILE);
      }
    }
  }

  npcs.forEach(n => {
    const sx = n.x - camera.x, sy = n.y - camera.y;
    if (sx < -100 || sx > canvas.width + 100 || sy < -100 || sy > canvas.height + 100) return;
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(sx-4, sy+24, 28, 8);
    ctx.fillStyle = n.color;
    ctx.fillRect(sx, sy+12, 20, 16);
    ctx.fillStyle = '#f0c8a0';
    ctx.fillRect(sx+2, sy, 16, 14);
    ctx.fillStyle = '#000';
    ctx.fillRect(sx+6, sy+6, 4, 4);
    ctx.fillRect(sx+12, sy+6, 4, 4);
    ctx.fillStyle = '#fff';
    ctx.font = '16px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(n.name, sx+10, sy-8);
    ctx.textAlign = 'left';
  });

  animals.forEach(a => {
    const sx = a.x - camera.x, sy = a.y - camera.y;
    if (sx < -100 || sx > canvas.width + 100 || sy < -100 || sy > canvas.height + 100) return;
    drawAnimal({ ...a, x: sx, y: sy });
  });

  workers.forEach(w => {
    const sx = w.x - camera.x, sy = w.y - camera.y;
    if (sx < -100 || sx > canvas.width + 100 || sy < -100 || sy > canvas.height + 100) return;
    drawWorker({ ...w, x: sx, y: sy });
  });

  army.forEach(s => {
    const sx = s.x - camera.x, sy = s.y - camera.y;
    if (sx < -100 || sx > canvas.width + 100 || sy < -100 || sy > canvas.height + 100) return;
    drawSoldier({ ...s, x: sx, y: sy });
  });

  wolves.forEach(w => {
    const sx = w.x - camera.x, sy = w.y - camera.y;
    if (sx < -100 || sx > canvas.width + 100 || sy < -100 || sy > canvas.height + 100) return;
    drawWolf({ ...w, x: sx, y: sy });
  });

  projectiles.forEach(p => {
    const sx = p.x - camera.x, sy = p.y - camera.y;
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(sx-2, sy-2, 6, 6);
  });

  const psx = player.x - camera.x;
  const psy = player.y - camera.y;
  drawPlayer(psx, psy);

  const darkness = getDarkness();
  if (darkness > 0) {
    ctx.fillStyle = `rgba(10,10,40,${darkness})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    for (let ty = startY; ty < endY; ty++) {
      for (let tx = startX; tx < endX; tx++) {
        if (aw[ty] && aw[ty][tx] === T_LAMP) {
          const lx = tx * TILE - camera.x + 16;
          const ly = ty * TILE - camera.y + 16;
          const grad = ctx.createRadialGradient(lx, ly, 0, lx, ly, 120);
          grad.addColorStop(0, 'rgba(255,237,74,0.3)');
          grad.addColorStop(1, 'rgba(255,237,74,0)');
          ctx.fillStyle = grad;
          ctx.fillRect(lx-120, ly-120, 240, 240);
        }
      }
    }
    
    const pgrad = ctx.createRadialGradient(psx+10, psy+10, 0, psx+10, psy+10, 100);
    pgrad.addColorStop(0, 'rgba(255,255,200,0.15)');
    pgrad.addColorStop(1, 'rgba(255,255,200,0)');
    ctx.fillStyle = pgrad;
    ctx.fillRect(psx-100, psy-100, 220, 220);
  }

  const tod = getTimeOfDay();
  const tint = skyColors[tod];
  if (tint && tint !== 'rgba(255,255,255,0.0)') {
    ctx.fillStyle = tint;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
}

// ============================================
// ==== HUD UPDATE ====
// ============================================
function updateHUD() {
  const hpFill = document.getElementById('hpFill');
  const hungerFill = document.getElementById('hungerFill');
  const hpText = document.getElementById('hpText');
  const hungerText = document.getElementById('hungerText');
  const goldEl = document.getElementById('gold');
  const timeOfDay = document.getElementById('timeOfDay');
  const dayNum = document.getElementById('dayNum');
  const clock = document.getElementById('clock');
  const workerCount = document.getElementById('workerCount');
  const armyCount = document.getElementById('armyCount');
  const guardCount = document.getElementById('guardCount');
  const woodEl = document.getElementById('wood');
  const foodEl = document.getElementById('food');
  const wheatEl = document.getElementById('wheat');
  const arrowsEl = document.getElementById('arrows');

  if (hpFill) hpFill.style.width = Math.max(0, player.hp / player.hpMax * 100) + '%';
  if (hungerFill) hungerFill.style.width = Math.max(0, player.hunger / player.hungerMax * 100) + '%';
  if (hpText) hpText.textContent = `${Math.max(0, Math.round(player.hp))}/${player.hpMax}`;
  if (hungerText) hungerText.textContent = `${Math.max(0, Math.round(player.hunger))}/${player.hungerMax}`;
  if (goldEl) goldEl.textContent = gameGold;
  
  const tod = getTimeOfDay();
  const todEmoji = { dawn:'🌅', day:'☀️', evening:'🌇', night:'🌙' };
  if (timeOfDay) timeOfDay.textContent = `${todEmoji[tod]} ${tod.charAt(0).toUpperCase() + tod.slice(1)}`;
  if (dayNum) dayNum.textContent = time.day;
  if (clock) clock.textContent = getClockString();
  
  if (workerCount) workerCount.textContent = workers.length;
  if (armyCount) armyCount.textContent = army.length;
  if (guardCount) guardCount.textContent = army.filter(s => s.guard).length;
  
  if (woodEl) woodEl.textContent = inventory.wood || 0;
  if (foodEl) foodEl.textContent = inventory.food || 0;
  if (wheatEl) wheatEl.textContent = inventory.wheat || 0;
  if (arrowsEl) arrowsEl.textContent = inventory.arrows || 0;
}

// ============================================
// ==== SAVE / LOAD ====
// ============================================
function saveGame() {
  try {
    const saveData = {
      version: 15,
      player: { x: player.x, y: player.y, hp: player.hp, hunger: player.hunger },
      time: { totalMinutes: time.totalMinutes, day: time.day },
      inventory: { ...inventory },
      gold: gameGold,
      autoSell: autoSell,
      stats: {
        harvestCount: stats.harvestCount,
        fishCaught: stats.fishCaught,
        animalsKilled: stats.animalsKilled,
        wolvesKilled: stats.wolvesKilled,
        treesChopped: stats.treesChopped,
        shopPurchases: stats.shopPurchases,
        sleepCount: stats.sleepCount,
        maxGold: stats.maxGold,
        workersHired: stats.workersHired,
        soldiersRecruited: stats.soldiersRecruited,
      },
      achievements: Object.fromEntries(
        Object.entries(achievements).map(([k, v]) => [k, v.unlocked])
      ),
      world: world,
      crops: crops,
      workers: workers.map(w => ({
        x: w.x, y: w.y, farmArea: w.farmArea, currentCropType: w.currentCropType,
      })),
    };
    localStorage.setItem('pixelFarmRPG_v15', JSON.stringify(saveData));
    sfxSave();
    showSaveIndicator();
  } catch (e) {
    console.warn('Save error:', e);
  }
}

function loadGame() {
  try {
    const raw = localStorage.getItem('pixelFarmRPG_v15');
    if (!raw) return false;
    const data = JSON.parse(raw);
    if (!data || data.version !== 15) return false;
    
    player.x = data.player.x;
    player.y = data.player.y;
    player.hp = data.player.hp;
    player.hunger = data.player.hunger;
    time.totalMinutes = data.time.totalMinutes;
    time.day = data.time.day;
    Object.assign(inventory, data.inventory);
    gameGold = data.gold;
    autoSell = data.autoSell || false;
    Object.assign(stats, data.stats);
    if (data.achievements) {
      Object.entries(data.achievements).forEach(([k, v]) => {
        if (achievements[k]) achievements[k].unlocked = v;
      });
    }
    if (data.world) world = data.world;
    if (data.crops) {
      Object.keys(crops).forEach(k => delete crops[k]);
      Object.assign(crops, data.crops);
    }
    if (data.workers) {
      workers.length = 0;
      data.workers.forEach((w, i) => {
        workers.push({
          x: w.x, y: w.y, w: 20, h: 28,
          name: `Petani #${i+1}`,
          color: '#8b6f47', shirt: '#5a8a3a',
          speed: 1.2, actionDelay: 1.5, actionTimer: 0,
          dir: 'down', animTimer: 0, walkFrame: 0,
          state: 'idle', targetTile: null,
          salary: 5, salaryTimer: 60,
          currentCropType: w.currentCropType || 'wheat',
          farmArea: w.farmArea,
        });
      });
    }
    return true;
  } catch (e) {
    console.warn('Load error:', e);
    return false;
  }
}

function showSaveIndicator() {
  const el = document.getElementById('saveIndicator');
  if (!el) return;
  el.style.display = 'block';
  clearTimeout(el._timeout);
  el._timeout = setTimeout(() => el.style.display = 'none', 1500);
}

// ============================================
// ==== MAIN LOOP ====
// ============================================
let lastTime = performance.now();
function gameLoop(now) {
  const dt = Math.min(0.05, (now - lastTime) / 1000);
  lastTime = now;

  time.totalMinutes += dt * time.minutesPerSecond;
  if (time.totalMinutes >= 24 * 60) {
    time.totalMinutes -= 24 * 60;
    time.day++;
    checkAchievements();
  }

  player.hunger -= dt * 0.5;
  if (player.hunger <= 0) {
    player.hp -= dt * 2;
    if (player.hp <= 0) {
      player.hp = player.hpMax;
      player.hunger = 50;
      player.x = 20*TILE; player.y = 20*TILE;
      showToast('💀 Kelaparan! Respawn...', '#ff4444');
    }
  }
  player.hunger = Math.max(0, player.hunger);
  player.hp = Math.min(player.hpMax, player.hp);

  updatePlayer(dt);
  updateWorkers(dt);
  updateArmy(dt);
  updateWolves(dt);
  updateAnimals(dt);
  updateCrops(dt);
  updateProjectiles(dt);
  updateNPCs(dt);
  updateFishing(dt);

  const h = (time.totalMinutes/60) % 24;
  if ((h >= 20 || h < 5) && wolves.length < 4 && Math.random() < 0.002) {
    spawnWolf();
  }

  const targetCamX = player.x + player.w/2 - canvas.width/2;
  const targetCamY = player.y + player.h/2 - canvas.height/2;
  camera.x += (targetCamX - camera.x) * 0.1;
  camera.y += (targetCamY - camera.y) * 0.1;
  camera.x = Math.max(0, Math.min(WORLD_W*TILE - canvas.width, camera.x));
  camera.y = Math.max(0, Math.min(WORLD_H*TILE - canvas.height, camera.y));

  render();
  updateHUD();

  if (dialogTimer > 0) {
    dialogTimer--;
    if (dialogTimer <= 0) {
      const d = document.getElementById('dialog');
      if (d) d.style.display = 'none';
    }
  }

  requestAnimationFrame(gameLoop);
}

// ============================================
// ==== EVENT LISTENERS ====
// ============================================
document.querySelectorAll('.tool').forEach(t => {
  t.addEventListener('click', () => {
    ensureAudio();
    sfxClick();
    setTool(t.dataset.tool === currentTool ? null : t.dataset.tool);
  });
});

document.querySelectorAll('.seedOpt').forEach(s => {
  s.addEventListener('click', () => {
    sfxClick();
    currentSeed = s.dataset.seed;
    document.querySelectorAll('.seedOpt').forEach(x => x.classList.remove('active'));
    s.classList.add('active');
  });
});

document.querySelectorAll('.shopTab').forEach(t => {
  t.addEventListener('click', () => {
    sfxClick();
    renderShop(t.dataset.tab);
  });
});

document.getElementById('closeInvBtn').onclick = () => { sfxClick(); closeAllPanels(); };
document.getElementById('closeShopBtn').onclick = () => { sfxClick(); closeAllPanels(); };
document.getElementById('closeHireBtn').onclick = () => { sfxClick(); closeAllPanels(); };
document.getElementById('closeArmyBtn').onclick = () => { sfxClick(); closeAllPanels(); };
document.getElementById('closeAchBtn').onclick = () => { sfxClick(); closeAllPanels(); };

document.getElementById('saveBtn').onclick = () => { ensureAudio(); saveGame(); };
document.getElementById('achBtn').onclick = () => { ensureAudio(); sfxClick(); toggleAchievements(); };
document.getElementById('shopBtn').onclick = () => { ensureAudio(); sfxClick(); toggleShop(); };
document.getElementById('hireBtn').onclick = () => { ensureAudio(); sfxClick(); toggleHirePanel(); };
document.getElementById('armyBtn').onclick = () => { ensureAudio(); sfxClick(); toggleArmyPanel(); };

document.getElementById('muteIcon').onclick = () => {
  muted = !muted;
  document.getElementById('muteIcon').textContent = muted ? '🔇' : '🔊';
  if (masterGain) masterGain.gain.value = muted ? 0 : masterVolume;
  sfxClick();
};

setInterval(() => {
  if (audioCtx) saveGame();
}, 30000);

window.addEventListener('beforeunload', () => saveGame());

// ============================================
// ==== INIT ====
// ============================================
const loaded = loadGame();
if (!loaded) {
  showToast('🌾 Selamat datang di Pixel Farm RPG!', '#ffed4a');
}
updateHUD();
requestAnimationFrame(gameLoop);

document.addEventListener('click', () => ensureAudio(), { once: true });
document.addEventListener('keydown', () => ensureAudio(), { once: true });

console.log('🌾 Pixel Farm RPG v15 loaded!');
</script>
</body>
</html>
"""

components.html(game_html, height=800, scrolling=False)
