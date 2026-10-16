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
  wheat:      { emoji:'🌾', name:'Gandum', sellPrice:10, food:false },
  corn:       { emoji:'🌽', name:'Jagung', sellPrice:25, food:false },
  tomato:     { emoji:'🍅', name:'Tomat',  sellPrice:40, food:false },
  wood:       { emoji:'🪵', name:'Kayu',   sellPrice:5,  food:false },
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
        // Makan
        const heal = info.hunger || 20;
        player.hunger = Math.min(player.hungerMax, player.hunger + heal);
        inventory[key]--;
        sfxEat();
        showToast(`🍗 +${heal} hunger`, '#5aff5a');
        updateHUD();
        renderInventory();
      } else if (info.sellPrice > 0) {
        // Jual
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
  const tabs = document.querySelectorAll('.shopTab');
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tab));

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
      if (c.stage >= 3) {
        // Ready to harvest
      }
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
    // Attack nearby animals/wolves
    attackNearby(worldX, worldY);
  } else if (currentTool === 'bow') {
    if (inventory.arrows > 0) {
      inventory.arrows--;
      // Shoot in player facing direction
      const dx = player.dir === 'right' ? 1 : player.dir === 'left' ? -1 : 0;
      const dy = player.dir === 'down' ? 1 : player.dir === 'up' ? -1 : 0;
      projectiles.push({
        x: player.x + 5, y: player.y + 5,
        vx: dx * 8, vy: dy * 8,
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
  // Cek apakah tile sekitar adalah water
  const tx = Math.floor(wx / TILE);
  const ty = Math.floor(wy / TILE);
  let nearWater = false;
  for (let dy=-1; dy<=1; dy++) {
    for (let dx=-1; dx<=1; dx++) {
      if (world[ty+dy] && world[ty+dy][tx+dx] === T_WATER) nearWater = true;
    }
  }
  if (!nearWater) {
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
    // Bar bergerak
    fishing.barPos += fishing.barDir * dt * 120;
    if (fishing.barPos >= 100) { fishing.barPos = 100; fishing.barDir = -1; }
    if (fishing.barPos <= 0) { fishing.barPos = 0; fishing.barDir = 1; }
    document.getElementById('fishBarFill').style.width = fishing.barPos + '%';
    fishing.timer += dt;
    if (fishing.timer > 1.2) {
      // Gagal
      fishing.active = false;
      indicator.style.display = 'none';
      sfxFishMiss();
      showToast('❌ Ikan lepas...', '#ff4444');
    }
  }
}

function fishingStrike() {
  if (!fishing.active || fishing.phase !== 'action') return;
  // Sukses kalau barPos 30-70
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

    // Target: player atau army terdekat
    let target = null, targetDist = 99999;
    const dp = Math.hypot(player.x - w.x, player.y - w.y);
    if (dp < 200) { target = player; targetDist = dp; }
    army.forEach(s => {
      const d = Math.hypot(s.x - w.x, s.y - w.y);
      if (d < targetDist && d < 200) { target = s; targetDist = d; }
    });

    if (target) {
      if (targetDist < 20) {
        // Attack
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
            // Army
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
        // Chase
        const dx = (target.x - w.x) / targetDist * w.speed;
        const dy = (target.y - w.y) / targetDist * w.speed;
        if (canMoveTo(w.x + dx, w.y, 12, 12, world)) w.x += dx;
        if (canMoveTo(w.x, w.y + dy, 12, 12, world)) w.y += dy;
        if (Math.abs(dx) > Math.abs(dy)) w.dir = dx > 0 ? 'right' : 'left';
        else w.dir = dy > 0 ? 'down' : 'up';
        w.animTimer++;
        if (w.animTimer > 10) { w.animTimer = 0; w.walkFrame = (w.walkFrame + 1) % 4; }
      }
    } else {
      // Wander
      w.wanderTimer -= dt;
      if (w.wanderTimer <= 0) {
        w.wanderTimer = 2 + Math.random() * 3;
        w.wanderAngle = Math.random() * Math.PI * 2;
      }
      const dx = Math.cos(w.wanderAngle) * w.speed * 0.5;
      const dy = Math.sin(w.wanderAngle) * w.speed * 0.5;
      if (canMoveTo(w.x + dx, w.y, 12, 12, world)) w.x += dx;
      if (canMoveTo(w.x, w.y + dy, 12, 12, world)) w.y += dy;
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

    // Flee dari player
    const dp = Math.hypot(player.x - a.x, player.y - a.y);
    if (dp < 60) {
      const dx = (a.x - player.x) / dp * a.speed * 2;
      const dy = (a.y - player.y) / dp * a.speed * 2;
      a.vx = dx; a.vy = dy;
    }

    if (canMoveTo(a.x + a.vx, a.y, 10, 10, world)) a.x += a.vx;
    else a.vx = 0;
    if (canMoveTo(a.x, a.y + a.vy, 10, 10, world)) a.y += a.vy;
    else a.vy = 0;

    if (Math.abs(a.vx) > Math.abs(a.vy)) a.dir = a.vx > 0 ? 'right' : 'left';
    else if (a.vy !== 0) a.dir = a.vy > 0 ? 'down' : 'up';

    a.animTimer++;
    if (a.animTimer > 12) { a.animTimer = 0; a.walkFrame = (a.walkFrame + 1) % 4; }
  });

  // Cleanup dead
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
    // Hit wolves
    wolves.forEach(w => {
      if (Math.abs(w.x - p.x) < 12 && Math.abs(w.y - p.y) < 12) {
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
    // Hit animals (player arrows only)
    if (p.fromPlayer) {
      animals.forEach(a => {
        if (a.dead) return;
        if (Math.abs(a.x - p.x) < 12 && Math.abs(a.y - p.y) < 12) {
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
    if (d > 4) {
      const nx = dx / d * n.speed;
      const ny = dy / d * n.speed;
      if (canMoveTo(n.x + nx, n.y, 10, 14, world)) n.x += nx;
      if (canMoveTo(n.x, n.y + ny, 10, 14, world)) n.y += ny;
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
  if (k === 'g') {
    // Toggle guard semua
    const anyGuard = army.some(s => s.guard);
    army.forEach((s, i) => { if (i < MAX_GUARDS) toggleGuard(i); });
  }
  if (k === 'e') {
    ensureAudio();
    if (nearBed) sleep();
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
  if (placementMode) {
    // Update preview
    return;
  }

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

  // Clamp
  player.x = Math.max(0, Math.min(WORLD_W*TILE - player.w, player.x));
  player.y = Math.max(0, Math.min(WORLD_H*TILE - player.h, player.y));

  // Check interactions
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

  // Bed prompt
  const bp = document.getElementById('bedPrompt');
  if (bp) bp.style.display = (nearBed && !currentInterior) ? 'block' : (currentInterior ? 'none' : 'none');
  if (currentInterior) {
    if (nearBed) bp.style.display = 'block';
  }
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

// Mouse handling
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

  // Interact with NPC
  for (const n of npcs) {
    if (Math.abs(n.x - wx) < 20 && Math.abs(n.y - wy) < 20) {
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
    ctx.fillRect(sx+2, sy+2, 4, 4);
    ctx.fillRect(sx+9, sy+7, 3, 3);
  } else if (t === T_PATH) {
    ctx.fillStyle = '#8a7a5a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#9a8a6a';
    ctx.fillRect(sx+1, sy+1, 14, 14);
  } else if (t === T_WATER) {
    ctx.fillStyle = '#2a5a9a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#3a6aaa';
    const wave = Math.sin(Date.now()/500 + sx/20) * 2;
    ctx.fillRect(sx+3, sy+5+wave, 10, 2);
    ctx.fillRect(sx+5, sy+10+wave, 6, 2);
  } else if (t === T_TREE) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+6, sy+8, 4, 8);
    ctx.fillStyle = '#2a6d2a';
    ctx.fillRect(sx+2, sy+2, 12, 10);
    ctx.fillStyle = '#3a8d3a';
    ctx.fillRect(sx+4, sy+3, 8, 6);
  } else if (t === T_FARMLAND) {
    ctx.fillStyle = '#6a4a2a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#7a5a3a';
    ctx.fillRect(sx+2, sy+3, 12, 2);
    ctx.fillRect(sx+2, sy+8, 12, 2);
    ctx.fillRect(sx+2, sy+13, 12, 2);
  } else if (t === T_CROP) {
    ctx.fillStyle = '#6a4a2a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#7a5a3a';
    ctx.fillRect(sx+2, sy+13, 12, 2);
  } else if (t === T_HOUSE) {
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#aa8a6a';
    ctx.fillRect(sx+1, sy+1, 14, 14);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx, sy, 16, 4);
  } else if (t === T_HOUSE_DOOR) {
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+2, sy+4, 12, 12);
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(sx+11, sy+10, 2, 2);
  } else if (t === T_FLOWER) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    const colors = ['#ff6b6b', '#ffed4a', '#4a90e2', '#ff69b4'];
    ctx.fillStyle = colors[(sx+sy) % colors.length];
    ctx.fillRect(sx+5, sy+5, 6, 6);
    ctx.fillStyle = '#fff';
    ctx.fillRect(sx+7, sy+7, 2, 2);
  } else if (t === T_LAMP) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+7, sy+6, 3, 10);
    ctx.fillStyle = '#ffed4a';
    ctx.fillRect(sx+5, sy+2, 7, 7);
    ctx.fillStyle = '#fff8a0';
    ctx.fillRect(sx+6, sy+3, 5, 5);
  } else if (t === T_STUMP) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+4, sy+8, 8, 6);
    ctx.fillStyle = '#7a5a3a';
    ctx.fillRect(sx+5, sy+9, 6, 4);
  } else if (t === T_SAPLING) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+7, sy+8, 2, 5);
    ctx.fillStyle = '#2a6d2a';
    ctx.fillRect(sx+5, sy+4, 6, 5);
  } else if (t === T_BED) {
    ctx.fillStyle = '#4a4a6a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#6a6a9a';
    ctx.fillRect(sx+2, sy+2, 12, 12);
    ctx.fillStyle = '#fff';
    ctx.fillRect(sx+3, sy+3, 10, 5);
  } else if (t === T_INTERIOR_FLOOR) {
    ctx.fillStyle = '#6a5a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#7a6a5a';
    ctx.fillRect(sx+1, sy+1, 14, 14);
  } else if (t === T_WALL) {
    ctx.fillStyle = '#4a3a2a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#5a4a3a';
    ctx.fillRect(sx+1, sy+1, 14, 14);
  } else if (t === T_TABLE) {
    ctx.fillStyle = '#6a5a4a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx+1, sy+1, 14, 14);
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(sx+2, sy+2, 12, 3);
  } else if (t === T_SHOP) {
    ctx.fillStyle = '#5a4a3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a6a4a';
    ctx.fillRect(sx+1, sy+1, 14, 14);
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(sx+3, sy+3, 10, 5);
    ctx.fillStyle = '#fff';
    ctx.font = '8px monospace';
    ctx.fillText('$', sx+6, sy+8);
  } else if (t === T_CAMP) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a5a3a';
    ctx.fillRect(sx+3, sy+5, 10, 8);
    ctx.fillStyle = '#aa7a5a';
    ctx.fillRect(sx+5, sy+3, 6, 6);
  } else if (t === T_FENCE) {
    ctx.fillStyle = '#3a7d3a';
    ctx.fillRect(sx, sy, TILE, TILE);
    ctx.fillStyle = '#8a5a2a';
    ctx.fillRect(sx+2, sy+2, 12, 12);
    ctx.fillStyle = '#aa7a4a';
    ctx.fillRect(sx+4, sy+4, 8, 8);
    ctx.fillStyle = '#6a4a1a';
    ctx.fillRect(sx+6, sy+6, 4, 4);
  }
}

