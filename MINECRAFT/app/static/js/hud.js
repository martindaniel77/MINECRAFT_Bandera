/* ==========================================================================
   MINECRAFT CTF - HUD JAVASCRIPT & RETRO SOUND ENGINE
   ========================================================================== */

// 1. Sintetizador de Sonidos Retro de Minecraft con Web Audio API (100% Offline)
class RetroAudioEngine {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
  }

  playClick() {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(800, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(200, this.ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.05);
  }

  playItemPickup() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(523.25, now); // C5
    osc.frequency.setValueAtTime(659.25, now + 0.08); // E5
    osc.frequency.setValueAtTime(783.99, now + 0.16); // G5
    osc.frequency.setValueAtTime(1046.50, now + 0.24); // C6
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(now + 0.45);
  }

  playLevelUp() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const notes = [440, 554, 659, 880, 1108, 1318];
    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(freq, now + idx * 0.07);
      gain.gain.setValueAtTime(0.2, now + idx * 0.07);
      gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.07 + 0.1);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now + idx * 0.07);
      osc.stop(now + idx * 0.07 + 0.12);
    });
  }

  playExplosion() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(120, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.5);
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(now + 0.55);
  }
}

const mcAudio = new RetroAudioEngine();

const HOTBAR_ORDER = ['iron', 'diamond', 'portal', 'gold', 'blaze', 'pearl', 'crystals', 'dragon', 'egg'];

// Reproducir sonido al hacer click en cualquier botón mc-btn
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mc-btn').forEach(btn => {
    btn.addEventListener('click', () => mcAudio.playClick());
  });
  syncInventoryHUD();
});

// 2. Control de Pistas y Codigo Fuente (acordeon)
function toggleHint(challengeId) {
  mcAudio.playClick();
  const hintEl = document.getElementById(`hint-${challengeId}`);
  if (hintEl) {
    hintEl.style.display = hintEl.style.display === 'block' ? 'none' : 'block';
  }
}

function toggleSource(challengeId) {
  mcAudio.playClick();
  const srcEl = document.getElementById(`source-${challengeId}`);
  if (srcEl) {
    srcEl.style.display = srcEl.style.display === 'block' ? 'none' : 'block';
  }
}

// 3. Aviso de dimension completada sin bloquear el hilo con alert()
function showCelebration(message) {
  const overlay = document.createElement('div');
  overlay.className = 'mc-celebration';
  const box = document.createElement('div');
  box.className = 'mc-celebration-box';
  box.textContent = message;
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 2400);
}

// 4. Refleja el ítem desbloqueado en el DOM sin recargar la página
function markItemUnlocked(step) {
  const index = HOTBAR_ORDER.indexOf(step);
  if (index === -1) return;

  const slotEl = document.getElementById(`slot-${index + 1}`);
  if (slotEl) {
    slotEl.classList.remove('locked');
    slotEl.classList.add('unlocked');
  }

  const inputEl = document.getElementById(`flag-input-${step}`);
  if (!inputEl) return;

  inputEl.setAttribute('readonly', 'readonly');
  const form = inputEl.closest('form');
  if (form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = '✅';
    }
  }
  const cardEl = inputEl.closest('.challenge-card');
  if (cardEl) cardEl.classList.add('unlocked');
}

// 5. Envío Asíncrono de Flags y Actualización de HUD
async function submitFlag(dimension, step, event) {
  if (event) event.preventDefault();
  mcAudio.playClick();

  const inputEl = document.getElementById(`flag-input-${step}`);
  const feedbackEl = document.getElementById(`feedback-${step}`);
  if (!inputEl) return;

  const flagValue = inputEl.value.trim();
  if (!flagValue) {
    if (feedbackEl) {
      feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">⚠️ Ingresa una bandera primero.</div>`;
    }
    return;
  }

  try {
    const res = await fetch('/api/submit_flag', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dimension: dimension, step: step, flag: flagValue })
    });
    const data = await res.json();

    if (data.success) {
      mcAudio.playItemPickup();
      if (feedbackEl) {
        feedbackEl.innerHTML = `<div class="mc-alert mc-alert-success">✨ ${data.message}</div>`;
      }
      markItemUnlocked(step);

      setTimeout(() => {
        syncInventoryHUD();

        if (data.all_completed) {
          mcAudio.playLevelUp();
          showCelebration('🏆 ¡JUEGO COMPLETADO! Redirigiendo a la pantalla de victoria...');
          setTimeout(() => { window.location.href = '/victory'; }, 1800);
          return;
        }

        if (data.dimension_completed) {
          mcAudio.playLevelUp();
          showCelebration(`🎉 ¡Has completado la dimensión ${dimension.toUpperCase()}!`);
          setTimeout(() => window.location.reload(), 1800);
        }
      }, 900);
    } else {
      if (feedbackEl) {
        feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">❌ ${data.message}</div>`;
      }
    }
  } catch (err) {
    if (feedbackEl) {
      feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">⚠️ Error de conexión con el servidor.</div>`;
    }
  }
}

// 6. Sincronización del Inventario HUD en Vivo
async function syncInventoryHUD() {
  try {
    const res = await fetch('/api/inventory');
    const data = await res.json();

    // Actualizar slots de inventario
    const items = HOTBAR_ORDER;
    let count = 0;

    items.forEach((item, index) => {
      const slotEl = document.getElementById(`slot-${index + 1}`);
      if (slotEl) {
        if (data.inventory.includes(item)) {
          slotEl.classList.remove('locked');
          slotEl.classList.add('unlocked');
          count++;
        } else {
          slotEl.classList.remove('unlocked');
          slotEl.classList.add('locked');
        }
      }
    });

    // Actualizar nivel de experiencia (XP Level)
    const levelEl = document.getElementById('mc-xp-level');
    if (levelEl) {
      levelEl.textContent = `NIVEL ${count * 10}`;
    }
  } catch (e) {
    console.error("Error sincronizando inventario HUD:", e);
  }
}
