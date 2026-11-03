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
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
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

  playXpConsume() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(987.77, now); // B5
    osc.frequency.exponentialRampToValueAtTime(440, now + 0.25); // A4
    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(now + 0.28);
  }

  playError() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(160, now);
    osc.frequency.setValueAtTime(110, now + 0.08);
    gain.gain.setValueAtTime(0.28, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(now + 0.26);
  }
}

const mcAudio = new RetroAudioEngine();
const HOTBAR_ORDER = ['iron', 'diamond', 'portal', 'gold', 'blaze', 'pearl', 'crystals', 'dragon', 'egg'];
window.unlockedHints = new Set();
window.currentXp = 30;

// Reproducir sonido al hacer click en cualquier botón mc-btn
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mc-btn:not(.mc-btn-disabled)').forEach(btn => {
    btn.addEventListener('click', () => mcAudio.playClick());
  });
  syncInventoryHUD();
});

// Función para sacudir botones bloqueados con sonido de error
function triggerLockedShake(buttonEl, message) {
  mcAudio.playError();
  if (buttonEl) {
    buttonEl.classList.remove('mc-btn-shake');
    void buttonEl.offsetWidth; // retrigger reflow
    buttonEl.classList.add('mc-btn-shake');
    setTimeout(() => buttonEl.classList.remove('mc-btn-shake'), 450);
  }
  if (message) {
    showToast(message, 'warning');
  }
}

// Toast de notificación retro no bloqueante
function showToast(message, type = 'info') {
  const existing = document.querySelector('.mc-toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `mc-toast-notification mc-toast-${type}`;
  toast.innerHTML = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 400);
  }, 2600);
}

// 2. Control de Pistas con Consumo de XP (Gamificado)
async function toggleHint(challengeId) {
  const hintEl = document.getElementById(`hint-${challengeId}`);
  const btn = document.querySelector(`button[onclick*="toggleHint('${challengeId}')"]`);

  if (!hintEl) return;

  // Si ya está visible, alternar para cerrar gratis
  if (hintEl.style.display === 'block') {
    mcAudio.playClick();
    hintEl.style.display = 'none';
    return;
  }

  // Si ya fue desbloqueada en esta sesión, abrir gratis
  if (window.unlockedHints.has(challengeId)) {
    mcAudio.playClick();
    hintEl.style.display = 'block';
    return;
  }

  // Intentar desbloquear consumiendo XP en el servidor
  try {
    const res = await fetch('/api/unlock_hint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ challenge: challengeId })
    });
    const data = await res.json();

    if (data.success) {
      window.unlockedHints.add(challengeId);
      window.currentXp = data.xp;
      mcAudio.playXpConsume();
      hintEl.style.display = 'block';
      
      if (btn) {
        btn.textContent = '💡 Ver Pista';
        btn.classList.add('mc-btn-unlocked');
      }

      updateXpDisplay(data.xp);
      showToast(`✨ ¡Pista desbloqueada! Se consumieron ${data.cost || 20} XP.`, 'success');
    } else {
      mcAudio.playError();
      if (btn) {
        btn.classList.remove('mc-btn-shake');
        void btn.offsetWidth;
        btn.classList.add('mc-btn-shake');
        setTimeout(() => btn.classList.remove('mc-btn-shake'), 450);
      }
      showToast(`⚠️ ${data.message}`, 'error');
    }
  } catch (err) {
    mcAudio.playError();
    showToast('⚠️ Error de conexión con el servidor.', 'error');
  }
}

function toggleSource(challengeId) {
  mcAudio.playClick();
  const srcEl = document.getElementById(`source-${challengeId}`);
  if (srcEl) {
    srcEl.style.display = srcEl.style.display === 'block' ? 'none' : 'block';
  }
}

// 3. Aviso de dimensión completada sin bloquear el hilo
function showCelebration(message) {
  const overlay = document.createElement('div');
  overlay.className = 'mc-celebration';
  const box = document.createElement('div');
  box.className = 'mc-celebration-box';
  box.innerHTML = message;
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 2600);
}

// 4. Refleja el ítem desbloqueado en el DOM
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

      if (data.xp !== undefined) {
        updateXpDisplay(data.xp);
      }

      setTimeout(() => {
        syncInventoryHUD();

        if (data.all_completed) {
          mcAudio.playLevelUp();
          showCelebration('🏆 ¡JUEGO COMPLETADO!<br>Redirigiendo a la pantalla de victoria...');
          setTimeout(() => { window.location.href = '/victory'; }, 2000);
          return;
        }

        if (data.dimension_completed) {
          mcAudio.playLevelUp();
          showCelebration(`🎉 ¡Has completado la dimensión ${dimension.toUpperCase()}! (+50 XP)`);
          setTimeout(() => window.location.reload(), 1900);
        }
      }, 700);
    } else {
      mcAudio.playError();
      if (feedbackEl) {
        feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">❌ ${data.message}</div>`;
      }
    }
  } catch (err) {
    mcAudio.playError();
    if (feedbackEl) {
      feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">⚠️ Error de conexión con el servidor.</div>`;
    }
  }
}

// Actualiza barra y textos de XP
function updateXpDisplay(xp) {
  window.currentXp = xp;
  const levelBadge = document.getElementById('mc-xp-level');
  if (levelBadge) {
    levelBadge.textContent = `XP ${xp}`;
  }

  const xpNum = document.getElementById('mc-xp-number');
  if (xpNum) {
    xpNum.textContent = `${xp}`;
  }

  const progressBar = document.getElementById('mc-xp-bar-progress');
  if (progressBar) {
    // Calculamos un porcentaje relativo (ej. base 100 XP por ciclo de nivel)
    const pct = Math.min(100, Math.max(0, (xp % 100 === 0 && xp > 0 ? 100 : (xp % 100))));
    progressBar.style.width = `${pct}%`;
  }
}

// 6. Sincronización del Inventario HUD en Vivo
async function syncInventoryHUD() {
  try {
    const res = await fetch('/api/inventory');
    const data = await res.json();

    // Actualizar slots de inventario
    const items = HOTBAR_ORDER;
    items.forEach((item, index) => {
      const slotEl = document.getElementById(`slot-${index + 1}`);
      if (slotEl) {
        if (data.inventory.includes(item)) {
          slotEl.classList.remove('locked');
          slotEl.classList.add('unlocked');
        } else {
          slotEl.classList.remove('unlocked');
          slotEl.classList.add('locked');
        }
      }
    });

    // Actualizar XP y pistas desbloqueadas
    if (data.xp !== undefined) {
      updateXpDisplay(data.xp);
    }

    if (Array.isArray(data.unlocked_hints)) {
      window.unlockedHints = new Set(data.unlocked_hints);
      data.unlocked_hints.forEach(challengeId => {
        const btn = document.querySelector(`button[onclick*="toggleHint('${challengeId}')"]`);
        if (btn) {
          btn.textContent = '💡 Ver Pista';
          btn.classList.add('mc-btn-unlocked');
        }
      });
    }
  } catch (e) {
    console.error("Error sincronizando inventario HUD:", e);
  }
}