function drawCrop(key, c, sx, sy) {
  if (c.stage < 0) return;
  const cropInfo = CROP_TYPES[c.type] || CROP_TYPES.wheat;
  if (c.stage === 0) {
    ctx.fillStyle = '#5aff5a';
    ctx.fillRect(sx+7, sy+10, 2, 3);
  } else if (c.stage === 1) {
    ctx.fillStyle = '#5aff5a';
    ctx.fillRect(sx+6, sy+7, 4, 6);
    ctx.fillStyle = '#7aff7a';
    ctx.fillRect(sx+7, sy+5, 2, 3);
  } else if (c.stage === 2) {
    ctx.fillStyle = '#5aff5a';
    ctx.fillRect(sx+5, sy+4, 6, 9);
    ctx.fillStyle = '#7aff7a';
    ctx.fillRect(sx+6, sy+2, 4, 4);
  } else if (c.stage >= 3) {
    ctx.fillStyle = cropInfo.color;
    ctx.fillRect(sx+4, sy+2, 8, 12);
    ctx.fillStyle = '#fff';
    ctx.fillRect(sx+5, sy+3, 2, 2);
    ctx.fillRect(sx+9, sy+5, 2, 2);
    // Ready glow
    ctx.fillStyle = 'rgba(255,255,100,0.3)';
    ctx.fillRect(sx+2, sy, 12, 16);
  }
}

