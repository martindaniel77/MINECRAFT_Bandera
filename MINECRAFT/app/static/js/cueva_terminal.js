/* ==========================================================================
   MINECRAFT CTF - CONSOLA DE LAS CUEVAS (Actividad 3)
   Desarrollado por: Thorfinn777, Martyn777, Sassyjack777
   ========================================================================== */

(function () {
  'use strict';

  const form = document.getElementById('cave-form');
  const input = document.getElementById('cave-input');
  const output = document.getElementById('cave-output');
  const terminal = document.getElementById('cave-terminal');

  if (!form || !input || !output || !terminal) {
    return;
  }

  const PROMPT = 'steve@cueva:/cueva$';
  const history = [];
  let historyPos = 0;
  let busy = false;

  function scrollToBottom() {
    output.scrollTop = output.scrollHeight;
  }

  function appendLine(text, kind) {
    const line = document.createElement('div');
    line.className = 'cave-line' + (kind ? ' cave-line-' + kind : '');
    line.textContent = text;
    output.appendChild(line);
    scrollToBottom();
  }

  function appendBlock(text, kind) {
    if (!text) {
      return;
    }
    const block = document.createElement('pre');
    block.className = 'cave-pre' + (kind ? ' cave-line-' + kind : '');
    block.textContent = text;
    output.appendChild(block);
    scrollToBottom();
  }

  function clearScreen() {
    output.replaceChildren();
    appendLine('Pantalla limpia. La cueva sigue en silencio.', 'muted');
  }

  async function runCommand(rawCommand) {
    const command = rawCommand.trim();
    if (!command) {
      return;
    }

    history.push(command);
    historyPos = history.length;

    appendLine(PROMPT + ' ' + command, 'command');

    if (command.toLowerCase() === 'clear') {
      clearScreen();
      return;
    }

    busy = true;
    input.disabled = true;

    try {
      const response = await fetch('/overworld/cueva/terminal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
      });

      if (!response.ok) {
        throw new Error('HTTP ' + response.status);
      }

      const data = await response.json();
      if (data.clear) {
        clearScreen();
      } else {
        appendBlock(data.output || '', data.kind || 'text');
      }
    } catch (error) {
      appendLine('Error de conexión con la cueva: ' + error.message, 'error');
    } finally {
      busy = false;
      input.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (busy) {
      return;
    }
    const value = input.value;
    input.value = '';
    runCommand(value);
  });

  input.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (historyPos > 0) {
        historyPos -= 1;
        input.value = history[historyPos] || '';
      }
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (historyPos < history.length) {
        historyPos += 1;
        input.value = historyPos === history.length ? '' : (history[historyPos] || '');
      }
    }
  });

  terminal.addEventListener('click', function () {
    input.focus();
  });

  input.focus();
})();
