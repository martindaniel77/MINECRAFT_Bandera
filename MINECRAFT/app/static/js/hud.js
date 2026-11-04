/* ==========================================================================
   MINECRAFT CTF - HUD JAVASCRIPT & AUDIO ENGINE
   Developed by: Thorfinn777, Martyn777, Sassyjack777
   ========================================================================== */

console.log(
  "%c⛏️ MINECRAFT CTF LAB | Desarrollado por: Thorfinn777, Martyn777, Sassyjack777",
  "background: #1e3a1e; color: #55ff55; font-size: 13px; font-weight: bold; padding: 4px 8px; border: 1px solid #55ff55;"
);

// 1. Sintetizador de Sonidos de Minecraft con Web Audio API (100% Offline y sin retardo)
class RetroAudioEngine {
  constructor() {
    this.ctx = null;
    this.hasInteracted = false;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    this.hasInteracted = true;
  }

  // Sonido de click en interfaz
  playClick() {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(800, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(200, this.ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.18, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.05);
  }

  // Sonido de error o botón bloqueado
  playError() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(160, now);
    osc.frequency.setValueAtTime(110, now + 0.08);
    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(now + 0.24);
  }

  // Sonido al consumir XP por pista
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

  // --------------------------------------------------------------------------
  // SONIDOS CARACTERÍSTICOS DE LAS 3 DIMENSIONES Y VICTORIA DE MINECRAFT
  // --------------------------------------------------------------------------

  // 🟢 OVERWORLD: La clásica melodía ambiental pacífica y etérea estilo C418 (Wet Hands / Subwoofer Lullaby)
  playOverworld() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;

    // Arpegio cálido y pacífico con armónicos suaves: D4, F#4, A4, D5
    const notes = [
      { f: 293.66, t: 0.0, d: 0.9 }, // D4
      { f: 369.99, t: 0.35, d: 0.9 }, // F#4
      { f: 440.00, t: 0.70, d: 1.0 }, // A4
      { f: 587.33, t: 1.10, d: 1.5 }  // D5
    ];