function drawPlayer(x, y) {
  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(x-2, y+12, 14, 4);
  
  // Body
  ctx.fillStyle = '#4a90e2';
  ctx.fillRect(x, y+6, 10, 8);
  ctx.fillStyle = '#3a70b2';
  ctx.fillRect(x, y+10, 10, 4);
  
  // Head
  ctx.fillStyle = '#f0c8a0';
  ctx.fillRect(x+1, y, 8, 7);
  ctx.fillStyle = '#3a2a1a';
  ctx.fillRect(x, y-1, 10, 4);
  
  // Eyes
  const eyeX = player.dir === 'left' ? 1 : player.dir === 'right' ? 7 : 3;
  ctx.fillStyle = '#000';
  ctx.fillRect(x+eyeX, y+3, 2, 2);
  if (player.dir !== 'left' && player.dir !== 'right') {
    ctx.fillRect(x+eyeX+3, y+3, 2, 2);
  }
  
  // Legs
  const legOff = player.walkFrame === 1 ? -1 : player.walkFrame === 3 ? 1 : 0;
  ctx.fillStyle = '#2a2a3e';
  ctx.fillRect(x+1+legOff, y+14, 3, 3);
  ctx.fillRect(x+6-legOff, y+14, 3, 3);
}

function drawWorker(w) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(w.x-2, w.y+12, 14, 4);
  
  ctx.fillStyle = w.shirt;
  ctx.fillRect(w.x, w.y+6, 10, 8);
  ctx.fillStyle = w.color;
  ctx.fillRect(w.x, w.y+10, 10, 4);
  
  ctx.fillStyle = '#f0c8a0';
  ctx.fillRect(w.x+1, w.y, 8, 7);
  ctx.fillStyle = '#8a6a2a';
  ctx.fillRect(w.x, w.y-1, 10, 4);
  
  ctx.fillStyle = '#000';
  ctx.fillRect(w.x+3, w.y+3, 2, 2);
  ctx.fillRect(w.x+6, w.y+3, 2, 2);
  
  const legOff = w.walkFrame === 1 ? -1 : w.walkFrame === 3 ? 1 : 0;
  ctx.fillStyle = '#2a2a3e';
  ctx.fillRect(w.x+1+legOff, w.y+14, 3, 3);
  ctx.fillRect(w.x+6-legOff, w.y+14, 3, 3);
}

