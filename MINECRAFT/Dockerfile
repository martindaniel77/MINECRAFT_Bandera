FROM python:3.11-slim

LABEL maintainer="Thorfinn777, Martyn777, Sassyjack777"
LABEL authors="Thorfinn777, Martyn777, Sassyjack777"
LABEL description="Minecraft CTF Security Lab Platform"

# Instalar herramientas básicas del sistema para el entorno CTF
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    net-tools \
    procps \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios de secretos y desafíos en el sistema de archivos del contenedor
RUN mkdir -p /secret /var/www/honeypot /root

# Configuración de las banderas del sistema en el contenedor (Formato Flag{...})
RUN echo "FLAG{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}" > /secret/iron_ingot.txt && \
    echo "FLAG{MINECRAFT_DIAMOND_SQL1_Y58_UNLOCKED}" > /secret/diamond_vault.txt && \
    echo "FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}" > /secret/portal_key.txt && \
    echo "FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}" > /secret/gold_ingot.txt && \
    echo "FLAG{MINECRAFT_BLAZE_ROD_WEBSHELL_RCE}" > /secret/blaze_rod.txt && \
    echo "FLAG{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}" > /secret/ender_pearl.txt && \
    echo "FLAG{MINECRAFT_END_CRYSTALS_CVE_SHATTERED}" > /secret/end_crystals.txt && \
    echo "FLAG{MINECRAFT_ENDER_DRAGON_SLAIN_COMMAND_INJECTION}" > /secret/dragon_slain.txt && \
    echo "FLAG{MINECRAFT_FINAL_DRAGON_EGG_VICTORY_GG}" > /root/real_dragon_egg.txt && \
    echo "FLAG{HONEYPOT_TRAP_NICE_TRY_LOOK_IN_ROOT}" > /var/www/honeypot/fake_egg.txt

# Asignar permisos
RUN chmod 644 /secret/*.txt && \
    chmod 755 /root && \
    chmod 644 /root/real_dragon_egg.txt && \
    chmod 755 /var/www /var/www/honeypot && \
    chmod 644 /var/www/honeypot/fake_egg.txt

# Copiar código de la aplicación
COPY app/ /app/

# Crear carpeta de subidas para el reto de File Upload
RUN mkdir -p /app/static/uploads

# Pre-generar bytecode, base de datos y assets durante el build
# Esto evita consumo de CPU y latencia de disco virtual (VirtualBox) en el arranque
RUN python -m compileall -q /app && \
    python /app/bootstrap.py

# Ejecutar la aplicación sin privilegios de root
RUN useradd --create-home --shell /usr/sbin/nologin mcuser && \
    chown -R mcuser:mcuser /app

USER mcuser

# Exponer el puerto principal de la plataforma
EXPOSE 8080

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MALLOC_ARENA_MAX=2

# Configuración de Gunicorn afinada para 2 vCPUs y bajo consumo de RAM:
# - 2 workers (1 por vCPU) con 2 threads = 4 solicitudes concurrentes sin contención de CPU
# - --preload para compartir memoria física entre workers vía Copy-on-Write (COW)
# - --max-requests y --max-requests-jitter para reciclar memoria periódicamente sin caída de servicio
CMD ["gunicorn", "--preload", "--workers", "2", "--threads", "2", "--max-requests", "500", "--max-requests-jitter", "50", "--timeout", "30", "--bind", "0.0.0.0:8080", "wsgi:app"]