    notes.forEach(n => {
      // Onda seno principal (tono puro y suave de piano/chime)
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(n.f, now + n.t);

      // Armónico sutil tipo triángulo para darle calidez de instrumento acústico
      const overtone = this.ctx.createOscillator();
      const overGain = this.ctx.createGain();
      overtone.type = 'triangle';
      overtone.frequency.setValueAtTime(n.f * 2, now + n.t);

      const startTime = now + n.t;
      const endTime = startTime + n.d;

      gain.gain.setValueAtTime(0.001, startTime);
      gain.gain.linearRampToValueAtTime(0.18, startTime + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, endTime);

      overGain.gain.setValueAtTime(0.001, startTime);
      overGain.gain.linearRampToValueAtTime(0.06, startTime + 0.03);
      overGain.gain.exponentialRampToValueAtTime(0.0001, endTime);

      osc.connect(gain);
      overtone.connect(overGain);
      gain.connect(this.ctx.destination);
      overGain.connect(this.ctx.destination);

      osc.start(startTime);
      overtone.start(startTime);
      osc.stop(endTime);
      overtone.stop(endTime);
    });
  }

  // 🔴 NETHER: El sonido del Portal del Nether (drone pulsante grave wub-wub y siseo etéreo)
  playNether() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const dur = 2.4;

    // 1. Sub-bass profundo y misterioso
    const subOsc = this.ctx.createOscillator();
    const subGain = this.ctx.createGain();
    subOsc.type = 'sawtooth';
    subOsc.frequency.setValueAtTime(75, now);
    subOsc.frequency.exponentialRampToValueAtTime(55, now + dur);

    // Filtro paso-bajo con resonancia para recrear el zumbido del portal
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(320, now);
    filter.Q.setValueAtTime(6.0, now);

    // LFO para oscilar la resonancia (el clásico "wub-wub" del portal)
    const lfo = this.ctx.createOscillator();
    const lfoGain = this.ctx.createGain();
    lfo.type = 'sine';
    lfo.frequency.setValueAtTime(2.2, now); // 2.2 Hz de pulsación
    lfoGain.gain.setValueAtTime(140, now);
    lfo.connect(filter.frequency);

    subGain.gain.setValueAtTime(0.001, now);
    subGain.gain.linearRampToValueAtTime(0.22, now + 0.25);
    subGain.gain.exponentialRampToValueAtTime(0.001, now + dur);

    subOsc.connect(filter);
    filter.connect(subGain);
    subGain.connect(this.ctx.destination);

    // 2. Ruido etéreo de fondo (portal whoosh)
    try {
      const bufSize = this.ctx.sampleRate * 1.5;
      const noiseBuffer = this.ctx.createBuffer(1, bufSize, this.ctx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufSize; i++) {
        output[i] = Math.random() * 2 - 1;
      }
      const whiteNoise = this.ctx.createBufferSource();
      whiteNoise.buffer = noiseBuffer;

      const noiseFilter = this.ctx.createBiquadFilter();
      noiseFilter.type = 'bandpass';
      noiseFilter.frequency.setValueAtTime(450, now);
      noiseFilter.Q.setValueAtTime(3.5, now);

      const noiseGain = this.ctx.createGain();
      noiseGain.gain.setValueAtTime(0.001, now);
      noiseGain.gain.linearRampToValueAtTime(0.12, now + 0.3);
      noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 1.8);

      whiteNoise.connect(noiseFilter);
      noiseFilter.connect(noiseGain);
      noiseGain.connect(this.ctx.destination);

      whiteNoise.start(now);
      whiteNoise.stop(now + 1.8);
    } catch (e) {}

    subOsc.start(now);
    lfo.start(now);
    subOsc.stop(now + dur);
    lfo.stop(now + dur);
  }

  // 🟣 THE END: Sonido cósmico del portal del End / resonancia misteriosa del vacío
  playTheEnd() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const dur = 2.6;

    // Tritono cósmico y resonante (misterio y peligro del vacío)
    const frequencies = [65.4, 130.8, 185.0, 520.0];

    frequencies.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = idx === 3 ? 'sine' : 'sawtooth';
      osc.frequency.setValueAtTime(freq, now);

      if (idx === 2) {
        osc.frequency.linearRampToValueAtTime(freq * 0.95, now + dur);
      }

      const filter = this.ctx.createBiquadFilter();
      filter.type = idx === 3 ? 'highpass' : 'bandpass';
      filter.frequency.setValueAtTime(freq * 1.5, now);
      filter.Q.setValueAtTime(4.0, now);

      const vol = idx === 3 ? 0.08 : 0.14;
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(vol, now + 0.3);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + dur);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + dur);
    });
  }

  // 🐉 VICTORIA: El rugido y explosión épica de la muerte del Ender Dragón
  playDragonDefeat() {
    this.init();
    if (!this.ctx) return;
    const now = this.ctx.currentTime;

    // 1. RUGIDO Y RETUMBO CAVERNOSO DEL DRAGÓN (Tono descendente con distorsión)
    const roarOsc = this.ctx.createOscillator();
    const roarGain = this.ctx.createGain();
    roarOsc.type = 'sawtooth';
    roarOsc.frequency.setValueAtTime(320, now);
    roarOsc.frequency.exponentialRampToValueAtTime(38, now + 1.4);

    const roarFilter = this.ctx.createBiquadFilter();
    roarFilter.type = 'lowpass';
    roarFilter.frequency.setValueAtTime(750, now);
    roarFilter.frequency.exponentialRampToValueAtTime(120, now + 1.4);
    roarFilter.Q.setValueAtTime(5, now);

    roarGain.gain.setValueAtTime(0.001, now);
    roarGain.gain.linearRampToValueAtTime(0.35, now + 0.08);
    roarGain.gain.exponentialRampToValueAtTime(0.001, now + 1.6);

    roarOsc.connect(roarFilter);
    roarFilter.connect(roarGain);
    roarGain.connect(this.ctx.destination);

    roarOsc.start(now);
    roarOsc.stop(now + 1.6);

    // 2. DETONACIONES SUCESIVAS DE EXPERIENCIA (Explosiones al romperse el dragón)
    [0.1, 0.45, 0.85, 1.25].forEach(offset => {
      try {
        const noiseLen = this.ctx.sampleRate * 0.4;
        const nBuffer = this.ctx.createBuffer(1, noiseLen, this.ctx.sampleRate);
        const data = nBuffer.getChannelData(0);
        for (let i = 0; i < noiseLen; i++) data[i] = Math.random() * 2 - 1;

        const noiseSrc = this.ctx.createBufferSource();
        noiseSrc.buffer = nBuffer;

        const nFilter = this.ctx.createBiquadFilter();
        nFilter.type = 'lowpass';
        nFilter.frequency.setValueAtTime(300, now + offset);

        const nGain = this.ctx.createGain();
        nGain.gain.setValueAtTime(0.3, now + offset);
        nGain.gain.exponentialRampToValueAtTime(0.001, now + offset + 0.38);

        noiseSrc.connect(nFilter);
        nFilter.connect(nGain);
        nGain.connect(this.ctx.destination);

        noiseSrc.start(now + offset);
        noiseSrc.stop(now + offset + 0.4);
      } catch (e) {}
    });

    // 3. HAZ DE LUZ ASCENDENTE (Fte. de Experiencia: Sweeps ascendentes celestiales)
    const beamOsc = this.ctx.createOscillator();
    const beamGain = this.ctx.createGain();
    beamOsc.type = 'sine';
    beamOsc.frequency.setValueAtTime(350, now + 0.5);
    beamOsc.frequency.exponentialRampToValueAtTime(1400, now + 2.2);

    beamGain.gain.setValueAtTime(0.001, now + 0.5);
    beamGain.gain.linearRampToValueAtTime(0.2, now + 1.0);
    beamGain.gain.exponentialRampToValueAtTime(0.001, now + 2.5);

    beamOsc.connect(beamGain);
    beamGain.connect(this.ctx.destination);

    beamOsc.start(now + 0.5);
    beamOsc.stop(now + 2.5);

    // 4. ACORDE FINAL DE NIVEL SUPERIOR / TRIUNFO (Level Up Chime)
    const triumphNotes = [523.25, 659.25, 783.99, 1046.50];
    triumphNotes.forEach((freq, idx) => {
      const tOsc = this.ctx.createOscillator();
      const tGain = this.ctx.createGain();
      tOsc.type = 'triangle';
      const tStart = now + 1.8 + idx * 0.1;
      tOsc.frequency.setValueAtTime(freq, tStart);

      tGain.gain.setValueAtTime(0.001, tStart);
      tGain.gain.linearRampToValueAtTime(0.22, tStart + 0.04);
      tGain.gain.exponentialRampToValueAtTime(0.001, tStart + 0.8);

      tOsc.connect(tGain);
      tGain.connect(this.ctx.destination);

      tOsc.start(tStart);
      tOsc.stop(tStart + 0.85);
    });
  }

  // Reproducir según la dimensión especificada
  playDimensionSound(dimension) {
    if (dimension === 'overworld') {
      this.playOverworld();
    } else if (dimension === 'nether') {
      this.playNether();
    } else if (dimension === 'the_end') {
      this.playTheEnd();
    } else if (dimension === 'victory') {
      this.playDragonDefeat();
    }
  }
}