function drawSoldier(s) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(s.x-2, s.y+12, 14, 4);
  
  if (s.hurtFlash > 0) {
    ctx.fillStyle = '#ff8888';
    ctx.fillRect(s.x, s.y, 10, 16);
    return;
  }
  
  // Armor
  ctx.fillStyle = s.armorColor || '#888';
  ctx.fillRect(s.x, s.y+6, 10, 8);
  ctx.fillStyle = s.shirt;
  ctx.fillRect(s.x+1, s.y+7, 8, 6);
  
  // Head
  ctx.fillStyle = '#f0c8a0';
  ctx.fillRect(s.x+1, s.y, 8, 7);
  ctx.fillStyle = s.color;
  ctx.fillRect(s.x, s.y-1, 10, 4);
  
  // Weapon
  if (s.type === 'archer') {
    ctx.fillStyle = '#5a3a1a';
    ctx.fillRect(s.x+9, s.y+4, 2, 8);
  } else if (s.type === 'knight') {
    ctx.fillStyle = '#c0c0c0';
    ctx.fillRect(s.x-2, s.y+5, 2, 10);
    ctx.fillRect(s.x+10, s.y+5, 2, 10);
  } else {
    ctx.fillStyle = '#ccc';
    ctx.fillRect(s.x+9, s.y+2, 2, 10);
    ctx.fillStyle = '#8a5a2a';
    ctx.fillRect(s.x+9, s.y+11, 4, 2);
  }
  
  // Guard indicator
  if (s.guard) {
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(s.x+3, s.y-6, 4, 4);
  }
}

