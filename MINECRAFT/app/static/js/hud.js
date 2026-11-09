/* ==========================================================================
   MINECRAFT CTF - HUD JAVASCRIPT & AUDIO ENGINE
   Developed by: Thorfinn777, Martyn777, Sassyjack777
   ========================================================================== */

console.log(
  "%cMINECRAFT CTF LAB | Desarrollado por: Thorfinn777, Martyn777, Sassyjack777",
  "background: #1e3a1e; color: #55ff55; font-size: 13px; font-weight: bold; padding: 4px 8px; border: 1px solid #55ff55;"
);

window.unlockedHints = new Set();
window.currentXp = 30;

// Inicialización de Eventos y Sonido de Dimensión
document.addEventListener('DOMContentLoaded', () => {

  // Sincronizar HUD
  syncInventoryHUD();


  // Mostrar/ocultar barra inferior (HUD)
  const hudToggle = document.getElementById('mc-hud-toggle');
  const hudBottom = document.getElementById('mc-hud-bottom');
  let hudVisible = true;
  function setHudVisible(visible) {
    hudVisible = visible;
    document.body.classList.toggle('hud-hidden', !visible);
    if (hudToggle) {
      hudToggle.setAttribute('aria-expanded', String(visible));
      hudToggle.textContent = visible ? 'Ocultar HUD' : 'Mostrar HUD';
      hudToggle.style.bottom = visible ? '150px' : '12px';
    }
  }
  if (hudToggle) {
    hudToggle.addEventListener('click', () => setHudVisible(!hudVisible));
  }

  // Barra lateral desplegable a la derecha
  const sidebarToggle = document.getElementById('mc-sidebar-toggle');
  const sidebar = document.getElementById('mc-sidebar-right');
  const sidebarClose = document.getElementById('mc-sidebar-close');
  const sidebarBackdrop = document.getElementById('mc-sidebar-backdrop');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('open');
    if (sidebarBackdrop) sidebarBackdrop.classList.add('open');
    if (sidebarToggle) sidebarToggle.setAttribute('aria-expanded', 'true');
    sidebar.setAttribute('aria-hidden', 'false');
  }

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    if (sidebarBackdrop) sidebarBackdrop.classList.remove('open');
    if (sidebarToggle) sidebarToggle.setAttribute('aria-expanded', 'false');
    sidebar.setAttribute('aria-hidden', 'true');
  }

  if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
  if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
  if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', closeSidebar);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSidebar();
  });
});

// Detectar y reproducir sonido cuando se entra o cambia entre las 3 dimensiones / victoria

// Sacudir botones bloqueados con sonido de error
function triggerLockedShake(buttonEl, message) {
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
        hintEl.style.display = 'none';
    return;
  }

  // Si ya fue desbloqueada en esta sesión, abrir gratis
  if (window.unlockedHints.has(challengeId)) {
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
            hintEl.style.display = 'block';
      
      if (btn) {
        btn.textContent = 'Ver Pista';
        btn.classList.add('mc-btn-unlocked');
      }

      updateXpDisplay(data.xp);
      showToast(`Pista desbloqueada! Se consumieron ${data.cost || 20} XP.`, 'success');
    } else {
            if (btn) {
        btn.classList.remove('mc-btn-shake');
        void btn.offsetWidth;
        btn.classList.add('mc-btn-shake');
        setTimeout(() => btn.classList.remove('mc-btn-shake'), 450);
      }
      showToast(`Aviso: ${data.message}`, 'error');
    }
  } catch (err) {
        showToast('Error: Error de conexión con el servidor.', 'error');
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
      submitBtn.textContent = '';
    }
  }
  const cardEl = inputEl.closest('.challenge-card');
  if (cardEl) cardEl.classList.add('unlocked');
}

// 5. Envío Asíncrono de Flags y Actualización de HUD (Sin sonido repetitivo de flag y sin retrasos)
async function submitFlag(dimension, step, event) {
  if (event) event.preventDefault();
  
  const inputEl = document.getElementById(`flag-input-${step}`);
  const feedbackEl = document.getElementById(`feedback-${step}`);
  if (!inputEl) return;

  const flagValue = inputEl.value.trim();
  if (!flagValue) {
    if (feedbackEl) {
      feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error"> Ingresa una bandera primero.</div>`;
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
        feedbackEl.innerHTML = `<div class="mc-alert mc-alert-success">${data.message}</div>`;
      }
      markItemUnlocked(step);

      if (data.xp !== undefined) {
        updateXpDisplay(data.xp);
      }

      // Sincronización inmediata sin lag artificial
      syncInventoryHUD();

      // Si se completó el juego completo (derrota final del dragón)
      if (data.all_completed) {
                showCelebration('HAS LIBERADO EL END!<br>¡Ender Dragón derrotado! Redirigiendo...');
        setTimeout(() => { 
          sessionStorage.setItem('mc_last_dimension', 'the_end'); // fuerza sonido en victoria si corresponde
          window.location.href = '/victory'; 
        }, 1200);
        return;
      }

      // Si completó la dimensión actual, permitir avanzar
      if (data.dimension_completed) {
        showCelebration(`Has completado la dimension ${dimension.toUpperCase()}! (+50 XP)`);
        setTimeout(() => window.location.reload(), 1400);
      }
    } else {
            if (feedbackEl) {
        feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">Error: ${data.message}</div>`;
      }
    }
  } catch (err) {
        if (feedbackEl) {
      feedbackEl.innerHTML = `<div class="mc-alert mc-alert-error">Error: Error de conexión con el servidor.</div>`;
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
          btn.textContent = 'Ver Pista';
          btn.classList.add('mc-btn-unlocked');
        }
      });
    }
  } catch (e) {
    console.error("Error sincronizando inventario HUD:", e);
  }
}