const mcAudio = new RetroAudioEngine();
const HOTBAR_ORDER = ['iron', 'diamond', 'portal', 'gold', 'blaze', 'pearl', 'crystals', 'dragon', 'egg'];
window.unlockedHints = new Set();
window.currentXp = 30;

// Inicialización de Eventos y Sonido de Dimensión
document.addEventListener('DOMContentLoaded', () => {
  // Desbloquear AudioContext en cualquier interacción del usuario
  document.querySelectorAll('.mc-btn:not(.mc-btn-disabled), a, button').forEach(el => {
    el.addEventListener('click', () => mcAudio.init());
  });

  // Click en botones regulares
  document.querySelectorAll('.mc-btn:not(.mc-btn-disabled):not(.mc-btn-sound)').forEach(btn => {
    btn.addEventListener('click', () => mcAudio.playClick());
  });

  // Sincronizar HUD
  syncInventoryHUD();

  // Control de sonido al cambiar de dimensión
  handleDimensionAudioOnLoad();
});

// Detectar y reproducir sonido cuando se entra o cambia entre las 3 dimensiones / victoria
function handleDimensionAudioOnLoad() {
  const currentDim = document.body.dataset.dimension || 
                     (document.body.className.match(/dimension-([a-z_]+)/) || [])[1] || 
                     'overworld';

  const lastDim = sessionStorage.getItem('mc_last_dimension');

  // Si es la página de victoria, siempre reproducir el sonido de derrota del dragón
  if (currentDim === 'victory') {
    sessionStorage.setItem('mc_last_dimension', 'victory');
    // Intentar reproducir de inmediato (y si el navegador exige click, reproducir al primer click)
    const playVictory = () => {
      mcAudio.playDragonDefeat();
      document.removeEventListener('click', playVictory);
    };
    mcAudio.playDragonDefeat();
    document.addEventListener('click', playVictory, { once: true });
    return;
  }

  // Si cambió de dimensión (o es la primera entrada a una dimensión diferente del menú)
  if (lastDim !== currentDim) {
    sessionStorage.setItem('mc_last_dimension', currentDim);

    const playDim = () => {
      mcAudio.playDimensionSound(currentDim);
      document.removeEventListener('click', playDim);
    };

    mcAudio.playDimensionSound(currentDim);
    // Fallback si el navegador requería un click previo
    document.addEventListener('click', playDim, { once: true });
  }
}

// Sacudir botones bloqueados con sonido de error
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
  setTimeout(() => overlay.remove(), 2400);
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

// 5. Envío Asíncrono de Flags y Actualización de HUD (Sin sonido repetitivo de flag y sin retrasos)
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
      // SE ELIMINÓ EL SONIDO REPETITIVO EN CADA FLAG CONSEGUIDA SEGÚN REQUERIMIENTO DEL USUARIO
      if (feedbackEl) {
        feedbackEl.innerHTML = `<div class="mc-alert mc-alert-success">✨ ${data.message}</div>`;
      }
      markItemUnlocked(step);

      if (data.xp !== undefined) {
        updateXpDisplay(data.xp);
      }

      // Sincronización inmediata sin lag artificial
      syncInventoryHUD();

      // Si se completó el juego completo (derrota final del dragón)
      if (data.all_completed) {
        mcAudio.playDragonDefeat();
        showCelebration('🏆 ¡HAS LIBERADO EL END!<br>¡Ender Dragón derrotado! Redirigiendo...');
        setTimeout(() => { 
          sessionStorage.setItem('mc_last_dimension', 'the_end'); // fuerza sonido en victoria si corresponde
          window.location.href = '/victory'; 
        }, 1200);
        return;
      }

      // Si completó la dimensión actual, permitir avanzar
      if (data.dimension_completed) {
        showCelebration(`🎉 ¡Has completado la dimensión ${dimension.toUpperCase()}! (+50 XP)`);
        setTimeout(() => window.location.reload(), 1400);
      }
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