function drawAnimal(a) {
  if (a.dead) return;
  const info = ANIMAL_TYPES[a.type];
  ctx.fillStyle = 'rgba(0,0,0,0.2)';
  ctx.fillRect(a.x-1, a.y+8, 12, 3);
  
  let color = info.color;
  if (a.hurtFlash > 0) color = '#ff8888';
  ctx.fillStyle = color;
  ctx.fillRect(a.x, a.y+3, 10, 7);
  ctx.fillRect(a.x+2, a.y, 6, 5);
  
  ctx.fillStyle = '#000';
  ctx.fillRect(a.x+3, a.y+1, 1, 1);
  ctx.fillRect(a.x+6, a.y+1, 1, 1);
  
  const legOff = a.walkFrame === 1 ? -1 : a.walkFrame === 3 ? 1 : 0;
  ctx.fillStyle = color;
  ctx.fillRect(a.x+1+legOff, a.y+9, 2, 3);
  ctx.fillRect(a.x+7-legOff, a.y+9, 2, 3);
}

function drawWolf(w) {
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(w.x-2, w.y+8, 16, 4);
  
  let color = '#6a6a7a';
  if (w.hurtFlash > 0) color = '#ff8888';
  ctx.fillStyle = color;
  ctx.fillRect(w.x, w.y+3, 12, 8);
  ctx.fillRect(w.x+3, w.y, 7, 5);
  
  // Ears
  ctx.fillRect(w.x+3, w.y-2, 2, 3);
  ctx.fillRect(w.x+8, w.y-2, 2, 3);
  
  // Eyes
  ctx.fillStyle = '#ff4444';
  ctx.fillRect(w.x+4, w.y+2, 2, 2);
  ctx.fillRect(w.x+7, w.y+2, 2, 2);
  
  const legOff = w.walkFrame === 1 ? -1 : w.walkFrame === 3 ? 1 : 0;
  ctx.fillStyle = color;
  ctx.fillRect(w.x+1+legOff, w.y+10, 3, 3);
  ctx.fillRect(w.x+8-legOff, w.y+10, 3, 3);
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  const aw = getActiveWorld();
  const startX = Math.floor(camera.x / TILE);
  const startY = Math.floor(camera.y / TILE);
  const endX = Math.min(startX + Math.ceil(canvas.width / TILE) + 1, aw[0].length);
  const endY = Math.min(startY + Math.ceil(canvas.height / TILE) + 1, aw.length);

  // Draw tiles
  for (let ty = startY; ty < endY; ty++) {
    for (let tx = startX; tx < endX; tx++) {
      if (!aw[ty] || aw[ty][tx] === undefined) continue;
      const sx = tx * TILE - camera.x;
      const sy = ty * TILE - camera.y;
      drawTile(aw[ty][tx], sx, sy);
      
      // Draw crops
      const key = `${tx},${ty}`;
      if (crops[key] && aw[ty][tx] === T_CROP) {
        drawCrop(key, crops[key], sx, sy);
      }
    }
  }

  // Draw placement preview
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

  // Draw NPCs
  npcs.forEach(n => {
    const sx = n.x - camera.x, sy = n.y - camera.y;
    if (sx < -50 || sx > canvas.width + 50 || sy < -50 || sy > canvas.height + 50) return;
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(sx-2, sy+12, 14, 4);
    ctx.fillStyle = n.color;
    ctx.fillRect(sx, sy+6, 10, 8);
    ctx.fillStyle = '#f0c8a0';
    ctx.fillRect(sx+1, sy, 8, 7);
    ctx.fillStyle = '#000';
    ctx.fillRect(sx+3, sy+3, 2, 2);
    ctx.fillRect(sx+6, sy+3, 2, 2);
    // Name
    ctx.fillStyle = '#fff';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(n.name, sx+5, sy-4);
    ctx.textAlign = 'left';
  });

  // Draw animals
  animals.forEach(a => {
    const sx = a.x - camera.x, sy = a.y - camera.y;
    if (sx < -50 || sx > canvas.width + 50 || sy < -50 || sy > canvas.height + 50) return;
    drawAnimal({ ...a, x: sx, y: sy });
  });

  // Draw workers
  workers.forEach(w => {
    const sx = w.x - camera.x, sy = w.y - camera.y;
    if (sx < -50 || sx > canvas.width + 50 || sy < -50 || sy > canvas.height + 50) return;
    drawWorker({ ...w, x: sx, y: sy });
  });

  // Draw army
  army.forEach(s => {
    const sx = s.x - camera.x, sy = s.y - camera.y;
    if (sx < -50 || sx > canvas.width + 50 || sy < -50 || sy > canvas.height + 50) return;
    drawSoldier({ ...s, x: sx, y: sy });
  });

  // Draw wolves
  wolves.forEach(w => {
    const sx = w.x - camera.x, sy = w.y - camera.y;
    if (sx < -50 || sx > canvas.width + 50 || sy < -50 || sy > canvas.height + 50) return;
    drawWolf({ ...w, x: sx, y: sy });
  });

  // Draw projectiles
  projectiles.forEach(p => {
    const sx = p.x - camera.x, sy = p.y - camera.y;
    ctx.fillStyle = '#ffd700';
    ctx.fillRect(sx-1, sy-1, 3, 3);
  });

  // Draw player
  const psx = player.x - camera.x;
  const psy = player.y - camera.y;
  drawPlayer(psx, psy);

  // Draw darkness overlay
  const darkness = getDarkness();
  if (darkness > 0) {
    ctx.fillStyle = `rgba(10,10,40,${darkness})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Lamp glow
    for (let ty = startY; ty < endY; ty++) {
      for (let tx = startX; tx < endX; tx++) {
        if (aw[ty] && aw[ty][tx] === T_LAMP) {
          const lx = tx * TILE - camera.x + 8;
          const ly = ty * TILE - camera.y + 8;
          const grad = ctx.createRadialGradient(lx, ly, 0, lx, ly, 60);
          grad.addColorStop(0, 'rgba(255,237,74,0.3)');
          grad.addColorStop(1, 'rgba(255,237,74,0)');
          ctx.fillStyle = grad;
          ctx.fillRect(lx-60, ly-60, 120, 120);
        }
      }
    }
    
    // Player glow
    const pgrad = ctx.createRadialGradient(psx+5, psy+5, 0, psx+5, psy+5, 50);
    pgrad.addColorStop(0, 'rgba(255,255,200,0.15)');
    pgrad.addColorStop(1, 'rgba(255,255,200,0)');
    ctx.fillStyle = pgrad;
    ctx.fillRect(psx-50, psy-50, 110, 110);
  }

  // Sky tint
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
          x: w.x, y: w.y, w: 10, h: 14,
          name: `Petani #${i+1}`,
          color: '#8b6f47', shirt: '#5a8a3a',
          speed: 0.6, actionDelay: 1.5, actionTimer: 0,
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

  // Time
  time.totalMinutes += dt * time.minutesPerSecond;
  if (time.totalMinutes >= 24 * 60) {
    time.totalMinutes -= 24 * 60;
    time.day++;
    checkAchievements();
  }

  // Hunger
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

  // Spawn wolves at night
  const h = (time.totalMinutes/60) % 24;
  if ((h >= 20 || h < 5) && wolves.length < 4 && Math.random() < 0.002) {
    spawnWolf();
  }

  // Camera
  const targetCamX = player.x + player.w/2 - canvas.width/2;
  const targetCamY = player.y + player.h/2 - canvas.height/2;
  camera.x += (targetCamX - camera.x) * 0.1;
  camera.y += (targetCamY - camera.y) * 0.1;
  camera.x = Math.max(0, Math.min(WORLD_W*TILE - canvas.width, camera.x));
  camera.y = Math.max(0, Math.min(WORLD_H*TILE - canvas.height, camera.y));

  render();
  updateHUD();

  // Dialog timer
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

// Auto-save every 30 seconds
setInterval(() => {
  if (audioCtx) saveGame();
}, 30000);

// Save on exit
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

// Init audio on first interaction
document.addEventListener('click', () => ensureAudio(), { once: true });
document.addEventListener('keydown', () => ensureAudio(), { once: true });

console.log('🌾 Pixel Farm RPG v15 loaded!');
</script>
</body>
</html>
"""
components.html(game_html, height=700, scrolling=False)
