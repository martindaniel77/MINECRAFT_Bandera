# ⛏️ Minecraft CTF Lab - DVWA Style Platform

Laboratorio interactivo de Ciberseguridad con temática de **Minecraft**, diseñado para ejecutarse sobre **Docker** en **Kali Linux** y resolverse 100% mediante navegador web y herramientas de pentesting.

## Instalacion del Docker
```bash
sudo apt install -y docker.io docker-compose  
```

> ⚡ **Perfil de Optimización para VirtualBox:**
> Configurado y afinado específicamente para máquinas virtuales con **4048 MB de RAM (4 GB)** y **2 procesadores (vCPUs)**.
> - **Límite de CPU a 1.5 vCPUs:** Evita que el contenedor sature ambos núcleos al 100% y congele la interfaz de usuario (XFCE, LightDM) o el navegador de la VM.
> - **Límite de RAM a 512 MB (128 MB garantizados):** La app consume únicamente ~80 MB en reposo, dejando más de 3.5 GB libres para Kali Linux, Firefox, Burp Suite y herramientas de auditoría.
> - **Gunicorn Preload (2 workers + 2 threads):** Memoria compartida vía Copy-on-Write (COW) y reciclaje de memoria periódico (`--max-requests 500`).
> - **SQLite en modo WAL + synchronous NORMAL:** Reduce dramáticamente las operaciones de I/O y `fsync` en el disco virtual de VirtualBox.

---

## 🚀 Despliegue Rápido en Kali Linux

### 1. Clonar o copiar esta carpeta a tu máquina virtual de Kali Linux:
```bash
cd /ruta/a/MINECRAFT
```

### 2. Dar permisos y ejecutar el script de despliegue automático:
```bash
sed -i 's/\r$//' deploy.sh
chmod +x deploy.sh
./deploy.sh
```

*(O manualmente usando Docker Compose)*:
```bash
docker-compose up -d --build
```

### 3. Abrir en el navegador de Kali Linux:
```
http://localhost:8080
```

---

## 🎮 Estructura de Dimensiones y Retos

1. **🟢 Overworld (Fácil):**
   - ⛏️ **Hierro:** Esteganografía y Cifrado César (ROT-13) / Base64.
   - 💎 **Diamante:** Inyección SQL (SQLi) en el cofre $Y=-58$.
   - 🟣 **Portal:** Análisis de Metadatos (FOCA/Exif) en planos de construcción.

2. **🔴 Nether (Medio):**
   - 🟡 **Oro:** Stored XSS y Robo de Sesiones al Piglin Guard.
   - 🔥 **Varas de Blaze:** Carga de Archivos Arbitraria (File Upload) a RCE.
   - 👁️ **Ender Pearl:** Violación de Mínimo Privilegio / Parameter Tampering.

3. **🟣 The End (Difícil):**
   - 💥 **Cristales:** Explotación de Servicio / CVE Simulado (Estilo Metasploit).
   - 🐉 **Ender Dragón:** Inyección de Comandos (Command Injection) en Telemetría.
   - 🥚 **Huevo de Dragón:** Evasión de Honeypot y Path Traversal (LFI) hacia `/root/`.

---

## 📚 Documentación Adicional
- Consulta el archivo `solution_guide.md` para ver el Writeup completo y todos los payloads listos para usar en Kali Linux.
